from dataclasses import dataclass, field

from environs import Env

env = Env()

@dataclass
class ApiGroup:
    url: str = ""
    api_key_envname: str = ""
    group_name: str = ""
    model_name: str = ""
    model_id: str = ""
    model_type: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def api_key(self) -> str:
        return env.str(self.api_key_envname, '')