"""发布打包工具的回归：校验清单不能自指，同一内容两次打包必须逐字节相同。"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
import zipfile
from hashlib import sha256 as _sha256
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reg_release", HERE / "make_release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


def sha256_of(data: bytes) -> str:
    return _sha256(data).hexdigest()


def fill(stage: Path) -> None:
    (stage / "data").mkdir(parents=True)
    (stage / "data/script.fls").write_bytes(b"0SLF" + b"\x01" * 40)
    (stage / "README.txt").write_text("说明\n", encoding="utf-8")
    (stage / "\u6d4b\u8bd5\u8bf4\u660e-TESTING.md").write_bytes(b"doc\n")
    (stage / "empty.txt").write_bytes(b"")
    stale = "\u4e0a\u4e00\u6b21\u7684\u810f\u6587\u4ef6\n"
    (stage / "SHA256SUMS.txt").write_text(stale, encoding="utf-8")


class MakeReleaseTest(unittest.TestCase):
    def test_sums_exclude_their_own_file_and_verify(self):
        with tempfile.TemporaryDirectory(prefix="mx-release-") as tmp:
            stage = Path(tmp) / "stage"
            stage.mkdir()
            fill(stage)
            out = Path(tmp) / "pkg.zip"
            names = release.build_zip(stage, out)
            self.assertEqual(
                names,
                [
                    "README.txt",
                    "data/script.fls",
                    "empty.txt",
                    "\u6d4b\u8bd5\u8bf4\u660e-TESTING.md",
                    "SHA256SUMS.txt",
                ],
            )
            text = (stage / "SHA256SUMS.txt").read_text(encoding="utf-8")
            self.assertNotIn("SHA256SUMS.txt  ", text)
            self.assertIn(release.sha256_file(stage / "data/script.fls"), text)
            # 空文件也必須進清單（不允許按大小偷懶跳過）
            self.assertEqual(release.check_zip(out)["empty.txt"], sha256_of(b""))

    def test_same_inputs_produce_byte_identical_zip(self):
        with tempfile.TemporaryDirectory(prefix="mx-release-") as tmp:
            digests = []
            for run in ("a", "b"):
                stage = Path(tmp) / run / "stage"
                stage.mkdir(parents=True)
                fill(stage)
                out = Path(tmp) / run / "pkg.zip"
                release.build_zip(stage, out)
                digests.append(hashlib.sha256(out.read_bytes()).hexdigest())
            self.assertEqual(digests[0], digests[1])

    def test_self_referencing_sums_are_rejected(self):
        with tempfile.TemporaryDirectory(prefix="mx-release-") as tmp:
            out = Path(tmp) / "pkg.zip"
            with zipfile.ZipFile(out, "w") as archive:
                archive.writestr("data/script.fls", b"0SLF")
                archive.writestr("SHA256SUMS.txt", "x" * 64 + "  SHA256SUMS.txt\n")
            with self.assertRaises(SystemExit) as ctx:
                release.check_zip(out)
            self.assertIn("自指哈希", str(ctx.exception))

    def test_mismatched_member_fails_the_check(self):
        with tempfile.TemporaryDirectory(prefix="mx-release-") as tmp:
            stage = Path(tmp) / "stage"
            stage.mkdir()
            fill(stage)
            out = Path(tmp) / "pkg.zip"
            release.build_zip(stage, out)
            with zipfile.ZipFile(out) as archive:
                good = archive.read("data/script.fls")
            with zipfile.ZipFile(out, "w") as archive:
                archive.writestr("data/script.fls", good + b"tampered")
            with self.assertRaises(SystemExit):
                release.check_zip(out)

    def test_cli_reports_hashes(self):
        with tempfile.TemporaryDirectory(prefix="mx-release-") as tmp:
            stage = Path(tmp) / "stage"
            stage.mkdir()
            fill(stage)
            out = Path(tmp) / "pkg.zip"
            script = str(HERE / "make_release.py")
            built = subprocess.run(
                [sys.executable, script, "--stage", str(stage), "--zip", str(out)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
            self.assertIn("sha256=", built.stdout)
            checked = subprocess.run(
                [sys.executable, script, "--check", str(out)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
            self.assertIn("校验通过", checked.stdout)


if __name__ == "__main__":
    unittest.main()
