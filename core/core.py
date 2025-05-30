# ==== 标准库 ==== #
import asyncio

# ==== 第三方库 ==== #
from environs import Env
from loguru import logger

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
from TimeParser import get_birthday_countdown

# ==== 本模块代码 ==== #
env = Env()

__version__ = '4.0.0.0'

class Core:
    def __init__(self, max_concurrency: int = None):
        self.client = Client(env.int('MAX_CONCURRENCY', 10) if max_concurrency is None else max_concurrency)
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

    async def get_session_lock(self, user_id: str) -> asyncio.Lock:
        async with self.lock:
            if user_id not in self.session_locks:
                self.session_locks[user_id] = asyncio.Lock()
                lock = self.session_locks[user_id]
            else:
                lock = self.session_locks[user_id]
        return lock

    async def Chat(
        self,
        message: str,
        user_id: str,
        user_name: str,
        model_type: str = "",
        load_prompt: bool = True,
        print_chunk: bool = True
    ) -> dict[str, str]:
        lock = await self.get_session_lock(user_id)

        async with lock:
            context_loader = ContextLoader(
                config=self.user_config_manager,
                prompt=self.prompt_manager,
                context=self.context_manager,
                prompt_vp = await self.promptvariable.get_prompt_variable(
                    user_id = user_id,
                    username = user_name,
                    BirthdayCountdown = get_birthday_countdown(
                        env.int("BIRTHDAY_MONTH"),
                        env.int("BIRTHDAY_DAY"),
                        name=env.str(
                            "BOT_NAME",
                            default = ""
                        )
                    ),
                    model_type = model_type,
                    print_chunk = str(print_chunk)
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
            logger.info(f"API URL: {api.url}")
            logger.info(f"API Model: {api.model_name}")

            config = await self.user_config_manager.load(user_id=user_id)
            if not config or not isinstance(config, dict):
                config = {}

            request.temperature = config.get("temperature", 1.0)
            request.max_tokens = config.get("max_tokens", 1024)
            request.stop = config.get("stop", None)
            request.frequency_penalty = config.get("frequency_penalty", 0.0)
            request.presence_penalty = config.get("presence_penalty", 0.0)
            request.print_chunk = print_chunk

            response = await self.api_client.submit_Request(request)

            await context_loader.save(user_id=user_id, context=response.context)

            logger.success(f"{user_id} API call successful")
            
            return {
                "reasoning_content": response.context.reasoning_content,
                "content": response.context.new_content
            }
            