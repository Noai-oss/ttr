import tempfile
import unittest
from pathlib import Path

from ttr.cache import TranslationCache
from ttr.config import CacheConfig, Config
from ttr.errors import BackendError
from ttr.glossary import Glossary, GlossaryEntry
from ttr.lang import LangPair
from ttr.translator import Translator


class OfflineTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.cache = TranslationCache(root / "cache.sqlite")
        self.glossary = Glossary((GlossaryEntry("en", "zh", "repository", "仓库"),))

    def test_offline_uses_cache_first(self):
        self.cache.set("en", "zh", "repository", "cached repo", "mymemory")
        translator = Translator(Config(), cache=self.cache, glossary=self.glossary)
        result = translator.translate("repository", LangPair("en", "zh"), offline=True)
        self.assertEqual(result.text, "cached repo")
        self.assertEqual(result.backend, "mymemory")
        self.assertTrue(result.cached)

    def test_offline_uses_glossary_after_cache_miss(self):
        translator = Translator(Config(), cache=self.cache, glossary=self.glossary)
        result = translator.translate("repository", LangPair("en", "zh"), offline=True)
        self.assertEqual(result.text, "仓库")
        self.assertEqual(result.backend, "glossary")

    def test_cache_disabled_makes_offline_glossary_only(self):
        self.cache.set("en", "zh", "repository", "cached repo", "mymemory")
        translator = Translator(
            Config(cache=CacheConfig(enabled=False)), cache=self.cache, glossary=self.glossary
        )
        result = translator.translate("repository", LangPair("en", "zh"), offline=True)
        self.assertEqual(result.text, "仓库")
        self.assertEqual(result.backend, "glossary")

    def test_offline_miss_errors_without_backend_request(self):
        translator = Translator(Config(cache=CacheConfig(enabled=False)), glossary=Glossary())

        with self.assertRaisesRegex(BackendError, "offline miss"):
            translator.translate("unknown", LangPair("en", "zh"), offline=True)

    def test_substrings_are_an_offline_miss(self):
        translator = Translator(
            Config(cache=CacheConfig(enabled=False)),
            glossary=Glossary((GlossaryEntry("en", "zh", "cat", "猫"),)),
        )
        with self.assertRaisesRegex(BackendError, "offline miss"):
            translator.translate("concatenate", LangPair("en", "zh"), offline=True)


if __name__ == "__main__":
    unittest.main()
