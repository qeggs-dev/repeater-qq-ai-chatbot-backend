# ==== 标准库 ==== #
from typing import Any

# ==== 第三方库 ==== #
from environs import Env

# ==== 自定义库 ==== #
from .SubManager import SubManager
from sanitizeFilename import sanitize_filename, sanitize_filename_async
from .._user_mainmanager_interface import UserMainManagerInterface

env = Env()

class MainManager(UserMainManagerInterface):
    def __init__(self, base_name: str, cache_metadata:bool = False, cache_data:bool = False, sub_dir_name:str = "ParallelData"):
        self.base_name = sanitize_filename(base_name)
        self.sub_managers:dict[str, SubManager] = {}

        self.cache_metadata = cache_metadata
        self.cache_data = cache_data

        self.sub_dir_name = sub_dir_name
    
    async def load(self, user_id: str, default: Any = None) -> Any:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(
            user_id,
            SubManager(
                env.path('USER_DATA_DIR') / self.base_name / user_id,
                sub_dir_name = self.sub_dir_name,
                cache_metadata = self.cache_metadata,
                cache_data = self.cache_data
            )
        )
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        return await manager.load(item, default)
    
    async def save(self, user_id: str, data: Any) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(
            user_id,
            SubManager(
                env.path('USER_DATA_DIR') / self.base_name / user_id,
                sub_dir_name = self.sub_dir_name,
                cache_metadata = self.cache_metadata,
                cache_data = self.cache_data
            )
        )
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        await manager.save(item, data)
    
    async def delete(self, user_id: str) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(
            user_id,
            SubManager(
                env.path('USER_DATA_DIR') / self.base_name / user_id,
                sub_dir_name = self.sub_dir_name,
                cache_metadata = self.cache_metadata,
                cache_data=self.cache_data
            )
        )
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            item = metadata.get('default_item', 'default')
        else:
            item = 'default'
        await manager.delete(item)
    
    async def set_default_item_id(self, user_id: str, item: str) -> None:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(
            user_id,
            SubManager(
                env.path('USER_DATA_DIR') / self.base_name / user_id,
                sub_dir_name = self.sub_dir_name,
                cache_metadata = self.cache_metadata,
                cache_data = self.cache_data
            )
        )
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            metadata['default_item'] = item
        else:
            metadata = {'default_item': item}
        await manager.save_metadata(metadata)

    async def get_default_item_id(self, user_id: str) -> str:
        user_id = await sanitize_filename_async(user_id)
        manager = self.sub_managers.setdefault(
            user_id,
            SubManager(
                env.path('USER_DATA_DIR') / self.base_name / user_id,
                sub_dir_name = self.sub_dir_name,
                cache_metadata = self.cache_metadata,
                cache_data = self.cache_data
            )
        )
        metadata = await manager.load_metadata()
        if isinstance(metadata, dict):
            return metadata.get('default_item', 'default')
        else:
            return 'default'

    async def get_all_user_id(self) -> list:
        return [f.name for f in (env.path('USER_DATA_DIR') / self.base_name).iterdir() if f.is_dir()]

    async def get_all_item_id(self, user_id: str) -> list:
        return [f.stem for f in (env.path('USER_DATA_DIR') / self.base_name / user_id / self.sub_dir_name).iterdir() if f.is_file()]