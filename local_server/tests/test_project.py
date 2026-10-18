"""The local project must work without any sibling checkout or formal package."""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests._paths import ROOT


class ProjectTests(unittest.TestCase):
    def test_no_formal_import_or_gui_dependency_in_core(self):
        for path in (ROOT / "src").rglob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for name in names:
                    self.assertNotEqual(name.split(".")[0], "mxsj_server", path)
                    if "core" in path.parts:
                        self.assertNotEqual(name.split(".")[0], "PySide6", path)

    def test_entry_points_do_not_reach_sibling_sources(self):
        for name in ("run.py", "bootstrap.py", "local_server.spec", "build_exe.bat"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for forbidden in ("server/src", "../server", "..\\server", "mxsj_server"):
                self.assertNotIn(forbidden, text, name)

    def test_all_local_modules_import(self):
        import importlib
        import pkgutil

        import mxsj_local_server

        for info in pkgutil.walk_packages(
            mxsj_local_server.__path__, mxsj_local_server.__name__ + "."
        ):
            importlib.import_module(info.name)

    def test_copy_only_project_can_check_initialize_and_reopen(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            project = base / "独立本地服 with spaces"
            shutil.copytree(
                ROOT,
                project,
                ignore=shutil.ignore_patterns(
                    ".venv",
                    "__pycache__",
                    "*.egg-info",
                    "var",
                    "config.json",
                    "build",
                    "dist",
                    ".ruff_cache",
                    "启动日志.txt",
                ),
            )
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            env.pop("PYTHONPATH", None)

            def run(*args):
                result = subprocess.run(
                    [sys.executable, "-I", *map(str, args)],
                    cwd=base,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

            run(project / "bootstrap.py", "--check-only")
            self.assertFalse((project / "var").exists())
            config = json.loads(
                (project / "config.example.json").read_text(encoding="utf-8")
            )
            config_path = project / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            run(project / "run.py", "--config", config_path, "init-db")
            run(project / "run.py", "--config", config_path, "check")
            self.assertTrue((project / "var/local.sqlite3").is_file())
            self.assertTrue((project / "var/logs/server.jsonl").is_file())
            self.assertFalse((base / "server").exists())
