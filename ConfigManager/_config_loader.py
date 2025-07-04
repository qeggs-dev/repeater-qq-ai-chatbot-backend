import orjson
import asyncio
import aiofiles
import threading
from ._config_object import ConfigObject
from ._config_data_model import Config_Model
from ._exceptions import *
from typing import Any
from loguru import logger
import platform
from pydantic import ValidationError
from pathlib import Path

class ConfigLoader:
    """
    This class is used to automatically manage configuration information for the entire project.
    """
    _golbal_config: dict[str, ConfigObject] = {}

    def __init__(
            self,
            config_file_path: str | Path | None = None,
            strictly_case_sensitive: bool = False,
            use_global: bool = True
        ):
        self._use_global = use_global
        self._config: dict[str, ConfigObject] = {}
        self._config_sync_lock = threading.Lock()
        self._config_async_lock = asyncio.Lock()

        self._strictly_case_sensitive = strictly_case_sensitive

        if config_file_path is not None:
            self._config_file_path = Path(config_file_path)
            self.load_config(config_file_path)
        else:
            self._config_file_path = None
    
    @property
    def _get_config(self) -> dict[str, ConfigObject]:
        if self._use_global:
            return self._golbal_config
        return self._config
    
    def __repr__(self) -> str:
        return f"<ConfigLoader Length={len(self._get_config)}>"

    async def load_config_async(self, file_path: str | Path):
        """
        This method is used to load configuration information from a file.
        :param file_path: The file path of the configuration file.
        :return: None
        """
        async with self._config_async_lock:
            async with aiofiles.open(file_path, mode='rb') as f:
                config = await f.read()
            config:list[dict[str, Any]] = orjson.loads(config)
            await asyncio.to_thread(self._decode_config(config))
    
    def load_config(self, file_path: str | Path):
        """
        This method is used to load configuration information from a file.
        :param file_path: The file path of the configuration file.
        :return: None
        """
        with self._config_sync_lock:
            with open(file_path, mode='rb') as f:
                config = f.read()
            config:list[dict[str, Any]] = orjson.loads(config)
            self._decode_config(config)
        
    def _decode_config(self, config_list: list[dict[str, Any]]):
        """
        This method is used to decode the configuration information.
        :return: The decoded configuration information.
        """
        if not isinstance(config_list, list):
            raise TypeError("Config must be a list.")
        system = platform.system().lower()
        configs = self._get_config
        for item in reversed(config_list):
            try:
                config_model = Config_Model(**item)
            except ValidationError as e:
                raise ConfigSyntaxError("Invalid config syntax.", e.errors())
            if self._strictly_case_sensitive:
                name = config_model.name
            else:
                name = config_model.name.lower()
            if name in configs:
                config = configs[name]
            else:
                config = ConfigObject(name = name)

            for value_item in reversed(config_model.values):
                if value_item.system in {system, "*", "all", None}:
                    type = value_item.type
                    TYPES = {
                        "int": int,
                        "float": float,
                        "str": str,
                        "list": list,
                        "dict": dict
                    }
                    try:
                        if value_item.value is None:
                            value = None
                        if type in TYPES:
                            value = TYPES[type](value_item.value)
                        elif type == "bool":
                            if isinstance(value_item.value, str):
                                value = value_item.value.lower() in {"true", "1", "yes"}
                            else:
                                value = bool(value_item.value)
                        elif type == "json":
                            value = orjson.loads(value_item.value)
                        elif type == "path":
                            value = Path(value_item.value)
                        elif type in {"auto", "other"}:
                            value = value_item.value
                        config.value = value
                    except (ValueError, TypeError, orjson.JSONDecodeError):
                        logger.warning(f"The custom configuration data type conversion failed, and an attempt has been made to use the {config.value_type} type.", user_id = "[System]")
                        config.value = value_item.value
            
            configs[name] = config

    def get_config(self, name: str, default: Any = None) -> ConfigObject:
        configs = self._get_config
        if not self._strictly_case_sensitive:
            name = name.lower()
        if name in configs:
            return configs[name]
        else:
            config = ConfigObject(name = name)
            config.value = default
            return config

    def get_configs(self, names: list[str]) -> dict[str, ConfigObject]:
        return {name: self.get_config(name) for name in names}
    
    def add_config(self, name: str, value: Any) -> None:
        configs = self._get_config
        if not self._strictly_case_sensitive:
            name = name.lower()
        
        if name in configs:
            config = configs[name]
        else:
            config = ConfigObject(name)
        config.value = value

        configs[name] = config
    
    def __contains__(self, name: str) -> bool:
        return name in self._get_config