"""守护 runtimes 的字节不被改写：.gitattributes 规则与双击修复入口。"""

from __future__ import annotations

import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1]
REPO = TOOL.parent
RUNTS = TOOL / "runtimes"
VMS = ("py25", "py27")


class RuntimeCheckoutTest(unittest.TestCase):
    def test_gitattributes_keeps_compiler_files_binary(self):
        """清单逐个钉了 SHA256，任何换行转换都会让自检失败。"""
        rules = (REPO / ".gitattributes").read_text(encoding="utf-8").splitlines()
        self.assertIn("script_editor/runtimes/*/win-x86/** -text", rules)

    def test_repair_entry_points_exist(self):
        self.assertTrue((TOOL / "repair_runtimes.py").is_file())
        self.assertTrue((TOOL / "修复编译器文件.bat").is_file())

    def test_repair_launcher_is_crlf_and_ascii(self):
        data = (TOOL / "修复编译器文件.bat").read_bytes()
        self.assertIn(b"\r\n", data)
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        data.decode("ascii")  # 非 ASCII 在 cmd 控制台代码页下会乱码

    def test_check_launcher_hint_survives(self):
        data = (TOOL / "检查内置编译器.bat").read_bytes()
        self.assertIn(b"SHA256 mismatch", data)
        data.decode("ascii")

    def test_pinned_text_files_are_lf_in_index(self):
        """索引里的 BUILD.json 保持 LF：有仓库时直接用 git 读，没有就跳过。"""
        try:
            import subprocess

            out = subprocess.run(
                [
                    "git",
                    "-C",
                    str(REPO),
                    "show",
                    "HEAD:script_editor/runtimes/py25/win-x86/BUILD.json",
                ],
                capture_output=True,
                check=True,
                timeout=120,
            ).stdout
        except (OSError, subprocess.SubprocessError):
            self.skipTest("没有可用的 git 仓库")
        self.assertNotIn(b"\r\n", out)
        self.assertIn(b'"toolchain"', out)


if __name__ == "__main__":
    unittest.main()
