
from typing import Any
from ...auxiliary.http import ClientTimeout
from ...call_api.image import ImagesRequest
from ...clients.model_info import ModelInfo
from ...special_exception import HTTPException
from .request import Request

def make_request(
    request: Request,
    model: ModelInfo,
    model_id: str | list[str],
    header: dict[str, Any],
    timeout: int | float | ClientTimeout,
) -> ImagesRequest:
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

    return image_request