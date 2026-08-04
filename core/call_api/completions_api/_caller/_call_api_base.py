import sys
import openai

from typing import (
    AsyncGenerator,
    Literal,
    AsyncIterator,
    TextIO,
    TypeVar,
    ClassVar,
    Any,
    Coroutine,
    overload,
    Generic
)
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk
)
from openai.types import (
    Completion,
)
from openai import (
    AsyncStream,
)
from abc import ABC, abstractmethod
from .._objects import (
    Request,
    Response,
    Delta,
    Runtime,
    InterfaceType
)
from .._exceptions import *
from ....pools.client_pool import ClientInfo
from loguru import logger

T = TypeVar("T")
T_Value = TypeVar("T_Value")

class BaseCallAPI(ABC, Generic[T]):
    """
    Abstract class for calling API
    """

    def __init__(self, print_file: TextIO = sys.stdout):
        self._print_file = print_file
    
    @staticmethod
    def get_client(request: Request, runtime: Runtime) -> openai.AsyncClient:
        client_info = ClientInfo(
            url = request.url,
            proxy = request.proxy,
            limits = request.limits,
            timeout = request.timeout,
            encoding = request.encoding,
        )
        client = runtime.client_pool.get_openai(
            client_info = client_info,
            api_key = request.key,
            params = request.params,
            headers = request.headers,
            cookies = request.cookies,
        )
        return client
    
    @staticmethod
    @overload
    def none_to_omit(value: None) -> openai.Omit:
        ...
    
    @staticmethod
    @overload
    def none_to_omit(value: T_Value) -> T_Value:
        ...
    
    @staticmethod
    def none_to_omit(value: T_Value | None) -> T_Value | openai.Omit:
        if value is None:
            return openai.omit
        return value

    async def call(self, user_id: str, request: Request, runtime: Runtime) -> T:
        """
        调用API

        :param user_id: 用户ID
        :param request: 请求对象
        :return: 响应对象
        """
        if user_id is None:
            raise ValueError("user_id cannot be None")
        if not isinstance(request, Request):
            raise TypeError("request must be Request")
        if not isinstance(runtime, Runtime):
            raise TypeError("runtime must be Runtime")

        with runtime.status_stack.enter("Init objects"):
            # 创建模型响应对象
            model_response = runtime.response

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
        
        with runtime.status_stack.enter("Write calling log base data"):
            # 写入调用日志基础数据
            model_response.request_log.url = request.url
            model_response.request_log.user_id = user_id
            model_response.request_log.user_name = request.user_name
            model_response.request_log.model = request.model
            model_response.request_log.stream = request.stream

        # 如果上下文为空，则抛出异常
        with runtime.status_stack.enter("Check context"):
            if not request.context:
                raise ValueError("context is required")
        
        with runtime.status_stack.enter("Make extra body"):
            extra_body = self.make_extra_body(
                user_id = user_id,
                request = request,
                runtime = runtime,
            )
        
        match request.interface:
            case InterfaceType.OPENAI:
                try:
                    return await self._openai_call(
                        user_id,
                        request,
                        runtime,
                        client = client,
                        extra_body = extra_body,
                    )
                except openai.APITimeoutError as e:
                    raise APITimeoutError(
                        message = e.message,
                        request = e.request
                    ) from e
                except openai.APIConnectionError as e:
                    raise APIConnectionError(
                        message = e.message,
                        request = e.request,
                    ) from e
                except openai.APIStatusError as e:
                    match e.status_code:
                        case 400:
                            except_type = BadRequestError
                        case 401:
                            except_type = AuthenticationError
                        case 403:
                            except_type = PermissionDeniedError
                        case 404:
                            except_type = NotFoundError
                        case 422:
                            except_type = UnprocessableEntityError
                        case 429:
                            except_type = RateLimitError
                        case code:
                            if 400 <= code < 500:
                                except_type = ClientBadRequest
                            elif 500 <= code < 600:
                                except_type = InternalServerError
                            else:
                                except_type = UnknowAPIStatusError
                    raise except_type(
                        e.message,
                        response = e.response,
                        body = e.body,
                    ) from e
                except openai.APIError as e:
                    raise APIError(
                        e.message,
                        request = e.request,
                        body = e.body,
                    ) from e
            case interface:
                raise RuntimeError(f"Unknown InterfaceType: {interface}")
            
    @abstractmethod
    async def _openai_call(
            self,
            user_id:str,
            request: Request,
            runtime: Runtime,
            client: openai.AsyncOpenAI,
            extra_body: dict[str, Any],
     ) -> T:
        pass

    @overload
    async def _send_openai_request(
        self,
        user_id: str,
        request: Request,
        runtime: Runtime,
        client: openai.AsyncOpenAI,
        extra_body: dict[str, Any] | None = None,
        stream: Literal[False] = False,
    ) -> ChatCompletion | Completion: ...

    @overload
    async def _send_openai_request(
        self,
        user_id: str,
        request: Request,
        runtime: Runtime,
        client: openai.AsyncOpenAI,
        extra_body: dict[str, Any] | None = None,
        stream: Literal[True] = True,
    ) -> AsyncStream[ChatCompletionChunk] | AsyncStream[Completion]: ...

    async def _send_openai_request(
        self,
        user_id: str,
        request: Request,
        runtime: Runtime,
        client: openai.AsyncOpenAI,
        extra_body: dict[str, Any] | None = None,
        stream: bool = False,
    ) -> ChatCompletion | Completion | AsyncStream[ChatCompletionChunk] | AsyncStream[Completion]:
        response: ChatCompletion | Completion | AsyncStream[ChatCompletionChunk] | AsyncStream[Completion]
        if request.fim_mode:
            response = await client.completions.create(
                model = request.model,
                prompt = request.prompt,
                echo = self.none_to_omit(request.echo),
                suffix = self.none_to_omit(request.suffix),
                temperature = self.none_to_omit(request.temperature),
                top_p = self.none_to_omit(request.top_p),
                frequency_penalty = self.none_to_omit(request.frequency_penalty),
                presence_penalty = self.none_to_omit(request.presence_penalty),
                max_tokens = self.none_to_omit(request.max_tokens),
                logprobs = self.none_to_omit(request.top_logprobs if request.logprobs else None),
                stream = stream,
                seed = self.none_to_omit(request.seed),
                stop = self.none_to_omit(request.stop), 
                extra_body = extra_body,
            )
        else:
            if request.context is not None:
                context = request.context.to_context(
                    with_prompt = True,
                    remove_reasoning_prompt = request.remove_reasoning_prompt,
                    remove_created = request.remove_created,
                )
            else:
                context = []
            
            response = await client.chat.completions.create(
                model = request.model,
                temperature = self.none_to_omit(request.temperature),
                top_p = self.none_to_omit(request.top_p),
                frequency_penalty = self.none_to_omit(request.frequency_penalty),
                presence_penalty = self.none_to_omit(request.presence_penalty),
                max_tokens = self.none_to_omit(request.max_tokens),
                max_completion_tokens = self.none_to_omit(request.max_completion_tokens),
                stop = self.none_to_omit(request.stop),
                stream = stream,
                messages = context,
                seed = self.none_to_omit(request.seed),

                # 唉...
                # 不想搞这些东西
                # 特别麻烦不说还可能跑不起来
                # 先这样吧
                # 反正这样也能跑
                tools = self.none_to_omit(request.tools), # type: ignore
                tool_choice = self.none_to_omit(request.tool_choice), # type: ignore
                stream_options = self.none_to_omit(request.stream_options.model_dump()), # type: ignore
                
                logprobs = self.none_to_omit(request.logprobs),
                top_logprobs = self.none_to_omit(request.top_logprobs if request.top_logprobs else None),
                extra_body = extra_body
            )
        return response

    @property
    @abstractmethod
    def streamable(self) -> bool:
        pass

    def make_extra_body(self, user_id: str, request: Request, runtime: Runtime) -> dict[str, Any]:
        extra_body: dict[str, Any] = {}

        with runtime.status_stack.enter("thinking"):
            if request.thinking is not None:
                if request.thinking:
                    extra_body["thinking"] = {
                        "type": "enabled"
                    }
                else:
                    extra_body["thinking"] = {
                        "type": "disabled"
                    }
        
        with runtime.status_stack.enter("reasoning_effort"):
            if request.reasoning_effort is not None:
                extra_body["reasoning_effort"] = request.reasoning_effort.value
        
        if request.send_user_id:
            with runtime.status_stack.enter("user_id"):
                extra_body["user_id"] = user_id
        
        if request.top_a is not None:
            with runtime.status_stack.enter("top_a"):
                extra_body["top_a"] = request.top_a
        
        if request.top_k is not None:
            with runtime.status_stack.enter("top_k"):
                extra_body["top_k"] = request.top_k
        
        if request.repetition_penalty is not None:
            with runtime.status_stack.enter("repetition_penalty"):
                extra_body["repetition_penalty"] = request.repetition_penalty

        if request.extra_bodys:
            extra_body.update(request.extra_bodys)

        return extra_body

class CallNstreamAPIBase(BaseCallAPI, ABC):
    """
    Base class for calling non-streaming API
    """

    @property
    def streamable(self) -> Literal[False]:
        return False

    @abstractmethod
    async def _openai_call(
        self,
        user_id: str,
        request: Request,
        runtime: Runtime,
        client: openai.AsyncOpenAI,
        extra_body: dict[str, Any],
    ) -> Response:
        pass

class CallStreamAPIBase(BaseCallAPI, ABC):
    """
    Base class for calling streaming API
    """

    @property
    def streamable(self) -> Literal[True]:
        return True

    @abstractmethod
    async def _openai_call(
            self,
            user_id:str,
            request: Request,
            runtime: Runtime,
            client: openai.AsyncOpenAI,
            extra_body: dict[str, Any],
     ) -> Coroutine[Any, Any, AsyncGenerator[Delta, None]]:
        pass