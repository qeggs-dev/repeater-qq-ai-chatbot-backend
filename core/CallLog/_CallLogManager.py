import asyncio
import aiofiles
import orjson
import copy
from environs import Env
from loguru import logger
from pathlib import Path
from typing import List, AsyncIterator
from ._CallLogObject import CallLogObject, CallAPILogObject

_env = Env()

class CallLogManager:
    def __init__(self, log_file: Path, debonce_save_wait_time: int | None = None, max_cache_size: int | None = None):
        # 日志缓存列表
        self.log_list: List[CallLogObject | CallAPILogObject] = []

        # 防抖保存等待时间
        if debonce_save_wait_time is None:
            debonce_save_wait_time = _env.float("CALLLOG_DEBONCE_SAVE_WAIT_TIME", 60)
        self.debonce_save_wait_time = debonce_save_wait_time

        # 最大缓存大小
        if max_cache_size is None:
            max_cache_size = _env.int("CALLLOG_MAX_CACHE_SIZE", 1000)
        self.max_cache_size = max_cache_size

        # 日志文件路径
        self.log_file = log_file
        # 确保日志目录存在
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # 日志锁
        self.async_lock = asyncio.Lock()

        # 防抖任务
        self._debonce_task: asyncio.Task | None = None

    async def add_call_log(self, call_log: CallLogObject | CallAPILogObject) -> None:
        """
        添加调用日志项

        :param call_log: 调用日志项
        :return: None
        """
        async with self.async_lock:
            # 添加日志项
            self.log_list.append(call_log)
            logger.info("Call log added", user_id=call_log.user_id)
            
            # 防抖保存操作
            if self._debonce_task and not self._debonce_task.done():
                self._debonce_task.cancel()  # 如果已有任务，先取消
            if len(self.log_list) < self.max_cache_size:
                self._debonce_task = asyncio.create_task(self._wait_and_save_async(wait_time = self.debonce_save_wait_time))  # 重新创建
            else:
                self._debonce_task = asyncio.create_task(self._wait_and_save_async(wait_time = 0)) # 直接保存
            logger.info("Call log debonce task created", user_id="[System]")

    def _save_call_log(self) -> None:
        """
        保存队列中的所有日志到文件
        """
        # 如果日志列表为空，直接返回
        if not self.log_list:
            return
        
        # 将日志列表转换为字节流
        def write_log(log_list: List[CallLogObject]) -> bytes:
            return b'\n'.join(orjson.dumps(log.as_dict) for log in log_list) + b'\n'
        
        try:
            # 如果文件存在，以追加模式打开
            with open(self.log_file, 'ab') as f:
                f.write(write_log(self.log_list))
        except FileNotFoundError:
            # 如果文件不存在，以写入模式打开
            with open(self.log_file, 'wb') as f:
                f.write(write_log(self.log_list))
        
        logger.info(f"Saved {len(self.log_list)} call logs to file", user_id="[System]")

        # 清空日志列表
        self.log_list.clear()

    async def _save_call_log_async(self) -> None:
        """
        异步保存队列中的所有日志到文件
        """
        # 如果日志列表为空，则直接返回
        if not self.log_list:
            return
        
        # 定义一个函数，将日志列表转换为字节流
        def write_log(log_list: List[CallLogObject]) -> bytes:
            return b'\n'.join(orjson.dumps(log.as_dict) for log in log_list) + b'\n'
        
        try:
            # 如果文件存在，则以追加模式打开文件
            async with aiofiles.open(self.log_file, 'ab') as f:
                await f.write(write_log(self.log_list))
        except FileNotFoundError:
            # 如果文件不存在，则以写入模式打开文件
            async with aiofiles.open(self.log_file, 'wb') as f:
                await f.write(write_log(self.log_list)) 
        logger.info(f"Saved {len(self.log_list)} call logs to file", user_id="[System]")

        # 清空日志列表
        self.log_list.clear()

    async def read_call_log(self) -> List[CallLogObject]:
        """
        从文件读取所有调用日志

        :return: 所有调用日志
        """
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
        """
        从文件流式读取所有调用日志

        :return: 读取调用日志的生成器
        """
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
                    file_log_count += 1  # 计数
        
        # 生成内存日志
        for log in mem_logs:
            yield log

        # 记录总数（所有日志已生成）
        total = file_log_count + mem_log_count
        logger.info(f"Read {total} call logs from file", user_id="[System]")
        
    
    def save_call_log(self) -> None:
        """
        手动保存日志到文件
        """
        # 停止防抖任务
        if self._debonce_task and not self._debonce_task.done():
            self._debonce_task.cancel()  # 如果已有任务，先取消
        self._save_call_log()
    
    async def save_call_log_async(self) -> None:
        """手动保存日志到文件"""
        async with self.async_lock:
            # 停止防抖任务
            if self._debonce_task and not self._debonce_task.done():
                self._debonce_task.cancel()  # 如果已有任务，先取消
            await self._save_call_log_async()

    async def _wait_and_save_async(self, wait_time: float = 5) -> None:
        """等待并保存日志到文件"""
        try:
            # 等待指定时间
            await asyncio.sleep(wait_time)
            # 时间到后保存日志
            await self._save_call_log_async()
        except asyncio.CancelledError:
            logger.info("Call log save task cancelled", user_id="[System]")