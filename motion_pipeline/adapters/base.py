from abc import ABC, abstractmethod
from typing import Any

from motion_pipeline.core.task_spec import MotionDirective


class Adapter(ABC):
    @abstractmethod
    def to_directive(self, source: Any) -> MotionDirective:
        ...
