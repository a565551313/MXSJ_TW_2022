from __future__ import annotations

import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from native_fixtures import data_fixture, minimal_pyc, raw_string, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import Compiler, inspect_compiler
from script_editor.core.inspection.native import inspect_module
from script_editor.core.inspection.references import inspect_references
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import (
    CatalogRef,
    ProjectState,
    load_state,
    save_state,
)
from script_editor.core.services.workflow import (
    Snapshot,
    prepare_build,
    prepare_package,
    publish_build,
    text_sha,
)
from script_editor.core.vm.marshal_tree import parse
from script_editor.core.vm.py25.keys import read_catalog


def make_state(
    root, vm="py25", *, two_modules=False, filename=b"authored.py", expanded_size=65536
):
    source = root / (vm + ".py")
    source.write_text("# coding: utf-8\nx=0\n", encoding="utf-8")
    package = root / (vm + ".fls")
    catalogs = ()
    if vm == "py25":
        raw, keys = script_fixture(
            expanded_size=expanded_size, two_modules=two_modules, filename=filename
        )
        package.write_bytes(raw)
        path = root / "keys.json"
        path.write_text(json.dumps(keys), encoding="utf-8")
    else:
        package.write_bytes(data_fixture(filename=filename))
    with ArchiveDocument(package) as archive:
        binding = Binding.associate(archive, 0 if vm == "py25" else 1, source)
        if vm == "py25":
            catalogs = (
                CatalogRef(archive.path, archive.fingerprint(), path, file_sha(path)),
            )
        _, filename, _ = inspect_module(
            archive, binding.index, catalogs[0] if catalogs else None
        )
        binding = replace(binding, filename_hex=filename.hex())
    return ProjectState((binding,), catalogs)


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProjectStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-m3-project-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = make_state(self.root)
        self.project = self.root / "test.mxscript.json"

    def save(self):
        save_state(self.project, self.state.bindings, self.state.catalogs)

    def test_schema2_roundtrip_and_relative_move_without_copies(self):
        binding = replace(
            self.state.bindings[0], built_source_sha256=text_sha("compiled buffer")
        )
        self.state = replace(self.state, bindings=(binding,))
        self.save()
        text = self.project.read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), text)
        self.assertNotIn("compiled buffer", text)
        self.assertNotIn("executable", text)
        self.assertEqual(load_state(self.project), self.state)
        moved = self.root / "moved"
        moved.mkdir()
        for path in self.root.iterdir():
            if path.is_file():
                shutil.copyfile(path, moved / path.name)
        loaded = load_state(moved / self.project.name)
        self.assertEqual(loaded.bindings[0].archive.parent, moved)
        self.assertEqual(loaded.bindings[0].source.parent, moved)
        self.assertEqual(loaded.catalogs[0].path.parent, moved)

    def test_schema1_compatibility(self):
        self.save()
        doc = json.loads(self.project.read_text(encoding="utf-8"))
        doc["schema"] = 1
        doc.pop("catalogs")
        doc["bindings"][0].pop("filename_hex")
        doc["bindings"][0].pop("built_source_sha256")
        self.project.write_text(json.dumps(doc), encoding="utf-8")
        state = load_state(self.project)
        self.assertEqual(state.bindings[0].filename_hex, "")
        self.assertEqual(state.catalogs, ())

    def test_source_all_utf8_preflight_and_missing_file(self):
        self.save()
        source = self.state.bindings[0].source
        source.write_bytes(b"\xff\xfe")
        with self.assertRaises(UnicodeError):
            load_state(self.project)
        source.unlink()
        with self.assertRaises(FileNotFoundError):
            load_state(self.project)

    def test_changed_catalog_or_package_rejected(self):
        self.save()
        catalog = self.state.catalogs[0].path
        old = catalog.read_bytes()
        catalog.write_bytes(old + b" ")
        with self.assertRaisesRegex(ValueError, "XOR"):
            load_state(self.project)
        catalog.write_bytes(old)
        package = self.state.bindings[0].archive
        package.write_bytes(package.read_bytes() + b"changed")
        with self.assertRaises(ValueError):
            load_state(self.project)

    def test_duplicate_binding_catalog_or_bad_filename_rejected(self):
        self.save()
        original = self.project.read_text(encoding="utf-8")
        for field in ("bindings", "catalogs", "filename_hex", "built_source_sha256"):
            with self.subTest(field=field):
                doc = json.loads(original)
                if field in ("bindings", "catalogs"):
                    doc[field] *= 2
                else:
                    doc["bindings"][0][field] = "not-hex"
                self.project.write_text(json.dumps(doc), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_state(self.project)

    def test_project_cannot_overwrite_source_alias(self):
        os.link(self.state.bindings[0].source, self.project)
        before = self.project.read_bytes()
        with self.assertRaises(ValueError):
            self.save()
        self.assertEqual(self.project.read_bytes(), before)

    def test_generator_metadata_still_protects_source_aliases(self):
        os.link(self.state.bindings[0].source, self.project)
        before = self.project.read_bytes()
        with self.assertRaises(ValueError):
            save_state(
                self.project, iter(self.state.bindings), iter(self.state.catalogs)
            )
        self.assertEqual(self.project.read_bytes(), before)

    def test_catalog_read_bounded_even_when_oversized(self):
        path = self.root / "large.json"
        with path.open("wb") as stream:
            stream.truncate(16 * 1024 * 1024 + 1)
        with self.assertRaisesRegex(ValueError, "16MiB"):
            read_catalog(path)


class InspectionTests(unittest.TestCase):
    def test_filename_raw_interned_and_reference_bytes_not_guessed(self):
        filename = b"login/\xb5\xf9\xff.py"
        for vm in ("py25", "py27"):
            base = minimal_pyc(vm).replace(
                raw_string(b"authored.py"), raw_string(filename)
            )
            for tag in (b"s", b"t", b"R"):
                with self.subTest(vm=vm, tag=tag):
                    raw = base
                    if tag == b"t":
                        raw = raw.replace(
                            raw_string(filename), b"t" + raw_string(filename)[1:]
                        )
                    elif tag == b"R":
                        # Intern in consts first, then reference the same bytes.
                        raw = raw.replace(
                            b"(\1\0\0\0i" + struct.pack("<i", 1),
                            b"(\1\0\0\0t" + raw_string(filename)[1:],
                        )
                        raw = raw.replace(raw_string(filename), b"R" + bytes(4))
                    self.assertEqual(parse(raw[8:]).fields[5].value, filename)

    def test_static_hints_not_comment_string_or_execution(self):
        text = (
            "# api.FONT_EDIT and 'fake.dlg'\n"
            "warning='api.FONT_EDIT'\n"
            "path=r'login\\form.dlg'\n"
            "other='\\xff\\xfe/form.dlg'\n"
            "panel.GetObject('account')\napi.FONT_EDIT\n"
            "raise RuntimeError('DO NOT EXECUTE')\n"
        )
        hints = inspect_references(text)
        self.assertEqual(len(hints), 4)
        self.assertEqual(hints[0].text, "login\\form.dlg")
        self.assertEqual(hints[1].text, r"\xff\xfe/form.dlg")
        self.assertEqual(hints[2].text, "account")
        self.assertEqual(hints[3].line, 6)


class ResizePreviewTests(unittest.TestCase):
    """A resized module must survive ``prepare_build``'s own round-trip.

    The GUI reaches the package through ``prepare_build`` (F6 preview) and
    ``prepare_package`` (loose Ctrl+S), long before ``build_package`` runs. The
    round-trip there used to read back with the fixed-length ``crypt()``, so
    every resized save failed with "boundary rescaling forbidden" even after the
    experimental switch was turned on.
    """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-resize-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        # 512-byte slot: a 794-byte native payload needs a real resize.
        self.state = make_state(self.root, expanded_size=512)
        self.binding = self.state.bindings[0]
        self.catalog = self.state.catalogs[0]
        self.oversized = minimal_pyc("py25", 7, code=b"d\x01\x00S" + b"\x09" * 700)
        self.compiler = Compiler(
            Path(sys.executable), "py25", "unit-test-only", 64, "test"
        )

    def prepare(self, allow_resize):
        snapshot = Snapshot(self.binding, "# coding: utf-8\nx=0\n", "py25")

        def fake_compile(_compiler, _text, _filename, path):
            path.write_bytes(self.oversized)

        with (
            patch(
                "script_editor.core.services.workflow.compile_standard",
                side_effect=fake_compile,
            ),
            patch("script_editor.core.services.workflow.audit_standard"),
        ):
            return prepare_build(
                snapshot, self.compiler, self.catalog, allow_resize=allow_resize
            )

    def test_preview_round_trips_a_resized_module(self):
        plan = self.prepare(True)
        self.assertTrue(plan.resized)
        self.assertEqual(plan.replacement.standard_pyc, self.oversized)

    def test_preview_still_refuses_without_the_switch(self):
        with self.assertRaisesRegex(ValueError, "no shrink/rescale"):
            self.prepare(False)

    def test_package_plan_for_loose_save_carries_the_consent(self):
        snapshot = Snapshot(self.binding, "# coding: utf-8\nx=0\n", "py25")

        def fake_compile(_compiler, _text, _filename, path):
            path.write_bytes(self.oversized)

        with (
            patch(
                "script_editor.core.services.workflow.compile_standard",
                side_effect=fake_compile,
            ),
            patch("script_editor.core.services.workflow.audit_standard"),
        ):
            plan = prepare_package(
                (snapshot,), self.compiler, self.catalog, allow_resize=True
            )
        self.assertEqual(len(plan.entries), 1)
        self.assertTrue(plan.entries[0].resized)


class ActualWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-m3-workflow-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def compiler(self, vm):
        exe = os.environ.get("MXSJ_" + vm.upper())
        if not exe:
            self.skipTest("actual standard compiler not configured: " + vm)
        return inspect_compiler(Path(exe), vm)

    def prepare(self, vm="py25", **kwargs):
        state = make_state(self.root, vm, **kwargs)
        compiler = self.compiler(vm)
        sentinel = self.root / "must-not-execute"
        text = (
            "# coding: utf-8\nx=42\ntitle=u'測試'\n"
            f"open({str(sentinel)!r},'w').write('EXECUTED')\n"
            "raise RuntimeError('DO NOT EXECUTE')\n"
        )
        snap = Snapshot(state.bindings[0], text, vm, unsaved=True)
        plan = prepare_build(
            snap, compiler, state.catalogs[0] if state.catalogs else None
        )
        self.assertFalse(sentinel.exists())
        return state, plan

    def test_real_both_vm_preview_publish_save_reopen_and_continue(self):
        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                state, plan = self.prepare(vm)
                source = state.bindings[0].source
                disk, original = (
                    source.read_bytes(),
                    file_sha(state.bindings[0].archive),
                )
                # Preparation/implicit cancellation publishes nothing, changes nothing.
                self.assertFalse((self.root / "new.fls").exists())
                self.assertTrue(plan.payload_changed)
                self.assertIn("无可靠", plan.diff)
                report, rebased = publish_build(
                    plan, self.root / (vm + "-new.fls"), state
                )
                self.assertEqual(source.read_bytes(), disk)
                self.assertEqual(file_sha(state.bindings[0].archive), original)
                binding = rebased.bindings[0]
                self.assertEqual(binding.archive, report.output)
                self.assertEqual(
                    binding.built_source_sha256, text_sha(plan.snapshot.text)
                )
                self.assertEqual(report.modified_indexes, (binding.index,))
                with ArchiveDocument(report.output) as archive:
                    pyc, filename, _ = inspect_module(
                        archive,
                        binding.index,
                        rebased.catalogs[0] if rebased.catalogs else None,
                    )
                self.assertEqual(filename, b"authored.py")
                self.assertEqual(pyc[8:], plan.replacement.standard_pyc[8:])
                project = self.root / (vm + ".mxscript.json")
                save_state(project, rebased.bindings, rebased.catalogs)
                reopened = load_state(project)
                self.assertEqual(reopened, rebased)
                second = prepare_build(
                    Snapshot(binding, plan.snapshot.text + "x=99\n", vm),
                    plan.compiler,
                    reopened.catalogs[0] if reopened.catalogs else None,
                    baseline_text=plan.snapshot.text,
                )
                self.assertIn("+x=99", second.diff)
                publish_build(second, self.root / (vm + "-second.fls"), reopened)
                self.assertEqual(source.read_bytes(), disk)
                no_change = prepare_build(
                    Snapshot(binding, plan.snapshot.text, vm),
                    plan.compiler,
                    reopened.catalogs[0] if reopened.catalogs else None,
                )
                self.assertFalse(no_change.payload_changed)
                with self.assertRaises(ValueError):
                    publish_build(no_change, self.root / "no-change.fls", reopened)

    def test_unselected_binding_rebased_but_sha_and_payload_not_modified(self):
        state, plan = self.prepare(two_modules=True)
        with ArchiveDocument(state.bindings[0].archive) as archive:
            other = replace(
                Binding.associate(archive, 1, state.bindings[0].source),
                built_source_sha256="a" * 64,
            )
            before = archive.read_stored(1)
        state = replace(state, bindings=state.bindings + (other,))
        report, rebased = publish_build(plan, self.root / "next.fls", state)
        self.assertEqual(rebased.bindings[1].built_source_sha256, "a" * 64)
        self.assertEqual(rebased.bindings[1].archive, report.output)
        with ArchiveDocument(report.output) as archive:
            self.assertEqual(archive.read_stored(1), before)
        self.assertEqual(rebased.catalogs[0].fingerprint, report.output_sha256)

    def test_compile_error_reference_vm_and_stale_baseline_leave_state(self):
        state, plan = self.prepare()
        snap = plan.snapshot
        before = tuple(self.root.iterdir())
        for snapshot, baseline in (
            (replace(snap, reference=True), None),
            (replace(snap, vm="py27"), None),
            (replace(snap, text="def broken("), None),
            (snap, "wrong baseline"),
        ):
            with self.subTest(snapshot=snapshot, baseline=baseline):
                with self.assertRaises(ValueError):
                    prepare_build(snapshot, plan.compiler, state.catalogs[0], baseline)
        self.assertEqual(tuple(self.root.iterdir()), before)
        with self.assertRaises(ValueError):
            prepare_build(snap, plan.compiler)  # No implicit XOR catalog discovery.

    def test_publish_stale_binding_catalog_or_inconsistent_plan_refused(self):
        state, plan = self.prepare()
        target = self.root / "next.fls"
        for candidate, current in (
            (plan, ProjectState(())),
            (plan, replace(state, catalogs=())),
            (plan, replace(state, bindings=state.bindings * 2)),
            (replace(plan, source_sha256="0" * 64), state),
            (replace(plan, replacement=replace(plan.replacement, index=1)), state),
        ):
            with self.assertRaises(ValueError):
                publish_build(candidate, target, current)
            self.assertFalse(target.exists())
        state.catalogs[0].path.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            publish_build(plan, target, state)
        self.assertFalse(target.exists())

    def test_existing_output_and_failed_publication_preserve_source_and_state(self):
        state, plan = self.prepare()
        target = self.root / "next.fls"
        target.write_bytes(b"KEEP")
        original = file_sha(state.bindings[0].archive)
        with self.assertRaises(ValueError):
            publish_build(plan, target, state)
        self.assertEqual(target.read_bytes(), b"KEEP")
        target.unlink()
        with self.assertRaises(ValueError):
            publish_build(plan, target, state, protected=(target,))
        self.assertFalse(target.exists())
        with patch(
            "script_editor.core.services.native_build.os.link",
            side_effect=OSError("no hardlinks"),
        ):
            with self.assertRaises(OSError):
                publish_build(plan, target, state)
        self.assertFalse(target.exists())
        self.assertEqual(file_sha(state.bindings[0].archive), original)
        self.assertEqual(state.bindings[0].built_source_sha256, "")
        self.assertFalse(list(self.root.glob(".mxscript-build-*")))

    def test_real_both_compilers_preserve_non_utf8_filename_bytes(self):
        filename = b"login/\xb5\xf9\xff.py"
        for vm in ("py25", "py27"):
            with self.subTest(vm=vm):
                state, plan = self.prepare(vm, filename=filename)
                self.assertEqual(plan.filename, filename)
                self.assertEqual(
                    parse(plan.replacement.standard_pyc[8:]).fields[5].value, filename
                )
                report, rebased = publish_build(
                    plan, self.root / (vm + "-raw-name.fls"), state
                )
                with ArchiveDocument(report.output) as archive:
                    _, result, _ = inspect_module(
                        archive,
                        rebased.bindings[0].index,
                        rebased.catalogs[0] if rebased.catalogs else None,
                    )
                self.assertEqual(result, filename)


class RealRegistrationWorkflowTests(unittest.TestCase):
    def test_registration_source_prepare_publish_reopen_continue(self):
        repo = os.environ.get("MXSJ_M2_REPO")
        exe = os.environ.get("MXSJ_PY25")
        if not repo or not exe:
            self.skipTest("opt-in real package and standard 2.5.6 required")
        repo = Path(repo)
        compiler = inspect_compiler(Path(exe), "py25")
        with tempfile.TemporaryDirectory(prefix="mxscript-m3-registration-") as temp:
            root = Path(temp)
            source = root / "register.py"
            shutil.copyfile(repo / "tools/registration/register.py", source)
            text = source.read_text(encoding="utf-8")
            original_source = source.read_bytes()
            package = repo / "data/script.fls"
            keys = repo / "tools/decompiler/script_fls_keys.json"
            with ArchiveDocument(package) as archive:
                binding = Binding.associate(archive, 4007, source)
                catalog = CatalogRef(
                    archive.path, archive.fingerprint(), keys, file_sha(keys)
                )
            state = ProjectState((binding,), (catalog,))
            plan = prepare_build(Snapshot(binding, text, "py25"), compiler, catalog)
            report, next_state = publish_build(
                plan, root / "registration-offline.fls", state
            )
            self.assertEqual(report.unchanged_entries, 5001)
            self.assertEqual(next_state.bindings[0].built_source_sha256, text_sha(text))
            save_state(
                root / "register.mxscript.json",
                next_state.bindings,
                next_state.catalogs,
            )
            reopened = load_state(root / "register.mxscript.json")
            next_plan = prepare_build(
                Snapshot(reopened.bindings[0], text + "\nM3_OFFLINE_ONLY=1\n", "py25"),
                compiler,
                reopened.catalogs[0],
                baseline_text=text,
            )
            next_report, _ = publish_build(
                next_plan, root / "registration-second-offline.fls", reopened
            )
            self.assertEqual(next_report.unchanged_entries, 5001)
            self.assertEqual(source.read_bytes(), original_source)
            self.assertEqual(file_sha(package), binding.fingerprint)
            self.assertEqual(file_sha(keys), catalog.sha256)

    def test_real_data_offline_prepare_publish_reopen_continue(self):
        repo = os.environ.get("MXSJ_M2_REPO")
        exe = os.environ.get("MXSJ_PY27")
        if not repo or not exe:
            self.skipTest("opt-in real package and standard 2.7.13 required")
        compiler = inspect_compiler(Path(exe), "py27")
        with tempfile.TemporaryDirectory(prefix="mxscript-m3-data-offline-") as temp:
            root = Path(temp)
            source = root / "offline-only.py"
            source.write_text("MARKER='offline-only-m3-probe'\n", encoding="utf-8")
            text = source.read_text(encoding="utf-8")
            # Deliberately replacing a core library: never distribute/load in game.
            package = Path(repo) / "data/data.fls"
            with ArchiveDocument(package) as archive:
                binding = Binding.associate(archive, 75, source)
            state = ProjectState((binding,))
            plan = prepare_build(Snapshot(binding, text, "py27"), compiler)
            report, state = publish_build(plan, root / "offline-1.fls", state)
            self.assertEqual(report.unchanged_entries, 132)
            project = root / "offline.mxscript.json"
            save_state(project, state.bindings)
            state = load_state(project)
            plan = prepare_build(
                Snapshot(state.bindings[0], text + "VALUE=2\n", "py27"),
                compiler,
                baseline_text=text,
            )
            report, _ = publish_build(plan, root / "offline-2.fls", state)
            self.assertEqual(report.unchanged_entries, 132)
            self.assertEqual(file_sha(package), binding.fingerprint)
            self.assertEqual(source.read_text(encoding="utf-8"), text)
