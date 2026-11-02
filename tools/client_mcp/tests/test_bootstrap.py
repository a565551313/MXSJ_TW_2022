"""Bootstrap installation and stdio/HTTP dependency contract tests."""

import importlib.util
import json
import os
import socket
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, mock

PATH = Path(__file__).resolve().parents[1] / "bootstrap.py"
spec = importlib.util.spec_from_file_location("client_mcp_bootstrap", PATH)
bootstrap = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bootstrap)


class BootstrapTests(TestCase):
    def test_requirements_cover_http_dependencies(self):
        packages = {package for _, package in bootstrap.REQUIREMENTS}
        self.assertIn("mcp>=1.30.0,<2", packages)
        self.assertIn("uvicorn>=0.31.1", packages)
        self.assertIn("starlette>=0.27", packages)

    def test_check_only_never_installs(self):
        with mock.patch.object(bootstrap, "find_missing", return_value=["mcp"]):
            with mock.patch.object(bootstrap, "install_packages") as install:
                self.assertEqual(bootstrap.main(["--check-only"]), 2)
                install.assert_not_called()

    def test_install_fallback_and_recheck(self):
        results = [SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]
        with mock.patch.object(bootstrap.subprocess, "run", side_effect=results) as run:
            with mock.patch.object(bootstrap, "find_missing", return_value=[]):
                self.assertTrue(bootstrap.install_packages(["mcp>=1.30.0,<2"]))
        self.assertEqual(run.call_count, 2)
        self.assertIn(bootstrap.MIRRORS[1], run.call_args.args[0])
        self.assertIs(run.call_args.kwargs["stdout"], bootstrap.sys.stderr)

    def test_successful_pip_requires_import_recheck(self):
        with mock.patch.object(
            bootstrap.subprocess, "run", return_value=SimpleNamespace(returncode=0)
        ):
            with mock.patch.object(bootstrap, "find_missing", return_value=["mcp"]):
                self.assertFalse(bootstrap.install_packages(["mcp"]))


class LauncherHelperTests(TestCase):
    def test_token_is_created_once_and_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "token.txt"
            first = bootstrap.load_or_create_token(path)
            second = bootstrap.load_or_create_token(path)
        self.assertGreaterEqual(len(first), 16)
        self.assertEqual(first, second)

    def test_pick_port_skips_busy_port(self):
        free = bootstrap.pick_port(18765)
        holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            holder.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            holder.bind(("127.0.0.1", free))
            holder.listen(1)
            self.assertNotEqual(bootstrap.pick_port(free), free)
        finally:
            holder.close()

    def test_find_report_file_prefers_newest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            older = root / "old" / bootstrap.REPORT_NAME
            newer = root / bootstrap.REPORT_NAME
            older.parent.mkdir()
            older.write_text("{}", encoding="utf-8")
            newer.write_text("{}", encoding="utf-8")
            os.utime(older, (1000, 1000))
            os.utime(newer, (2000, 2000))
            found = bootstrap.find_report_file([root])
        self.assertEqual(found, newer)

    def test_client_config_contains_url_and_bearer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = bootstrap.write_client_config(
                "http://127.0.0.1:8765/mcp", "secret", Path(tmp) / "cfg.json"
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
        server = payload["mcpServers"]["mxsj-client"]
        self.assertEqual(server["url"], "http://127.0.0.1:8765/mcp")
        self.assertEqual(server["headers"]["Authorization"], "Bearer secret")

    def test_server_args_pass_report_when_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / bootstrap.REPORT_NAME
            report.write_text("{}", encoding="utf-8")
            args = bootstrap.server_args(8766, "token", report)
        self.assertIn("--report-file", args)
        self.assertEqual(args[args.index("--report-file") + 1], str(report))
        self.assertEqual(args[args.index("--port") + 1], "8766")
