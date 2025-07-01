from ._exceptions import ConfigManagerException
from environs import Env
from typing import (
    Any,
    Iterator,
    Dict,
    ItemsView,
    KeysView,
    ValuesView
)

class Configs:
    """
    Configs for user.
    """

    def __init__(self, user_id: str = "", configs: Dict[str, Any] = None):
        self._user_id = user_id
        self._configs = configs or {}
        if not isinstance(self._configs, dict):
            raise ConfigManagerException("Configs must be a dict")

    def __getitem__(self, key: str) -> Any:
        if key not in self._configs:
            raise KeyError(f"Key '{key}' not found")
        return self._configs[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._configs[key] = value

    def __delitem__(self, key: str) -> None:
        if key not in self._configs:
            raise KeyError(f"Key '{key}' not found")
        del self._configs[key]
    
    def __contains__(self, key: str) -> bool:
        return key in self._configs
    
    def __len__(self) -> int:
        return len(self._configs)
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._configs)
    
    def __repr__(self) -> str:
        return f"<Configs user_id={self.user_id} keys={list(self._configs.keys())}>"

    def keys(self) -> KeysView[str]:
        return self._configs.keys()
    
    def values(self) -> ValuesView[Any]:
        return self._configs.values()

    def items(self) -> ItemsView[str, Any]:
        return self._configs.items()
    
    def get(self, key: str, default: Any = None) -> Any:
        if key in self._configs:
            return self._configs[key]
        else:
            return default
    
    def set(self, key: str, value: Any) -> None:
        self._configs[key] = value
    
    def pop(self, key: str, default: Any = None) -> Any:
        if key in self._configs:
            return self._configs.pop(key)
        else:
            return default
    
    def update(self, other: Dict[str, Any] = None, **kwargs: Any) -> None:
        if other is not None:
            self._configs.update(other)
        if kwargs:
            self._configs.update(kwargs)
    
    def clear(self) -> None:
        self._configs.clear()

    def empty(self) -> bool:
        return not bool(self._configs)
    
    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def configs(self) -> Dict[str, Any]:
        return self._configs