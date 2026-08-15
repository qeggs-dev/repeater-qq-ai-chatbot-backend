from pydantic import BaseModel, ConfigDict
from ...call_api.image import (
    Background,
    Moderation,
    OutputFormat,
    Quality,
    ImageResponseFormat,
    ImageSize,
    ImageStyle,
    FILE_TYPES
)

class Request(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )
    
    model_id: str | list[str] | None = None
    images: list[FILE_TYPES] | None = None
    prompt: str = ""
    
    background: Background | None = None
    moderation: Moderation | None = None
    n: int | None = None
    output_compression: int | None = None
    output_format: OutputFormat | None = None
    partial_images: int | None = None
    quality: Quality | None = None
    response_format: ImageResponseFormat | None = None
    size: ImageSize | str | None = None
    stream: bool = False
    style: ImageStyle | None = None
    user: str | None = None
    raw_response: bool = False