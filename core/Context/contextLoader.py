# ==== 标准库 ==== #
import copy
import aiofiles
from typing import (
    Any,
    Awaitable,
)
import time
from pathlib import Path

# ==== 第三方库 ==== #
from openai import AsyncOpenAI
from environs import Env
from loguru import logger

# ==== 自定义库 ==== #
from ..DataManager import (
    PromptManager,
    ContextManager,
    UserConfigManager
)
from .object import (
    ContextObject,
)
from TextProcessors import (
    PromptVP,
    limit_blank_lines,
)
from sanitizeFilename import sanitize_filename_async

# ==== 本模块代码 ==== #
env = Env()

class ContextLoader:
    def __init__(
        self, config: UserConfigManager,
        prompt: PromptManager,
        context: ContextManager,
        prompt_vp: PromptVP
    ):
        self.config = config
        self.prompt = prompt
        self.context = context
        self.prompt_vp = prompt_vp
    
    async def _load_prompt(self, context:ContextObject, user_id: str) -> ContextObject:
        # 从环境变量中获取默认提示词文件位置
        default_prompt_dir = env.path("DEFAULT_PROMPT_DIR", Path())
        if default_prompt_dir.exists():
            # 如果存在默认提示词文件，则加载默认提示词文件
            parset_prompt_name = await self.config.load(user_id, env.str("PARSET_PROMPT_NAME"))

            default_prompt_file = default_prompt_dir / f'{await sanitize_filename_async(parset_prompt_name)}.txt'
            if default_prompt_file.exists():
                logger.info(f"Load Default Prompt File: {default_prompt_file}", user_id = user_id)
                async with aiofiles.open(default_prompt_file, mode="r", encoding="utf-8") as f:
                    context.prompt = await f.read()
        user_prompt:str = await self.prompt.load(user_id=user_id, default='')
        if user_prompt:
            context.prompt = user_prompt
        context.prompt = await self._expand_variables(context.prompt, variables = self.prompt_vp, user_id=user_id)
        return context

    async def _load_context(self, context:ContextObject, user_id: str, New_Message: str, Message_Role: str = 'user', Message_Role_Name: str | None = None) -> ContextObject:
        user_context:list[dict] = await self.context.load(user_id=user_id, default=[])
        context.context_list = user_context
        context.new_content = await self._expand_variables(New_Message, variables = self.prompt_vp, user_id=user_id)
        context.new_content_role = Message_Role
        context.new_content_role_name = Message_Role_Name
        return context
    
    async def load(self, user_id: str, New_Message: str, Message_Role: str = 'user', Message_Role_Name: str | None = None, load_prompt: bool = True) -> ContextObject:
        if load_prompt:
            context = await self._load_prompt(ContextObject(), user_id=user_id)
        context = await self._load_context(
            context = context,
            user_id = user_id,
            New_Message = New_Message,
            Message_Role = Message_Role,
            Message_Role_Name = Message_Role_Name
        )
        return context
    
    async def _expand_variables(self, prompt: str, variables: PromptVP, user_id: str) -> str:
        variables.reset_counter()
        prompt = variables.process(prompt)
        logger.info(f"Prompt Hits Variable: {variables.hit_var()}/{variables.discover_var()}({variables.hit_var() / variables.discover_var() if variables.discover_var() != 0 else 0:.2%})", user_id = user_id)
        variables.reset_counter()
        prompt = limit_blank_lines(prompt)
        return prompt

    async def save(self, user_id: str, context: ContextObject) -> None:
        context = copy.deepcopy(context)
        context.prompt = ''
        await self.context.save(user_id, context.full_context)