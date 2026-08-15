import time
from datetime import datetime, timezone
from .request import Request
from ...request_log import ImageRequestLog
from loguru import logger

class ImageFastStatistics:
    def __init__(
            self,
            request: Request,
            request_log: ImageRequestLog
        ):
        self.request = request
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
        if self.request.images:
            yield f"Input Image Count: {len(self.request.images)}"
        yield f"Prompt: \n{self.request.prompt}"
        if self.request.background:
            yield f"Background: {self.request.background.value}"
        if self.request.moderation:
            yield f"Moderation: {self.request.moderation.value}"
        yield f"Generation Count: {self.request.n}"
        if self.request.output_compression:
            yield f"Output Compression: {self.request.output_compression}"
        if self.request.output_format:
            yield f"Output Format: {self.request.output_format.value}"
        if self.request.partial_images:
            yield f"Partial Images: {self.request.partial_images}"
        if self.request.quality:
            yield f"Quality: {self.request.quality.value}"
        if self.request.response_format:
            yield f"Response Format: {self.request.response_format.value}"
        if self.request.size:
            yield f"Size: {self.request.size}"
        yield f"Stream: {self.request.stream}"
        if self.request.style:
            yield f"Style: {self.request.style.value}"
        yield f"User: {self.request.user}"
        yield f"Raw Response: {self.request.raw_response}"
        if isinstance(self.request_log.created_time, int):
            yield f"Created Time(Local): {datetime.fromtimestamp(self.request_log.created_time)}"
            yield f"Created Time(UTC): {datetime.fromtimestamp(self.request_log.created_time, tz=timezone.utc)}"
        elif isinstance(self.request_log.created_time, list):
            for index, created_time in enumerate(self.request_log.created_time):
                yield f"Index: {index}"
                yield f"  - Created Time(Local): {datetime.fromtimestamp(created_time)}"
                yield f"  - Created Time(UTC): {datetime.fromtimestamp(created_time, tz=timezone.utc)}"
        else:
            yield f"Created Time: {self.request_log.created_time}"
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

def log_statistics(
        request: Request,
        request_log: ImageRequestLog
    ) -> None:
    logger.info(
        "Generating fast statistics...",
        user_id = request_log.user_id
    )
    fs_start_time = time.perf_counter_ns()
    fast_statistics = ImageFastStatistics(
        request,
        request_log
    )
    fs_end_time = time.perf_counter_ns()

    fs_format_start_time = time.perf_counter_ns()
    fast_statistics_str = fast_statistics.get_statistics()
    fs_format_end_end = time.perf_counter_ns() 
    logger.info(
        "Fast Statistics (Operation Time: {fs_time:.2f}ms | Format Time: {format_time:.2f}ms):\n{content}",
        user_id = request_log.user_id,
        fs_time = (fs_end_time - fs_start_time) / 1e6,
        format_time = (fs_format_end_end - fs_format_start_time) / 1e6,
        content = fast_statistics_str
    )