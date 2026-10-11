from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "ttr"


def config_dir() -> Path:
    if sys.platform == "win32":
        root = os.environ.get("APPDATA")
        return Path(root) / APP_NAME if root else Path.home() / "AppData" / "Roaming" / APP_NAME

    root = os.environ.get("XDG_CONFIG_HOME")
    return Path(root) / APP_NAME if root else Path.home() / ".config" / APP_NAME


def cache_dir() -> Path:
    if sys.platform == "win32":
        root = os.environ.get("LOCALAPPDATA")
        return Path(root) / APP_NAME if root else Path.home() / "AppData" / "Local" / APP_NAME

    root = os.environ.get("XDG_CACHE_HOME")
    return Path(root) / APP_NAME if root else Path.home() / ".cache" / APP_NAME


def config_file() -> Path:
    return config_dir() / "config.toml"


def glossary_file() -> Path:
    return config_dir() / "glossary.tsv"


def cache_file() -> Path:
    return cache_dir() / "cache.sqlite"
