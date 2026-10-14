from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from script_editor.native_cli import main


class CliTests(unittest.TestCase):
    def args(self):
        return [
            "--archive",
            "source.fls",
            "--archive-sha256",
            "0" * 64,
            "--entry-index",
            "0",
            "--entry-identity",
            "00000064",
            "--source",
            "own.py",
            "--module-filename",
            "module.py",
            "--compiler",
            "python.exe",
            "--vm",
            "py25",
            "--output",
            "new.fls",
        ]

    def test_no_source_confirmation_never_launches_compiler(self):
        with patch("script_editor.native_cli.inspect_compiler") as inspect:
            with contextlib.redirect_stderr(io.StringIO()) as errors:
                self.assertEqual(main(self.args()), 2)
            self.assertIn("源码来源", errors.getvalue())
            inspect.assert_not_called()

    def test_help_without_qt(self):
        with contextlib.redirect_stdout(io.StringIO()) as text:
            with self.assertRaises(SystemExit) as result:
                main(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertIn("--confirm-authored-source", text.getvalue())
