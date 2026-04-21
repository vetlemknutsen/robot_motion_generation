from abc import ABC, abstractmethod
from pathlib import Path

from motion_pipeline.core.task_level import TaskDescription


class Adapter(ABC):
    """
    Base class for input adapters.

    Subclass this and implement to_taskdescription() to add a new input format.
    See JsonScenarioAdapter and MediaPipeCSVAdapter for examples.
    """
    @abstractmethod
    def to_taskdescription(self, source: Path) -> TaskDescription:
        """Parse the input file from source and return a TaskDescription."""
        ...
