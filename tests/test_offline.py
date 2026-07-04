import tempfile
import unittest
from pathlib import Path

from ttr.cache import TranslationCache
from ttr.config import CacheConfig, Config
from ttr.errors import BackendError
from ttr.glossary import Glossary, GlossaryEntry
from ttr.lang import LangPair
from ttr.translator import TranslateOptions, Translator


class OfflineTests(unittest.TestCase):
    def test_offline_uses_cache_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "repository", "cached repo", "mymemory")
            glossary = Glossary((GlossaryEntry("en", "zh", "repository", "仓库"),))
            translator = Translator(Config(), cache=cache, glossary=glossary)

            result = translator.translate(
                "repository",
                LangPair("en", "zh"),
                TranslateOptions(offline=True),
            )

            self.assertEqual(result.text, "cached repo")
            self.assertEqual(result.backend, "mymemory")
            self.assertTrue(result.cached)

    def test_offline_uses_glossary_after_cache_miss(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            glossary = Glossary((GlossaryEntry("en", "zh", "repository", "仓库"),))
            translator = Translator(Config(), cache=cache, glossary=glossary)

            result = translator.translate(
                "repository",
                LangPair("en", "zh"),
                TranslateOptions(offline=True),
            )

            self.assertEqual(result.text, "仓库")
            self.assertEqual(result.backend, "glossary")

    def test_cache_disabled_makes_offline_glossary_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "repository", "cached repo", "mymemory")
            glossary = Glossary((GlossaryEntry("en", "zh", "repository", "仓库"),))
            translator = Translator(Config(cache=CacheConfig(enabled=False)), cache=cache, glossary=glossary)

            result = translator.translate(
                "repository",
                LangPair("en", "zh"),
                TranslateOptions(offline=True, cache_enabled=False),
            )

            self.assertEqual(result.text, "仓库")
            self.assertEqual(result.backend, "glossary")

    def test_offline_miss_errors_without_backend_request(self):
        translator = Translator(Config(), glossary=Glossary())

        with self.assertRaisesRegex(BackendError, "offline miss"):
            translator.translate("unknown", LangPair("en", "zh"), TranslateOptions(offline=True))


if __name__ == "__main__":
    unittest.main()

