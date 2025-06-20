from .UserDataManager import MainManager as UserDataManager

class ContextManager(UserDataManager):
    def __init__(self):
        super().__init__('Context_UserData')

class PromptManager(UserDataManager):
    def __init__(self):
        super().__init__('Prompt_UserData')

class UserConfigManager(UserDataManager):
    def __init__(self):
        super().__init__('UserConfig_UserData')