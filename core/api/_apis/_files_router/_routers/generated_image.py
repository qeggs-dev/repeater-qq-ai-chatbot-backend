from .._router import files_router
from .....auxiliary.path import validate_path
from .....global_config_manager import ConfigManager
from .....special_exception import HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

@files_router.get("/generated_image/{image_name}", name = "files.generated_image")
async def generated_image(image_name: str):
    global_configs = ConfigManager.get_configs()

    base_dir = global_configs.generated_images.base_dir
    if not validate_path(base_dir, image_name):
        raise HTTPException(
            status_code = 400,
            detail = "Invalid image name"
        )

    return FileResponse(
        Path(base_dir) / image_name,
        status_code = 200,
    )