import orjson
from dataclasses import dataclass
from environs import Env
from typing import Any
from pathlib import Path
from enum import Enum
from ._exceptions import *

_env: Env = Env()

class EnvType(Enum):
    """
    环境变量类型
    """
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    LIST = "list"
    STR = "str"
    JSON = "json"
    PATH = "path"
    AUTO = "auto"

# 类型转换列表 (必须是有序容器以保证类型转换的优先级)
_TYPES = [
    float,
    int,
    bool,
    list
]

@dataclass
class EnvObject:
    """
    环境变量对象

    :param name: 环境变量名称
    :param default: 默认值
    :param env_type: 环境变量类型

    :raises EnvNotFoundError: 环境变量未找到
    :raises EnvTypeError: 环境变量类型错误
    """
    name: str = ""
    default: Any | None = None
    env_type: EnvType | None = None
    
    @property
    def int(self) -> int:
        """
        获取环境变量值（int类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(f"{self.name} not found")
        if self.env_type not in {EnvType.INT, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not an int")
        return _env.int(self.name, self.default)

    @property
    def float(self) -> float:
        """
        获取环境变量值（float类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.FLOAT, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a float")
        return _env.float(self.name, self.default)

    @property
    def str(self) -> str:
        """
        获取环境变量值（str类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.STRING, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a string")
        return _env.str(self.name, self.default)

    @property
    def bool(self) -> bool:
        """
        获取环境变量值（bool类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.BOOL, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a bool")
        return _env.bool(self.name, self.default)

    @property
    def list(self) -> list:
        """
        获取环境变量值（list类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.LIST, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a list")
        return _env.list(self.name, self.default)

    @property
    def json(self) -> Any:
        """
        获取环境变量值（json类型）
        """

        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.JSON, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a json")
        return _env.json(self.name, self.default)
    
    @property
    def path(self) -> Path:
        """
        获取环境变量值（路径类型）
        """
        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        if self.env_type not in {EnvType.PATH, EnvType.AUTO}:
            raise EnvTypeError(f"{self.name} is not a path")
        return _env.path(self.name, self.default)
    
    @property
    def auto(self) -> Any:
        """
        获取环境变量值（自动类型）
        """

        if self.default is None and not self.exists():
            raise EnvNotFoundError(self.name)
        elif self.default is not None:
            return self.default
        
        if self.env_type != EnvType.AUTO:
            raise EnvTypeError(f"{self.name} is not an auto type")

        env = _env.str(self.name)
        if env in {"null", "None"}:
            return None
        for type in _TYPES:
            try:
                return type(env)
            except ValueError:
                pass
        try:
            return orjson.loads(env)
        except orjson.JSONEncodeError:
            pass
        return env
    
    @property
    def maybe_type(self) -> type:
        """
        返回可能的类型
        """
        return self.env_type
        

    def exists(self) -> bool:
        """
        判断环境变量是否存在
        """
        return self.name in _env

    def __repr__(self) -> str:
        return f"<EnvObject {self.name} {self.auto!r}>"
    
    def __bool__(self) -> bool:
        return self.exists()
    
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, EnvObject):
            return self.name == other.name
        return self.auto == other