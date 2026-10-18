"""Real rotating files, process leases, redaction and non-recursive failures."""

from __future__ import annotations

import io
import json
import logging
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mxsj_local_server.core.observability.events import EventLogger
from tests._paths import ROOT

SECRET = "DO_NOT_RECORD_PASSWORD_OR_TICKET"


class EventTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.console = io.StringIO()

    def logger(self, **kwargs):
        events = EventLogger.open(self.root / "logs", **kwargs)
        events.console = self.console
        self.addCleanup(events.close)
        return events

    def test_allowlist_redacts_payload_and_exception_content(self):
        events = self.logger()
        try:
            raise RuntimeError(SECRET)
        except RuntimeError as exc:
            events.emit(
                "account.authenticate",
                outcome="failed",
                error_code="INTERNAL_ERROR",
                exception=exc,
                password=SECRET,
                credential=SECRET,
                ticket=SECRET,
                sql=SECRET,
                request={"secret": SECRET},
                account_name=SECRET,
                name=SECRET,
                reason=SECRET,
                account_id=SECRET,
                trace_id=SECRET,
                operation_id=SECRET,
            )
        for text in (
            self.console.getvalue(),
            (self.root / "logs/server.jsonl").read_text(encoding="utf-8"),
        ):
            self.assertNotIn(SECRET, text)
            row = json.loads(text)
            self.assertNotIn("account_id", row)
            self.assertNotIn("trace_id", row)
            self.assertEqual(len(row["operation_id_sha256"]), 64)
            self.assertEqual(row["exception"]["type"], "RuntimeError")
            self.assertEqual(row["level"], "ERROR")
            self.assertNotIn("request", row)

    def test_json_line_injection_is_not_possible_via_unknown_fields(self):
        events = self.logger()
        events.emit("config.validated", message='x\n{"event":"fake"}', duration_ms=True)
        lines = self.console.getvalue().splitlines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(json.loads(lines[0])["event"], "config.validated")
        self.assertNotIn("duration_ms", json.loads(lines[0]))

    def test_unexpected_event_never_prints_attacker_name(self):
        events = self.logger()
        with patch("mxsj_local_server.core.observability.events.emergency") as fallback:
            events.emit(SECRET)
            events.emit(SECRET)
            self.assertEqual(fallback.call_count, 1)
        self.assertNotIn(SECRET, self.console.getvalue())
        self.assertEqual(events.health()["failures"], 2)

    def test_rotation_retention_and_permissions(self):
        events = self.logger(max_bytes=4096, backups=2)
        for n in range(150):
            events.emit(
                "character.create", account_id=1, character_id=n, trace_id="a" * 32
            )
        files = sorted((self.root / "logs").glob("server.jsonl*"))
        self.assertEqual(len(files), 3)
        for file in files:
            self.assertLessEqual(file.stat().st_size, 4096)
            for line in file.read_text(encoding="utf-8").splitlines():
                self.assertEqual(json.loads(line)["event"], "character.create")
            if os.name != "nt":
                self.assertEqual(file.stat().st_mode & 0o077, 0)

    def test_debug_threshold_is_explicit(self):
        events = self.logger()
        events.emit("database.transaction")
        events.emit(
            "database.transaction", outcome="failed", error_code="STORAGE_ERROR"
        )
        rows = [json.loads(line) for line in self.console.getvalue().splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["level"], "ERROR")

    def test_invalid_limits_rejected(self):
        for options in (
            {"max_bytes": 0},
            {"backups": 0},
            {"max_bytes": True},
            {"backups": 21},
            {"level": "secret"},
        ):
            with self.assertRaises(ValueError):
                self.logger(**options)

    def test_file_failure_is_visible_bounded_and_recovers(self):
        events = self.logger()
        with patch.object(events.handler, "emit", side_effect=OSError(SECRET)):
            with patch(
                "mxsj_local_server.core.observability.events.emergency"
            ) as fallback:
                for _ in range(3):
                    events.emit("character.create")
                self.assertEqual(fallback.call_count, 1)
        self.assertEqual(events.health(), {"failures": 3, "degraded": True})
        self.assertNotIn(SECRET, self.console.getvalue())
        self.assertEqual(len(self.console.getvalue().splitlines()), 3)
        events.emit("character.create")
        self.assertEqual(events.health(), {"failures": 3, "degraded": False})

    def test_real_disk_write_error_uses_no_logging_default_traceback(self):
        events = self.logger()
        with patch.object(events.handler.stream, "write", side_effect=OSError(SECRET)):
            with patch(
                "mxsj_local_server.core.observability.events.emergency"
            ) as fallback:
                events.emit("process.start", outcome="started")
                fallback.assert_called_once()
        self.assertNotIn(SECRET, self.console.getvalue())
        self.assertTrue(events.health()["degraded"])

    def test_console_failure_preserves_file(self):
        events = self.logger()
        with patch.object(self.console, "write", side_effect=OSError(SECRET)):
            with patch(
                "mxsj_local_server.core.observability.events.emergency"
            ) as fallback:
                events.emit("config.validated")
                fallback.assert_called_once()
        row = json.loads((self.root / "logs/server.jsonl").read_text(encoding="utf-8"))
        self.assertEqual(row["event"], "config.validated")
        self.assertNotIn(SECRET, json.dumps(row))

    def test_double_close_and_reconfigure_do_not_add_root_handlers(self):
        before = list(logging.getLogger().handlers)
        events = self.logger()
        events.emit("process.start")
        events.close()
        events.close()
        again = self.logger()
        again.emit("process.stop")
        self.assertEqual(logging.getLogger().handlers, before)
        self.assertEqual(
            len(
                (self.root / "logs/server.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            ),
            2,
        )

    def test_same_directory_is_exclusive_across_processes_and_crash_releases(self):
        events = self.logger()
        script = """
import os, sys
from pathlib import Path
from mxsj_local_server.core.observability.events import EventLogger
try:
    logger = EventLogger.open(Path(sys.argv[1]))
except OSError:
    sys.exit(7)
os._exit(0)
"""

        def run():
            return subprocess.run(
                [sys.executable, "-c", script, str(self.root / "logs")],
                capture_output=True,
                timeout=10,
                env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            )

        self.assertEqual(run().returncode, 7)
        events.close()
        self.assertEqual(run().returncode, 0)
        again = self.logger()  # Lock file remains but crashed process does not own it.
        again.emit("config.validated")

    def test_symlink_or_hardlink_log_target_cannot_overwrite_source(self):
        logdir = self.root / "logs"
        logdir.mkdir()
        source = self.root / "source.bin"
        source.write_bytes(b"preserve")
        target = logdir / "server.jsonl"
        os.link(source, target)
        with self.assertRaises(ValueError):
            self.logger()
        self.assertEqual(source.read_bytes(), b"preserve")
        target.unlink()
        try:
            target.symlink_to(source)
        except OSError:
            self.skipTest("Symbolic links not supported on this host")
        with self.assertRaises(ValueError):
            self.logger()
        self.assertEqual(source.read_bytes(), b"preserve")

    def test_rotation_backup_alias_is_rejected(self):
        logdir = self.root / "logs"
        logdir.mkdir()
        source = self.root / "source.bin"
        source.write_bytes(b"preserve")
        os.link(source, logdir / "server.jsonl.1")
        with self.assertRaises(ValueError):
            self.logger()
        self.assertEqual(source.read_bytes(), b"preserve")

    def test_formatting_failure_and_invalid_shape_do_not_escape(self):
        events = self.logger()
        with patch("mxsj_local_server.core.observability.events.emergency"):
            events.emit([])
            with patch(
                "mxsj_local_server.core.observability.events.json.dumps",
                side_effect=ValueError(SECRET),
            ):
                events.emit("character.create")
        self.assertEqual(events.health()["failures"], 2)
        self.assertNotIn(SECRET, self.console.getvalue())
