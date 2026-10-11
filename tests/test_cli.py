import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ttr.cache import TranslationCache
from ttr.cli import extract_lang_and_text, main


class CliTests(unittest.TestCase):
    def test_extract_lang_and_text(self):
        cases = [
            (["en:zh", "hello"], ("en:zh", ["hello"])),
            ([":zh", "hello"], (":zh", ["hello"])),
            (["zh:", "你好"], ("zh:", ["你好"])),
            (["hello"], (None, ["hello"])),
        ]
        for args, expected in cases:
            with self.subTest(args=args):
                self.assertEqual(extract_lang_and_text(args), expected)


class CliIntegrationTests(unittest.TestCase):
    def setUp(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        env = {
            "XDG_CONFIG_HOME": str(root),
            "XDG_CACHE_HOME": str(root),
            "APPDATA": str(root),
            "LOCALAPPDATA": str(root),
        }
        self.enterContext(patch.dict(os.environ, env, clear=True))
        self.enterContext(
            patch(
                "urllib.request.urlopen", side_effect=AssertionError("unexpected network request")
            )
        )
        self.config_dir = root / "ttr"
        self.config_dir.mkdir()
        self.config_path = self.config_dir / "config.toml"
        self.glossary_path = self.config_dir / "glossary.tsv"
        self.cache = TranslationCache()

    def invoke(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err), patch("sys.stdin", io.StringIO()):
            try:
                code = main(list(args))
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_bad_config_is_a_clean_error(self):
        self.config_path.write_text("cache = true", encoding="utf-8")
        code, out, err = self.invoke("en:zh", "hello")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("cache must be a TOML table", err)
        self.assertNotIn("Traceback", err)

    def test_help_and_version_do_not_need_valid_config(self):
        self.config_path.write_text("[broken", encoding="utf-8")
        for option in ("--help", "--version"):
            with self.subTest(option=option):
                code, out, err = self.invoke(option)
                self.assertEqual(code, 0)
                self.assertTrue(out)
                self.assertEqual(err, "")

    def test_glossary_is_only_loaded_when_needed(self):
        self.glossary_path.write_bytes(b"\xff\xfe")
        self.cache.set("en", "zh", "hello", "你好", "mymemory")
        cases = [
            (("en:zh", "hello"), "你好\n", True),
            (("--offline", "en:zh", "hello"), "你好\n", False),
            (("en:en", "hello"), "hello\n", False),
        ]
        for args, expected, online in cases:
            with (
                self.subTest(args=args),
                patch(
                    "ttr.backends.mymemory.MyMemoryBackend.translate", return_value="你好"
                ) as translate,
            ):
                self.assertEqual(self.invoke(*args), (0, expected, ""))
                self.assertEqual(translate.called, online)

    def test_cache_write_failure_keeps_json_and_warns_on_stderr(self):
        self.cache.path.write_bytes(b"not a database")
        with patch("ttr.backends.mymemory.MyMemoryBackend.translate", return_value="你好"):
            code, out, err = self.invoke("--json", "en:zh", "hello")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["text"], "你好")
        self.assertFalse(data["cached"])
        self.assertEqual(err.count("warning:"), 1)
        self.assertIn("warning: translation was not cached", err)

    def test_lines_report_actual_cached_backend_and_keep_blank_lines(self):
        self.cache.set("en", "zh", "hello", "你好", "deepl")
        for text, expected in (("hello", "你好"), ("hello\n\nhello", "你好\n\n你好")):
            with self.subTest(text=text):
                code, out, err = self.invoke("--offline", "--lines", "--json", "en:zh", text)
                self.assertEqual((code, err), (0, ""))
                data = json.loads(out)
                self.assertEqual(data["text"], expected)
                self.assertEqual(data["backend"], "deepl")
                self.assertTrue(data["cached"])

    def test_lines_report_mixed_cache_and_glossary(self):
        self.cache.set("en", "zh", "hello", "你好", "mymemory")
        self.glossary_path.write_text("en\tzh\tcache\t缓存\n", encoding="utf-8")
        code, out, err = self.invoke("--offline", "--lines", "--json", "en:zh", "hello\ncache")
        self.assertEqual((code, err), (0, ""))
        data = json.loads(out)
        self.assertEqual(data["text"], "你好\n缓存")
        self.assertEqual(data["backend"], "mixed")
        self.assertFalse(data["cached"])

    def test_lines_glossary_and_identity_metadata(self):
        self.glossary_path.write_text("en\tzh\tcache\t缓存\n", encoding="utf-8")
        for pair, text, backend in (
            ("en:zh", "cache\ncache", "glossary"),
            ("en:en", "hello\nworld", "identity"),
            ("en:zh", "\n", "identity"),
        ):
            with self.subTest(pair=pair, text=text):
                code, out, err = self.invoke("--offline", "--lines", "--json", pair, text)
                self.assertEqual((code, err), (0, ""))
                data = json.loads(out)
                self.assertEqual(data["backend"], backend)
                self.assertFalse(data["cached"])

    def test_cli_backend_overrides_config(self):
        self.config_path.write_text('backend = "libre"', encoding="utf-8")
        with patch(
            "ttr.backends.mymemory.MyMemoryBackend.translate", return_value="你好"
        ) as translate:
            code, out, err = self.invoke("--backend", "mymemory", "en:zh", "hello")
        self.assertEqual((code, out, err), (0, "你好\n", ""))
        translate.assert_called_once_with("hello", "en", "zh")


if __name__ == "__main__":
    unittest.main()
