import orjson
import numpy as np

from datetime import datetime, timezone
from typing import Generator, Callable, ClassVar, Self
from ..._objects import (
    Request,
    Response,
)
from ..chunk import ChunkStatistics
from ..format import (
    format_title,
    format_special_values,
    format_timedelta,
    format_token
)
from .running_time import RunningTime
from .runtimer import Runtimer

class FastStatistics:
    def __init__(
        self,
        user_id: str,
        request: Request,
        response: Response,
    ) -> None:
        self.now = datetime.now()
        self.user_id = user_id
        self.request = request
        self.response = response
        
        self.total_time = response.request_log.stream_processing_end_time.monotonic - response.request_log.request_start_time.monotonic
        self.preprocessing_time = response.request_log.prepare_end_time.monotonic - response.request_log.prepare_start_time.monotonic
        self.requests_time = response.request_log.request_end_time.monotonic - response.request_log.request_start_time.monotonic
        self.stream_processing_time = response.request_log.stream_processing_end_time.monotonic - response.request_log.stream_processing_start_time.monotonic
        
        if response.token_usage is not None:
            generation_speed = response.token_usage.completion_tokens / (self.stream_processing_time / 1e9)
        else:
            generation_speed = 0.0

        self.generation_speed = generation_speed

        self.created_utc_dt = datetime.fromtimestamp(response.created, tz=timezone.utc)
        self.created_utc_str = self.created_utc_dt.strftime("%Y-%m-%d %H:%M:%S (UTC)")

        self.created_local_dt = datetime.fromtimestamp(response.created)
        self.created_local_str = self.created_local_dt.strftime("%Y-%m-%d %H:%M:%S (Local)")

        self.generated_chunk_statistics = ChunkStatistics(
            name = "Generated",
            request_log = response.request_log,
            raw_timestamps = [timestamp.monotonic for timestamp in response.request_log.chunk_generated_times]
        )
        self.translation_chunk_statistics = ChunkStatistics(
            name = "Translation",
            request_log = response.request_log,
            raw_timestamps = [timestamp.monotonic for timestamp in response.request_log.translation_chunk_times],
            raw_queue_backlogs = response.request_log.translation_queue_backlog
        )
        self.buffer_chunk_statistics = ChunkStatistics(
            name = "Buffered",
            request_log = response.request_log,
            raw_timestamps = [timestamp.monotonic for timestamp in response.request_log.chunk_times],
            raw_queue_backlogs = response.request_log.queue_backlog
        )
        
        self.avg_token_gen_rate = 0.0
        if (
            response.stream and
            response.request_log.chunk_times and
            len(response.request_log.chunk_times) > 1 and
            response.token_usage is not None
        ):
            self.avg_token_gen_rate = response.token_usage.completion_tokens / (
                (
                    response.request_log.chunk_times[-1].monotonic -
                    response.request_log.chunk_times[0].monotonic
                ) / 1e9
            )
        
        
        self.historical_context_text_length = response.historical_context.total_length
        self.new_context_text_length = response.new_context.total_length
        self.response.request_log.reasoning_content_length = sum(len(content.reasoning_content) for content in response.new_context.context_list if content.reasoning_content)
        self.response.request_log.new_content_length = sum(len(content.content) for content in response.new_context.context_list)
        self.total_context_length = self.historical_context_text_length + self.new_context_text_length
        self.reasoning_content_length = response.request_log.reasoning_content_length
        self.new_content_length = response.request_log.new_content_length
        self.historical_context_length = self.historical_context_text_length
        self.new_context_length = self.new_context_text_length
        self.extra_body_json = orjson.dumps(self.request.extra_bodys, option=orjson.OPT_INDENT_2).decode("utf-8")
    
    def format_statistics(
        self,
        dividing: str = "=",
        title_width: int = 40,
        chart_width: int = 50,
        chart_height: int = 10,
        step_char: str = "\n",
    ) -> str:
        """
        快速统计请求内容并生成字符串

        :param dividing: 分隔符
        :param title_width: 标题宽度
        :param step_char: 换行符
        :return: 统计字符串
        """
        buffer: list[str] = []
        buffer.extend(
            self.format_statistics_stream(
                dividing = dividing,
                chart_width = chart_width,
                chart_height = chart_height,
                title_width = title_width
            )
        )
        return step_char.join(buffer)

    def format_statistics_stream(
        self,
        dividing: str = "=",
        chart_width: int = 50,
        chart_height: int = 10,
        title_width: int = 40
    ) -> Generator[str, None, None]:
        """
        快速统计请求内容并生成字符串

        :param dividing: 分隔符
        :param title_width: 标题宽度
        :return: 统计字符串
        """
        yield format_title(
            "Fast Statistics",
            dividing = dividing,
            title_width = title_width
        )
        yield "Generating statistics..."
        yield f"Create Fast Statistics on {self.now.strftime('%Y-%m-%d %H:%M:%S.%f')}"
        running_time = RunningTime()

        with Runtimer() as timer:
            yield from self._format_request_info(
                dividing = dividing,
                title_width = title_width
            )
            running_time.request_info = timer.get_time()
        
        with Runtimer() as timer:
            yield from self._format_response(
                dividing = dividing,
                title_width = title_width
            )
            running_time.response = timer.get_time()
        
        with Runtimer() as timer:
            yield from self._format_chunk_count(
                dividing = dividing,
                title_width = title_width
            )
            running_time.chunk_count = timer.get_time()

        with Runtimer() as timer:
            yield from self._format_time_statistics(
                dividing = dividing,
                title_width = title_width
            )
            running_time.time = timer.get_time()
        
        with Runtimer() as timer:
            yield from self._chunk_statistics(
                dividing = dividing,
                chart_width = chart_width,
                chart_height = chart_height,
                title_width = title_width
            )
            running_time.chunk_statistics = timer.get_time()

        with Runtimer() as timer:
            yield from self._format_token_count(
                dividing = dividing,
                title_width = title_width
            )
            running_time.token_count = timer.get_time()
        
        with Runtimer() as timer:
            yield from self._format_content(
                dividing = dividing,
                title_width = title_width
            )
            running_time.content = timer.get_time()
        
        yield format_title(
            "Formatting time",
            dividing = dividing,
            title_width = title_width
        )
        yield running_time.format()

        yield dividing * title_width
    
    def _format_request_info(
        self,
        dividing: str = "=",
        title_width: int = 40
    ) -> Generator[str, None, None]:
        yield format_title(
            "Requests INFO",
            dividing = dividing,
            title_width = title_width
        )
        yield f"API URL: {self.request.url}"
        yield f"Model: {self.request.model}"
        yield f"User ID: {self.user_id}"
        yield f"User Name: {self.request.user_name}"
        yield f"Task ID: {self.response.request_log.task_id}"
        yield f"Response ID: {self.response.id}"
        yield f"Thinking: {format_special_values(self.request.thinking)}"
        yield f"Seed: {format_special_values(self.request.seed)}"
        yield f"Temperature: {format_special_values(self.request.temperature)}"
        yield f"Top A: {format_special_values(self.request.top_a)}"
        yield f"Top P: {format_special_values(self.request.top_p)}"
        yield f"Top K: {format_special_values(self.request.top_k)}"
        yield f"Repetition Penalty: {format_special_values(self.request.repetition_penalty)}"
        yield f"Frequency Penalty: {format_special_values(self.request.frequency_penalty)}"
        yield f"Presence Penalty: {format_special_values(self.request.presence_penalty)}"
        yield f"Max Tokens: {format_special_values(self.request.max_tokens)}"
        yield f"Max Completion Tokens: {format_special_values(self.request.max_completion_tokens)}"
        if self.request.fim_mode:
            yield "Completion Mode: FIM"
            yield f"FIM Echo: {format_special_values(self.request.echo)}"
        else:
            yield "Completion Mode: Chat"
        
        if not self.request.remove_reasoning_prompt:
            yield "Reasoning Prompt: Retained"
        else:
            yield "Reasoning Prompt: Removed"

        if self.request.extra_bodys:
            yield "Extra Body:"
            yield self.extra_body_json
    
    def _format_response(
        self,
        dividing: str = "=",
        title_width: int = 40
    ) -> Generator[str, None , None]:
        
        yield format_title(
            "Response INFO",
            dividing = dividing,
            title_width = title_width
        )
        if self.response.system_fingerprint:
            yield f"System Fingerprint: {self.response.system_fingerprint}"
        yield f"Finish Reason: {self.response.finish_reason}"
        yield f"Finish Reason Cause: {self.response.finish_reason_cause}"

    def _format_chunk_count(
        self,
        dividing: str = "=",
        title_width: int = 40
    ) -> Generator[str, None , None]:
        if self.response.request_log.total_chunk > 0:
            yield format_title(
                "Chunk Count",
                dividing = dividing,
                title_width = title_width
            )
            yield f"Total Chunk: {self.response.request_log.total_chunk}"
            if self.response.request_log.empty_chunk > 0:
                yield f"Empty Chunk: {self.response.request_log.empty_chunk}"
                yield f"Non-Empty Chunk: {self.response.request_log.total_chunk - self.response.request_log.empty_chunk}"
            
            if self.response.request_log.total_chunk != 0:
                chunk_effective_ratio = 1 - self.response.request_log.empty_chunk / self.response.request_log.total_chunk
            else:
                chunk_effective_ratio = np.nan
            yield f"Chunk effective ratio: {chunk_effective_ratio:.2%}"
    
    def _format_time_statistics(
        self,
        dividing: str = "=",
        title_width: int = 40
    ) -> Generator[str, None , None]:
        yield format_title(
            "Time Statistics",
            dividing = dividing,
            title_width = title_width
        )
        
        yield f"Total Time: {format_timedelta(self.total_time)}"
        yield f"Preprocessing Time: {format_timedelta(self.preprocessing_time)}"
        yield f"API Request Time (TTFB): {format_timedelta(self.requests_time)}"
        yield f"Response First Chunk Wait Time (TTFC): {format_timedelta(self.requests_time + int(self.generated_chunk_statistics.first_chunk_wait_time))}"
        yield f"Stream Processing Time: {format_timedelta(self.stream_processing_time)}"
        yield f"Generation Speed: {self.generation_speed:.2f} Tokens/s"
        yield f"Created Time: {self.created_utc_str}"
        yield f"Created Time: {self.created_local_str}"

    def _chunk_statistics(
        self,
        dividing: str = "=",
        title_width: int = 40,
        chart_width: int = 50,
        chart_height: int = 10,
    ) -> Generator[str, None , None]:
        if self.response.request_log.total_chunk > 0:
            if self.response.request_log.chunk_generated_times:
                yield from self.generated_chunk_statistics.format_statistics_stream(
                    title_width = title_width,
                    chart_width = chart_width,
                    chart_height = chart_height,
                    dividing_line_char = dividing
                )
        
            if self.response.request_log.chunk_generated_times:
                yield from self.translation_chunk_statistics.format_statistics_stream(
                    title_width = title_width,
                    chart_width = chart_width,
                    chart_height = chart_height,
                    dividing_line_char = dividing
                )
        
            if self.response.request_log.chunk_times:
                yield from self.buffer_chunk_statistics.format_statistics_stream(
                    title_width = title_width,
                    chart_width = chart_width,
                    chart_height = chart_height,
                    dividing_line_char = dividing
                )

    def _format_token_count(
        self,
        dividing: str,
        title_width: int = 0
    ) -> Generator[str, None, None]:
        if self.response.token_usage is not None:
            yield format_title(
                "Token Count",
                dividing = dividing,
                title_width = title_width
            )
            yield f"Total Tokens: {format_token(self.response.token_usage.total_tokens)}"
            yield f"Context Input Tokens: {format_token(self.response.token_usage.prompt_tokens)}"

            if self.response.token_usage.prompt_cache_hit_tokens is not None:
                yield f"Cache Hit Tokens: {format_token(self.response.token_usage.prompt_cache_hit_tokens)}"
            if self.response.token_usage.prompt_cache_miss_tokens is not None:
                yield f"Cache Miss Tokens: {format_token(self.response.token_usage.prompt_cache_miss_tokens)}"

            yield f"Completion Output Tokens: {format_token(self.response.token_usage.completion_tokens)}"
            
            if not np.isnan(self.response.token_usage.cache_hit_ratio()):
                yield f"Cache Hit Ratio: {self.response.token_usage.cache_hit_ratio():.2%}"
            
            if self.avg_token_gen_rate != 0.0:
                yield f"Average Generation Rate: {self.avg_token_gen_rate:.2f} Token/s"

    def _format_content(
        self,
        dividing: str,
        title_width: int = 0
    ) -> Generator[str, None, None]:
        yield format_title(
            "Content",
            dividing = dividing,
            title_width = title_width
        )

        yield f"Total Content Length: {self.total_context_length}"
        yield f"New Reasoning Content Length: {self.reasoning_content_length}"
        yield f"New Answer Content Length: {self.new_content_length}"
        yield f"Historical Context Text Length: {self.historical_context_length}"
        yield f"New Content Text Length: {self.new_context_length}"