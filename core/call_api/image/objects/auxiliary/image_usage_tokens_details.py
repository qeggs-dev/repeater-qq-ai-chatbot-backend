from pydantic import BaseModel

class ImageUsageTokensDetails(BaseModel):
    image_tokens: int | None = None
    text_tokens: int | None = None