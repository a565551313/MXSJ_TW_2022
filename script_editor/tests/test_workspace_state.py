from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from corpus_fixtures import fixture

from script_editor.core.project.storage import load_state, save_state
from script_editor.core.project.workspace import EditorState
from script_editor.core.services.corpus_manifest import load_corpus
from script_editor.core.services.corpus_recovery import corpus_report


class WorkspaceStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive, self.catalog, self.manifest, _ = fixture(self.root)
        self.corpus = load_corpus(self.archive, self.manifest)
        self.report = corpus_report(
            self.corpus, self.archive, 0, self.catalog
        ).for_candidate(1)
        self.editor = EditorState(
            self.root / "unsaved.py",
            "py25",
            "recovered-draft",
            "# my unsaved edits\n",
            True,
            False,
            self.report,
        )
        self.path = self.root / "session.mxscript.json"

    def tearDown(self):
        self.archive.close()
        self.temp.cleanup()

    def save(self, **kwargs):
        save_state(
            self.path,
            (),
            (self.catalog,),
            editors=(self.editor,),
            corpora=(self.corpus.ref,),
            **kwargs,
        )

    def test_unsaved_draft_report_and_exact_raw_bytes_roundtrip(self):
        self.save()
        state = load_state(self.path)
        self.assertEqual(state.editors, (self.editor,))
        self.assertEqual(state.corpora, (self.corpus.ref,))
        self.assertFalse(state.bindings)
        self.assertFalse(self.editor.path.exists())
        self.assertEqual(state.editors[0].report.candidates[1].stdout, b"x='\xff'\n")
        self.assertFalse(state.editors[0].report.candidates[1].complete)
        self.assertEqual(json.loads(self.path.read_bytes())["schema"], 3)

    def test_missing_external_corpus_does_not_lose_saved_draft(self):
        self.save()
        self.manifest.unlink()
        state = load_state(self.path)
        self.assertEqual(state.editors[0].text, self.editor.text)
        self.assertEqual(state.corpora[0].sha256, self.corpus.ref.sha256)

    def test_sources_not_overwritten_when_embedded_dirty_text_saved(self):
        self.editor.path.write_text("disk version\n", encoding="utf8")
        self.editor = replace(self.editor, draft_saved=True)
        self.save()
        self.assertEqual(self.editor.path.read_text(encoding="utf8"), "disk version\n")
        self.assertEqual(load_state(self.path).editors[0].text, "# my unsaved edits\n")

    def test_portable_relative_paths_move_with_original_and_catalog(self):
        self.save()
        self.archive.close()
        import shutil

        destination = self.root / "moved"
        destination.mkdir()
        for name in ("session.mxscript.json", "original.fls", "keys.json"):
            shutil.move(str(self.root / name), destination / name)
        state = load_state(destination / "session.mxscript.json")
        self.assertEqual(
            state.editors[0].report.archive, (destination / "original.fls").resolve()
        )
        self.assertEqual(state.editors[0].path, (destination / "unsaved.py").resolve())

    def test_changed_original_package_rejected_without_any_source_writes(self):
        self.save()
        self.archive.path.write_bytes(self.archive.path.read_bytes() + b"changed")
        with self.assertRaises(ValueError):
            load_state(self.path)
        self.assertFalse(self.editor.path.exists())

    def test_malformed_base64_or_snapshot_kind_does_not_gain_trust(self):
        self.save()
        original = json.loads(self.path.read_bytes())
        import copy

        for change in ("base64", "kind", "vm", "identity"):
            doc = copy.deepcopy(original)
            row = doc["editors"][0]
            if change == "base64":
                row["report"]["candidates"][0]["stdout"] = "!invalid!"
            if change == "kind":
                row["source_kind"] = "recovered-reviewed"
            if change == "vm":
                row["vm"] = "py27"
            if change == "identity":
                row["report"]["identity"] = "wrong"
            self.path.write_text(json.dumps(doc), encoding="utf8")
            with self.subTest(change=change), self.assertRaises(ValueError):
                load_state(self.path)

    def test_policy_report_cannot_be_loaded_as_a_draft(self):
        self.save()
        doc = json.loads(self.path.read_bytes())
        doc["editors"][0]["report"]["index"] = 1288
        self.path.write_text(json.dumps(doc), encoding="utf8")
        with self.assertRaises(ValueError):
            load_state(self.path)

    def test_size_failure_is_atomic_and_source_aliases_protected(self):
        self.save()
        before = self.path.read_bytes()
        with patch("script_editor.core.project.workspace.MAX_TEXT", 2):
            with self.assertRaises(ValueError):
                self.save()
        self.assertEqual(self.path.read_bytes(), before)
        with self.assertRaises(ValueError):
            save_state(self.editor.path, (), editors=(self.editor,))

    def test_project_cannot_write_inside_readonly_corpus(self):
        with self.assertRaises(ValueError):
            save_state(
                self.manifest.parent / "new.mxscript.json",
                (),
                corpora=(self.corpus.ref,),
            )

    def test_large_offline_corpus_candidate_over_process_limit_can_continue(self):
        from corpus_fixtures import write_manifest

        rows = [json.loads(line) for line in self.manifest.read_bytes().splitlines()]
        large = b"x=1\n" * (524288 + 1)
        data = rows[0]["engines"]["uncompyle6"]
        import hashlib

        for ref in (data["stdout"], data["candidates"][0]):
            target = self.manifest.parent.parent / ref["path"]
            target.write_bytes(large)
            ref.update(bytes=len(large), sha256=hashlib.sha256(large).hexdigest())
        write_manifest(self.manifest, rows)
        self.corpus = load_corpus(self.archive, self.manifest)
        self.report = corpus_report(self.corpus, self.archive, 0, self.catalog)
        self.editor = replace(self.editor, text=self.report.source, report=self.report)
        self.save()
        state = load_state(self.path)
        self.assertEqual(state.editors[0], self.editor)
        self.assertGreater(
            len(state.editors[0].report.candidates[0].stdout), 2 * 1024 * 1024
        )

    def test_embedded_authored_buffer_can_resume_without_disk_source(self):
        from script_editor.core.project.document import Binding

        self.editor.path.write_text("disk original\n", encoding="utf8")
        binding = Binding.associate(self.archive, 0, self.editor.path)
        self.editor = replace(self.editor, source_kind="authored", report=None)
        save_state(self.path, (binding,), editors=(self.editor,))
        self.editor.path.unlink()
        state = load_state(self.path)
        self.assertEqual(state.editors[0].text, self.editor.text)
        self.assertEqual(state.bindings[0], binding)
        doc = json.loads(self.path.read_bytes())
        doc["editors"][0]["vm"] = "py27"
        self.path.write_text(json.dumps(doc), encoding="utf8")
        with self.assertRaises(ValueError):
            load_state(self.path)

    def test_policy_snapshot_is_rejected_on_save_before_output_written(self):
        self.editor = replace(self.editor, report=replace(self.report, index=1288))
        with self.assertRaises(ValueError):
            self.save()
        self.assertFalse(self.path.exists())
