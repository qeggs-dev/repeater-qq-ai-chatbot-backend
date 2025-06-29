from environs import Env
from .UserDataManager import MainManager as UserDataManager

_env = Env()

_sub_dir_name:str = _env.str("USER_DATA_SUB_DIR_NAME", "ParallelData")

class ContextManager(UserDataManager):
    def __init__(self):
        super().__init__('Context_UserData', sub_dir_name = _sub_dir_name)

class PromptManager(UserDataManager):
    def __init__(self):
        super().__init__('Prompt_UserData', sub_dir_name = _sub_dir_name)

class UserConfigManager(UserDataManager):
    def __init__(self):
        super().__init__('UserConfig_UserData', sub_dir_name = _sub_dir_name)