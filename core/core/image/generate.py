import uuid
import time
from typing import AsyncGenerator

from ...call_api import (
    CompletedImageEvent,
    PartialImageEvent,
    ImageGenerateClient,
    ImagesRequest as ImagesRequest,
    ImagesRuntime,
    ImagesResponse,
    ImageDownloader
)
from ...special_exception import (
    HTTPException,
)
from ...global_config_manager import ConfigManager
from ...runtime_container import RuntimeContainer
from .request import Request
from fastapi import Request as FastAPI_Request
from .make_request import make_request
from .get_model import get_model
from .parse_response import parse_response
from loguru import logger

async def generate_image(
    user_id: str,
    request: Request,
    fastapi_request: FastAPI_Request
):
    """
    Generate image from prompt.
    """
    task_start_time = time.perf_counter_ns()
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

    model_id, model = await get_model(
        model_id = request.model_id,
        model_client = model_client,
        user_configs = user_configs,
        global_configs = global_configs
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

    image_request = make_request(
        request = request,
        model = model,
        model_id = model_id,
        header = header,
        timeout = timeout
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
    task_finished_time = time.perf_counter_ns()

    return await parse_response(
        request = request,
        user_id = user_id,
        task_id = task_id,
        task_start_time = task_start_time,
        task_finished_time = task_finished_time,
        model = model,
        fastapi_request = fastapi_request,
        global_configs = global_configs,
        runtime = runtime,
        result = result,
        downloader = downloader
    )