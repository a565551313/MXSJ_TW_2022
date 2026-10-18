"""Portable publication contract tests; never access the game client or network."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from wsgiref.util import setup_testing_defaults
from wsgiref.validate import validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
DATA = ROOT / "src/mxsj_web_server/data"
from mxsj_web_server.core.publication import create_app  # noqa: E402  # Source checkout.


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "public").mkdir()
        self.body = "測試公告".encode("big5")
        (self.root / "public/news.txt").write_bytes(self.body)
        (self.root / "public/private.txt").write_text("not published", encoding="utf-8")
        self.config = self.root / "config.json"
        self.raw = {
            "content_root": "public",
            "resources": [
                {
                    "url": "/news.txt",
                    "file": "news.txt",
                    "content_type": "text/plain",
                    "max_age": 0,
                },
            ],
        }

    def app(self):
        self.config.write_text(json.dumps(self.raw), encoding="utf-8")
        return create_app(self.config)

    def request(self, app, path="/news.txt", method="GET", **extra):
        env = {}
        setup_testing_defaults(env)
        env.update(PATH_INFO=path, REQUEST_METHOD=method, QUERY_STRING="")
        env.update(extra)
        result = []
        response = validator(app)(
            env, lambda status, headers: result.extend([status, dict(headers)])
        )
        try:
            body = b"".join(response)
        finally:
            response.close()
        return *result, body

    def test_exact_bytes_no_implicit_encoding(self):
        status, headers, body = self.request(self.app())
        self.assertEqual(status, "200 OK")
        self.assertEqual(body, self.body)
        self.assertEqual(headers["Content-Length"], str(len(body)))

    def test_head(self):
        status, headers, body = self.request(self.app(), method="HEAD")
        self.assertEqual(status, "200 OK")
        self.assertEqual(body, b"")
        self.assertEqual(headers["Content-Length"], str(len(self.body)))

    def test_conditional_get(self):
        app = self.app()
        _, headers, _ = self.request(app)
        status, headers, body = self.request(
            app, HTTP_IF_NONE_MATCH="W/" + headers["ETag"]
        )
        self.assertEqual(status, "304 Not Modified")
        self.assertEqual(body, b"")
        self.assertNotIn("Content-Length", headers)

    def test_unpublished_and_traversal_are_not_served(self):
        app = self.app()
        for path in [
            "/",
            "/private.txt",
            "/../config.json",
            "/%2e%2e/config.json",
            "/server.txt",
        ]:
            self.assertEqual(self.request(app, path)[0], "404 Not Found")

    def test_write_methods_rejected(self):
        for method in ["POST", "PUT", "DELETE", "TRACE"]:
            self.assertEqual(
                self.request(self.app(), method=method)[0], "405 Method Not Allowed"
            )

    def test_health_is_not_game_health(self):
        _, headers, body = self.request(self.app(), "/healthz")
        self.assertEqual(json.loads(body)["service"], "web_server")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_snapshot_changes_only_on_restart(self):
        app = self.app()
        (self.root / "public/news.txt").write_bytes(b"new release")
        self.assertEqual(self.request(app)[2], self.body)
        self.assertEqual(self.request(self.app())[2], b"new release")

    def test_invalid_config_fails_closed(self):
        for key, value in [
            ("file", "../config.json"),
            ("file", "C:\\secret"),
            ("content_type", "text/plain\r\nInjected: yes"),
            ("max_age", True),
            ("url", "/healthz"),
        ]:
            with self.subTest(key=key, value=value):
                original = self.raw["resources"][0][key]
                self.raw["resources"][0][key] = value
                with self.assertRaises(ValueError):
                    self.app()
                self.raw["resources"][0][key] = original

    def test_duplicate_url_rejected(self):
        self.raw["resources"].append(dict(self.raw["resources"][0]))
        with self.assertRaises(ValueError):
            self.app()

    def test_hardlink_rejected(self):
        path = self.root / "public/news.txt"
        os.link(path, self.root / "other.txt")
        with self.assertRaises(ValueError):
            self.app()

    def test_symlink_rejected(self):
        path = self.root / "public/news.txt"
        path.unlink()
        try:
            path.symlink_to(self.root / "public/private.txt")
        except OSError:
            self.skipTest("Host does not permit symlinks")
        with self.assertRaises(ValueError):
            self.app()

    def test_check_only_has_no_listener_or_file_writes(self):
        self.app()
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "run.py"),
                "--config",
                str(self.config),
                "--check-only",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("no server started", result.stdout)

    def test_query_never_changes_path_or_response(self):
        status, _, body = self.request(
            self.app(), QUERY_STRING="file=private.txt&token=secret"
        )
        self.assertEqual(status, "200 OK")
        self.assertEqual(body, self.body)

    def test_oversized_file_and_missing_file_fail_startup(self):
        path = self.root / "public/news.txt"
        with path.open("wb") as stream:
            stream.truncate(8 * 1024 * 1024 + 1)
        with self.assertRaises(ValueError):
            self.app()
        path.unlink()
        with self.assertRaises(FileNotFoundError):
            self.app()
