"""Project standards and entry-point regressions; no Qt/display dependency."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mxsj_web_server import __version__  # noqa: E402  # Source checkout.
from mxsj_web_server.app import resource_directory  # noqa: E402  # Source checkout.
from mxsj_web_server.core.paths import (  # noqa: E402  # Source checkout.
    initialize_example,
    user_directory,
)

spec = importlib.util.spec_from_file_location("web_bootstrap", ROOT / "bootstrap.py")
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class ProjectTests(unittest.TestCase):
    def test_versions_and_python_floor(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertEqual(re.search(r'^version = "([^"]+)"', text, re.M)[1], __version__)
        self.assertIn(__version__, (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn('requires-python = ">=3.10"', text)
        for path in [*ROOT.glob("*.py"), *(ROOT / "src").rglob("*.py")]:
            ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 10))

    def test_core_does_not_import_gui_or_network_runner(self):
        for path in (ROOT / "src/mxsj_web_server/core").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                self.assertFalse(any("PySide6" in m or ".gui" in m for m in modules))
                self.assertNotIn("mxsj_web_server.app", modules)

    def test_bat_scripts_ascii_crlf_and_fail_stop(self):
        for name in ["启动Web服务.bat", "build_exe.bat"]:
            data = (ROOT / name).read_bytes()
            data.decode("ascii")
            self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
            self.assertIn(b'cd /d "%~dp0"', data)
            self.assertIn(b"pause", data)
            self.assertIn(b"where py", data)
            self.assertIn(b"where python", data)

    def test_profile_paths_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            self.assertEqual(user_directory(None, home), home / "MXSJWebServer")
            self.assertEqual(
                user_directory(str(home / "appdata"), home),
                home / "appdata/MXSJWebServer",
            )
            output = home / "中文 空格"
            config = initialize_example(resource_directory(), output)
            self.assertEqual(
                json.loads(config.read_text(encoding="utf-8"))["content_root"], "public"
            )
            with self.assertRaises(FileExistsError):
                initialize_example(resource_directory(), output)

    def test_frozen_resources_are_not_user_config(self):
        with (
            patch.object(sys, "frozen", True, create=True),
            patch.object(sys, "_MEIPASS", "/bundle", create=True),
        ):
            self.assertEqual(resource_directory(), Path("/bundle/mxsj_web_server/data"))
        self.assertNotEqual(resource_directory(), user_directory(None, Path.home()))

    def test_bootstrap_check_has_no_profile_or_listener(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(ROOT / "bootstrap.py"), "--check-only"],
                env={**os.environ, "APPDATA": tmp, "PYTHONDONTWRITEBYTECODE": "1"},
                capture_output=True,
                timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((Path(tmp) / "MXSJWebServer").exists())

    def test_old_python_rejected_without_dependencies(self):
        with (
            patch.object(bootstrap.sys, "version_info", (3, 9)),
            patch.object(bootstrap, "ensure_dependencies") as dep,
        ):
            self.assertEqual(bootstrap.main(["--check-only"]), 2)
            dep.assert_not_called()

    def test_dependency_recheck_and_mirror_order(self):
        missing = [("fake", "fake-package")]
        success = subprocess.CompletedProcess([], 0)
        with (
            patch.object(
                bootstrap, "find_missing", side_effect=[missing, missing, missing, []]
            ),
            patch.object(bootstrap.subprocess, "run", return_value=success) as run,
        ):
            self.assertTrue(bootstrap.ensure_dependencies())
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(len(commands), 4)
        self.assertNotIn("--index-url", commands[1])
        self.assertIn(bootstrap.MIRRORS[1], commands[2])
        self.assertIn(bootstrap.MIRRORS[2], commands[3])
        self.assertTrue(all(cmd[0] == sys.executable for cmd in commands))

    def test_bootstrap_exception_logs_trace_and_returns_two(self):
        with (
            patch.object(
                bootstrap,
                "ensure_dependencies",
                side_effect=RuntimeError("fake startup"),
            ),
            patch.object(bootstrap, "log_failure") as log,
        ):
            self.assertEqual(bootstrap.main(["--check-only"]), 2)
            self.assertIn("Traceback", log.call_args.args[0])

    def test_bootstrap_passes_arguments(self):
        with patch("mxsj_web_server.app.main", return_value=0) as app:
            self.assertEqual(
                bootstrap.main(["--config", "test.json", "--port", "8081"]), 0
            )
            app.assert_called_once_with(
                ["--config", "test.json", "--port", "8081"], raise_errors=True
            )

    def test_independent_copy_with_chinese_space_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "中文 Web 服务"
            shutil.copytree(
                ROOT,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "var", "dist", "build", "*.egg-info"
                ),
            )
            env = {
                **os.environ,
                "PYTHONPATH": str(target / "src"),
                "PYTHONDONTWRITEBYTECODE": "1",
            }
            commands = [
                [str(target / "bootstrap.py"), "--check-only"],
                ["-m", "mxsj_web_server", "--version"],
                [
                    str(target / "run.py"),
                    "--init-example",
                    str(Path(tmp) / "配置 数据"),
                ],
                [
                    str(target / "run.py"),
                    "--config",
                    str(Path(tmp) / "配置 数据/config.json"),
                    "--check-only",
                ],
                [
                    str(target / "content.py"),
                    "--source",
                    str(Path(tmp) / "配置 数据/content.json"),
                    "--output",
                    str(Path(tmp) / "发布 001"),
                ],
            ]
            for command in commands:
                result = subprocess.run(
                    [sys.executable, *command],
                    cwd=tmp,
                    env=env,
                    capture_output=True,
                    timeout=15,
                )
                self.assertEqual(result.returncode, 0, (command, result.stderr))

    def test_spec_modes_are_structurally_valid(self):
        # This checks spec wiring with stand-ins, NOT a successful EXE build.
        import types

        hooks = types.ModuleType("PyInstaller.utils.hooks")
        hooks.collect_submodules = lambda package: [package + ".app"]
        for single in (False, True):
            calls = {}

            def analysis(*args, _calls=calls, **kwargs):
                _calls["analysis"] = kwargs
                return types.SimpleNamespace(pure=[], scripts=[], binaries=[], datas=[])

            def exe(*args, _calls=calls, **kwargs):
                _calls["exe"] = kwargs
                return "exe"

            def collect(*args, _calls=calls, **kwargs):
                _calls["collect"] = kwargs

            namespace = {
                "SPECPATH": str(ROOT),
                "Analysis": analysis,
                "PYZ": lambda _: None,
                "EXE": exe,
                "COLLECT": collect,
            }
            with (
                patch.dict(sys.modules, {"PyInstaller.utils.hooks": hooks}),
                patch.dict(os.environ, {"WEB_SERVER_ONEFILE": "1" if single else "0"}),
            ):
                exec(
                    compile(
                        (ROOT / "web_server.spec").read_text(encoding="utf-8"),
                        "web_server.spec",
                        "exec",
                    ),
                    namespace,
                )
            self.assertEqual(calls["exe"]["exclude_binaries"], not single)
            self.assertEqual("collect" in calls, not single)
            self.assertTrue(calls["exe"]["console"])
            self.assertEqual(calls["analysis"]["datas"][0][1], "mxsj_web_server/data")

    def test_source_http_health_and_clean_shutdown(self):
        import http.client
        import threading
        from wsgiref.simple_server import make_server

        from mxsj_web_server.app import SafeHandler
        from mxsj_web_server.core.publication import create_app

        server = make_server(
            "127.0.0.1",
            0,
            create_app(resource_directory() / "config.example.json"),
            handler_class=SafeHandler,
        )
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            connection = http.client.HTTPConnection(
                "127.0.0.1", server.server_port, timeout=5
            )
            try:
                connection.request("GET", "/healthz")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read())["service"], "web_server")
            finally:
                connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
        self.assertFalse(thread.is_alive())
