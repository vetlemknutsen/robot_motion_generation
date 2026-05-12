from abc import ABC, abstractmethod
from pathlib import Path

from motion_pipeline.types.TaskDescription import TaskDescription

ADAPTERS: dict[str, type["Adapter"]] = {}

def register_adapter(key: str):
    def decorator(cls):
        ADAPTERS[key] = cls
        return cls
    return decorator


class Adapter(ABC):
    """
    Base class for input adapters.

    Subclass this, decorate with @register_adapter("key"), and implement to_taskdescription() to add a new input format.
    See SimpleJSONAdapter and MediaPipeCSVAdapter for examples.
    """
    @abstractmethod
    def to_taskdescription(self, source: Path) -> TaskDescription:
        """Parse the input file from source and return a TaskDescription."""
        ...
