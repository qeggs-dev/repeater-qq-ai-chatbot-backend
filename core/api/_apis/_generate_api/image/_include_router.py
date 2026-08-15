from .._router import generate_router
from ._router import image_router

generate_router.include_router(image_router)