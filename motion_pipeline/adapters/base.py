from abc import ABC, abstractmethod
from typing import Any

from motion_pipeline.core.schema import Program


class Adapter(ABC):
    @abstractmethod
    def to_program(self, source: Any) -> Program:
        ...
