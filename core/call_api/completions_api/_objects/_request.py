from pydantic import BaseModel, Field, ConfigDict
from typing import Callable, Any
from ._stream_options import StreamOptions
from ....context import (
    ContentRole
)
from ....global_config_manager import (
    ReasoningEffort,
    ServiceTier
)
from ....context import Context
from ._interface_type import InterfaceType
from ....auxiliary.http import (
    ClientLimits,
    ClientTimeout
)

class Request(BaseModel):
    """
    This class is used to store the request data
    """
    model_config = ConfigDict(
        validate_assignment = True
    )

    url: str = ""
    proxy: str | None = None
    limits: ClientLimits = Field(default_factory=ClientLimits)
    encoding: str = "utf-8"
    headers: dict[str, Any] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    cookies: dict[str, Any] = Field(default_factory=dict)
    timeout: int | float | ClientTimeout = 600.0
    interface: InterfaceType = InterfaceType.OPENAI
    service_tier: ServiceTier | None = None

    model: str = ""
    model_id: str | list[str] = ""
    model_uid: str = ""
    key: str = ""

    user_name: str | None = None

    temperature: float | None = None
    top_a: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    seed: int | None = None
    repetition_penalty: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    max_tokens: int | None = None
    max_completion_tokens: int | None = None
    stream: bool = False
    thinking: bool | None = None
    stop: list[str] | None = None
    stream_options: StreamOptions = Field(default_factory=StreamOptions)
    reasoning_effort: ReasoningEffort | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = None

    context: Context | None = None
    prompt: str | None = None
    echo: bool | None = None
    suffix: str | None = None

    fim_mode: bool = False
    
    remove_reasoning_prompt: bool = True
    tool_calling_remove_reasoning: bool = True
    remove_created: bool = True
    
    print_chunk: bool = True
    send_user_id: bool = False
    output_role: ContentRole = ContentRole.ASSISTANT

    tools: list[dict[str, Any]] | None = None
    tool_choice: str | dict[str, str | dict[str, str]] | None = None

    extra_bodys: dict[str, Any] = Field(default_factory=dict)