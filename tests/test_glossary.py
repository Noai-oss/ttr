import tempfile
import unittest
from pathlib import Path

from ttr.errors import TTRError
from ttr.glossary import Glossary, GlossaryEntry


class GlossaryTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = root / "glossary.tsv"

    def test_loads_utf8_with_or_without_bom(self):
        for encoding in ("utf-8", "utf-8-sig"):
            with self.subTest(encoding=encoding):
                self.path.write_text("en\tzh\trepository\t仓库\n", encoding=encoding)
                glossary = Glossary.load(self.path)
                self.assertEqual(glossary.translate_exact("en", "zh", "repository"), "仓库")

    def test_only_matches_complete_text(self):
        glossary = Glossary((GlossaryEntry("en", "zh", "cache", "缓存"),))

        self.assertIsNone(glossary.translate_exact("en", "zh", "cache miss"))

    def test_invalid_row_reports_file_and_line(self):
        self.path.write_text("# comment\nen\tzh\tmissing translation\n", encoding="utf-8")
        with self.assertRaisesRegex(TTRError, r"glossary.tsv:2"):
            Glossary.load(self.path)

    def test_invalid_encoding_reports_file(self):
        self.path.write_bytes(b"\xff\xfe")
        with self.assertRaisesRegex(TTRError, "cannot read glossary"):
            Glossary.load(self.path)

    def test_invalid_language_reports_file_and_line(self):
        self.path.write_text("en zh\tzh\tcache\t缓存\n", encoding="utf-8")
        with self.assertRaisesRegex(TTRError, r"glossary.tsv:1: invalid language"):
            Glossary.load(self.path)


if __name__ == "__main__":
    unittest.main()
