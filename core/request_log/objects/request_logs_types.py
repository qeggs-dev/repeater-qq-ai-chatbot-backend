from typing import Union
from .chat_request_log import RequestLog
from .image_request_log import ImageRequestLog

RequestLogTypes = Union[RequestLog, ImageRequestLog]