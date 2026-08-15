from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal
from ..timestamp_object import TimeStamp
from .._logprob import Logprob

class BaseRequestLog(BaseModel):
    """
    Class to represent a request log object.
    """
    model_config = ConfigDict(
        validate_assignment=True,
    )

    type: Literal["repeater.request_log.chat"] = "repeater.request_log.chat"
    
    url: str = ""
    model: str = ""
    user_id: str = ""
    task_id: str = ""
    
    created_time: int | list[int] = 0