from pydantic import BaseModel, ConfigDict, Field
from typing import Any
from .auxiliary import (
    Background,
    Moderation,
    OutputFormat,
    Quality,
    ImageResponseFormat,
    ImageSize,
    ImageStyle,
    FILE_TYPES
)
from ....auxiliary.http import (
    ClientLimits,
    ClientTimeout
)

class ImagesRequest(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True
    )

    url: str = ""
    proxy: str | None = None
    limits: ClientLimits = Field(default_factory=ClientLimits)
    encoding: str = "utf-8"
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    cookies: dict[str, Any] = Field(default_factory=dict)
    timeout: int | float | ClientTimeout = 600.0

    model: str = ""
    model_id: str | list[str] = ""
    model_uid: str = ""
    key: str = ""
    
    images: list[FILE_TYPES] | None = None
    prompt: str = Field(...)
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