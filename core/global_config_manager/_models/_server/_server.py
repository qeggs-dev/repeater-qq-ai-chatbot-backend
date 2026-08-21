import ssl
from pydantic import BaseModel, Field
from typing import Any, Literal
from ._uvicron import UvicronConfig

class ServerConfig(BaseModel):
    uvicorn: UvicronConfig = Field(default_factory=UvicronConfig)
    restart: bool = False
    run_server: bool = True
    asyncio_debug: bool = False