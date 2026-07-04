from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import Backend, BackendTranslation
from ..errors import BackendError


LIBRE_LANGS = {
    "zh": "zh-Hans",
}


def api_lang(lang: str) -> str:
    return LIBRE_LANGS.get(lang, lang)


class LibreBackend(Backend):
    name = "libre"

    def __init__(self, url: str = "http://127.0.0.1:5000", timeout: float = 8.0) -> None:
        self.url = url.rstrip("/")
        self.timeout = timeout

    def translate(self, text: str, source: str, target: str) -> BackendTranslation:
        payload = json.dumps(
            {
                "q": text,
                "source": api_lang(source),
                "target": api_lang(target),
                "format": "text",
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.url}/translate",
            data=payload,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "ttr/0.1.0",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise BackendError(f"request failed: HTTP {exc.code}: {details}") from exc
        except OSError as exc:
            raise BackendError(f"service unavailable at {self.url}: {exc}") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackendError("returned invalid JSON") from exc

        translated = data.get("translatedText")
        if not translated:
            raise BackendError(f"returned no translatedText: {raw}")
        return BackendTranslation(text=str(translated), backend=self.name)


