from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .lang import normalize_lang
from .paths import config_file


@dataclass(frozen=True)
class MyMemoryConfig:
    email: str | None = None


@dataclass(frozen=True)
class DeepLConfig:
    api_key: str | None = None
    url: str | None = None


@dataclass(frozen=True)
class LibreConfig:
    url: str = "http://127.0.0.1:5000"


@dataclass(frozen=True)
class CacheConfig:
    enabled: bool = True


@dataclass(frozen=True)
class Config:
    source: str | None = "en"
    target: str | None = "zh"
    backend: str = "mymemory"
    mymemory: MyMemoryConfig = MyMemoryConfig()
    deepl: DeepLConfig = DeepLConfig()
    libre: LibreConfig = LibreConfig()
    cache: CacheConfig = CacheConfig()
    path: Path = config_file()


def load_config(path: Path | None = None) -> Config:
    cfg_path = path or config_file()
    raw: dict = {}

    if cfg_path.exists():
        with cfg_path.open("rb") as handle:
            raw = tomllib.load(handle)

    source = env_or_config("TTR_SOURCE_LANG", raw, "source")
    target = env_or_config("TTR_TARGET_LANG", raw, "target")
    source = normalize_optional_lang(source) or "en"
    target = normalize_optional_lang(target) or "zh"
    backend = str(os.environ.get("TTR_BACKEND") or raw.get("backend") or "mymemory").lower()

    mymemory_raw = raw.get("mymemory") or {}
    deepl_raw = raw.get("deepl") or {}
    libre_raw = raw.get("libre") or {}
    cache_raw = raw.get("cache") or {}

    cache_enabled = parse_bool(cache_raw.get("enabled"), default=True)
    env_cache = os.environ.get("TTR_CACHE")
    if env_cache is not None:
        cache_enabled = parse_bool(env_cache, default=True)

    return Config(
        source=source,
        target=target,
        backend=backend,
        mymemory=MyMemoryConfig(
            email=os.environ.get("TTR_MYMEMORY_EMAIL") or mymemory_raw.get("email")
        ),
        deepl=DeepLConfig(
            api_key=os.environ.get("TTR_DEEPL_API_KEY") or deepl_raw.get("api_key"),
            url=os.environ.get("TTR_DEEPL_URL") or deepl_raw.get("url"),
        ),
        libre=LibreConfig(
            url=str(
                os.environ.get("TTR_LIBRE_URL")
                or libre_raw.get("url")
                or "http://127.0.0.1:5000"
            )
        ),
        cache=CacheConfig(enabled=cache_enabled),
        path=cfg_path,
    )


def env_or_config(env_name: str, raw: dict, key: str) -> str | None:
    value = os.environ.get(env_name)
    if value is not None:
        return value
    raw_value = raw.get(key)
    return str(raw_value) if raw_value is not None else None


def normalize_optional_lang(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    return normalize_lang(str(value))


def parse_bool(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}
