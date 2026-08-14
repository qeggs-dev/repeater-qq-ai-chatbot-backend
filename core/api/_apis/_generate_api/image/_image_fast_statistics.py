from datetime import datetime, timezone
from .....request_log import ImageRequestLog

class ImageFastStatistics:
    def __init__(self, request_log: ImageRequestLog):
        self.request_log = request_log
        self.now = datetime.now()

    @staticmethod
    def centre_title(
            title: str,
            title_width: int = 40,
            fill_char: str = "="
        ):
        return f" {title} ".center(title_width, fill_char)

    def gen_statistics_lines(
        self,
        title_width: int = 40,
        fill_char: str = "="
    ):
        yield self.centre_title(
            "Image Statistics",
            title_width = title_width,
            fill_char = fill_char,
        )
        yield "Generating statistics..."
        yield f"Create Fast Statistics on {self.now.strftime('%Y-%m-%d %H:%M:%S.%f')}"
        yield self.centre_title(
            "Request Info",
            title_width = title_width,
            fill_char = fill_char,
        )
        yield f"API URL: {self.request_log.url}"
        yield f"Model: {self.request_log.model}"
        yield f"User ID: {self.request_log.user_id}"
        yield f"Task ID: {self.request_log.task_id}"
        yield f"Created Time(Local): {datetime.fromtimestamp(self.request_log.created_time)}"
        yield f"Created Time(UTC): {datetime.fromtimestamp(self.request_log.created_time, tz=timezone.utc)}"
        yield self.centre_title(
            "Token Count", 
            title_width = title_width,
            fill_char = fill_char,
        )
        yield f"Input Tokens: {self.request_log.input_tokens}"
        yield f"  - Image Tokens: {self.request_log.input_image_tokens}"
        yield f"  - Text Tokens: {self.request_log.input_text_tokens}"
        yield f"Output Tokens: {self.request_log.output_tokens}"
        yield f"  - Image Tokens: {self.request_log.output_image_tokens}"
        yield f"  - Text Tokens: {self.request_log.output_text_tokens}"
        yield f"Total Tokens: {self.request_log.total_tokens}"
        yield fill_char * title_width

    def get_statistics(self) -> str:
        return "\n".join(self.gen_statistics_lines())