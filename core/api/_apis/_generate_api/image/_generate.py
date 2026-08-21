
from ._router import image_router
from fastapi import Request as FastAPI_Request
from .....core.image import (
    Request,
    generate_image as generate_image_core
)

@image_router.post("/generate/{user_id}")
async def generate_image(
    user_id: str,
    request: Request,
    fastapi_request: FastAPI_Request
):
    """
    Generate image from prompt.
    """
    return await generate_image_core(
        user_id,
        request,
        fastapi_request
    )