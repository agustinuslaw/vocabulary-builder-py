import re
from collections import defaultdict

from src.dict import Dictionary
from src.perf import Stopwatch

class DictCCToken:
    """This class measures elapsed time from enter to exit in seconds"""

    def __init__(self, word:str, translation:str, pos:str, gender:str|None, tags:str|None):
        self.word = word
        self.translation = translation
        self.pos = pos
        self.tags = tags
        self.gender = gender

def remove_square_content(text):
    return re.sub(r"\[([^\]]+)\]", "", text)

def remove_gender(text):
    return re.sub(r" {0,1}\{([fmnpl]{1,2})\}", "", text)


def extract_gender(word, pos):
    if pos != "noun":
        return word, None
    # match for noun gender {m} {f} {n} {pl}
    match = re.search(r"\{([fmnpl]{1,2})\}", word)
    if match:
        gender = match.group(1)
        word = remove_gender(word)
        return word, gender
    return word, None

class DictCCDict(Dictionary):
    """Represent an offline dict.cc single word dictionary. Downloadable for free."""
    def __init__(self, file_path: str, number: int=1):
        self.number = number
        with Stopwatch(f"DictCC load '{file_path}'"):
            self.dictionary = self.load_dictionary(file_path)
            
    def load_dictionary(self, file_path: str) -> defaultdict[str, list[DictCCToken]]:
        """Read dict.cc dictionary for DE-EN

        Args:
            file_path (sts): File to dict.cc dictionary text

        Returns:
            dict: dictionary[word] containing list of EN translation
        """
        # dict.cc dictionary structure
        dictcc_dictionary: defaultdict[str, list[DictCCToken]] = defaultdict(list)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Split into: word, translation, pos
                parts = [e.strip() for e in line.split("\t")]
                if len(parts) < 3:
                    continue

                # Richtlinie {f} zur ... [Markenrichtlinie] [89/104/EEC]
                # Richtkrone {m} [eines Richtfests]
                word = remove_square_content(parts[0])
                translation = remove_square_content(parts[1]).strip()
                pos = parts[2]
                tags = parts[3] if len(parts) > 3 else None
                word, gender = extract_gender(word, pos)
                
                token = DictCCToken(word, translation, pos, gender, tags)

                dictcc_dictionary[word].append(token)
        return dictcc_dictionary

    def translate(self, text: str, num: int = None, sep: str = ', ') -> str:
        """Translate text/lemma with num amount of possible translations. Only works on lemmas not sentences"""
        if num is None:
            num = self.number

        tokens = self.dictionary[text][:num]        
        if len(tokens) == 0:
            return None
        translations = [x.translation for x in tokens]
        first: DictCCToken = tokens[0]
        gender = first.gender
        if gender:
            return gender + ' ' + sep.join(translations)            
        return sep.join(translations)