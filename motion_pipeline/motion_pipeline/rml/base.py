from abc import ABC, abstractmethod
from motion_pipeline.core.joint_level import Program
    
"""
Abstract base class for output emitters

Subclass this and implement emit() to add a new output format
See BasicRMLEmitter for an example
"""
class Emitter(ABC):
    @abstractmethod
    def emit(self, program: Program) -> str:
        """Convert a Program to an output string."""
        ...
