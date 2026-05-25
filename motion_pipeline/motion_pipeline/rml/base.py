from abc import ABC, abstractmethod
from motion_pipeline.types.JointDescription import JointDescription
    
"""
Abstract base class for output emitters

Subclass this and implement emit() to add a new output format
See BasicRMLEmitter for an example
"""
class Emitter(ABC):
    @abstractmethod
    def emit(self, program: JointDescription) -> str:
        """Render a joint-space program as output text.
        Subclasses implement this to support new output formats, (swapping RML with something else)
        Args:
            program: The JointDescription to render.
        Returns:
            The rendered text.
        """
        ...
