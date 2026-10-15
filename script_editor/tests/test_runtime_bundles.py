"""Synthetic PE headers test guards ONLY, never a real Windows runtime pass."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from script_editor.core.compiler.bundles import BundleError, load_bundle
from script_editor.core.compiler.distribution import audit_runtimes, stage_runtimes
from script_editor.core.compiler.runner import (
    CompilerError,
    bundled_compiler,
    compile_standard,
)
from script_editor.release_checks import (
    OPTIONAL_MATERIAL_TESTS,
    REQUIRED_RELEASE_TESTS,
    forbidden_skips,
    suite_ids,
)
from script_editor.runtime_cli import main


def synthetic_pe(*, dll=False, machine=0x14C, magic=0x10B):
    dos = bytearray(128)
    dos[:2] = b"MZ"
    struct.pack_into("<I", dos, 60, 128)
    coff = struct.pack(
        "<HHIIIHH", machine, 1, 0, 0, 0, 224, 0x102 | (0x2000 if dll else 0)
    )
    return bytes(dos) + b"PE\0\0" + coff + struct.pack("<H", magic) + bytes(222)


def hash_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def make_manifest(root):
    base = root / "runtimes"
    base.mkdir(parents=True)
    items = []
    for vm, suffix, version, magic in (
        ("py25", "25", "2.5.6", "b3f20d0a"),
        ("py27", "27", "2.7.13", "03f30d0a"),
    ):
        folder = base / vm / "win-x86"
        folder.mkdir(parents=True)
        contents = {
            "python.exe": synthetic_pe(),
            f"python{suffix}.dll": synthetic_pe(dll=True),
            f"python{suffix}.zip": b"TEST-ONLY-NOT-A-STDLIB",
            "LICENSE.txt": b"TEST-ONLY-NOT-A-LICENSE",
        }
        for name, raw in contents.items():
            (folder / name).write_bytes(raw)
        items.append(
            {
                "vm": vm,
                "platform": "win32",
                "version": version,
                "bits": 32,
                "magic": magic,
                "root": f"{vm}/win-x86",
                "executable": f"{vm}/win-x86/python.exe",
                "files": {name: hash_bytes(raw) for name, raw in contents.items()},
                "source": {
                    "url": f"https://github.com/python/cpython/archive/refs/tags/v{version}.tar.gz",
                    "revision": "b" * 40,
                    "archive_sha256": "a" * 64,
                },
                "licenses": [{"component": "CPython", "path": "LICENSE.txt"}],
            }
        )
    doc = {"schema": 2, "compilers": items}
    (base / "manifest.json").write_text(json.dumps(doc), encoding="utf-8")
    return doc


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-runtime-guards-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.doc = make_manifest(self.root)
        self.manifest = self.root / "runtimes/manifest.json"
        self.runtime = self.root / "runtimes/py25/win-x86"
        self.output = self.root / "output"
        self.output.mkdir()

    def write(self, doc=None):
        self.manifest.write_text(
            json.dumps(self.doc if doc is None else doc), encoding="utf-8"
        )

    def test_static_full_pair_is_explicitly_not_execution_or_game_acceptance(self):
        with patch("script_editor.core.compiler.runner._run") as run:
            report = audit_runtimes(self.root)
        run.assert_not_called()
        self.assertEqual(report["status"], "static-only")
        self.assertEqual(report["native_game_acceptance"], "not-tested")
        self.assertEqual(len(report["compilers"]), 2)
        self.assertTrue(
            all(r["execution"] == "not-executed" for r in report["compilers"])
        )

    def test_dll_stdlib_license_and_exe_changes_rejected_before_any_launch(self):
        for name in self.doc["compilers"][0]["files"]:
            with self.subTest(name=name):
                path = self.runtime / name
                old = path.read_bytes()
                path.write_bytes(old + b"tampered")
                with (
                    patch("script_editor.core.compiler.runner.sys.platform", "win32"),
                    patch("script_editor.core.compiler.runner._run") as run,
                ):
                    with self.assertRaises(CompilerError):
                        bundled_compiler("py25", self.root)
                run.assert_not_called()
                path.write_bytes(old)

    def test_extra_file_and_missing_file_refused(self):
        extra = self.runtime / "unlisted.pyd"
        extra.write_bytes(synthetic_pe(dll=True))
        with self.assertRaises(BundleError):
            load_bundle("py25", self.root)
        extra.unlink()
        (self.runtime / "python25.zip").unlink()
        with self.assertRaises(BundleError):
            load_bundle("py25", self.root)

    def test_bad_paths_case_collisions_and_windows_names_refused(self):
        for name in (
            "../outside.dll",
            "/outside",
            "C:/outside",
            "a\\x",
            "a//x",
            "NUL.txt",
            "dir/x.",
            "python.EXE",
        ):
            with self.subTest(name=name):
                doc = copy.deepcopy(self.doc)
                doc["compilers"][0]["files"][name] = "a" * 64
                self.write(doc)
                with self.assertRaises(BundleError):
                    load_bundle("py25", self.root)

    def test_file_symlink_guard_without_needing_windows_symlink_privileges(self):
        original = Path.is_symlink
        victim = self.runtime / "python25.dll"
        with patch.object(Path, "is_symlink", lambda p: p == victim or original(p)):
            with self.assertRaises(BundleError):
                load_bundle("py25", self.root)

    def test_non_x86_or_wrong_binary_type_even_with_correct_recorded_digest(self):
        for raw in (
            synthetic_pe(machine=0x8664),
            synthetic_pe(magic=0x20B),
            synthetic_pe(dll=True),
            b"not PE",
        ):
            (self.runtime / "python.exe").write_bytes(raw)
            doc = copy.deepcopy(self.doc)
            doc["compilers"][0]["files"]["python.exe"] = hash_bytes(raw)
            self.write(doc)
            with self.assertRaises(BundleError):
                load_bundle("py25", self.root)

    def test_missing_source_license_or_schema1_nonempty_refused(self):
        for field in ("source", "licenses", "version", "magic", "bits"):
            doc = copy.deepcopy(self.doc)
            doc["compilers"][0].pop(field)
            self.write(doc)
            with self.assertRaises(BundleError):
                load_bundle("py25", self.root)
        doc = copy.deepcopy(self.doc)
        doc["schema"] = 1
        self.write(doc)
        with self.assertRaises(BundleError):
            load_bundle("py25", self.root)

    def test_duplicate_vm_and_json_fields_refused(self):
        self.doc["compilers"].append(copy.deepcopy(self.doc["compilers"][0]))
        self.write()
        with self.assertRaises(BundleError):
            load_bundle("py25", self.root)
        self.manifest.write_text(
            '{"schema":2,"schema":2,"compilers":[]}', encoding="utf-8"
        )
        with self.assertRaises(BundleError):
            load_bundle("py25", self.root)

    def test_source_url_revision_digest_and_crt_license_required(self):
        for key, value in (
            ("url", "https://github.com/other/python/file"),
            ("url", "http://www.python.org/source"),
            ("url", "https://user:secret@github.com/python/cpython/source"),
            ("revision", "v2.5.6"),
            ("archive_sha256", "not-a-sha"),
        ):
            doc = copy.deepcopy(self.doc)
            doc["compilers"][0]["source"][key] = value
            self.write(doc)
            with self.assertRaises(BundleError):
                load_bundle("py25", self.root)
        self.doc["compilers"][0]["files"]["msvcr71.dll"] = "a" * 64
        self.write()
        with self.assertRaisesRegex(BundleError, "CRT"):
            load_bundle("py25", self.root)

    def test_pin_detects_manifest_changes_after_registration(self):
        pin = load_bundle("py25", self.root)
        self.manifest.write_text(
            self.manifest.read_text(encoding="utf-8") + " ", encoding="utf-8"
        )
        with self.assertRaises(BundleError):
            pin.verify()

    def test_stage_exact_pair_and_reverify_copied_inventory(self):
        report = stage_runtimes(self.root, self.output)
        self.assertEqual(report["status"], "static-only")
        for vm in ("py25", "py27"):
            pin = load_bundle(vm, self.output)
            self.assertEqual(
                dict(pin.files),
                self.doc["compilers"][0 if vm == "py25" else 1]["files"],
            )
        with self.assertRaises(FileExistsError):
            stage_runtimes(self.root, self.output)
        self.assertTrue((self.output / "runtimes/manifest.json").exists())

    def test_stage_copy_failure_cleans_only_new_runtime_folder(self):
        keeper = self.output / "editor.exe"
        keeper.write_bytes(b"KEEP")
        with patch(
            "script_editor.core.compiler.distribution.shutil.copyfile",
            side_effect=OSError("disk full"),
        ):
            with self.assertRaises(OSError):
                stage_runtimes(self.root, self.output)
        self.assertFalse((self.output / "runtimes").exists())
        self.assertEqual(keeper.read_bytes(), b"KEEP")
        load_bundle("py25", self.root).verify()

    def test_stage_copy_corruption_never_passes(self):
        import shutil

        original = shutil.copyfile

        def corrupt(src, dst):
            result = original(src, dst)
            if Path(dst).name == "python25.zip":
                Path(dst).write_bytes(b"wrong")
            return result

        with patch(
            "script_editor.core.compiler.distribution.shutil.copyfile",
            side_effect=corrupt,
        ):
            with self.assertRaises(BundleError):
                stage_runtimes(self.root, self.output)
        self.assertFalse((self.output / "runtimes").exists())

    def test_one_vm_cannot_make_complete_distribution(self):
        self.doc["compilers"].pop()
        self.write()
        with self.assertRaises(BundleError):
            stage_runtimes(self.root, self.output)
        self.assertFalse((self.output / "runtimes").exists())

    def test_non_windows_execution_forbidden_even_if_static_passes(self):
        with (
            patch("script_editor.core.compiler.distribution.sys.platform", "linux"),
            patch("script_editor.core.compiler.runner._run") as run,
        ):
            with self.assertRaises(BundleError):
                audit_runtimes(self.root, execute=True)
        run.assert_not_called()

    def test_cli_static_json_and_missing_bundle_exit2(self):
        with patch("sys.stdout", new_callable=io.StringIO) as output:
            code = main(["audit", "--root", str(self.root), "--static"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "static-only")
        self.manifest.unlink()
        with patch("sys.stderr", new_callable=io.StringIO) as error:
            code = main(["audit", "--root", str(self.root), "--static"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(error.getvalue())["status"], "failed")

    def test_mocked_probe_mutation_is_detected_after_subprocess(self):
        def mutate(*args):
            (self.runtime / "python25.dll").write_bytes(b"changed while probing")
            return b"2.5.6 b3f20d0a 32"

        with (
            patch("script_editor.core.compiler.runner.sys.platform", "win32"),
            patch("script_editor.core.compiler.runner._run", side_effect=mutate),
        ):
            with self.assertRaises(CompilerError):
                bundled_compiler("py25", self.root)

    def test_mocked_registered_bundle_rechecked_before_compile_and_protected(self):
        with (
            patch("script_editor.core.compiler.runner.sys.platform", "win32"),
            patch(
                "script_editor.core.compiler.runner._run",
                return_value=b"2.5.6 b3f20d0a 32",
            ),
        ):
            compiler = bundled_compiler("py25", self.root)
        self.assertIsNotNone(compiler.bundle)
        self.assertIn(self.runtime / "python25.zip", compiler.protected)
        alias = self.root / "stdlib-alias.pyc"
        os.link(self.runtime / "python25.zip", alias)
        with patch("script_editor.core.compiler.runner._run") as run:
            with self.assertRaises(ValueError):
                compile_standard(compiler, "x=1", b"filename.py", alias)
        run.assert_not_called()
        self.assertEqual(alias.read_bytes(), b"TEST-ONLY-NOT-A-STDLIB")
        target = self.root / "old.pyc"
        target.write_bytes(b"KEEP")
        (self.runtime / "python25.zip").write_bytes(b"tampered")
        with patch("script_editor.core.compiler.runner._run") as run:
            with self.assertRaises(CompilerError):
                compile_standard(compiler, "x=1", b"filename.py", target)
        run.assert_not_called()
        self.assertEqual(target.read_bytes(), b"KEEP")

    def test_mocked_subprocess_generated_extra_pyc_rejects_output(self):
        with (
            patch("script_editor.core.compiler.runner.sys.platform", "win32"),
            patch(
                "script_editor.core.compiler.runner._run",
                return_value=b"2.5.6 b3f20d0a 32",
            ),
        ):
            compiler = bundled_compiler("py25", self.root)
        target = self.root / "old.pyc"
        target.write_bytes(b"KEEP")

        def fake_run(executable, args, cwd):
            if args[0] == "-c":
                return b"2.5.6 b3f20d0a 32"
            Path(args[2]).write_bytes(bytes.fromhex("b3f20d0a") + bytes(4) + b"c")
            (self.runtime / "unlisted.pyc").write_bytes(b"generated")
            return b""

        with patch("script_editor.core.compiler.runner._run", side_effect=fake_run):
            with self.assertRaises(CompilerError):
                compile_standard(compiler, "x=1", b"filename.py", target)
        self.assertEqual(target.read_bytes(), b"KEEP")

    def test_release_skip_policy_never_allows_gui_or_compiler_skips(self):
        class Test:
            def __init__(self, name):
                self.name = name

            def id(self):
                return self.name

        result = unittest.TestResult()
        for name in OPTIONAL_MATERIAL_TESTS:
            result.addSkip(Test(name), "external materials not distributed")
        self.assertEqual(forbidden_skips(result), [])
        result.addSkip(
            Test(
                "test_gui_workflow.GuiWorkflowTests.test_real_worker_callback_runs_on_gui_thread_and_restores_actions"
            ),
            "no Qt",
        )
        result.addSkip(
            Test("test_compiler.LegacyCompilation.test_actual_cpython25"), "no compiler"
        )
        self.assertEqual(len(forbidden_skips(result)), 2)

    def test_staging_manifest_change_during_copy_is_not_silently_adopted(self):
        import shutil

        original = shutil.copyfile

        def change_manifest(src, dst):
            result = original(src, dst)
            if Path(dst).name == "python25.zip":
                self.manifest.write_text(
                    self.manifest.read_text(encoding="utf-8") + " ", encoding="utf-8"
                )
            return result

        with patch(
            "script_editor.core.compiler.distribution.shutil.copyfile",
            side_effect=change_manifest,
        ):
            with self.assertRaises(BundleError):
                stage_runtimes(self.root, self.output)
        self.assertFalse((self.output / "runtimes").exists())

    def test_empty_license_and_oversized_or_bad_manifest_rejected(self):
        license = self.runtime / "LICENSE.txt"
        license.write_bytes(b"")
        self.doc["compilers"][0]["files"]["LICENSE.txt"] = hash_bytes(b"")
        self.write()
        with self.assertRaisesRegex(BundleError, "许可文件为空"):
            load_bundle("py25", self.root)
        for raw in (b"[]", b"{not-json", b" " * (4 * 1024 * 1024 + 1)):
            self.manifest.write_bytes(raw)
            with self.assertRaises(BundleError):
                load_bundle("py25", self.root)

    def test_staging_destination_inside_input_runtime_tree_refused(self):
        with self.assertRaises(BundleError):
            stage_runtimes(self.root, self.runtime)
        load_bundle("py25", self.root).verify()

    def test_optional_skip_ids_correspond_to_actual_opt_in_tests(self):
        import ast

        actual = set()
        for path in Path(__file__).parent.glob("test_*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in (n for n in tree.body if isinstance(n, ast.ClassDef)):
                for method in (n for n in cls.body if isinstance(n, ast.FunctionDef)):
                    actual.add(f"{path.stem}.{cls.name}.{method.name}")
        self.assertLessEqual(OPTIONAL_MATERIAL_TESTS | REQUIRED_RELEASE_TESTS, actual)
        suite = unittest.TestSuite(
            [unittest.TestSuite([unittest.FunctionTestCase(lambda: None)])]
        )
        self.assertEqual(len(suite_ids(suite)), 1)
        self.assertTrue(REQUIRED_RELEASE_TESTS - suite_ids(suite))
        self.assertEqual(suite_ids(unittest.TestSuite()), set())
