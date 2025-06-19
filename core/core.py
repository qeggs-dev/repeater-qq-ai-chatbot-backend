# ==== 标准库 ==== #
import asyncio
import sys
import time
import atexit
from typing import (
    Coroutine,
)
import random
from pathlib import Path

# ==== 第三方库 ==== #
from environs import Env
from loguru import logger
import aiofiles
import orjson

# ==== 自定义库 ==== #
from .CallAPI import (
    Client,
    Request,
    Response
)
from .Context import (
    ContextLoader,
    LoadPromptVariable,
    ContextObject
)
from .DataManager import (
    ContextManager,
    PromptManager,
    UserConfigManager
)
from .ApiInfo import (
    ApiInfo,
    ApiGroup
)
from .CallLog import (
    CallLogManager,
    CallLog
)
from TextProcessors import (
    PromptVP
)
from TimeParser import (
    format_timestamp,
    get_birthday_countdown,
    date_to_zodiac,
    format_timestamp,
    calculate_age
)

# ==== 本模块代码 ==== #
env = Env()

__version__ = env.str("VERSION", "4.0.1.0 Beta")

class Core:
    def __init__(self, max_concurrency: int | None = None):
        self.client = Client(env.int('MAX_CONCURRENCY', 10) if max_concurrency is None else max_concurrency)

        logger.remove()  # 移除默认处理器
        logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[user_id]}</cyan> - <level>{message}</level>")

        self.lock = asyncio.Lock()
        self.context_manager = ContextManager()
        self.prompt_manager = PromptManager()
        self.user_config_manager = UserConfigManager()
        self.promptvariable = LoadPromptVariable(
            version = __version__
        )
        self.api_client = Client()
        self.apiinfo = ApiInfo()
        self.apiinfo.load(env.path('API_INFO_FILE_PATH'))
        self.session_locks = {}
        self.calllog = CallLogManager(env.path('CALL_LOG_FILE_PATH'))
        
        def _exit():
            if env.bool("SAVE_CALL_LOG", True):
                self.calllog.save_call_log()

        atexit.register(_exit)

    async def _get_session_lock(self, user_id: str) -> asyncio.Lock:
        async with self.lock:
            if user_id not in self.session_locks:
                self.session_locks[user_id] = asyncio.Lock()
            lock = self.session_locks[user_id]
        return lock
    
    
    # region > get prompt_vp
    async def get_prompt_vp(
        self,
        user_id: str,
        user_name: str = "",
        model_type: str = "",
        print_chunk: bool = True,
        config: dict = {}
    ) -> PromptVP:
        return await self.promptvariable.get_prompt_variable(
            user_id = user_id,
            user_name = user_name,
            BirthdayCountdown = lambda **kw: get_birthday_countdown(
                env.int("BIRTHDAY_MONTH"),
                env.int("BIRTHDAY_DAY"),
                name=env.str("BOT_NAME","Bot")
            ),
            model_type = model_type,
            botname = env.str("BOT_NAME", "Bot"),
            print_chunk = str(print_chunk),
            birthday = f'{env.int("BIRTHDAY_YEAR")}.{env.int("BIRTHDAY_MONTH")}.{env.int("BIRTHDAY_DAY")}',
            zodiac = lambda **kw: date_to_zodiac(env.int("BIRTHDAY_MONTH"), env.int("BIRTHDAY_DAY")),
            time = lambda **kw: format_timestamp(time.time(), config.get("timezone", env.int("TIMEZONE_OFFSET", default=8)), '%Y-%m-%d %H:%M:%S %Z'),
            age = lambda **kw: calculate_age(env.int("BIRTHDAY_YEAR"), env.int("BIRTHDAY_MONTH"), env.int("BIRTHDAY_DAY"), offset_timezone = config.get("timezone", env.int("TIMEZONE_OFFSET", default=8))),
            random = lambda min, max: random.randint(int(min), int(max)),
            randfloat = lambda min, max: random.uniform(float(min), float(max)),
            randchoice = lambda *args: random.choice(args)
        )
    # endregion
    
    # region > load nickname mapping
    async def load_nickname_mapping(self, user_id: str, user_name: str) -> str:
        unm_path = env.path('USER_NICKNAME_MAPPING_FILE_PATH', Path())
        if not unm_path.exists():
            return user_name
        async with aiofiles.open(env.path('USER_NICKNAME_MAPPING_FILE_PATH'), 'rb') as f:
            fdata = await f.read()
            try:
                nickname_mapping = orjson.loads(fdata)
            except orjson.JSONDecodeError:
                nickname_mapping = {}
        
        if user_name in nickname_mapping:
            logger.info(f"User Name [{user_name}] -> [{nickname_mapping[user_name]}]", user_id=user_id)
            user_name = nickname_mapping[user_name]
        elif user_id in nickname_mapping:
            user_name = nickname_mapping[user_id]
        
        return user_name
    # endregion

    # region > Chat
    async def Chat(
        self,
        message: str,
        user_id: str,
        user_name: str,
        role: str = "user",
        role_name:  str = "",
        model_type: str | None = None,
        load_prompt: bool = True,
        print_chunk: bool = True,
        save_context: bool = True,
        reference_context_id: str | None = None,
        continue_completion: bool = False,
    ) -> dict[str, str]:
        task_start_time = time.time_ns()
        lock = await self._get_session_lock(user_id)
        
        async with lock:
            logger.info("====================================", user_id = user_id)
            logger.info("Start Task", user_id = user_id)

            user_name = await self.load_nickname_mapping(user_id, user_name)

            config = await self.user_config_manager.load(user_id=user_id)
            if not config or not isinstance(config, dict):
                config = {}
            
            if not model_type:
                model_type = config.get("model_type", env.str("DEFAULT_MODEL_TYPE", "chat"))

            context_loader = ContextLoader(
                config=self.user_config_manager,
                prompt=self.prompt_manager,
                context=self.context_manager,
                prompt_vp = await self.get_prompt_vp(
                    user_id = user_id,
                    user_name = user_name,
                    model_type = model_type,
                    print_chunk = print_chunk,
                    config = config
                )
            )

            if reference_context_id:
                context = await context_loader.load(
                    user_id = reference_context_id,
                    message = message,
                    role = role,
                    roleName = role_name if role_name else user_name,
                    load_prompt = load_prompt,
                    continue_completion = continue_completion
                )
            else:
                context = await context_loader.load(
                    user_id = user_id,
                    message = message,
                    role = role,
                    load_prompt = load_prompt,
                    continue_completion = continue_completion
                )
            
            request = Request()
            request.context = context
    
            apilist = self.apiinfo.find_type(model_type = model_type)
            api = apilist[0]
            
            request.url = api.url
            request.model = api.model_id
            request.key = api.api_key
            logger.info(f"API URL: {api.url}", user_id = user_id)
            logger.info(f"API Model: {api.model_name}", user_id = user_id)
            if request.context.last_content.content:
                logger.info("Message:", user_id = user_id)
                print(request.context.last_content.content, file=sys.stderr, flush=True)
            else:
                logger.warning("No message to send", user_id = user_id)
            logger.info(f"User Name: {user_name}", user_id = user_id)

            request.user_name = user_name
            request.temperature = config.get("temperature", env.float("DEFAULT_TEMPERATURE", default=None))
            request.top_p = config.get("top_p", env.float("DEFAULT_TOP_P", default=None))
            request.max_tokens = config.get("max_tokens", env.int("DEFAULT_MAX_TOKENS", default=None))
            request.max_completion_tokens = config.get("max_completion_tokens", env.int("DEFAULT_MAX_COMPLETION_TOKENS", default=None))
            request.stop = config.get("stop", None)
            request.stream = env.bool("STREAM", True)
            request.frequency_penalty = config.get("frequency_penalty", env.float("DEFAULT_FREQUENCY_PENALTY", default=None))
            request.presence_penalty = config.get("presence_penalty", env.float("DEFAULT_PRESENCE_PENALTY", default=None))
            request.print_chunk = print_chunk

            call_prepare_end_time = time.time_ns()

            response = await self.api_client.submit_Request(user_id=user_id, request=request)

            response.calling_log.task_start_time = task_start_time
            response.calling_log.call_prepare_start_time = task_start_time
            response.calling_log.call_prepare_end_time = call_prepare_end_time
            response.calling_log.created_time = response.created
            prompt_vp = await self.get_prompt_vp(
                user_id = user_id,
                user_name = user_name,
                model_type = model_type,
                print_chunk = print_chunk,
                config = config
            )
            response.context.last_content.content = prompt_vp.process(response.context.last_content.content)
            logger.info(f"Prompt Hits Variable: {prompt_vp.hit_var()}/{prompt_vp.discover_var()}({prompt_vp.hit_var() / prompt_vp.discover_var() if prompt_vp.discover_var() != 0 else 0:.2%})", user_id = user_id)
            if save_context:
                await context_loader.save(
                    user_id = user_id,
                    context = response.context
                )
            else:
                logger.warning("Context not saved", user_id = user_id)

            response.calling_log.task_end_time = time.time_ns()

            await self.calllog.add_call_log(response.calling_log)

            logger.success(f"API call successful", user_id = user_id)
            return {
                "reasoning_content": response.context.last_content.reasoning_content,
                "content": response.context.last_content.content,
                "model_name": api.model_name,
                "model_type": api.model_type,
                "model_id": api.model_id,
            }
    # endregion