import httpx
from environs import Env
from ._exceptions import *
from ._object import (
    FunctionParameter,
    Function,
    FunctionResponse,
    ErrorResponse,
)
import json

env = Env()

class FuncerClient:
    def __init__(self, url: str):
        self._client = httpx.AsyncClient(base_url=url)
        self._functions: set[Function] = set()

    async def update_functions(self):
        """
        update functions from the server
        """
        response = await self._client.get(
            url = "/funcer/functions"
        )

        if response.status_code == 200:
            try:
                functions = response.json()
                self._functions.clear()  # 确保更新
                for function in functions:
                    self._functions.add(Function(function))
            except (httpx.HTTPError, json.JSONDecodeError) as e:
                raise UnderstandFormatError(f"Update failed: {str(e)}")
        else:
            raise UnderstandFormatError("Failed to update functions")
    
    async def call(self, function_request: Function, allow_noexistent: bool = False):
        """
        call function
        """
        if not allow_noexistent and function_request.name not in self:
            raise FunctionNotFoundError(f"Function {function_request.name} not found")
        response = await self._client.post(
            url = f"/funcer/call/{function_request.name}",
            json = function_request.as_dict,
            timeout = function_request.timeout
        )

        try:
            if response.status_code == 200:
                return FunctionResponse(response.json())
            else:
                raise BadResponse("Bad response from the server", body = response.json(), code = response.status_code)
        except json.JSONDecodeError as e:
            raise BadResponse("Bad response from the server", body = response.text, code = response.status_code)
    
    async def silence(self, function_request: Function):
        """
        silence function
        """
        if function_request not in self:
            raise FunctionNotFoundError(f"Function {function_request.name} not found")
        response = await self._client.post(
            url = f"/funcer/silence/{function_request.name}",
            json = function_request.as_dict
        )

        try:
            if response.status_code == 200:
                self._functions.remove(function_request)
            else:
                raise BadResponse("Bad response from the server", body = response.json(), code = response.status_code)
        except json.JSONDecodeError as e:
            raise BadResponse("Bad response from the server", body = response.text, code = response.status_code)
    
    def __iter__(self):
        functions = self._functions
        for function in functions:
            yield function

    def __len__(self):
        return len(self._functions)
    
    def __repr__(self):
        return f"<FuncerClient>"
    
    def __contains__(self, item):
        if isinstance(item, Function):
            return item in self._functions
        elif isinstance(item, str):  # 支持函数名检查
            return any(f.name == item for f in self._functions)
        return False