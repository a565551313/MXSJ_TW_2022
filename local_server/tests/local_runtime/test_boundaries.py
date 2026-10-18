"""Prevent SQLite/local-specific branches from leaking into shared business."""

from __future__ import annotations

import ast
import unittest

from tests._paths import ROOT


class BoundaryTests(unittest.TestCase):
    def test_shared_business_has_no_driver_or_old_mock_dependency(self):
        base = ROOT / "src/mxsj_local_server/core/modules"
        paths = [
            base / module / layer / filename
            for module, layer, filename in (
                ("account", "application", "service.py"),
                ("account", "domain", "security.py"),
                ("character", "application", "service.py"),
                ("character", "domain", "creation.py"),
            )
        ]
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for name in names:
                    self.assertFalse(
                        any(
                            part in name.removeprefix("mxsj_local_server.core.")
                            for part in (
                                "sqlite",
                                "psycopg",
                                "asyncpg",
                                "socket",
                                "mock_server",
                                "local_server",
                                "transport",
                                "protocol",
                            )
                        ),
                        (path, name),
                    )

    def test_local_launcher_does_not_import_mock_or_patch_client(self):
        text = (ROOT / "run.py").read_text(encoding="utf-8")
        for forbidden in ("mock_server", "ensure_client_ready", "patch_script_fls"):
            self.assertNotIn(forbidden, text)

    def test_storage_ports_do_not_expose_sql_or_connections(self):
        text = (ROOT / "src/mxsj_local_server/core/persistence/ports.py").read_text(
            encoding="utf-8",
        )
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.assertNotIn(node.name, {"execute", "cursor", "connection"})
        self.assertNotIn("import sqlite3", text)
