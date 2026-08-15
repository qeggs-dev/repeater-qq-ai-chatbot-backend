import uuid
import asyncio
from ....pools.resource_pool import ResourcePool
from ....status_map import StatusStack
from ....text_buffer import ContentBuffer
from ....runtime_container import RepeaterRuntime

class TaskStatusStacks:
    def __init__(self, runtime: RepeaterRuntime):
        self._runtime = runtime

    async def get_user_status_stacks(self, user_id: str) -> ResourcePool[str, StatusStack[str]]:
        if user_id in self._runtime.task_status_stacks:
            user_status_stack = await self._runtime.task_status_stacks.get(
                user_id
            )
        else:
            user_status_stack = ResourcePool()
            await self._runtime.task_status_stacks.add(
                user_id,
                user_status_stack
            )
        return user_status_stack
    
    def __contains__(self, task_id: str) -> bool:
        return task_id in self._runtime.task_status_stacks
    
    async def get_task_status_stack(self, user_id: str, task_id: str) -> StatusStack[str]:
        user_status_stack = await self.get_user_status_stacks(user_id)
        if task_id in user_status_stack:
            task_status_stack = await user_status_stack.get(task_id)
        else:
            task_status_stack = StatusStack()
            await user_status_stack.add(task_id, task_status_stack)
        return task_status_stack
    
    async def remove_task_status_stack(self, user_id: str, task_id: str) -> None:
        user_status_stack = await self.get_user_status_stacks(user_id)
        if task_id in user_status_stack:
            await user_status_stack.remove(task_id)
        if not user_status_stack:
            await self.remove_user_status_stacks(user_id)
    
    async def remove_user_status_stacks(self, user_id: str) -> None:
        if user_id in self._runtime.task_status_stacks:
            await self._runtime.task_status_stacks.remove(user_id)