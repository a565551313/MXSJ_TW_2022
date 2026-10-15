from __future__ import annotations

import importlib.util
import unittest
from unittest.mock import patch

from support import TOOL

spec = importlib.util.spec_from_file_location(
    "manual_bootstrap_test", TOOL / "bootstrap.py"
)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(unittest.TestCase):
    def test_wrong_version_is_dependency_failure(self):
        with patch.object(bootstrap.importlib.metadata, "version", return_value="0"):
            self.assertEqual(len(bootstrap.missing_dependencies()), 2)

    def test_missing_dependency_is_installable(self):
        with patch.object(
            bootstrap.importlib, "import_module", side_effect=ImportError
        ):
            self.assertEqual(len(bootstrap.missing_dependencies()), 2)

    def test_mirrors_tried_in_order_on_pip_failure(self):
        class Result:
            returncode = 1

        with patch.object(
            bootstrap, "missing_dependencies", return_value=["fixture==1"]
        ):
            with patch.object(
                bootstrap.subprocess, "run", return_value=Result()
            ) as run:
                with patch("builtins.print"):
                    self.assertFalse(bootstrap.ensure_dependencies())
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(len(commands), 5)  # pip check + ensurepip + 3 mirrors
        self.assertNotIn("--index-url", commands[2])
        self.assertIn(bootstrap.MIRRORS[1], commands[3])
        self.assertIn(bootstrap.MIRRORS[2], commands[4])

    def test_check_only_failure_returns_two_without_prompt(self):
        with patch.object(
            bootstrap, "ensure_dependencies", side_effect=RuntimeError("fixture")
        ):
            with (
                patch.object(bootstrap, "log_failure") as log,
                patch("builtins.input") as prompt,
                patch("builtins.print"),
            ):
                self.assertEqual(bootstrap.main(["--check-only"]), 2)
                log.assert_called_once()
                prompt.assert_not_called()

    def test_batch_files_are_ascii_crlf(self):
        attributes = (TOOL / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes)
        self.assertIn("*.bat text eol=crlf", attributes)
        for name in ("启动脚本手册.bat", "build_exe.bat"):
            raw = (TOOL / name).read_bytes()
            raw.decode("ascii")
            self.assertIn(b"chcp 65001", raw)
            self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
