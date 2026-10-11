import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ttr.cache import CacheHit, TranslationCache


class CacheTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.cache = TranslationCache(root / "cache.sqlite")

    def test_round_trip_tracks_hits(self):
        self.cache.set("en", "zh", "hello", "你好", "mymemory")
        self.assertEqual(self.cache.get("en", "zh", "hello"), CacheHit("你好", "mymemory"))
        self.assertIsNone(self.cache.get("en", "zh", "unknown"))
        self.assertEqual(self.cache.stats(), (1, 1))

    def test_keeps_backends_separate_and_reads_latest(self):
        with patch("ttr.cache.time.time", side_effect=[1, 2, 3]):
            self.cache.set("en", "zh", "hello", "你好", "mymemory")
            self.cache.set("en", "zh", "hello", "您好", "deepl")
            self.assertEqual(self.cache.get("en", "zh", "hello"), CacheHit("您好", "deepl"))
        self.assertEqual(self.cache.stats(), (2, 1))

    def test_clear(self):
        self.cache.set("en", "zh", "hello", "你好", "test")
        self.assertEqual(self.cache.clear(), 1)
        self.assertIsNone(self.cache.get("en", "zh", "hello"))


if __name__ == "__main__":
    unittest.main()
