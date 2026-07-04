from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .lang import normalize_lang
from .paths import glossary_file


@dataclass(frozen=True)
class GlossaryEntry:
    source: str
    target: str
    term: str
    translation: str


@dataclass(frozen=True)
class Glossary:
    entries: tuple[GlossaryEntry, ...] = ()

    @classmethod
    def load(cls, path: Path | None = None) -> "Glossary":
        gpath = path or glossary_file()
        if not gpath.exists():
            return cls()

        entries: list[GlossaryEntry] = []
        for line in gpath.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) < 4:
                continue

            source, target, term, translation = parts[:4]
            if not term or not translation:
                continue

            entries.append(
                GlossaryEntry(
                    source=normalize_lang(source),
                    target=normalize_lang(target),
                    term=term,
                    translation=translation,
                )
            )

        return cls(tuple(entries))

    def translate_exact(self, source: str, target: str, text: str) -> str | None:
        for entry in self.entries:
            if entry.source == source and entry.target == target and entry.term == text:
                return entry.translation
        return None

    def apply_terms(self, source: str, target: str, text: str) -> str | None:
        translated = text
        changed = False
        for entry in self.entries:
            if entry.source != source or entry.target != target:
                continue
            if entry.term in translated:
                translated = translated.replace(entry.term, entry.translation)
                changed = True
        return translated if changed else None

