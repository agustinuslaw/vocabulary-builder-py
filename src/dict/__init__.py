from typing import Protocol

class Dictionary(Protocol):
    """Dictionary protocol """
    def translate(self, text: str) -> str:
        """Dictionary must translate text"""
