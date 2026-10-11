from __future__ import annotations

import re
from dataclasses import dataclass

LANG_SPEC_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9-]*)?:([a-zA-Z][a-zA-Z0-9-]*)?$")

ZH_ALIASES = {"zh", "zh-cn", "zh-hans", "cn", "chinese"}
EN_ALIASES = {"en", "eng", "english"}


@dataclass(frozen=True)
class LangPair:
    source: str
    target: str


def looks_like_lang_spec(value: str) -> bool:
    return ":" in value and LANG_SPEC_RE.match(value) is not None


def parse_lang_spec(
    spec: str | None,
    default_source: str | None = None,
    default_target: str | None = None,
) -> LangPair:
    if spec is None:
        source = require_lang("source", default_source)
        target = require_lang("target", default_target)
        return LangPair(source=source, target=target)

    match = LANG_SPEC_RE.match(spec)
    if match is None:
        raise ValueError(f"invalid language pair; use en:zh, :zh, or zh:: {spec}")

    raw_source, raw_target = match.groups()
    if raw_source is None and raw_target is None:
        raise ValueError("language pair is empty; pass en:zh or configure source and target")

    source = normalize_lang(raw_source) if raw_source else require_lang("source", default_source)
    target = normalize_lang(raw_target) if raw_target else require_lang("target", default_target)
    return LangPair(source=source, target=target)


def require_lang(name: str, value: str | None) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{name} language missing; pass en:zh or set {name} in config")
    return normalize_lang(value)


def normalize_lang(value: str) -> str:
    lowered = value.strip().lower()
    if lowered == "auto" or re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", lowered) is None:
        raise ValueError(f"invalid language: {value}; use an explicit language code")
    if lowered in ZH_ALIASES:
        return "zh"
    if lowered in EN_ALIASES:
        return "en"
    return lowered
