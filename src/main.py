import argparse
import os
from concurrent.futures import ProcessPoolExecutor
import re
import spacy
from sortedcontainers import SortedSet

from src.perf import Stopwatch
from src.lang.de import separable_prefixes
from src.dict.dictcc import DictCCDict
from src.dict.argos import ArgosDict
from src.dict import Dictionary
from src.dict.multi import CoalesceDict, AppendDict

def read_word_set(file_path):
    """Reads the word exclusion or other wordlist file."""
    words = SortedSet()
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # ignore comments links and very short lines
            if line.startswith("#"):
                continue
            # remove whitespace
            word = line.strip()
            words.add(word)
    return words


def read_file_extract_lemmas(args):
    """Reads the file and extract lemmas in the text. Separable verbs already combined."""
    file_path = args.input
    included_pos = tuple(e.strip() for e in args.part_of_speech.split(","))
    with Stopwatch(f"Extraction of '{file_path}'"):
        nlp = spacy.load("de_core_news_sm")

        excludes = load_organize_excluded_lemmas(args.exclude, args.organize_excludes)

        text_lemmas = SortedSet()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # ignore comments links and very short lines
                if line.startswith("#") or line.startswith("https://") or len(line) < 4:
                    continue
                line_lemmas = extract_de_lemmas(line, nlp, included_pos)
                text_lemmas.update(line_lemmas)
        print(f"Found {len(text_lemmas)} lemmas in text '{file_path}'")

    if len(excludes) > 0:
        filtered = text_lemmas - excludes
        print(f"Found {len(filtered)} lemmas after removing excluded lemmas")
        return filtered
    return text_lemmas


def write_lines_to_file(lines, file_path: str):
    """Writes each line from the set to the file, one per line."""
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line + "\n")


def parse_args(args=None):
    """Parse arguments from CLI"""
    parser = argparse.ArgumentParser(
        prog="VocabularyBuilder",
        description="Process German text files to get vocabulary list. Requires offline dict.cc dictionary text. See https://www1.dict.cc/translation_file_request.php",
    )

    parser.add_argument("-i", "--input", type=str, help="path to input text file.")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="vocabulary.txt",
        help="path to output text file.",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        default="",
        help="optional path to word exclusion file text, words are separated by new line.",
    )

    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=3,
        help="how many translation per word from dict.cc dictionary.",
    )

    parser.add_argument(
        "--organize-excludes", action=argparse.BooleanOptionalAction, default=False
    )

    parser.add_argument(
        "-d",
        "--dictcc-file",
        type=str,
        help="dictionary for DE_EN from dict.cc"
    )

    parser.add_argument(
        "-m",
        "--method",
        type=str,
        default="coalesce",
        choices=("dictcc", "argos", "coalesce", "append"),
        help="method determines the translation method. dict_cc is an offline tabular dictionary, argos is a neural network, serial defaults to dict_cc then argos"
    )

    parser.add_argument(
        "-f",
        "--from-lang",
        type=str,
        default="de",
        help="argostranslate from-language code e.g. 'de'",
    )

    parser.add_argument(
        "-t",
        "--to-lang",
        type=str,
        default="en",
        help="argostranslate to-language code e.g. 'en'",
    )

    parser.add_argument(
        "-pos",
        "--part-of-speech",
        type=str,
        default="VERB,NOUN,ADJ,ADV",
        help="Available: VERB,NOUN,ADJ,ADV,PROPN,AUX,ADP,SYM,NUM",
    )

    parsed_args = parser.parse_args(args)
    
    # Validate args
    print(f'Method: {parsed_args.method}')
    print(f'Input: {parsed_args.input}')
    print(f'Output: {parsed_args.output}')
    print(f'POS: {parsed_args.part_of_speech}')
    
    validate_path(parsed_args.input)
    method = parsed_args.method
    if method in ("dictcc", "coalesce", "append"):
        validate_exist(parsed_args.dictcc_file, f'Missing dictcc_file for method {method}')
        validate_path(parsed_args.dictcc_file)
        validate_exist(parsed_args.number, f'Missing number for method {method}')
    if method in ("argos", "coalesce", "append"):
        validate_exist(parsed_args.from_lang, f'Missing from_lang for method {method}')
        validate_exist(parsed_args.to_lang, f'Missing to_lang for method {method}')

    if parsed_args.exclude != "":
        validate_path(parsed_args.exclude)

    return parsed_args


def extract_de_lemmas(sentence, nlp, included_pos):
    """Extract German (DE) lemmas from sentence

    Args:
        sentence (str): Textual sentence

    Returns:
        SortedSet: Sorted lemmas
    """
    tokens = nlp(sentence)
    lemmas = SortedSet()
    separable_tokens = SortedSet()
    
    for token in tokens:
        token_lemma = token.lemma_.lower()
        # https://spacy.io/usage/linguistic-features
        # POS, PROPN, AUX, VERB, ADP, VERB, PROPN, NOUN, ADP, SYM, NUM
        token_pos = token.pos_
        # filter part of speech
        if token_pos not in included_pos:
            continue
        # filter words that dont start with unicode char
        if re.match(r'^[^\d\W].*', token.text) is None:
            continue
        if token_pos != "NOUN":
            lemmas.add(token_lemma)
        elif token_pos == "NOUN":
            # German specific logic, nouns are capitalized
            lemmas.add(token_lemma.capitalize())
        
        # German specific logic, find separable verbs
        if token.text in separable_prefixes:
            head = token.head
            if head.pos_ == "VERB":
                head_lemma = head.lemma_.lower()
                separable_tokens.add(token_lemma)
                separable_tokens.add(head_lemma)
                lemmas.add(f"{token_lemma}{head_lemma}")

    # print(separable_tokens)
    return lemmas - separable_tokens


def load_organize_excluded_lemmas(exclude_file, flag_organize_excludes):
    """Load excluded lemmas path, may reorganize the exclude file if flagged"""
    if exclude_file == "":
        return SortedSet()
    excluded_lemmas = read_word_set(exclude_file)
    if flag_organize_excludes:
        write_lines_to_file(excluded_lemmas, exclude_file)
    print(f"Found {len(excluded_lemmas)} excluded lemmas in '{exclude_file}'")
    return excluded_lemmas


def validate_path(path):
    """Check the path really exists"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Error! File not found '{path}'")


def validate(expr: bool, message: str):
    """Check expr is true"""
    if not expr:
        raise ValueError(message)


def validate_exist(value: str, message: str):
    """Check expr is true"""
    if not (value is not None or value != ''):
        raise ValueError(message)
    


def main(args=None):
    """Main function, accepts CLI args"""
    args = parse_args(args)

    with ProcessPoolExecutor() as executor:
        method = args.method
        
        # future_lemmas = executor.submit(read_file_extract_lemmas, args)

        futures = []
        # ordering matters, dict_cc is added first
        if method in ("dictcc" , "coalesce", "append"):
            future_dictcc = executor.submit(DictCCDict, args.dictcc_file, args.number)
            futures.append(future_dictcc)
        if method in ("argos" , "coalesce", "append"):
            future_argos = executor.submit(ArgosDict, args.from_lang, args.to_lang)
            futures.append(future_argos)
        
        validate(len(futures) > 0, f"Unsupported dictionary method: {method}")
        
        lemmas = read_file_extract_lemmas(args)
        if method == "coalesce":
            # preserve task ordering
            dictionary: Dictionary = CoalesceDict([f.result() for f in futures])
        elif method == "append":
            # preserve task ordering
            dictionary: Dictionary = AppendDict([f.result() for f in futures])
        else:
            dictionary: Dictionary = futures[0].result()
    
    print("Begin translation")
    with Stopwatch("Translation"):
        translated = SortedSet([f"{x}: {dictionary.translate(x)}" for x in lemmas])

    # sectioning by initials
    initials = SortedSet(map(lambda x: f"{x[0]} ---- {x[0]} ----", translated))
    sectioned = SortedSet(translated)
    sectioned.update(initials)

    print(f"Write translated lemmas '{args.output}' with size: {len(translated)}")
    write_lines_to_file(sectioned, args.output)


if __name__ == "__main__":
    main()
