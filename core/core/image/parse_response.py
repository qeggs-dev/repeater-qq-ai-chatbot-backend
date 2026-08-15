import time
import orjson
from uuid import UUID
from ...call_api.image import (
    ImagesResponse,
    ImageDownloader,
    Image,
    PartialImageEvent,
    CompletedImageEvent
)
from ...clients.model_info import ModelInfo
from fastapi import Request as FastAPI_Request
from fastapi.responses import ORJSONResponse, StreamingResponse
from ...global_config_manager import GlobalConfigs
from ...runtime_container import RepeaterRuntime
from .delete_file import delete_file
from .create_request_log import create_request_log
from .request import Request
from typing import AsyncGenerator
from .image_fast_statistics import log_statistics

async def parse_response(
    request: Request,
    user_id: str,
    task_id: UUID,
    task_start_time: int,
    task_finished_time: int,
    model: ModelInfo,
    fastapi_request: FastAPI_Request,
    global_configs: GlobalConfigs,
    runtime: RepeaterRuntime,
    result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse,
    downloader: ImageDownloader
):
    if isinstance(result, ImagesResponse):
        images: list[Image] = []
        async for response, path in downloader.download():
            url = fastapi_request.url_for("files.generated_image", image_name = path.name)
            images.append(
                Image(
                    url = str(url),
                )
            )
            if global_configs.generated_images.image_timeout:
                await runtime.delayed_tasks_pool.add_task(
                    sleep_time = global_configs.generated_images.image_timeout,
                    task = delete_file(
                        file = path
                    )
                )
        
        if not request.raw_response:
            result.data = images

        request_log = create_request_log(
            user_id = user_id,
            task_id = task_id,
            model = model,
            created_time = response.created,
            image_token_usage = response.usage,
        )
        
        await runtime.request_log.add_request_log(
            request_log
        )

        log_statistics(request_log)
        
        return ORJSONResponse(
            result.model_dump(exclude_none = True),
            status_code = 200
        )
    else:
        async def stream(result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]):
            create_at: list[int] = []
            async for event, path in downloader.download_stream():
                # url = fastapi_request.url_for("files.generated_image", image_name = path.name)
                if global_configs.generated_images.image_timeout:
                    await runtime.delayed_tasks_pool.add_task(
                        sleep_time = global_configs.generated_images.image_timeout,
                        task = delete_file(
                            file = path
                        )
                    )
                if event.created_at:
                    create_at.append(event.created_at)
                yield orjson.dumps(event.model_dump(exclude_none = True)) + b"\n"
                
                if isinstance(event, CompletedImageEvent):
                    request_log = create_request_log(
                        user_id = user_id,
                        task_id = task_id,
                        model = model,
                        created_time = create_at,
                        image_token_usage = event.usage,
                    )
        
        return StreamingResponse(
            stream(result),
            status_code = 200
        )
        