from dataclasses import dataclass, field, fields, replace
import orjson
import copy

@dataclass
class FunctionParameters:
    """
    This class is used to store the information about a parameter of a function to be called by the OpenAI API.
    """
    name: str = ''
    type: str = ''
    description: str = ''
    required: bool = False

@dataclass
class CallingFunction:
    """
    This class is used to store the information about a function to be called by the OpenAI API.
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
    CallingFunctionRequest class is used to store the information about a function request to be sent to the OpenAI API.
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
class FunctionResponse:
    """
    FunctionResponse is a dataclass that represents the response from a function call.
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

@dataclass
class CallingFunctionResponse:
    """
    CallingFunctionResponse is a dataclass that represents the response from a calling function.
    """
    callingFunctionResponse:list[FunctionResponse] = field(default_factory=list)

    @property
    def as_content(self) -> list[dict]:
        """
        Returns the response as a list of dictionaries.
        """
        return [f.as_dict for f in self.callingFunctionResponse]

@dataclass
class ContextObject:
    """Context objects, which are responsible for delivering contextual content"""
    prompt: str = ""
    context_list: list[dict] = field(default_factory=list)
    reasoning_content:str = ""
    new_content: str = ""
    new_content_role: str = "user"
    new_content_role_name: str |  None = None
    prefix: bool | None = None
    funcResponse: CallingFunctionResponse | None = None
    tool_call_id: str = ""

    @property
    def context(self) -> list[dict]:
        if self.new_content_role not in {"system", "user", "assistant", "tool"}:
            raise ValueError("new_context_role must be 'system', 'user', 'assistant' or 'tool'")
        
        context_list = copy.deepcopy(self.context_list)

        if self.new_content:
            if self.new_content_role in {"system", "user"}:
                content = {
                    "role": self.new_content_role,
                    "content": self.new_content
                }
                if self.new_content_role_name:
                    content["name"] = self.new_content_role_name
                context_list += [content]

            elif self.new_content_role == "assistant":
                assistant_content = {
                    "role": "assistant",
                    "content": self.new_content,
                }
                if self.new_content_role_name:
                    content["name"] = self.new_content_role_name
                if self.prefix:
                    content["prefix"] = self.prefix
                if self.reasoning_content:
                    content["reasoning_content"] = self.reasoning_content
                if self.funcResponse:
                    content["tool_calls"] = self.funcResponse.as_content
                context_list += [assistant_content]
        if self.funcResponse:
            if self.new_content_role == "tool":
                tool_content = {
                    "role": "tool",
                    "content": self.new_content,
                    "tool_call_id": self.tool_call_id
                }
        
        return context_list
    
    @property
    def full_context(self) -> list[dict]:
        context_list = self.context
        if self.prompt:
            context_list = [
                {
                    "role": "system",
                    "content": self.prompt
                }
            ] + context_list
        
        return context_list