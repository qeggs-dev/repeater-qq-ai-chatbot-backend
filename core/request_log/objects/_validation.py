from .request_logs_types import RequestLogTypes
from pydantic import validate_call

@validate_call
def validate_request_log(request_log_type: RequestLogTypes) -> RequestLogTypes:
    """
    Validate the request log type.

    Args:
        request_log_type (RequestLogTypes): The request log type.

    Returns:
        RequestLogTypes: The validated request log type.
    """
    return request_log_type

