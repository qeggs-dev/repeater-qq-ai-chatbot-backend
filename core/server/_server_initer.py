# ==== 标准库 ==== #
from __future__ import annotations
import ssl
import asyncio
from os import PathLike
from typing import Callable, Awaitable, Literal, Any, IO
from configparser import RawConfigParser

# ==== 第三方库 ==== #
from loguru import logger
from fastapi import (
    FastAPI,
    Request,
    Response
)
from uvicorn.config import LOGGING_CONFIG

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
        host: str = "127.0.0.1",
        port: int = 8000,
        uds: str | None = None,
        fd: int | None = None,
        loop: Literal["none", "auto", "asyncio", "uvloop"] | str = "auto",
        http: Literal["auto", "h11", "httptools"] | type[asyncio.Protocol] | str = "auto",
        ws: Literal["auto", "none", "websockets", "websockets-sansio", "wsproto"] | type[asyncio.Protocol] | str = "auto",
        ws_max_size: int = 16 * 1024 * 1024,
        ws_max_queue: int = 32,
        ws_ping_interval: float | None = 20,
        ws_ping_timeout: float | None = 20,
        ws_per_message_deflate: bool = True,
        lifespan: Literal["auto", "on", "off"] = "auto",
        env_file: str | PathLike[str] | None = None,
        log_config: dict[str, Any] | str | RawConfigParser | IO[Any] | None = LOGGING_CONFIG,
        log_level: str | int | None = None,
        access_log: bool = True,
        use_colors: bool | None = None,
        interface: Literal["auto", "asgi3", "asgi2", "wsgi"] = "auto",
        reload: bool = False,
        reload_dirs: list[str] | str | None = None,
        reload_delay: float = 0.25,
        reload_includes: list[str] | str | None = None,
        reload_excludes: list[str] | str | None = None,
        workers: int | None = None,
        proxy_headers: bool = True,
        server_header: bool = True,
        date_header: bool = True,
        forwarded_allow_ips: list[str] | str | None = None,
        root_path: str = "",
        limit_concurrency: int | None = None,
        limit_max_requests: int | None = None,
        backlog: int = 2048,
        timeout_keep_alive: int = 5,
        timeout_notify: int = 30,
        timeout_graceful_shutdown: int | None = None,
        timeout_worker_healthcheck: int = 5,
        callback_notify: Callable[..., Awaitable[None]] | None = None,
        ssl_keyfile: str | PathLike[str] | None = None,
        ssl_certfile: str | PathLike[str] | None = None,
        ssl_keyfile_password: str | None = None,
        ssl_version: int = ssl.PROTOCOL_TLS_SERVER,
        ssl_cert_reqs: int = ssl.CERT_NONE,
        ssl_ca_certs: str | PathLike[str] | None = None,
        ssl_ciphers: str = "TLSv1",
        headers: list[tuple[str, str]] | None = None,
        factory: bool = False,
        h11_max_incomplete_event_size: int | None = None,
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
                uds = uds,
                fd = fd,
                loop = loop,
                http = http,
                ws = ws,
                ws_max_size = ws_max_size,
                ws_max_queue = ws_max_queue,
                ws_ping_interval = ws_ping_interval,
                ws_ping_timeout = ws_ping_timeout,
                ws_per_message_deflate = ws_per_message_deflate,
                lifespan = lifespan,
                env_file = env_file,
                log_config = log_config,
                log_level = log_level,
                access_log = access_log,
                use_colors = use_colors,
                interface = interface,
                reload = reload,
                reload_dirs = reload_dirs,
                reload_delay = reload_delay,
                reload_includes = reload_includes,
                reload_excludes = reload_excludes,
                workers = workers,
                proxy_headers = proxy_headers,
                server_header = server_header,
                date_header = date_header,
                forwarded_allow_ips = forwarded_allow_ips,
                root_path = root_path,
                limit_concurrency = limit_concurrency,
                limit_max_requests = limit_max_requests,
                backlog = backlog,
                timeout_keep_alive = timeout_keep_alive,
                timeout_notify = timeout_notify,
                timeout_graceful_shutdown = timeout_graceful_shutdown,
                timeout_worker_healthcheck = timeout_worker_healthcheck,
                callback_notify = callback_notify,
                ssl_keyfile = ssl_keyfile,
                ssl_certfile = ssl_certfile,
                ssl_keyfile_password = ssl_keyfile_password,
                ssl_version = ssl_version,
                ssl_cert_reqs = ssl_cert_reqs,
                ssl_ca_certs = ssl_ca_certs,
                ssl_ciphers = ssl_ciphers,
                headers = headers,
                factory = factory,
                h11_max_incomplete_event_size = h11_max_incomplete_event_size
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