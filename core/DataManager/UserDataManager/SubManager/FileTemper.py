import asyncio
import os
import time
from pathlib import Path
from typing import Optional, Union

class AsyncBufferedFile:
    def __init__(
        self,
        file_path: Union[str, Path],
        save_delay: float = 2.0,
        initial_data: bytes = b'',
        *,
        auto_create: bool = True
    ):
        """
        基于 aiofiles 的异步延迟保存文件管理
        
        :param file_path: 文件路径
        :param save_delay: 保存延迟时间（秒），默认2秒
        :param initial_data: 初始数据（二进制）
        :param auto_create: 如果文件不存在是否自动创建
        """
        self.file_path = Path(file_path)
        self._data = initial_data
        self.save_delay = save_delay
        self.lock = asyncio.Lock()
        self._save_task: Optional[asyncio.Task] = None
        self._last_modified = time.monotonic()
        self._has_full_update = False
        self._dirty = False
        self._auto_create = auto_create
        self._file_exists = self.file_path.exists()
        self._loaded = False if initial_data else not self._file_exists

    async def read(self) -> bytes:
        """读取文件内容（优先从内存读取）"""
        async with self.lock:
            if not self._loaded and self._file_exists:
                # 从文件异步加载数据
                try:
                    import aiofiles
                    async with aiofiles.open(self.file_path, 'rb') as f:
                        self._data = await f.read()
                    self._loaded = True
                    return self._data
                except FileNotFoundError:
                    self._file_exists = False
                    return b''
            return self._data

    async def update_full(self, new_data: bytes):
        """全量更新文件内容"""
        async with self.lock:
            self._data = new_data
            self._has_full_update = True
            self._dirty = True
            self._loaded = True  # 标记已加载数据
            self._schedule_save()

    async def update_append(self, additional_data: bytes):
        """追加文件内容"""
        async with self.lock:
            self._data += additional_data
            # 如果之前没有全量更新，可以保持追加模式
            if not self._has_full_update:
                self._dirty = True
                self._schedule_save()
            self._loaded = True  # 标记已加载数据

    async def save_immediately(self):
        """立即保存文件"""
        async with self.lock:
            # 取消任何待处理的保存任务
            if self._save_task and not self._save_task.done():
                self._save_task.cancel()
            
            await self._perform_save()

    def _schedule_save(self):
        """调度延迟保存任务（重置现有计时器）"""
        self._last_modified = time.monotonic()
        
        # 取消现有的保存任务
        if self._save_task and not self._save_task.done():
            self._save_task.cancel()
        
        # 创建新的延迟保存任务
        self._save_task = asyncio.create_task(self._delayed_save())

    async def _delayed_save(self):
        """执行延迟保存的核心逻辑"""
        try:
            # 等待延迟时间，但允许被新任务取消
            await asyncio.sleep(self.save_delay)
            
            async with self.lock:
                # 检查在等待期间是否有新更新
                elapsed = time.monotonic() - self._last_modified
                if elapsed >= self.save_delay - 0.001:  # 处理浮点精度问题
                    await self._perform_save()
        except asyncio.CancelledError:
            # 任务被取消是正常情况，无需处理
            pass

    async def _perform_save(self):
        """使用 aiofiles 执行异步文件保存"""
        if not self._dirty or not self._data:
            return
        
        # 确保目录存在
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            import aiofiles
            
            # 根据更新类型选择写入模式
            mode = 'wb' if self._has_full_update else 'ab'
            
            async with aiofiles.open(self.file_path, mode) as f:
                await f.write(self._data)
            
            # 更新文件状态
            self._file_exists = True
            self._dirty = False
            self._has_full_update = False  # 重置全量更新标志
            
        except Exception as e:
            print(f"保存文件 {self.file_path} 失败: {e}")
            # 保存失败时重新调度
            self._schedule_save()

    async def close(self):
        """关闭并确保保存文件"""
        await self.save_immediately()
        if self._save_task and not self._save_task.done():
            self._save_task.cancel()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.close()