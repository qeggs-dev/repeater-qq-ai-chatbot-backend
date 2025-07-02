from abc import ABC, abstractmethod
from typing import Any

class UserMainManagerInterface(ABC):
    @abstractmethod
    def __init__(self, base_name: str, cache_metadata:bool = False, cache_data:bool = False, sub_dir_name:str = "ParallelData"):
        pass

    @abstractmethod
    async def load(self, user_id: str, default: Any = None) -> Any:
        pass
    
    @abstractmethod
    async def save(self, user_id: str, data: Any) -> None:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> None:
        pass
    
    @abstractmethod
    async def set_default_item_id(self, user_id: str, item: str) -> None:
        pass
    
    @abstractmethod
    async def get_default_item_id(self, user_id: str) -> str:
        pass
    
    @abstractmethod
    async def get_all_user_id(self) -> list:
        pass

    @abstractmethod
    async def get_all_item_id(self, user_id: str) -> list:
        pass