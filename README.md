# README

From a text file generate a vocabulary list. If translation is possible, then the list will also contain translation.

## Requires

- Python 3.11.9 
  - Due to sentencepie==2.0.0 
- Dictionary downloaded from dict.cc (see https://www1.dict.cc/translation_file_request.php?l=e)

## Setup Windows

```
cd {root project}
py -3.11.9 -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Setup Unix

```
cd {root project}
py -3.11.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage 

- Do setup for your OS
- Remember to activate venv

Examples below in Powershell.

To get help use `--help`.
```powershell
(venv) PS workspace\vocabulary-builder-py> py -m src.main -h
usage: VocabularyBuilder [-h] [-i INPUT] [-o OUTPUT] [-e EXCLUDE] [-n NUMBER] [--organize-excludes | --no-organize-excludes] [-d DICTIONARY]

Process German text files to get vocabulary list. Requires offline dict.cc dictionary text. See
https://www1.dict.cc/translation_file_request.php

options:
  -h, --help            show this help message and exit
  -i, --input INPUT     path to input text file.
  -o, --output OUTPUT   path to output text file.
  -e, --exclude EXCLUDE
                        optional path to word exclusion file text, words are separated by new line.
  -n, --number NUMBER   how many translation per word from dict.cc dictionary.
  --organize-excludes, --no-organize-excludes
  -d, --dictionary DICTIONARY
                        dictionary for DE_EN from dict.cc
```

Example usage with excludes
```powershell
(venv) PS workspace\vocabulary-builder-py> py -m src.main -d dict_cc_de_en.txt -i german_novel_ch2.txt -o vocabulary.txt -e excludes.txt
Found 539 excluded lemmas in 'excludes.txt'
Found 890 lemmas in text 'german_novel_ch2.txt'
Extraction of 'german_novel_ch2.txt' elapsed: 2.33 seconds
Found 559 lemmas after removing excluded lemmas
Load dictionary elapsed: 5.41 seconds
Write translated lemmas 'vocabulary.txt' with size: 353
```

Example usage without excludes
```powershell
(venv) PS workspace\vocabulary-builder-py> py src\main.py -d dict_cc_de_en.txt -i german_novel_ch2.txt -o vocabulary.txt
Found 890 lemmas in text 'german_novel_ch2.txt'
Extraction of 'german_novel_ch2.txt' elapsed: 2.28 seconds
Load dictionary elapsed: 4.57 seconds
Write translated lemmas 'vocabulary.txt' with size: 634
```

## Testing

Go to root project and run `test.test_main`
```powershell
(venv) PS workspace\vocabulary-builder-py> py -m unittest test.test_main
```