import environs
from typing import Any
from ._exceptions import *
from ._object import EnvObject, EnvType

class EnvManager:
    """
    一个环境变量管理器
    允许在运行时检查环境变量

    :param check_after_definition: 是否在定义环境变量后立即检查
    """
    def __init__(self, check_after_definition: bool = True):
        self._env = environs.Env()
        self._required:dict[str, EnvObject] = {}
        self._optional:dict[str, EnvObject] = {}
        self.check_after_definition = check_after_definition

    def load_env(self, env_file):
        """加载环境变量文件"""
        self._env.read_env(env_file)
    
    def def_required(self, key: str, type: EnvType = EnvType.AUTO):
        """定义一个必须的环境变量"""
        if not self.check_after_definition:
            self._required[key] = EnvObject(key, env_type = type)
        else:
            if key in self._env:
                self._required[key] = EnvObject(key, env_type = type)
            else:
                raise EnvNotFoundError(f"Environment variable {key} not found")

    def def_optional(self, key: str, default: Any, env_type: EnvType):
        """定义一个可选的环境变量"""
        self._optional[key] = EnvObject(key, default, env_type)
    
    def batch_def(self, required: list[dict[str, Any]]):
        """批量定义环境变量"""
        try:
            for item in required:
                if item["mode"] == "required":
                    try:
                        self.def_required(item["key"], EnvType(item.get("type", "auto").lower()))
                    except ValueError:
                        raise EnvTypeError(f"Environment variable {item['key']} type error")
                elif item["mode"] == "optional":
                    try:
                        self.def_optional(item["key"], item["default"], EnvType(item.get("type", "auto").lower()))
                    except ValueError:
                        raise EnvTypeError(f"Environment variable {item['key']} type error")
                else:
                    raise UnintelligibleBatchFormat(f"Unintelligible batch format: {item}")
        except KeyError as e:
            raise UnintelligibleBatchFormat(f"Missing key in batch format: {e}")
        
    
    def get(self, key: str, default: Any = None) -> EnvObject:
        """获取环境变量"""
        if key in self._required and key in self._env:
            return self._required[key]
        elif key in self._optional:
            env = self._optional[key]
            if default is not None:
                env.default = default
            return env
        else:
            raise EnvNotFoundError(f"Key {key} is not defined in the environment manager")
    
