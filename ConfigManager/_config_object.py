from dataclasses import dataclass, field
from typing import Any, Callable
from enum import Enum
from copy import deepcopy

@dataclass
class ConfigObject:
    """
    A class to store configuration data for a single object.
    """
    name: str
    _values: list[Any] = field(default_factory=list)
    _now_index: int = 0
    _changed_callbacks: dict[str, Callable] = {}
    strict_type: bool = False

    @property
    def type(self) -> type:
        """
        The type of the current value.
        """
        return type(self._values[self._now_index])

    @property
    def value(self) -> Any:
        """
        Snapshot of the current value.

        Note! If you need high performance, don't rely on this value! 
        Please cache it yourself.
        """
        if len(self._values) == 0:
            return None
        # 此处使用深拷贝以防止外部修改内部管理值
        return deepcopy(self._values[self._now_index])
    
    @value.setter
    def value(self, value: Any) -> None:
        """
        Set the current value.
        """
        if self.strict_type and not isinstance(value, self.type):
            raise TypeError(f"Value must be of type {self.type.__name__}")
        self._values.append(value)
        self._now_index = len(self._values) - 1

        if self._changed_callbacks:
            for callback in self._changed_callbacks.values():
                callback(value)
    
    def clear(self) -> None:
        """
        Clear all values.
        """
        self._values = []
        self._now_index = 0
    
    def downgrade(self) -> None:
        """
        Downgrade to the previous value.
        """
        if len(self._values) > 1:
            self._values.pop()
            if self._now_index > len(self._values) - 1:
                self._now_index = len(self._values) - 1
    
    def backtracking(self) -> bool:
        """
        Backtracking to the previous value.
        """
        if self._now_index > 0:
            self._now_index -= 1
            return True
        return False

    def forwardtracking(self) -> bool:
        """
        Forwardtracking to the next value.
        """
        if self._now_index < len(self._values) - 1:
            self._now_index += 1
            return True
        return False

    def add_change_callback(self, key: str, callback: Callable[[Any], None]) -> None:
        """
        Add a callback function when the value changes.

        :param key: The key of the function.
        :param callback: The callback function.
        """
        self._changed_callbacks[key] = callback
    
    def remove_change_callback(self, key: str) -> bool:
        """
        Remove a callback function when the value changes.

        :param key: The key of the function.
        """
        if key in self._changed_callbacks:
            del self._changed_callbacks[key]
            return True
        return False
