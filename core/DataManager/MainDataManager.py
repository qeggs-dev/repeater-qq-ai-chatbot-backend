from .UserDataManager import MainManager

class ContextManager(MainManager):
    def __init__(self):
        super().__init__('Context_UserData')

class PromptManager(MainManager):
    def __init__(self):
        super().__init__('Prompt_UserData')

class UserConfigManager(MainManager):
    def __init__(self):
        super().__init__('UserConfig_UserData')