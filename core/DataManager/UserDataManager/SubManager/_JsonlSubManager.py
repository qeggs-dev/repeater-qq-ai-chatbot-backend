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
from ._SubManager import SubManager

class JsonlSubManager(SubManager):
    def __init__(self, base_path, sub_dir_name):
        super().__init__(base_path, sub_dir_name)

    def _get_file_path(self, name: str) -> Path:
        if not self._default_base_file.exists():
            self._default_base_file.mkdir(parents=True, exist_ok=True)
        name = sanitize_filename(name)
        return self._default_base_file / f"{name}.jsonl"
    
    async def load(self, item: str, default: list | None = None) -> list:
        if not isinstance(default, list):
            raise TypeError('default must be a list')
        outlist = []
        async with self._global_lock:
            try:
                async with aiofiles.open(self._get_file_path(item), "rb") as f:
                    async for line in f:
                        try:
                            if line:
                                outlist.append(orjson.loads(line))
                        except orjson.JSONDecodeError:
                            continue
            except FileNotFoundError:
                return default
        if outlist:
            return outlist
        return default
    
    async def save(self, item: str, data: list) -> None:
        if not isinstance(data, list):
            raise TypeError('data must be a list')
        async with self._global_lock:
            async with aiofiles.open(self._get_file_path(item), "wb") as f:
                for line in data:
                    await f.write(orjson.dumps(line))
                    await f.write(b'\n')
    
    async def append(self, item: str, data: list) -> None:
        if not isinstance(data, list):
            raise TypeError('data must be a list')
        async with self._global_lock:
            async with aiofiles.open(self._get_file_path(item), "ab") as f:
                for line in data:
                    await f.write(orjson.dumps(line))
                    await f.write(b'\n')