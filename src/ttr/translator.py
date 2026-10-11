from __future__ import annotations

from .backends import DeepLBackend, MyMemoryBackend
from .cache import TranslationCache
from .config import Config
from .errors import BackendError, CacheError
from .glossary import Glossary
from .lang import LangPair
from .result import TranslateResult


class Translator:
    def __init__(
        self,
        config: Config,
        cache: TranslationCache | None = None,
        glossary: Glossary | None = None,
    ) -> None:
        self.config = config
        self.cache = cache or TranslationCache()
        self.glossary = glossary

    def translate(self, text: str, pair: LangPair, *, offline: bool = False) -> TranslateResult:
        if pair.source == pair.target:
            return TranslateResult(text, pair.source, pair.target, "identity")

        if offline:
            return self._translate_offline(text, pair)

        backend = self._backend()
        try:
            translated = backend.translate(text, pair.source, pair.target)
        except BackendError as exc:
            raise BackendError(f"{backend.name}: {exc}") from exc

        warnings = ()
        if self.config.cache.enabled:
            try:
                self.cache.set(pair.source, pair.target, text, translated, backend.name)
            except CacheError as exc:
                warnings = (f"translation was not cached: {exc}",)
        return TranslateResult(
            translated, pair.source, pair.target, backend.name, warnings=warnings
        )

    def translate_lines(
        self, text: str, pair: LangPair, *, offline: bool = False
    ) -> TranslateResult:
        lines = [
            self.translate(line, pair, offline=offline) if line else None
            for line in text.splitlines()
        ]
        results = [result for result in lines if result is not None]
        backends = {result.backend for result in results}
        backend = next(iter(backends)) if len(backends) == 1 else "mixed"
        return TranslateResult(
            text="\n".join(result.text if result is not None else "" for result in lines),
            source=pair.source,
            target=pair.target,
            backend=backend if results else "identity",
            cached=bool(results) and all(result.cached for result in results),
            warnings=tuple(warning for result in results for warning in result.warnings),
        )

    def _translate_offline(self, text: str, pair: LangPair) -> TranslateResult:
        if self.config.cache.enabled:
            hit = self.cache.get(pair.source, pair.target, text)
            if hit is not None:
                return TranslateResult(
                    text=hit.text,
                    source=pair.source,
                    target=pair.target,
                    backend=hit.backend,
                    cached=True,
                )

        glossary = self.glossary if self.glossary is not None else Glossary.load()
        exact = glossary.translate_exact(pair.source, pair.target, text)
        if exact is not None:
            return TranslateResult(exact, pair.source, pair.target, "glossary")

        raise BackendError("offline miss: no cache or glossary entry")

    def _backend(self) -> DeepLBackend | MyMemoryBackend:
        backend_name = self.config.backend
        if backend_name == "mymemory":
            return MyMemoryBackend(email=self.config.mymemory.email)
        if backend_name == "deepl":
            return DeepLBackend(api_key=self.config.deepl.api_key, url=self.config.deepl.url)
        raise BackendError(f"unknown backend: {backend_name}")
