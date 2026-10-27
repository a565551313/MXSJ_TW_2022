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
    PROBE_ENTRIES,
    PackageCheck,
    _allowed_failures,
    _probe_refuses,
    verified_with_cache,
    verify_with_catalog,
)
from script_editor.core.services.verdict_cache import VerdictCache


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


class ProbeBoundaryTests(unittest.TestCase):
    """The bounded probe may only refuse; it must never be stricter than a scan."""

    def test_probe_tolerance_tracks_the_acceptance_ratio(self):
        # Large packages: the full pass tolerates more than the 96-entry window,
        # so the probe keeps that (larger) tolerance.
        for total in (5001, 20000):
            tolerance = _allowed_failures(total)
            self.assertGreater(tolerance, PROBE_ENTRIES * 0.5)
            self.assertFalse(_probe_refuses(total, tolerance))
            self.assertTrue(_probe_refuses(total, tolerance + 1))
        # Small packages: tolerance is 0, so the sample window is the floor.
        self.assertEqual(_allowed_failures(97), 0)
        self.assertFalse(_probe_refuses(97, 48))
        self.assertTrue(_probe_refuses(97, 49))

    def test_probe_is_never_stricter_than_a_full_pass(self):
        for total in (97, 500, 5001, 20000):
            allowed = _allowed_failures(total)
            # A full pass still accepts exactly ``allowed`` failures.
            self.assertFalse(_probe_refuses(total, allowed))

    def test_clustered_damage_within_tolerance_does_not_refuse(self):
        # 96 sampled entries, 30 broken: the full pass would accept 5001-entry
        # packages with that many failures, so the probe must not end the run.
        self.assertFalse(_probe_refuses(5001, 30))
        # Wrong catalog: nearly everything in the window fails.
        self.assertTrue(_probe_refuses(5001, 90))


class VerdictExclusionTests(unittest.TestCase):
    """A cache hit must report the same exclusions a fresh scan reports."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def test_cached_verdict_keeps_the_policy_exclusion_count(self):
        payload, rows = complete_script_fixture()
        package = self.root / "script.fls"
        package.write_bytes(payload)
        params = self.root / "params.json"
        params.write_text(json.dumps(rows), encoding="utf-8")
        cache = VerdictCache(self.root / "verdicts", "test-tool")
        with patch("script_editor.core.policy.POLICY_EXCLUDED", {("py25", 2)}):
            with ArchiveDocument(package) as archive:
                fresh = verified_with_cache(
                    archive, params, cache, tool_version="test-tool", probe=False
                )
            with ArchiveDocument(package) as archive:
                cached = verified_with_cache(
                    archive, params, cache, tool_version="test-tool", probe=False
                )
        self.assertTrue(fresh.accepted)
        self.assertEqual(fresh.excluded, 1)
        self.assertTrue(cached.cached)
        self.assertEqual(cached.excluded, fresh.excluded)
        self.assertEqual(cached.passed, fresh.passed)
        self.assertEqual(cached.failures, fresh.failures)


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

    #: The original TW v2.27.2 package is the locked input; the 2026-10-23
    #: registration build (`a45e0e49…`) is a *derived* test package and is not
    #: committed here. Both decode with the same authorized catalog.
    ORIGINAL = "8b6e9266bbe9"
    DERIVED_REGISTRATION = "a45e0e49ed33"

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
            hashlib.sha256(package.read_bytes()).hexdigest()[:12], self.ORIGINAL
        )

    def test_known_catalog_pins_cover_both_original_and_registration_builds(self):
        from script_editor.core.services.bundled_catalog import BUNDLED_CATALOGS

        for digest in (
            "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72",
            "a45e0e49ed336367a1bf00b5377229c5c48de2c30ac2b61f9bf7d67549a445b9",
        ):
            with self.subTest(digest=digest[:12]):
                self.assertIn(digest, BUNDLED_CATALOGS)


if __name__ == "__main__":
    unittest.main()
