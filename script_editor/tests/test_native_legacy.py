from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from native_fixtures import data_fixture, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import compile_standard, inspect_compiler
from script_editor.core.services.native_build import Replacement, build_package
from script_editor.core.vm.py25.keys import load_profile


class ActualLegacyBuild(unittest.TestCase):
    def exercise(self, vm):
        exe = os.environ.get("MXSJ_" + vm.upper())
        if not exe:
            self.skipTest("actual standard compiler not configured: " + vm)
        compiler = inspect_compiler(Path(exe), vm)
        with tempfile.TemporaryDirectory(prefix="mxscript-m2-real-") as temp:
            root = Path(temp)
            source_path = root / "source.fls"
            if vm == "py25":
                package, keys = script_fixture(expanded_size=65536)
                source_path.write_bytes(package)
                catalog = root / "catalog.json"
                catalog.write_text(json.dumps(keys), encoding="utf-8")
            else:
                source_path.write_bytes(data_fixture())
            digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
            with ArchiveDocument(source_path) as archive:
                index = 0 if vm == "py25" else 1
                identity = archive.entries[index].identity
                profiles = (
                    {}
                    if vm == "py27"
                    else {
                        index: load_profile(
                            archive,
                            index,
                            catalog,
                            archive_sha256=digest,
                            catalog_sha256=hashlib.sha256(
                                catalog.read_bytes()
                            ).hexdigest(),
                        )
                    }
                )
            sentinel = root / "must-not-execute"
            source = (
                "# coding: utf-8\nimport os\nnumber=12345678901234567890L\n"
                "complex_number=1.5+2j\ntitle=u'測試'\n"
                "class Example(object):\n def run(self, items):\n"
                "  try:\n   return [i[1:3] for i in items if i]\n"
                "  except Exception:\n   return None\n"
                "def outer(x):\n def inner(y):\n  return x+y\n return inner\n"
                + "x=1;" * 200
                + "\nx=2\n"
                + "\n" * 300
                + "x=3\n"
                + f"open({str(sentinel)!r},'w').write('EXECUTED')\n"
                "raise RuntimeError('DO NOT EXECUTE')\n"
            )
            if vm == "py27":
                source = source.replace(
                    "class Example(object):\n",
                    "from os import path as selected_path\n"
                    "dictionary={'a': number}\nset_value={1,2}\n"
                    "attribute=os.path\ncomparison=number>0\n"
                    "class Example(object):\n",
                )
            pyc = root / "fresh.pyc"
            compile_standard(compiler, source, "自己的模块.py", pyc)
            result = build_package(
                source_path,
                root / "new.fls",
                source_sha256=digest,
                compiler=compiler,
                profiles=profiles,
                replacements=(Replacement(index, identity, pyc.read_bytes()),),
            )
            self.assertEqual(result.unchanged_entries, 2)
            self.assertFalse(sentinel.exists())
            self.assertEqual(
                hashlib.sha256(source_path.read_bytes()).hexdigest(), digest
            )
            self.assertFalse(list(root.glob(".mxscript-build-*")))

    def test_full_actual_py25_compile_native_package_readback(self):
        self.exercise("py25")

    def test_full_actual_py27_compile_native_package_readback(self):
        self.exercise("py27")


class RealMaterialBuild(unittest.TestCase):
    def exercise(self, vm):
        location = os.environ.get("MXSJ_M2_REPO")
        executable = os.environ.get("MXSJ_" + vm.upper())
        if not location or not executable:
            self.skipTest("opt-in game materials and compiler required")
        repo = Path(location)
        base, index, unchanged = (
            ("script", 4007, 5001) if vm == "py25" else ("data", 75, 132)
        )
        source_path = repo / "data" / (base + ".fls")
        expected = (
            "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72"
            if vm == "py25"
            else "5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c"
        )
        compiler = inspect_compiler(Path(executable), vm)
        with tempfile.TemporaryDirectory(prefix="mxscript-m2-material-") as temp:
            root = Path(temp)
            with ArchiveDocument(source_path) as archive:
                self.assertEqual(archive.fingerprint(), expected)
                identity = archive.entries[index].identity
                profiles = {}
                if vm == "py25":
                    catalog = repo / "tools" / "decompiler" / "script_fls_keys.json"
                    profiles[index] = load_profile(
                        archive,
                        index,
                        catalog,
                        archive_sha256=expected,
                        catalog_sha256="43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
                    )
            # This data.fls output intentionally replaces a core library with a probe:
            # offline-only, NEVER a distributable game/client test package.
            source = (
                (repo / "tools" / "registration" / "register.py").read_text(
                    encoding="utf-8"
                )
                if vm == "py25"
                else "# coding: utf-8\nMARKER='offline-only-m2-probe'\n"
                "def nested(items):\n return [x[1:3] for x in items if x]\n"
            )
            pyc = root / "fresh.pyc"
            compile_standard(compiler, source, "offline_m2.py", pyc)
            result = build_package(
                source_path,
                root / (base + "_offline.fls"),
                source_sha256=expected,
                compiler=compiler,
                profiles=profiles,
                replacements=(Replacement(index, identity, pyc.read_bytes()),),
            )
            self.assertEqual(result.unchanged_entries, unchanged)
            self.assertEqual(
                hashlib.sha256(source_path.read_bytes()).hexdigest(), expected
            )

    def test_real_mainpage_337_native_boundaries_remove_false_opcode_error(self):
        location = os.environ.get("MXSJ_M2_REPO")
        executable = os.environ.get("MXSJ_PY25")
        if not location or not executable:
            self.skipTest("opt-in game materials and compiler required")
        source = Path(location) / "data" / "script.fls"
        catalog = Path(location) / "tools" / "decompiler" / "script_fls_keys.json"
        compiler = inspect_compiler(Path(executable), "py25")
        with tempfile.TemporaryDirectory(prefix="mxscript-m2-calibrated-") as temp:
            output = Path(temp) / "mainpage-offline.fls"
            with ArchiveDocument(source) as archive:
                digest = archive.fingerprint()
                identity = archive.entries[337].identity
                profile = load_profile(
                    archive,
                    337,
                    catalog,
                    archive_sha256=digest,
                    catalog_sha256="43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb",
                )
            from native_fixtures import minimal_pyc

            # The old boundary 8473 cut through a VM instruction. Do not
            # preserve that research-table bug as a required opcode failure.
            self.assertEqual(profile.bounds, (2163, 4281, 6390, 8474))
            report = build_package(
                source,
                output,
                source_sha256=digest,
                compiler=compiler,
                profiles={337: profile},
                replacements=(Replacement(337, identity, minimal_pyc("py25")),),
            )
            self.assertEqual(report.unchanged_entries, 5001)
            self.assertTrue(output.is_file())

    def test_actual_script_register_source(self):
        self.exercise("py25")

    def test_actual_data_offline_probe(self):
        self.exercise("py27")
