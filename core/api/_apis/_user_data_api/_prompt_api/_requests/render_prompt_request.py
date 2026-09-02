from pydantic import BaseModel
from ......assist_struct import RequestUserInfo

class RenderPromptRequest(BaseModel):
    model_id: str | None = None
    user_info: RequestUserInfo | None = None