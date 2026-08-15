import uuid
import asyncio
from ....pools.resource_pool import ResourcePool
from ....status_map import StatusStack
from ....text_buffer import ContentBuffer
from ....runtime_container import RepeaterRuntime

class TaskContextBuffers:
    def __init__(self, runtime: RepeaterRuntime):
        self._runtime = runtime
    
    async def get_user_content_buffers(self, user_id: str) -> ResourcePool[str, ContentBuffer]:
        if user_id in self._runtime.content_buffers_pools:
            user_content_buffers = await self._runtime.content_buffers_pools.get(
                user_id
            )
        else:
            user_content_buffers = ResourcePool()
            await self._runtime.content_buffers_pools.add(
                user_id,
                user_content_buffers
            )
        return user_content_buffers
    
    def __contains__(self, task_id: str) -> bool:
        return task_id in self._runtime.content_buffers_pools
    
    async def get_task_content_buffer(self, user_id: str, task_id: str) -> ContentBuffer:
        user_content_buffers = await self.get_user_content_buffers(user_id)
        if task_id in user_content_buffers:
            task_content_buffer = await user_content_buffers.get(task_id)
        else:
            task_content_buffer = ContentBuffer()
            await user_content_buffers.add(task_id, task_content_buffer)
        return task_content_buffer
    
    async def remove_task_content_buffer(self, user_id: str, task_id: str) -> None:
        user_status_stack = await self.get_user_content_buffers(user_id)
        await user_status_stack.remove(task_id)
        if not user_status_stack:
            await self.remove_user_content_buffers(user_id)
    
    async def remove_user_content_buffers(self, user_id: str) -> None:
        await self._runtime.task_status_stacks.remove(user_id)