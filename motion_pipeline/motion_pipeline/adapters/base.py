from abc import ABC, abstractmethod
from pathlib import Path

from motion_pipeline.core.task_level import Motion


class Adapter(ABC):
    """
    Base class for input adapters.

    Subclass this and implement to_motion() to add a new input format.
    See JsonScenarioAdapter and MediaPipeCSVAdapter for examples.
    """
    @abstractmethod
    def to_motion(self, source: Path) -> Motion:
        """Parse the input file from source and return a Motion."""
        ...
