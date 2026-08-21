# ==== 标准库 ==== #
from typing import (
    Any,
)

# ==== 第三方库 ==== #
from loguru import logger

# ==== 自定义库 ==== #
from ...context import (
    ContextLoader,
    ContentRole,
    Context,
    ContentUnit,
)
from ...user_config_manager import (
    UserConfigs
)
from ...global_config_manager import ConfigManager
from ...assist_struct import (
    CrossUserDataRouting,
    AdditionalData
)
from ...special_exception import HTTPException
from ...template_render import (
    TemplateParser
)
from ...status_map import StatusStack
from ._get_context import get_context
from ...clients.static_resources_client import (
    StaticResourcesClient
)

async def make_context(
    user_id: str,
    message: str | None,
    configs: UserConfigs,
    context_loader: ContextLoader,
    template_parser: TemplateParser,
    static_resources_client: StaticResourcesClient,
    task_status_stack: StatusStack[str],
    cross_user_data_routing: CrossUserDataRouting[str],
    history_messages: list[ContentUnit] | None = None,
    history_msg_role_map: dict[ContentRole, ContentRole | None] | None = None,
    role: ContentRole = ContentRole.USER,
    role_name:  str | None = "",
    extra_template_fields: dict[str, Any] | None = None,
    temporary_prompt: str | None = None,
    additional_data: AdditionalData | None = None,
    load_prompt: bool | None = None,
) -> tuple[Context, ContentUnit | None]:

    with task_status_stack.enter("Getting history context"):
        if load_prompt is None:
            if configs.load_prompt is None:
                load_prompt = ConfigManager.get_configs().prompt.load_prompt
            else:
                load_prompt = configs.load_prompt
        
        submit_context: Context = await get_context(
            context_loader = context_loader,
            static_resources_client = static_resources_client,
            history_messages = history_messages,
            temporary_prompt = temporary_prompt,
            load_prompt = load_prompt,
            cross_user_data_routing = cross_user_data_routing,
            template_parser = template_parser,
        )
    
    if history_msg_role_map is not None:
        with task_status_stack.enter("Role mapping"):
            logger.info(
                "Role mapping:\n{role_map}",
                role_map = "\n".join(f"{raw_role} -> {new_role}" for raw_role, new_role in history_msg_role_map.items()),
            )
            submit_context.role_map(history_msg_role_map)

    with task_status_stack.enter("Check Multimodal Message"):
        make_multimodal_message = configs.make_multimodal_message
        if make_multimodal_message is None:
            make_multimodal_message = ConfigManager.get_configs().context.make_multimodal_message
    
    with task_status_stack.enter("Splicing user input"):
        user_input: ContentUnit | None
        if message is not None:
            user_input = await context_loader.make_user_content(
                user_id = user_id,
                new_message = message,
                role = role,
                role_name = role_name,
                additional_data = additional_data,
                make_multimodal_message = make_multimodal_message,
                extra_template_fields = extra_template_fields,
                enable_user_input_template = ConfigManager.get_configs().text_template.enable.user_input_template,
                template_parser = template_parser
            )
            submit_context.append(user_input)
        else:
            user_input = None
    
    with task_status_stack.enter("Shrinking context"):
        # 如果上下文需要收缩，则进行收缩(为零或类型不对则不进行操作)
        if len(submit_context.context_list) > 0:
            max_context_length = configs.context_shrink_limit or ConfigManager.get_configs().context.context_shrink_limit
            if isinstance(max_context_length, int) and max_context_length > 0:
                if submit_context.total_length > max_context_length:
                    logger.info(
                        "Context length exceeds {max_context_length}, auto shrink",
                        user_id = user_id,
                        max_context_length = max_context_length
                    )
                    try:
                        submit_context.shrink(max_context_length)
                    except Exception as e:
                        logger.error(
                            "Failed to shrink context: {error}",
                            user_id = user_id,
                            error = str(e)
                        )
                        raise HTTPException(
                            status_code = 400,
                            detail = (
                                "Sorry, I failed to shrink the context.\n"
                                "This can be caused by an incorrect parameter input.\n"
                                "Please check that the context field is working properly in your configuration.\n"
                                "Or whether the Context data does not contain the specified header Role.\n"
                                "Or maybe you set the contraction value too low.\n"
                                f"Error: {e}"
                            ),
                        )
    
    return submit_context, user_input
    