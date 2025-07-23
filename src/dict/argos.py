import argostranslate.package
import argostranslate.translate
from src.perf import Stopwatch

def init_argos(from_code, to_code):
    with Stopwatch(f"Init argostranslate {from_code}-{to_code}"):
        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages,
            )
        )
        package_to_install_download = package_to_install.download()
        argostranslate.package.install_from_path(package_to_install_download)


def translate(text, from_code, to_code):
    return argostranslate.translate.translate(
        text, from_code, to_code
    )

if __name__ == "__main__":
    init_argos("de", "en")
    translatedText = argostranslate.translate.translate(
        "Hello World", "de", "en"
    )
    print(translatedText)
    # '¡Hola Mundo!'
