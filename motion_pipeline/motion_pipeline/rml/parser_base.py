from abc import ABC, abstractmethod

"""
Abstract base class for RML text -> JSON conversion.

Subclass this to swap out the Langium-based parser for
another implementation (Python-native, remote service, etc).
See LangiumRMLParser for an example.
"""
class RMLParser(ABC):
    @abstractmethod
    def parse(self, rml_text: str) -> dict:
        """Parse and validate RML text, returning its JSON representation.
        Args:
            rml_text: The RML source as a string.
        Returns:
            A dict matching the RML JSON schema.
        Raises:
            Exception: If the RML is invalid (specific exception type
                depends on the implementation).
        """
        ...
