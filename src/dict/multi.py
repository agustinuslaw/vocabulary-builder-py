import argostranslate.package
import argostranslate.translate
from src.dict import Dictionary
from typing import Iterable


class CoalesceDict(Dictionary):
    """This dictionary uses several other dictionaries in sequence"""

    def __init__(self, dicts: Iterable[Dictionary]):
        self.dicts = dicts
    
    def translate(self, text):
        """Translate text"""
        for dictionary in self.dicts:
            result = dictionary.translate(text)
            if result is not None and result != '':
                return result
        return None    
        
        
class AppendDict(Dictionary):
    """This dictionary uses several other dictionaries in sequence"""

    def __init__(self, dicts: Iterable[Dictionary], sep: str = ', '):
        self.dicts = dicts
        self.sep = sep
    
    def translate(self, text):
        """Translate text"""
        results = set()
        for dictionary in self.dicts:
            result = dictionary.translate(text)
            if result is not None and result != '':
                results.update(result.lower().split(', '))
        return self.sep.join(results)    