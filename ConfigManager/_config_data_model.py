from pydantic import (
    BaseModel,
    field_validator,
    conint
)
from typing import Literal, List, Dict, Any

class Config_Item(BaseModel):
    type: Literal["int", "float", "str", "bool", "list", "dict", "json", "path", "auto", "other", None] = "auto"
    type_name: str | None = None
    system: str | None = None
    value: Any | None = None

    @field_validator("type_name")
    @classmethod
    def validate_type_name(cls, v, values):
        if v is None:
            return v
        if values["type"] in {"other", "auto"}:
            raise ValueError("type_name cannot be set if type is 'other' or 'auto'")
        return v

class Config_Model(BaseModel):
    name: str
    # version: str
    values: List[Config_Item]
    annotations: str | None = None