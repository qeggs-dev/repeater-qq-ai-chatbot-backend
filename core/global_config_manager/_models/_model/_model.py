from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from ._reasoning_effort import ReasoningEffort
from ._service_tier import ServiceTier

class ModelConfig(BaseModel):
    default_timeout: float = Field(default=600.0, ge = 0.0)
    default_seed: int | None = None
    default_temperature: float | None = Field(default=0.7, ge = 0.0, le = 2.0)
    default_top_a: float | None = Field(default=None, ge = 0.0)
    default_top_p: float | None = Field(default=None, ge = 0.0, le = 1.0)
    default_top_k: int | None = Field(default=None, ge = 1)
    default_max_tokens: int | None = Field(default=None, ge = 0)
    default_max_completion_tokens: int | None = Field(default=None, ge = 0)
    default_repetition_penalty: float | None = Field(default=None, gt = 0.0, le = 2.0)
    default_frequency_penalty: float | None = Field(default=None, ge = -2.0, le = 2.0)
    default_presence_penalty: float | None = Field(default=None, ge = -2.0, le = 2.0)
    default_stop: list[str] | None = None
    default_thinking: bool | None = None
    default_fim_echo: bool | None = None
    default_reasoning_effort: ReasoningEffort | None = None
    default_service_tier: ServiceTier | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = Field(default=None, ge = 0)
    stream: bool = True
    extra_bodys: dict[str, Any] | None = None