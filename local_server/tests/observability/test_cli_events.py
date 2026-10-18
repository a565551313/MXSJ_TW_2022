"""CLI log setup precedes database creation; old configurations remain valid."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._paths import ROOT


class CliEventsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = json.loads(
            (ROOT / "config.example.json").read_text(encoding="utf-8")
        )
        self.config["database"] = "db.sqlite3"
        self.path = self.root / "config.json"

    def run_cli(self, command="init-db"):
        self.path.write_text(json.dumps(self.config), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "run.py"),
                "--config",
                str(self.path),
                command,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )

    def test_legacy_config_and_repeated_cli_open(self):
        self.config.pop("logging")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("check")
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [
            json.loads(line)
            for line in (self.root / "var/logs/server.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        self.assertEqual(sum(r["event"] == "process.start" for r in rows), 2)
        self.assertTrue(any(r["event"] == "database.initialize" for r in rows))
        self.assertTrue(any(r["event"] == "database.check" for r in rows))

    def test_unopenable_log_directory_does_not_create_db(self):
        (self.root / "not_a_directory").write_text("preserve", encoding="utf-8")
        self.config["logging"]["directory"] = "not_a_directory"
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "db.sqlite3").exists())
        self.assertIn('"event":"process.failed"', result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_invalid_config_secret_not_in_error(self):
        self.config["logging"]["level"] = "SECRET_BAD_CONFIG"
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "db.sqlite3").exists())
        self.assertNotIn("SECRET_BAD_CONFIG", result.stdout + result.stderr)
