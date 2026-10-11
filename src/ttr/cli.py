from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .cache import TranslationCache
from .clipboard import read_clipboard, write_clipboard
from .config import BACKENDS, load_config
from .errors import TTRError
from .lang import looks_like_lang_spec, parse_lang_spec
from .paths import cache_file, glossary_file
from .translator import Translator


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if args and args[0] == "doctor":
            return doctor()
        if args and args[0] == "cache":
            return cache_cmd(args[1:])
        return translate_cmd(args)
    except (TTRError, ValueError) as exc:
        print(f"ttr: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("ttr: interrupted", file=sys.stderr)
        return 130


def configure_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure") and not stream.isatty():
            stream.reconfigure(encoding="utf-8")


def translate_cmd(argv: list[str]) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    config = load_config(backend=ns.backend)

    lang_spec, text_parts = extract_lang_and_text(ns.text)
    pair = parse_lang_spec(lang_spec, default_source=config.source, default_target=config.target)
    text = read_input(text_parts, use_clip=ns.clip)

    if not text:
        raise TTRError("no input text")

    translator = Translator(config)
    if ns.lines:
        result = translator.translate_lines(text, pair, offline=ns.offline)
    else:
        result = translator.translate(text, pair, offline=ns.offline)

    for warning in result.warnings:
        print(f"ttr: warning: {warning}", file=sys.stderr)

    if ns.copy:
        write_clipboard(result.text)

    if ns.json:
        print(
            json.dumps(
                {
                    "text": result.text,
                    "source": result.source,
                    "target": result.target,
                    "backend": result.backend,
                    "cached": result.cached,
                },
                ensure_ascii=False,
            )
        )
    else:
        print(result.text)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ttr",
        description="Translate text from arguments, stdin, or clipboard.",
    )
    parser.add_argument("text", nargs="*", help="optional [source]:[target] spec and text")
    parser.add_argument(
        "--backend",
        choices=BACKENDS,
        default=None,
        help="translation backend (defaults to the configured backend)",
    )
    parser.add_argument("--offline", action="store_true", help="read cache and glossary only")
    parser.add_argument("--clip", action="store_true", help="read input from clipboard")
    parser.add_argument("--copy", action="store_true", help="copy translated text to clipboard")
    parser.add_argument("--json", action="store_true", help="write structured JSON output")
    parser.add_argument("--lines", action="store_true", help="translate each line independently")
    parser.add_argument("--version", action="version", version=__version__)
    return parser


def extract_lang_and_text(parts: list[str]) -> tuple[str | None, list[str]]:
    if parts and looks_like_lang_spec(parts[0]):
        return parts[0], parts[1:]
    return None, parts


def read_input(text_parts: list[str], use_clip: bool) -> str:
    if use_clip:
        return read_clipboard()

    if text_parts:
        return " ".join(text_parts)

    if not sys.stdin.isatty():
        return sys.stdin.read().lstrip("\ufeff").rstrip("\n")

    return ""


def doctor() -> int:
    cfg = load_config()
    print(f"ttr {__version__}")
    print(f"config: {cfg.path}")
    print(f"cache: {cache_file()}")
    print(f"glossary: {glossary_file()}")
    print(f"source: {cfg.source or 'not set'}")
    print(f"target: {cfg.target or 'not set'}")
    print(f"backend: {cfg.backend}")
    print(f"cache enabled: {cfg.cache.enabled}")
    print(f"mymemory email: {'set' if cfg.mymemory.email else 'not set'}")
    print(f"deepl api key: {'set' if cfg.deepl.api_key else 'not set'}")
    print(f"deepl url: {cfg.deepl.url or 'auto'}")
    print(f"config exists: {cfg.path.exists()}")
    print(f"glossary exists: {glossary_file().exists()}")
    return 0


def cache_cmd(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="ttr cache")
    parser.add_argument("action", choices=["clear", "stats"])
    ns = parser.parse_args(argv)

    cache = TranslationCache()
    if ns.action == "clear":
        count = cache.clear()
        print(f"cleared {count} entries")
        return 0

    entries, hits = cache.stats()
    print(f"entries: {entries}")
    print(f"hits: {hits}")
    return 0
