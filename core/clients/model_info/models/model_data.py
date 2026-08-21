import time
from pydantic import BaseModel, Field
from .architecture import Architecture
from .pricing import Pricing
from .top_provider import TopProvider
from .supported_parameters import SupportedParameters
from .links import Links

class ModelAPIData(BaseModel):
    id: str | None = None
    canonical_slug: str | None = None
    hugging_face_id: str | None = None
    name: str | None = None
    created: int | None = None
    description: str | None = None
    context_length: int | None = None
    architecture: Architecture | None = None
    pricing: Pricing | None = None
    top_provider: TopProvider | None = None
    per_request_limits: None = None
    supported_parameters: list[SupportedParameters | str] | None = None
    knowledge_cutoff: str | None = None
    expiration_date: str | None = None
    links: Links | None = None
    disable_to: int | None = None

    def disable(self, timeout: int):
        now = time.time_ns()
        self.disable_to = now + timeout

class ModelAPIResponse(BaseModel):
    data: list[ModelAPIData] = Field(default_factory=list)