"""Whole-package verdict: the pins are a cache, the decode is the evidence.

These tests pin the behaviour the user asked for -- "any package I build later
must open without registering it" -- and the failure mode that must not come
back: a catalog from another package being adopted because it was selected
by hand.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import complete_script_fixture, data_fixture, many_module_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.services.bundled_catalog import resolve_catalog
from script_editor.core.services.package_selfcheck import (
    MIN_ACCEPTED_RATIO,
    PackageCheck,
    verify_with_catalog,
)


class PackageSelfCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self, payload, rows, name="script.fls", catalog="params.json"):
        package = self.root / name
        package.write_bytes(payload)
        params = self.root / catalog
        params.write_text(json.dumps(rows), encoding="utf-8")
        return package, params

    def corrupt(self, package: Path, index: int) -> None:
        """Damage one entry's stored bytes without touching the directory."""
        with ArchiveDocument(package) as archive:
            span = archive.index.spans[index]
        data = bytearray(package.read_bytes())
        data[span.offset + span.length // 2] ^= 0xFF
        package.write_bytes(bytes(data))

    def test_unlisted_package_is_adopted_from_its_own_decode_evidence(self):
        package, params = self.write(*complete_script_fixture())
        with ArchiveDocument(package) as archive:
            check = verify_with_catalog(archive, params)
            check.apply(archive)
            self.assertTrue(check.accepted)
            self.assertEqual(check.passed, 3)
            self.assertEqual(check.excluded, 0)
            self.assertEqual(check.failures, ())
            self.assertEqual(archive.module_paths[0], "script/login/register.py")
            self.assertIn("3 条逐条严格解码全部成功", check.summary())

    def test_wrong_catalog_is_refused_for_the_same_package(self):
        package, rows = complete_script_fixture()
        for row in rows.values():
            row["keys"] = [(k + 1) % 256 for k in row["keys"]]
        package, params = self.write(package, rows)
        with ArchiveDocument(package) as archive:
            check = verify_with_catalog(archive, params)
        self.assertFalse(check.accepted)
        self.assertEqual(check.passed, 0)
        self.assertEqual(len(check.failures), 3)
        self.assertIn("不匹配", check.summary())

    def test_one_damaged_entry_is_named_while_the_package_stays_usable(self):
        package, rows = many_module_fixture()
        package, params = self.write(package, rows)
        self.corrupt(package, 37)
        with ArchiveDocument(package) as archive:
            check = verify_with_catalog(archive, params)
        # 119/120 = 99.2% decodes, so the parameters still fit the package and
        # the user keeps every healthy entry.
        self.assertGreaterEqual(MIN_ACCEPTED_RATIO, 0.99)
        self.assertTrue(check.accepted)
        self.assertEqual([index for index, _ in check.failures], [37])
        self.assertIn("条目 #37", check.report())

    def test_damage_beyond_the_threshold_is_refused_instead_of_half_adopted(self):
        package, rows = many_module_fixture()
        package, params = self.write(package, rows)
        for index in (3, 7, 11):
            self.corrupt(package, index)
        with ArchiveDocument(package) as archive:
            check = verify_with_catalog(archive, params)
        # 117/120 = 97.5% < 99%: too much is broken for the parameters to be
        # trusted, so nothing is attached and the entries are listed.
        self.assertFalse(check.accepted)
        self.assertEqual([index for index, _ in check.failures], [3, 7, 11])
        self.assertIn("未套用", check.report())

    def test_policy_excluded_entries_are_skipped_not_counted_as_failures(self):
        package, params = self.write(*complete_script_fixture())
        with (
            patch("script_editor.core.policy.POLICY_EXCLUDED", {("py25", 2)}),
            ArchiveDocument(package) as archive,
        ):
            check = verify_with_catalog(archive, params)
        self.assertTrue(check.accepted)
        self.assertEqual(check.passed, 2)
        self.assertEqual(check.excluded, 1)
        self.assertEqual(check.failures, ())
        self.assertIn("1 条按策略跳过", check.summary())

    def test_data_package_is_rejected_outright(self):
        package = self.root / "data.fls"
        package.write_bytes(data_fixture())
        package, params = self.write(
            package.read_bytes(), {"0": {"keys": [0] * 5, "bounds": [1] * 4}}
        )
        with ArchiveDocument(package) as archive:
            with self.assertRaises(ValueError):
                verify_with_catalog(archive, params)

    def test_acceptance_threshold_is_a_share_not_a_magic_count(self):
        def check(passed, failed):
            failures = tuple((i, "boom") for i in range(failed))
            return PackageCheck(ref=None, passed=passed, failures=failures)

        self.assertTrue(check(5000, 1).accepted)
        self.assertFalse(check(4000, 1001).accepted)
        self.assertFalse(check(0, 0).accepted)


class ResolveCatalogTests(unittest.TestCase):
    """The decision the open/project paths make, without any GUI."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        payload, rows = complete_script_fixture()
        self.package = self.root / "script.fls"
        self.package.write_bytes(payload)
        self.fingerprint = hashlib.sha256(payload).hexdigest()
        folder = self.root / "decoding"
        folder.mkdir()
        self.params = folder / "script-original.json"
        self.params.write_text(json.dumps(rows), encoding="utf-8")
        self.digest = hashlib.sha256(self.params.read_bytes()).hexdigest()

    def builtin(self):
        return patch(
            "script_editor.core.services.bundled_catalog.ORIGINAL_CATALOG",
            ("script-original.json", self.digest),
        )

    def test_pinned_package_needs_no_scan(self):
        with (
            patch(
                "script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS",
                {self.fingerprint: ("script-original.json", self.digest)},
            ),
            ArchiveDocument(self.package) as archive,
        ):
            ref, warning, check = resolve_catalog(archive, self.root)
            self.assertIsNotNone(ref)
            self.assertEqual(warning, "")
            self.assertIsNone(check)
            self.assertEqual(archive.module_paths, {})

    def test_unlisted_package_is_adopted_and_named(self):
        with (
            patch("script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS", {}),
            self.builtin(),
            ArchiveDocument(self.package) as archive,
        ):
            ref, warning, check = resolve_catalog(archive, self.root)
            self.assertIsNotNone(ref)
            self.assertEqual(warning, "")
            self.assertTrue(check.accepted)
            self.assertEqual(archive.module_paths[0], "script/login/register.py")

    def test_mismatched_builtin_catalog_is_refused_and_names_stay_unknown(self):
        params = json.loads(self.params.read_text(encoding="utf-8"))
        for row in params.values():
            row["keys"] = [(k + 1) % 256 for k in row["keys"]]
        self.params.write_text(json.dumps(params), encoding="utf-8")
        self.digest = hashlib.sha256(self.params.read_bytes()).hexdigest()
        with (
            patch("script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS", {}),
            self.builtin(),
            ArchiveDocument(self.package) as archive,
        ):
            ref, warning, check = resolve_catalog(archive, self.root)
            self.assertIsNone(ref)
            self.assertEqual(warning, "")
            self.assertFalse(check.accepted)
            self.assertEqual(archive.module_paths, {})

    def test_missing_or_tampered_asset_is_reported_not_hidden(self):
        with (
            patch("script_editor.core.services.bundled_catalog.BUNDLED_CATALOGS", {}),
            ArchiveDocument(self.package) as archive,
        ):
            ref, warning, check = resolve_catalog(archive, self.root)
        self.assertIsNone(ref)
        self.assertIn("SHA256", warning)
        self.assertIsNone(check)


class RepositoryPackageTests(unittest.TestCase):
    """The package committed in this repository must pass its own self-check."""

    def test_committed_script_package_decodes_with_builtin_catalog(self):
        root = Path(__file__).resolve().parents[1]
        package = root.parent / "data" / "script.fls"
        catalog = root / "decoding" / "script-original.json"
        if not package.is_file():
            self.skipTest("data/script.fls 不在")
        with ArchiveDocument(package) as archive:
            check = verify_with_catalog(archive, catalog)
        self.assertTrue(check.accepted, check.report())
        self.assertEqual(check.failures, ())
        self.assertIn(4007, check.paths)
        self.assertEqual(check.paths[4007], "script/login/register.py")
        self.assertEqual(
            hashlib.sha256(package.read_bytes()).hexdigest()[:12], "a45e0e49ed33"
        )


if __name__ == "__main__":
    unittest.main()
