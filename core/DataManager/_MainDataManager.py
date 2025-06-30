from environs import Env
from .UserDataManager import MainManager as UserDataManager

_env = Env()

_sub_dir_name:str = _env.str("USER_DATA_SUB_DIR_NAME", "ParallelData")
_cache_metadata:bool = _env.bool("USER_DATA_CACHE_METADATA", False)
_cache_data:bool = _env.bool("USER_DATA_CACHE_DATA", False)

class ContextManager(UserDataManager):
    def __init__(self):
        self.base_name = 'Context_UserData'
        super().__init__(
            base_name = self.base_name,
            cache_metadata = _env.bool(f"{self.base_name.upper()}_CACHE_METADATA", _cache_metadata),
            cache_data = _env.bool(f"{self.base_name.upper()}_CACHE_DATA", _cache_data),
            sub_dir_name = _sub_dir_name
        )

class PromptManager(UserDataManager):
    def __init__(self):
        self.base_name = 'Prompt_UserData'
        super().__init__(
            base_name = self.base_name,
            cache_metadata = _env.bool(f"{self.base_name.upper()}_CACHE_METADATA", _cache_metadata),
            cache_data = _env.bool(f"{self.base_name.upper()}_CACHE_DATA", _cache_data),

            sub_dir_name = _sub_dir_name
        )

class UserConfigManager(UserDataManager):
    def __init__(self):
        self.base_name = 'UserConfig_UserData'
        super().__init__(
            base_name = self.base_name,
            cache_metadata = _env.bool(f"{self.base_name.upper()}_CACHE_METADATA", _cache_metadata),
            cache_data = _env.bool(f"{self.base_name.upper()}_CACHE_DATA", _cache_data),
            sub_dir_name = _sub_dir_name
        )