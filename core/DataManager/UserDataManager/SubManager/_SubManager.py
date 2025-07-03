# ==== 标准库 ==== #
import os
import asyncio
import weakref
from typing import Any
from pathlib import Path

# ==== 第三方库 ==== #
import orjson
import aiofiles
from environs import Env

# ==== 项目库 ==== #
from SanitizeFilename import sanitize_filename, sanitize_filename_async
from PathProcessors import validate_path

class SubManager:
    _env = Env()
    _metadata_filename = _env.str("USER_DATA_METADATA_FILENAME", "metadata.json")

    def __init__(self, base_path: Path, sub_dir_name: str, cache_metadata:bool = False, cache_data:bool = False):
        self.base_path: Path = base_path
        sub_dir_name: str = sanitize_filename(sub_dir_name)
        self.sub_dir_name: str = sub_dir_name
        self._global_lock: asyncio.Lock = asyncio.Lock()
        self._item_locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.cache_metadata:bool = cache_metadata
        self._metadata_cache: Any | None = None

        self.cache_data:bool = cache_data
        self._data_cache: dict[str, Any] = {}

    @property
    def _default_base_file(self) -> Path:
        """获取默认文件路径"""
        return self.base_path / self.sub_dir_name
    @property
    def _get_metadata_file_path(self) -> Path:
        """获取元数据文件路径"""
        return self.base_path / self._metadata_filename
    
    def _get_file_path(self, name: str) -> Path:
        """获取文件路径"""
        if not self._default_base_file.exists():
            self._default_base_file.mkdir(parents=True, exist_ok=True)
        name = sanitize_filename(name)
        return self._default_base_file / f"{name}.json"
    
    async def _get_item_lock(self, item_name: str) -> asyncio.Lock:
        """获取 item_name 对应的锁，如果没有则创建"""
        async with self._global_lock:
            lock: asyncio.Lock | None = self._item_locks.get(item_name)
            if lock is None:
                lock = asyncio.Lock()
                self._item_locks[item_name] = lock
        return lock
    
    async def load_metadata(self, default: Any | None = None) -> Any:
        """
        Load metadata from file

        Args:
            default (Any, optional): Default value if file does not exist. Defaults to None.

        Returns:
            Any: Metadata
        """
        async with self._global_lock:
            try:
                if self.cache_metadata and self._metadata_cache is not None:
                    return self._metadata_cache
                else:
                    async with aiofiles.open(self._get_metadata_file_path, "rb") as f:
                        fdata = await f.read()
                        metadata = await asyncio.to_thread(orjson.loads, fdata)
                        if self.cache_metadata:
                            self._metadata_cache = metadata
                        return metadata
            except FileNotFoundError:
                return default
            except orjson.JSONDecodeError:
                return default
    
    async def save_metadata(self, data: Any):
        """
        Save metadata to file

        Args:
            data (Any): Metadata to save
        Returns:
            None
        """
        async with self._global_lock:
            async with aiofiles.open(self._get_metadata_file_path, "wb") as f:
                fdata = await asyncio.to_thread(orjson.dumps, data)
                await f.write(fdata)
            if self.cache_metadata:
                self._metadata_cache = data
    
    async def load(self, item: str, default: Any | None = None) -> Any:
        """
        Load data from file

        Args:
            item (str): Item name
            default (Any | None, optional): Default value if item not found. Defaults to None.
        Returns:
            Any: Loaded data
        """
        async with self._global_lock:
            try:
                if self.cache_data and self._data_cache is not None and item in self._data_cache:
                    return self._data_cache[item]
                else:
                    async with aiofiles.open(self._get_file_path(item), "rb") as f:
                        fdata = await f.read()
                        data = await asyncio.to_thread(orjson.loads, fdata)
                        if self.cache_data:
                            self._data_cache[item] = data
                        return data
            except FileNotFoundError:
                return default
            except orjson.JSONDecodeError:
                return default
    
    async def save(self, item: str, data: Any) -> None:
        """
        Save data to a file.

        Args:
            item (str): The name of the item to save.
            data (Any): The data to save.

        Returns:
            None
        """
        async with self._global_lock:
            async with aiofiles.open(self._get_file_path(item), "wb") as f:
                await f.write(await asyncio.to_thread(orjson.dumps, data))
            if self.cache_data:
                self._data_cache[item] = data
    
    async def delete(self, item: str) -> None:
        """Delete a file from the cache.

        Args:
            item (str): The item of the file to delete.

        Returns:
            None
        """
        async with self._global_lock:
            try:
                await asyncio.to_thread(os.remove, self._get_file_path(item))
            except FileNotFoundError:
                pass
