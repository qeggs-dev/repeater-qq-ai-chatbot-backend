# ==== 标准库 ==== #
import asyncio
from typing import (
    Any,
)

# ==== 第三方库 ==== #
from loguru import logger

# ==== 自定义库 ==== #
from ...call_api.completions_api import (
    FinishReason
)
from ...model_requester import (
    MultiResponse
)
from ...context import (
    ContextLoader,
    Context,
    ContentUnit,
    TextBlock,
)
from ...global_config_manager import ConfigManager
from ...assist_struct import (
    Response,
    CrossUserDataRouting
)
from ...special_exception import HTTPException
from ...request_log import (
    TimeStamp
)
from ...template_render import (
    TemplateParser
)
from ...runtime_container import RepeaterRuntime
from ...status_map import (
    StatusStack
)
from ...request_log import (
    RequestLogManager
)

async def post_treatment(
    user_id: str,
    template_parser: TemplateParser,
    responses: MultiResponse,
    context_loader: ContextLoader,
    enable_assistant_template: bool,
    cross_user_data_routing: CrossUserDataRouting[str],
    task_status_stack: StatusStack[str],
    request_log_manager: RequestLogManager,
    extra_template_fields: dict[str, Any] | None = None,
    request_statistics_template: str = "",
    user_input: ContentUnit | None = None,
    output: Response = Response(),
    save_context: bool | None = None,
    save_only_text: bool = False,
    save_new_only: bool = False,
) -> Response:
    with task_status_stack.enter("PostProcessing"):
        # 补充调用日志的时间信息
        saved_user_id = cross_user_data_routing.context.save_to_user_id
        if extra_template_fields is None:
            extra_template_fields = {}
        
        new_context = responses.new_contexts()

        # 展开模型输出内容中的变量
        if enable_assistant_template:
            content_unit = new_context.last_content
            if content_unit is not None:
                if isinstance(content_unit.content, str):
                    content = await template_parser.render_ex(
                        content_unit.content,
                        user_id,
                        **extra_template_fields
                    )
                    content_unit.content = content
                elif isinstance(content_unit.content, list):
                    content = content_unit.to_plaintext_content()
                    content = await template_parser.render_ex(
                        content,
                        user_id,
                        **extra_template_fields
                    )
                    content_unit = content_unit.remove_context_block(TextBlock)
                    if isinstance(content_unit.content, list):
                        content_unit.content.append(
                            TextBlock(text = content)
                        )
                if content_unit.reasoning_content:
                    content_unit.reasoning_content = await template_parser.render_ex(
                        content_unit.reasoning_content,
                        user_id,
                        **extra_template_fields
                    )
                new_context.last_content = content_unit
        
        with task_status_stack.enter("Saving Context"):
            if cross_user_data_routing.context.save_to_user_id == user_id:
                historical_context = responses.historical_context
            else:
                historical_context = await context_loader.load_context(saved_user_id)
                if user_input is not None:
                    historical_context.append(user_input)

            # 保存上下文
            if save_context:
                if save_new_only:
                    saved_context: Context = Context()
                    if user_input is not None:
                        saved_context.append(user_input)
                    if new_context:
                        saved_context.extend(new_context)
                    logger.info(
                        "Saving new context...",
                        user_id = saved_user_id,
                    )
                else:
                    saved_context = historical_context
                    if new_context:
                        saved_context.extend(new_context)
                    logger.info(
                        "Saving context...",
                        user_id = saved_user_id,
                    )
                await context_loader.save(
                    user_id = saved_user_id,
                    context = saved_context,
                    reduce_to_text = save_only_text,
                )
            else:
                logger.warning("Context not saved", user_id = saved_user_id)

        # 记录任务结束时间
        for response in responses:
            response.request_log.task_end_time = TimeStamp()

        # 记录调用日志
        with task_status_stack.enter("Recording request log"):
            await request_log_manager.add_multi_request_log(responses.request_logs())

        # 记录API调用成功
        logger.success(f"Task Finished!", user_id = saved_user_id)

        # 返回模型输出内容
        with task_status_stack.enter("Returning response"):
            output.context = new_context
            output.create_time = responses[0].created
            output.id = responses[0].id

            last_response = responses[-1]

            output.finish_reason_cause = last_response.finish_reason_cause
            output.finish_reason_code = last_response.finish_reason.value if isinstance(last_response.finish_reason, FinishReason) else last_response.finish_reason
            output.request_log = responses.request_logs()

            if ConfigManager.get_configs().text_template.enable.request_statistics_template:
                output.request_statistics = await template_parser.render_ex(
                    request_statistics_template,
                    user_id,
                    request_log = responses[-1].request_log,
                    **extra_template_fields
                )

            return output