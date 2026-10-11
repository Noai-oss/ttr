import subprocess
import sys
import unittest
from unittest.mock import patch

from ttr.clipboard import _run_read, _run_write, read_clipboard, write_clipboard
from ttr.errors import ClipboardError


class ClipboardTests(unittest.TestCase):
    def test_read_preserves_utf8_and_trailing_newlines(self):
        text = "你好 café 🔄\r\n\r\n"
        script = f"import sys; sys.stdout.buffer.write({text.encode('utf-8')!r})"
        self.assertEqual(_run_read([sys.executable, "-c", script]), text)

    def test_write_sends_utf8_bytes(self):
        text = "你好 café 🔄\r\n"
        script = f"import sys; assert sys.stdin.buffer.read() == {text.encode('utf-8')!r}"
        _run_write([sys.executable, "-c", script], text)

    def test_read_invalid_encoding_is_a_clear_error(self):
        script = "import sys; sys.stdout.buffer.write(b'\\xff')"
        with self.assertRaisesRegex(ClipboardError, "invalid UTF-8"):
            _run_read([sys.executable, "-c", script])

    def test_windows_write_reads_stdin_without_interpolating_text(self):
        text = "你好 $(not-a-command) 'quoted'\n"
        completed = subprocess.CompletedProcess([], 0, stdout=b"", stderr=b"")
        with (
            patch("ttr.clipboard.sys.platform", "win32"),
            patch("subprocess.run", return_value=completed) as run,
        ):
            write_clipboard(text)
        command = run.call_args.args[0][-1]
        self.assertIn("[Console]::In.ReadToEnd()", command)
        self.assertIn("Set-Clipboard -Value", command)
        self.assertIn("InputEncoding", command)
        self.assertNotIn(text, command)
        self.assertEqual(run.call_args.kwargs["input"], text.encode("utf-8"))

    def test_windows_read_sets_utf8_output_and_preserves_text(self):
        text = "你好\n"
        completed = subprocess.CompletedProcess([], 0, stdout=text.encode("utf-8"), stderr=b"")
        with (
            patch("ttr.clipboard.sys.platform", "win32"),
            patch("subprocess.run", return_value=completed) as run,
        ):
            self.assertEqual(read_clipboard(), text)
        command = run.call_args.args[0][-1]
        self.assertIn("OutputEncoding", command)
        self.assertIn("[Console]::Out.Write((Get-Clipboard -Raw))", command)

    def test_command_failure_preserves_diagnostic(self):
        completed = subprocess.CompletedProcess([], 1, stdout=b"", stderr="无法访问剪贴板".encode())
        with (
            patch("subprocess.run", return_value=completed),
            self.assertRaisesRegex(ClipboardError, "无法访问剪贴板"),
        ):
            _run_write(["clipboard"], "hello")
