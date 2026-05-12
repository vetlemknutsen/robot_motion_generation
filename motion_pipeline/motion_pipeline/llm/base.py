from abc import ABC, abstractmethod


class Labeler(ABC):
    """
    Base class for output labelers.

    Subclass this and implement label_code() to add a new labeler
    See LLMLabeler for an example.
    """
    @abstractmethod
    def label_code(self, rml_text: str, robot_key: str) -> str:
        """Annotate the given RML text and return the labeled RML."""
        ...