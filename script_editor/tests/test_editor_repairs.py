"""Regression coverage uses synthetic containers, never original game modules."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from native_fixtures import minimal_pyc
from test_gui import QT_ERROR
from test_workflow import make_state

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.archives.writer import write_script
from script_editor.core.compiler.runner import inspect_compiler
from script_editor.core.inspection.native import inspect_module
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import load_state
from script_editor.core.services.files import (
    SourceRevision,
    read_source_snapshot,
    save_source,
)
from script_editor.core.services.module_browser import ModuleReport, read_module
from script_editor.core.services.module_paths import scan_script_paths
from script_editor.core.services.native_build import (
    BuildReport,
    Replacement,
    _native,
    build_package,
)
from script_editor.core.services.workflow import Snapshot
from script_editor.core.vm.py25.keys import inflate_script, load_profile

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication, QFileDialog

    from script_editor.gui.window import Window


class SourceConflictTests(unittest.TestCase):
    def test_raw_bom_crlf_baseline_and_successive_save(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.py"
            path.write_bytes(b"\xef\xbb\xbfx=1\r\n")
            text, revision = read_source_snapshot(path)
            self.assertEqual(text, "x=1\n")
            save_source(path, "x=2\n", expected=revision)
            save_source(path, "x=3\n", expected=SourceRevision.capture(path))
            self.assertEqual(path.read_bytes(), b"x=3\n")

    def test_delete_recreate_and_change_during_temporary_write_are_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.py"
            path.write_text("x=1\n", encoding="utf8")
            revision = SourceRevision.capture(path)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "外部"):
                save_source(path, "x=2\n", expected=revision)
            self.assertFalse(path.exists())
            absent = SourceRevision.capture(path)
            path.write_text("external\n", encoding="utf8")
            with self.assertRaisesRegex(ValueError, "外部"):
                save_source(path, "x=2\n", expected=absent)
            current = SourceRevision.capture(path)
            with patch(
                "script_editor.core.services.files.os.fsync",
                side_effect=lambda fd: path.write_bytes(b"new external\n"),
            ):
                with self.assertRaisesRegex(ValueError, "外部"):
                    save_source(path, "x=2\n", expected=current)
            self.assertEqual(path.read_bytes(), b"new external\n")
            self.assertFalse(list(path.parent.glob(".mxscript-*")))


class ExclusionTests(unittest.TestCase):
    def test_all_module_entrypoints_reject_before_payload_or_catalog_access(self):
        archive = SimpleNamespace(
            vm="py25",
            kind="0slf",
            path=Path("synthetic.fls"),
            entries=[SimpleNamespace(directory=False, identity="synthetic")] * 1289,
            read_stored=Mock(side_effect=AssertionError("payload must not be read")),
            fingerprint=lambda: "0" * 64,
            _assert_unchanged=lambda: None,
        )
        self.assertFalse(read_module(archive, 1288).source)
        actions = [
            lambda: inspect_module(archive, 1288),
            lambda: inflate_script(archive, 1288),
            lambda: load_profile(
                archive,
                1288,
                Path("not-opened.json"),
                archive_sha256="",
                catalog_sha256="",
            ),
            lambda: _native(archive, Replacement(1288, "", b""), None),
            lambda: Binding.associate(archive, 1288, Path("not-opened.py")),
        ]
        for action in actions:
            with (
                self.subTest(action=action),
                self.assertRaisesRegex(ValueError, "excluded_by_policy"),
            ):
                action()
        archive.read_stored.assert_not_called()
        with tempfile.TemporaryDirectory() as directory:
            keys = Path(directory) / "keys.json"
            keys.write_text('{"1288": {}}', encoding="utf8")
            catalog = SimpleNamespace(
                path=keys,
                sha256=hashlib.sha256(keys.read_bytes()).hexdigest(),
                verify=lambda source: None,
            )
            archive.entries = [SimpleNamespace(index=1288)]
            paths, errors = scan_script_paths(archive, catalog)
            self.assertFalse(paths)
            self.assertIn("excluded_by_policy", errors[1288])
            archive.read_stored.assert_not_called()

    def test_direct_builder_rejects_exclusion_before_audit_or_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = Mock()
            archive.vm = "py25"
            archive.fingerprint.return_value = "0" * 64
            archive.__enter__ = Mock(return_value=archive)
            archive.__exit__ = Mock(return_value=False)
            with (
                patch(
                    "script_editor.core.services.native_build.ArchiveDocument",
                    return_value=archive,
                ),
                patch(
                    "script_editor.core.services.native_build.audit_standard"
                ) as audit,
                self.assertRaisesRegex(ValueError, "excluded_by_policy"),
            ):
                build_package(
                    root / "source.fls",
                    root / "output.fls",
                    source_sha256="0" * 64,
                    replacements=(Replacement(1288, "", b""),),
                    compiler=SimpleNamespace(vm="py25"),
                )
            audit.assert_not_called()
            archive.read_stored.assert_not_called()
            self.assertFalse((root / "output.fls").exists())


@unittest.skipIf(bool(QT_ERROR), "GUI unavailable: " + QT_ERROR)
class EditorRepairGuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.windows = []
        self.window = self.new_window()

    def new_window(self):
        window = Window(self.root)
        self.windows.append(window)
        return window

    def tearDown(self):
        for window in self.windows:
            for i in range(window.tabs.count()):
                window.tabs.widget(i).editor.document().setModified(False)
            window.project_dirty = False
            window.close()
            window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def save_project(self, window, path):
        with patch.object(QFileDialog, "getSaveFileName", return_value=(str(path), "")):
            self.assertTrue(window.save_project())

    def test_external_update_preserved_with_dirty_buffer_and_undo(self):
        source = self.root / "source.py"
        source.write_bytes(b"x=1\n")
        tab = self.window.add_source(source)
        tab.editor.insertPlainText("# editor\n")
        text = tab.editor.toPlainText()
        source.write_bytes(b"x=3  # external\n")
        with self.assertRaisesRegex(ValueError, "外部"):
            self.window.save_tab(tab)
        self.assertEqual(source.read_bytes(), b"x=3  # external\n")
        self.assertEqual(tab.editor.toPlainText(), text)
        self.assertTrue(tab.editor.document().isModified())
        self.assertTrue(tab.editor.document().isUndoAvailable())

    def test_project_restoration_keeps_original_disk_baseline(self):
        source = self.root / "source.py"
        source.write_bytes(b"x=1\n")
        tab = self.window.add_source(source)
        tab.editor.insertPlainText("# editor\n")
        project = self.root / "session.mxscript.json"
        self.save_project(self.window, project)
        source.write_bytes(b"x=3  # external\n")
        restored = self.new_window()
        restored.adopt_project(restored.prepare_project(project))
        with self.assertRaisesRegex(ValueError, "外部"):
            restored.save_tab(restored.current())
        self.assertEqual(source.read_bytes(), b"x=3  # external\n")

    def test_save_draft_marks_project_dirty_and_resaves_real_path(self):
        virtual = self.root / ".virtual.recovered.py"
        tab = self.window.add_source(
            virtual, text="x=1\n", source_kind="recovered-draft"
        )
        tab.draft_saved = False
        project = self.root / "session.mxscript.json"
        self.save_project(self.window, project)
        self.assertFalse(self.window.project_dirty)
        renamed = self.root / "draft.py"
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=(str(renamed), "")
        ):
            self.assertTrue(self.window.save_draft(tab))
        self.assertTrue(self.window.project_dirty)
        self.save_project(self.window, project)
        state = load_state(project)
        self.assertEqual(state.editors[0].path, renamed)
        self.assertTrue(state.editors[0].draft_saved)
        self.assertEqual(
            state.editors[0].disk_sha256,
            hashlib.sha256(renamed.read_bytes()).hexdigest(),
        )

    def setup_continuation(self):
        state = make_state(self.root, two_modules=True)
        old = ArchiveDocument(state.bindings[0].archive)
        self.window.add_archive(old)
        self.window.bindings, self.window.catalogs = (
            list(state.bindings),
            list(state.catalogs),
        )
        standard, filename, _ = inspect_module(old, 1, state.catalogs[0])
        report = ModuleReport(
            old.path,
            old.fingerprint(),
            1,
            old.entries[1].identity,
            "py25",
            filename.hex(),
            hashlib.sha256(standard).hexdigest(),
            "# coding: utf-8\nx=1\n",
            True,
            "",
            (),
            "",
        )
        tab = self.window.open_recovery_candidate(report)
        tab.editor.insertPlainText("# keep edit\n")
        return state, old, report, tab

    def publish_synthetic(self, state, old, name, changed=0, value=2):
        # Test GUI transition with real codec/writer. No compiler audit is claimed.
        _, _, profile = inspect_module(old, changed, state.catalogs[0])
        replacement = Replacement(
            changed, old.entries[changed].identity, minimal_pyc("py25", value)
        )
        output = self.root / name
        with output.open("w+b") as out:
            write_script(old, {changed: _native(old, replacement, profile)}, out)
        new = ArchiveDocument(output)
        digest = new.fingerprint()
        next_state = replace(
            state,
            bindings=tuple(
                replace(b, archive=output, fingerprint=digest) for b in state.bindings
            ),
            catalogs=tuple(
                replace(c, archive=output, fingerprint=digest) for c in state.catalogs
            ),
        )
        build = BuildReport(old.fingerprint(), digest, (changed,), 2, output)
        plan = SimpleNamespace(snapshot=Snapshot(state.bindings[0], "x=2\n", "py25"))
        self.window.adopt_build(plan, (build, next_state, new, None))
        return next_state, new, build

    def test_unchanged_draft_continues_twice_and_project_preserves_provenance(self):
        state, old, origin, tab = self.setup_continuation()
        text = tab.editor.toPlainText()
        state, new, _ = self.publish_synthetic(state, old, "new.fls")
        self.assertEqual(tab.recovery.archive, origin.archive)
        self.assertEqual(tab.recovery.fingerprint, origin.fingerprint)
        self.assertEqual(tab.recovery.current_archive, new.path)
        state, newer, _ = self.publish_synthetic(state, new, "newer.fls", value=3)
        self.assertEqual(tab.recovery.current_archive, newer.path)
        self.assertEqual(tab.editor.toPlainText(), text)
        self.assertTrue(tab.editor.document().isUndoAvailable())
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(1))
        self.window.tabs.setCurrentWidget(tab)
        with patch.object(self.window, "fail") as fail:
            self.window.adopt_recovery()
        self.assertIn("编译器", str(fail.call_args.args[0]))
        project = self.root / "continued.mxscript.json"
        self.save_project(self.window, project)
        loaded = load_state(project).editors[0].report
        self.assertEqual(loaded, tab.recovery)
        restored = self.new_window()
        restored.adopt_project(restored.prepare_project(project))
        restored_tab = next(
            restored.tabs.widget(i)
            for i in range(restored.tabs.count())
            if restored.tabs.widget(i).recovery is not None
        )
        self.assertEqual(restored_tab.recovery.current_archive, newer.path)
        self.assertEqual(restored_tab.recovery.archive, origin.archive)

    def test_continued_draft_reaches_real_compile_and_adoption(self):
        executable = os.environ.get("MXSJ_PY25")
        if not executable:
            self.skipTest("actual standard 2.5.6 required")
        state, old, origin, tab = self.setup_continuation()
        _, new, _ = self.publish_synthetic(state, old, "new.fls")
        compiler = inspect_compiler(Path(executable), "py25")
        self.window.compilers["py25"] = compiler
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(1))
        self.window.tabs.setCurrentWidget(tab)
        from PySide6.QtWidgets import QMessageBox

        with (
            patch.object(
                QFileDialog,
                "getSaveFileName",
                return_value=(str(self.root / "draft.py"), ""),
            ),
            patch.object(
                QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
            ),
            patch.object(
                self.window, "task", side_effect=lambda work, done: done(work())
            ),
            patch.object(self.window, "fail") as fail,
        ):
            self.window.adopt_recovery()
        fail.assert_not_called()
        self.assertEqual(tab.source_kind, "recovered-reviewed")
        binding = next(b for b in self.window.bindings if b.index == 1)
        self.assertEqual(binding.archive, new.path)
        self.assertEqual(tab.recovery.archive, origin.archive)

    def test_legacy_snapshot_and_invalid_continuation_target(self):
        state, old, origin, tab = self.setup_continuation()
        project = self.root / "legacy.mxscript.json"
        self.save_project(self.window, project)
        doc = json.loads(project.read_bytes())
        for row in doc["editors"]:
            row.pop("disk_sha256")
            row["report"].pop("target_archive")
            row["report"].pop("target_fingerprint")
        project.write_text(json.dumps(doc), encoding="utf8")
        loaded = load_state(project).editors[0]
        self.assertEqual(loaded.disk_sha256, "")
        self.assertEqual(loaded.report, origin)
        _, new, _ = self.publish_synthetic(state, old, "new.fls")
        self.save_project(self.window, project)
        doc = json.loads(project.read_bytes())
        doc["editors"][0]["report"]["target_fingerprint"] = "0" * 64
        project.write_text(json.dumps(doc), encoding="utf8")
        with self.assertRaisesRegex(ValueError, "继续采用目标"):
            load_state(project)

    def test_changed_draft_does_not_migrate(self):
        state, old, origin, tab = self.setup_continuation()
        _, new, _ = self.publish_synthetic(state, old, "new.fls", changed=1)
        self.assertEqual(tab.recovery, origin)
        self.assertNotEqual(tab.recovery.current_archive, new.path)

    def test_forged_target_cannot_pass_full_bytecode_source_check(self):
        state, old, origin, tab = self.setup_continuation()
        _, new, build = self.publish_synthetic(state, old, "new.fls", changed=1)
        tab.recovery = replace(
            origin, target_archive=new.path, target_fingerprint=build.output_sha256
        )
        tab.path = self.root / "draft.py"
        tab.path.write_text(tab.editor.toPlainText(), encoding="utf8")
        tab.draft_saved = True
        self.window.tree.setCurrentItem(self.window.tree.topLevelItem(0).child(1))
        self.window.tabs.setCurrentWidget(tab)
        self.window.compilers["py25"] = object()
        with (
            patch.object(
                self.window, "task", side_effect=lambda work, done: done(work())
            ),
            patch.object(self.window, "fail") as fail,
            patch("script_editor.gui.module_actions.prepare_build") as prepare,
        ):
            self.window.adopt_recovery()
        prepare.assert_not_called()
        self.assertIn("标准字节码已变化", str(fail.call_args.args[0]))
