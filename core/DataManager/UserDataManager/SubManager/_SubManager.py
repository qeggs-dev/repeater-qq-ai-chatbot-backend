# ==== 标准库 ==== #
import os
import asyncio
from typing import Any
from pathlib import Path

# ==== 第三方库 ==== #
import orjson
import aiofiles

# ==== 自定义库 ==== #
from sanitizeFilename import sanitize_filename, sanitize_filename_async

class SubManager:
    def __init__(self, base_path: Path, sub_dir_name: str, cache_metadata:bool = False, cache_data:bool = False):
        self.base_path: Path = base_path
        sub_dir_name: str = sanitize_filename(sub_dir_name)
        self.sub_dir_name: str = sub_dir_name
        self.lock: asyncio.Lock = asyncio.Lock()
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)
        
        self.cache_metadata:bool = cache_metadata
        self._metadata: Any | None = None

        self.cache_data:bool = cache_data
        self._data: dict[str, Any] = {}

    @property
    def _default_base_file(self) -> Path:
        return self.base_path / self.sub_dir_name
    @property
    def _get_metadata_file_path(self) -> Path:
        return self.base_path / "metadata.json"
    
    def _get_file_path(self, name: str) -> Path:
        if not self._default_base_file.exists():
            self._default_base_file.mkdir(parents=True, exist_ok=True)
        name = sanitize_filename(name)
        return self._default_base_file / f"{name}.json"
    
    
    async def load_metadata(self, default: Any | None = None) -> Any:
        """
        Load metadata from file

        Args:
            default (Any, optional): Default value if file does not exist. Defaults to None.

        Returns:
            Any: Metadata
        """
        async with self.lock:
            try:
                if self.cache_metadata and self._metadata is not None:
                    return self._metadata
                else:
                    async with aiofiles.open(self._get_metadata_file_path, "rb") as f:
                        fdata = await f.read()
                        metadata = await asyncio.to_thread(orjson.loads, fdata)
                        if self.cache_metadata:
                            self._metadata = metadata
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
        async with self.lock:
            async with aiofiles.open(self._get_metadata_file_path, "wb") as f:
                fdata = await asyncio.to_thread(orjson.dumps, data)
                await f.write(fdata)
            if self.cache_metadata:
                self._metadata = data
    
    async def load(self, item: str, default: Any | None = None) -> Any:
        """
        Load data from file

        Args:
            item (str): Item name
            default (Any | None, optional): Default value if item not found. Defaults to None.
        Returns:
            Any: Loaded data
        """
        async with self.lock:
            try:
                if self.cache_data and self._data is not None and item in self._data:
                    return self._data[item]
                else:
                    async with aiofiles.open(self._get_file_path(item), "rb") as f:
                        fdata = await f.read()
                        data = await asyncio.to_thread(orjson.loads, fdata)
                        if self.cache_data:
                            self._data[item] = data
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
        async with self.lock:
            async with aiofiles.open(self._get_file_path(item), "wb") as f:
                await f.write(await asyncio.to_thread(orjson.dumps, data))
            if self.cache_data:
                self._data[item] = data
    
    async def delete(self, item: str) -> None:
        """Delete a file from the cache.

        Args:
            item (str): The item of the file to delete.

        Returns:
            None
        """
        async with self.lock:
            try:
                await asyncio.to_thread(os.remove, self._get_file_path(item))
            except FileNotFoundError:
                pass
