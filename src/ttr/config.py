from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .errors import TTRError
from .lang import normalize_lang
from .paths import config_file

BACKENDS = ("mymemory", "deepl")


@dataclass(frozen=True)
class MyMemoryConfig:
    email: str | None = None


@dataclass(frozen=True)
class DeepLConfig:
    api_key: str | None = None
    url: str | None = None


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
    cache: CacheConfig = CacheConfig()
    path: Path = field(default_factory=config_file)


def load_config(path: Path | None = None, *, backend: str | None = None) -> Config:
    cfg_path = path or config_file()
    raw: dict = {}

    try:
        with cfg_path.open("rb") as handle:
            raw = tomllib.load(handle)
    except FileNotFoundError:
        pass
    except (OSError, ValueError) as exc:
        raise TTRError(f"cannot read config {cfg_path}: {exc}") from exc

    defaults = Config(path=cfg_path)
    source = string_setting(raw, "source", "TTR_SOURCE_LANG", defaults.source)
    target = string_setting(raw, "target", "TTR_TARGET_LANG", defaults.target)
    selected_backend = (
        backend
        if backend is not None
        else string_setting(raw, "backend", "TTR_BACKEND", defaults.backend)
    )
    if selected_backend is None or selected_backend.lower() not in BACKENDS:
        raise TTRError(f"unknown backend: {selected_backend}; choose {', '.join(BACKENDS)}")

    mymemory_raw = config_table(raw, "mymemory")
    deepl_raw = config_table(raw, "deepl")
    cache_raw = config_table(raw, "cache")

    env_cache = os.environ.get("TTR_CACHE")
    if env_cache is not None:
        cache_enabled = parse_bool(env_cache)
    else:
        cache_enabled = cache_raw.get("enabled", defaults.cache.enabled)
        if not isinstance(cache_enabled, bool):
            raise TTRError("cache.enabled must be a boolean")

    return Config(
        source=normalize_lang(source) if source is not None else None,
        target=normalize_lang(target) if target is not None else None,
        backend=selected_backend.lower(),
        mymemory=MyMemoryConfig(email=string_setting(mymemory_raw, "email", "TTR_MYMEMORY_EMAIL")),
        deepl=DeepLConfig(
            api_key=string_setting(deepl_raw, "api_key", "TTR_DEEPL_API_KEY"),
            url=string_setting(deepl_raw, "url", "TTR_DEEPL_URL"),
        ),
        cache=CacheConfig(enabled=cache_enabled),
        path=cfg_path,
    )


def config_table(raw: dict, key: str) -> dict:
    value = raw.get(key, {})
    if not isinstance(value, dict):
        raise TTRError(f"{key} must be a TOML table")
    return value


def string_setting(raw: dict, key: str, env_name: str, default: str | None = None) -> str | None:
    value = os.environ.get(env_name, raw.get(key, default))
    if value is None:
        return None
    if not isinstance(value, str):
        raise TTRError(f"{key} must be a string")
    return value.strip() or None


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise TTRError("TTR_CACHE must be 1/0, true/false, yes/no, or on/off")
