import tempfile
import unittest
from pathlib import Path

from ttr.cache import TranslationCache


class CacheTests(unittest.TestCase):
    def test_round_trip_is_backend_specific(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "hello", "你好", "mymemory")

            hit = cache.get("en", "zh", "hello", "mymemory")

            self.assertIsNotNone(hit)
            self.assertEqual(hit.text, "你好")
            self.assertEqual(hit.backend, "mymemory")

    def test_backend_specific_lookup_does_not_cross_backends(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "hello", "你好", "mymemory")

            self.assertIsNone(cache.get("en", "zh", "hello", "deepl"))

    def test_get_any_returns_cached_translation_for_offline_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "hello", "你好", "mymemory")

            hit = cache.get_any("en", "zh", "hello")

            self.assertIsNotNone(hit)
            self.assertEqual(hit.text, "你好")
            self.assertEqual(hit.backend, "mymemory")

    def test_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = TranslationCache(Path(tmp) / "cache.sqlite")
            cache.set("en", "zh", "hello", "你好", "test")
            self.assertEqual(cache.clear(), 1)
            self.assertIsNone(cache.get("en", "zh", "hello", "test"))


if __name__ == "__main__":
    unittest.main()

