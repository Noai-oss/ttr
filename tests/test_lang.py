import unittest

from ttr.lang import parse_lang_spec


class LangTests(unittest.TestCase):
    def test_parse_full_pair(self):
        pair = parse_lang_spec("en:zh")
        self.assertEqual(pair.source, "en")
        self.assertEqual(pair.target, "zh")

    def test_parse_target_only_from_default_source(self):
        pair = parse_lang_spec(":zh", default_source="en", default_target="ja")
        self.assertEqual(pair.source, "en")
        self.assertEqual(pair.target, "zh")

    def test_parse_source_only_from_default_target(self):
        pair = parse_lang_spec("zh:", default_source="en", default_target="en")
        self.assertEqual(pair.source, "zh")
        self.assertEqual(pair.target, "en")

    def test_parse_missing_pair_from_defaults(self):
        pair = parse_lang_spec(None, default_source="en", default_target="zh")
        self.assertEqual(pair.source, "en")
        self.assertEqual(pair.target, "zh")

    def test_missing_source_errors(self):
        with self.assertRaises(ValueError):
            parse_lang_spec(":zh", default_source=None, default_target="en")

    def test_missing_target_errors(self):
        with self.assertRaises(ValueError):
            parse_lang_spec("zh:", default_source="en", default_target=None)

    def test_auto_and_invalid_configured_languages_are_rejected(self):
        for source in ("auto", "en zh", "en:", "en--us"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                parse_lang_spec(None, default_source=source, default_target="zh")


if __name__ == "__main__":
    unittest.main()
