"""Loose-mode publication: overwrite the source package, never a third file.

Fixtures only — no original client package is read or written here. The point
of these tests is that "write back in place" keeps every strict guarantee and
adds exactly two things: a rolling ``.bak`` and an atomic swap.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import data_fixture, minimal_pyc, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import Compiler
from script_editor.core.services.native_build import (
    BACKUP_SUFFIX,
    Replacement,
    build_package,
    guard_in_place,
)
from script_editor.core.vm.py25.keys import load_profile


class InPlaceBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-inplace-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "script.fls"
        self.audit = patch("script_editor.core.services.native_build.audit_standard")
        self.audit.start()
        self.addCleanup(self.audit.stop)

    def prepare(self, vm="py25"):
        self.vm = vm
        if vm == "py25":
            raw, catalog = script_fixture()
            self.catalog = self.root / "catalog.json"
            self.catalog.write_text(json.dumps(catalog), encoding="utf-8")
        else:
            raw = data_fixture()
        self.source.write_bytes(raw)
        self.before = raw
        self.digest = hashlib.sha256(raw).hexdigest()
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
        self.compiler = Compiler(
            Path(sys.executable), vm, "unit-test-only", 64, "test"
        )

    def build(self, **overrides):
        options = dict(
            source_sha256=self.digest,
            compiler=self.compiler,
            replacements=(
                Replacement(self.index, self.identity, minimal_pyc(self.vm, 2)),
            ),
            profiles=self.profiles,
            in_place=True,
        )
        options.update(overrides)
        return build_package(self.source, self.source, **options)

    def test_source_is_replaced_and_matches_the_reported_digest(self):
        self.prepare()
        report = self.build()
        self.assertEqual(report.output, self.source)
        self.assertEqual(report.source_sha256, self.digest)
        self.assertNotEqual(report.output_sha256, self.digest)
        self.assertEqual(
            hashlib.sha256(self.source.read_bytes()).hexdigest(), report.output_sha256
        )
        with ArchiveDocument(self.source) as doc:
            self.assertEqual(doc.fingerprint(), report.output_sha256)
            self.assertNotEqual(doc.read_stored(self.index), b"")

    def test_rolling_backup_holds_the_previous_bytes(self):
        self.prepare()
        self.build()
        backup = self.source.with_name(self.source.name + BACKUP_SUFFIX)
        self.assertTrue(backup.is_file())
        self.assertEqual(backup.read_bytes(), self.before)

        # A second save replaces the same rolling backup instead of adding one.
        first = self.source.read_bytes()
        self.digest = hashlib.sha256(first).hexdigest()
        with ArchiveDocument(self.source) as doc:
            identity = doc.entries[self.index].identity
            profiles = dict(self.profiles)
            if self.vm == "py25":
                # The XOR profile is bound to the archive digest, which the
                # first save just changed; it must be re-derived, exactly as the
                # GUI does after reopening a written package.
                profiles[self.index] = load_profile(
                    doc,
                    self.index,
                    self.catalog,
                    archive_sha256=self.digest,
                    catalog_sha256=hashlib.sha256(
                        self.catalog.read_bytes()
                    ).hexdigest(),
                )
        self.build(
            source_sha256=self.digest,
            replacements=(Replacement(self.index, identity, minimal_pyc(self.vm, 3)),),
            profiles=profiles,
        )
        self.assertEqual(backup.read_bytes(), first)
        self.assertEqual(
            sorted(p.name for p in self.root.iterdir() if p.suffix in {".fls", ".bak"}),
            ["script.fls", "script.fls" + BACKUP_SUFFIX],
        )

    def test_backup_can_be_turned_off(self):
        self.prepare()
        self.build(backup=False)
        self.assertFalse(
            self.source.with_name(self.source.name + BACKUP_SUFFIX).exists()
        )

    def test_stale_source_digest_is_refused_and_nothing_is_written(self):
        self.prepare()
        stale = "0" * 64
        with self.assertRaises(ValueError) as caught:
            self.build(source_sha256=stale)
        self.assertIn("digest/VM mismatch", str(caught.exception))
        self.assertEqual(self.source.read_bytes(), self.before)
        self.assertFalse(
            self.source.with_name(self.source.name + BACKUP_SUFFIX).exists()
        )

    def test_backup_that_captured_other_bytes_aborts_the_swap(self):
        """A writer between the hash check and the copy must not lose data."""
        self.prepare()
        real_copy = shutil.copy2

        def racing_copy(src, dst, **options):
            # Another process rewrote the package after we hashed it.
            Path(src).write_bytes(self.before + b"drift")
            return real_copy(src, dst, **options)

        with (
            patch(
                "script_editor.core.services.native_build.shutil.copy2",
                side_effect=racing_copy,
            ),
            self.assertRaises(ValueError) as caught,
        ):
            self.build()
        self.assertIn("备份期间被改动", str(caught.exception))
        self.assertEqual(self.source.read_bytes(), self.before + b"drift")
        self.assertFalse(
            self.source.with_name(self.source.name + BACKUP_SUFFIX).exists()
        )
        self.assertFalse(list(self.root.glob(".mxscript-bak-*")))

    def test_destination_must_be_the_same_package(self):
        self.prepare()
        other = self.root / "other.fls"
        other.write_bytes(self.before)
        with self.assertRaises(ValueError) as caught:
            build_package(
                self.source,
                other,
                source_sha256=self.digest,
                compiler=self.compiler,
                replacements=(
                    Replacement(self.index, self.identity, minimal_pyc(self.vm, 2)),
                ),
                profiles=self.profiles,
                in_place=True,
            )
        self.assertIn("只能指向本次构建的原包本身", str(caught.exception))
        self.assertEqual(other.read_bytes(), self.before)
        self.assertEqual(self.source.read_bytes(), self.before)

    def test_third_party_protected_file_is_not_overwritten(self):
        self.prepare()
        catalog = getattr(self, "catalog", None)
        if catalog is None:
            self.skipTest("py27 fixture has no catalog")
        with self.assertRaises(ValueError) as caught:
            build_package(
                self.source,
                catalog,
                source_sha256=self.digest,
                compiler=self.compiler,
                replacements=(
                    Replacement(self.index, self.identity, minimal_pyc(self.vm, 2)),
                ),
                profiles=self.profiles,
                protected=(catalog,),
                in_place=True,
            )
        self.assertIn(".fls", str(caught.exception))

    def test_guard_allows_only_the_exact_source_path(self):
        self.prepare()
        self.assertEqual(
            guard_in_place(self.source, self.source, (self.source,)), self.source
        )
        # The source appearing among the protected inputs is the whole point of
        # loose mode; any *other* protected path still fails closed.
        other = self.root / "catalog.json"
        other.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            guard_in_place(other, self.source, (self.source, other))
        self.assertIn(".fls", str(caught.exception))

    def test_temp_files_are_cleaned_up_after_a_successful_swap(self):
        self.prepare()
        self.build()
        self.assertFalse(list(self.root.glob(".mxscript-build-*")))
        self.assertFalse(list(self.root.glob(".mxscript-bak-*")))

    def test_loose_mode_refuses_the_policy_excluded_entry(self):
        self.prepare()
        if self.vm != "py25":
            self.skipTest("only the script package excludes an entry")
        with self.assertRaises(ValueError):
            self.build(
                replacements=(
                    Replacement(1288, "00000000", minimal_pyc(self.vm, 2)),
                )
            )

    def test_data_package_can_be_rewritten_in_place(self):
        self.prepare("py27")
        report = self.build()
        self.assertEqual(
            hashlib.sha256(self.source.read_bytes()).hexdigest(), report.output_sha256
        )
        with ArchiveDocument(self.source) as doc:
            self.assertEqual(doc.vm, "py27")


if __name__ == "__main__":
    unittest.main()
