import asyncio
from typing import Coroutine, Any, Optional, TypeVar

T = TypeVar('T')

class ScheduledTask:
    def __init__(self, coroutine: Coroutine[Any, Any, T]):
        self._coroutine: Coroutine[Any, Any, T] = coroutine
        self._return_value: Optional[T] = None
        self._exception: Optional[Exception] = None
        self._scheduledTask: Optional[asyncio.Task] = None
        self._runningCoroutine: asyncio.Task | None = None
        self._keepRunningCoroutine: bool = True

    async def createTask(self, delay: float, runningCoroutine: bool = True) -> None:
        """创建延迟任务"""
        self._scheduledTask = asyncio.create_task(self._waittime(delay))
        self._scheduledTask.add_done_callback(self._done_callback)
        self._keepRunningCoroutine = runningCoroutine

    async def _waittime(self, delay: float) -> None:
        """等待延迟并执行协程"""
        await asyncio.sleep(delay)
        try:
            self._return_value = await self._coroutine
        except Exception as e:
            self._exception = e
            raise

    async def _done_callback(self, task: asyncio.Task) -> None:
        """任务完成回调"""
        if task.cancelled():
            if self._keepRunningCoroutine:
                self._runningCoroutine = asyncio.create_task(self._coroutine)
        elif exc := task.exception():
            self._exception = exc
    


    async def breakTask(self) -> None:
        """中断任务"""
        if self._scheduledTask and not self._scheduledTask.done():
            self._scheduledTask.cancel()
            try:
                await self._scheduledTask
            except asyncio.CancelledError:
                pass

    async def get_return_value(self) -> T:
        """获取返回值"""
        if self._exception:
            raise self._exception
        return self._return_value