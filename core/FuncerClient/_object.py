from dataclasses import dataclass, asdict
from typing import Any
from ._exceptions import *

@dataclass
class FunctionParameter:
    name: str = ""
    type: str = ""
    value: Any | None = None

    @property
    def as_dict(self):
        return asdict(self)

class Function:
    def __init__(self, from_dict: dict | None = None):
        self.name: str = ""
        self.parameters: dict[str, FunctionParameter] = {}
        self.return_type: str = ""
        self.timeout: float = 5.0

        if from_dict is not None:
            self._load_from_dict(from_dict)
    
    def _load_from_dict(self, from_dict: dict):
        try:
            self.name = from_dict["name"]
            parameters:dict = from_dict["parameters"]
            if parameters is not None:
                for key, value in parameters.items():
                    parameter = FunctionParameter()
                    if "name" in value and isinstance(value["name"], str):
                        parameter.name = value["name"]
                    else:
                        raise FormattingError("Invalid parameter name")
                    if "type" in value and isinstance(value["type"], str):
                        parameter.type = value["type"]
                    else:
                        raise FormattingError("Invalid parameter type")
                    if "value" in value:
                        parameter.value = value["value"]
                    else:
                        parameter.value = None
                    self.parameters[key] = parameter
            self.return_type = from_dict["return_type"]
            if "timeout" in value:
                self.timeout = value["timeout"]
        except KeyError as e:
            raise FormattingError(f"Missing key in response: {e}")
    
    def add_parameter(self, parameter:FunctionParameter) -> None:
        self.parameters[parameter.name] = parameter
    @property
    def as_dict(self):
        parameters = {}
        for key, value in self.parameters.items():
            parameters[key] = value.as_dict
        
        return {
            "name": self.name,
            "parameters": parameters,
            "return_type": self.return_type
        }
    
    def __post_init__(self):
        if not self.name:
            raise FormattingError("Function name cannot be empty")
    
    def __hash__(self):
        return hash(self.name)  # 支持set操作

@dataclass
class ErrorResponse:
    code: int = 0
    message: str = ""
    funcname: str | None = None

    @property
    def as_dict(self):
        error_response = {
            "code": self.code,
            "message": self.message
        }
        if self.funcname:
            error_response["funcname"] = self.funcname
        return error_response

class FunctionResponse:
    def __init__(self, from_dict: dict | None = None):
        self.name: str = ""
        self.return_type: str = ""
        self.return_value: Any = None
        self.server_error: ErrorResponse | None = None
    
        if from_dict is not None:
            self._load_from_dict(from_dict)

    def _load_from_dict(self, from_dict: dict):
        try:
            self.name = from_dict["name"]
            self.return_type = from_dict["return_type"]
            self.return_value = from_dict["return_value"]
            error_response = ErrorResponse()
            if "error_response" in from_dict:
                error_response.code = from_dict["error_response"]["code"]
                error_response.message = from_dict["error_response"]["message"]
                if "funcname" in from_dict["error_response"]:
                    error_response.funcname = from_dict["error_response"]["funcname"]
                self.server_error = error_response
        except KeyError as e:
            raise UnderstandFormatError(f"Missing key in response: {e}")

    @property
    def as_dict(self):
        return {
            "name": self.name,
            "return_type": self.return_type,
            "return_value": self.return_value,
            "server_error": self.server_error.as_dict
        }
