import re
from src.dict import Dictionary
from src.perf import Stopwatch
from collections import defaultdict

class DictCCDict(Dictionary):
    """Represent an offline dict.cc single word dictionary. Downloadable for free."""
    def __init__(self, file_path: str, number: int=1):
        self.number = number
        with Stopwatch(f"DictCC load '{file_path}'"):
            self.dictionary = self.load_dictionary(file_path)
            
    def load_dictionary(self, file_path: str) -> defaultdict[str, list]:
        """Read dict.cc dictionary for DE-EN

        Args:
            file_path (sts): File to dict.cc dictionary text

        Returns:
            dict: dictionary[word] containing list of EN translation
        """
        # dict.cc dictionary structure
        dictcc_dictionary = defaultdict(list)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # remove tags [...]
                line = re.sub(r"\[([^\]]+)\]", "", line)
                # Split into: word, translation, pos
                parts = line.strip().split("\t")
                if len(parts) < 3:
                    continue

                word_def = parts[0]
                translation = parts[1].strip()
                pos = parts[2]
                if pos in ("noun", "verb"):
                    pos = pos[0]
                # if pos != "n":
                #     translation = f"{translation} {pos}."

                # move gender to translation
                if pos == "n":
                    # match for noun gender
                    match = re.match(r"^(.*)\{(\w+)\}", word_def)
                    if match:
                        word_def = match.group(1).strip()
                        gender = match.group(2).strip()
                        # translation = f"{gender}. {translation}"

                dictcc_dictionary[word_def].append(translation)
        return dictcc_dictionary

    def translate(self, text: str, num: int = None) -> str:
        """Translate text/lemma with num amount of possible translations. Only works on lemmas not sentences"""
        if num is None:
            num = self.number
        return ', '.join(self.dictionary[text][:num])
         