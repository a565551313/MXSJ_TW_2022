from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from threading import Event
from unittest.mock import patch

from native_fixtures import data_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.project.storage import load_state, save_state
from script_editor.core.project.workspace import EditorState
from script_editor.core.services.corpus_manifest import load_corpus
from script_editor.core.services.corpus_recovery import (
    corpus_report,
    verified_parameters,
)
from script_editor.core.services.data_corpus import build_data_corpus
from script_editor.core.services.recovery_candidates import (
    DRAFT_HEADER,
    RecoveryCandidate,
)
from script_editor.core.services.recovery_process import RecoveryCancelled


def candidates():
    source = DRAFT_HEADER + "# MXSJ-RECOVERY-VM: py27\nx=1\n"
    return (
        RecoveryCandidate(
            "uncompyle6",
            "test",
            "complete",
            source,
            stdout=b"x=1\n",
            raw_kind="compat-not-pristine",
            trace_stdout=b"trace",
        ),
        RecoveryCandidate(
            "pycdc",
            "test",
            "partial",
            source,
            stdout=b"x='\xff'\n",
            stderr=b"diagnostic",
            raw_kind="engine-bytes",
        ),
    )


class DataCorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.package = self.root / "data.fls"
        self.original = data_fixture()
        self.package.write_bytes(self.original)
        self.archive = ArchiveDocument(self.package)
        self.output = self.root / "cache"

    def tearDown(self):
        self.archive.close()
        self.temp.cleanup()

    def build(self, **kwargs):
        with patch(
            "script_editor.core.services.data_corpus.recover_standard",
            return_value={"candidates": candidates()},
        ) as recover:
            ret = build_data_corpus(self.archive, self.output, **kwargs)
            self.assertEqual(recover.call_count, 1)
            self.assertEqual(recover.call_args.args[1], "py27")
            return ret

    def rewrite(self, edit):
        path = self.output / "full/manifest.audited.jsonl"
        rows = [json.loads(r) for r in path.read_bytes().splitlines()]
        edit(rows)
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf8")
        return path

    def test_full_build_directory_exclusion_strict_pyc_and_exact_raw_roundtrip(self):
        index, summary = self.build()
        self.assertEqual(summary["entries"], 3)
        self.assertEqual(summary["counts"]["directory"], 1)
        self.assertEqual(summary["counts"]["strict_decoded"], 1)
        self.assertEqual(
            summary["counts"]["failed"], 1
        )  # opaque resource, not fake code
        self.assertFalse((self.output / "INCOMPLETE.txt").exists())
        report = corpus_report(index, self.archive, 1)
        self.assertTrue(report.origin_verified)
        self.assertIn("MXSJ-RECOVERY-VM: py27", report.source)
        self.assertNotIn("MXSJ-RECOVERY-VM: py25", report.source)
        self.assertEqual(report.source.count("MXSJ-RECOVERED-DRAFT"), 1)
        self.assertEqual(report.candidates[0].raw_kind, "compat-not-pristine")
        self.assertEqual(report.candidates[0].trace_stdout, b"trace")
        self.assertEqual(report.candidates[1].stdout, b"x='\xff'\n")
        self.assertFalse(report.candidates[1].complete)
        self.assertEqual(self.package.read_bytes(), self.original)
        self.assertFalse((self.output / "full/entries/0000").exists())
        with self.assertRaisesRegex(ValueError, "目录不是脚本"):
            corpus_report(index, self.archive, 0)

    def test_vm_path_identity_and_directory_confusion_are_rejected(self):
        self.build()
        original = (self.output / "full/manifest.audited.jsonl").read_bytes()
        edits = [
            lambda r: r[1].update(archive_vm="py25"),
            lambda r: r[1].update(entry_identity="other.pyo"),
            lambda r: r[0].update(status="complete"),
            lambda r: r[1].update(directory=True),
            lambda r: r[1].update(status="excluded_by_policy"),
            lambda r: r[0].update(engines=r[1]["engines"]),
        ]
        for edit in edits:
            (self.output / "full/manifest.audited.jsonl").write_bytes(original)
            path = self.rewrite(edit)
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                load_corpus(self.archive, path)

    def test_wrong_magic_cannot_be_labeled_data_standard_pyc(self):
        self.build()
        raw = bytearray((self.output / "full/entries/0001/standard.pyc").read_bytes())
        raw[:4] = bytes.fromhex("b3f20d0a")
        (self.output / "full/entries/0001/standard.pyc").write_bytes(raw)

        def change(rows):
            rows[1]["artifacts"][0]["sha256"] = hashlib.sha256(raw).hexdigest()

        index = load_corpus(self.archive, self.rewrite(change))
        with self.assertRaisesRegex(ValueError, "pyc头不符"):
            corpus_report(index, self.archive, 1)

    def test_nonzero_timestamp_is_preserved_and_accepted_for_vm27(self):
        index, _ = self.build()
        path = self.output / "full/entries/0001/standard.pyc"
        raw = bytearray(path.read_bytes())
        raw[4:8] = b"ABCD"
        path.write_bytes(raw)

        def change(rows):
            rows[1]["artifacts"][0]["sha256"] = hashlib.sha256(raw).hexdigest()

        index = load_corpus(self.archive, self.rewrite(change))
        report = corpus_report(index, self.archive, 1)
        self.assertTrue(report.source)
        self.assertFalse(
            report.origin_verified
        )  # Header difference is still a difference.

    def test_data_does_not_accept_script_xor_catalog_workflow(self):
        index, _ = self.build()
        with self.assertRaisesRegex(ValueError, "独立VM2.7"):
            verified_parameters(index, self.archive, object())

    def test_existing_destination_never_overwritten(self):
        self.build()
        before = (self.output / "full/manifest.audited.jsonl").read_bytes()
        with self.assertRaises(FileExistsError):
            self.build()
        self.assertEqual(
            (self.output / "full/manifest.audited.jsonl").read_bytes(), before
        )

    def test_pre_cancel_reads_no_payload_and_creates_no_cache(self):
        cancel = Event()
        cancel.set()
        with patch.object(
            self.archive, "read_stored", side_effect=AssertionError("payload")
        ):
            with self.assertRaises(RecoveryCancelled):
                self.build(cancel=cancel)
        self.assertFalse(self.output.exists())

    def test_mid_cancel_has_no_usable_manifest_or_source_changes(self):
        cancel = Event()

        def recover(*args, **kwargs):
            cancel.set()
            return {"candidates": candidates()}

        with patch(
            "script_editor.core.services.data_corpus.recover_standard",
            side_effect=recover,
        ):
            with self.assertRaises(RecoveryCancelled):
                build_data_corpus(self.archive, self.output, cancel=cancel)
        self.assertTrue((self.output / "INCOMPLETE.txt").exists())
        self.assertFalse((self.output / "full/manifest.audited.jsonl").exists())
        self.assertEqual(self.package.read_bytes(), self.original)

    def test_schema3_vm27_corpus_and_dirty_buffer_resume_without_corpus(self):
        index, _ = self.build()
        report = corpus_report(index, self.archive, 1)
        editor = EditorState(
            self.root / "dirty.py",
            "py27",
            "recovered-draft",
            "# keep\n",
            True,
            False,
            report,
        )
        project = self.root / "work.mxscript.json"
        save_state(project, (), editors=(editor,), corpora=(index.ref,))
        index.ref.path.unlink()
        state = load_state(project)
        self.assertEqual(state.editors, (editor,))
        self.assertEqual(state.corpora, (index.ref,))
        self.assertFalse(state.bindings)

    def test_failed_engines_keep_diagnostics_not_fake_source(self):
        failed = tuple(replace(c, source="", status="failed") for c in candidates())
        with patch(
            "script_editor.core.services.data_corpus.recover_standard",
            return_value={"candidates": failed},
        ):
            index, summary = build_data_corpus(self.archive, self.output)
        report = corpus_report(index, self.archive, 1)
        self.assertFalse(report.source)
        self.assertEqual(report.candidates[1].stderr, b"diagnostic")
        self.assertEqual(summary["counts"].get("editable_candidates", 0), 0)

    def test_top_level_recovery_failure_remains_visible_after_cache_import(self):
        with patch(
            "script_editor.core.services.data_corpus.recover_standard",
            side_effect=ValueError("missing engine"),
        ):
            index, _ = build_data_corpus(self.archive, self.output)
        report = corpus_report(index, self.archive, 1)
        self.assertFalse(report.source)
        self.assertIn("missing engine", report.diagnostics)


class SignedLegacyLongTests(unittest.TestCase):
    def test_signed_long_values_zero_positive_negative_and_large_are_exact(self):
        import struct

        import xdis.unmarshal

        from script_editor.data.recovery_worker import install_legacy_long_reader

        original = xdis.unmarshal.VersionIndependentUnmarshaller
        with patch.object(xdis.unmarshal, "VersionIndependentUnmarshaller", original):
            install_legacy_long_reader()
            for magic in (62131, 62211):
                for value in (
                    0,
                    1,
                    -1,
                    32768,
                    -32768,
                    2**127 + 65537,
                    -(2**127 + 65537),
                ):
                    digits = []
                    number = abs(value)
                    while number:
                        digits.append(number & 32767)
                        number >>= 15
                    raw = b"l" + struct.pack(
                        "<i", len(digits) * (-1 if value < 0 else 1)
                    )
                    raw += b"".join(struct.pack("<H", v) for v in digits)
                    actual = xdis.unmarshal.load_code(raw, magic, code_objects={})
                    with self.subTest(magic=magic, value=value):
                        self.assertEqual(actual, value)

    def test_signed_long_invalid_digit_and_absurd_count_are_rejected(self):
        import struct

        import xdis.unmarshal

        from script_editor.data.recovery_worker import install_legacy_long_reader

        original = xdis.unmarshal.VersionIndependentUnmarshaller
        with patch.object(xdis.unmarshal, "VersionIndependentUnmarshaller", original):
            install_legacy_long_reader()
            for raw in (
                b"l" + struct.pack("<iH", 1, 32768),
                b"l" + struct.pack("<i", -2147483648),
            ):
                with self.assertRaises(ValueError):
                    xdis.unmarshal.load_code(raw, 62211, code_objects={})


@unittest.skipUnless(
    os.environ.get("MXSJ_DATA_CORPUS"), "opt-in actual data corpus required"
)
class RealDataCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive = ArchiveDocument(
            Path(os.environ["MXSJ_M2_REPO"]) / "data/data.fls"
        )
        cls.index = load_corpus(
            cls.archive,
            Path(os.environ["MXSJ_DATA_CORPUS"]) / "full/manifest.audited.jsonl",
        )

    @classmethod
    def tearDownClass(cls):
        cls.archive.close()

    def test_every_real_data_entry_candidate_has_exact_strict_origin(self):
        directories = 0
        editable = 0
        for entry in self.archive.entries:
            if entry.directory:
                directories += 1
                continue
            report = corpus_report(self.index, self.archive, entry.index)
            with self.subTest(entry=entry.index):
                self.assertTrue(report.origin_verified)
                self.assertEqual(report.vm, "py27")
                self.assertEqual(report.candidate_pyc_sha256, report.standard_sha256)
                self.assertTrue(report.source)
                self.assertIn("MXSJ-RECOVERY-VM: py27", report.source)
                self.assertEqual(len(report.candidates), 2)
                self.assertFalse(
                    any(c.metadata()["semantics_verified"] for c in report.candidates)
                )
            editable += bool(report.source)
        self.assertEqual((directories, editable), (12, 121))

    def test_real_data_corpus_probe_compile_publish_reopen_does_not_execute(self):
        executable = os.environ.get("MXSJ_PY27")
        if not executable:
            self.skipTest("actual CPython2.7.13 required")
        from script_editor.core.compiler.runner import inspect_compiler
        from script_editor.core.inspection.native import inspect_module
        from script_editor.core.project.document import Binding
        from script_editor.core.project.storage import ProjectState
        from script_editor.core.services.workflow import (
            Snapshot,
            prepare_build,
            publish_build,
        )

        report = corpus_report(self.index, self.archive, 75)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sentinel = root / "MUST_NOT_EXECUTE"
            text = f"probe=2\nopen({str(sentinel)!r},'w').write('NO')\n"
            source = root / "edit.py"
            source.write_text(text, encoding="utf8")
            binding = replace(
                Binding.associate(self.archive, 75, source),
                filename_hex=report.filename_hex,
                source_kind="recovered-reviewed",
                recovery_sha256=report.standard_sha256,
            )
            compiler = inspect_compiler(Path(executable), "py27")
            plan = prepare_build(Snapshot(binding, text, "py27"), compiler)
            result, state = publish_build(
                plan, root / "new.fls", ProjectState((binding,))
            )
            self.assertEqual(result.unchanged_entries, 132)
            self.assertFalse(sentinel.exists())
            with ArchiveDocument(result.output) as archive:
                actual, filename, _ = inspect_module(archive, 75)
                self.assertEqual(actual, plan.replacement.standard_pyc)
                self.assertEqual(filename.hex(), report.filename_hex)
            self.assertEqual(state.bindings[0].vm, "py27")

    def test_real_uuid_negative_longs_remain_exact_not_replaced_or_nopped(self):
        report = corpus_report(self.index, self.archive, 82)
        self.assertTrue(report.origin_verified)
        self.assertTrue(report.complete)
        self.assertIn("-13835058055282163713", report.source)
        self.assertIn("-1133367955888714851287041", report.source)
        self.assertEqual(report.selected_engine, "uncompyle6")

    def test_real_uuid_direct_browser_opens_without_prebuilt_corpus(self):
        from script_editor.core.services.module_browser import read_module

        report = read_module(self.archive, 82, timeout=10)
        self.assertTrue(report.complete, report.diagnostics)
        self.assertEqual(report.vm, "py27")
        self.assertFalse(report.corpus_manifest_sha256)
        self.assertIn("-13835058055282163713", report.source)


@unittest.skipUnless(
    os.environ.get("MXSJ_PY25") and os.environ.get("MXSJ_PY27"),
    "actual standard compilers required",
)
class ActualSignedLongRecoveryTests(unittest.TestCase):
    def test_both_real_vms_negative_long_recovery_recompiles_exact_constants(self):
        from script_editor.core.compiler.runner import (
            compile_standard,
            inspect_compiler,
        )
        from script_editor.core.services.module_browser import recover_standard
        from script_editor.core.vm.marshal_tree import parse

        for vm, env in (("py25", "MXSJ_PY25"), ("py27", "MXSJ_PY27")):
            with self.subTest(vm=vm), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                standard = root / "original.pyc"
                rebuilt = root / "recompiled.pyc"
                compiler = inspect_compiler(Path(os.environ[env]), vm)
                text = (
                    "negative=-13835058055282163713L\n"
                    "positive=170141183460469231731687303715884171265L\n"
                )
                compile_standard(compiler, text, b"long-constants.py", standard)
                report = recover_standard(standard.read_bytes(), vm)
                self.assertTrue(report["complete"], report["diagnostics"])
                compile_standard(
                    compiler, report["source"], b"long-constants.py", rebuilt
                )

                def longs(path):
                    return sorted(
                        n.raw
                        for n in parse(path.read_bytes()[8:]).fields[0].items
                        if n.tag == b"l"
                    )

                self.assertEqual(longs(standard), longs(rebuilt))
                self.assertEqual(len(longs(rebuilt)), 2)
