import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ttr.config import load_config


class ConfigTests(unittest.TestCase):
    def test_defaults_are_explicit_and_cache_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {}, clear=True):
                cfg = load_config(Path(tmp) / "missing.toml")

            self.assertEqual(cfg.backend, "mymemory")
            self.assertTrue(cfg.cache.enabled)

    def test_language_env_vars_override_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {"TTR_SOURCE_LANG": "english", "TTR_TARGET_LANG": "zh-cn"}
            with patch.dict(os.environ, env, clear=True):
                cfg = load_config(Path(tmp) / "missing.toml")

            self.assertEqual(cfg.source, "en")
            self.assertEqual(cfg.target, "zh")

    def test_cache_can_be_disabled_in_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text("[cache]\nenabled = false\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                cfg = load_config(path)

            self.assertFalse(cfg.cache.enabled)

    def test_cache_can_be_disabled_by_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"TTR_CACHE": "0"}, clear=True):
                cfg = load_config(Path(tmp) / "missing.toml")

            self.assertFalse(cfg.cache.enabled)


if __name__ == "__main__":
    unittest.main()
