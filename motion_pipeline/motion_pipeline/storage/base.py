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
        """Save a new motion. Returns nothing."""
        ...

    @abstractmethod
    def delete(self, id: int) -> None:
        """Delete the motion with the given id."""
        ...

    @abstractmethod
    def get(self, id: int) -> Optional[Tuple]:
        """Return one motion as a tuple, or None if not found."""
        ...

    @abstractmethod
    def get_all(self) -> List[Tuple]:
        """Return every stored motion as a list of tuples."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Close the underlying connection."""
        ...
