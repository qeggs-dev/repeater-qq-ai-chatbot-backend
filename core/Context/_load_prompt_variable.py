from ..DataManager import PromptManager, ContextManager
from TimeParser import (
    format_deltatime,
    format_deltatime_ns,
    format_deltatime_high_precision
)
from TextProcessors import PromptVP, limit_blank_lines

class LoadPromptVariable:
    def __init__(self, **kwargs):
        self._variable = kwargs

    # def __init__(self, config: UserConfigManager, prompt: PromptManager, context: ContextManager):
    #     self.config = config
    #     self.prompt = prompt
    #     self.context = context

    async def get_prompt_variable(self, user_id: str, **kwargs) -> PromptVP:
        prompt_vp = PromptVP()

        prompt_vp.bulk_register_variable(**self._variable)
        prompt_vp.bulk_register_variable(**kwargs)
        prompt_vp.register_variable("user_id", user_id)
    
        return prompt_vp
