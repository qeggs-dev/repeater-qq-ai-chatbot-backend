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
from loguru import logger
import aiofiles
import orjson

# ==== 自定义库 ==== #
from . import CallAPI
from . import Context
from . import DataManager
from . import UserConfigManager
from .ApiInfo import (
    ApiInfo,
    ApiGroup
)
from . import CallLog
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
from ConfigManager import ConfigLoader

# ==== 本模块代码 ==== #
configs = ConfigLoader()

__version__ = configs.get_config("VERSION", "4.1.0.0").get_value(str)

class Core:
    def __init__(self, max_concurrency: int | None = None):

        # 移除默认处理器
        logger.remove()
        logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[user_id]}</cyan> - <level>{message}</level>")

        # 全局锁(用于获取会话锁)
        self.lock = asyncio.Lock()

        # 初始化用户数据管理器
        self.context_manager = DataManager.ContextManager()
        self.prompt_manager = DataManager.PromptManager()
        self.user_config_manager = UserConfigManager.ConfigManager()

        # 初始化变量加载器
        self.promptvariable = Context.LoadPromptVariable(
            version = __version__
        )
        # 初始化Client并设置并发大小
        self.api_client = CallAPI.Client(configs.get_config('max_concurrency', 10).get_value(int) if max_concurrency is None else max_concurrency)

        # 初始化API信息管理器
        self.apiinfo = ApiInfo()
        # 从指定文件加载API信息
        self.apiinfo.load(configs.get_config("api_info_file_path", "./config/api_info.json").get_value(Path))

        # 初始化会话锁池
        self.session_locks = {}

        # 初始化调用日志管理器
        self.calllog = CallLog.CallLogManager(configs.get_config('Call_Log_File_Path').get_value(Path))

        
        # 添加退出函数
        def _exit():
            """
            退出时执行的任务
            """
            # 保存调用日志
            if configs.get_config("save_call_log", True).get_value(bool):
                self.calllog.save_call_log()
        
        # 注册退出函数
        atexit.register(_exit)

    async def _get_session_lock(self, user_id: str) -> asyncio.Lock:
        """
        获取指定用户的会话锁

        :param user_id: 用户ID
        :return: 会话锁
        """
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
            config: UserConfigManager.Configs = UserConfigManager.Configs(),
        ) -> PromptVP:
        """
        获取指定用户的PromptVP实例

        :param user_id: 用户ID
        :param user_name: 用户名
        :param model_type: 模型类型
        :param config: 用户配置
        :return: PromptVP实例
        """
        bot_birthday_year = configs.get_config("birthday_year").get_value(int)
        bot_birthday_month = configs.get_config("birthday_month").get_value(int)
        bot_birthday_day = configs.get_config("birthday_day").get_value(int)
        timezone = configs.get_config("timezone", 8).get_value(int)
        bot_name = configs.get_config("bot_name", "Bot").get_value(str)
        return await self.promptvariable.get_prompt_variable(
            user_id = user_id,
            user_name = user_name,
            BirthdayCountdown = lambda **kw: get_birthday_countdown(
                bot_birthday_month,
                bot_birthday_day,
                name=bot_name
            ),
            model_type = model_type if model_type else config.get("model_type"),
            botname = bot_name,
            birthday = f'{bot_birthday_year}.{bot_birthday_month}.{bot_birthday_day}',
            zodiac = lambda **kw: date_to_zodiac(bot_birthday_month, bot_birthday_day),
            time = lambda **kw: format_timestamp(time.time(), config.get("timezone", timezone), '%Y-%m-%d %H:%M:%S %Z'),
            age = lambda **kw: calculate_age(bot_birthday_year, bot_birthday_month, bot_birthday_day, offset_timezone = config.get("timezone", timezone)),
            random = lambda min, max: random.randint(int(min), int(max)),
            randfloat = lambda min, max: random.uniform(float(min), float(max)),
            randchoice = lambda *args: random.choice(args)
        )
    # endregion
    
    # region > load nickname mapping
    async def load_nickname_mapping(self, user_id: str, user_name: str) -> str:
        """
        加载用户昵称映射
        :param user_id: 用户ID
        :param user_name: 用户名
        :return: 昵称
        """
        user_nickname_mapping_file_path = configs.get_config("user_nickname_mapping_file_path", "./config/user_nickname_mapping.json").get_value(Path)
        unm_path = user_nickname_mapping_file_path
        if not unm_path.exists():
            return user_name
        async with aiofiles.open(user_nickname_mapping_file_path, 'rb') as f:
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

    # region > get config
    async def get_config(self, user_id: str) -> UserConfigManager.Configs:
        """
        加载用户配置
        :param user_id: 用户ID
        :param default: 默认配置
        :return: 用户配置
        """
        config = await self.user_config_manager.load(user_id=user_id)
        return config
    # endregion

    # region > get context
    async def get_context_loader(
            self,
            user_id: str,
            user_name: str,
            model_type: str = configs.get_config("default_model_type", "chat").get_value(str),
            user_config: dict = {},
        ) -> Context.ContextLoader:
        """
        加载上下文
        :param user_id: 用户ID
        :param user_name: 用户名
        :param model_type: 模型类型
        :param user_config: 用户配置
        :return: 上下文加载器
        """
        context_loader = Context.ContextLoader(
            config=self.user_config_manager,
            prompt=self.prompt_manager,
            context=self.context_manager,
            prompt_vp = await self.get_prompt_vp(
                user_id = user_id,
                user_name = user_name,
                model_type = model_type,
                config = user_config
            )
        )
        return context_loader
    
    async def get_context(
            self,
            context_loader: Context.ContextLoader,
            user_id: str,
            message: str,
            user_name: str,
            role: str = 'user',
            role_name: str | None = None,
            load_prompt: bool = True,
            continue_completion: bool = False,
            reference_context_id: str | None = None
        ) -> Context.ContextObject:
        """
        获取上下文
        :param context_loader: 上下文加载器
        :param user_id: 用户ID
        :param message: 消息
        :param user_name: 用户名
        :param role: 角色
        :param role_name: 角色名
        :param load_prompt: 是否加载提示
        :param continue_completion: 是否继续完成
        :param reference_context_id: 引用上下文ID
        :return: 上下文对象
        """
        if reference_context_id:
            context = await context_loader.load(
                user_id = reference_context_id,
                message = message,
                role = role,
                role_name = role_name if role_name else user_name,
                load_prompt = load_prompt,
                continue_completion = continue_completion
            )
        else:
            context = await context_loader.load(
                user_id = user_id,
                message = message,
                role = role,
                role_name = role_name,
                load_prompt = load_prompt,
                continue_completion = continue_completion
            )
        return context
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
        """
        与模型对话

        :param message: 用户输入的消息
        :param user_id: 用户ID
        :param user_name: 用户名
        :param role: 角色
        :param role_name: 角色名
        :param model_type: 模型类型
        :param load_prompt: 是否加载提示
        :param print_chunk: 是否打印片段
        :param save_context: 是否保存上下文
        :param reference_context_id: 引用上下文ID
        :param continue_completion: 是否继续完成
        :return: 返回对话结果
        """
        # 记录开始时间
        task_start_time = time.time_ns()

        # 获取用户锁对象
        lock = await self._get_session_lock(user_id)
        
        # 加锁执行
        async with lock:
            logger.info("====================================", user_id = user_id)
            logger.info("Start Task", user_id = user_id)

            # 进行用户名映射
            user_name = await self.load_nickname_mapping(user_id, user_name)

            # 获取配置
            config = await self.get_config(user_id)
            
            # 获取模型类型
            if not model_type:
                model_type = config.get("model_type", configs.get_config("default_model_type", "chat").get_value(str))

            # 获取上下文加载器
            context_loader = await self.get_context_loader(
                user_id = user_id,
                user_name = user_name,
                model_type = model_type,
                user_config = config
            )

            # 获取上下文
            context = await self.get_context(
                context_loader = context_loader,
                user_id = user_id,
                message = message,
                user_name = user_name,
                role = role,
                role_name = role_name,
                load_prompt = load_prompt,
                continue_completion = continue_completion,
                reference_context_id = reference_context_id
            )
            
            # 创建请求对象
            request = CallAPI.Request()
            # 设置上下文
            request.context = context

            # 获取API信息
            apilist = self.apiinfo.find_type(model_type = model_type)
            # 取第一个API
            api = apilist[0]
            
            # 设置请求对象的API信息
            request.url = api.url
            request.model = api.model_id
            request.key = api.api_key
            logger.info(f"API URL: {api.url}", user_id = user_id)
            logger.info(f"API Model: {api.model_name}", user_id = user_id)

            # 打印上下文信息
            if request.context.last_content.content:
                logger.info(f"Message:{request.context.last_content.content}", user_id = user_id)
            else:
                logger.warning("No message to send", user_id = user_id)
            logger.info(f"User Name: {user_name}", user_id = user_id)

            # 如果有设置角色名称信息，则打印日志
            if role_name:
                logger.info(f"Role Name: {role_name}", user_id = user_id)

            # 设置请求对象的参数信息
            request.user_name = user_name
            request.temperature = config.get("temperature", configs.get_config("default_temperature", 1.0).get_value(float))
            request.top_p = config.get("top_p", configs.get_config("default_top_p", 1.0).get_value(float))
            request.max_tokens = config.get("max_tokens", configs.get_config("default_max_tokens", 4096).get_value(int))
            request.max_completion_tokens = config.get("max_completion_tokens", configs.get_config("default_max_completion_tokens", 4096).get_value(int))
            request.stop = config.get("stop", configs.get_config("default_stop", None).get_value((list, None)))
            request.stream = configs.get_config("stream", True).get_value(bool)
            request.frequency_penalty = config.get("frequency_penalty", configs.get_config("default_frequency_penalty", 0.0).get_value(float))
            request.presence_penalty = config.get("presence_penalty", configs.get_config("default_presence_penalty", 0.0).get_value(float))
            request.print_chunk = print_chunk

            # 记录预处理结束时间
            call_prepare_end_time = time.time_ns()

            # 输出
            output =  {
                "reasoning_content": "",
                "content": "",
                "model_name": api.model_name,
                "model_type": api.model_type,
                "model_id": api.model_id,
            }

            # 提交请求
            try:
                response = await self.api_client.submit_Request(user_id=user_id, request=request)
            except CallAPI.Exceptions.CallApiException as e:
                output["content"] = f"Error:{e}"
                return output

            # 补充调用日志的时间信息
            response.calling_log.task_start_time = task_start_time
            response.calling_log.call_prepare_start_time = task_start_time
            response.calling_log.call_prepare_end_time = call_prepare_end_time
            response.calling_log.created_time = response.created

            # 获取Prompt_vp以展开模型输出内容
            prompt_vp = await self.get_prompt_vp(
                user_id = user_id,
                user_name = user_name,
                model_type = model_type,
                config = config
            )
            # 处理模型输出内容
            response.context.last_content.content = prompt_vp.process(response.context.last_content.content)
            # 记录Prompt_vp的命中情况
            logger.info(f"Prompt Hits Variable: {prompt_vp.hit_var()}/{prompt_vp.discover_var()}({prompt_vp.hit_var() / prompt_vp.discover_var() if prompt_vp.discover_var() != 0 else 0:.2%})", user_id = user_id)

            # 保存上下文
            if save_context:
                await context_loader.save(
                    user_id = user_id,
                    context = response.context
                )
            else:
                logger.warning("Context not saved", user_id = user_id)

            # 记录任务结束时间
            response.calling_log.task_end_time = time.time_ns()

            # 记录调用日志
            await self.calllog.add_call_log(response.calling_log)

            # 记录API调用成功
            logger.success(f"API call successful", user_id = user_id)

            # 返回模型输出内容
            
            output["reasoning_content"] = response.context.last_content.reasoning_content
            output["content"] = response.context.last_content.content
            return output
    # endregion

    # region > 重新加载API信息
    async def reload_apiinfo(self):
        await self.apiinfo.load_async(configs.get_config("api_info_file_path", "./config/api_info.json").get_value(Path))
    # endregion

    # region > 加载指定API INFO文件
    async def load_apiinfo(self, api_info_file_path: Path):
        if not api_info_file_path.exists():
            raise FileNotFoundError(f"File not found: {api_info_file_path}")
        await self.apiinfo.load_async(api_info_file_path)
    # endregion