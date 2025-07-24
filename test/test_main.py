import unittest
from src.main import parse_args, main, validate_path
import os
from src.perf import Stopwatch

class TestMain(unittest.TestCase):
    def test_args(self):
        """Test argument parsing"""
        args = parse_args(
            [
                "-m",
                "dictcc",
                "-d",
                "dictcc/de_en.txt",
                "-o",
                "test/vocab1.txt",
                "-i",
                "test/sample1.txt",
                "-e",
                "test/exclude1.txt",
            ]
        )
        self.assertEqual("dictcc/de_en.txt", args.dictcc_file)
        self.assertEqual("test/vocab1.txt", args.output)
        self.assertEqual("test/exclude1.txt", args.exclude)

    def test_args_no_exclude(self):
        """Test argument parsing without optional exclude"""
        args = parse_args(
            [
                "-m",
                "dictcc",
                "-d",
                "dictcc/de_en.txt",
                "-o",
                "test/vocab1.txt",
                "-i",
                "test/sample1.txt",
            ]
        )
        self.assertEqual("dictcc/de_en.txt", args.dictcc_file)
        self.assertEqual("test/vocab1.txt", args.output)
        self.assertEqual("", args.exclude)

    def test_args_argos(self):
            args = parse_args(
            [
                "-m",
                "argos",
                "-d",
                "dictcc/de_en.txt",
                "-o",
                "test/vocab1.txt",
                "-i",
                "test/sample1.txt",
            ]
        )

    def test_create_vocab_dictcc(self):
        """Test main creates vocab file with the right content"""
        output = "test/vocab_dictcc.txt"
        main(
            [
                "-m",
                "dictcc",
                "-i",
                "test/sample1.txt",
                "-o",
                output,
                "-e",
                "test/exclude1.txt",
                "-d",
                "test/de_en.txt"
            ]
        )
        validate_path(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should be contained with proper translation
        self.assertRegex(content, r"Arzt.*[Dd]octor")
        self.assertRegex(content, r"Ohr.*[Ee]ar")
        # Should be excluded
        self.assertFalse("Konsol" in content)
        self.assertFalse("vielleicht" in content)
        os.remove(output)

    def test_create_vocab_argos(self):
        """Test main creates vocab file with the right content"""
        output = "test/vocab_argos.txt"
        main(
            [
                "-m",
                "argos",
                "-i",
                "test/sample1.txt",
                "-o",
                output,
                "-e",
                "test/exclude1.txt"
            ]
        )
        validate_path(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should be contained with proper translation
        self.assertRegex(content, r"Arzt.*[Dd]octor")
        self.assertRegex(content, r"Ohr.*[Ee]ar")
        # Should be excluded
        self.assertFalse("Konsol" in content)
        self.assertFalse("vielleicht" in content)
        os.remove(output)

    def test_create_vocab_coalesce(self):
        """Test main creates vocab file with the right content"""
        output = "test/vocab_coalesce.txt"
        main(
            [
                "-m",
                "coalesce",
                "-i",
                "test/sample1.txt",
                "-o",
                output,
                "-e",
                "test/exclude1.txt",
                "-d",
                "test/de_en.txt"
            ]
        )
        validate_path(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should be contained with proper translation
        self.assertRegex(content, r"Arzt.*[Dd]octor")
        self.assertRegex(content, r"Ohr.*[Ee]ar")
        # Should be excluded
        self.assertFalse("Konsol" in content)
        self.assertFalse("vielleicht" in content)
        os.remove(output)

    def test_create_vocab_append(self):
        """Test main creates vocab file with the right content"""
        output = "test/vocab_append.txt"
        main(
            [
                "-m",
                "append",
                "-i",
                "test/sample1.txt",
                "-o",
                output,
                "-e",
                "test/exclude1.txt",
                "-d",
                "test/de_en.txt"
            ]
        )
        validate_path(output)
        with open(output, "r", encoding="utf-8") as f:
            content = f.read()
        # Should be contained with proper translation
        self.assertRegex(content, r"Arzt.*[Dd]octor")
        self.assertRegex(content, r"Ohr.*[Ee]ar")
        # Should be excluded
        self.assertFalse("Konsol" in content)
        self.assertFalse("vielleicht" in content)
        os.remove(output)

if __name__ == "__main__":
    unittest.main()
