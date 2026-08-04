# ==== 标准库 ==== #
import uuid
import atexit
import asyncio
import traceback
from pathlib import Path
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Any,
    overload,
    Literal,
)

# ==== 第三方库 ==== #
import orjson
import aiofiles
from loguru import logger

# ==== 自定义库 ==== #
from ..call_api.completions_api import (
    Runtime as RequestRuntime,
    Response as ModelResponse,
    CallAPIException,
    Delta
)
from ..model_requester import (
    ModelRequester,
    MultiResponse
)
from ..context import (
    ContextLoader,
    ContentRole,
    ContentUnit,
)
from ..user_config_manager import (
    UserConfigs
)
from ..pools.lock_pool import AsyncLockPool
from ..text_buffer import ContentBuffer
from ..global_config_manager import (
    ConfigManager,
    GlobalConfigs
)
from ..assist_struct import (
    Response,
    RequestUserInfo,
    CrossUserDataRouting,
    AdditionalData
)
from ..special_exception import HTTPException
from ..request_log import (
    TimeStamp
)
from ..clients.model_info import (
    ModelInfo
)
from ..template_render import (
    TemplateParser
)
from ..runtime_container import RepeaterRuntime
from ._make_request import make_request
from ._make_context import make_context
from ._post_treatment import post_treatment
from ._check_rul import check_rul
from ._task_lifespan import TaskLifespan

class Core:
    # region > init
    def __init__(self, runtime: RepeaterRuntime, max_concurrency: int | None = None):
        # 配置最大并发数
        self._max_concurrency = max_concurrency

        # 全局锁(用于获取会话锁)
        self.lock = asyncio.Lock()

        # 初始化锁池
        self.namespace_locks: AsyncLockPool = AsyncLockPool()

        self.runtime = runtime

        # 添加退出函数
        def _exit():
            """
            退出时执行的任务
            """
            configs = ConfigManager.get_configs()
            # 保存调用日志
            if configs.request_log.auto_save:
                self.runtime.request_log.save_request_log()
            logger.info("Exiting...")
        
        # 注册退出函数
        atexit.register(_exit)
    # endregion

    # region > get namespace lock
    async def _get_namespace_lock(self, user_id: str) -> asyncio.Lock:
        """
        获取指定用户的命名空间锁

        :param user_id: 用户ID
        :return:该命名空间的锁
        """
        
        return await self.namespace_locks.get_lock(user_id)
    # endregion
    
    # region > nickname mapping
    async def nickname_mapping(self, user_id: str, user_info: RequestUserInfo, global_configs: GlobalConfigs) -> RequestUserInfo:
        """
        用户昵称映射

        :param user_id: 用户ID
        :param user_info: 用户信息
        :return: 昵称
        """
        user_nickname_mapping_file_path = Path(global_configs.user_nickname_mapping.file_path)
        if not user_nickname_mapping_file_path.exists():
            return user_info
        async with aiofiles.open(user_nickname_mapping_file_path, "rb") as f:
            fdata = await f.read()
            try:
                nickname_mapping = orjson.loads(fdata)
            except orjson.JSONDecodeError:
                logger.warning(
                    "Failed to decode nickname mapping file [{user_nickname_mapping_file_path}]",
                    user_id = user_id,
                    user_nickname_mapping_file_path = user_nickname_mapping_file_path
                )
                nickname_mapping = {}
        
        output = user_info
        if user_info.nickname in nickname_mapping:
            logger.info("User Name [{user_name}] -> [{to_nickname}]", user_id=user_id, user_name = user_info.nickname, to_nickname = nickname_mapping[user_info.nickname])
            output.nickname = nickname_mapping[user_info.nickname]
        elif user_info.username in nickname_mapping:
            logger.info("User Name [{user_name}] -> [{to_nickname}]", user_id=user_id, user_name = user_info.username, to_nickname = nickname_mapping[user_info.username])
            output.username  = nickname_mapping[user_info.username]
        elif user_id in nickname_mapping:
            logger.info("User Name [{user_id}](ID) -> [{to_nickname}]", user_id=user_id, to_nickname = nickname_mapping[user_id])
            output.username = nickname_mapping[user_id]
        
        return output
    # endregion

    # region > get config
    async def get_config(self, user_id: str) -> UserConfigs:
        """
        加载用户配置

        :param user_id: 用户ID
        :return: 用户配置
        """
        config: UserConfigs = await self.runtime.user_config_manager.load(user_id = user_id)
        return config
    # endregion

    # region > get context
    def get_context_loader(self) -> ContextLoader:
        """
        加载上下文
        :return: 上下文加载器
        """
        context_loader = ContextLoader(
            config=self.runtime.user_config_manager,
            prompt=self.runtime.prompt_manager,
            context=self.runtime.context_manager,
        )
        return context_loader
    # endregion

    # region > load blacklist
    async def load_blacklist(self, global_configs: GlobalConfigs, path: str | Path | None = None) -> None:
        """
        加载黑名单

        :param path: 黑名单文件路径
        """
        if not path:
            blacklist_file_path = Path(global_configs.blacklist.file_path)
        else:
            blacklist_file_path = Path(path)
        
        if blacklist_file_path.exists():
            self.runtime.blacklist.clear()
            async with aiofiles.open(blacklist_file_path, "r") as f:
                try:
                    self.runtime.blacklist.load(await f.read())
                except ValueError as e:
                    logger.warning(
                        "load blacklist failed: {error}",
                        error = str(e),
                    )
    # endregion

    # region > in blacklist
    async def in_blacklist(self, user_id: str) -> bool:
        """
        判断用户是否在黑名单中

        :param user_id: 用户ID
        :return: 是否在黑名单中
        """
        async def _match_blacklist(user_id: str, timeout: int | float | None) -> bool:
            if timeout is not None:
                return bool(await asyncio.wait_for(asyncio.to_thread(self.runtime.blacklist.check, user_id), timeout = timeout))
            else:
                return bool(await asyncio.to_thread(self.runtime.blacklist.check, user_id))
        
        try:
            if await _match_blacklist(user_id, self.runtime.blacklist_match_timeout):
                logger.info("User in blacklist", user_id = user_id)
                return True
        except asyncio.exceptions.TimeoutError:
            logger.warning("Blacklist match timeout", user_id = user_id)
            return False
        return False
    # endregion

    # region > get_template_parser
    async def get_template_parser(
        self,
        user_config: UserConfigs,
        global_config: GlobalConfigs,
        model: ModelInfo | None = None,
        user_info: RequestUserInfo | None = None,
    ) -> TemplateParser:
        if model is None:
            model_id = user_config.model_id
            if model_id is None:
                model_id = global_config.model_api.default_model_id
            model = await self.runtime.model_info_client.get_random_model(
                model_id = model_id,
            )
        
        template_parser = TemplateParser(
            model = model,
            user_info = user_info,
            global_config = global_config,
            user_config = user_config
        )
        return template_parser
    # endregion
    
    # region > fill missing cross user data routing
    async def fill_missing_cross_user_data_routing(self, user_id: str, cross_user_data_routing: CrossUserDataRouting[str | None] | None = None) -> CrossUserDataRouting[str]:
        if cross_user_data_routing is None:
            cross_user_data_routing = CrossUserDataRouting()
        if not cross_user_data_routing.is_all_defined():
            cross_user_data_routing.fill_missing(user_id = user_id)
        parsed_cross_user_data_routing = await cross_user_data_routing.removal_not_allowed_user(
            user_id = user_id,
            user_config_manager = self.runtime.user_config_manager
        )
        return parsed_cross_user_data_routing
    # endregion

    # region > Chat
    async def chat(
            self,
            message: str | None,
            user_id: str,
            task_id: str | uuid.UUID | None = None,
            suffix: str | None = None,
            echo: bool | None = None,
            fim_mode: bool = False,
            history_messages: list[ContentUnit] | None = None,
            history_msg_role_map: dict[ContentRole, ContentRole | None] | None = None,
            user_info: RequestUserInfo = RequestUserInfo(),
            role: ContentRole = ContentRole.USER,
            assistant_role: ContentRole = ContentRole.ASSISTANT,
            role_name:  str | None = "",
            extra_template_fields: dict[str, Any] | None = None,
            temporary_prompt: str | None = None,
            additional_data: AdditionalData | None = None,
            model_id: str | list[str] | None = None,
            thinking: bool | None = None,
            load_prompt: bool | None = None,
            save_context: bool | None = None,
            save_new_only: bool | None = None,
            cross_user_data_routing: CrossUserDataRouting[str | None] | None = None,
            allowed_tool_calls: set[str] | None = None,
            stream: bool = False,
            extra_bodys: dict[str, Any] | None = None,
        ) -> Response | AsyncGenerator[Delta | ContentUnit, None]:
        """
        与模型对话

        :param message: 用户输入的消息
        :param user_id: 用户ID
        :param task_id: 任务ID
        :param history_messages: 历史消息
        :param history_msg_role_map: 历史消息角色映射
        :param user_info: 用户信息
        :param role: 角色
        :param role_name: 角色名
        :param extra_template_fields: 模板字段扩展
        :param temporary_prompt: 临时提示词
        :param additional_data: 额外数据
        :param model_id: 模型 ID
        :param thinking: 使用思考模式
        :param load_prompt: 是否加载提示
        :param save_context: 是否保存上下文
        :param save_new_only: 是否只保存最新的内容
        :param cross_user_data_operations: 跨用户数据流
        :param allow_tool_calls: 是否允许工具调用
        :param stream: 是否流式输出
        :param extra_bodys: 额外请求参数
        :return: 返回对话结果
        """
        try:
            # 记录开始时间
            task_start_time = TimeStamp()

            if task_id is None:
                task_id = uuid.uuid4()

            logger.info("====================================", user_id = user_id)
            logger.info(
                "Start Task {task_id}",
                user_id = user_id,
                task_id = task_id,
            )

            # 获取用户锁对象
            lock = await self._get_namespace_lock(user_id)

            # region [Getting Config]
            global_configs = ConfigManager.get_configs()
            configs = await self.get_config(user_id)
            # endregion

            enable_rul = check_rul(
                fim_mode = fim_mode,
                configs = configs,
                global_configs = global_configs,
                save_context = save_context
            )

            # 进入RUL执行
            async with TaskLifespan(
                user_id = user_id,
                task_id = task_id,
                rul = lock,
                enable_rul = enable_rul,
                runtime = self.runtime
            ) as task_lifespan:
                task_status_stack = task_lifespan.task_status_stack

                # 进入状态
                with task_status_stack.enter("Tasking"):
                    logger.info(
                        "Enter Task {task_id}",
                        user_id = user_id,
                        task_id = task_lifespan.task_id_str
                    )
                
                    with task_status_stack.enter("Prepareing"):
                        prepare_start_time = TimeStamp()

                        # region [Checking Blacklist]
                        with task_status_stack.enter("Checking Blacklist"):
                            # 判断用户是否在黑名单中
                            if await self.in_blacklist(user_id):
                                raise HTTPException(
                                    status_code = 403,
                                    detail = "Error: Sorry, you are in blacklist.",
                                )
                            
                            if not global_configs.model.stream and stream:
                                raise HTTPException(
                                    status_code = 403,
                                    detail = "Error: The streaming response feature is turned off in the server configuration.",
                                )
                        # endregion

                        # region [Pre-Processing Arguments]
                        with task_status_stack.enter("Pre-Processing Arguments"):
                            extra_template_fields = extra_template_fields or {}
                        # endregion
                        
                        # region [Processing Cross User Data Access]
                        with task_status_stack.enter("Processing Cross User Data Access"):
                            if not configs.cross_user_data_access:
                                logger.warning("Cross user data routing is not allowed.", user_id = user_id)
                                cross_user_data_routing = None
                            elif not global_configs.user_data.cross_user_data_access:
                                logger.warning("Cross user data routing is not allowed.", user_id = user_id)
                                cross_user_data_routing = None
                        
                            parsed_cross_user_data_routing = await self.fill_missing_cross_user_data_routing(user_id, cross_user_data_routing)

                            if user_id != parsed_cross_user_data_routing.config.load_from_user_id:
                                configs = await self.get_config(parsed_cross_user_data_routing.config.load_from_user_id)
                        # endregion
                        
                        # region [Getting model]
                        with task_status_stack.enter("Getting model"):
                            # 获取默认模型uid
                            if not model_id:
                                model_id = configs.model_id
                                if not model_id:
                                    model_id = global_configs.model_api.default_model_id
                            model = await self.runtime.model_info_client.get_random_model(
                                model_id = model_id
                            )
                        # endregion

                        # region [Getting model info]
                        with task_status_stack.enter("Mapping user name"):
                            # 进行用户名映射
                            user_info = await self.nickname_mapping(
                                user_id = user_id,
                                user_info = user_info,
                                global_configs = global_configs
                            )
                        # endregion

                        # region [Getting template parser]
                        with task_status_stack.enter("Getting template parser"):
                            # 获取变量展开器以展开变量内容
                            template_parser = await self.get_template_parser(
                                user_config = configs,
                                global_config = global_configs,
                                model = model,
                                user_info = user_info,
                            )
                        # endregion

                        # region [Processing context]
                        with task_status_stack.enter("Processing context"):
                            context_loader = self.get_context_loader()
                            submit_context, user_input = await make_context(
                                user_id = user_id,
                                message = message,
                                configs = configs,
                                context_loader = context_loader,
                                template_parser = template_parser,
                                static_resources_client = self.runtime.static_resources_client,
                                history_messages = history_messages if not fim_mode else [],
                                history_msg_role_map = history_msg_role_map,
                                role = role,
                                role_name = role_name,
                                extra_template_fields = extra_template_fields,
                                temporary_prompt = temporary_prompt,
                                additional_data = additional_data,
                                load_prompt = load_prompt,
                                cross_user_data_routing = parsed_cross_user_data_routing,
                                task_status_stack = task_status_stack
                            )
                            if suffix:
                                suffix = await template_parser.render_ex(
                                    suffix,
                                    user_id,
                                    **extra_template_fields
                                )
                        # endregion
                        
                        # region [Make Request Object]
                        with task_status_stack.enter("Make Request Object"):
                            request = await asyncio.to_thread(
                                make_request,
                                user_id = user_id,
                                user_input = user_input,
                                suffix = suffix,
                                echo = echo,
                                fim_mode = fim_mode,
                                user_info = user_info,
                                submit_context = submit_context,
                                model_id = model_id,
                                model = model,
                                configs = configs,
                                global_configs = global_configs,
                                assistant_role = assistant_role,
                                role_name = role_name,
                                thinking = thinking,
                                extra_bodys = extra_bodys
                            )

                            if configs.max_generate_times:
                                max_generate_times = configs.max_generate_times
                            else:
                                max_generate_times = global_configs.callapi.max_generate_times
                            
                            if global_configs.tool_calls.enabled:
                                tool_calls_configs = global_configs.tool_calls
                                server_registed_tools = tool_calls_configs.registed
                                if allowed_tool_calls:
                                    user_registed_tools = allowed_tool_calls
                                elif configs.allowed_tool_calls:
                                    user_registed_tools = configs.allowed_tool_calls
                                elif tool_calls_configs.allowed_by_default:
                                    user_registed_tools = tool_calls_configs.allowed_by_default
                                else:
                                    user_registed_tools = set()

                                available_tool_calls = server_registed_tools.intersection(user_registed_tools)
                            else:
                                available_tool_calls = set()
                            
                            # 创建内容缓冲区
                            content_buffer = task_lifespan.task_content_buffer
                        # endregion
                        
                        # region [Make Request Object]
                        with task_status_stack.enter("Make Request Runtime Object"):
                            request_runtime = RequestRuntime(
                                client_pool = self.runtime.openai_pool,
                                status_stack = task_status_stack,
                                content_buffer = content_buffer
                            )
                        # endregion

                        # region [Pre-filled output]
                        with task_status_stack.enter("Pre-filled output"):
                            # 输出 (为了自动填充输出内容)
                            output = Response()
                            output.model_group = model.parent
                            output.model_name = model.name
                            output.model_uid = model.uid
                            output.user_raw_input = message

                            if user_input is not None:
                                output.user_input = user_input.content

                            # 是否保存上下文
                            if save_context is None:
                                if configs.save_context is not None:
                                    save_context = configs.save_context
                                else:
                                    save_context = global_configs.context.save_context
                            
                            # 是否在保存时删除多模态内容
                            if configs.save_text_only is not None:
                                save_only_text: bool = configs.save_text_only
                            else:
                                save_only_text: bool = global_configs.context.save_text_only
                            
                            if save_new_only is None:
                                if configs.save_new_only is not None:
                                    save_new_only = configs.save_new_only
                                else:
                                    save_new_only = global_configs.context.save_new_only
                            
                            enable_assistant_template = global_configs.text_template.enable.assistant_template

                            request_statistics_template = configs.request_statistics_template
                            if request_statistics_template is None:
                                request_statistics_template = global_configs.text_template.request_statistics_template
                        # endregion

                        # region [Pre-filled Model Response]
                        with task_status_stack.enter("Pre-filled Model Response"):
                            model_response = ModelResponse(
                                user_id = user_id,
                                stream = request.stream
                            )
                            model_response.request_log.user_id = user_id
                            model_response.request_log.task_id = task_lifespan.get_task_id_str()
                            model_response.request_log.task_start_time = task_start_time
                            model_response.request_log.prepare_start_time = prepare_start_time
                    
                    # 记录预处理结束时间
                    prepare_end_time = TimeStamp()

                    model_response.request_log.prepare_end_time = prepare_end_time
                    request_runtime.response = model_response

                    # region [Requesting]
                    with task_status_stack.enter("Requesting"):
                        # 初始化 Client 并设置并发大小
                        model_caller = ModelRequester(
                            user_id = user_id,
                            user_configs = configs,
                            global_configs = global_configs,
                            model_info_client = self.runtime.model_info_client,
                            max_concurrency = (
                                global_configs.callapi.max_concurrency
                                if self._max_concurrency is None else self._max_concurrency
                            ),
                            context_loader = context_loader,
                            static_resources_client = self.runtime.static_resources_client
                        )
                        try:
                            model_responses: MultiResponse | None = None
                            
                            async def submit():
                                nonlocal output, model_responses
                                model_responses = await model_caller.submit(
                                    user_id = user_id,
                                    request = request,
                                    runtime = request_runtime,
                                    max_generated_times = max_generate_times,
                                    available_tool_calls = available_tool_calls,
                                    stream = stream
                                )
                                
                                output = await post_treatment(
                                    user_id = user_id,
                                    output = output,
                                    responses = model_responses,
                                    template_parser = template_parser,
                                    user_input = user_input,
                                    save_context = save_context if not fim_mode else False,
                                    save_new_only = save_new_only,
                                    context_loader = context_loader,
                                    task_status_stack = task_status_stack,
                                    request_log_manager = self.runtime.request_log,
                                    cross_user_data_routing = parsed_cross_user_data_routing,
                                    enable_assistant_template = enable_assistant_template,
                                    request_statistics_template = request_statistics_template,
                                    save_only_text = save_only_text,
                                )
                            
                            task = asyncio.create_task(submit())

                            if stream:
                                return model_caller.generator()
                            else:
                                await task
                                return output
                        except CallAPIException as e:
                            traceback_info = traceback.format_exc()
                            logger.exception(
                                "CallAPI Error: \n{traceback_info}",
                                user_id = user_id,
                                traceback_info = traceback_info,
                            )
                            
                            raise HTTPException(
                                status_code = 500,
                                detail = f"API Error: {e}"
                            )
                    # endregion
        except Exception as e:
            traceback_info = traceback.format_exc()
            logger.error("API call failed: \n{traceback}", user_id = user_id, traceback = traceback_info)
            raise
    # endregion