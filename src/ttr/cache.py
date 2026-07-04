from __future__ import annotations

import hashlib
import sqlite3
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from .paths import cache_file


SCHEMA = """
CREATE TABLE IF NOT EXISTS translations (
    key TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    text TEXT NOT NULL,
    translated TEXT NOT NULL,
    backend TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    used_at INTEGER NOT NULL,
    hits INTEGER NOT NULL DEFAULT 0
);
"""


@dataclass(frozen=True)
class CacheHit:
    text: str
    backend: str


def cache_key(source: str, target: str, text: str, backend: str) -> str:
    payload = "\0".join([source, target, backend, text]).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class TranslationCache:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or cache_file()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.path)
        con.execute(SCHEMA)
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def get(self, source: str, target: str, text: str, backend: str) -> CacheHit | None:
        key = cache_key(source, target, text, backend)
        return self._get_by_key(key)

    def get_any(self, source: str, target: str, text: str) -> CacheHit | None:
        now = int(time.time())
        with self._connect() as con:
            row = con.execute(
                """
                SELECT key, translated, backend
                FROM translations
                WHERE source = ? AND target = ? AND text = ?
                ORDER BY used_at DESC, created_at DESC
                LIMIT 1
                """,
                (source, target, text),
            ).fetchone()
            if row is None:
                return None
            con.execute(
                "UPDATE translations SET used_at = ?, hits = hits + 1 WHERE key = ?",
                (now, row[0]),
            )
            return CacheHit(text=row[1], backend=row[2])

    def _get_by_key(self, key: str) -> CacheHit | None:
        now = int(time.time())
        with self._connect() as con:
            row = con.execute(
                "SELECT translated, backend FROM translations WHERE key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            con.execute(
                "UPDATE translations SET used_at = ?, hits = hits + 1 WHERE key = ?",
                (now, key),
            )
            return CacheHit(text=row[0], backend=row[1])

    def set(self, source: str, target: str, text: str, translated: str, backend: str) -> None:
        key = cache_key(source, target, text, backend)
        now = int(time.time())
        with self._connect() as con:
            con.execute(
                """
                INSERT OR REPLACE INTO translations
                    (key, source, target, text, translated, backend, created_at, used_at, hits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(
                    (SELECT hits FROM translations WHERE key = ?), 0
                ))
                """,
                (key, source, target, text, translated, backend, now, now, key),
            )

    def clear(self) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) FROM translations").fetchone()
            count = int(row[0])
            con.execute("DELETE FROM translations")
            return count

    def stats(self) -> tuple[int, int]:
        with self._connect() as con:
            row = con.execute(
                "SELECT COUNT(*), COALESCE(SUM(hits), 0) FROM translations"
            ).fetchone()
            return int(row[0]), int(row[1])

