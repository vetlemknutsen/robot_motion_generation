from abc import ABC, abstractmethod
from pathlib import Path

from motion_pipeline.types.TaskDescription import TaskDescription

# registry of all adapters. Keys are short names like "json" or "mediapipecsv
# The pipeline looks adapters up here by key
ADAPTERS: dict[str, type["Adapter"]] = {}


# decorator. Put @register_adapter("your_key") on top of Adapter subclass
# and it gets added to the registry automatically
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
        """Parse an input file and return a TaskDescription.
        Subclasses implement this to support new input formats. The output
        is robot-independent, the pipeline runs IK afterwards.
        Args:
            source: Path to the input file.
        Returns:
            A TaskDescription containing the parsed frames.
        """
        ...
