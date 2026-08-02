from __future__ import annotations

# ==== 标准库 ==== #
from pathlib import Path

# ==== 第三方库 ==== #
from loguru import logger
from environs import Env

# ==== 自定义库 ==== #
from ..auxiliary.time import print_init_runtime
from ..data_manager import (
    ContextManager,
    PromptManager
)
from ..user_config_manager import (
    ConfigManager as UserConfigManager
)
from ..pools.resource_pool import ResourcePool
from ..text_buffer import ContentBuffer
from ..auxiliary.regex_checker import RegexChecker
from ..global_config_manager import ConfigManager
from ..clients.model_info import (
    ModelsClient
)
from ..clients.nexus_client import NexusClient
from ..clients.html_render_client import HTMLRenderClient
from ..licenses_loader import LicenseLoader
from ..clients.static_resources_client import StaticResourcesClient
from ..request_log import (
    RequestLogManager
)
from ..status_map import StatusStack
from ..pools.awaitable_pool import TaskPool
from ..pools.openai_pool import OpenAIPool
from ..auxiliary.http import (
    ssl_context,
    RepeaterTransport
)

class RepeaterRuntime:
    _env = Env()

    # 初始化列表
    # 用于保证初始化顺序
    init_list = []

    def __init__(self):
        self._configs = ConfigManager.get_configs()
        for init_func in self.init_list:
            init_func(self)

    @init_list.append
    @print_init_runtime("Repeater Transport Layer")
    def init_transport(self):
        self.transport = RepeaterTransport(
            verify = ssl_context.get_ssl_context()
        )

    @init_list.append
    @print_init_runtime("Data Manager")
    def init_data_manager(self):
        # 初始化用户数据管理器
        self.context_manager = ContextManager()
        self.prompt_manager = PromptManager()
        self.user_config_manager: UserConfigManager = UserConfigManager()

    @init_list.append
    @print_init_runtime("Models Manager")
    def init_models_manager(self):
        # 初始化 Model 管理器
        self.model_info_client = ModelsClient(
            base_url = self._configs.model_api.base_url,
            api_key = self._env.str(
                self._configs.model_api.api_key_env_name
            ),
            timeout = self._configs.model_api.timeout,
            headers = {
                "User-Agent": self._configs.system_identification.system_ua
            },
            transport = self.transport,
        )

    @init_list.append
    @print_init_runtime("Static Resources Client")
    def init_static_resources_client(self):
        # 初始化静态资源客户端
        self.static_resources_client = StaticResourcesClient(
            base_url = self._configs.static_resources_server.base_url,
            timeout = self._configs.static_resources_server.timeout,
            headers = {
                "User-Agent": self._configs.system_identification.system_ua
            },
            transport = self.transport,
        )

    @init_list.append
    @print_init_runtime("Content Buffers Pool")
    def init_content_buffers_pool(self):
        # 初始化内容缓冲池
        self.content_buffers_pools: ResourcePool[str, ResourcePool[str, ContentBuffer]] = ResourcePool()

    @init_list.append
    @print_init_runtime("Call Log Manager")
    def init_call_log_manager(self):
        # 初始化调用日志管理器
        self.request_log = RequestLogManager(
            self._configs.request_log.dir,
            auto_save = self._configs.request_log.auto_save,
        )

    @init_list.append
    @print_init_runtime("Blacklist")
    def init_blacklist(self):
        # 黑名单
        self.blacklist: RegexChecker = RegexChecker()
        blacklist_file_path = Path(self._configs.blacklist.file_path)
        try:
            with open(blacklist_file_path, "r", encoding="utf-8") as f:
                self.blacklist.load_strstream(f)
        except ValueError:
            logger.error("Invalid blacklist file")
        except FileNotFoundError:
            logger.error(
                "Blacklist file not found: {blacklist_file_path}",
                blacklist_file_path = blacklist_file_path
            )
        self.blacklist_match_timeout: int | float | None = self._configs.blacklist.match_timeout

    @init_list.append
    @print_init_runtime("Task Status Map")
    def init_task_status_map(self):
        # Task 状态表
        self.task_status_stacks: ResourcePool[str, ResourcePool[str, StatusStack[str]]] = ResourcePool()

    @init_list.append
    @print_init_runtime("Chat Task Pool")
    def init_chat_task_pool(self):
        # 初始化任务池
        self.chat_task_pool: TaskPool = TaskPool()

    @init_list.append
    @print_init_runtime("Openai Pool")
    def init_openai_pool(self):
        # 初始化客户端池
        config = self._configs
        self.openai_pool: OpenAIPool = OpenAIPool(
            config.callapi.client_cache_size
        )
    
    @init_list.append
    @print_init_runtime("HTML Render Client")
    def init_html_render_client(self):
        render_config = self._configs.render
        self.html_render_client = HTMLRenderClient(
            base_url = render_config.to_image.base_url,
            timeout = render_config.to_image.timeout,
            headers = {
                "User-Agent": self._configs.system_identification.system_ua
            },
            transport = self.transport,
        )
    
    @init_list.append
    @print_init_runtime("Nexus Client")
    def init_nexus_client(self):
        nexus_config = self._configs.nexus
        self.nexus_client: NexusClient = NexusClient(
            base_url = nexus_config.base_url,
            request_timeout = nexus_config.api_timeout,
            headers = {
                "User-Agent": self._configs.system_identification.system_ua
            },
            transport = self.transport,
        )
    
    @init_list.append
    @print_init_runtime("License Loader")
    def init_licenses_data(self):
        self.licenses = LicenseLoader(self._configs.licenses)
        self.licenses.scan_licenses()