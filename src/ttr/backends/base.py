from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendTranslation:
    text: str
    backend: str


class Backend:
    name = "backend"

    def translate(self, text: str, source: str, target: str) -> BackendTranslation:
        raise NotImplementedError

