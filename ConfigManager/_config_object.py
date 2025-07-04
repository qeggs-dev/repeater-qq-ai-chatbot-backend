from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar
from enum import Enum
from copy import deepcopy
from pathlib import Path


T = TypeVar('T')

@dataclass
class ConfigObject:
    """
    A class to store configuration data for a single object.
    """
    name: str
    _values: list[Any] = field(default_factory=list)
    _now_index: int = 0
    _changed_callbacks: dict[str, Callable] = field(default_factory=dict)
    strict_type: bool = False

    def __repr__(self) -> str:
        if self._values:
            return f"<ConfigObject: \"{self.name}\" = {repr(self._values[self._now_index])}>"
        else:
            return f"<ConfigObject: \"{self.name}\" = None>"

    @property
    def value_type(self) -> type:
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
        if self.strict_type and not isinstance(value, self.value_type):
            raise TypeError(f"Value must be of type {self.value_type.__name__}")
        self._values.append(value)
        self._now_index = len(self._values) - 1

        if self._changed_callbacks:
            for callback in self._changed_callbacks.values():
                callback(value)

    def get_value(
        self,
        target_types: type[T] | tuple[type[T], ...] | None = None,
        *,
        skip_conversion_if_match: bool = True
    ) -> T:
        """Enhanced value getter with conversion support.

        Args:
            target_types: Type or tuple of types to attempt conversion to.
            skip_conversion_if_match: Whether to prefer the original type over the target type (default: True).

        Returns:
            Converted value in specified type, or original value if conversion fails.

        Examples:
            >>> config.get_value(int)  # Try converting to int
            >>> config.get_value(converter=lambda x: datetime.fromisoformat(x))
        """
        raw_value = self._values[self._now_index]

        # 情况1：不要求类型转换
        if target_types is None:
            return deepcopy(raw_value)

        # 统一处理为类型元组
        types = (target_types,) if isinstance(target_types, type) else target_types

        # 情况2：优先检查原始类型
        if skip_conversion_if_match:
            if type(raw_value) in types:  # 精确匹配类型
                return deepcopy(raw_value)
            if bool in types and isinstance(raw_value, bool):  # 处理bool特殊情况
                return raw_value
            if None in types and raw_value is None:  # 处理None特殊情况
                return None

        # 情况3：尝试类型转换
        type_handlers = {
            bool: lambda x: x if isinstance(x, bool) else str(x).lower() in ("true", "1", "yes"),
            Path: lambda x: x if isinstance(x, Path) else Path(str(x)),
            int: lambda x: int(float(x)) if isinstance(x, str) and "." in x else int(x)
        }

        for t in types:
            try:
                # 如果已经是该类型且未开启prefer_original_type，仍会执行转换（可能触发__init__）
                if skip_conversion_if_match and isinstance(raw_value, t):
                    continue

                handler = type_handlers.get(t, t)
                converted = handler(raw_value)
                return deepcopy(converted)
            except (TypeError, ValueError, AttributeError):
                continue
            
        # 所有转换尝试失败后返回原始值
        return deepcopy(raw_value)
    
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
