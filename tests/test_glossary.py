import tempfile
import unittest
from pathlib import Path

from ttr.glossary import Glossary, GlossaryEntry


class GlossaryTests(unittest.TestCase):
    def test_loads_exact_terms(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "glossary.tsv"
            path.write_text("en\tzh\trepository\t仓库\n", encoding="utf-8")

            glossary = Glossary.load(path)

            self.assertEqual(glossary.translate_exact("en", "zh", "repository"), "仓库")

    def test_applies_terms_inside_text(self):
        glossary = Glossary((GlossaryEntry("en", "zh", "cache", "缓存"),))

        self.assertEqual(glossary.apply_terms("en", "zh", "cache miss"), "缓存 miss")


if __name__ == "__main__":
    unittest.main()

