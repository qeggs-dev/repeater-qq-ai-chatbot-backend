# ==== 标准库 ==== #
from __future__ import annotations
from typing import Callable, Awaitable

# ==== 第三方库 ==== #
from loguru import logger
from fastapi import (
    FastAPI,
    Request,
    Response
)

# ==== 自定义库 ==== #
from ..auxiliary.time import print_init_runtime
from ..global_config_manager import ConfigManager
from ._server import Server

class ServerIniter:
    init_list: list[Callable[..., None]] = []

    def __init__(
        self,
        server: Server,
    ) -> None:
        self.server = server

    def inited(self):
        return self.server.inited()

    def init_all(self):
        for init_func in ServerIniter.init_list:
            init_func(self)
    
    def init_middleware(self):
        self.middleware_factory()
    
    def init_logger(self):
        from ..logger_init import logger_init
        # 初始化日志
        logger_init(
            ConfigManager.get_configs().logger,
        )
        logger.info("Logger has been initialized.")
        Server._logger_inited = True
    
    @init_list.append
    @print_init_runtime("Runtime")
    def init_runtime(self):
        """
        Init runtime instance.
        """
        from ..runtime_container import RuntimeContainer
        self.server.runtime = RuntimeContainer.init_runtime()
    
    @init_list.append
    @print_init_runtime("Core")
    def init_core(self):
        """
        Init core instance.
        """
        from ..core.chat import Core
        self.server.core = Core(
            runtime = self.server.runtime
        )
    
    @init_list.append
    @print_init_runtime("Routers")
    def init_routers(self):
        """
        Init api routers.
        """
        from ..api import root_router
        self.server.app.include_router(
            root_router
        )
    
    @init_list.append
    @print_init_runtime("Admin Key Manager")
    def init_admin_key_manager(self):
        """
        Init admin key manager.
        """
        from ..admin_api_key_manager import AdminKeyManager
        self.server.admin_key_manager = AdminKeyManager()
    
    @print_init_runtime("Server")
    def init_server(
        self,
        host: str,
        port: int,
        workers: int = 1,
        reload: bool = False
    ):
        """
        Init server.
        """
        from uvicorn import Server, Config
        # 初始化API
        self.server.server = Server(
            Config(
                app = self.server.app,
                host = host,
                port = port,
                workers = workers,
                reload = reload,
                log_config = None
            )
        )
    
    def set_inited_flag(self):
        """
        Set the inited flag of the server initer.

        Important! The program needs to set this Flag to start.
        """
        self.server._inited = True
    
    def middleware_factory(self):
        """
        Make a http middleware.

        :return: A http middleware.
        """
        from ..repeater_traceback import log_traceback
        @self.server.app.middleware("http")
        async def http_middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]):
            """
            Http middleware.

            :param request: Request
            :param call_next: Callable[[Request], Awaitable[Response]]
            :return: Response
            """
            try:
                return await call_next(request)
            except Exception as e:
                return await log_traceback(e, self.server)
            except BaseException as e:
                if ConfigManager().get_configs().global_exception_handler.record_all_exceptions:
                    await log_traceback(e, self.server)
                raise
        return http_middleware