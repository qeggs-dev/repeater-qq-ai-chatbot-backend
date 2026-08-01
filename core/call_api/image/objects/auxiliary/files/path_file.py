import aiofiles

from pydantic import BaseModel
from typing import Literal

class PathFile(BaseModel):
    type: Literal["path"] = "path"
    path: str

    async def get_file(self) -> bytes:
        async with aiofiles.open(self.path, "rb") as file:
            return await file.read()
