from dataclasses import dataclass, asdict, field
from typing import Callable, Coroutine

from ..Context import ContextObject
from ..CallLog import CallLog

@dataclass
class TokensCount:
    """
    Dataclass to store the token usage data for a given date.
    """
    prompt_tokens = 0
    completion_tokens  = 0
    total_tokens = 0
    prompt_cache_hit_tokens = 0
    prompt_cache_miss_tokens = 0
    
    @property
    def as_dict(self) -> dict[str, int]:
        return asdict(self)

@dataclass
class Top_Logprob:
    token: str = ""
    logprob: float = 0.0

@dataclass
class Logprob:
    """
    Dataclass to store the logprobs data for a given date.
    """
    token: str = ""
    logprob: float = 0.0
    top_logprobs: list[Top_Logprob] = field(default_factory=list)

@dataclass
class Delta:
    """
    Dataclass to store the delta data for a given date.
    """
    id: str = ""
    reasoning_content: str = ""
    content: str = ""
    function_id: str | None = None
    function_type: str | None = None
    function_name: str | None = None
    function_arguments: str | None = None
    token_usage: TokensCount | None = None
    created: int = 0
    model: str = ""
    system_fingerprint: str = ""
    logprobs: list[Logprob] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """
        Check if the delta data is empty.
        """
        return not (self.reasoning_content or self.content or self.function_name or self.function_arguments or self.token_usage)

@dataclass
class Request:
    """
    This class is used to store the request data
    """
    url: str = ""
    key: str = ""
    model: str = ""
    user_name: str = ""
    temperature: float = 1.0
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    max_tokens: int = 0
    max_completion_tokens: int = 0
    stream: bool = False
    stop: list[str] | None = None
    context: ContextObject | None = None
    logprobs: bool = False
    top_logprobs: int | None = None
    print_chunk: bool = True
    continue_processing_callback_function: Callable[[str, Delta], bool] | None = None

@dataclass
class Response:
    """
    This class is used to store the response data
    """
    id: str = ""
    context: ContextObject | None = None
    created: int = 0
    model: str = ""
    token_usage: TokensCount | None = None
    stream: bool = False

    stream_processing_start_time_ns:int = 0
    stream_processing_end_time_ns:int = 0
    chunk_times: list[int] = field(default_factory=list)
    finish_reason: str = ""
    system_fingerprint: str = ""
    logprobs: list[Logprob] | None = None
    calling_log: CallLog | None = None

