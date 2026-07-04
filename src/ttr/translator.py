from __future__ import annotations

from dataclasses import dataclass

from .backends import DeepLBackend, LibreBackend, MyMemoryBackend
from .backends.base import Backend
from .cache import TranslationCache
from .config import Config
from .errors import BackendError
from .glossary import Glossary
from .lang import LangPair, resolve_pair
from .result import TranslateResult


@dataclass(frozen=True)
class TranslateOptions:
    backend: str = "mymemory"
    offline: bool = False
    cache_enabled: bool = True


class Translator:
    def __init__(
        self,
        config: Config,
        cache: TranslationCache | None = None,
        glossary: Glossary | None = None,
    ) -> None:
        self.config = config
        self.cache = cache or TranslationCache()
        self.glossary = glossary or Glossary.load()

    def translate(self, text: str, pair: LangPair, options: TranslateOptions) -> TranslateResult:
        resolved = resolve_pair(pair, text)

        if resolved.source == resolved.target:
            return TranslateResult(text, resolved.source, resolved.target, "identity")

        if options.offline:
            return self._translate_offline(text, resolved, read_cache=options.cache_enabled)

        result = self._translate_online(text, resolved, options.backend)

        if options.cache_enabled:
            self.cache.set(
                resolved.source,
                resolved.target,
                text,
                result.text,
                result.backend,
            )
        return result

    def _translate_offline(self, text: str, pair: LangPair, read_cache: bool) -> TranslateResult:
        if read_cache:
            hit = self.cache.get_any(pair.source, pair.target, text)
            if hit is not None:
                return TranslateResult(
                    text=hit.text,
                    source=pair.source,
                    target=pair.target,
                    backend=hit.backend,
                    cached=True,
                )

        exact = self.glossary.translate_exact(pair.source, pair.target, text)
        if exact is not None:
            return TranslateResult(exact, pair.source, pair.target, "glossary")

        applied = self.glossary.apply_terms(pair.source, pair.target, text)
        if applied is not None:
            return TranslateResult(applied, pair.source, pair.target, "glossary")

        raise BackendError("offline miss: no cache or glossary entry")

    def _translate_online(self, text: str, pair: LangPair, backend_name: str) -> TranslateResult:
        backend = self._backend(backend_name)
        try:
            translated = backend.translate(text, pair.source, pair.target)
        except BackendError as exc:
            raise BackendError(format_backend_error(backend.name, str(exc))) from exc

        return TranslateResult(
            translated.text,
            pair.source,
            pair.target,
            translated.backend,
        )

    def _backend(self, backend_name: str) -> Backend:
        backend_name = backend_name.lower()
        if backend_name == "mymemory":
            return MyMemoryBackend(email=self.config.mymemory.email)
        if backend_name == "deepl":
            return self._deepl_backend()
        if backend_name == "libre":
            return self._libre_backend()
        raise BackendError(f"unknown backend: {backend_name}")

    def _deepl_backend(self) -> DeepLBackend:
        return DeepLBackend(api_key=self.config.deepl.api_key, url=self.config.deepl.url)

    def _libre_backend(self) -> LibreBackend:
        return LibreBackend(url=self.config.libre.url)


def format_backend_error(backend_name: str, message: str) -> str:
    lowered = message.lower()
    prefixes = (
        f"{backend_name} failed: ",
        f"{backend_name} request failed: ",
        f"{backend_name}: ",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return f"{backend_name}: {message[len(prefix):]}"
    return f"{backend_name}: {message}"

