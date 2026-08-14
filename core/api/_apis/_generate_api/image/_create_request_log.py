from uuid import UUID
from .....request_log import ImageRequestLog
from .....call_api.image import (
    ImageTokenUsage
)
from .....clients.model_info import ModelInfo

def create_request_log(
    user_id: str,
    task_id: UUID,
    model: ModelInfo,
    created_time: int,
    image_token_usage: ImageTokenUsage | None = None,
) -> ImageRequestLog:
    request_log = ImageRequestLog(
        url = model.get_base_url(),
        model = model.id,
        user_id = user_id,
        task_id = str(task_id),
        created_time = created_time,
    )

    if image_token_usage:
        request_log.input_tokens = image_token_usage.input_tokens
        if image_token_usage.input_tokens_details:
            request_log.input_image_tokens = image_token_usage.input_tokens_details.image_tokens
            request_log.input_text_tokens = image_token_usage.input_tokens_details.text_tokens
        request_log.output_tokens = image_token_usage.output_tokens
        request_log.total_tokens = image_token_usage.total_tokens
        if image_token_usage.output_tokens_details:
            request_log.output_image_tokens = image_token_usage.output_tokens_details.image_tokens
            request_log.output_text_tokens = image_token_usage.output_tokens_details.text_tokens
    
    return request_log