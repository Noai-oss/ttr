import tempfile
import unittest
from pathlib import Path

from ttr.backends.base import Backend, BackendTranslation
from ttr.cache import TranslationCache
from ttr.config import Config
from ttr.glossary import Glossary
from ttr.lang import LangPair
from ttr.translator import TranslateOptions, Translator


class FakeBackend(Backend):
    name = "fake"

    def translate(self, text: str, source: str, target: str) -> BackendTranslation:
        return BackendTranslation(text=f"fresh:{text}", backend=self.name)


class FakeTranslator(Translator):
    def _backend(self, backend_name: str) -> Backend:
        return FakeBackend()


class TranslatorCacheTests(unittest.TestCase):
    def test_online_translation_writes_cache_without_reading_existing_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "hello", "stale", "fake")
            translator = FakeTranslator(Config(), cache=cache, glossary=Glossary())

            result = translator.translate(
                "hello",
                LangPair("en", "zh"),
                TranslateOptions(backend="fake", cache_enabled=True),
            )
            hit = cache.get("en", "zh", "hello", "fake")

            self.assertEqual(result.text, "fresh:hello")
            self.assertFalse(result.cached)
            self.assertIsNotNone(hit)
            self.assertEqual(hit.text, "fresh:hello")

    def test_online_translation_does_not_write_cache_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            translator = FakeTranslator(Config(), cache=cache, glossary=Glossary())

            translator.translate(
                "hello",
                LangPair("en", "zh"),
                TranslateOptions(backend="fake", cache_enabled=False),
            )

            self.assertIsNone(cache.get("en", "zh", "hello", "fake"))


if __name__ == "__main__":
    unittest.main()

