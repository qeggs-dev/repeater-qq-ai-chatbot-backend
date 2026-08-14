import random
import asyncio

from .....auxiliary.async_tools.aioping.executor import Response
from fastapi.responses import ORJSONResponse
from .._send_ping import send_ping, Detail
from .....global_config_manager import ConfigManager
from .....repeater_main import RepeaterMain
from .....special_exception import HTTPException
from .._router import ping_provider_router
from .request import PingRequest
from .response import PingResponse, PingDetail

@ping_provider_router.post("/{user_id}")
async def ping_provider(user_id: str, request: PingRequest):
    global_config = ConfigManager.get_configs()
    server = RepeaterMain.get_now_server()
    runtime = server.runtime
    user_configs = await runtime.user_config_manager.load(user_id)

    model_ids = request.model_id

    if model_ids is None:
        model_ids = user_configs.model_id
    if model_ids is None:
        model_ids = global_config.model_api.default_model_id
    
    model_info = await runtime.model_info_client.get_model_list(model_ids)
    
    model_urls = {model.base_url if model.proxy is None else model.proxy for model in model_info}
    
    timeout = request.timeout
    if timeout is None:
        timeout = global_config.model_api.ping_provider.timeout
    times = request.times
    if times is None:
        times = global_config.model_api.ping_provider.times
    size = request.size
    if size is None:
        size = global_config.model_api.ping_provider.size
    interval = request.interval
    if interval is None:
        interval = global_config.model_api.ping_provider.interval
    
    ping_details = [
        Detail(
            url = model_url,
            timeout = timeout,
            times = times,
            size = size,
            interval = interval,
        )
        for model_url in model_urls
    ]

    tasks = [
        asyncio.create_task(
            send_ping(detail)
        )
        for detail in ping_details
    ]

    responses = await asyncio.gather(*tasks)

    success_count: int = 0
    time_ms: list[float] = []
    details: list[Detail] = []

    for model_info in responses:
        detail = PingDetail(
            host_names = model_info.host_names,
            ip = model_info.ip,
        )
        total_time_ms: float = 0.0
        ping_response = model_info.responses
        for ping_detail in ping_response:
            ping_detail: Response

            if ping_detail.success:
                success_count += 1
            
            time_ms.append(ping_detail.time_elapsed_ms)
            detail.time.append(ping_detail.time_elapsed_ms)

            total_time_ms += ping_detail.time_elapsed_ms
            if ping_detail.time_elapsed_ms > detail.max_time:
                detail.max_time = ping_detail.time_elapsed_ms
            if ping_detail.time_elapsed_ms < detail.min_time or detail.min_time == 0.0:
                detail.min_time = ping_detail.time_elapsed_ms
        
        detail.avg_time = total_time_ms / len(ping_response)
        detail.packet_loss = ping_response.packet_loss
        details.append(detail)

    return ORJSONResponse(
        content = PingResponse(
            success_count = success_count,
            average_time_spent = sum(time_ms) / len(time_ms) if len(time_ms) > 0 else 0,
            details = details
        ).model_dump()
    )
