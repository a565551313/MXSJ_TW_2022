"""Real HTTP listeners, shared state, access policy and failure boundaries."""

from __future__ import annotations

import copy
import http.client
import json
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from mxsj_web_server.app import create_manager  # noqa: E402
from mxsj_web_server.core.manager import Conflict  # noqa: E402
from mxsj_web_server.core.security.access import client_ip, permitted  # noqa: E402

PASSWORD = "fake-long-password-for-test-only"


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ManagementTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.manager = create_manager(self.root)
        self.addCleanup(lambda: self.manager.close())
        settings = self.manager.snapshot()["settings"]
        ports = [free_port(), free_port()]
        while ports[0] == ports[1]:
            ports[1] = free_port()
        for kind, port in zip(("public", "admin"), ports, strict=True):
            settings[kind].update(port=port, origin=f"http://127.0.0.1:{port}")
        self.manager.save_settings(settings, 0)
        self.manager.set_password(PASSWORD)
        self.cookie, self.csrf = "", ""

    def request(self, kind, path, data=None, headers=None, method=None):
        port = self.manager.snapshot()["services"][kind]["active_config"]["port"]
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=6)
        hdr = {"Cookie": self.cookie, "X-CSRF-Token": self.csrf}
        if data is not None:
            hdr.update(
                {
                    "Content-Type": "application/json",
                    "Origin": f"http://127.0.0.1:{port}",
                }
            )
        hdr.update(headers or {})
        try:
            conn.request(
                method or ("POST" if data is not None else "GET"),
                path,
                body=json.dumps(data).encode() if data is not None else None,
                headers=hdr,
            )
            response = conn.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            conn.close()

    def login(self):
        status, headers, body = self.request(
            "admin", "/api/login", {"password": PASSWORD}
        )
        self.assertEqual(status, 200, body)
        self.cookie = headers["Set-Cookie"].split(";", 1)[0]
        self.csrf = json.loads(body)["csrf"]

    def start(self, kind):
        self.manager.control(kind, "start")

    def revision(self):
        return self.manager.snapshot()["revision"]

    def publish(self):
        state = self.manager.create_release(self.revision())
        identity = state["releases"][0]["id"]
        self.manager.activate(identity, state["revision"])
        return identity

    def test_default_off_and_local_password_required(self):
        self.assertEqual(
            [s["status"] for s in self.manager.snapshot()["services"].values()],
            ["stopped", "stopped"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            other = create_manager(Path(tmp))
            try:
                with self.assertRaises(ValueError):
                    other.control("admin", "start")
            finally:
                other.close()

    def test_single_controller_lock_released_after_close(self):
        with self.assertRaises(OSError):
            create_manager(self.root)
        self.manager.close()
        self.manager = create_manager(self.root)
        self.assertTrue(self.manager.snapshot()["has_password"])

    def test_publication_switch_pause_restart_and_admin_independence(self):
        identity = self.publish()
        self.start("public")
        self.start("admin")
        self.assertEqual(self.request("public", "/news.txt")[0], 200)
        self.manager.control("public", "pause")
        self.assertEqual(self.request("public", "/news.txt")[0], 503)
        self.login()
        self.manager.control("public", "resume")
        self.manager.control("admin", "stop")
        self.assertEqual(self.request("public", "/news.txt")[0], 200)
        self.start("admin")
        self.assertEqual(self.request("admin", "/api/state")[0], 401)
        self.manager.control("public", "restart")
        self.assertEqual(self.manager.snapshot()["active"], identity)
        self.assertEqual(self.request("public", "/news.txt")[0], 200)

    def test_public_has_no_management_and_unknown_update_404(self):
        self.start("public")
        for path in [
            "/api/state",
            "/api/login",
            "/httpupdate.txt",
            "/filemd5.txt",
            "/../management.sqlite3",
        ]:
            self.assertEqual(self.request("public", path)[0], 404)
        self.assertEqual(self.request("public", "/news.txt")[0], 503)

    def test_auth_csrf_origin_host_and_cookie_flags(self):
        self.start("admin")
        self.assertEqual(self.request("admin", "/api/state")[0], 401)
        self.assertEqual(
            self.request(
                "admin",
                "/api/login",
                {"password": PASSWORD},
                {"Origin": "https://evil.invalid"},
            )[0],
            403,
        )
        self.assertEqual(
            self.request("admin", "/", headers={"Host": "evil.invalid"})[0], 403
        )
        self.login()
        state = json.loads(self.request("admin", "/api/state")[2])
        self.assertNotIn("credential", state)
        self.assertEqual(
            self.request(
                "admin",
                "/api/build",
                {"revision": self.revision()},
                {"X-CSRF-Token": "wrong"},
            )[0],
            403,
        )
        status, headers, _ = self.request("admin", "/api/login", {"password": PASSWORD})
        self.assertEqual(status, 200)
        self.assertIn("HttpOnly", headers["Set-Cookie"])
        self.assertIn("SameSite=Strict", headers["Set-Cookie"])
        self.assertEqual(
            self.request("admin", "/api/state")[0], 401
        )  # Login rotates old cookie.

    def test_admin_pause_read_only_local_writes_remain_available(self):
        self.start("admin")
        self.login()
        self.manager.control("admin", "pause")
        self.assertEqual(self.request("admin", "/api/state")[0], 200)
        self.assertEqual(self.request("admin", "/api/preview", {})[0], 200)
        self.assertEqual(
            self.request("admin", "/api/build", {"revision": self.revision()})[0], 423
        )
        self.manager.create_release(self.revision())
        self.manager.control("admin", "resume")
        self.assertEqual(
            self.request("admin", "/api/build", {"revision": self.revision()})[0], 200
        )

    def test_remote_public_control_and_no_admin_control(self):
        self.start("admin")
        self.login()
        status, _, body = self.request("admin", "/api/control", {"action": "start"})
        self.assertEqual(status, 200, body)
        self.assertEqual(
            self.manager.snapshot()["services"]["public"]["status"], "running"
        )
        self.assertEqual(self.request("admin", "/api/admin/stop", {})[0], 404)
        self.assertEqual(
            self.request("admin", "/api/control", {"action": "stop"})[0], 200
        )

    def test_whitelist_deny_priority_expiry_and_ipv6(self):
        policy = {
            "mode": "white",
            "white": [{"cidr": "2001:db8::/32", "expires": 0}],
            "black": [{"cidr": "2001:db8::1/128", "expires": 50}],
        }
        self.assertFalse(permitted("2001:db8::1", policy, 10))
        self.assertTrue(permitted("2001:db8::1", policy, 60))
        self.assertFalse(permitted("127.0.0.1", policy, 60))
        policy["white"] = []
        self.assertFalse(permitted("2001:db8::1", policy, 60))

    def test_forwarded_header_only_from_trusted_peer(self):
        self.assertEqual(client_ip("192.0.2.10", "127.0.0.1", []), "192.0.2.10")
        self.assertEqual(
            client_ip("127.0.0.1", "1.1.1.1, 192.0.2.10", ["127.0.0.1/32"]),
            "192.0.2.10",
        )
        with self.assertRaises(ValueError):
            client_ip("127.0.0.1", "invalid", ["127.0.0.1/32"])

    def test_network_denied_but_local_can_repair(self):
        self.start("admin")
        settings = self.manager.snapshot()["settings"]
        settings["admin"]["mode"] = "white"
        self.manager.save_settings(settings, self.revision())
        self.assertEqual(self.request("admin", "/")[0], 403)
        settings["admin"]["mode"] = "allow"
        self.manager.save_settings(settings, self.revision())
        self.login()

    def test_stale_draft_conflict_and_no_raw_secret_in_logs(self):
        raw = self.manager.snapshot()["draft"]
        revision = self.revision()
        self.manager.save_draft(raw, revision)
        with self.assertRaises(Conflict):
            self.manager.save_draft(raw, revision)
        self.start("admin")
        self.login()
        self.request("admin", "/api/state?password=secret-query")
        text = (self.root / "web_server.jsonl").read_text(encoding="utf-8")
        for secret in [PASSWORD, "secret-query", self.cookie, self.csrf]:
            self.assertNotIn(secret, text)

    def test_commit_failure_never_changes_published_content(self):
        old = self.publish()
        new = copy.deepcopy(self.manager.snapshot()["draft"])
        new["news"] = "新版測試"
        self.manager.save_draft(new, self.revision())
        state = self.manager.create_release(self.revision())
        identity = next(r["id"] for r in state["releases"] if r["id"] != old)
        with patch.object(
            self.manager.store, "commit", side_effect=OSError("disk failure")
        ):
            with self.assertRaises(OSError):
                self.manager.activate(identity, self.revision())
        self.assertEqual(self.manager.snapshot()["active"], old)
        self.start("public")
        self.assertNotEqual(
            self.request("public", "/news.txt")[2], "新版測試\r\n".encode("big5")
        )

    def test_log_failure_does_not_replace_committed_success(self):
        with patch.object(
            self.manager.events.handler, "emit", side_effect=OSError("disk failure")
        ):
            self.manager.create_release(self.revision())
        self.assertEqual(len(self.manager.snapshot()["releases"]), 1)
        self.assertTrue(self.manager.events.snapshot()["degraded"])

    def test_recovery_keeps_active_content_not_listeners_or_sessions(self):
        identity = self.publish()
        self.start("admin")
        self.login()
        self.manager.close()
        self.manager = create_manager(self.root)
        self.assertEqual(self.manager.snapshot()["active"], identity)
        self.assertEqual(self.manager.snapshot()["sessions"], 0)
        self.assertEqual(
            self.manager.snapshot()["services"]["admin"]["status"], "stopped"
        )

    def test_port_conflict_does_not_stop_other_service(self):
        self.start("public")
        port = self.manager.snapshot()["settings"]["admin"]["port"]
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", port))
            sock.listen()
            with self.assertRaises(ValueError):
                self.start("admin")
        self.assertEqual(
            self.manager.snapshot()["services"]["public"]["status"], "running"
        )
        self.assertEqual(
            self.manager.snapshot()["services"]["admin"]["status"], "stopped"
        )

    def test_parallel_local_and_remote_service_actions_do_not_deadlock(self):
        self.start("admin")
        self.login()
        errors = []

        def remote():
            try:
                self.request("admin", "/api/control", {"action": "start"})
            except Exception as exc:
                errors.append(type(exc).__name__)

        thread = threading.Thread(target=remote)
        thread.start()
        self.manager.control("public", "stop")
        thread.join(timeout=7)
        self.assertFalse(thread.is_alive())
        self.assertFalse(errors)

    def test_login_rate_limit_and_body_limit(self):
        self.start("admin")
        for _ in range(5):
            self.assertEqual(
                self.request("admin", "/api/login", {"password": "wrong"})[0], 401
            )
        self.assertEqual(
            self.request("admin", "/api/login", {"password": PASSWORD})[0], 429
        )
        self.assertEqual(
            self.request(
                "admin", "/api/login", {}, {"Content-Length": str(2 * 1024 * 1024)}
            )[0],
            413,
        )

    def test_password_reset_and_expiry_revoke_sessions(self):
        self.start("admin")
        self.login()
        for session in self.manager.sessions.entries.values():
            session["expires"] = 0
        self.assertEqual(self.request("admin", "/api/state")[0], 401)
        self.login()
        self.manager.set_password("a-new-fake-long-password")
        self.assertEqual(self.request("admin", "/api/state")[0], 401)

    def test_admin_external_http_rejected_and_https_cookie_secure(self):
        from mxsj_web_server.core.configuration.settings import validate
        from mxsj_web_server.web.admin.api import cookie

        settings = self.manager.snapshot()["settings"]
        settings["admin"]["host"] = "0.0.0.0"
        with self.assertRaises(ValueError):
            validate(settings)
        settings["admin"]["origin"] = "HTTPS://ADMIN.EXAMPLE.COM:443"
        normalized = validate(settings)
        self.assertEqual(normalized["admin"]["origin"], "https://admin.example.com")
        self.assertIn("; Secure", cookie("fake", normalized["admin"]["origin"]))

    def test_runtime_rotation_retention_and_private_permissions(self):
        import os

        events = self.manager.events
        events.handler.maxBytes = 4096
        events.handler.backupCount = 2
        for _ in range(100):
            events.emit("access", service="public", path="/news.txt", status=200)
        files = list(self.root.glob("web_server.jsonl*"))
        self.assertEqual(len(files), 3)
        for path in files:
            for line in path.read_text(encoding="utf-8").splitlines():
                self.assertIsInstance(json.loads(line), dict)
            if os.name != "nt":
                self.assertEqual(path.stat().st_mode & 0o077, 0)

        events.close()
        events.emit("access", service="public", path="/news.txt", status=200)
        self.assertIsNone(events.handler.stream)  # Must never reopen after shutdown.

    def test_public_head_etag_and_conditional_get(self):
        self.publish()
        self.start("public")
        status, headers, body = self.request("public", "/news.txt")
        self.assertEqual(status, 200)
        status, head, empty = self.request("public", "/news.txt", method="HEAD")
        self.assertEqual(status, 200)
        self.assertEqual(empty, b"")
        self.assertEqual(head["Content-Length"], str(len(body)))
        self.assertEqual(
            self.request(
                "public", "/news.txt", headers={"If-None-Match": headers["ETag"]}
            )[0],
            304,
        )

    def test_browser_routes_publish_conflict_and_rollback(self):
        old = self.publish()
        self.start("public")
        original = self.request("public", "/news.txt")[2]
        self.start("admin")
        self.login()
        content = self.manager.snapshot()["draft"]
        content["news"] = "遠端測試公告"
        revision = self.revision()
        self.assertEqual(
            self.request(
                "admin", "/api/draft", {"content": content, "revision": revision}
            )[0],
            200,
        )
        self.assertEqual(
            self.request(
                "admin", "/api/draft", {"content": content, "revision": revision}
            )[0],
            409,
        )
        self.assertEqual(
            self.request("admin", "/api/build", {"revision": self.revision()})[0], 200
        )
        identity = next(
            r["id"] for r in self.manager.snapshot()["releases"] if r["id"] != old
        )
        self.assertEqual(
            self.request(
                "admin", "/api/activate", {"id": identity, "revision": self.revision()}
            )[0],
            200,
        )
        self.assertEqual(
            self.request("public", "/news.txt")[2], "遠端測試公告\r\n".encode("big5")
        )
        self.assertEqual(
            self.request(
                "admin", "/api/activate", {"id": old, "revision": self.revision()}
            )[0],
            200,
        )
        self.assertEqual(self.request("public", "/news.txt")[2], original)
        _, headers, _ = self.request("admin", "/")
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])

    def test_remote_cannot_change_admin_listener(self):
        self.start("admin")
        self.login()
        settings = self.manager.snapshot()["settings"]
        settings["admin"]["port"] = free_port()
        self.assertEqual(
            self.request(
                "admin",
                "/api/settings",
                {"settings": settings, "revision": self.revision()},
            )[0],
            400,
        )

    def test_corrupt_state_is_not_silently_reinitialized(self):
        import sqlite3

        self.manager.close()
        db = sqlite3.connect(self.root / "management.sqlite3")
        try:
            with db:
                db.execute("UPDATE state SET body='corrupt' WHERE id=1")
            with self.assertRaises(ValueError):
                create_manager(self.root)
            self.assertEqual(
                db.execute("SELECT body FROM state").fetchone()[0], "corrupt"
            )
        finally:
            db.close()

    def test_https_admin_rejects_direct_nonproxy_transport(self):
        settings = self.manager.snapshot()["settings"]
        settings["admin"]["origin"] = "https://admin.example.invalid"
        self.manager.save_settings(settings, self.revision())
        self.start("admin")
        self.assertEqual(
            self.request("admin", "/", headers={"Host": "admin.example.invalid"})[0],
            403,
        )
        settings["admin"]["trusted_proxies"] = ["127.0.0.1/32"]
        self.manager.save_settings(settings, self.revision())
        self.assertEqual(
            self.request("admin", "/", headers={"Host": "admin.example.invalid"})[0],
            200,
        )
