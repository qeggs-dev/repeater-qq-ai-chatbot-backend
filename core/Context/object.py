from dataclasses import dataclass, field, fields, replace
import orjson
from enum import Enum
from .exceptions import *

@dataclass
class FunctionParameters:
    """
    FunctionCalling的函数参数对象
    """
    name: str = ''
    type: str = ''
    description: str = ''
    required: bool = False

@dataclass
class CallingFunction:
    """
    FunctionCalling的函数对象
    """
    name: str = ''
    description: str = ''
    parameters: list[FunctionParameters] = field(default_factory=list)

    @property
    def as_dict(self) -> dict:
        properties = {}
        required = []
        for param in self.parameters:
            properties[param.name] = {
                'type': param.type,
                'description': param.description
            }
            if param.required:
                required.append(param.name)
        
        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'description': self.description,
                'parameters': {
                    'type': 'object',
                    'properties': properties,
                    'required': required
                }
            }
        }


@dataclass
class CallingFunctionRequest:
    """
    FunctionCalling请求对象
    """
    functions: list[CallingFunction] = field(default_factory=list)
    func_choice: str | None = None

    @property
    def tool_choice(self) -> str | dict | None:
        if self.func_choice in {'none', 'auto', 'required'}:
            return self.func_choice
        elif self.func_choice:
            return {
                'type': 'function',
                'function': {
                    'name': self.func_choice
                }
            }
        else:
            return None
    
    @property
    def tools(self) -> list[dict]:
        return [f.as_dict() for f in self.functions]

@dataclass
class FunctionResponseUnit:
    """
    FunctionCalling响应对象单元
    """
    id: str = ''
    type: str = ''
    name: str = ''
    arguments_str: str = ''

    @property
    def arguments(self) -> dict:
        """
        Returns the arguments as a dictionary.
        """
        return orjson.loads(self.arguments_str)
    
    @property
    def as_dict(self) -> dict:
        """
        Returns the response as a dictionary.
        """
        return {
            'id': self.id,
            'type': self.type,
            'function':{
                'name': self.name,
                'arguments': self.arguments
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """
        Creates a FunctionResponseUnit from a dictionary.
        """
        if 'id' not in data:
            raise ContextNecessaryFieldsMissingError('"id" is a necessary field.')
        elif not isinstance(data['id'], str):
            raise ContextFieldTypeError('"id" must be a string.')
        else:
            id = data['id']
        if 'type' not in data:
            raise ContextNecessaryFieldsMissingError('"type" is a necessary field.')
        elif not isinstance(data['type'], str):
            raise ContextFieldTypeError('"type" must be a string.')
        else:
            type = data['type']
        if 'function' not in data:
            raise ContextNecessaryFieldsMissingError('"function" is a necessary field')
        elif not isinstance(data['function'], dict):
            raise ContextFieldTypeError('"function" must be a dictionary.')
        else:
            if 'name' not in data['function']:
                raise ContextNecessaryFieldsMissingError('"function.name" is a necessary field')
            elif not isinstance(data['function']['name'], str):
                raise ContextFieldTypeError('"function.name" must be a string')
            else:
                name = data['function']['name']
            if 'arguments' not in data['function']:
                raise ContextNecessaryFieldsMissingError('"function.arguments" is a necessary field')
            elif not isinstance(data['function']['arguments'], str):
                raise ContextFieldTypeError('"function.arguments" must be a string')
            else:
                arguments_str = data['function']['arguments']
        return cls(
            id = id,
            type = type,
            name = name,
            arguments_str = arguments_str
        )

@dataclass
class CallingFunctionResponse:
    """
    FunctionCalling响应对象
    """
    callingFunctionResponse:list[FunctionResponseUnit] = field(default_factory=list)

    @property
    def as_content(self) -> list[dict]:
        """
        Returns the response as a list of dictionaries.
        """
        return [f.as_dict for f in self.callingFunctionResponse]
    
    @classmethod
    def from_content(cls, content: list[dict]):
        """
        Creates a CallingFunctionResponse from a list of dictionaries.
        """
        return cls(
            callingFunctionResponse=[FunctionResponseUnit.from_dict(f) for f in content]
        )


class ContextRole(Enum):
    """
    上下文角色
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "tool"

@dataclass
class ContentUnit:
    """
    上下文单元
    """
    reasoning_content:str = ""
    content: str = ""
    role: ContextRole = ContextRole.USER
    role_name: str |  None = None
    prefix: bool | None = None
    funcResponse: CallingFunctionResponse | None = None
    tool_call_id: str = ""
    
    # 导出为列表
    @property
    def as_content(self) -> list[dict]:
        """
        导出为content列表
        """
        content_list = []
        if self.content:
            if self.role in {ContextRole.SYSTEM, ContextRole.USER}:
                content = {
                    "role": self.role.value,
                    "content": self.content
                }
                if self.role_name:
                    content["name"] = self.role_name
                content_list.append(content)

            elif self.role == ContextRole.ASSISTANT:
                assistant_content = {
                    "role": self.role.value,
                    "content": self.content,
                }
                if self.role_name:
                    assistant_content["name"] = self.role_name
                if self.prefix:
                    assistant_content["prefix"] = self.prefix
                if self.reasoning_content:
                    assistant_content["reasoning_content"] = self.reasoning_content
                if self.funcResponse:
                    assistant_content["tool_calls"] = self.funcResponse.as_content
                content_list.append(assistant_content)
        if self.funcResponse:
            if self.role == ContextRole.FUNCTION:
                tool_content = {
                    "role": self.role.value,
                    "content": self.content,
                    "tool_call_id": self.tool_call_id
                }
                content_list.append(tool_content)
        
        return content_list
    
    # 从列表中加载内容
    @classmethod
    def load_content(cls, context: dict):
        """
        从字典中加载内容
        """
        content = cls()

        if "role" not in context:
            raise ContextNecessaryFieldsMissingError("Not found role field")
        elif not isinstance(context["role"], str):
            raise ContextFieldTypeError("role field is not str")
        elif context["role"] not in [role.value for role in ContextRole]:
            raise ContextInvalidRoleError(f"Invalid role: {context['role']}")
        else:
            content.role = ContextRole(context["role"])
        
        if "content" not in context:
            raise ContextNecessaryFieldsMissingError("Not found content field")
        elif not isinstance(context["content"], str):
            raise ContextFieldTypeError("content field is not str")
        else:
            content.content = context["content"]
        
        if "reasoning_content" in context:
            if not isinstance(context["reasoning_content"], str):
                raise ContextFieldTypeError("reasoning_content field is not str")
            else:
                content.reasoning_content = context["reasoning_content"]
        
        if "prefix" in context:
            if not isinstance(context["prefix"], bool):
                raise ContextFieldTypeError("prefix field is not bool")
            else:
                content.prefix = context["prefix"]
        
        if content.role == ContextRole.ASSISTANT:
            if "tool_calls" in context:
                if not content.funcResponse:
                    content.funcResponse = FunctionResponse()
                content.funcResponse.from_content(context["tool_calls"])
        
        if content.role == ContextRole.FUNCTION:
            if "tool_call_id" not in context:
                raise ContextNecessaryFieldsMissingError("Not found tool_call_id field")
            elif not isinstance(context['tool_call_id'], str):
                raise ContextFieldTypeError("tool_call_id field is not str")
            else:
                content.tool_call_id = context["tool_call_id"]
        
        return content

@dataclass
class ContextObject:
    """
    上下文对象
    """
    prompt: ContentUnit | None = None
    context_list: list[ContentUnit] = field(default_factory=list)

    @property
    def context(self) -> list[dict]:
        """Get context list"""
        context_list = []
        if self.context_list:
            for content in self.context_list:
                context_list += content.as_content
        return context_list
    
    @property
    def full_context(self) -> list[dict]:
        context_list = self.context
        if self.prompt:
            context_list = self.prompt.as_content + context_list
        return context_list
    
    @property
    def last_content(self) -> ContentUnit:
        """Get last content"""
        if not self.context_list:
            self.context_list.append(ContentUnit())
        return self.context_list[-1]
    
    @property
    def is_empty(self) -> bool:
        return not self.prompt and not self.context_list
    
    @classmethod
    def from_context(cls, context: list[dict]) -> "ContextObject":
        """从上下文列表创建ContextObject
        
        :param context: 上下文列表
        :return: 新的ContextObject
        """
        contextObj = cls()
        contextObj.context_list = []
        for content in context:
            contextObj.context_list.append(ContentUnit.load_content(content))
        return contextObj