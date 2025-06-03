from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class CallLogObject:
    """
    Class to represent a call log object.
    """
    id: str = ""
    url: str = ""
    model: str = ""
    user_id: str = ""
    user_name: str = ""

    total_chunk: int = 0
    empty_chunk: int = 0

    task_start_time: int = 0
    task_end_time: int = 0
    request_start_time: int = 0
    request_end_time: int = 0
    stream_processing_start_time: int = 0
    stream_processing_end_time: int = 0
    call_prepare_start_time: int = 0
    call_prepare_end_time: int = 0
    chunk_times: list = field(default_factory=list)
    created_time: int = 0

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cache_hit_count: int = 0
    cache_miss_count: int = 0

    total_context_length: int = 0
    reasoning_content_length: int = 0
    new_content_length: int = 0

    @property
    def as_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict[str: Any]):
        return cls(**data)