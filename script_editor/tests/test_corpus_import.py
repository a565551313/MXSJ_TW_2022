from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from corpus_fixtures import fixture, write_manifest

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.services.bundled_catalog import bundled_catalog
from script_editor.core.services.corpus_manifest import artifact_path, load_corpus
from script_editor.core.services.corpus_recovery import (
    corpus_report,
    verified_parameters,
)
from script_editor.core.services.recovery_process import RecoveryCancelled


class CorpusImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.archive, self.catalog, self.path, self.rows = fixture(self.root)

    def tearDown(self):
        self.archive.close()
        self.temp.cleanup()

    def load(self):
        write_manifest(self.path, self.rows)
        return load_corpus(self.archive, self.path)

    def test_index_and_raw_bytes_are_separate_from_editable_source(self):
        index = self.load()
        report = corpus_report(index, self.archive, 0, self.catalog)
        self.assertTrue(report.origin_verified)
        self.assertEqual(len(report.candidates), 2)
        second = report.candidates[1]
        self.assertIn(b"\xff", second.stdout)
        self.assertIn("\\xff", second.source)
        self.assertFalse(second.complete)
        self.assertEqual(second.stderr, b"line1\nline2\n")
        self.assertIn("MXSJ-RECOVERED-DRAFT", report.source)
        self.assertFalse(second.metadata()["syntax_checked"])
        self.assertEqual(report.corpus_manifest_sha256, index.ref.sha256)

    def test_whole_manifest_change_detected_not_only_current_row(self):
        index = self.load()
        self.rows[2]["status"] = "partial"
        write_manifest(self.path, self.rows)
        with self.assertRaisesRegex(ValueError, "变化"):
            index.row(self.archive, 0)

    def test_reordered_duplicate_missing_and_wrong_archive_records_rejected(self):
        for change in ("reorder", "duplicate", "missing", "fingerprint", "identity"):
            original = json.loads(json.dumps(self.rows))
            with self.subTest(change=change):
                if change == "reorder":
                    self.rows.reverse()
                if change == "duplicate":
                    self.rows[1]["entry_index"] = 0
                if change == "missing":
                    self.rows.pop()
                if change == "fingerprint":
                    self.rows[0]["archive_sha256"] = "a" * 64
                if change == "identity":
                    self.rows[0]["transpile"]["entry_id"] = 999
                with self.assertRaises(ValueError):
                    self.load()
            self.rows = original

    def test_bool_schema_and_malformed_engine_rejected(self):
        self.rows[0]["schema_version"] = True
        with self.assertRaises(ValueError):
            self.load()
        self.rows[0]["schema_version"] = 1
        self.rows[0]["engines"] = []
        with self.assertRaises(ValueError):
            self.load()

    def test_line_and_total_limit_are_fail_closed(self):
        with patch("script_editor.core.services.corpus_manifest.MAX_ROW", 32):
            with self.assertRaises(ValueError):
                self.load()
        with patch("script_editor.core.services.corpus_manifest.MAX_MANIFEST", 32):
            with self.assertRaises(ValueError):
                self.load()

    def test_cancellation_before_import_never_reads_artifacts(self):
        cancel = threading.Event()
        cancel.set()
        with self.assertRaises(RecoveryCancelled):
            load_corpus(self.archive, self.path, cancel=cancel)

    def test_bad_artifact_hash_length_or_cross_entry_rejected(self):
        original = json.loads(json.dumps(self.rows))
        for change in ("hash", "length", "entry"):
            with self.subTest(change=change):
                ref = self.rows[0]["engines"]["pycdc"]["stdout"]
                if change == "hash":
                    ref["sha256"] = "0" * 64
                if change == "length":
                    ref["bytes"] += 1
                if change == "entry":
                    ref["path"] = ref["path"].replace("/0000/", "/0001/")
                with self.assertRaises(ValueError):
                    corpus_report(self.load(), self.archive, 0, self.catalog)
            self.rows = json.loads(json.dumps(original))

    def test_path_traversal_absolute_windows_alias_and_symlink_rejected(self):
        for name in (
            "../secret",
            "/etc/passwd",  # win-ok: deliberate hostile path; never opened
            "C:/secret",
            "full\\secret",
            "full/../secret",
            "full/a./x",
            "full//x",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                artifact_path(self.path.parent.parent, name)
        target = self.path.parent.parent / "link"
        try:
            target.symlink_to(self.root, target_is_directory=True)
        except OSError:
            return  # Windows may forbid creating test symlinks without Developer Mode.
        with self.assertRaises(ValueError):
            artifact_path(self.path.parent.parent, "link/keys.json")

    def test_all_comment_failure_output_is_not_source(self):
        for value in self.rows[0]["engines"].values():
            value["has_source_body"] = False
            value["status"] = "failed"
            value["candidates"][0]["candidate_kind"] = "diagnostic_only"
        report = corpus_report(self.load(), self.archive, 0, self.catalog)
        self.assertFalse(report.source)
        self.assertTrue(all(not c.source for c in report.candidates))

    def test_different_pyc_is_readable_but_not_verified_origin(self):
        self.archive.close()
        import shutil

        shutil.rmtree(self.root)
        self.root.mkdir()
        self.archive, self.catalog, self.path, self.rows = fixture(
            self.root, mismatched=True
        )
        report = corpus_report(self.load(), self.archive, 0, self.catalog)
        self.assertTrue(report.source)
        self.assertFalse(report.origin_verified)
        self.assertNotEqual(report.standard_sha256, report.candidate_pyc_sha256)

    def test_repair_parameters_require_exact_strict_byte_equality(self):
        self.archive.close()
        import shutil

        shutil.rmtree(self.root)
        self.root.mkdir()
        self.archive, self.catalog, self.path, self.rows = fixture(
            self.root, repair=True
        )
        before = self.catalog.path.read_bytes()
        raw, accepted, rejected = verified_parameters(
            self.load(), self.archive, self.catalog
        )
        self.assertEqual(accepted, (0,))
        self.assertFalse(rejected)
        self.assertEqual(self.catalog.path.read_bytes(), before)
        self.assertNotEqual(
            json.loads(raw)["0"]["bounds"], json.loads(before)["0"]["bounds"]
        )
        self.rows[0]["transpile"]["keys"][0] ^= 1
        _, accepted, rejected = verified_parameters(
            self.load(), self.archive, self.catalog
        )
        self.assertFalse(accepted)
        self.assertIn(0, rejected)

    def test_wrong_original_parameters_or_artifact_never_admitted(self):
        self.rows[0]["transpile"]["stage"] = "resolved"
        self.rows[0]["transpile"]["original_parameters"]["keys"] = [5] * 5
        _, accepted, rejected = verified_parameters(
            self.load(), self.archive, self.catalog
        )
        self.assertFalse(accepted)
        self.assertIn(0, rejected)

    def test_exclusion_happens_before_any_artifact_read(self):
        index = self.load()
        fake = replace(self.archive.entries[0], index=1288)
        from types import SimpleNamespace

        archive = SimpleNamespace(
            vm="py25",
            path=self.archive.path,
            fingerprint=self.archive.fingerprint,
            _assert_unchanged=self.archive._assert_unchanged,
            entries={1288: fake},
        )
        with patch.object(
            type(index), "row", side_effect=AssertionError("must not read row")
        ):
            report = corpus_report(index, archive, 1288, self.catalog)
        self.assertFalse(report.source)
        self.assertFalse(report.standard_sha256)

    def test_malformed_engine_record_is_value_error_for_safe_native_fallback(self):
        self.rows[0]["engines"]["uncompyle6"] = []
        index = self.load()
        with self.assertRaisesRegex(ValueError, "语料引擎记录结构非法"):
            corpus_report(index, self.archive, 0, self.catalog)

    def test_original_parameter_numeric_alias_is_not_exact_integer_match(self):
        row = self.rows[0]["transpile"]
        row["stage"] = "seam_refine"
        row["original_parameters"]["keys"][0] = float(
            row["original_parameters"]["keys"][0]
        )
        index = self.load()
        _, accepted, rejected = verified_parameters(index, self.archive, self.catalog)
        self.assertFalse(accepted)
        self.assertIn("原参数", rejected[0])


@unittest.skipUnless(
    os.environ.get("MXSJ_CORPUS_REVIEW"), "opt-in full audited corpus required"
)
class RealCorpusImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = ArchiveDocument(
            Path(os.environ["MXSJ_M2_REPO"]) / "data/script.fls"
        )
        cls.index = load_corpus(
            cls.archive,
            Path(os.environ["MXSJ_CORPUS_REVIEW"]) / "full/manifest.audited.jsonl",
        )
        cls.catalog = bundled_catalog(
            cls.archive, Path(os.environ["MXSJ_M2_REPO"]) / "script_editor"
        )

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()

    def test_eight_real_repairs_match_exact_pyc_and_original_catalog_unchanged(self):
        before = self.catalog.path.read_bytes()
        raw, accepted, rejected = verified_parameters(
            self.index, self.archive, self.catalog
        )
        self.assertEqual(accepted, (63, 1013, 1528, 1854, 1931, 2643, 2984, 4305))
        self.assertEqual(len(rejected), 7)
        self.assertEqual(self.catalog.path.read_bytes(), before)
        self.assertEqual(len(json.loads(raw)), 5002)

    def test_124_and_4861_keep_editable_candidates_without_verified_origin(self):
        for entry in (124, 4861):
            report = corpus_report(self.index, self.archive, entry, self.catalog)
            self.assertTrue(report.source)
            self.assertFalse(report.origin_verified)
            self.assertIn("pycdc", [c.engine for c in report.candidates])

    def test_2371_local_repair_delta_not_misrepresented_as_verified(self):
        report = corpus_report(self.index, self.archive, 2371, self.catalog)
        self.assertTrue(report.source)
        self.assertFalse(report.origin_verified)
        self.assertNotEqual(report.standard_sha256, report.candidate_pyc_sha256)

    def test_real_repaired_4305_compile_publish_reopen_without_execution(self):
        executable = os.environ.get("MXSJ_PY25")
        if not executable:
            self.skipTest("actual standard 2.5.6 required")
        from script_editor.core.compiler.runner import inspect_compiler
        from script_editor.core.inspection.native import inspect_module
        from script_editor.core.project.document import Binding
        from script_editor.core.project.storage import CatalogRef, ProjectState
        from script_editor.core.services.workflow import (
            Snapshot,
            prepare_build,
            publish_build,
        )

        raw, accepted, _ = verified_parameters(self.index, self.archive, self.catalog)
        self.assertIn(4305, accepted)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            params = root / "verified.json"
            params.write_bytes(raw)
            ref = CatalogRef(
                self.archive.path,
                self.archive.fingerprint(),
                params,
                hashlib.sha256(raw).hexdigest(),
            )
            original, filename, _ = inspect_module(self.archive, 4305, ref)
            sentinel = root / "MUST_NOT_EXECUTE"
            text = f"probe=2\nopen({str(sentinel)!r},'w').write('NO')\n"
            source = root / "edited.py"
            source.write_text(text, encoding="utf8")
            binding = replace(
                Binding.associate(self.archive, 4305, source),
                filename_hex=filename.hex(),
                source_kind="recovered-reviewed",
                recovery_sha256=hashlib.sha256(original).hexdigest(),
            )
            compiler = inspect_compiler(Path(executable), "py25")
            plan = prepare_build(Snapshot(binding, text, "py25"), compiler, ref)
            result, state = publish_build(
                plan, root / "new.fls", ProjectState((binding,), (ref,))
            )
            self.assertEqual(result.unchanged_entries, 5001)
            self.assertFalse(sentinel.exists())
            with ArchiveDocument(result.output) as archive:
                actual, actual_filename, _ = inspect_module(
                    archive, 4305, state.catalogs[0]
                )
                self.assertEqual(actual, plan.replacement.standard_pyc)
                self.assertEqual(actual_filename, filename)
            self.assertEqual(self.archive.fingerprint(), self.index.ref.fingerprint)

    def test_real_large_entry_1182_is_not_blocked_by_live_process_output_limit(self):
        report = corpus_report(self.index, self.archive, 1182, self.catalog)
        self.assertTrue(report.source)
        self.assertGreater(
            max(len(c.stdout) for c in report.candidates), 4 * 1024 * 1024
        )
        self.assertTrue(
            all(c.raw_kind == "corpus-engine-bytes" for c in report.candidates)
        )
