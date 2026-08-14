from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal
from .base_request_log import BaseRequestLog

class ImageRequestLog(BaseRequestLog):
    """
    Class to represent a generate image request log object.
    """
    model_config = ConfigDict(
        validate_assignment=True,
    )

    type: Literal["repeater.request_log.image"] = "repeater.request_log.image"

    input_tokens: int | None = None
    input_image_tokens: int | None = None
    input_text_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    output_image_tokens: int | None = None
    output_text_tokens: int | None = None