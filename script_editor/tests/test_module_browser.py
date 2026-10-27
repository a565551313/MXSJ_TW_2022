from __future__ import annotations

import ast
import json
import os
import subprocess
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from native_fixtures import minimal_pyc
from test_workflow import make_state

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import compile_standard, inspect_compiler
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import (
    ProjectState,
    load_state,
    save_state,
)
from script_editor.core.services.bundled_catalog import bundled_catalog
from script_editor.core.services.files import save_new_source
from script_editor.core.services.module_browser import (
    MAX_SOURCE_CHARS,
    MAX_TRACE_CHARS,
    RecoveryCandidate,
    RecoverySessionCache,
    read_module,
    recover_standard,
    validate_result,
)
from script_editor.core.services.recovery_process import RecoveryProcessError
from script_editor.core.services.workflow import Snapshot, prepare_build, publish_build
from script_editor.core.vm.marshal_tree import Atom, Code, parse


class ModuleBrowserTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mx-recovery-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def compiler(self, vm):
        executable = os.environ.get("MXSJ_" + vm.upper())
        if not executable:
            self.skipTest("actual standard compiler required: " + vm)
        return inspect_compiler(Path(executable), vm)

    def make_original(self, vm):
        state = make_state(self.root, vm)
        compiler = self.compiler(vm)
        sentinel = self.root / "NEVER_EXECUTE"
        text = (
            "# coding: utf-8\nx=42\ntitle=u'測試'\nraw='\\xff'\n"
            f"open({str(sentinel)!r},'w').write('EXECUTED')\n"
            "def calculate(value):\n    return value + 1\n"
        )
        catalog = state.catalogs[0] if state.catalogs else None
        plan = prepare_build(Snapshot(state.bindings[0], text, vm), compiler, catalog)
        _, state = publish_build(plan, self.root / (vm + "-original.fls"), state)
        return state, compiler, sentinel

    def test_both_real_vms_package_recover_edit_compile_publish_reopen(self):
        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                state, compiler, sentinel = self.make_original(vm)
                binding = state.bindings[0]
                catalog = state.catalogs[0] if state.catalogs else None
                original = binding.archive.read_bytes()
                with ArchiveDocument(binding.archive) as archive:
                    report = read_module(archive, binding.index, catalog)
                    self.assertTrue(report.complete, report.diagnostics)
                    self.assertIn("calculate", report.source)
                    self.assertIn("LOAD_CONST", report.disassembly)
                    self.assertIn("MXSJ-RECOVERED-DRAFT", report.source)
                    self.assertEqual(report.vm, vm)
                    self.assertFalse(sentinel.exists())
                    source = self.root / (vm + "-recovered.py")
                    save_new_source(source, report.source + "\nRECOVERY_EDIT = 99\n")
                    reviewed = replace(
                        Binding.associate(archive, binding.index, source),
                        filename_hex=report.filename_hex,
                        source_kind="recovered-reviewed",
                        recovery_sha256=report.standard_sha256,
                    )
                state = ProjectState((reviewed,), state.catalogs)
                plan = prepare_build(
                    Snapshot(reviewed, source.read_text(encoding="utf-8"), vm),
                    compiler,
                    catalog,
                )
                output = self.root / (vm + "-edited.fls")
                result, state = publish_build(plan, output, state)
                self.assertEqual(result.unchanged_entries, 2)
                self.assertEqual(binding.archive.read_bytes(), original)
                self.assertFalse(sentinel.exists())
                project = self.root / (vm + ".mxscript.json")
                save_state(project, state.bindings, state.catalogs)
                reopened = load_state(project)
                self.assertEqual(reopened.bindings[0].source_kind, "recovered-reviewed")
                self.assertEqual(
                    reopened.bindings[0].recovery_sha256, report.standard_sha256
                )
                with ArchiveDocument(output) as archive:
                    next_report = read_module(
                        archive,
                        binding.index,
                        reopened.catalogs[0] if vm == "py25" else None,
                    )
                    self.assertTrue(next_report.complete, next_report.diagnostics)
                    self.assertIn("RECOVERY_EDIT", next_report.source)
                self.assertFalse(sentinel.exists())

    def test_unicode_quotes_non_bmp_future_unicode_and_bytes_survive_rendering(self):
        def constants(node):
            if isinstance(node, Atom):
                return [(node.tag, node.value)]
            children = node.fields if isinstance(node, Code) else node.items
            return [value for child in children for value in constants(child)]

        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                compiler = self.compiler(vm)
                value = "測試😀'\\\n"
                text = (
                    "from __future__ import unicode_literals\n" if vm == "py27" else ""
                )
                text += (
                    "title = u"
                    + ascii(value)
                    + "\npayload = "
                    + ("b" if vm == "py27" else "")
                    + "'\\xff'\n"
                )
                original, rebuilt = (
                    self.root / (vm + "-unicode.pyc"),
                    self.root / (vm + "-rebuilt.pyc"),
                )
                compile_standard(compiler, text, b"unicode.py", original)
                result = recover_standard(original.read_bytes(), vm)
                self.assertTrue(result["complete"], result["diagnostics"])
                compile_standard(compiler, result["source"], b"unicode.py", rebuilt)
                for code in (original, rebuilt):
                    values = constants(parse(code.read_bytes()[8:]))
                    self.assertIn((b"u", value.encode("utf-8")), values)
                    self.assertIn((b"s", b"\xff"), values)

    def test_collection_values_and_all_256_bytes_survive_recovery(self):
        values = {
            "numbers": [7, 9, 10, 5, 8, 4, 2, 1],
            "labels": ["1", "0", "x", "9"],
            "pairs": {"a": 7, "b": 9},
        }
        raw = bytes(range(256))
        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                compiler = self.compiler(vm)
                source = "\n".join(
                    name + " = " + repr(value) for name, value in values.items()
                )
                source += "\npayload = " + repr(raw).removeprefix("b") + "\n"
                original, rebuilt = (
                    self.root / (vm + "-collections.pyc"),
                    self.root / (vm + "-collections-new.pyc"),
                )
                compile_standard(compiler, source, b"collections.py", original)
                report = recover_standard(original.read_bytes(), vm)
                self.assertTrue(report["complete"], report["diagnostics"])
                tree = ast.parse(report["source"])
                recovered = {
                    n.targets[0].id: ast.literal_eval(n.value)
                    for n in tree.body
                    if isinstance(n, ast.Assign)
                }
                for name, value in values.items():
                    self.assertEqual(recovered[name], value)
                compile_standard(compiler, report["source"], b"collections.py", rebuilt)
                for path in (original, rebuilt):
                    constants = parse(path.read_bytes()[8:]).fields[0].items
                    self.assertTrue(
                        any(isinstance(n, Atom) and n.value == raw for n in constants)
                    )

    def test_wrong_engine_cannot_recover_even_if_gui_was_allowed_to_open(self):
        from script_editor.data.recovery_worker import recover
        from script_editor.recovery_dependencies import RECOVERY_VERSIONS

        with patch(
            "importlib.metadata.version",
            side_effect=lambda name: (
                "6.1.8" if name == "xdis" else RECOVERY_VERSIONS[name.replace("-", "_")]
            ),
        ):
            with self.assertRaisesRegex(ValueError, "依赖版本"):
                recover(self.root / "NEVER_READ_TARGET.pyc", "py25")

    def test_stale_worker_protocol_cannot_be_mistaken_for_current_engine(self):
        compiler = self.compiler("py25")
        path = self.root / "protocol.pyc"
        compile_standard(compiler, "x=1\n", b"protocol.py", path)

        def old_worker(command, **kwargs):
            output = Path(command[command.index("--output") + 1])
            output.write_text(
                json.dumps(
                    {
                        "source": "x=1\n",
                        "complete": True,
                        "disassembly": "old",
                        "diagnostics": [],
                    }
                ),
                encoding="utf8",
            )
            return SimpleNamespace(returncode=0)

        with (
            patch(
                "script_editor.core.services.module_browser.subprocess.run",
                side_effect=old_worker,
            ),
            self.assertRaisesRegex(ValueError, "recovery result"),
        ):
            recover_standard(path.read_bytes(), "py25")

    def test_missing_catalog_opens_diagnostic_not_fake_source(self):
        state = make_state(self.root)
        with ArchiveDocument(state.bindings[0].archive) as archive:
            report = read_module(archive, 0)
        self.assertFalse(report.complete)
        self.assertEqual(report.source, "")
        self.assertTrue(report.stored_preview)
        self.assertIn("XOR", "\n".join(report.diagnostics))

    def test_resource_entry_has_explicit_decode_failure(self):
        state = make_state(self.root, "py27")
        with ArchiveDocument(state.bindings[0].archive) as archive:
            report = read_module(archive, 2)
        self.assertFalse(report.complete)
        self.assertEqual(report.source, "")
        self.assertTrue(report.diagnostics)
        self.assertTrue(report.stored_preview)

    def test_unreviewed_binding_cannot_prepare_even_with_valid_source(self):
        state = make_state(self.root)
        for kind in ("recovered-draft", "reference", "pretend-original"):
            binding = replace(state.bindings[0], source_kind=kind)
            with ArchiveDocument(binding.archive) as archive:
                with self.assertRaisesRegex(ValueError, "未核验"):
                    binding.verify(archive)

    def test_new_source_refuses_existing_and_publication_race(self):
        path = self.root / "draft.py"
        save_new_source(path, "first")
        with self.assertRaises(FileExistsError):
            save_new_source(path, "overwrite")
        self.assertEqual(path.read_text(encoding="utf-8"), "first")
        other = self.root / "race.py"
        real_link = os.link

        def race(src, dst):
            Path(dst).write_text("other process", encoding="utf-8")
            real_link(src, dst)

        with patch("script_editor.core.services.files.os.link", side_effect=race):
            with self.assertRaises(FileExistsError):
                save_new_source(other, "overwrite")
        self.assertEqual(other.read_text(encoding="utf-8"), "other process")
        self.assertFalse(list(self.root.glob(".mxsource-*")))

    def test_worker_timeout_never_returns_success_or_executes_module(self):
        compiler = self.compiler("py25")
        path = self.root / "input.pyc"
        compile_standard(compiler, "x=1\n", b"sample.py", path)
        with patch(
            "script_editor.core.services.module_browser.subprocess.run",
            side_effect=subprocess.TimeoutExpired("worker", 1),
        ):
            with self.assertRaisesRegex(ValueError, "时间限制"):
                recover_standard(path.read_bytes(), "py25")

    def test_source_budget_accepts_a_4_to_8_mib_module(self):
        """The worker's own limit is 8 MiB; validating at 4 MiB contradicted it."""
        text = "x" * (6 * 1024 * 1024)
        result = {
            "engine_protocol": "mxsj-recovery/3",
            "source": text,
            "disassembly": "",
            "complete": True,
            "diagnostics": [],
            "raw_source": text,
        }
        self.assertIs(validate_result(result), result)

    def test_source_budget_still_rejects_oversized_text(self):
        over = "x" * (MAX_SOURCE_CHARS + 1)
        for key in ("source", "raw_source"):
            result = {
                "engine_protocol": "mxsj-recovery/3",
                "source": "",
                "disassembly": "",
                "complete": True,
                "diagnostics": [],
            }
            self.assertEqual(len(over), MAX_SOURCE_CHARS + 1)
            result[key] = over
            with self.assertRaises(ValueError):
                validate_result(result)

    def test_worker_trace_keeps_the_smaller_budget(self):
        result = {
            "engine_protocol": "mxsj-recovery/3",
            "source": "",
            "disassembly": "",
            "complete": True,
            "diagnostics": [],
            "worker_stderr": "e" * (MAX_TRACE_CHARS + 1),
        }
        with self.assertRaises(ValueError):
            validate_result(result)

    def test_timeout_is_not_cached_but_a_finished_run_is(self):
        """One timeout must not poison the session for that module."""
        payload = minimal_pyc("py25")
        cache = RecoverySessionCache()
        # A second engine is present, so the primary failure is turned into a
        # candidate rather than raised: that is the path that could cache it.
        second = SimpleNamespace(source_commit="deadbeef")
        with (
            patch(
                "script_editor.core.services.module_browser._recover_primary",
                side_effect=RecoveryProcessError("timeout"),
            ),
            patch(
                "script_editor.core.services.module_browser.pycdc_candidate",
                return_value=RecoveryCandidate("pycdc", "deadbeef", "failed", "", ()),
            ),
        ):
            outcome = recover_standard(payload, "py25", pycdc=second, cache=cache)
        self.assertEqual(len(cache), 0)
        self.assertIn("timeout", [c.status for c in outcome["candidates"]])

        finished = {
            "engine_protocol": "mxsj-recovery/3",
            "source": "x=1\n",
            "disassembly": "",
            "complete": True,
            "diagnostics": [],
        }
        with (
            patch(
                "script_editor.core.services.module_browser._recover_primary",
                return_value=finished,
            ),
            patch(
                "script_editor.core.services.module_browser.pycdc_candidate",
                return_value=RecoveryCandidate("pycdc", "deadbeef", "failed", "", ()),
            ),
        ):
            recover_standard(payload, "py25", pycdc=second, cache=cache)
        self.assertEqual(len(cache), 1)

    def test_invalid_vm_and_marshal_rejected_before_worker(self):
        with patch("script_editor.core.services.module_browser.subprocess.run") as run:
            for pyc, vm in ((b"junk", "py25"), (b"junk", "py27"), (b"junk", "py3")):
                with self.assertRaises(ValueError):
                    recover_standard(pyc, vm)
            run.assert_not_called()


class RealModuleBrowserTests(unittest.TestCase):
    def test_real_registration_correct_lists_do_not_bypass_fixed_capacity(self):
        repo = os.environ.get("MXSJ_M2_REPO")
        compiler_path = os.environ.get("MXSJ_PY25")
        if not repo or not compiler_path:
            self.skipTest("opt-in real package and actual compiler required")
        root = Path(repo)
        with (
            ArchiveDocument(root / "data/script.fls") as archive,
            tempfile.TemporaryDirectory() as tmp,
        ):
            catalog = bundled_catalog(archive, root / "script_editor")
            report = read_module(archive, 4007, catalog)
            self.assertTrue(report.complete, report.diagnostics)
            self.assertIn("A = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3", report.source)
            self.assertIn("code = ['1', '0', 'x', '9'", report.source)
            path = Path(tmp) / "register.py"
            save_new_source(path, report.source)
            binding = replace(
                Binding.associate(archive, 4007, path),
                source_kind="recovered-reviewed",
                recovery_sha256=report.standard_sha256,
                filename_hex=report.filename_hex,
            )
            compiler = inspect_compiler(Path(compiler_path), "py25")
            with self.assertRaisesRegex(ValueError, "fixed XOR length"):
                prepare_build(
                    Snapshot(binding, report.source, "py25"), compiler, catalog
                )

    def test_real_script_and_data_recover_edit_without_original_authored_source(self):
        repo = os.environ.get("MXSJ_M2_REPO")
        if not repo or not all(
            os.environ.get("MXSJ_" + vm.upper()) for vm in ("py25", "py27")
        ):
            self.skipTest("opt-in real packages and actual standard compilers required")
        root = Path(repo)
        for vm, name, index in (("py25", "script.fls", 4001), ("py27", "data.fls", 75)):
            with self.subTest(vm=vm), tempfile.TemporaryDirectory() as temporary:
                work = Path(temporary)
                compiler = inspect_compiler(Path(os.environ["MXSJ_" + vm.upper()]), vm)
                with ArchiveDocument(root / "data" / name) as archive:
                    before = archive.fingerprint()
                    catalog = bundled_catalog(archive, root / "script_editor")
                    self.assertEqual(catalog is not None, vm == "py25")
                    report = read_module(archive, index, catalog)
                    self.assertTrue(report.complete, report.diagnostics)
                    self.assertGreater(len(report.disassembly), 1000)
                    self.assertTrue(report.source)
                    # Source presentation alone does not certify semantics.
                    source = report.source
                    if vm == "py25":
                        self.assertIn("Kindle Paperwhite", source)
                        # Isolated constant edit frees space inside the ORIGINAL
                        # fixed envelope. Never rescale boundaries or trim lnotab.
                        source = source.replace("Kindle Paperwhite", "K")
                    else:
                        source += "\nRECOVERY_EDITED = True\n"
                    path = work / "reviewed.py"
                    save_new_source(path, source)
                    binding = replace(
                        Binding.associate(archive, index, path),
                        filename_hex=report.filename_hex,
                        source_kind="recovered-reviewed",
                        recovery_sha256=report.standard_sha256,
                    )
                    plan = prepare_build(
                        Snapshot(binding, source, vm), compiler, catalog
                    )
                    state = ProjectState((binding,), (catalog,) if catalog else ())
                    output = work / "new.fls"
                    built, _ = publish_build(plan, output, state)
                    self.assertEqual(
                        built.unchanged_entries, 5001 if vm == "py25" else 132
                    )
                    self.assertEqual(archive.fingerprint(), before)
                    self.assertTrue(output.is_file())
