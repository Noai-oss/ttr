from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .cache import TranslationCache
from .clipboard import read_clipboard, write_clipboard
from .config import Config, load_config
from .errors import TLError
from .lang import looks_like_lang_spec, parse_lang_spec
from .paths import cache_file, config_file, glossary_file
from .translator import TranslateOptions, Translator


BACKENDS = ("mymemory", "deepl", "libre")


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        if args and args[0] == "doctor":
            return doctor()
        if args and args[0] == "cache":
            return cache_cmd(args[1:])
        return translate_cmd(args)
    except (TLError, ValueError) as exc:
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
    config = load_config()
    parser = build_parser(config)
    ns = parser.parse_args(argv)

    if ns.version:
        print(__version__)
        return 0

    lang_spec, text_parts = extract_lang_and_text(ns.text)
    pair = parse_lang_spec(lang_spec, default_source=config.source, default_target=config.target)
    text = read_input(text_parts, use_clip=ns.clip)

    if not text:
        raise TLError("no input text")

    translator = Translator(config)
    options = TranslateOptions(
        backend=ns.backend or config.backend,
        offline=ns.offline,
        cache_enabled=config.cache.enabled,
    )

    if ns.lines:
        outputs = []
        for line in text.splitlines():
            if not line:
                outputs.append("")
                continue
            outputs.append(translator.translate(line, pair, options).text)
        translated_text = "\n".join(outputs)
        backend_name = "mixed"
        cached = False
        source = pair.source
        target = pair.target
    else:
        result = translator.translate(text, pair, options)
        translated_text = result.text
        backend_name = result.backend
        cached = result.cached
        source = result.source
        target = result.target

    if ns.copy:
        write_clipboard(translated_text)

    if ns.json:
        print(
            json.dumps(
                {
                    "text": translated_text,
                    "source": source,
                    "target": target,
                    "backend": backend_name,
                    "cached": cached,
                },
                ensure_ascii=False,
            )
        )
    else:
        print(translated_text)

    return 0


def build_parser(config: Config) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ttr",
        description="Translate text from arguments, stdin, or clipboard.",
    )
    parser.add_argument("text", nargs="*", help="optional [source]:[target] spec and text")
    parser.add_argument(
        "--backend",
        choices=list(BACKENDS),
        default=None,
        help=f"translation backend (default: {config.backend})",
    )
    parser.add_argument("--offline", action="store_true", help="read cache and glossary only")
    parser.add_argument("--clip", action="store_true", help="read input from clipboard")
    parser.add_argument("--copy", action="store_true", help="copy translated text to clipboard")
    parser.add_argument("--json", action="store_true", help="write structured JSON output")
    parser.add_argument("--lines", action="store_true", help="translate each line independently")
    parser.add_argument("--version", action="store_true", help="print version and exit")
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
    print(f"libre url: {cfg.libre.url}")
    print(f"config exists: {config_file().exists()}")
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

