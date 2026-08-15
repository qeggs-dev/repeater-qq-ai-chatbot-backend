import sys
import time
import asyncio

from typing import (
    ClassVar
)
from environs import Env
from ..global_config_manager import (
    ConfigManager,
    GlobalConfigs,       
)
from ..server import (
    Server,
    ServerIniter,
)
from pathlib import Path
from .._info import __version__
from ..requirements_version_checker import check_package_list
from loguru import logger
from .config_force_load_list import is_config_force_load_list

class RepeaterMain:
    env = Env()
    env.read_env()
    _now_server: ClassVar[Server | None] = None

    def __init__(self):
        self.server = Server()
        self.server_initer = ServerIniter(self.server)

    @classmethod
    def get_now_server(cls) -> Server:
        """
        Get the current server instance
        """
        if cls._now_server is None:
            raise RuntimeError("Server not inited")
        return cls._now_server

    def load_configs(self) -> GlobalConfigs:
        """
        Load configs from file

        Tip: The program needs a configuration file to boot, please load the configuration file first.
        """
        path = self.env.path("CONFIG_DIR", Path("./configs/project_configs"))
        force_load_list = self.env.json("CONFIG_FORCE_LOAD_LIST", None)
        if force_load_list is not None and not is_config_force_load_list(force_load_list):
            raise RuntimeError("CONFIG_FORCE_LOAD_LIST is not valid")
        ConfigManager.update_base_path(
            path = path,
            force_load_list = force_load_list
        )
        return ConfigManager.load(
            create_if_missing=True
        )
    
    def init_server(self, configs: GlobalConfigs) -> None:
        """
        Init the server

        :param configs: GlobalConfigs
        """
        host = "0.0.0.0" # 默认监听所有地址
        port = 8000 # 默认监听8000端口

        env_config_host = self.env.str("HOST", host)
        env_config_port = self.env.int("PORT", port)
        env_config_workers = self.env.int("WORKERS", None)
        env_config_reload = self.env.bool("RELOAD", False)

        host: str | None = configs.server.uvicorn.host
        if host is None:
            host = env_config_host
        
        port: int | None = configs.server.uvicorn.port
        if port is None:
            port = env_config_port
        
        workers: int | None = configs.server.uvicorn.workers
        if workers is None:
            workers = env_config_workers
        
        reload: bool | None = configs.server.uvicorn.reload
        if reload is None:
            reload = env_config_reload

        logger.info(
            "Starting server at {host}:{port}",
            host = host,
            port = port
        )

        if workers:
            logger.info(
                "Server will run with {workers} workers",
                workers = workers
            )
        
        if reload:
            logger.info("Server will reload on code change")

        data = configs.server.uvicorn.model_dump()

        data["host"] = host
        data["port"] = port
        data["workers"] = workers
        data["reload"] = reload
        
        self.server_initer.init_server(
            **data
        )

        self.server_initer.init_middleware()
    
    def check_package(self, configs: GlobalConfigs) -> None:
        """
        Check that the package meets the requirements
        
        **Warning: it will be discarded**

        :param configs: GlobalConfigs
        """
        logger.info("Checking Packages...")
        start_check_packages_time = time.perf_counter_ns()
        check_package_list(
            strict_mode = configs.requirements.strict_mode
        )
        end_check_packages_time = time.perf_counter_ns()
        logger.info(
            "Check Packages Time: {check_packages_time:.2f}ms",
            check_packages_time = (end_check_packages_time - start_check_packages_time) / 1e6
        )
    
    def init_logger(self):
        self.server_initer.init_logger()
    
    def init_all(self, configs: GlobalConfigs) -> None:
        """
        One-click handles most initialization.

        :param configs: GlobalConfigs
        """
        logger.info(
            "Run With Python {major}.{minor}.{micro}",
            major = sys.version_info.major,
            minor = sys.version_info.minor,
            micro = sys.version_info.micro
        )
        logger.info(
            "Repeater Version: {version}",
            version = __version__
        )

        if configs.requirements.enable_check:
            self.check_package(configs)

        start_init_resource_time = time.perf_counter_ns()
        self.server_initer.init_all()
        end_init_resource_time = time.perf_counter_ns()

        logger.info(
            "Init Server Time: {init_resource_time:.2f}ms",
            init_resource_time = (end_init_resource_time - start_init_resource_time) / 1e6
        )
    
    def set_inited_flag(self) -> None:
        """
        Set the inited flag of the server initer.

        Important! The program needs to set this Flag to start.
        """
        self.server_initer.set_inited_flag()
    
    async def run_server(self) -> int:
        """
        Run the server in async mode.
        """
        RepeaterMain._now_server = self.server
        try:
            return await self.server.run_server()
        finally:
            RepeaterMain._now_server = None

    def run(self, debug: bool | None = None) -> int:
        """
        Run the server.
        """
        logger.info("Server starting...")
        configs = ConfigManager.get_configs()
        asyncio_debug = debug
        if asyncio_debug is None:
            asyncio_debug = configs.server.asyncio_debug
        
        try:
            return asyncio.run(
                self.run_server(),
                debug = asyncio_debug
            )
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.exception(e)
            return 1
        return 0