import io
import json
import unittest
from unittest.mock import patch

from ttr.backends.deepl import (
    FREE_ENDPOINT,
    MAX_REQUEST_BYTES,
    PRO_ENDPOINT,
    DeepLBackend,
    build_payload,
    default_endpoint,
    source_lang,
    target_lang,
)
from ttr.errors import BackendError
from ttr.lang import parse_lang_spec


class DeepLTests(unittest.TestCase):
    def test_free_key_uses_free_endpoint(self):
        self.assertEqual(default_endpoint("example:fx"), FREE_ENDPOINT)

    def test_non_free_key_uses_pro_endpoint(self):
        self.assertEqual(default_endpoint("example"), PRO_ENDPOINT)

    def test_english_target_defaults_to_us_variant(self):
        self.assertEqual(target_lang("en"), "EN-US")

    def test_english_source_variants_map_to_generic_english(self):
        self.assertEqual(source_lang("en-gb"), "EN")
        self.assertEqual(source_lang("en_US"), "EN")

    def test_known_target_variants_are_preserved(self):
        self.assertEqual(target_lang("en-gb"), "EN-GB")
        self.assertEqual(target_lang("pt-br"), "PT-BR")
        self.assertEqual(target_lang("es-419"), "ES-419")
        self.assertEqual(target_lang("zh-hant"), "ZH-HANT")

    def test_unknown_regional_variant_errors(self):
        with self.assertRaisesRegex(BackendError, "unsupported deepl target language"):
            target_lang("fr-ca")

    def test_payload_is_compact_utf8_json(self):
        payload = build_payload("你好", "zh", "en")
        data = json.loads(payload.decode("utf-8"))

        self.assertEqual(data["text"], ["你好"])
        self.assertEqual(data["source_lang"], "ZH")
        self.assertEqual(data["target_lang"], "EN-US")
        self.assertNotIn(b"\\u4f60", payload)

    def test_missing_api_key_errors_before_http(self):
        with self.assertRaisesRegex(BackendError, "api key"):
            DeepLBackend(api_key=None).translate("hello", "en", "zh")

    def test_request_shape(self):
        response = io.BytesIO('{"translations":[{"text":"你好"}]}'.encode())
        with patch("ttr.backends.deepl.urllib.request.urlopen", return_value=response) as urlopen:
            result = DeepLBackend(api_key="test-key:fx", timeout=3.5).translate("hello", "en", "zh")

        request = urlopen.call_args.args[0]
        data = json.loads(request.data.decode("utf-8"))
        self.assertEqual(result, "你好")
        self.assertEqual(request.full_url, FREE_ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "DeepL-Auth-Key test-key:fx")
        self.assertEqual(request.get_header("Content-type"), "application/json; charset=utf-8")
        self.assertEqual(request.get_header("User-agent"), "ttr/0.1.0")
        self.assertEqual(data, {"text": ["hello"], "source_lang": "EN", "target_lang": "ZH"})
        urlopen.assert_called_once_with(request, timeout=3.5)

    def test_large_request_errors_before_http(self):
        with (
            patch("ttr.backends.deepl.urllib.request.urlopen") as urlopen,
            self.assertRaisesRegex(BackendError, "request too large"),
        ):
            DeepLBackend(api_key="test-key").translate("a" * MAX_REQUEST_BYTES, "en", "zh")

        urlopen.assert_not_called()

    def test_traditional_target_survives_language_parsing(self):
        pair = parse_lang_spec("en:zh-hant")
        payload = json.loads(build_payload("hello", pair.source, pair.target))
        self.assertEqual(payload["target_lang"], "ZH-HANT")

    def test_invalid_responses_are_rejected(self):
        responses = [
            [],
            None,
            {},
            {"translations": {}},
            {"translations": [None]},
            {"translations": [{"text": None}]},
            {"translations": [{"text": 1}]},
            {"translations": [{"text": {"error": "broken"}}]},
            {"translations": [{"text": "first"}, {"text": "second"}]},
        ]
        for payload in responses:
            with (
                self.subTest(payload=payload),
                patch(
                    "urllib.request.urlopen",
                    return_value=io.BytesIO(json.dumps(payload).encode()),
                ),
                self.assertRaises(BackendError),
            ):
                DeepLBackend("test:fx").translate("hello", "en", "zh")

    def test_invalid_json_and_encoding_are_rejected(self):
        for payload in (b"not JSON", b"\xff"):
            with (
                self.subTest(payload=payload),
                patch("urllib.request.urlopen", return_value=io.BytesIO(payload)),
                self.assertRaisesRegex(BackendError, "invalid UTF-8 JSON"),
            ):
                DeepLBackend("test:fx").translate("hello", "en", "zh")


if __name__ == "__main__":
    unittest.main()
