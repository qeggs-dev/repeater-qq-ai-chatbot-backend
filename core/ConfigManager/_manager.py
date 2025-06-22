
from typing import Any
from ..DataManager import UserConfigManager
from ._exceptions import *
from envManager import (
    EnvManager,
    EnvType
)
from envManager import Exceptions as EnvExceptions

class ConfigManager:
    # 用户配置管理器 (定义为类属性以减少重复实例化)
    _userConfigManager = UserConfigManager()
    # 环境变量管理器 (同上，定义为类属性以减少重复实例化)
    _envManager = EnvManager()
    
    def __init__(self):
        pass

    def get(self, user_id: str, key: str, default = None):
        config = self._userConfigManager.load(user_id, {})
        if not isinstance(config, dict):
            config = {}
        
        return config.get(key, self._envManager.get(key, default))

    def register(self, required: list[dict[str, Any]]):
        """批量定义配置"""
        try:
            for config in required:
                config["key"]
                self._envManager.batch_def([config])
        except KeyError as e:
            raise UnintelligibleBatchFormat(f"Missing key in batch format: {e}")