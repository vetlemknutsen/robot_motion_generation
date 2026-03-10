from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

"""
Abstract base class for motion storage backends

Subclass this to add a new storage backend
See SQLiteMotionStore for an example.
"""

class MotionStore(ABC):
    @abstractmethod
    def insert(self, name: str, robot: str, rml: str) -> None:
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        ...

    @abstractmethod
    def get(self, id: int) -> Optional[Tuple]:
        ...

    @abstractmethod
    def get_all(self) -> List[Tuple]:
        ...

    @abstractmethod
    def close(self) -> None:
        ...
