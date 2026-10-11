from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .. import __version__
from ..errors import BackendError

MYMEMORY_LANGS = {
    "zh": "zh-CN",
}

MAX_QUERY_BYTES = 500


def api_lang(lang: str) -> str:
    return MYMEMORY_LANGS.get(lang, lang)


class MyMemoryBackend:
    name = "mymemory"
    endpoint = "https://api.mymemory.translated.net/get"

    def __init__(self, email: str | None = None, timeout: float = 12.0) -> None:
        self.email = email
        self.timeout = timeout

    def translate(self, text: str, source: str, target: str) -> str:
        if source == "auto":
            raise BackendError("mymemory requires a known source language")

        size = len(text.encode("utf-8"))
        if size > MAX_QUERY_BYTES:
            raise BackendError(
                f"text too large for mymemory ({size} bytes > {MAX_QUERY_BYTES} bytes); "
                "split the input or choose another backend"
            )

        query = {
            "q": text,
            "langpair": f"{api_lang(source)}|{api_lang(target)}",
        }
        if self.email:
            query["de"] = self.email

        url = f"{self.endpoint}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"User-Agent": f"ttr/{__version__}"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except OSError as exc:
            raise BackendError(f"request failed: {exc}") from exc

        try:
            data = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise BackendError("returned invalid UTF-8 JSON") from exc

        if not isinstance(data, dict):
            raise BackendError("returned an invalid response; expected an object")
        status = data.get("responseStatus")
        if status not in (200, "200"):
            details = data.get("responseDetails") or "unknown error"
            raise BackendError(str(details))

        response_data = data.get("responseData")
        if not isinstance(response_data, dict):
            raise BackendError("returned invalid responseData; expected an object")
        translated = response_data.get("translatedText")
        if not isinstance(translated, str) or not translated:
            raise BackendError("returned invalid translatedText; expected a nonempty string")

        return translated
