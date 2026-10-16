from __future__ import annotations

import importlib.util
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "manual_check_runner", Path(__file__).resolve().parents[1] / "check_manual.py"
)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class GateRunnerTests(unittest.TestCase):
    def run_gate(self, results, args=()):
        output = io.StringIO()
        with (
            patch.object(runner.sys, "argv", ["check_manual.py", *args]),
            patch.object(runner.subprocess, "run", side_effect=results) as run,
            redirect_stdout(output), redirect_stderr(output),
        ):
            status = runner.main()
        return status, run.call_args_list, output.getvalue()

    @staticmethod
    def ok():
        return SimpleNamespace(returncode=0)

    def test_includes_independent_suites_and_strict_validation(self):
        status, calls, _ = self.run_gate([self.ok() for _ in range(6)])
        self.assertEqual(status, 0)
        commands = [c.args[0] for c in calls]
        self.assertIn("--verify-evidence", commands[0])
        self.assertIn("--require-full-inventory", commands[0])
        self.assertIn("test_signature_metadata.py", commands[2])
        self.assertIn("test_recover_entries.py", commands[3])
        self.assertIn("script_manual/script_manual.spec", commands[4])
        self.assertIn("--strict", commands[5])
        self.assertIn("--no-git", commands[5])
        for call in calls:
            self.assertFalse(call.kwargs["check"])
            self.assertEqual(call.kwargs["env"]["PYTHONDONTWRITEBYTECODE"], "1")

    def test_nonzero_gate_fails_overall_but_runs_remaining_gates(self):
        results = [self.ok() for _ in range(6)]
        results[2] = SimpleNamespace(returncode=7)
        status, calls, output = self.run_gate(results)
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 6)
        self.assertIn("FAILED GATES", output)

    def test_missing_executable_is_failure_not_silent_success(self):
        status, calls, output = self.run_gate(
            [OSError("missing synthetic executable"), *[self.ok() for _ in range(5)]]
        )
        self.assertEqual(status, 1)
        self.assertEqual(len(calls), 6)
        self.assertIn("Cannot start gate", output)

    def test_require_gui_is_explicitly_propagated(self):
        status, calls, _ = self.run_gate(
            [self.ok() for _ in range(6)], ["--require-gui"]
        )
        self.assertEqual(status, 0)
        for call in calls:
            self.assertEqual(call.kwargs["env"]["MXSJ_MANUAL_REQUIRE_GUI"], "1")
