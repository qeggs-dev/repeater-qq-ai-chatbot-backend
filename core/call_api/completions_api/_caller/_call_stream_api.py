# ==== 标准库 ==== #
import asyncio
from typing import (
    AsyncGenerator,
    Any,
    Coroutine,
)

# ==== 第三方库 ==== #
import openai
from openai.types.chat import ChatCompletionChunk
from openai.types.completion import Completion
from openai import AsyncStream
from loguru import logger

# ==== 自定义库 ==== #
from .._objects import (
    Request,
    Delta,
    Runtime
)
from ....request_log import TimeStamp
from ._translation_openai_chunk import translation_openai_chunk
from ._call_api_base import CallStreamAPIBase
from .._exceptions import *

class StreamAPI(CallStreamAPIBase):
    async def _openai_call(
            self,
            user_id:str,
            request: Request,
            runtime: Runtime,
            client: openai.AsyncOpenAI,
            extra_body: dict[str, Any],
     ) -> AsyncGenerator[Delta, None]:
        """
        调用流式API

        :param user_id: 用户ID
        :param request: 请求对象
        :return: 响应流
        """
        assert isinstance(user_id, str), "user_id must be a string"
        assert isinstance(request, Request), "request must be a Request object"
        assert isinstance(runtime, Runtime), "runtime must be a Runtime object"

        if not request.stream:
            raise NotImplementedError("Direct API is not implemented")

        with runtime.status_stack.enter("Create OpenAI Client"):
            # 创建OpenAI Client
            logger.info(
                "Created OpenAI Client",
                user_id = user_id
            )
            client = self.get_client(
                request = request,
                runtime = runtime
            )

        with runtime.status_stack.enter("Check context"):
            # 如果context为空，则抛出异常
            if not request.context:
                raise ValueError("context is required")
        
        with runtime.status_stack.enter("Make extra body"):
            extra_body = self.make_extra_body(
                user_id = user_id,
                request = request,
                runtime = runtime
            )
        
        # 请求流式连接
        with runtime.status_stack.enter("Send Request"):
            logger.info(
                "Start Connecting to the API",
                user_id = user_id
            )
            runtime.response.request_log.request_start_time = TimeStamp()
            response = await self._send_openai_request(
                user_id = user_id,
                request = request,
                runtime = runtime,
                client = client,
                extra_body = extra_body,
                stream = True,
            )
            runtime.response.request_log.request_end_time = TimeStamp()
        
        with runtime.status_stack.enter("Streaming"):
            chunk_queue: asyncio.Queue[ChatCompletionChunk | Completion | Exception | None] = asyncio.Queue()
            chunk_times: list[TimeStamp] = []
            translation_chunk_times:list[TimeStamp] = []
            translation_queue_backlog: list[int] = []

            async def fetch_response_chunks(response: AsyncStream[ChatCompletionChunk] | AsyncStream[Completion]):
                nonlocal chunk_queue, runtime
                try:
                    async for chunk in response:
                        this_chunk_time = TimeStamp()
                        await chunk_queue.put(chunk)
                        chunk_times.append(this_chunk_time)
                    await chunk_queue.put(None)
                    runtime.response.request_log.chunk_generated_times = chunk_times
                except Exception as e:
                    await chunk_queue.put(e)
            
            async def translation_chunks():
                nonlocal chunk_queue, translation_chunk_times, runtime, translation_queue_backlog
                logger.info("Start Streaming", user_id = user_id)
                while True:
                    chunk = await chunk_queue.get()
                    translation_queue_backlog.append(chunk_queue.qsize())
                    if chunk is None:
                        break
                    elif isinstance(chunk, Exception):
                        raise chunk
                    delta_data = await translation_openai_chunk(chunk)
                    translation_chunk_times.append(TimeStamp())
                    yield delta_data
                runtime.response.request_log.translation_chunk_times = translation_chunk_times
                runtime.response.request_log.translation_queue_backlog = translation_queue_backlog

            fetch_response_chunks_task = asyncio.create_task(
                fetch_response_chunks(
                    response
                )
            )

            return translation_chunks()