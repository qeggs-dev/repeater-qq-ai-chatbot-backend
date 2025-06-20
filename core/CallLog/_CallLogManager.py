import asyncio
import aiofiles
import orjson
import copy
from loguru import logger
from pathlib import Path
from typing import List, AsyncIterator
from ._CallLogObject import CallLogObject, CallAPILogObject


class CallLogManager:
    def __init__(self, log_file: Path, max_log_length: int = 1000):
        self.log_list: List[CallLogObject | CallAPILogObject] = []
        self.max_log_length = max_log_length
        self.log_file = log_file
        self.async_lock = asyncio.Lock()
        
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    async def add_call_log(self, call_log: CallLogObject | CallAPILogObject) -> None:
        async with self.async_lock:
            self.log_list.append(call_log)
            logger.info("Call log added", user_id=call_log.user_id)
            if len(self.log_list) > self.max_log_length:
                await self._save_call_log()

    def _save_call_log(self) -> None:
        """保存队列中的所有日志到文件"""
        if not self.log_list:
            return
        
        def write_log(log_list: List[CallLogObject]) -> bytes:
            return b'\n'.join(orjson.dumps(log.as_dict) for log in log_list) + b'\n'
        
        try:
            with open(self.log_file, 'ab') as f:
                f.write(write_log(self.log_list))
        except FileNotFoundError:
            with open(self.log_file, 'wb') as f:
                f.write(write_log(self.log_list))
            
        logger.info(f"Saved {len(self.log_list)} call logs to file", user_id="[System]")
        self.log_list.clear()

    async def _save_call_log_async(self) -> None:
        """异步保存队列中的所有日志到文件"""
        if not self.log_list:
            return
        
        def write_log(log_list: List[CallLogObject]) -> bytes:
            return b'\n'.join(orjson.dumps(log.as_dict) for log in log_list) + b'\n'
        
        try:
            async with aiofiles.open(self.log_file, 'ab') as f:
                await f.write(write_log(self.log_list))
        except FileNotFoundError:
            async with aiofiles.open(self.log_file, 'wb') as f:
                await f.write(write_log(self.log_list))
            
        logger.info(f"Saved {len(self.log_list)} call logs to file", user_id="[System]")
        self.log_list.clear()

    async def read_call_log(self) -> List[CallLogObject]:
        """从文件读取所有调用日志"""
        call_log_list = []
        if self.log_file.exists():
            async with aiofiles.open(self.log_file, 'rb') as f:
                async for line in f:
                    data = await asyncio.to_thread(orjson.loads, line)
                    call_log_list.append(CallLogObject.from_dict(data))
        async with self.async_lock:
            call_log_list += copy.deepcopy(self.log_list)
        logger.info(f"Read {len(call_log_list)} call logs from file", user_id="[System]")
        return call_log_list

    async def read_stream_call_log(self) -> AsyncIterator[CallLogObject]:
        """从文件流式读取所有调用日志"""
        # 深拷贝内存日志
        async with self.async_lock:
            mem_logs = copy.deepcopy(self.log_list)
        mem_log_count = len(mem_logs)
        
        # 读取文件日志
        file_log_count = 0
        if self.log_file.exists():
            async with aiofiles.open(self.log_file, 'rb') as f:
                async for line in f:
                    data = await asyncio.to_thread(orjson.loads, line)
                    yield CallLogObject.from_dict(data)  # 生成文件日志
                    file_log_count += 1  # 正确计数
        
        # 生成内存日志
        for log in mem_logs:
            yield log

        # 正确记录总数（所有日志已生成）
        total = file_log_count + mem_log_count
        logger.info(f"Read {total} call logs from file", user_id="[System]")
        
    
    def save_call_log(self) -> None:
        """手动保存日志到文件"""
        self._save_call_log()
    
    async def save_call_log_async(self) -> None:
        """手动保存日志到文件"""
        async with self.async_lock:
            await self._save_call_log_async()