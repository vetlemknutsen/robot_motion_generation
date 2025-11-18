from abc import ABC, abstractmethod
from typing import Any

from motion_pipeline.core.motion import MotionSequence


class Adapter(ABC):
    @abstractmethod
    def to_motion(self, source: Any) -> MotionSequence:
        ...
