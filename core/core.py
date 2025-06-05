# ==== 标准库 ==== #
import asyncio
import sys
import time
import atexit
from typing import (
    Coroutine,
)

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
from TimeParser import (
    format_timestamp,
    get_birthday_countdown,
    date_to_zodiac,
    format_timestamp,
    calculate_age
)

# ==== 本模块代码 ==== #
env = Env()

__version__ = '4.0.0.0 Beta'

class Core:
    def __init__(self, max_concurrency: int = None):
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
            self.calllog.save_call_log()

        atexit.register(_exit)

    async def get_session_lock(self, user_id: str) -> asyncio.Lock:
        async with self.lock:
            if user_id not in self.session_locks:
                self.session_locks[user_id] = asyncio.Lock()
            lock = self.session_locks[user_id]
        return lock

    # region > Chat
    async def Chat(
        self,
        message: str,
        user_id: str,
        user_name: str,
        model_type: str = "",
        load_prompt: bool = True,
        print_chunk: bool = True,
        save_context: bool = True
    ) -> dict[str, str]:
        task_start_time = time.time_ns()
        lock = await self.get_session_lock(user_id)
        
        async with lock:
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

            config = await self.user_config_manager.load(user_id=user_id)
            if not config or not isinstance(config, dict):
                config = {}

            context_loader = ContextLoader(
                config=self.user_config_manager,
                prompt=self.prompt_manager,
                context=self.context_manager,
                prompt_vp = await self.promptvariable.get_prompt_variable(
                    user_id = user_id,
                    user_name = user_name,
                    BirthdayCountdown = lambda **kw: get_birthday_countdown(
                        env.int("BIRTHDAY_MONTH"),
                        env.int("BIRTHDAY_DAY"),
                        name=env.str(
                            "BOT_NAME",
                            default = ""
                        )
                    ),
                    model_type = model_type,
                    print_chunk = str(print_chunk),
                    birthday = f'{env.int("BIRTHDAY_YEAR")}.{env.int("BIRTHDAY_MONTH")}.{env.int("BIRTHDAY_DAY")}',
                    zodiac = lambda **kw: date_to_zodiac(env.int("BIRTHDAY_MONTH"), env.int("BIRTHDAY_DAY")),
                    time = lambda **kw: format_timestamp(time.time(), config.get("timezone", env.int("TIMEZONE_OFFSET", default=8)), '%Y-%m-%d %H:%M:%S %Z'),
                    age = lambda **kw: calculate_age(env.int("BIRTHDAY_YEAR"), env.int("BIRTHDAY_MONTH"), env.int("BIRTHDAY_DAY"), offset_timezone = config.get("timezone", env.int("TIMEZONE_OFFSET", default=8)))
                )
            )

            context = await context_loader.load(user_id=user_id, New_Message=message, load_prompt=load_prompt)
            
            request = Request()
            request.context = context
    
            apilist = self.apiinfo.find_type(model_type=model_type)
            api = apilist[0]
            
            request.url = api.url
            request.model = api.model_id
            request.key = api.api_key
            logger.info(f"API URL: {api.url}", user_id = user_id)
            logger.info(f"API Model: {api.model_name}", user_id = user_id)
            logger.info(f"Message: \n{request.context.new_content}", user_id = user_id)
            logger.info(f"User Name: {user_name}", user_id = user_id)

            request.user_name = user_name
            request.temperature = config.get("temperature", env.float("DEFAULT_TEMPERATURE", default=0.8))
            request.max_tokens = config.get("max_tokens", env.int("DEFAULT_MAX_TOKENS", default=None))
            request.max_completion_tokens = config.get("max_completion_tokens", env.int("DEFAULT_MAX_COMPLETION_TOKENS", default=None))
            request.stop = config.get("stop", None)
            request.frequency_penalty = config.get("frequency_penalty", env.float("DEFAULT_FREQUENCY_PENALTY", default=0.0))
            request.presence_penalty = config.get("presence_penalty", env.float("DEFAULT_PRESENCE_PENALTY", default=0.0))
            request.print_chunk = print_chunk

            call_prepare_end_time = time.time_ns()

            response = await self.api_client.submit_Request(user_id=user_id, request=request)

            response.calling_log.task_start_time = task_start_time
            response.calling_log.call_prepare_start_time = task_start_time
            response.calling_log.call_prepare_end_time = call_prepare_end_time
            response.calling_log.created_time = response.created
            if save_context:
                await context_loader.save(
                    user_id=user_id,
                    context=response.context
                )

            response.calling_log.task_end_time = time.time_ns()

            await self.calllog.add_call_log(response.calling_log)

            logger.success(f"API call successful", user_id = user_id)
            
            return {
                "reasoning_content": response.context.reasoning_content,
                "content": response.context.new_content
            }
    # endregion

    