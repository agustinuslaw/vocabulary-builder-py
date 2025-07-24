import argostranslate.package
import argostranslate.translate
from src.perf import Stopwatch
from src.dict import Dictionary

class ArgosDict(Dictionary):
    """Dictionary using Argostranslate"""

    def __init__(self, from_lang: str, to_lang: str):
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.cache = {}
        self.install(from_lang, to_lang)

    def install(self, from_lang: str, to_lang: str):
        """Download the required package and install"""
        with Stopwatch(f"Install argostranslate {from_lang}-{to_lang}"):
            # Download and install Argos Translate package
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_lang and x.to_code == to_lang,
                    available_packages,
                )
            )
            package_to_install_download = package_to_install.download()
            argostranslate.package.install_from_path(package_to_install_download)

    def translate(self, text):
        """Translate text"""
        cached = self.cache.get(text)
        if cached:
            return cached
        return argostranslate.translate.translate(text, self.from_lang, self.to_lang).strip()


if __name__ == "__main__":
    d = ArgosDict("de", "en")
    translatedText = d.translate("Hallo Welt!")
    print(translatedText)