# ==== 标准库 ==== #
from typing import (
    Any,
)

# ==== 第三方库 ==== #
import openai
from loguru import logger

# ==== 自定义库 ==== #
from .._objects import (
    Request,
    Runtime,
    Response,
)
from ....request_log import TimeStamp
from ._call_api_base import CallNstreamAPIBase
from .._exceptions import *
from ._translation_openai_response import translation_openai_response

class CallAPI(CallNstreamAPIBase):
    async def _openai_call(
            self,
            user_id:str,
            request: Request,
            runtime: Runtime,
            client: openai.AsyncOpenAI,
            extra_body: dict[str, Any],
        ) -> Response:
        """调用API"""
        # 检查参数
        assert isinstance(user_id, str), "user_id must be str"
        assert isinstance(request, Request), "request must be Request"
        assert isinstance(runtime, Runtime), "runtime must be Runtime"

        model_response = runtime.response

        if request.stream:
            raise NotImplementedError("Stream API not implemented")

        # 发送请求
        with runtime.status_stack.enter("Send Request"):
            logger.info(
                "Send Request",
                user_id = user_id
            )
            request_start_time = TimeStamp()
            response = await self._send_openai_request(
                user_id = user_id,
                request = request,
                runtime = runtime,
                client = client,
                extra_body = extra_body,
                stream = False,
            )
            request_end_time = TimeStamp()

        with runtime.status_stack.enter("Processing Response"):
            model_response.request_log.request_start_time = request_start_time
            model_response.request_log.request_end_time = request_end_time
            return translation_openai_response(
                request = request,
                response = response,
                runtime = runtime,
                print_file = self._print_file
            )