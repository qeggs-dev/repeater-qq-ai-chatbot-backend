from dataclasses import dataclass
from typing import Any, Type, TypeVar

T = TypeVar('T')

@dataclass
class UserConfig:
    key: str = ''
    value: T = None
    value_type: Type[T] = None
    upper_limit: int | float = 0
    lower_limit: int | float = 0

    @property
    def get_value(self) -> T:
        if isinstance(self.value, self.value_type):
            if self.upper_limit != 0 or self.lower_limit != 0:
                return max(min(self.value, self.upper_limit), self.lower_limit)
            return self.value
        else:
            try:
                return self.value_type(self.value)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Failed to convert value to {self.value_type}: {e}")