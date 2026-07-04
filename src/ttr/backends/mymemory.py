from __future__ import annotations

import json
import urllib.parse
import urllib.request

from .base import Backend, BackendTranslation
from ..errors import BackendError


MYMEMORY_LANGS = {
    "zh": "zh-CN",
}

MAX_QUERY_BYTES = 480


def api_lang(lang: str) -> str:
    return MYMEMORY_LANGS.get(lang, lang)


def utf8_len(value: str) -> int:
    return len(value.encode("utf-8"))


class MyMemoryBackend(Backend):
    name = "mymemory"
    endpoint = "https://api.mymemory.translated.net/get"

    def __init__(self, email: str | None = None, timeout: float = 12.0) -> None:
        self.email = email
        self.timeout = timeout

    def translate(self, text: str, source: str, target: str) -> BackendTranslation:
        if source == "auto":
            raise BackendError("mymemory requires a known source language")

        size = utf8_len(text)
        if size > MAX_QUERY_BYTES:
            raise BackendError(
                f"text too large for mymemory ({size} bytes > {MAX_QUERY_BYTES} bytes); "
                "split the input or choose another backend"
            )

        translated = self._translate_request(text, source=source, target=target)
        return BackendTranslation(text=translated, backend=self.name)

    def _translate_request(self, text: str, source: str, target: str) -> str:
        query = {
            "q": text,
            "langpair": f"{api_lang(source)}|{api_lang(target)}",
        }
        if self.email:
            query["de"] = self.email

        url = f"{self.endpoint}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(url, headers={"User-Agent": "ttr/0.1.0"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read().decode("utf-8")
        except OSError as exc:
            raise BackendError(f"mymemory request failed: {exc}") from exc

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise BackendError("mymemory returned invalid JSON") from exc

        status = data.get("responseStatus")
        translated = (data.get("responseData") or {}).get("translatedText")

        if status not in {200, "200"} or not translated:
            details = data.get("responseDetails") or "unknown error"
            raise BackendError(f"mymemory failed: {details}")

        return str(translated)

