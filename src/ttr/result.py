from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TranslateResult:
    text: str
    source: str
    target: str
    backend: str
    cached: bool = False
    warnings: tuple[str, ...] = ()
