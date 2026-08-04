from httpx import Response as HttpxResponse
from typing import (
    TypeVar,
    Generic,
    Type,
    Any
)
from pydantic import BaseModel, ValidationError
from loguru import logger

T = TypeVar("T", bound = BaseModel)

class Response(Generic[T]):
    """Response Model"""
    def __init__(
            self,
            response: HttpxResponse,
            model: Type[T] | None = None
        ) -> None:
        self._response = response
        self._model = model
    
    def __bool__(self) -> bool:
        return self._response.status_code == 200
    
    @property
    def code(self) -> int:
        return self._response.status_code
    
    @property
    def text(self) -> str:
        return self._response.text
    
    @property
    def content(self) -> bytes:
        return self._response.content
    
    def json(self) -> Any:
        return self._response.json()
    
    def json_or_str(self) -> Any | str:
        try:
            return self._response.json()
        except:
            return self._response.text
    
    def get_data(self) -> T | None:
        if self._model is None:
            raise ValueError("Model is not set")
        try:
            return self._model(
                **self._response.json()
            )
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                logger.error(
                    "{field}: {message}",
                    field = ".".join(str(i) for i in error["loc"]),
                    message = error["msg"]
                )
            return None
