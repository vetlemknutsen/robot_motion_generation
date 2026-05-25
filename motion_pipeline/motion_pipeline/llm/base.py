from abc import ABC, abstractmethod


class Labeler(ABC):
    """
    Base class for output labelers.

    Subclass this and implement label_code() to add a new labeler
    See LLMLabeler for an example.
    """
    @abstractmethod
    def label_code(self, rml_text: str, robot_key: str) -> str:
        """Add intent labels to an RML program.
        Subclasses implement this to annotate RML with high-level intent
        comments (reach, grab, release, ...). Implementations should
        return the original text unchanged on failure rather than raise.
        Args:
            rml_text: The RML program to label.
            robot_key: Robot identifier, used to give the labeler robot-
                specific context (e.g. how the gripper is closed).
        Returns:
            The labeled RML text.
        """
        ...