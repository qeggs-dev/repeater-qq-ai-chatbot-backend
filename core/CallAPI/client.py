# ==== 标准库 ==== #
import asyncio
import inspect
from typing import (
    Any,
    Awaitable,
)
import time
from datetime import datetime, timezone

# ==== 第三方库 ==== #
from openai import AsyncOpenAI
from environs import Env
from loguru import logger

# ==== 自定义库 ==== #
from .object import (
    Request,
    Response,
    Top_Logprob,
    Logprob,
    Delta,
    TokensCount
)
from ..Context import (
    FunctionResponse,
    ContextObject
)
from TimeParser import (
    format_deltatime,
    format_deltatime_ns
)

# ==== 本模块代码 ==== #
env = Env()

class Client:
    def __init__(self, max_concurrency: int | None = None):
        # 协程池
        self.max_concurrency = max_concurrency if max_concurrency is not None else env.int('MAX_CONCURRENCY', 10) # 最大并发数
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.tasks = set()  # 存储运行中的任务
    # region > 协程池管理
    async def _submit(self, coro: Awaitable[Any]) -> Any:
        """提交任务到协程池，并等待返回结果"""
        async with self.semaphore:  # 控制并发数
            task = asyncio.create_task(coro)
            self.tasks.add(task)
            logger.debug(f'Created a new task for {inspect.currentframe().f_back.f_code.co_name} ({len(self.tasks)}/{self.max_concurrency})')
            try:
                result = await task
                return result
            finally:
                self.tasks.remove(task)
                logger.debug(f'Removed a task ({len(self.tasks)}/{self.max_concurrency})')
        
    async def _shutdown(self):
        """关闭池，等待所有任务完成"""
        await asyncio.gather(*self.tasks)

    async def set_concurrency(self, new_max: int):
        """动态修改并发限制"""
        self.max_concurrency = new_max
        self.semaphore = asyncio.Semaphore(new_max)
    # endregion

    async def submit_Request(self, request: Request) -> Response:
        """提交请求到协程池，并等待返回结果"""
        return await self._submit(self._call_api(request))
    
    async def _call_api(self, request: Request) -> Response:
        """调用API"""
        client = AsyncOpenAI(base_url=request.url, api_key=request.key)

        if not request.context:
            raise ValueError("context is required")
        request_start_time = time.time_ns()
        response = await client.chat.completions.create(
            model = request.model,
            temperature = request.temperature,
            frequency_penalty = request.frequency_penalty,
            presence_penalty = request.presence_penalty,
            max_tokens = request.max_tokens,
            stop = request.stop,
            stream = True,
            messages = request.context.full_context
        )
        request_end_time = time.time_ns()

        model_response_context:ContextObject = ContextObject()
        model_response_context.new_content_role = "assistant"
        model_response_context.context_list = request.context.context
        chunk_count:int = 0
        empty_chunk_count:int = 0
        model_response = Response()
        stream_processing_start_time:int = time.time_ns()
        last_chunk_time:int = 0
        chunk_times:list[int] = []
        async for chunk in response:
            delta_data = await self._process_chunk(chunk)

            if not model_response.created:
                model_response.created = delta_data.created
            
            if last_chunk_time == 0:
                last_chunk_time = delta_data.created * (10**9)
            else:
                this_chunk_time = time.time_ns()
                chunk_times.append(last_chunk_time - this_chunk_time)
                last_chunk_time = this_chunk_time
            
            if not model_response.id:
                model_response.id = delta_data.id
            
            if not model_response.model:
                model_response.model = delta_data.model
            
            if delta_data.token_usage:
                model_response.token_usage = delta_data.token_usage

            if delta_data.reasoning_content:
                if request.print_chunk:
                    if not model_response_context.reasoning_content:
                        print('\n\n', end="", flush=True)
                    print(delta_data.reasoning_content, end="", flush=True)
                model_response_context.reasoning_content += delta_data.reasoning_content
            
            if delta_data.content:
                if request.print_chunk:
                    if not model_response_context.new_content:
                        print('\n\n', end="", flush=True)
                    print(delta_data.content, end="", flush=True)
                model_response_context.new_content += delta_data.content
            
            if delta_data.function_id:
                model_response_context.funcResponse.callingFunctionResponse.append(
                    FunctionResponse(
                        id = delta_data.function_id,
                        type = delta_data.function_type,
                        name = delta_data.function_name,
                        arguments_str = delta_data.function_arguments,
                    )
                )

            if delta_data.is_empty:
                empty_chunk_count += 1
            chunk_count += 1
        stream_processing_end_time = time.time_ns()
        print('\n\n', end="", flush=True)

        model_response.context = model_response_context

        # 打印统计日志
        logger.info("============= API INFO =============")
        logger.info(f"API_URL: {request.url}")
        logger.info(f"MODEL: {model_response.model}")
        logger.info("============ Chunk Count ===========")
        logger.info(f"Total Chunk: {chunk_count}")
        if empty_chunk_count > 0:
            logger.info(f"Empty Chunk: {empty_chunk_count}")
            logger.info(f"Non-Empty Chunk: {chunk_count - empty_chunk_count}")
        logger.info(f"Chunk effective ratio: {1 - empty_chunk_count / chunk_count :.2%}")
        logger.info("========== Time Statistics =========")
        logger.info(f"Total Time: {format_deltatime_ns(stream_processing_end_time - request_start_time, '%H:%M:%S.%n')}")
        logger.info(f"API Request Time: {format_deltatime_ns(request_end_time - request_start_time, '%H:%M:%S.%n')}")
        logger.info(f"Stream Processing Time: {format_deltatime_ns(stream_processing_end_time - stream_processing_start_time, '%H:%M:%S.%n')}")

        created_utc_dt = datetime.fromtimestamp(model_response.created, tz=timezone.utc)
        created_utc_str = created_utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        logger.info(f"Created Time: {created_utc_str} UTC")

        created_local_dt = datetime.fromtimestamp(model_response.created)
        created_local_str = created_local_dt.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Created Time: {created_local_str} (Local Time)")

        logger.info(f"Chunk Average Spawn Time: {format_deltatime_ns(sum(chunk_times) // len(chunk_times), '%H:%M:%S.%n')}")
        logger.info(f"Chunk Max Spawn Time: {format_deltatime_ns(max(chunk_times), '%H:%M:%S.%n')}")
        logger.info(f"Chunk Min Spawn Time: {format_deltatime_ns(min(chunk_times), '%H:%M:%S.%n')}")

        logger.info("=========== Token Count ============")
        logger.info(f"Total Tokens: {model_response.token_usage.total_tokens}")
        logger.info(f"Total Prompt Tokens: {model_response.token_usage.prompt_tokens}")
        logger.info(f"Total Completion Tokens: {model_response.token_usage.completion_tokens}")
        logger.info(f"Total Cache Hit Count: {model_response.token_usage.prompt_cache_hit_tokens}")
        logger.info(f"Total Cache Miss Count: {model_response.token_usage.prompt_cache_miss_tokens}")
        logger.info(f"Token Cache Hit Ratio: {model_response.token_usage.prompt_cache_hit_tokens / model_response.token_usage.prompt_tokens :.2%}")
        logger.info(f"Token Average Generation Rate: {(stream_processing_end_time - stream_processing_start_time)}")

        logger.info("========== Content Length ==========")
        logger.info(f"Total Content Length: {len(model_response.context.reasoning_content) + len(model_response.context.new_content)}")
        logger.info(f"Total Reasoning Content Length: {len(model_response.context.reasoning_content)}")
        logger.info(f"Total New Content Length: {len(model_response.context.new_content)}")

        logger.info("====================================")
        return model_response
        
        

    # region > 处理单个API响应块
    async def _process_chunk(
        self,
        chunk
    ) -> Delta:
        """
        处理单个API响应块

        :param chunk: API响应块
        :return: Delta_data对象
        """
        tokens_usage = TokensCount()
        delta_data = Delta()
        if hasattr(chunk, "id"):
            delta_data.id = chunk.id
        if hasattr(chunk, "created"):
            delta_data.created = chunk.created
        if hasattr(chunk, "model"):
            delta_data.model = chunk.model
        
        if hasattr(chunk, "choices") and len(chunk.choices) > 0:
            choice = chunk.choices[0]
            if hasattr(choice, "delta"):
                # 处理推理内容
                if hasattr(choice.delta, "reasoning_content"):
                    reasoning_data = choice.delta.reasoning_content
                    if reasoning_data is not None:
                        delta_data.reasoning_content = reasoning_data

                # 处理响应内容
                if hasattr(choice.delta, "content"):
                    content = choice.delta.content
                    if content:
                        delta_data.content = content
                if hasattr(choice.delta, "tool_calls"):
                    content = choice.delta.tool_calls
                    if content:
                        tool = content[0]
                        if hasattr(tool, "id"):
                            delta_data.function_id = tool.id
                        if hasattr(tool, "type"):
                            delta_data.function_type = tool.type
                        if hasattr(tool, "function"):
                            if hasattr(tool.function, "name"):
                                delta_data.function_name = tool.function.name
                            if hasattr(tool.function, "arguments"):
                                delta_data.function_arguments = tool.function.arguments
        
        if hasattr(choice, "logprobs"):
            if hasattr(choice.logprobs, "content"):
                logprobs = []
                for token in choice.logprobs.content:
                    logprob = Logprob()
                    if hasattr(token, "token"):
                        logprob.token = token.token
                    if hasattr(token, "logprob"):
                        logprob.logprob = token.logprob
                    if hasattr(token, "top_logprob"):
                        top_logprobs = []
                        for top_token in token.top_logprob:
                            top_logprob = Top_Logprob()
                            if hasattr(top_token, "token"):
                                top_logprob.token = top_token.token
                            if hasattr(top_token, "logprob"):
                                top_logprob.logprob = top_token.logprob
                            top_logprobs.append(top_logprob)
                        logprob.top_logprobs = top_logprobs
                    logprobs.append(logprob)
                delta_data.logprobs = logprobs
                        
        
        if hasattr(chunk, 'usage') and chunk.usage is not None:
            # 只在最后一个chunk中获取usage数据
            if hasattr(chunk.usage, 'prompt_tokens') and chunk.usage.prompt_tokens is not None:
                tokens_usage.prompt_tokens = chunk.usage.prompt_tokens
            if hasattr(chunk.usage, 'completion_tokens') and chunk.usage.completion_tokens is not None:
                tokens_usage.completion_tokens = chunk.usage.completion_tokens
            if hasattr(chunk.usage, 'total_tokens') and chunk.usage.total_tokens is not None:
                tokens_usage.total_tokens = chunk.usage.total_tokens
            if hasattr(chunk.usage, 'prompt_cache_hit_tokens') and chunk.usage.prompt_cache_hit_tokens is not None:
                tokens_usage.prompt_cache_hit_tokens = chunk.usage.prompt_cache_hit_tokens
            if hasattr(chunk.usage, 'prompt_cache_miss_tokens') and chunk.usage.prompt_cache_miss_tokens is not None:
                tokens_usage.prompt_cache_miss_tokens = chunk.usage.prompt_cache_miss_tokens
        
        delta_data.token_usage = tokens_usage

        return delta_data
    # endregion