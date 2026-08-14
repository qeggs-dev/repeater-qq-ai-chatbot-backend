import uuid
import time
import orjson
from typing import AsyncGenerator

from .....call_api import (
    CompletedImageEvent,
    PartialImageEvent,
    ImageGenerateClient,
    ImagesRequest as ImagesRequest,
    Image,
    ImagesRuntime,
    ImagesResponse,
    ImageDownloader
)
from .....special_exception import (
    HTTPException,
)
from .....global_config_manager import ConfigManager
from .....runtime_container import RuntimeContainer
from ._router import image_router
from ._request import Request
from fastapi import Request as FastAPI_Request
from fastapi.responses import (
    ORJSONResponse,
    StreamingResponse
)
from .....request_log.objects import (
    ImageRequestLog
)
from loguru import logger
from ._delete_file import delete_file
from ._create_request_log import create_request_log
from ._image_fast_statistics import ImageFastStatistics

@image_router.post("/generate/{user_id}")
async def generate_image(
    user_id: str,
    request: Request,
    fastapi_request: FastAPI_Request
):
    """
    Generate image from prompt.
    """
    task_id = uuid.uuid4()
    logger.info(
        "Generate image task {task_id} start.",
        task_id = task_id
    )
    runtime = RuntimeContainer.get_runtime()
    model_client = runtime.model_info_client
    user_config_manager = runtime.user_config_manager
    user_configs = await user_config_manager.load(user_id)
    global_configs = ConfigManager.get_configs()

    model_id = request.model_id
    if model_id is None:
        model_id = user_configs.image_model_id
    if model_id is None:
        model_id = global_configs.model_api.default_image_model_id
    
    model = await model_client.get_random_model(
        model_id
    )

    timeout = user_configs.gen_image_timeout
    if timeout is None:
        timeout = global_configs.model.gen_image_timeout

    if timeout is None:
        timeout = model.timeout

    openai_pool = runtime.openai_pool
    image_generate_client = ImageGenerateClient(
        max_concurrency = 1000,
        download_chunk_size = global_configs.generated_images.download_chunk_size,
        file_name_prefix = global_configs.generated_images.file_name_prefix,
        base_dir = global_configs.generated_images.base_dir,
        save_file_suffix = global_configs.generated_images.save_file_suffix
    )

    header = {
        "User-Agent": global_configs.system_identification.system_ua
    }

    if model.api_key is None:
        raise HTTPException(
            status_code = 400,
            detail = "Model api key is not set."
        )

    image_request = ImagesRequest(
        url = model.get_base_url(),
        proxy = model.proxy,
        key = model.api_key,
        model = model.id,
        model_id = model_id,
        model_uid = model.uid,

        limits = model.limits,
        headers = header,
        timeout = timeout,

        images = request.images,
        prompt = request.prompt,
        background = request.background,
        moderation = request.moderation,
        n = request.n,
        output_compression = request.output_compression,
        output_format = request.output_format,
        partial_images = request.partial_images,
        quality = request.quality,
        response_format = request.response_format,
        size = request.size,
        stream = request.stream,
        style = request.style,
        user = request.user,
    )

    image_runtime = ImagesRuntime(
        client_pool = openai_pool
    )

    result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse
    downloader: ImageDownloader
    result, downloader = await image_generate_client.call(
        image_request,
        image_runtime
    )

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

        logger.info(
            "Generating fast statistics...",
            user_id = user_id
        )
        fs_start_time = time.perf_counter_ns()
        fast_statistics = ImageFastStatistics(request_log)
        fs_end_time = time.perf_counter_ns()

        fs_format_start_time = time.perf_counter_ns()
        fast_statistics_str = fast_statistics.get_statistics()
        fs_format_end_end = time.perf_counter_ns() 
        logger.info(
            "Fast Statistics (Operation Time: {fs_time:.2f}ms | Format Time: {format_time:.2f}ms):\n{content}",
            user_id = user_id,
            fs_time = (fs_end_time - fs_start_time) / 1e6,
            format_time = (fs_format_end_end - fs_format_start_time) / 1e6,
            content = fast_statistics_str
        )
        
        await runtime.request_log.add_request_log(
            request_log
        )
        
        return ORJSONResponse(
            result.model_dump(exclude_none = True),
            status_code = 200
        )
    else:
        async def stream(result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]):
            async for event, path in downloader.download_stream():
                # url = fastapi_request.url_for("files.generated_image", image_name = path.name)
                if global_configs.generated_images.image_timeout:
                    await runtime.delayed_tasks_pool.add_task(
                        sleep_time = global_configs.generated_images.image_timeout,
                        task = delete_file(
                            file = path
                        )
                    )
                yield orjson.dumps(event.model_dump(exclude_none = True)) + b"\n"
        
        return StreamingResponse(
            stream(result),
            status_code = 200
        )
        