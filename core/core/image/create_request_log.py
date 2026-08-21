from uuid import UUID
from ...request_log import ImageRequestLog
from ...call_api.image import (
    ImageTokenUsage,
    StreamUsage
)
from ...clients.model_info import ModelInfo

def create_request_log(
    user_id: str,
    task_id: UUID,
    model: ModelInfo,
    created_time: int | list[int],
    image_token_usage: ImageTokenUsage | StreamUsage | None = None,
) -> ImageRequestLog:
    request_log = ImageRequestLog(
        url = model.get_base_url(),
        model = model.id,
        user_id = user_id,
        task_id = str(task_id),
        created_time = created_time,
    )

    if isinstance(image_token_usage, ImageTokenUsage):
        _fill_image_token_usage(image_token_usage, request_log)
    elif isinstance(image_token_usage, StreamUsage):
        _fill_stream_token_usage(image_token_usage, request_log)
    else:
        raise TypeError("image_token_usage must be ImageTokenUsage or StreamUsage")
    
    return request_log

def _fill_image_token_usage(
    image_token_usage: ImageTokenUsage,
    request_log: ImageRequestLog,
) -> None:
    request_log.input_tokens = image_token_usage.input_tokens
    if image_token_usage.input_tokens_details:
        request_log.input_image_tokens = image_token_usage.input_tokens_details.image_tokens
        request_log.input_text_tokens = image_token_usage.input_tokens_details.text_tokens
    request_log.output_tokens = image_token_usage.output_tokens
    request_log.total_tokens = image_token_usage.total_tokens
    if image_token_usage.output_tokens_details:
        request_log.output_image_tokens = image_token_usage.output_tokens_details.image_tokens
        request_log.output_text_tokens = image_token_usage.output_tokens_details.text_tokens

def _fill_stream_token_usage(
    stream_usage: StreamUsage,
    request_log: ImageRequestLog,
) -> None:
    request_log.input_tokens = stream_usage.input_tokens
    if stream_usage.input_tokens_details:
        request_log.input_image_tokens = stream_usage.input_tokens_details.image_tokens
        request_log.input_text_tokens = stream_usage.input_tokens_details.text_tokens
    request_log.output_tokens = stream_usage.output_tokens
    request_log.total_tokens = stream_usage.total_tokens