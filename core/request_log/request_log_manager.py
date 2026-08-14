import os
import copy
import orjson
import asyncio
import aiofiles
import datetime
import numpy as np
from pathlib import Path
from loguru import logger
from ..global_config_manager import ConfigManager
from typing import List, AsyncIterator, Generator, Iterable
from .objects import RequestLogTypes, validate_request_log
from pydantic import ValidationError

class RequestLogManager:
    def __init__(
            self,
            base_dir: str | os.PathLike,
            debonce_save_wait_time: float | None = None,
            cache_keep_time: float | None = None,
            max_cache_size: int | None = None,
            auto_save: bool = True
        ):

        # 日志缓存列表
        self._log_cache: List[RequestLogTypes] = []
        self._log_list: List[RequestLogTypes] = []

        # 防抖保存等待时间
        if debonce_save_wait_time is None:
            debonce_save_wait_time = ConfigManager.get_configs().request_log.debonce_save_wait_time
        self._debonce_save_wait_time:float = debonce_save_wait_time

        # 缓存保留时间
        if cache_keep_time is None:
            cache_keep_time = ConfigManager.get_configs().request_log.cache_keep_time
        self._cache_keep_time:float = cache_keep_time

        # 最大缓存大小
        if max_cache_size is None:
            max_cache_size = ConfigManager.get_configs().request_log.max_cache_size
        self._max_cache_size = max_cache_size

        # 日志文件路径
        self._base_dir = Path(base_dir)
        if self._base_dir.exists():
            if not self._base_dir.is_dir():
                raise ValueError(f"Invalid path \"{self._base_dir}\"")
        else:
            # 确保日志目录存在
            self._base_dir.mkdir(parents=True, exist_ok=True)

        # 日志锁
        self._data_lock = asyncio.Lock()

        # 防抖任务
        self._debonce_save_task: asyncio.Task | None = None
        self._cache_remove_task: asyncio.Task | None = None

        # 自动保存
        self._auto_save: bool = auto_save
    
    @property
    def log_file_path(self) -> Path:
        """
        日志文件路径
        """
        time = datetime.datetime.now()
        return self._base_dir / f"{time.strftime('%Y-%m-%d')}.jsonl"
    
    async def _debonce_save(self) -> None:
        # 防抖保存操作
        if self._debonce_save_task and not self._debonce_save_task.done():
            self._debonce_save_task.cancel()  # 如果已有任务，先取消
        if len(self._log_list) < self._max_cache_size:
            logger.info("Request log debonce task created")
            wait_time = self._debonce_save_wait_time
        else:
            logger.info("Request log saved immediately")
            wait_time = 0
        self._debonce_save_task = asyncio.create_task(
            self._wait_and_save_async(
                wait_time = wait_time
            )
        )
    
    async def _debonce_remove_cache(self):
        if self._cache_remove_task and not self._cache_remove_task.done():
            self._cache_remove_task.cancel()
        
        wait_time = self._debonce_save_wait_time
        logger.info("Request log remove cache task created")
        
        self._cache_remove_task = asyncio.create_task(
            self._wait_and_remove_cache(
                wait_time = wait_time
            )
        )

    async def add_request_log(self, request_log: RequestLogTypes) -> None:
        """
        添加调用日志项

        :param request_log: 调用日志项
        :return: None
        """
        async with self._data_lock:
            # 添加日志项
            self._log_list.append(request_log)
            logger.info("Request log added", user_id=request_log.user_id)
            await self._debonce_save()

    async def add_multi_request_log(self, request_logs: Iterable[RequestLogTypes]) -> None:
        """
        添加多个调用日志项

        :param request_log: 调用日志项
        :return: None
        """
        async with self._data_lock:
            # 添加日志项
            user_ids: dict[str, int] = {}
            for request_log in request_logs:
                self._log_list.append(request_log)
                if request_log.user_id not in user_ids:
                    user_ids[request_log.user_id] = 1
                else:
                    user_ids[request_log.user_id] += 1
            for user_id, count in user_ids.items():
                if count == 1:
                    logger.info(
                        "Request log added",
                        user_id = user_id
                    )
                else:
                    logger.info(
                        "Request log added {count} times",
                        user_id = user_id,
                        count = count
                    )
            await self._debonce_save()
        
    # 将日志列表转换为字节流
    @staticmethod
    def _log_bytestream(log_list: Iterable[RequestLogTypes]) -> Generator[bytes, None, None]:
        for log in log_list:
            yield orjson.dumps(log.model_dump()) + b"\n"

    def _save_request_log(self) -> None:
        """
        保存队列中的所有日志到文件
        """
        # 如果日志列表为空，直接返回
        if not self._log_list:
            return
        
        path = self.log_file_path
        
        if path.exists():
            # 如果文件存在，以追加模式打开
            with open(path, "ab") as f:
                for chunk in self._log_bytestream(self._log_list):
                    f.write(chunk)
        else:
            # 如果文件不存在，以写入模式打开
            with open(path, "wb") as f:
                for chunk in self._log_bytestream(self._log_list):
                    f.write(chunk)
        
        logger.info(
            "Saved {log_list_len} request logs to file",
            log_list_len = len(self._log_list)
        )

        # 清空日志列表
        self._log_list.clear()

    async def _save_request_log_async(self) -> None:
        """
        异步保存队列中的所有日志到文件
        """
        # 如果日志列表为空，则直接返回
        if not self._log_list:
            return
        
        if self._log_cache:
            self._log_cache.extend(self._log_list)
        
        path = self.log_file_path

        if path.exists():
            # 如果文件存在，则以追加模式打开文件
            async with aiofiles.open(path, "ab") as f:
                for chunk in self._log_bytestream(self._log_list):
                    await f.write(chunk)
        else:
            # 如果文件不存在，则以写入模式打开文件
            async with aiofiles.open(path, "wb") as f:
                for chunk in self._log_bytestream(self._log_list):
                    await f.write(chunk)
        
        logger.info(
            "Saved {log_list_len} request logs to file",
            log_list_len = len(self._log_list)
        )

        # 清空日志列表
        self._log_list.clear()

    async def read_request_log(self) -> list[RequestLogTypes]:
        """
        从文件读取所有调用日志

        :return: 所有调用日志
        """
        request_log_list = []
        async for request_log in self.read_stream_request_log():
            request_log_list.append(request_log)
        return request_log_list

    async def read_stream_request_log(self) -> AsyncIterator[RequestLogTypes]:
        """
        从文件流式读取所有调用日志

        :return: 读取调用日志的生成器
        """
        # 深拷贝内存日志
        async with self._data_lock:
            mem_logs = copy.deepcopy(self._log_list)
        mem_log_count = len(mem_logs)
        logger.info(
            "From {mem_log_count} memory logs",
            mem_log_count = mem_log_count
        )
        readed_log_count: int = 0
        cached = False

        if self._log_cache:
            for log in self._log_cache:
                yield log
                readed_log_count += 1
            cached = True
        else:
            cache: list[RequestLogTypes] = []
            full_memory_cache = ConfigManager.get_configs().request_log.full_memory_cache

            async for log in self._read_file_logs():
                yield log
                readed_log_count += 1
                if full_memory_cache:
                    cache.append(log)
            
            if full_memory_cache:
                async with self._data_lock:
                    self._log_cache = cache
                    await self._debonce_remove_cache()
        
        # 输出内存日志
        for log in mem_logs:
            yield log

        # 记录总数（所有日志已生成）
        total = readed_log_count + mem_log_count
        logger.info(
            "Read {total} request logs"
            if cached else
            "Read {total} request logs (Cached)",
            total = total,
        )
    
    async def _read_file_logs(self) -> AsyncIterator[RequestLogTypes]:
        request_log_files = np.array(
            [str(file) for file in self._base_dir.glob("*.jsonl")]
        )
        sorted_request_log_files = np.sort(request_log_files)
        # 读取文件日志
        log_file_count = 0
        for file in sorted_request_log_files:
            path = Path(file)
            if path.exists():
                async with aiofiles.open(path, "rb") as f:
                    async for line in f:
                        try:
                            data = await asyncio.to_thread(orjson.loads, line)
                        except orjson.JSONDecodeError as e:
                            logger.error(   
                                "JSONDecodeError: {error}\nLine: {line}",
                                error = e,
                                line = line
                            )
                            continue
                        try:
                            yield validate_request_log(**data)  # 生成文件日志
                        except ValidationError as e:
                            errors = e.errors()
                            for error in errors:
                                logger.error(
                                    "Error in log file {file}/{error_field}: {error_message}",
                                    file = file,
                                    error_field = ".".join(str(i) for i in error["loc"]),
                                    error_message = error["msg"]
                                )
                log_file_count += 1  # 文件计数
        logger.info(
            "From {log_file_count} file read logs",
            log_file_count = log_file_count
        )
        
    
    def save_request_log(self) -> None:
        """
        手动保存日志到文件
        """
        # 停止防抖任务
        if self._debonce_save_task and not self._debonce_save_task.done():
            self._debonce_save_task.cancel()  # 如果已有任务，先取消
        self._save_request_log()
    
    async def save_request_log_async(self) -> None:
        """手动保存日志到文件"""
        async with self._data_lock:
            # 停止防抖任务
            if self._debonce_save_task and not self._debonce_save_task.done():
                self._debonce_save_task.cancel()  # 如果已有任务，先取消
            await self._save_request_log_async()

    async def _wait_and_remove_cache(self, wait_time: float = 5) -> None:
        """等待并移除缓存"""
        try:
            logger.info(
                "Wait {wait_time} seconds to remove cache",
                wait_time = wait_time
            )
            # 等待指定时间
            await asyncio.sleep(wait_time)
            # 时间到后保存日志
            async with self._data_lock:
                self._log_cache.clear()
        except asyncio.CancelledError:
            logger.info("Request log remove cache task cancelled")

    async def _wait_and_save_async(self, wait_time: float = 5) -> None:
        """等待并保存日志到文件"""
        try:
            logger.info(
                "Wait {wait_time} seconds to save request log",
                wait_time = wait_time
            )
            # 等待指定时间
            await asyncio.sleep(wait_time)
            # 时间到后保存日志
            if self._auto_save:
                async with self._data_lock:
                    await self._save_request_log_async()
            else:
                self._log_list.clear()
        except asyncio.CancelledError:
            logger.info("Request log save task cancelled")