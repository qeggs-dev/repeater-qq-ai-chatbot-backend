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
from ._object import (
    Request,
    Response,
    Top_Logprob,
    Logprob,
    Delta,
    TokensCount
)
from ..Context import (
    FunctionResponseUnit,
    ContextObject,
    ContentUnit,
    ContextRole
)
from ..CallLog import CallLog
from TimeParser import (
    format_deltatime,
    format_deltatime_ns
)

# ==== 本模块代码 ==== #
env = Env()

def remove_keys_from_dicts(dict_list: list[dict], keys_to_remove: list[str] | set[str]):
    """
    从字典列表中删除指定的键
    
    :param dict_list: 包含字典的列表
    :param keys_to_remove: 需要删除的键列表
    :return: 新的字典列表（原列表不被修改）
    """
    return [
        {k: v for k, v in d.items() if k not in keys_to_remove}
        for d in dict_list
    ]

def sum_string_lengths(items, field_name):
    """
    计算列表中所有字典指定字段的字符串长度总和
    
    :param items: 字典列表
    :param field_name: 要计算长度的字段名
    :return: 字符串长度总和
    """
    return sum(len(item[field_name]) for item in items if field_name in item and isinstance(item[field_name], str))

class Client:
    def __init__(self, max_concurrency: int | None = None):
        # 协程池
        self.max_concurrency = max_concurrency if max_concurrency is not None else env.int('MAX_CONCURRENCY', 1000) # 最大并发数
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.tasks = set()  # 存储运行中的任务
    # region 协程池管理
    async def _submit(self, coro: Awaitable[Any], user_id: str) -> Any:
        """提交任务到协程池，并等待返回结果"""
        async with self.semaphore:  # 控制并发数
            task = asyncio.create_task(coro)
            self.tasks.add(task)
            logger.debug(f'Created a new task for {inspect.currentframe().f_back.f_code.co_name} ({len(self.tasks)}/{self.max_concurrency})', user_id = user_id)
            try:
                result = await task
                return result
            finally:
                self.tasks.remove(task)
                logger.debug(f'Removed a task ({len(self.tasks)}/{self.max_concurrency})', user_id = user_id)
        
    async def _shutdown(self):
        """关闭池，等待所有任务完成"""
        await asyncio.gather(*self.tasks)

    async def set_concurrency(self, new_max: int):
        """动态修改并发限制"""
        self.max_concurrency = new_max
        self.semaphore = asyncio.Semaphore(new_max)
    # endregion

    # region 提交任务
    async def submit_Request(self, user_id:str, request: Request) -> Response:
        """提交请求到协程池，并等待返回结果"""
        if request.stream:
            response = await self._submit(self._call_stream_api(user_id, request), user_id = user_id)
        else:
            response = await self._submit(self._call_api(user_id, request), user_id = user_id)
        
        await self._print_log(
            user_id = user_id,
            request = request,
            response = response
        )
        return response
    # endregion
    
    # region 非流式API
    async def _call_api(self, user_id:str, request: Request) -> Response:
        """调用API"""
        model_response = Response()
        model_response.calling_log = CallLog()
        logger.info(f"Created OpenAI Client", user_id = user_id)
        client = AsyncOpenAI(base_url=request.url, api_key=request.key)
        model_response.calling_log.url = request.url
        model_response.calling_log.user_id = user_id
        model_response.calling_log.user_name = request.user_name
        model_response.calling_log.model = request.model
        model_response.calling_log.stream = request.stream

        if not request.context:
            raise ValueError("context is required")
        logger.info(f"Send Request", user_id = user_id)
        request_start_time = time.time_ns()
        response = await client.chat.completions.create(
            model = request.model,
            temperature = request.temperature,
            top_p = request.top_p,
            frequency_penalty = request.frequency_penalty,
            presence_penalty = request.presence_penalty,
            max_tokens = request.max_tokens,
            max_completion_tokens=request.max_completion_tokens,
            stop = request.stop,
            stream = False,
            messages = remove_keys_from_dicts(request.context.full_context, {"reasoning_content"}) if not request.context.last_content.prefix else request.context.full_context,
        )
        request_end_time = time.time_ns()

        model_response_content_unit:ContentUnit = ContentUnit()
        model_response_content_unit.role = ContextRole.ASSISTANT
        chunk_count:int = 0
        empty_chunk_count:int = 0
        print("\n", end="", flush=True)

        # 处理响应基础信息
        if hasattr(response, "id"):
            model_response.id = response.id
        
        if hasattr(response, "created"):
            model_response.created = response.created
        
        if hasattr(response, "model"):
            model_response.model = response.model
        
        if hasattr(response, "system_fingerprint"):
            model_response.system_fingerprint = response.system_fingerprint
        
        # 处理响应内容
        if hasattr(response, "choices"):
            choices = response.choices[0]
            if hasattr(choices, "finish_reason"):
                model_response.finish_reason = choices.finish_reason
            if hasattr(choices, "message"):
                # 处理输出内容
                if hasattr(choices.message, "content"):
                    model_response_content_unit.content = choices.message.content
                    print(f"\n\n{model_response_content_unit.content}\n\n", end="", flush=True)
                
                # 处理推理内容
                if hasattr(choices.message, "reasoning_content"):
                    model_response_content_unit.reasoning_content = choices.message.reasoning_content
                    print(f"\n\n\033[7m{model_response_content_unit.reasoning_content}\033[0m", end="", flush=True)
                
                # 处理工具调用
                if hasattr(choices.message, "tool_calls") and choices.message.tool_calls is not None:
                    for tool_call in choices.message.tool_calls:
                        if hasattr(tool_call, "id"):
                            id = tool_call.id
                        else:
                            id = ""
                        if hasattr(tool_call, "type"):
                            type = tool_call.type
                        else:
                            type = ""
                        if hasattr(tool_call, "function"):
                            if hasattr(tool_call.function, "name"):
                                name = tool_call.function.name
                            else:
                                name = ""
                            if hasattr(tool_call.function, "arguments"):
                                arguments = tool_call.function.arguments
                            else:
                                arguments = ""

                        model_response_content_unit.funcResponse.callingFunctionResponse.append(
                            FunctionResponseUnit(
                                id = id,
                                type = type,
                                name = name,
                                arguments = arguments
                            )
                        )
        
        # 处理logprobs
        if hasattr(response.choices, "logprobs"):
            if hasattr(response.choices.logprobs, "content"):
                logprobs = []
                for token in response.choices.logprobs.content:
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
                logprobs = logprobs
        
        # 处理usage数据
        model_response.token_usage = TokensCount()
        if hasattr(response, 'usage') and response.usage is not None:
            if hasattr(response.usage, 'prompt_tokens') and response.usage.prompt_tokens is not None:
                model_response.token_usage.prompt_tokens = response.usage.prompt_tokens
            if hasattr(response.usage, 'completion_tokens') and response.usage.completion_tokens is not None:
                model_response.token_usage.completion_tokens = response.usage.completion_tokens
            if hasattr(response.usage, 'total_tokens') and response.usage.total_tokens is not None:
                model_response.token_usage.total_tokens = response.usage.total_tokens
            if hasattr(response.usage, 'prompt_cache_hit_tokens') and response.usage.prompt_cache_hit_tokens is not None:
                model_response.token_usage.prompt_cache_hit_tokens = response.usage.prompt_cache_hit_tokens
            if hasattr(response.usage, 'prompt_cache_miss_tokens') and response.usage.prompt_cache_miss_tokens is not None:
                model_response.token_usage.prompt_cache_miss_tokens = response.usage.prompt_cache_miss_tokens

        print('\n\n', end="", flush=True)

        # 添加日志统计数据
        model_response.calling_log.id = model_response.id
        model_response.calling_log.total_chunk = chunk_count
        model_response.calling_log.empty_chunk = empty_chunk_count
        model_response.calling_log.request_start_time = request_start_time
        model_response.calling_log.request_end_time = request_end_time
        model_response.calling_log.total_tokens = model_response.token_usage.total_tokens
        model_response.calling_log.prompt_tokens = model_response.token_usage.prompt_tokens
        model_response.calling_log.completion_tokens = model_response.token_usage.completion_tokens
        model_response.calling_log.cache_hit_count = model_response.token_usage.prompt_cache_hit_tokens
        model_response.calling_log.cache_miss_count = model_response.token_usage.prompt_cache_miss_tokens

        # 添加上下文
        model_response.context = request.context
        model_response.context.context_list.append(model_response_content_unit)

        # 输出响应
        return model_response
    # endregion

    # region 流式API
    async def _call_stream_api(self, user_id:str, request: Request) -> Response:
        """调用流式API"""
        model_response = Response()
        model_response.calling_log = CallLog()
        logger.info(f"Created OpenAI Client", user_id = user_id)
        client = AsyncOpenAI(base_url=request.url, api_key=request.key)
        model_response.calling_log.url = request.url
        model_response.calling_log.user_id = user_id
        model_response.calling_log.user_name = request.user_name
        model_response.calling_log.model = request.model
        model_response.calling_log.stream = request.stream

        if not request.context:
            raise ValueError("context is required")
        logger.info(f"Make Request", user_id = user_id)
        request_start_time = time.time_ns()
        response = await client.chat.completions.create(
            model = request.model,
            temperature = request.temperature,
            top_p = request.top_p,
            frequency_penalty = request.frequency_penalty,
            presence_penalty = request.presence_penalty,
            max_tokens = request.max_tokens,
            max_completion_tokens=request.max_completion_tokens,
            stop = request.stop,
            stream = True,
            messages = remove_keys_from_dicts(request.context.full_context, {"reasoning_content"}) if not request.context.last_content.prefix else request.context.full_context,
        )
        request_end_time = time.time_ns()

        model_response_content_unit:ContentUnit = ContentUnit()
        model_response_content_unit.role = ContextRole.ASSISTANT
        chunk_count:int = 0
        empty_chunk_count:int = 0
        logger.info(f"Start Streaming", user_id = user_id)
        print("\n", end="", flush=True)
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
                time_difference = this_chunk_time - last_chunk_time
                chunk_times.append(time_difference)
                last_chunk_time = this_chunk_time
            
            if not model_response.id:
                model_response.id = delta_data.id
            
            if not model_response.model:
                model_response.model = delta_data.model
            
            if delta_data.token_usage:
                model_response.token_usage = delta_data.token_usage

            if delta_data.reasoning_content:
                if request.print_chunk:
                    if not model_response_content_unit.reasoning_content:
                        print('\n\n', end="", flush=True)
                    print(f"\033[7m{delta_data.reasoning_content}\033[0m", end="", flush=True)
                model_response_content_unit.reasoning_content += delta_data.reasoning_content
            
            if delta_data.content:
                if request.print_chunk:
                    if not model_response_content_unit.content:
                        print('\n\n', end="", flush=True)
                    print(delta_data.content, end="", flush=True)
                model_response_content_unit.content += delta_data.content
            
            if delta_data.function_id:
                model_response_content_unit.funcResponse.callingFunctionResponse.append(
                    FunctionResponseUnit(
                        id = delta_data.function_id,
                        type = delta_data.function_type,
                        name = delta_data.function_name,
                        arguments_str = delta_data.function_arguments,
                    )
                )

            if delta_data.is_empty:
                empty_chunk_count += 1
            chunk_count += 1

            if request.continue_processing_callback_function is not None:
                if request.continue_processing_callback_function(user_id, delta_data):
                    break
        stream_processing_end_time = time.time_ns()
        print('\n\n', end="", flush=True)

        # 添加日志统计数据
        model_response.calling_log.id = model_response.id
        model_response.calling_log.total_chunk = chunk_count
        model_response.calling_log.empty_chunk = empty_chunk_count
        model_response.calling_log.request_start_time = request_start_time
        model_response.calling_log.request_end_time = request_end_time
        model_response.calling_log.stream_processing_start_time = stream_processing_start_time
        model_response.calling_log.stream_processing_end_time = stream_processing_end_time
        model_response.calling_log.chunk_times = chunk_times
        model_response.calling_log.total_tokens = model_response.token_usage.total_tokens
        model_response.calling_log.prompt_tokens = model_response.token_usage.prompt_tokens
        model_response.calling_log.completion_tokens = model_response.token_usage.completion_tokens
        model_response.calling_log.cache_hit_count = model_response.token_usage.prompt_cache_hit_tokens
        model_response.calling_log.cache_miss_count = model_response.token_usage.prompt_cache_miss_tokens

        # 添加上下文
        model_response.context = request.context
        model_response.context.context_list.append(model_response_content_unit)

        # 输出响应
        return model_response
    # endregion

    # region 处理单个API响应块
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
        # 处理元数据
        if hasattr(chunk, "id"):
            delta_data.id = chunk.id
        if hasattr(chunk, "created"):
            delta_data.created = chunk.created
        if hasattr(chunk, "model"):
            delta_data.model = chunk.model
        
        # 处理内容
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

        # 获取usage数据
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

    # region 打印日志
    async def _print_log(self, user_id: str, request: Request, response: Response):
        # 打印统计日志
        logger.info("============= API INFO =============", user_id = user_id)
        logger.info(f"API_URL: {request.url}", user_id = user_id)
        logger.info(f"Model: {response.model}", user_id = user_id)
        logger.info(f"UserName: {request.user_name}", user_id = user_id)
        logger.info(f"Chat Completion ID: {response.id}", user_id = user_id)
        logger.info(f"Temperature: {request.temperature}", user_id = user_id)
        logger.info(f"Frequency Penalty: {request.frequency_penalty}", user_id = user_id)
        logger.info(f"Presence Penalty: {request.presence_penalty}", user_id = user_id)
        logger.info(f"Max Tokens: {request.max_tokens if request.max_tokens else 'MAX'}", user_id = user_id)
        logger.info(f"Max Completion Tokens: {request.max_completion_tokens if request.max_completion_tokens else 'MAX'}", user_id = user_id)
        if response.calling_log.total_chunk > 0:
            logger.info("============ Chunk Count ===========", user_id = user_id)
            logger.info(f"Total Chunk: {response.calling_log.total_chunk}", user_id = user_id)
            if response.calling_log.empty_chunk > 0:
                logger.info(f"Empty Chunk: {response.calling_log.empty_chunk}", user_id = user_id)
                logger.info(f"Non-Empty Chunk: {response.calling_log.total_chunk - response.calling_log.empty_chunk}", user_id = user_id)
            logger.info(f"Chunk effective ratio: {1 - response.calling_log.empty_chunk / response.calling_log.total_chunk :.2%}", user_id = user_id)
        logger.info("========== Time Statistics =========", user_id = user_id)
        logger.info(f"Total Time: {format_deltatime_ns(response.calling_log.stream_processing_end_time - response.calling_log.request_start_time, '%H:%M:%S.%f.%u.%n')}", user_id = user_id)
        logger.info(f"API Request Time: {format_deltatime_ns(response.calling_log.request_end_time - response.calling_log.request_start_time, '%H:%M:%S.%f.%u.%n')}", user_id = user_id)
        logger.info(f"Stream Processing Time: {format_deltatime_ns(response.calling_log.stream_processing_end_time - response.calling_log.stream_processing_start_time, '%H:%M:%S.%f.%u.%n')}", user_id = user_id)

        created_utc_dt = datetime.fromtimestamp(response.created, tz=timezone.utc)
        created_utc_str = created_utc_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        logger.info(f"Created Time: {created_utc_str}", user_id = user_id)

        created_local_dt = datetime.fromtimestamp(response.created)
        created_local_str = created_local_dt.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Created Time: {created_local_str}", user_id = user_id)

        if response.calling_log.total_chunk > 0:
            chunk_nozero_times = [time for time in response.calling_log.chunk_times if time != 0]
            logger.info(f"Chunk Average Spawn Time: {format_deltatime_ns(sum(chunk_nozero_times) // len(chunk_nozero_times), '%H:%M:%S.%f.%u.%n')}", user_id = user_id)
            logger.info(f"Chunk Max Spawn Time: {format_deltatime_ns(max(chunk_nozero_times), '%H:%M:%S.%f.%u.%n')}", user_id = user_id)
            logger.info(f"Chunk Min Spawn Time: {format_deltatime_ns(min(chunk_nozero_times), '%H:%M:%S.%f.%u.%n')}", user_id = user_id)

        logger.info("=========== Token Count ============", user_id = user_id)
        logger.info(f"Total Tokens: {response.token_usage.total_tokens}", user_id = user_id)
        logger.info(f"Context Input Tokens: {response.token_usage.prompt_tokens}", user_id = user_id)
        logger.info(f"Completion Output Tokens: {response.token_usage.completion_tokens}", user_id = user_id)
        logger.info(f"Cache Hit Count: {response.token_usage.prompt_cache_hit_tokens}", user_id = user_id)
        logger.info(f"Cache Miss Count: {response.token_usage.prompt_cache_miss_tokens}", user_id = user_id)
        logger.info(f"Cache Hit Ratio: {response.token_usage.prompt_cache_hit_tokens / response.token_usage.prompt_tokens :.2%}", user_id = user_id)
        if response.stream:
            logger.info(f"Average Generation Rate: {response.token_usage.completion_tokens / ((response.calling_log.stream_processing_end_time - response.calling_log.stream_processing_start_time) / 1e9):.2f} /s", user_id = user_id)

        logger.info("========== Content Length ==========", user_id = user_id)
        logger.info(f"Total Content Length: {len(response.context.last_content.reasoning_content) + len(response.context.last_content.content)}", user_id = user_id)
        response.calling_log.total_context_length = sum_string_lengths(response.context.full_context, "content")
        logger.info(f"Reasoning Content Length: {len(response.context.last_content.reasoning_content)}", user_id = user_id)
        response.calling_log.reasoning_content_length = len(response.context.last_content.reasoning_content)
        logger.info(f"New Content Length: {len(response.context.last_content.content)}", user_id = user_id)
        response.calling_log.new_content_length = len(response.context.last_content.content)

        logger.info("====================================", user_id = user_id)