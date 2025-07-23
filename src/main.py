from sortedcontainers import SortedSet
import re
import argparse
import os
import sys
import spacy
from collections import defaultdict
import re
import time
import queue
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from src.perf import Stopwatch
from src.lang.de import separable_prefixes


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
    with Stopwatch(f"Extraction of '{file_path}'"):
        nlp = spacy.load("de_core_news_sm")

        excludes = load_organize_excluded_lemmas(args)

        text_lemmas = SortedSet()
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                # ignore comments links and very short lines
                if line.startswith("#") or line.startswith("https://") or len(line) < 4:
                    continue
                line_lemmas = extract_lemmas(line, nlp)
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
        default=2,
        help="how many translation per word from dict.cc dictionary.",
    )

    parser.add_argument(
        "--organize-excludes", action=argparse.BooleanOptionalAction, default=False
    )

    parser.add_argument(
        "-d",
        "--dictionary",
        type=str,
        default="dict_cc_de_en.txt",
        help="dictionary for DE_EN from dict.cc",
    )

    parsed_args = parser.parse_args(args)

    # Validate file paths
    validate_path(parsed_args.input)
    validate_path(parsed_args.dictionary)
    if parsed_args.exclude != "":
        validate_path(parsed_args.exclude)

    return parsed_args


def extract_lemmas(sentence, nlp):
    """Extract lemmas from sentence

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
        # print("DEBUG token:", token.text, token.lemma_, token.pos_)
        if token.pos_ in ("VERB", "ADV", "ADJ"):
            lemmas.add(token_lemma)
        elif token.pos_ == "NOUN":
            lemmas.add(token_lemma.capitalize())

        # Find separable verbs
        if token.text in separable_prefixes:
            head = token.head
            if head.pos_ == "VERB":
                head_lemma = head.lemma_.lower()
                separable_tokens.add(token_lemma)
                separable_tokens.add(head_lemma)
                lemmas.add(f"{token_lemma}{head_lemma}")

    # print(separable_tokens)
    return lemmas - separable_tokens


def load_dictionary(file_path):
    """Read dict.cc dictionary for DE-EN

    Args:
        file_path (sts): File to dict.cc dictionary text

    Returns:
        dict: dictionary[word] containing list of EN translation
    """
    with Stopwatch("Load dictionary"):
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
                translation = parts[1]
                pos = parts[2]
                if pos in ("noun", "verb"):
                    pos = pos[0]
                if pos != "n":
                    translation = f"{translation} {pos}."

                # move gender to translation
                if pos == "n":
                    # match for noun gender
                    match = re.match(r"^(.*)\{(\w+)\}", word_def)
                    if match:
                        word_def = match.group(1).strip()
                        gender = match.group(2).strip()
                        translation = f"{gender}. {translation}"

                dictcc_dictionary[word_def].append(translation)
    return dictcc_dictionary


def load_organize_excluded_lemmas(args):
    """Load excluded lemmas path, may reorganize the exclude file if flagged"""
    if args.exclude == "":
        return SortedSet()
    excluded_lemmas = read_word_set(args.exclude)
    if args.organize_excludes:
        write_lines_to_file(excluded_lemmas, args.exclude)
    print(f"Found {len(excluded_lemmas)} excluded lemmas in '{args.exclude}'")
    return excluded_lemmas


def validate_path(path):
    """Check the path really exists"""
    if not os.path.isfile(path):
        print(f"Error! File not found '{path}'")
        sys.exit(1)


def main(args=None):
    """Main function, accepts CLI args"""
    args = parse_args(args)

    with ProcessPoolExecutor() as executor:
        # Load dictionary in parallel, slow ~4s
        future_dict = executor.submit(load_dictionary, args.dictionary)

        lemmas = read_file_extract_lemmas(args)

        dictionary = future_dict.result()

    translated = SortedSet(
        [
            f"{lemma}: {', '.join(dictionary[lemma][:args.number])}"
            for lemma in lemmas
            if lemma in dictionary
        ]
    )

    # sectioning by initials
    initials = SortedSet(map(lambda x: f"{x[0]} ---- {x[0]} ----", translated))
    sectioned = SortedSet(translated)
    sectioned.update(initials)

    print(f"Write translated lemmas '{args.output}' with size: {len(translated)}")
    write_lines_to_file(sectioned, args.output)


if __name__ == "__main__":
    main()
