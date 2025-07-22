import unittest
from src.main import parse_args, main, validate_path
import os


class TestMain(unittest.TestCase):
    def test_args(self):
        """Test argument parsing"""
        args = parse_args(
            [
                "-d",
                "dict_cc_de_en.txt",
                "-o",
                "test/vocab1.txt",
                "-i",
                "test/sample1.txt",
                "-e",
                "test/exclude1.txt",
            ]
        )
        self.assertEqual("dict_cc_de_en.txt", args.dictionary)
        self.assertEqual("test/vocab1.txt", args.output)
        self.assertEqual("test/exclude1.txt", args.exclude)

    def test_args_no_exclude(self):
        """Test argument parsing without optional exclude"""
        args = parse_args(
            [
                "-d",
                "dict_cc_de_en.txt",
                "-o",
                "test/vocab1.txt",
                "-i",
                "test/sample1.txt",
            ]
        )
        self.assertEqual("dict_cc_de_en.txt", args.dictionary)
        self.assertEqual("test/vocab1.txt", args.output)
        self.assertEqual("", args.exclude)

    def test_main(self):
        """Test main creates vocab file with the right content"""
        output = "test/vocab1.txt"
        main(
            [
                "-d",
                "dict_cc_de_en.txt",
                "-o",
                output,
                "-i",
                "test/sample1.txt",
                "-e",
                "test/exclude1.txt",
            ]
        )
        validate_path(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should be contained with proper translation
        self.assertRegex(content, r"Arzt.*doctor")
        self.assertRegex(content, r"Ohr.*ear")
        # Should be excluded
        self.assertFalse("Konsol" in content)
        self.assertFalse("vielleicht" in content)
        os.remove(output)


if __name__ == "__main__":
    unittest.main()
