from src.perf import Stopwatch


def init(from_code, to_code):
    with Stopwatch(f"Init dictcc {from_code}-{to_code}"):
        return None


def translate(text, from_code, to_code):
    return None