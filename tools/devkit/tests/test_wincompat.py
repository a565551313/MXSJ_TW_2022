"""wincompat 单元测试：``python3 -m unittest discover -s tools/devkit/tests -v``。"""

from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from pathlib import Path

DEVKIT = Path(__file__).resolve().parents[1]
if str(DEVKIT) not in sys.path:
    sys.path.insert(0, str(DEVKIT))

import check_windows_compat  # noqa: E402
from wincompat import CheckOptions, Severity, run_checks  # noqa: E402
from wincompat.batch import check_batch_file  # noqa: E402
from wincompat.filenames import check_paths  # noqa: E402
from wincompat.model import RULES  # noqa: E402
from wincompat.pysource import check_python_source  # noqa: E402


def codes(findings) -> list[str]:
    return sorted(f.code for f in findings)


def py(rel: str, body: str):
    return check_python_source(rel, textwrap.dedent(body))


class FilenameTests(unittest.TestCase):
    def test_clean_paths_pass(self):
        self.assertEqual(check_paths(["a/b.txt", "c/d_e.py", "中文/文件.md"]), [])

    def test_illegal_characters(self):
        found = check_paths(["notes/bytecode_58_<module>.bin"])
        self.assertEqual(codes(found), ["WIN101"])
        self.assertIn("'<' '>'", found[0].message)

    def test_reserved_names_any_extension(self):
        self.assertEqual(codes(check_paths(["logs/nul.txt"])), ["WIN102"])
        self.assertEqual(codes(check_paths(["COM1"])), ["WIN102"])
        self.assertEqual(check_paths(["console.py", "com10.txt"]), [])

    def test_trailing_space_or_dot(self):
        self.assertEqual(codes(check_paths(["dir./x"])), ["WIN103"])
        self.assertEqual(codes(check_paths(["x/name .txt"])), [])
        self.assertEqual(codes(check_paths(["x/name. "])), ["WIN103"])

    def test_case_collisions_reported_once(self):
        found = check_paths(
            ["Tools/a.py", "tools/b.py", "tools/c.py", "x/Readme", "x/README"]
        )
        self.assertEqual(codes(found), ["WIN104", "WIN104"])

    def test_long_path(self):
        self.assertEqual(codes(check_paths(["a" * 201])), ["WIN105"])

    def test_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real.txt").write_text("x", encoding="utf-8")
            try:
                (root / "link.txt").symlink_to(root / "real.txt")
            except (OSError, NotImplementedError):
                self.skipTest("当前环境不能创建符号链接")
            self.assertEqual(
                codes(check_paths(["link.txt", "real.txt"], root)), ["WIN106"]
            )


class BatchTests(unittest.TestCase):
    def test_crlf_ascii_passes(self):
        self.assertEqual(check_batch_file("a.bat", b"@echo off\r\necho hi\r\n"), [])

    def test_lf_reports_first_line(self):
        found = check_batch_file("a.bat", b"@echo off\r\necho hi\necho x\r\n")
        self.assertEqual(codes(found), ["WIN201"])
        self.assertEqual(found[0].line, 2)

    def test_bom_is_error(self):
        found = check_batch_file("a.bat", b"\xef\xbb\xbf@echo off\r\n")
        self.assertEqual(codes(found), ["WIN203"])
        self.assertEqual(found[0].severity, Severity.ERROR)

    def test_non_ascii_without_chcp(self):
        data = "@echo off\r\necho 错误\r\n".encode()
        found = check_batch_file("a.bat", data)
        self.assertEqual(codes(found), ["WIN202"])
        self.assertEqual(found[0].line, 2)

    def test_non_ascii_after_chcp_is_fine(self):
        data = "@echo off\r\nchcp 65001 >nul\r\necho 错误\r\n".encode()
        self.assertEqual(check_batch_file("a.bat", data), [])


class PythonSourceTests(unittest.TestCase):
    def test_open_without_encoding(self):
        found = py(
            "t.py",
            """
            with open("a.txt") as f:
                pass
            open("b.bin", "rb")
            open("c.txt", encoding="utf-8")
            open("d.txt", mode="w", encoding="utf-8")
            import io
            io.open("e.txt")
            from pathlib import Path
            Path("f.txt").open()
            Path("g.txt").open("rb")
            open("h.txt", dynamic_mode)
            """,
        )
        self.assertEqual(codes(found), ["WIN301"] * 3)
        self.assertEqual([f.line for f in found], [2, 8, 10])

    def test_read_write_text_without_encoding(self):
        found = py(
            "t.py",
            """
            from pathlib import Path
            Path("a").read_text()
            Path("b").write_text("x", encoding="utf-8")
            some.obj.write_text("x")
            """,
        )
        self.assertEqual(codes(found), ["WIN302", "WIN302"])

    def test_posix_only_imports(self):
        found = py("t.py", "import fcntl\nfrom termios import tcgetattr\n")
        self.assertEqual(codes(found), ["WIN303", "WIN303"])
        self.assertTrue(all(f.severity == Severity.ERROR for f in found))

    def test_guarded_import_is_warning(self):
        found = py(
            "t.py",
            """
            try:
                import fcntl
            except ImportError:
                fcntl = None
            """,
        )
        self.assertEqual(codes(found), ["WIN303"])
        self.assertEqual(found[0].severity, Severity.WARNING)

    def test_posix_only_calls(self):
        found = py(
            "t.py",
            """
            import os
            import signal as sig
            os.killpg(os.getpgid(1), sig.SIGKILL)
            os.path.join("a", "b")
            from os import fork
            """,
        )
        self.assertEqual(codes(found), ["WIN304"] * 4)
        self.assertTrue(all(f.severity == Severity.ERROR for f in found))

    def test_platform_guard_downgrades(self):
        found = py(
            "t.py",
            """
            import os, sys
            if sys.platform != "win32":
                os.setsid()
            """,
        )
        self.assertEqual(codes(found), ["WIN304"])
        self.assertEqual(found[0].severity, Severity.WARNING)

    def test_hardcoded_posix_paths_skip_docstrings(self):
        found = py(
            "t.py",
            '''
            """Writes to /tmp/example by default."""
            OUT = "/tmp/out.json"
            HOME = "/home/user/x"
            URL = "/api/v1"
            RELATIVE = "tmp/x"
            ''',
        )
        self.assertEqual(codes(found), ["WIN305", "WIN305"])
        self.assertEqual([f.line for f in found], [3, 4])

    def test_python_literal_subprocess(self):
        found = py(
            "t.py",
            """
            import subprocess, sys, os
            from subprocess import check_output
            subprocess.run(["python3", "x.py"])
            check_output("python -m pip --version", shell=True)
            os.system("python3.11 x.py")
            subprocess.run([sys.executable, "x.py"])
            subprocess.run(["git", "status"])
            """,
        )
        self.assertEqual(codes(found), ["WIN306"] * 3)

    def test_gui_framework_convention(self):
        found = py("t.py", "import tkinter as tk\nfrom PyQt5 import QtWidgets\n")
        self.assertEqual(codes(found), ["CONV001", "CONV001"])
        self.assertEqual(py("t.py", "from PySide6 import QtWidgets\n"), [])

    def test_inline_suppression(self):
        found = py("t.py", 'open("a.txt")  # win-ok: 由上层保证 UTF-8\n')
        self.assertEqual(found, [])

    def test_syntax_error_is_info(self):
        found = py("legacy.py", "print 'python2'\n")
        self.assertEqual(codes(found), ["WIN307"])
        self.assertEqual(found[0].severity, Severity.INFO)


class RunnerTests(unittest.TestCase):
    def _make_tree(self, root: Path) -> None:
        (root / "tool").mkdir()
        (root / "tool" / "ok.py").write_text(
            "from pathlib import Path\n\n"
            "TEXT = Path('a').read_text(encoding='utf-8')\n",
            encoding="utf-8",
        )
        (root / "tool" / "bad.py").write_text("import fcntl\n", encoding="utf-8")
        (root / "tool" / "run.bat").write_bytes(b"@echo off\necho hi\n")
        (root / "tool" / "data.bin").write_bytes(b"\x00\x01")
        (root / "other").mkdir()
        (root / "other" / "nul.txt").write_text("x", encoding="utf-8")

    def test_walk_mode_scopes_paths_and_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            result = run_checks(
                CheckOptions(root=root, paths=[str(root / "tool")], use_git=False)
            )
            self.assertEqual(result.source, "walk")
            self.assertEqual(result.scanned_files, 3)
            self.assertEqual(codes(result.findings), ["WIN201", "WIN303"])
            self.assertEqual(result.exit_code(), 1)

            everything = run_checks(CheckOptions(root=root, use_git=False))
            self.assertEqual(codes(everything.findings), ["WIN102", "WIN201", "WIN303"])

    def test_exit_code_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.bat").write_bytes(b"@echo off\n")
            result = run_checks(CheckOptions(root=root, use_git=False))
            self.assertEqual(codes(result.findings), ["WIN201"])
            self.assertEqual(result.exit_code(), 0)
            self.assertEqual(result.exit_code(strict=True), 1)

    def test_excludes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            result = run_checks(
                CheckOptions(root=root, use_git=False, excludes=("tool/", "other/"))
            )
            self.assertEqual(result.findings, [])

    def test_cli_json_and_list_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_tree(root)
            report = root / "report.json"
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = check_windows_compat.main(
                    ["--root", str(root), "--no-git", "--quiet", "--json", str(report)]
                )
            self.assertEqual(code, 1)
            self.assertIn("[wincompat]", buffer.getvalue())
            payload = report.read_text(encoding="utf-8")
            self.assertIn('"WIN303"', payload)

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                self.assertEqual(check_windows_compat.main(["--list-rules"]), 0)
            for rule in RULES:
                self.assertIn(rule, buffer.getvalue())


class GitModeTests(unittest.TestCase):
    def _git(self, root: Path, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "t",
                "GIT_AUTHOR_EMAIL": "t@x",
                "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@x",
            },
        )

    def test_since_scans_changed_and_untracked_only(self):
        if shutil.which("git") is None:
            self.skipTest("没有 git")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            self._git(root, "init", "-q")
            (root / "old.py").write_text("import fcntl\n", encoding="utf-8")
            (root / "ignored.py").write_text("import fcntl\n", encoding="utf-8")
            (root / ".gitignore").write_text("ignored.py\n", encoding="utf-8")
            self._git(root, "add", "-A")
            self._git(root, "commit", "-q", "-m", "base")
            (root / "changed.py").write_text("import pwd\n", encoding="utf-8")
            self._git(root, "add", "changed.py")
            self._git(root, "commit", "-q", "-m", "change")
            (root / "new.bat").write_bytes(b"@echo off\n")

            full = run_checks(CheckOptions(root=root))
            self.assertEqual(full.source, "git")
            self.assertEqual(codes(full.findings), ["WIN201", "WIN303", "WIN303"])

            since = run_checks(CheckOptions(root=root, since="HEAD~1"))
            self.assertEqual(since.scanned_files, 2)
            self.assertEqual(codes(since.findings), ["WIN201", "WIN303"])
            self.assertEqual(
                sorted(f.path for f in since.findings), ["changed.py", "new.bat"]
            )


class SelfCheckTests(unittest.TestCase):
    def test_devkit_passes_its_own_rules(self):
        result = run_checks(
            CheckOptions(root=DEVKIT, paths=[str(DEVKIT)], use_git=False)
        )
        self.assertEqual(result.findings, [], [f.format() for f in result.findings])


if __name__ == "__main__":
    unittest.main()
