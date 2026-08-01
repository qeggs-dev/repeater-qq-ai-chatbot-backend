import orjson
from typing import AsyncGenerator

from .....call_api import (
    CompletedImageEvent,
    PartialImageEvent,
    ImageGenerateClient,
    ImagesRequest as ImagesRequest,
    ImagesRuntime,
    ImagesResponse
)
from .....special_exception import (
    HTTPException,
)
from .....global_config_manager import ConfigManager
from .....runtime_container import RuntimeContainer
from ._router import image_router
from ._request import Request
from fastapi.responses import (
    ORJSONResponse,
    StreamingResponse
)

@image_router.post("/generate/{user_id}")
async def generate_image(
    user_id: str,
    request: Request,
):
    """
    Generate image from prompt.
    """
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

    openai_pool = runtime.openai_pool
    image_generate_client = ImageGenerateClient(
        max_concurrency = 1000
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
        timeout = model.timeout,

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

    result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None] | ImagesResponse = await image_generate_client.call(
        image_request,
        image_runtime
    )

    if isinstance(result, ImagesResponse):
        return ORJSONResponse(
            result.model_dump(),
            status_code = 200
        )
    else:
        async def stream(result: AsyncGenerator[PartialImageEvent | CompletedImageEvent, None]):
            async for image in result:
                yield orjson.dumps(image.model_dump()) + b"\n"
        
        return StreamingResponse(
            stream(result),
            status_code = 200
        )
        