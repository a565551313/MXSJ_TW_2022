from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from script_editor.core.compiler.profiles import PROFILES
from script_editor.core.compiler.runner import (
    Compiler,
    CompilerError,
    _run,
    bundled_compiler,
    compile_standard,
    inspect_compiler,
)


class CompilerGuards(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-compiler-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_python3_cannot_compile_game_scripts(self):
        for vm in PROFILES:
            with self.subTest(vm=vm), self.assertRaises(CompilerError):
                inspect_compiler(Path(sys.executable), vm)

    def test_missing_compiler(self):
        with self.assertRaises(OSError):
            inspect_compiler(self.root / "not-there", "py25")

    def test_timeout_is_explicit(self):
        with patch(
            "script_editor.core.compiler.runner.subprocess.run",
            side_effect=subprocess.TimeoutExpired("compiler", 30),
        ):
            with self.assertRaises(CompilerError):
                _run(Path(sys.executable), [], self.root)

    def test_empty_bundled_manifest_disables_compilation(self):
        (self.root / "runtimes").mkdir()
        (self.root / "runtimes" / "manifest.json").write_text(
            '{"schema":1,"compilers":[]}', encoding="utf-8"
        )
        with self.assertRaises(CompilerError):
            bundled_compiler("py25", self.root)

    def test_manifest_hash_checked_before_launch(self):
        base = self.root / "runtimes"
        base.mkdir()
        (base / "python.exe").write_bytes(b"not-an-executable")
        manifest = {
            "schema": 1,
            "compilers": [
                {
                    "vm": "py25",
                    "platform": sys.platform,
                    "executable": "python.exe",
                    "sha256": "0" * 64,
                }
            ],
        }
        (base / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with patch("script_editor.core.compiler.runner._run") as run:
            with self.assertRaises(CompilerError):
                bundled_compiler("py25", self.root)
            run.assert_not_called()

    def test_manifest_path_escape(self):
        base = self.root / "runtimes"
        base.mkdir()
        executable = self.root / "outside.exe"
        executable.write_bytes(b"not-run")
        manifest = {
            "schema": 1,
            "compilers": [
                {
                    "vm": "py25",
                    "platform": sys.platform,
                    "executable": "../outside.exe",
                    "sha256": hashlib.sha256(executable.read_bytes()).hexdigest(),
                }
            ],
        }
        (base / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with patch("script_editor.core.compiler.runner._run") as run:
            with self.assertRaises(CompilerError):
                bundled_compiler("py25", self.root)
            run.assert_not_called()

    def test_vm_version_and_magic_must_both_match(self):
        for output in (
            b"2.7.13 b3f20d0a 32",
            b"2.5.6 03f30d0a 32",
            b"2.5.6 b3f20d0a 64 noise",
        ):
            with self.subTest(output=output):
                with patch(
                    "script_editor.core.compiler.runner._run", return_value=output
                ):
                    with self.assertRaises(CompilerError):
                        inspect_compiler(Path(sys.executable), "py25")

    def test_standard_output_only_and_encoding_header(self):
        c = Compiler(Path(sys.executable), "py25", "2.5.6", 64, "hash")
        with self.assertRaises(CompilerError):
            compile_standard(c, "x=1", "x.py", self.root / "script.fls")
        with self.assertRaises(CompilerError):
            compile_standard(c, "# coding: big5\nx=1", "x.py", self.root / "x.pyc")

    def test_compiler_changed_or_failed_never_replaces_output(self):
        c = Compiler(Path(sys.executable), "py25", "2.5.6", 64, "hash")
        target = self.root / "old.pyc"
        target.write_bytes(b"old")
        with patch(
            "script_editor.core.compiler.runner.inspect_compiler", return_value=None
        ):
            with self.assertRaises(CompilerError):
                compile_standard(c, "x=1", "x.py", target)
        with patch(
            "script_editor.core.compiler.runner.inspect_compiler", return_value=c
        ):
            with patch(
                "script_editor.core.compiler.runner._run", side_effect=CompilerError
            ):
                with self.assertRaises(CompilerError):
                    compile_standard(c, "x=1", "x.py", target)
        self.assertEqual(target.read_bytes(), b"old")


class LegacyCompilation(unittest.TestCase):
    def run_profile(self, vm):
        executable = os.environ.get("MXSJ_" + vm.upper())
        if not executable:
            self.skipTest(f"{vm}: set MXSJ_{vm.upper()} to actual standard compiler")
        compiler = inspect_compiler(Path(executable), vm)
        with tempfile.TemporaryDirectory(prefix="mxscript-legacy-") as temp:
            root = Path(temp)
            sentinel = root / "must-not-exist"
            output = root / "standard.pyc"
            # Executing target source would fail AND leave a sentinel.
            source = (
                "# coding: utf-8\nmarker='script-editor-m1'\n"
                f"open({str(sentinel)!r}, 'w').write('EXECUTED')\n"
                "raise RuntimeError('target must not execute')\n"
                "title=u'測試'\n"
            )
            digest = compile_standard(compiler, source, "自己的脚本.py", output)
            self.assertFalse(sentinel.exists())
            self.assertEqual(output.read_bytes()[:4], PROFILES[vm].magic)
            self.assertEqual(digest, hashlib.sha256(output.read_bytes()).hexdigest())
            name = root / "filename.txt"
            name.write_bytes("自己的脚本.py".encode())
            # Independent marshal audit, no imports/exec of the compiled game module.
            audit = (
                "import sys,marshal;f=open(sys.argv[1],'rb');f.read(8);"
                "c=marshal.load(f);assert f.read()=='';"
                "assert c.co_filename==open(sys.argv[2],'rb').read();"
                "assert 'script-editor-m1' in c.co_consts;assert len(c.co_code)>0"
            )
            subprocess.run(
                [
                    str(compiler.executable),
                    "-E",
                    "-S",
                    "-c",
                    audit,
                    str(output),
                    str(name),
                ],
                check=True,
                timeout=30,
                cwd=root,
                capture_output=True,
            )
            again = root / "again.pyc"
            compile_standard(compiler, source, "自己的脚本.py", again)
            self.assertEqual(output.read_bytes(), again.read_bytes())
            before = output.read_bytes()
            with self.assertRaisesRegex(CompilerError, "SYNTAX"):
                compile_standard(compiler, "def broken(:\n", "x.py", output)
            self.assertEqual(output.read_bytes(), before)
            self.assertFalse(sentinel.exists())
            other = "py27" if vm == "py25" else "py25"
            with self.assertRaises(CompilerError):
                inspect_compiler(compiler.executable, other)

    def test_actual_cpython25(self):
        self.run_profile("py25")

    def test_actual_cpython27(self):
        self.run_profile("py27")
