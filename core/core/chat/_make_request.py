# ==== 标准库 ==== #
import random
import atexit
import asyncio
import traceback
from pathlib import Path
from typing import (
    AsyncIterator,
    Any,
)

# ==== 第三方库 ==== #
import orjson
import aiofiles
from loguru import logger

# ==== 自定义库 ==== #
from ...call_api.completions_api import (
    Request,
)
from ...context import (
    ContentRole,
    Context,
    ContentUnit,
)
from ...user_config_manager import (
    UserConfigs
)
from ...global_config_manager import GlobalConfigs
from ...assist_struct import (
    RequestUserInfo,
)
from ...clients.model_info import (
    ModelInfo,
)
from ...special_exception import HTTPException
from ._print_request_info import print_request_info

def make_request(
    *,
    user_id: str,
    user_input: ContentUnit | None = None,
    suffix: str | None = None,
    echo: bool | None = None,
    fim_mode: bool = False,
    user_info: RequestUserInfo,
    submit_context: Context,
    model_id: str | list[str],
    model: ModelInfo,
    configs: UserConfigs,
    global_configs: GlobalConfigs,
    assistant_role: ContentRole,
    role_name: str | None = None,
    thinking: bool | None = None,
    extra_bodys: dict[str, Any] | None = None,
) -> Request:
    # 创建请求对象
    request = Request()

    # 设置上下文
    request.context = submit_context
    
    # 设置 Model 信息
    request.url = model.get_base_url()
    request.model = model.id
    request.model_id = model_id
    request.model_uid = model.uid
    request.limits = model.limits
    request.timeout = model.timeout
    if configs.model_timeout is None:
        request.timeout = model.timeout
    else:
        request.timeout = configs.model_timeout
    if model.api_key is None:
        raise HTTPException("Model api key is None")
    request.key = model.api_key
    
    print_request_info(
        user_id = user_id,
        api = model,
        suffix = suffix,
        user_input = user_input,
        user_info = user_info,
        role_name = role_name,
    )

    # 设置请求对象的参数信息
    request.user_name = user_info.display_username()

    if configs.remove_reasoning_prompt is not None:
        request.remove_reasoning_prompt = configs.remove_reasoning_prompt
    else:
        request.remove_reasoning_prompt = global_configs.context.remove_reasoning_prompt
    
    if configs.tool_calling_remove_reasoning is not None:
        request.tool_calling_remove_reasoning = configs.tool_calling_remove_reasoning
    else:
        request.tool_calling_remove_reasoning = global_configs.context.tool_calling_remove_reasoning
    
    if configs.seed is not None:
        request.seed = configs.seed
    else:
        request.seed = global_configs.model.default_seed
    
    if configs.temperature is not None:
        request.temperature = configs.temperature
    else:
        request.temperature = global_configs.model.default_temperature
    
    if configs.top_a is not None:
        request.top_a = configs.top_a
    else:
        request.top_a = global_configs.model.default_top_a
    
    if configs.top_p is not None:
        request.top_p = configs.top_p
    else:
        request.top_p = global_configs.model.default_top_p
    
    if configs.top_k is not None:
        request.top_k = configs.top_k
    else:
        request.top_k = global_configs.model.default_top_k
    
    if configs.repetition_penalty is not None:
        request.repetition_penalty = configs.repetition_penalty
    else:
        request.repetition_penalty = global_configs.model.default_repetition_penalty
    
    if configs.frequency_penalty is not None:
        request.frequency_penalty = configs.frequency_penalty
    else:
        request.frequency_penalty = global_configs.model.default_frequency_penalty
    
    if configs.presence_penalty is not None:
        request.presence_penalty = configs.presence_penalty
    else:
        request.presence_penalty = global_configs.model.default_presence_penalty
    
    if configs.max_tokens is not None:
        request.max_tokens = configs.max_tokens
    else:
        request.max_tokens = global_configs.model.default_max_tokens
    
    if configs.max_completion_tokens is not None:
        request.max_completion_tokens = configs.max_completion_tokens
    else:
        request.max_completion_tokens = global_configs.model.default_max_completion_tokens
    
    if configs.stop is not None:
        request.stop = configs.stop
    else:
        request.stop = global_configs.model.default_stop
    
    if thinking is not None:
        request.thinking = thinking
    elif configs.thinking is not None:
        request.thinking = configs.thinking
    else:
        request.thinking = global_configs.model.default_thinking
    
    if configs.reasoning_effort is not None:
        request.reasoning_effort = configs.reasoning_effort
    else:
        request.reasoning_effort = global_configs.model.default_reasoning_effort
    
    if configs.send_user_id is not None:
        request.send_user_id = configs.send_user_id
    else:
        request.send_user_id = global_configs.callapi.send_user_id
    
    if fim_mode:
        request.fim_mode = fim_mode
        if user_input is not None:
            request.prompt = user_input.to_text()
        else:
            request.prompt = ""
        request.suffix = suffix

        if echo is not None:
            request.echo = echo
        elif configs.fim_echo is not None:
            request.echo = configs.fim_echo
        else:
            request.echo = global_configs.model.default_fim_echo

    if global_configs.model.enable_user_extra_bodys and extra_bodys is not None:
        request.extra_bodys.update(extra_bodys)
    if global_configs.model.extra_bodys:
        request.extra_bodys.update(global_configs.model.extra_bodys)
    if global_configs.model.enable_user_extra_bodys and configs.extra_bodys is not None:
        request.extra_bodys.update(configs.extra_bodys)
    if global_configs.model.extra_bodys_priority:
        request.extra_bodys.update(global_configs.model.extra_bodys_priority)
    
    request.stream = global_configs.model.stream
    request.stream_options.include_obfuscation = global_configs.callapi.include_obfuscation
    request.stream_options.include_usage = global_configs.callapi.include_usage
    request.output_role = assistant_role
    request.logprobs = global_configs.model.logprobs
    request.top_logprobs = global_configs.model.top_logprobs

    request.headers = {
        "User-Agent": global_configs.system_identification.system_ua
    }

    return request