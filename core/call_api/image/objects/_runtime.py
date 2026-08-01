from dataclasses import dataclass, field
from ....pools.openai_pool import OpenAIPool

@dataclass
class ImagesRuntime:
    client_pool: OpenAIPool = field(default_factory=OpenAIPool)
    