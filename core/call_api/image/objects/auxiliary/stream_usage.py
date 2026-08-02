from pydantic import BaseModel
from .image_usage_tokens_details import ImageUsageTokensDetails

class StreamUsage(BaseModel):
    input_tokens: int | None = None
    input_tokens_details: ImageUsageTokensDetails | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None