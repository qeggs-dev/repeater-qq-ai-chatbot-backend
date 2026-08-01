from pydantic import BaseModel, ConfigDict
from .auxiliary import (
    Image,
    Background,
    OutputFormat,
    Quality,
    ImageSize,
    ImageTokenUsage,
)

class ImagesResponse(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    created: int = 0
    background: Background | None = None
    data: list[Image] | None = None
    output_format: OutputFormat | None = None
    quality: Quality | None = None
    size: ImageSize | str | None = None
    usage: ImageTokenUsage | None = None