from __future__ import annotations
from pydantic import BaseModel, ConfigDict, Field
import time

class TimeStamp(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
    )

    timestamp: int = Field(default_factory=lambda: time.time_ns())
    monotonic: int = Field(default_factory=lambda: time.perf_counter_ns())

    def record(self, update_time: bool = True, update_monotonic: bool = True) -> None:
        """
        Record the current time
        """
        if update_time:
            self.timestamp = time.time_ns()
        if update_monotonic:
            self.monotonic = time.perf_counter_ns()
    
    def __add__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp + other.timestamp,
                monotonic = self.monotonic + other.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp + other,
                monotonic = self.monotonic + other
            )
        else:
            return NotImplemented
    
    def __radd__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp + self.timestamp,
                monotonic = other.monotonic + self.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other + self.timestamp,
                monotonic = other + self.monotonic
            )
        else:
            return NotImplemented
    
    def __iadd__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp += other.timestamp
            self.monotonic += other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp += other
            self.monotonic += other
            return self
        else:
            return NotImplemented
    
    def __sub__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp - other.timestamp,
                monotonic = self.monotonic - other.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp - other,
                monotonic = self.monotonic - other
            )
        else:
            return NotImplemented
    
    def __rsub__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp - self.timestamp,
                monotonic = other.monotonic - self.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other - self.timestamp,
                monotonic = other - self.monotonic
            )
        else:
            return NotImplemented
    
    def __isub__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp -= other.timestamp
            self.monotonic -= other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp -= other
            self.monotonic -= other
            return self
        else:
            return NotImplemented
    
    def __mul__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp * other.timestamp,
                monotonic = self.monotonic * other.monotonic,
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp * other,
                monotonic = self.monotonic * other,
            )
        else:
            return NotImplemented
    
    def __rmul__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp * self.timestamp,
                monotonic = other.monotonic * self.monotonic,
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other * self.timestamp,
                monotonic = other * self.monotonic,
            )
        else:
            return NotImplemented
    
    def __imul__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp *= other.timestamp
            self.monotonic *= other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp *= other
            self.monotonic *= other
            return self
        else:
            return NotImplemented
    
    def __floordiv__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp // other.timestamp,
                monotonic = self.monotonic // other.monotonic,
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp // other,
                monotonic = self.monotonic // other,
            )
        else:
            return NotImplemented
    
    def __truediv__(self, other: TimeStamp | int) -> TimeStamp:
        return NotImplemented
    
    def __rtruediv__(self, other: TimeStamp | int) -> TimeStamp:
        return NotImplemented
    
    def __rfloordiv__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp // self.timestamp,
                monotonic = other.monotonic // self.monotonic,
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other // self.timestamp,
                monotonic = other // self.monotonic,
            )
        else:
            return NotImplemented
    
    def __itruediv__(self, other: TimeStamp | int) -> TimeStamp:
        return NotImplemented
    
    def __ifloordiv__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp //= other.timestamp
            self.monotonic //= other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp //= other
            self.monotonic //= other
            return self
        else:
            return NotImplemented
    
    def __mod__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp % other.timestamp,
                monotonic = self.monotonic % other.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp % other,
                monotonic = self.monotonic % other
            )
        else:
            return NotImplemented
    
    def __rmod__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp % self.timestamp,
                monotonic = other.monotonic % self.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other % self.timestamp,
                monotonic = other % self.monotonic
            )
        else:
            return NotImplemented
    
    def __imod__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp %= other.timestamp
            self.monotonic %= other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp %= other
            self.monotonic %= other
            return self
        else:
            return NotImplemented
    
    def __pow__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = self.timestamp ** other.timestamp,
                monotonic = self.monotonic ** other.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = self.timestamp ** other,
                monotonic = self.monotonic ** other
            )
        else:
            return NotImplemented
    
    def __rpow__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            return TimeStamp(
                timestamp = other.timestamp ** self.timestamp,
                monotonic = other.monotonic ** self.monotonic
            )
        elif isinstance(other, int):
            return TimeStamp(
                timestamp = other ** self.timestamp,
                monotonic = other ** self.monotonic
            )
        else:
            return NotImplemented

    def __ipow__(self, other: TimeStamp | int) -> TimeStamp:
        if isinstance(other, TimeStamp):
            self.timestamp **= other.timestamp
            self.monotonic **= other.monotonic
            return self
        elif isinstance(other, int):
            self.timestamp **= other
            self.monotonic **= other
            return self
    
    def __neg__(self) -> TimeStamp:
        return TimeStamp(
            timestamp = -self.timestamp,
            monotonic = -self.monotonic
        )
    
    def __pos__(self) -> TimeStamp:
        return TimeStamp(
            timestamp = +self.timestamp,
            monotonic = +self.monotonic
        )
    
    def __abs__(self) -> TimeStamp:
        return TimeStamp(
            timestamp = abs(self.timestamp),
            monotonic = abs(self.monotonic)
        )
    
    def __eq__(self, other: TimeStamp) -> bool:
        return self.timestamp == other.timestamp and self.monotonic == other.monotonic
    
    def __ne__(self, other: TimeStamp) -> bool:
        return self.timestamp != other.timestamp or self.monotonic != other.monotonic
    
    def __hash__(self) -> int:
        return hash((self.timestamp, self.monotonic))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.timestamp}, {self.monotonic})"