from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import Backend, BackendTranslation
from ..errors import BackendError


FREE_ENDPOINT = "https://api-free.deepl.com/v2/translate"
PRO_ENDPOINT = "https://api.deepl.com/v2/translate"
MAX_REQUEST_BYTES = 128 * 1024

DEEPL_SOURCE_LANGS = {
    "en": "EN",
    "en-gb": "EN",
    "en-us": "EN",
    "zh": "ZH",
    "zh-cn": "ZH",
    "zh-hans": "ZH",
    "zh-hant": "ZH",
}

DEEPL_TARGET_LANGS = {
    "en": "EN-US",
    "en-us": "EN-US",
    "en-gb": "EN-GB",
    "pt": "PT-PT",
    "pt-pt": "PT-PT",
    "pt-br": "PT-BR",
    "es-419": "ES-419",
    "zh": "ZH",
    "zh-cn": "ZH",
    "zh-hans": "ZH",
    "zh-hant": "ZH",
}


def source_lang(lang: str) -> str:
    normalized = normalize_lang(lang)
    mapped = DEEPL_SOURCE_LANGS.get(normalized)
    if mapped is not None:
        return mapped
    if "-" in normalized:
        raise BackendError(f"unsupported deepl source language: {lang}")
    return normalized.upper()


def target_lang(lang: str) -> str:
    normalized = normalize_lang(lang)
    mapped = DEEPL_TARGET_LANGS.get(normalized)
    if mapped is not None:
        return mapped
    if "-" in normalized:
        raise BackendError(f"unsupported deepl target language: {lang}")
    return normalized.upper()


def normalize_lang(lang: str) -> str:
    return lang.strip().replace("_", "-").lower()


def default_endpoint(api_key: str | None) -> str:
    if api_key and api_key.endswith(":fx"):
        return FREE_ENDPOINT
    return PRO_ENDPOINT


def build_payload(text: str, source: str, target: str) -> bytes:
    payload = json.dumps(
        {
            "text": [text],
            "source_lang": source_lang(source),
            "target_lang": target_lang(target),
        },
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    if len(payload) > MAX_REQUEST_BYTES:
        raise BackendError(
            f"request too large for deepl ({len(payload)} bytes > {MAX_REQUEST_BYTES} bytes); "
            "split the input or choose another backend"
        )
    return payload


class DeepLBackend(Backend):
    name = "deepl"

    def __init__(
        self,
        api_key: str | None,
        url: str | None = None,
        timeout: float = 12.0,
    ) -> None:
        self.api_key = api_key
        self.url = url or default_endpoint(api_key)
        self.timeout = timeout

    def translate(self, text: str, source: str, target: str) -> BackendTranslation:
        if not self.api_key:
            raise BackendError("api key is not configured")

        payload = build_payload(text, source, target)
        request = urllib.request.Request(
            self.url,
            data=payload,
            headers={
                "Authorization": f"DeepL-Auth-Key {self.api_key}",
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
            raise BackendError(f"request failed: {exc}") from exc

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BackendError("returned invalid JSON") from exc

        translations = data.get("translations") or []
        if not translations or "text" not in translations[0]:
            raise BackendError(f"returned no translation: {raw}")
        return BackendTranslation(text=str(translations[0]["text"]), backend=self.name)
