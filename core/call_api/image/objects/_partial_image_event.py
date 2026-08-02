from pydantic import BaseModel, ConfigDict
from .auxiliary.background import Background
from .auxiliary.output_format import OutputFormat
from .auxiliary.quality import Quality
from .auxiliary.size import ImageSize
from typing import Literal

class PartialImageEvent(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    b64_json: str | None = None
    background: Background | None = None
    created_at: int | None = None
    output_format: OutputFormat | None = None
    partial_image_index: int | None = None
    quality: Quality | None = None
    size: ImageSize | None = None
    type: Literal["image_generation.partial_image"] = "image_generation.partial_image"