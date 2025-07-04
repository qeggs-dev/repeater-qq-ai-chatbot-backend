# ==== 标准库 ==== #
import copy
import aiofiles
from typing import (
    Any,
    Awaitable,
)
import time
from pathlib import Path
import orjson

# ==== 第三方库 ==== #
from openai import AsyncOpenAI
from loguru import logger

# ==== 自定义库 ==== #
from ..DataManager import (
    PromptManager,
    ContextManager
)
from ..UserConfigManager import (
    ConfigManager,
    Configs
)
from ._object import (
    ContextObject,
    ContentUnit,
    ContextRole
)
from ._exceptions import *
from TextProcessors import (
    PromptVP,
    limit_blank_lines,
)
from PathProcessors import validate_path, sanitize_filename_async
from ConfigManager import ConfigLoader

# ==== 本模块代码 ==== #
configs = ConfigLoader()

class ContextLoader:
    def __init__(
            self,
            config: ConfigManager,
            prompt: PromptManager,
            context: ContextManager,
            prompt_vp: PromptVP
        ):
        self.config: ConfigManager = config
        self.prompt: PromptManager = prompt
        self.context: ContextManager = context
        self.prompt_vp: PromptVP = prompt_vp
    
    async def _load_prompt(self, context:ContextObject, user_id: str) -> ContextObject:
        user_prompt:str = await self.prompt.load(user_id=user_id, default='')
        if user_prompt:
            # 使用用户提示词
            prompt = user_prompt
            logger.info(f"Load User Prompt", user_id = user_id)
        else:
            # 加载默认提示词
            default_prompt_dir = configs.get_config("Default_Prompt_Dir", Path()).get_value(Path)
            if default_prompt_dir.exists():
                # 如果存在默认提示词文件，则加载默认提示词文件
                config = await self.config.load(user_id)
                
                # 获取默认提示词文件名
                parset_prompt_name = config.get("parset_prompt_name", configs.get_config("parset_prompt_name", "default").get_value(str))

                # 加载默认提示词文件
                default_prompt_file = default_prompt_dir / f'{await sanitize_filename_async(parset_prompt_name)}.txt'
                if not validate_path(default_prompt_dir, default_prompt_file):
                    raise InvalidPromptPathError(f"Invalid Prompt Path: {default_prompt_file}")
                if default_prompt_file.exists():
                    logger.info(f"Load Default Prompt File: {default_prompt_file}", user_id = user_id)
                    async with aiofiles.open(default_prompt_file, mode="r", encoding="utf-8") as f:
                        prompt = await f.read()
                else:
                    logger.warning(f"Default Prompt File Not Found: {default_prompt_file}", user_id = user_id)
                    prompt = ""
            else:
                logger.warning(f"Default Prompt Directory Not Found: {default_prompt_dir}", user_id = user_id)
                prompt = ""
        # 展开变量
        prompt = await self._expand_variables(prompt, variables = self.prompt_vp, user_id=user_id)

        # 创建Content单元
        prompt = ContentUnit(
            role = ContextRole.SYSTEM,
            content = prompt
        )
        # 将Content单元加入Context
        context.prompt = prompt
        return context

    async def _append_context(
            self,
            context:ContextObject,
            user_id: str,
            new_message: str,
            role: str = 'user',
            role_name: str | None = None,
            continue_completion: bool = False
        ) -> ContextObject:
        """
        添加上下文

        :param context: 上下文对象
        :param user_id: 用户ID
        :param New_Message: 新消息
        :param role: 角色
        :param roleName: 角色名称
        :param continue_completion: 是否继续完成
        :return: 上下文对象
        """
        try:
            context_list = await self.context.load(user_id=user_id, default=[])
        except orjson.JSONDecodeError:
            raise ContextLoadingSyntaxError(f"Context File Syntax Error: {user_id}")
        if not continue_completion:
            # 构建上下文对象
            contextObj = ContextObject()
            content = ContentUnit()
            content.content = await self._expand_variables(new_message, variables = self.prompt_vp, user_id=user_id)
            content.role = ContextRole(role)
            content.role_name = role_name
            contextObj.update_from_context(context_list)
            logger.info(f"Load Context: {len(contextObj.context_list)}", user_id = user_id)

            # 添加上下文
            if not context.context_list:
                context.context_list = []
            context.context_list += contextObj.context_list
            context.context_list.append(content)
        return context
    
    async def load(
            self,
            user_id: str,
            message: str,
            role: str = 'user',
            role_name: str | None = None,
            load_prompt: bool = True,
            continue_completion: bool = False
        ) -> ContextObject:
        """
        加载上下文

        :param user_id: 用户ID
        :param message: 消息内容
        :param role: 角色
        :param roleName: 角色名称
        :param load_prompt: 是否加载提示词
        :param continue_completion: 是否继续生成
        """
        # 如果允许添加提示词，就加载提示词，否则使用空上下文对象
        if load_prompt:
            context = await self._load_prompt(ContextObject(), user_id=user_id)
        else:
            context = ContextObject()
        
        # 添加上下文
        context = await self._append_context(
            context = context,
            user_id = user_id,
            new_message = message,
            role = role,
            role_name = role_name,
            continue_completion = continue_completion
        )
        return context
    
    async def _expand_variables(self, prompt: str, variables: PromptVP, user_id: str) -> str:
        """
        展开变量

        :param prompt: 提示词
        :param variables: 变量
        :param user_id: 用户ID
        """
        variables.reset_counter()
        prompt = variables.process(prompt)
        logger.info(f"Prompt Hits Variable: {variables.hit_var()}/{variables.discover_var()}({variables.hit_var() / variables.discover_var() if variables.discover_var() != 0 else 0:.2%})", user_id = user_id)
        variables.reset_counter()
        prompt = limit_blank_lines(prompt)
        return prompt

    async def save(
            self,
            user_id: str,
            context: ContextObject,
        ) -> None:
        """
        保存上下文

        :param user_id: 用户ID
        :param context: 上下文对象
        """
        await self.context.save(user_id, context.context)