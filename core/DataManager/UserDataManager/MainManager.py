# ==== 标准库 ==== #
from typing import Any

# ==== 第三方库 ==== #
from environs import Env

# ==== 自定义库 ==== #
from .SubManager import SubManager
from sanitizeFilename import sanitize_filename, sanitize_filename_async

env = Env()

class MainManager:
    def __init__(self, base_name: str):
        self.base_name = sanitize_filename(base_name)
        self.sub_managers:dict[str, SubManager] = {}
    
    async def load(self, user_id: str, default: Any = None) -> Any:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(user_id, SubManager(env.path('USER_DATA_DIR') / self.base_name / user_id, 'ParallelData'))
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        return await manager.load(item, default)
    
    async def save(self, user_id: str, data: Any) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(user_id, SubManager(env.path('USER_DATA_DIR') / self.base_name / user_id, 'ParallelData'))
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        await manager.save(item, data)
    
    async def delete(self, user_id: str) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(user_id, SubManager(env.path('USER_DATA_DIR') / self.base_name / user_id, 'ParallelData'))
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        await manager.delete(item)
    
    async def set_default_item(self, user_id: str, item: str) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(user_id, SubManager(env.path('USER_DATA_DIR') / self.base_name / user_id, 'ParallelData'))
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            metadata['default_item'] = item
        else:
            metadata = {'default_item': item}
        await manager.save_metadata(metadata)

    async def get_default_item(self, user_id: str) -> str:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(user_id, SubManager(env.path('USER_DATA_DIR') / self.base_name / user_id, 'ParallelData'))
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            return metadata.get('default_item', 'default')
        else:
            return 'default'
