# ==== 标准库 ==== #

# ==== 第三方库 ==== #
from loguru import logger

# ==== 自定义库 ==== #
from ...context import (
    ContextLoader,
    Context,
    ContentUnit,
)
from ...assist_struct import (
    CrossUserDataRouting,
)
from ...template_render import (
    TemplateParser
)
from ...clients.static_resources_client import (
    StaticResourcesClient,
)
    
async def get_context(
    context_loader: ContextLoader,
    cross_user_data_routing: CrossUserDataRouting[str],
    static_resources_client: StaticResourcesClient,
    history_messages: list[ContentUnit] | None = None,
    temporary_prompt: str | None = None,
    load_prompt: bool = True,
    template_parser: TemplateParser | None = None
) -> Context:
    """
    获取上下文

    :param context_loader: 上下文加载器
    :param user_id: 用户ID
    :param message: 消息
    :param role: 角色
    :param role_name: 角色名
    :param temporary_prompt: 临时提示词
    :param image_url: 图片URL
    :param load_prompt: 是否加载提示
    :param continue_completion: 是否继续完成
    :param reference_context_id: 引用上下文ID
    :param template_parser: 模板解析器
    :return: 上下文对象
    """
    context_load_source: str = cross_user_data_routing.context.load_from_user_id
    prompt_load_source: str = cross_user_data_routing.prompt.load_from_user_id
    
    if history_messages is None:
        context: Context = await context_loader.load_context(
            user_id = context_load_source
        )
    else:
        context: Context = Context(
            context_list = history_messages,
        )

    if load_prompt:
        prompt: ContentUnit = await context_loader.load_prompt(
            user_id = prompt_load_source,
            static_resources_client = static_resources_client,
            temporary_prompt = temporary_prompt,
            template_parser = template_parser
        )
        context.prompt = prompt

    return context