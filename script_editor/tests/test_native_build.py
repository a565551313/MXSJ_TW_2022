from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import data_fixture, minimal_pyc, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.archives.writer import write_script
from script_editor.core.compiler.runner import Compiler
from script_editor.core.services.native_build import Replacement, build_package
from script_editor.core.vm.py25.keys import load_profile


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-m2-build-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source.fls"
        self.output = self.root / "new.fls"
        self.audit = patch("script_editor.core.services.native_build.audit_standard")
        self.audit.start()
        self.addCleanup(self.audit.stop)

    def prepare(self, vm="py25"):
        self.vm = vm
        if vm == "py25":
            raw, catalog = script_fixture()
            self.source.write_bytes(raw)
            self.catalog = self.root / "catalog.json"
            self.catalog.write_text(json.dumps(catalog), encoding="utf-8")
        else:
            self.source.write_bytes(data_fixture())
        self.before = self.source.read_bytes()
        self.digest = hashlib.sha256(self.before).hexdigest()
        with ArchiveDocument(self.source) as doc:
            self.index = 0 if vm == "py25" else 1
            self.identity = doc.entries[self.index].identity
            self.profiles = {}
            if vm == "py25":
                self.profiles[0] = load_profile(
                    doc,
                    0,
                    self.catalog,
                    archive_sha256=self.digest,
                    catalog_sha256=hashlib.sha256(
                        self.catalog.read_bytes()
                    ).hexdigest(),
                )
        self.compiler = Compiler(Path(sys.executable), vm, "unit-test-only", 64, "test")

    def build(self, **overrides):
        options = dict(
            source_sha256=self.digest,
            compiler=self.compiler,
            replacements=(
                Replacement(self.index, self.identity, minimal_pyc(self.vm, 2)),
            ),
            profiles=self.profiles,
        )
        options.update(overrides)
        return build_package(self.source, self.output, **options)

    def assert_clean(self):
        self.assertFalse(list(self.root.glob(".mxscript-build-*")))
        self.assertEqual(self.source.read_bytes(), self.before)

    def test_script_preserves_unsorted_physical_order_gaps_and_tail(self):
        self.prepare()
        report = self.build()
        self.assertEqual(report.unchanged_entries, 2)
        self.assertEqual(report.modified_indexes, (0,))
        with ArchiveDocument(self.output) as doc:
            self.assertEqual(doc.read_stored(1), b"unmodified-one")
        self.assert_clean()

    def test_two_explicit_modules_are_both_verified(self):
        self.prepare()
        raw, catalog = script_fixture(two_modules=True)
        self.source.write_bytes(raw)
        self.before = raw
        self.digest = hashlib.sha256(raw).hexdigest()
        self.catalog.write_text(json.dumps(catalog), encoding="utf-8")
        with ArchiveDocument(self.source) as source:
            self.profiles = {
                i: load_profile(
                    source,
                    i,
                    self.catalog,
                    archive_sha256=self.digest,
                    catalog_sha256=hashlib.sha256(
                        self.catalog.read_bytes()
                    ).hexdigest(),
                )
                for i in (0, 1)
            }
            replacements = tuple(
                Replacement(i, source.entries[i].identity, minimal_pyc("py25", i + 2))
                for i in (0, 1)
            )
        result = self.build(replacements=replacements)
        self.assertEqual(result.modified_indexes, (0, 1))
        self.assertEqual(result.unchanged_entries, 1)
        self.assert_clean()

    def test_generated_script_can_be_reopened_and_edited_again(self):
        self.prepare()
        original, original_bytes = self.source, self.before
        first = self.build()
        self.source = self.output
        self.before = self.source.read_bytes()
        self.digest = first.output_sha256
        self.output = self.root / "second.fls"
        with ArchiveDocument(self.source) as archive:
            self.profiles = {
                0: load_profile(
                    archive,
                    0,
                    self.catalog,
                    archive_sha256=self.digest,
                    catalog_sha256=hashlib.sha256(
                        self.catalog.read_bytes()
                    ).hexdigest(),
                )
            }
        self.build(
            replacements=(Replacement(0, self.identity, minimal_pyc("py25", 3)),)
        )
        self.assertEqual(original.read_bytes(), original_bytes)
        self.assert_clean()

    def test_data_preserves_directory_padding_names_flags_local_records(self):
        self.prepare("py27")
        report = self.build()
        self.assertEqual(report.unchanged_entries, 2)
        self.assert_clean()

    def test_existing_output_source_aliases_refused(self):
        self.prepare()
        self.output.write_bytes(b"OLD OUTPUT")
        with self.assertRaises(ValueError):
            self.build()
        self.assertEqual(self.output.read_bytes(), b"OLD OUTPUT")
        self.output.unlink()
        os.link(self.source, self.output)
        with self.assertRaises(ValueError):
            self.build()
        self.assert_clean()

    def test_invalid_identity_duplicate_index_directory_wrong_vm(self):
        self.prepare()
        for replacements in [
            (),
            (Replacement(-1, self.identity, b""),),
            (Replacement(0, "bad", minimal_pyc("py25")),),
            (Replacement(0, self.identity, minimal_pyc("py25")),) * 2,
        ]:
            with self.assertRaises(ValueError):
                self.build(replacements=replacements)
        with self.assertRaises(ValueError):
            self.build(source_sha256="0" * 64)
        self.prepare("py27")
        with self.assertRaises(ValueError):
            self.build(replacements=(Replacement(0, "lib\\", minimal_pyc("py27")),))
        with self.assertRaises(ValueError):
            self.build(
                replacements=(Replacement(2, "config.txt", minimal_pyc("py27")),)
            )
        self.assert_clean()

    def test_catalog_and_archive_digest_pins(self):
        self.prepare()
        with ArchiveDocument(self.source) as doc:
            for kwargs in [
                dict(archive_sha256="0" * 64, catalog_sha256="0" * 64),
                dict(archive_sha256=self.digest, catalog_sha256="0" * 64),
            ]:
                with self.assertRaises(ValueError):
                    load_profile(doc, 0, self.catalog, **kwargs)
        with self.assertRaises(ValueError):
            self.build(profiles={})
        self.assert_clean()

    def test_xor_boundary_size_and_unrecognized_baseline_fail_closed(self):
        from dataclasses import replace

        self.prepare()
        for profile in [
            replace(self.profiles[0], keys=(1,)),
            replace(self.profiles[0], bounds=(400, 300, 200, 100)),
            replace(self.profiles[0], keys=(0, 0, 0, 0, 0)),
            replace(self.profiles[0], stored_sha256="0" * 64),
        ]:
            with self.assertRaises(ValueError):
                self.build(profiles={0: profile})
        oversized = minimal_pyc("py25", code=b"\x09" * 600)
        with self.assertRaisesRegex(ValueError, "no shrink/rescale"):
            self.build(replacements=(Replacement(0, self.identity, oversized),))
        self.assert_clean()

    def test_unchanged_entry_and_header_corruption_abort_before_publish(self):
        self.prepare()
        for position in (12, 19):

            def corrupt(source, changed, out, pos=position):
                write_script(source, changed, out)
                out.seek(pos)
                out.write(b"X")

            with patch(
                "script_editor.core.services.native_build.write_script", corrupt
            ):
                with self.assertRaises(ValueError):
                    self.build()
            self.assertFalse(self.output.exists())
            self.assert_clean()

    def test_full_pyc_mismatch_abort_before_publish(self):
        self.prepare()
        with patch(
            "script_editor.core.services.native_build.py25.decode", return_value=b"bad"
        ):
            with self.assertRaisesRegex(ValueError, "readback"):
                self.build()
        self.assertFalse(self.output.exists())
        self.assert_clean()

    def test_late_cpython_marshal_audit_failure_never_publishes(self):
        self.prepare()
        with patch(
            "script_editor.core.services.native_build.audit_standard",
            side_effect=[None, ValueError("late audit failure")],
        ):
            with self.assertRaisesRegex(ValueError, "late audit"):
                self.build()
        self.assertFalse(self.output.exists())
        self.assert_clean()

    def test_publication_failure_leaves_no_temp_or_output(self):
        self.prepare()
        with patch(
            "script_editor.core.services.native_build.os.link", side_effect=OSError
        ):
            with self.assertRaises(OSError):
                self.build()
        self.assertFalse(self.output.exists())
        self.assert_clean()

    def test_racing_output_is_never_overwritten(self):
        self.prepare()
        real_link = os.link

        def race(src, dst):
            self.output.write_bytes(b"RACER")
            return real_link(src, dst)

        with patch(
            "script_editor.core.services.native_build.os.link", side_effect=race
        ):
            with self.assertRaises(FileExistsError):
                self.build()
        self.assertEqual(self.output.read_bytes(), b"RACER")
        self.assert_clean()
