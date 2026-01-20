from abc import ABC, abstractmethod
from typing import Any

from motion_pipeline.core.task_level import Motion


class Adapter(ABC):
    @abstractmethod
    def to_motion(self, source: Any) -> Motion:
        ...
