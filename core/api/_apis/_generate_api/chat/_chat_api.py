import uuid
import orjson
import asyncio

from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Coroutine
)
from fastapi.responses import (
    ORJSONResponse,
    StreamingResponse
)

from core.context.objects._content_unit import ContentUnit
from .....special_exception import (
    HTTPException
)
from .....repeater_main import RepeaterMain
from .....assist_struct import Response
from .....call_api.completions_api import Delta
from ._router import chat_router
from ._requests import (
    ChatRequest
)

@chat_router.post("/completion/{user_id}")
async def chat_endpoint(
    user_id: str,
    request: ChatRequest
):
    """
    Endpoint for chat
    """
    server = RepeaterMain.get_now_server()
    task_id = request.task_id or uuid.uuid4()
    chat_coroutine: Coroutine[Any, Any, Response | AsyncGenerator[Delta | ContentUnit, None]] = server.core.chat(
        user_id = user_id,
        task_id = task_id,
        message = request.message,
        suffix = request.suffix,
        echo = request.echo,
        fim_mode = request.fim_mode,
        history_messages = request.history_messages,
        history_msg_role_map = request.history_msg_role_map,
        user_info = request.user_info,
        role = request.role,
        assistant_role = request.assistant_role,
        role_name = request.role_name,
        extra_template_fields = request.extra_template_fields,
        temporary_prompt = request.temporary_prompt,
        additional_data = request.additional_data,
        model_id = request.model_id,
        thinking = request.thinking,
        load_prompt = request.load_prompt,
        save_context = request.save_context,
        save_new_only = request.save_new_only,
        cross_user_data_routing = request.cross_user_data_routing,
        allowed_tool_calls = request.allowed_tool_calls,
        stream = request.stream,
        extra_bodys = request.extra_bodys
    )
    try:
        response = await server.runtime.chat_task_pool.run_task(
            user_id = user_id,
            task_id = str(task_id),
            coro = chat_coroutine
        )
    except asyncio.CancelledError:
        raise HTTPException(
            detail = "Chat Completion Task Cancelled or System Abnormal Shutdown.",
            status_code = 409 # Conflict
        )
        
    if isinstance(response, Response):
        return ORJSONResponse(
            response.model_dump(
                exclude_none = True
            ),
            status_code=response.status
        )
    else:
        async def generator_wrapper(context: AsyncGenerator[Delta | ContentUnit, None]) -> AsyncGenerator[bytes, None]:
            async for chunk in context:
                yield orjson.dumps(chunk.model_dump(exclude_none=True)) + b"\n"

        return StreamingResponse(generator_wrapper(response), media_type="application/x-ndjson")