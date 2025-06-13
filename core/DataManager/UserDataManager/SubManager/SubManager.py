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
    def __init__(self, base_path: Path, sub_dir_name: str):
        self.base_path = base_path
        sub_dir_name = sanitize_filename(sub_dir_name)
        self.sub_dir_name = sub_dir_name
        self.lock = asyncio.Lock()
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

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
        async with self.lock:
            try:
                async with aiofiles.open(self._get_metadata_file_path, "rb") as f:
                    fdata = await f.read()
                    return await asyncio.to_thread(orjson.loads, fdata)
            except FileNotFoundError:
                return default
            except orjson.JSONDecodeError:
                return default
    
    async def save_metadata(self, data: Any):
        async with self.lock:
            async with aiofiles.open(self._get_metadata_file_path, "wb") as f:
                fdata = await asyncio.to_thread(orjson.dumps, data)
                await f.write(fdata)
    
    async def load(self, item: str, default: Any | None = None) -> Any:
        async with self.lock:
            try:
                async with aiofiles.open(self._get_file_path(item), "rb") as f:
                    fdata = await f.read()
                    return await asyncio.to_thread(orjson.loads, fdata)
            except FileNotFoundError:
                return default
            except orjson.JSONDecodeError:
                return default
    
    async def save(self, item: str, data: Any) -> None:
        async with self.lock:
            async with aiofiles.open(self._get_file_path(item), "wb") as f:
                await f.write(await asyncio.to_thread(orjson.dumps, data))
    
    async def delete(self, name: str) -> None:
        async with self.lock:
            try:
                await asyncio.to_thread(os.remove, self._get_file_path(name))
            except FileNotFoundError:
                pass
