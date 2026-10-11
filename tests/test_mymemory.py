import json
import unittest
from unittest.mock import patch

from ttr.backends.mymemory import MAX_QUERY_BYTES, MyMemoryBackend
from ttr.errors import BackendError


class MyMemoryTests(unittest.TestCase):
    def test_long_input_errors_before_request(self):
        text = "a" * (MAX_QUERY_BYTES + 1)

        with self.assertRaisesRegex(BackendError, "text too large"):
            MyMemoryBackend().translate(text, "en", "zh")

    def test_successful_response_preserves_unicode(self):
        with patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
                {"responseStatus": "200", "responseData": {"translatedText": "你好 café 🔄"}},
                ensure_ascii=False,
            ).encode("utf-8")
            self.assertEqual(MyMemoryBackend().translate("hello", "en", "zh"), "你好 café 🔄")

    def test_invalid_responses_are_rejected(self):
        responses = [[], None, {}, {"responseStatus": []}]
        responses.extend(
            {"responseStatus": 200, "responseData": value}
            for value in (
                None,
                [],
                {},
                {"translatedText": None},
                {"translatedText": 1},
                {"translatedText": {"error": "broken"}},
            )
        )
        for payload in responses:
            with self.subTest(payload=payload), patch("urllib.request.urlopen") as urlopen:
                urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
                    payload
                ).encode()
                with self.assertRaises(BackendError):
                    MyMemoryBackend().translate("hello", "en", "zh")

    def test_invalid_json_and_encoding_are_rejected(self):
        for payload in (b"not JSON", b"\xff"):
            with self.subTest(payload=payload), patch("urllib.request.urlopen") as urlopen:
                urlopen.return_value.__enter__.return_value.read.return_value = payload
                with self.assertRaisesRegex(BackendError, "invalid UTF-8 JSON"):
                    MyMemoryBackend().translate("hello", "en", "zh")

    def test_service_error_details_are_preserved(self):
        with patch("urllib.request.urlopen") as urlopen:
            urlopen.return_value.__enter__.return_value.read.return_value = (
                b'{"responseStatus":429,"responseDetails":"quota exceeded"}'
            )
            with self.assertRaisesRegex(BackendError, "^quota exceeded$"):
                MyMemoryBackend().translate("hello", "en", "zh")


if __name__ == "__main__":
    unittest.main()
