"""Legacy text bytes and release publication; no game executable is run."""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app import create_app  # noqa: E402
from content import build, render, text_bytes  # noqa: E402


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(
            (ROOT / "content.example.json").read_text(encoding="utf-8")
        )

    def test_checked_in_samples_match_generator(self):
        for name, body in render(self.raw).items():
            self.assertEqual((ROOT / "public" / name).read_bytes(), body)
            self.assertFalse(body.startswith(b"\xef\xbb\xbf"))
            self.assertNotIn(b"\n", body.replace(b"\r\n", b""))
            body.decode("big5")

    def test_exact_five_fields(self):
        lines = render(self.raw)["server.txt"].decode("big5").splitlines()
        self.assertEqual(lines, ["測試區", "本地測試服 127.0.0.1 3134 3 &"])

    def test_line_endings_and_unrepresentable_text(self):
        self.assertEqual(text_bytes("a\rb\nc\r\n"), b"a\r\nb\r\nc\r\n")
        with self.assertRaises(UnicodeEncodeError):
            text_bytes("announcement 😀")
        with self.assertRaises(ValueError):
            text_bytes("bad\x00text")

    def test_invalid_server_rows_rejected(self):
        for key, value in [
            ("name", "bad name"),
            ("ip", "example.invalid"),
            ("ip", "::1"),
            ("port", True),
            ("port", 65536),
            ("type", "&\nInjected"),
            ("reserve", ""),
        ]:
            raw = copy.deepcopy(self.raw)
            raw["groups"][0]["servers"][0][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                render(raw)

    def test_optional_id_and_unknown_top_level_not_silently_accepted(self):
        raw = copy.deepcopy(self.raw)
        raw["groups"][0]["servers"][0]["serverid"] = 1
        with self.assertRaises(ValueError):
            render(raw)
        self.raw["update_version"] = "9.9.9"
        with self.assertRaises(ValueError):
            render(self.raw)

    def test_duplicate_and_empty_groups_rejected(self):
        self.raw["groups"].append(copy.deepcopy(self.raw["groups"][0]))
        with self.assertRaises(ValueError):
            render(self.raw)
        self.raw["groups"] = []
        with self.assertRaises(ValueError):
            render(self.raw)

    def test_release_serves_exact_bytes_and_unknown_updates_404(self):
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "release"
            build(ROOT / "content.example.json", destination)
            app = create_app(destination / "config.json")
            for name, body in render(self.raw).items():
                response = []
                result = app(
                    {"PATH_INFO": "/" + name, "REQUEST_METHOD": "GET"},
                    lambda status, headers, response=response: response.append(status),
                )
                self.assertEqual(response, ["200 OK"])
                self.assertEqual(b"".join(result), body)
            for path in [
                "/httpupdate.txt",
                "/filemd5.txt",
                "/servernotice.txt",
                "/config.json",
            ]:
                response = []
                app(
                    {"PATH_INFO": path},
                    lambda status, headers, response=response: response.append(status),
                )
                self.assertEqual(response, ["404 Not Found"])
            with self.assertRaises(FileExistsError):
                build(ROOT / "content.example.json", destination)
            self.assertEqual(
                (destination / "server.txt").read_bytes(),
                render(self.raw)["server.txt"],
            )

    def test_invalid_content_creates_no_release(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / "input.json", Path(folder) / "release"
            self.raw["news"] = "😀"
            source.write_text(json.dumps(self.raw), encoding="utf-8")
            with self.assertRaises(UnicodeEncodeError):
                build(source, output)
            self.assertFalse(output.exists())
