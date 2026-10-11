import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ttr.config import Config, load_config
from ttr.errors import TTRError


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.path = self.root / "config.toml"
        self.enterContext(patch.dict(os.environ, {}, clear=True))

    def test_defaults_are_explicit_and_cache_enabled(self):
        cfg = load_config(self.path)
        self.assertEqual(cfg.backend, "mymemory")
        self.assertTrue(cfg.cache.enabled)

    def test_language_env_vars_override_defaults(self):
        with patch.dict(os.environ, {"TTR_SOURCE_LANG": "english", "TTR_TARGET_LANG": "zh-cn"}):
            cfg = load_config(self.path)
        self.assertEqual(cfg.source, "en")
        self.assertEqual(cfg.target, "zh")

    def test_cache_can_be_disabled_in_config(self):
        self.path.write_text("[cache]\nenabled = false\n", encoding="utf-8")
        self.assertFalse(load_config(self.path).cache.enabled)

    def test_cache_can_be_disabled_by_env(self):
        with patch.dict(os.environ, {"TTR_CACHE": "0"}):
            self.assertFalse(load_config(self.path).cache.enabled)

    def test_invalid_config_types_are_rejected(self):
        cases = {
            "cache = true": "cache must be a TOML table",
            'deepl = "key"': "deepl must be a TOML table",
            "mymemory = []": "mymemory must be a TOML table",
            '[cache]\nenabled = "tru"': "cache.enabled must be a boolean",
            "[cache]\nenabled = 1": "cache.enabled must be a boolean",
            "[deepl]\napi_key = 42": "api_key must be a string",
            "[deepl]\nurl = []": "url must be a string",
            "source = 12": "source must be a string",
            "backend = true": "backend must be a string",
        }
        for content, error in cases.items():
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                with self.assertRaisesRegex(TTRError, error):
                    load_config(self.path)

    def test_invalid_env_boolean_is_rejected(self):
        with (
            patch.dict(os.environ, {"TTR_CACHE": "tru"}),
            self.assertRaisesRegex(TTRError, "TTR_CACHE"),
        ):
            load_config(self.path)

    def test_backend_precedence_and_validation(self):
        self.path.write_text('backend = "deepl"', encoding="utf-8")
        self.assertEqual(load_config(self.path).backend, "deepl")
        with patch.dict(os.environ, {"TTR_BACKEND": "mymemory"}):
            self.assertEqual(load_config(self.path).backend, "mymemory")
            self.assertEqual(load_config(self.path, backend="deepl").backend, "deepl")
        with patch.dict(os.environ, {"TTR_BACKEND": "libre"}):
            with self.assertRaisesRegex(TTRError, "unknown backend: libre"):
                load_config(self.path)
            self.assertEqual(load_config(self.path, backend="mymemory").backend, "mymemory")

    def test_empty_language_is_not_replaced_by_default(self):
        with patch.dict(os.environ, {"TTR_SOURCE_LANG": ""}):
            self.assertIsNone(load_config(self.path).source)

    def test_config_path_is_resolved_at_construction(self):
        with patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.root), "APPDATA": str(self.root)}):
            self.assertEqual(Config().path, self.root / "ttr" / "config.toml")

    def test_unreadable_config_is_an_expected_error(self):
        with self.assertRaisesRegex(TTRError, "cannot read config"):
            load_config(self.root)


if __name__ == "__main__":
    unittest.main()
