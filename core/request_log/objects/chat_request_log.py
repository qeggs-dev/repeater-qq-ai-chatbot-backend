from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal
from ..timestamp_object import TimeStamp
from .._logprob import Logprob
from .base_request_log import BaseRequestLog

class RequestLog(BaseRequestLog):
    """
    Class to represent a request log object.
    """
    model_config = ConfigDict(
        validate_assignment=True,
    )

    type: Literal["repeater.request_log.chat"] = "repeater.request_log.chat"

    id: str = ""
    user_name: str | None = None
    stream: bool = True

    total_chunk: int = 0
    empty_chunk: int = 0

    task_start_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    prepare_start_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    prepare_end_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    request_start_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    request_end_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    stream_processing_start_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    stream_processing_end_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    task_end_time: TimeStamp = Field(default_factory=lambda: TimeStamp(timestamp=0, monotonic=0))
    chunk_generated_times: list[TimeStamp] = Field(default_factory=list)
    translation_chunk_times: list[TimeStamp] = Field(default_factory=list)
    translation_queue_backlog: list[int] = Field(default_factory=list)
    chunk_times: list[TimeStamp] = Field(default_factory=list)
    queue_backlog: list[int] = Field(default_factory=list)

    total_tokens: int | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cache_hit_count: int | None = None
    cache_miss_count: int | None = None
    logprob: Logprob | list[Logprob] | None = None

    total_context_length: int = 0
    reasoning_content_length: int = 0
    new_content_length: int = 0