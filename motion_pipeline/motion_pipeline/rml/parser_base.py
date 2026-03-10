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
        """Parse RML text and return a JSON dict."""
        ...
