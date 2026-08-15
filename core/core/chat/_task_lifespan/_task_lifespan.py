import uuid
import asyncio
from ....pools.resource_pool import ResourcePool
from ....status_map import StatusStack
from ....text_buffer import ContentBuffer
from ....runtime_container import RepeaterRuntime
from ._task_status_stack import TaskStatusStacks
from ._task_context_buffer import TaskContextBuffers

class TaskLifespan:
    def __init__(
        self,
        user_id: str,
        rul: asyncio.Lock,
        enable_rul: bool,
        runtime: RepeaterRuntime,
        task_id: str | uuid.UUID | None = None,
    ):
        self._rul = rul
        self._enable_rul = enable_rul

        if task_id is None:
            task_id = uuid.uuid4()
        elif isinstance(task_id, str):
            task_id = uuid.UUID(task_id)
        elif not isinstance(task_id, uuid.UUID):
            raise TypeError("task_id must be str or uuid.UUID")
        
        self._task_id = task_id
        self._runtime = runtime
        self._user_id = user_id

        self._task_status_stacks = TaskStatusStacks(self._runtime)
        self._task_context_buffers = TaskContextBuffers(self._runtime)

        if self.get_task_id_str() in self._task_status_stacks or self.get_task_id_str() in self._task_context_buffers:
            raise ValueError("task_id already exists")
    
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def task_id(self) -> uuid.UUID:
        return self._task_id
    
    @property
    def runtime(self) -> RepeaterRuntime:
        return self._runtime
    
    @property
    def task_id_str(self) -> str:
        return str(self._task_id)
    
    def get_task_id_str(self) -> str:
        return self.task_id_str
    
    @property
    def task_status_stack(self) -> StatusStack[str]:
        return self._task_status_stack
    
    @property
    def task_content_buffer(self) -> ContentBuffer:
        return self._task_content_buffer
    
    async def __aenter__(self):
        self._task_status_stack = await self._task_status_stacks.get_task_status_stack(
            self._user_id,
            self.get_task_id_str()
        )
        self._task_content_buffer = await self._task_context_buffers.get_task_content_buffer(
            self._user_id,
            self.get_task_id_str()
        )

        if self._enable_rul:
            await self._rul.acquire()
        return self
    
    async def __aexit__(self, exc_type, exc_value, exc_tb):
        if self._enable_rul:
            self._rul.release()
        
        await self._task_status_stacks.remove_task_status_stack(
            self._user_id,
            self.get_task_id_str()
        )
        await self._task_context_buffers.remove_task_content_buffer(
            self._user_id,
            self.get_task_id_str()
        )