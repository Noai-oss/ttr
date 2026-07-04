from __future__ import annotations

import shutil
import subprocess
import sys

from .errors import ClipboardError


def read_clipboard() -> str:
    if sys.platform == "win32":
        return _run_read(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"])
    if sys.platform == "darwin":
        return _run_read(["pbpaste"])

    if shutil.which("wl-paste"):
        return _run_read(["wl-paste", "--no-newline"])
    if shutil.which("xclip"):
        return _run_read(["xclip", "-selection", "clipboard", "-out"])
    if shutil.which("xsel"):
        return _run_read(["xsel", "--clipboard", "--output"])

    raise ClipboardError("no supported clipboard reader found")


def write_clipboard(text: str) -> None:
    if sys.platform == "win32":
        _run_write(["powershell", "-NoProfile", "-Command", "Set-Clipboard"], text)
        return
    if sys.platform == "darwin":
        _run_write(["pbcopy"], text)
        return

    if shutil.which("wl-copy"):
        _run_write(["wl-copy"], text)
        return
    if shutil.which("xclip"):
        _run_write(["xclip", "-selection", "clipboard"], text)
        return
    if shutil.which("xsel"):
        _run_write(["xsel", "--clipboard", "--input"], text)
        return

    raise ClipboardError("no supported clipboard writer found")


def _run_read(args: list[str]) -> str:
    try:
        completed = subprocess.run(args, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ClipboardError(f"clipboard command failed to start: {exc}") from exc

    if completed.returncode != 0:
        details = completed.stderr.strip() or "clipboard read failed"
        raise ClipboardError(details)
    return completed.stdout.rstrip("\r\n")


def _run_write(args: list[str], text: str) -> None:
    try:
        completed = subprocess.run(args, input=text, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ClipboardError(f"clipboard command failed to start: {exc}") from exc

    if completed.returncode != 0:
        details = completed.stderr.strip() or "clipboard write failed"
        raise ClipboardError(details)

