import base64

from pydantic import BaseModel
from typing import Literal

class Base64File(BaseModel):
    type: Literal["base64"] = "base64"
    data: str

    async def get_file(self) -> bytes:
        return base64.b64decode(self.data)