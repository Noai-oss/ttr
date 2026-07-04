import unittest

from ttr.cli import extract_lang_and_text


class CliTests(unittest.TestCase):
    def test_extract_explicit_lang(self):
        spec, text = extract_lang_and_text(["en:zh", "hello"])
        self.assertEqual(spec, "en:zh")
        self.assertEqual(text, ["hello"])

    def test_extract_target_only_lang(self):
        spec, text = extract_lang_and_text([":zh", "hello"])
        self.assertEqual(spec, ":zh")
        self.assertEqual(text, ["hello"])

    def test_extract_source_only_lang(self):
        spec, text = extract_lang_and_text(["zh:", "你好"])
        self.assertEqual(spec, "zh:")
        self.assertEqual(text, ["你好"])

    def test_extract_default_lang(self):
        spec, text = extract_lang_and_text(["hello"])
        self.assertIsNone(spec)
        self.assertEqual(text, ["hello"])


if __name__ == "__main__":
    unittest.main()

