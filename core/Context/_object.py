from dataclasses import dataclass, field, fields, replace
import orjson
from enum import Enum
from typing import Any
from ._exceptions import *

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
        """
        获取函数对象字典
        """
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

class FunctionChoice(Enum):
    """
    FunctionCalling选择对象
    """
    NONE = 'none'
    AUTO = 'auto'
    REQUIRED = 'required'
    SPECIFY = 'specify'


@dataclass
class CallingFunctionRequest:
    """
    FunctionCalling请求对象
    """
    functions: list[CallingFunction] = field(default_factory=list)
    func_choice: FunctionChoice | None = None
    func_choice_name: str | None = None

    @property
    def tool_choice(self) -> str | dict | None:
        """
        tool_choice字段值
        """
        if self.func_choice == FunctionChoice.SPECIFY:
            return {
                'type': 'function',
                'function': {
                    'name': self.func_choice_name
                }
            }
        else:
            return self.func_choice.value
    
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

    def update_from_dict(self, data: dict):
        """
        从字典更新对象
        """
        other = self.from_dict(data)
        self.id = other.id
        self.type = other.type
        self.name = other.name
        self.arguments_str = other.arguments_str

    @property
    def arguments(self) -> Any:
        """
        从模型输出的参数字符串中解析出对象
        """
        try:
            return orjson.loads(self.arguments_str)
        except orjson.JSONDecodeError:
            raise ContextSyntaxError('Invalid JSON format in function response arguments.')
    
    @property
    def as_dict(self) -> dict:
        """
        OpenAI兼容的FunctionCalling响应对象单元格式
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
    def from_dict(cls, data: dict) -> "FunctionResponseUnit":
        """
        从字典创建对象

        :param data: OpenAI兼容的FunctionCalling响应对象单元格式
        """
        # 处理id字段
        if 'id' not in data:
            raise ContextNecessaryFieldsMissingError('"id" is a necessary field.')
        elif not isinstance(data['id'], str):
            raise ContextFieldTypeError('"id" must be a string.')
        else:
            id = data['id']
        
        # 处理type字段
        if 'type' not in data:
            raise ContextNecessaryFieldsMissingError('"type" is a necessary field.')
        elif not isinstance(data['type'], str):
            raise ContextFieldTypeError('"type" must be a string.')
        else:
            type = data['type']
        
        # 处理function字段
        if 'function' not in data:
            raise ContextNecessaryFieldsMissingError('"function" is a necessary field')
        elif not isinstance(data['function'], dict):
            raise ContextFieldTypeError('"function" must be a dictionary.')
        else:
            # 处理function.name字段
            if 'name' not in data['function']:
                raise ContextNecessaryFieldsMissingError('"function.name" is a necessary field')
            elif not isinstance(data['function']['name'], str):
                raise ContextFieldTypeError('"function.name" must be a string')
            else:
                name = data['function']['name']
            
            # 处理function.arguments字段
            if 'arguments' not in data['function']:
                raise ContextNecessaryFieldsMissingError('"function.arguments" is a necessary field')
            elif not isinstance(data['function']['arguments'], str):
                raise ContextFieldTypeError('"function.arguments" must be a string')
            else:
                arguments_str = data['function']['arguments']
        
        # 返回对象
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

    def update_from_dict(self, content: list[dict]):
        other = self.from_content(content)
        self.callingFunctionResponse = other.callingFunctionResponse
    
    @property
    def as_content(self) -> list[dict]:
        """
        模型响应对象列表
        """
        return [f.as_dict for f in self.callingFunctionResponse]
    
    @classmethod
    def from_content(cls, content: list[dict]):
        """
        从模型响应对象列表中构建响应对象

        :param content: 模型响应对象列表
        :return: 响应对象
        """
        return cls(
            callingFunctionResponse = [FunctionResponseUnit().from_dict(f) for f in content]
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

    def __len__(self):
        if self.reasoning_content:
            return len(self.reasoning_content)
        else:
            return len(self.content)
    
    def update_from_content(self, content: dict) -> None:
        """
        更新上下文内容
        :param content: 上下文内容
        :return:
        """
        other = self.from_content(content)
        self.reasoning_content = other.reasoning_content
        self.content = other.content
        self.role = other.role
        self.role_name = other.role_name
        self.prefix = other.prefix
        self.funcResponse = other.funcResponse
        self.tool_call_id = other.tool_call_id
    
    # 导出为列表
    @property
    def as_content(self) -> list[dict]:
        """
        OpenAI Message兼容格式列表单元
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
    def from_content(cls, context: dict):
        """
        从Message列表单元中加载内容

        :param context: OpenAI Message兼容格式列表单元
        :return: Context
        """
        content = cls()

        if "role" not in context:
            raise ContextNecessaryFieldsMissingError("Not found role field")
        elif not isinstance(context["role"], str):
            raise ContextFieldTypeError("role field is not str")
        elif context["role"] not in [role.value for role in ContextRole]:
            raise ContextInvalidRoleError(f"Invalid role: {context['role']}")
        else:
            try:
                content.role = ContextRole(context["role"])
            except ValueError:
                raise ContextInvalidRoleError(f"Invalid role: {context['role']}")
        
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
                    content.funcResponse = CallingFunctionResponse()
                content.funcResponse.update_from_dict(context["tool_calls"])
        
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

    def __len__(self):
        return len(self.context_list)
    
    def update_from_context(self, context: list[dict]) -> None:
        """
        从上下文列表更新上下文
        
        :param context: 上下文列表
        :return: 构建的对象
        """
        other = self.from_context(context)
        self.context_list = other.context_list
        self.prompt = other.prompt

    @property
    def total_length(self) -> int:
        """
        获取上下文总长度
        
        :return: 上下文总长度
        """
        return sum([len(content) for content in self.context_list]) + (len(self.prompt) if self.prompt else 0)

    @property
    def context(self) -> list[dict]:
        """
        获取上下文
        """
        context_list = []
        if self.context_list:
            for content in self.context_list:
                context_list += content.as_content
        return context_list
    
    @property
    def full_context(self) -> list[dict]:
        """
        获取上下文，如果有提示词，则添加到最前面
        """
        context_list = self.context
        if self.prompt:
            context_list = self.prompt.as_content + context_list
        return context_list
    
    @property
    def last_content(self) -> ContentUnit:
        """
        获取最后一个上下文单元
        """
        if not self.context_list:
            self.context_list.append(ContentUnit())
        return self.context_list[-1]
    
    def append(self, content: ContentUnit) -> None:
        """
        添加上下文单元
        """
        self.context_list.append(content)
    
    @property
    def is_empty(self) -> bool:
        """
        判断上下文是否为空
        """
        return not self.prompt and not self.context_list
    
    @classmethod
    def from_context(cls, context: list[dict]) -> "ContextObject":
        """
        从上下文列表构建对象
        
        :param context: 上下文列表
        :return: 构建的对象
        """
        contextObj = cls()
        contextObj.context_list = []
        for content in context:
            contextObj.context_list.append(ContentUnit().from_content(content))
        return contextObj