from pydantic import BaseModel

class Image(BaseModel):
    b64_json: str | None = None
    revised_prompt: str | None = None
    url: str | None = None