"""守护 runtimes 的字节不被改写：属性规则、免 git 修复、双击入口。"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1]
REPO = TOOL.parent
RUNTS = TOOL / "runtimes"
VMS = ("py25", "py27")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fake_bundle(root: Path, crlf: bool) -> dict:
    """造一套最小 runtimes：3 个文件，清单钉 LF 版本的哈希。"""
    (root / "py25/win-x86").mkdir(parents=True)
    files = {"BUILD.json": b'{\n  "a": 1\n}\n', "LICENSE-x.txt": b"x\ny\n"}
    for name, data in files.items():
        payload = data.replace(b"\n", b"\r\n") if crlf else data
        (root / "py25/win-x86" / name).write_bytes(payload)
    manifest = {
        "schema": 2,
        "compilers": [
            {
                "vm": "py25",
                "root": "py25/win-x86",
                "files": {n: _sha(d) for n, d in files.items()},
            }
        ],
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


class RuntimeCheckoutTest(unittest.TestCase):
    def test_gitattributes_keeps_compiler_files_binary(self):
        """清单逐个钉了 SHA256，任何换行转换都会让自检失败。"""
        rules = (REPO / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("script_editor/runtimes/** -text", rules)

    def test_entries_exist(self):
        self.assertTrue((TOOL / "repair_runtimes.py").is_file())
        self.assertTrue((TOOL / "修复编译器文件.bat").is_file())

    def test_repair_needs_no_git(self):
        """用户机器上 git 不在 PATH（GitHub Desktop 自带但不导出）。"""
        source = (TOOL / "repair_runtimes.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("_git(", source)

    def test_launchers_are_crlf_ascii(self):
        for name in ("修复编译器文件.bat", "检查内置编译器.bat"):
            data = (TOOL / name).read_bytes()
            with self.subTest(name=name):
                self.assertIn(b"\r\n", data)
                self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
                data.decode("ascii")  # cmd 按控制台代码页解析 bat，非 ASCII 会乱码

    def test_check_launcher_retries_after_repair(self):
        data = (TOOL / "检查内置编译器.bat").read_text(encoding="ascii")
        self.assertIn("repair_runtimes.py", data)
        self.assertIn("Re-checking", data)

    def test_repair_restores_crlf_files(self):
        """复现用户状态：文本文件被改成 CRLF，修复后逐字节回到清单值。"""
        import repair_runtimes

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = _fake_bundle(root, crlf=True)
            fixed, intact, broken = repair_runtimes.repair_files(root)
            self.assertEqual(broken, [])
            self.assertEqual(len(fixed), len(manifest["compilers"][0]["files"]))
            self.assertEqual(intact, [])
            for name, expected in manifest["compilers"][0]["files"].items():
                data = (root / "py25/win-x86" / name).read_bytes()
                self.assertNotIn(b"\r\n", data)
                self.assertEqual(_sha(data), expected)

    def test_repair_leaves_intact_files_alone(self):
        import repair_runtimes

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fake_bundle(root, crlf=False)
            before = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
            fixed, intact, broken = repair_runtimes.repair_files(root)
            self.assertEqual((fixed, broken), ([], []))
            self.assertEqual(len(intact), 2)
            after = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_repair_refuses_unrelated_damage(self):
        """真损坏（不是换行）必须原样保留并点名，不能猜着覆盖。"""
        import repair_runtimes

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _fake_bundle(root, crlf=False)
            victim = root / "py25/win-x86/BUILD.json"
            victim.write_bytes(b"totally different bytes\n")
            fixed, intact, broken = repair_runtimes.repair_files(root)
            self.assertEqual(fixed, [])
            self.assertEqual(len(intact), 1)
            self.assertEqual(len(broken), 1)
            self.assertIn("BUILD.json", broken[0])
            self.assertEqual(victim.read_bytes(), b"totally different bytes\n")

    def test_real_runtimes_are_untouched(self):
        """仓库自身：跑一次修复不应改动任何字节。"""
        import repair_runtimes

        before = {p: p.read_bytes() for p in sorted(RUNTS.rglob("*")) if p.is_file()}
        fixed, intact, broken = repair_runtimes.repair_files(RUNTS)
        self.assertEqual((fixed, broken), ([], []))
        manifest = json.loads((RUNTS / "manifest.json").read_text(encoding="utf-8"))
        expected = sum(len(c["files"]) for c in manifest["compilers"])
        self.assertEqual(len(intact), expected)
        after = {p: p.read_bytes() for p in sorted(RUNTS.rglob("*")) if p.is_file()}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
