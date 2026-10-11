from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import TTRError
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
    def load(cls, path: Path | None = None) -> Glossary:
        gpath = path or glossary_file()
        try:
            lines = gpath.read_text(encoding="utf-8-sig").splitlines()
        except FileNotFoundError:
            return cls()
        except (OSError, UnicodeError) as exc:
            raise TTRError(f"cannot read glossary {gpath}: {exc}") from exc

        entries: list[GlossaryEntry] = []
        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) != 4 or any(not part.strip() for part in parts):
                raise TTRError(
                    f"invalid glossary entry at {gpath}:{line_number}; expected four nonempty TSV fields"
                )

            source, target, term, translation = parts
            try:
                entry = GlossaryEntry(
                    normalize_lang(source), normalize_lang(target), term, translation
                )
            except ValueError as exc:
                raise TTRError(f"invalid glossary entry at {gpath}:{line_number}: {exc}") from exc
            entries.append(entry)

        return cls(tuple(entries))

    def translate_exact(self, source: str, target: str, text: str) -> str | None:
        for entry in self.entries:
            if entry.source == source and entry.target == target and entry.term == text:
                return entry.translation
        return None
