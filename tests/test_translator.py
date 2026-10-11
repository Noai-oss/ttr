import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ttr.cache import CacheHit, TranslationCache
from ttr.config import CacheConfig, Config, DeepLConfig
from ttr.errors import BackendError, CacheError
from ttr.glossary import Glossary
from ttr.lang import LangPair
from ttr.translator import Translator


class TranslatorCacheTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.cache = TranslationCache(root / "cache.sqlite")

    def test_online_translation_writes_cache_without_reading_existing_cache(self):
        self.cache.set("en", "zh", "hello", "stale", "mymemory")
        translator = Translator(Config(), cache=self.cache)
        with patch("ttr.backends.mymemory.MyMemoryBackend.translate", return_value="你好"):
            result = translator.translate("hello", LangPair("en", "zh"))
        self.assertEqual(result.text, "你好")
        self.assertFalse(result.cached)
        self.assertEqual(self.cache.get("en", "zh", "hello"), CacheHit("你好", "mymemory"))

    def test_config_selects_backend_and_disables_cache(self):
        translator = Translator(
            Config(
                backend="deepl",
                deepl=DeepLConfig(api_key="test:fx"),
                cache=CacheConfig(enabled=False),
            ),
            cache=self.cache,
        )
        with (
            patch("ttr.backends.deepl.DeepLBackend.translate", return_value="你好") as deepl,
            patch.object(translator.cache, "set") as write,
        ):
            result = translator.translate("hello", LangPair("en", "zh"))
        self.assertEqual(result.backend, "deepl")
        self.assertEqual(result.text, "你好")
        deepl.assert_called_once_with("hello", "en", "zh")
        write.assert_not_called()

    def test_offline_cache_failure_is_reported(self):
        self.cache.path.write_bytes(b"not a database")
        translator = Translator(Config(), cache=self.cache, glossary=Glossary())
        with self.assertRaisesRegex(CacheError, "cache.sqlite"):
            translator.translate("hello", LangPair("en", "zh"), offline=True)

    def test_backend_error_has_one_prefix(self):
        translator = Translator(Config(cache=CacheConfig(enabled=False)))
        with (
            patch(
                "ttr.backends.mymemory.MyMemoryBackend.translate",
                side_effect=BackendError("request failed: timed out"),
            ),
            self.assertRaisesRegex(BackendError, "^mymemory: request failed: timed out$"),
        ):
            translator.translate("hello", LangPair("en", "zh"))


if __name__ == "__main__":
    unittest.main()
