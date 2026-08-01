import httpx

from pydantic import BaseModel
from typing import Literal

class UrlFile(BaseModel):
    type: Literal["url"] = "url"
    url: str

    async def get_file(self) -> bytes:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.url)
            return response.content
