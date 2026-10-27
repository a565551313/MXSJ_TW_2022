"""Performance and memoization guarantees, stated as observable behaviour.

Every case here protects a *correctness* property that the speed-up relies on:
the catalog file is still hashed, a stale or foreign verdict is never adopted,
a probe may only refuse, a truncated product is declared instead of silently
dropped, and an engine result must still match the bounded protocol.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from native_fixtures import complete_script_fixture, many_module_fixture, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.services import module_paths, package_selfcheck
from script_editor.core.services.module_browser import (
    MAX_DISASSEMBLY_CHARS,
    MAX_SOURCE_CHARS,
    RecoverySessionCache,
    validate_result,
)
from script_editor.core.services.package_selfcheck import (
    PROBE_ENTRIES,
    verified_with_cache,
    verify_with_catalog,
)
from script_editor.core.services.verdict_cache import (
    PackageVerdict,
    VerdictCache,
    default_cache_root,
    policy_fingerprint,
)
from script_editor.core.vm.py25 import cipher
from script_editor.core.vm.py25 import keys as py25keys


def _write(root: Path, name: str, payload: bytes, rows: dict) -> tuple[Path, Path]:
    package = root / name
    catalog = root / f"{name}.catalog.json"
    package.write_bytes(payload)
    catalog.write_text(json.dumps(rows), encoding="utf-8")
    return package, catalog


class CatalogSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        py25keys.clear_catalog_cache()
        self.addCleanup(py25keys.clear_catalog_cache)

    def test_one_read_serves_many_lookups_and_digest_matches_file(self):
        path = self.root / "catalog.json"
        path.write_text('{"0": {"keys": [1, 2, 3, 4, 5]}}', encoding="utf-8")
        with patch.object(
            py25keys, "read_catalog", wraps=py25keys.read_catalog
        ) as reads:
            rows, digest = py25keys.catalog_snapshot(path)
            for _ in range(20):
                again, again_digest = py25keys.catalog_snapshot(path)
        self.assertEqual(reads.call_count, 1)
        self.assertIs(rows, again)
        self.assertEqual(digest, again_digest)
        self.assertEqual(digest, hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(rows["0"]["keys"], [1, 2, 3, 4, 5])

    def test_changed_file_is_re_read_and_redigested(self):
        path = self.root / "catalog.json"
        path.write_text('{"0": {"keys": [1, 2, 3, 4, 5]}}', encoding="utf-8")
        _, first = py25keys.catalog_snapshot(path)
        path.write_text('{"0": {"keys": [5, 4, 3, 2, 1]}, "pad": 1}', encoding="utf-8")
        rows, second = py25keys.catalog_snapshot(path)
        self.assertNotEqual(first, second)
        self.assertEqual(rows["0"]["keys"], [5, 4, 3, 2, 1])

    def test_clear_cache_forces_a_fresh_read(self):
        path = self.root / "catalog.json"
        path.write_text("{}", encoding="utf-8")
        py25keys.catalog_snapshot(path)
        with patch.object(
            py25keys, "read_catalog", wraps=py25keys.read_catalog
        ) as reads:
            py25keys.clear_catalog_cache()
            py25keys.catalog_snapshot(path)
        self.assertEqual(reads.call_count, 1)

    def test_non_object_catalog_is_refused(self):
        path = self.root / "catalog.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        with self.assertRaises(ValueError):
            py25keys.catalog_snapshot(path)


class SeedTableTests(unittest.TestCase):
    def test_table_matches_the_recurrence_for_every_seed(self):
        table = cipher._seed_by_sequence()
        # Two 15-bit seeds really do collide on the five-key sequence, which is
        # why an ambiguous catalog row must stay refused instead of picking the
        # first candidate. The table keeps that distinction (value None).
        self.assertLessEqual(len(table), 32768)
        self.assertIn(None, table.values())
        for seed in (0, 1, 255, 256, 19084, 32767):
            keys = cipher.sequence(seed)
            self.assertEqual(table[keys], seed)
            self.assertEqual(cipher.seed_from_keys(keys), seed)
            self.assertEqual(cipher.sequence(cipher.seed_from_keys(keys)), keys)

    def test_keys_outside_the_table_are_refused(self):
        for keys in ((0, 0, 0, 0, 0), (1, 2, 3), (256, 0, 0, 0, 0)):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                cipher.seed_from_keys(keys)


class _ArchiveCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        py25keys.clear_catalog_cache()
        self.addCleanup(py25keys.clear_catalog_cache)

    def archive(self, fixture):
        payload, rows = fixture
        package, catalog = _write(self.root, "script.fls", payload, rows)
        archive = ArchiveDocument(package)
        self.addCleanup(archive.close)
        return archive, catalog


class VerdictCacheTests(_ArchiveCase):
    def test_hit_skips_recomputation_and_adopts_only_names(self):
        archive, catalog = self.archive(complete_script_fixture())
        cache = VerdictCache(self.root / "cache", "test-version")
        first = verified_with_cache(
            archive, catalog, cache, tool_version="test-version"
        )
        self.assertTrue(first.accepted)
        self.assertFalse(first.cached)

        with ArchiveDocument(archive.path) as reopened:
            with patch.object(
                package_selfcheck,
                "scan_script_paths",
                side_effect=AssertionError("a cache hit must not rescan"),
            ):
                second = verified_with_cache(
                    reopened, catalog, cache, tool_version="test-version"
                )
            self.assertTrue(second.cached)
            self.assertEqual(second.paths, first.paths)
            self.assertEqual(reopened.module_paths, first.paths)
            # A hit still never says the source is trusted.
            self.assertEqual(reopened.module_path_errors, first.errors)

    def test_foreign_or_stale_verdicts_are_never_adopted(self):
        archive, catalog = self.archive(complete_script_fixture())
        cache = VerdictCache(self.root / "cache", "test-version")
        verified_with_cache(archive, catalog, cache, tool_version="test-version")

        # A different parameter table (same package) is a different verdict.
        self.assertIsNone(cache.load(archive, "0" * 64))
        with ArchiveDocument(archive.path) as reopened:
            self.assertIsNone(
                VerdictCache(self.root / "cache", "newer-version").load(
                    reopened, hashlib.sha256(catalog.read_bytes()).hexdigest()
                )
            )
            hit = cache.load(reopened, hashlib.sha256(catalog.read_bytes()).hexdigest())
            self.assertIsNotNone(hit)
            # A verdict for a package with a different entry count never matches.
            self.assertFalse(
                PackageVerdict(
                    archive_sha256=hit.archive_sha256,
                    catalog_sha256=hit.catalog_sha256,
                    tool_version=hit.tool_version,
                    policy=hit.policy,
                    vm=hit.vm,
                    entries=hit.entries + 1,
                    accepted=True,
                    passed=hit.passed,
                    failures=hit.failures,
                    paths=hit.paths,
                    errors=hit.errors,
                ).matches(reopened, hit.catalog_sha256)
            )

    def test_damaged_cache_files_are_ignored_not_fatal(self):
        archive, catalog = self.archive(complete_script_fixture())
        cache = VerdictCache(self.root / "cache", "test-version")
        verified_with_cache(archive, catalog, cache, tool_version="test-version")
        digest = hashlib.sha256(catalog.read_bytes()).hexdigest()
        target = cache.path_for(archive.fingerprint())

        target.write_text("{not json", encoding="utf-8")
        self.assertIsNone(cache.load(archive, digest))
        target.write_text('{"schema": 99}', encoding="utf-8")
        self.assertIsNone(cache.load(archive, digest))
        target.write_text("{}", encoding="utf-8")
        self.assertIsNone(cache.load(archive, digest))
        target.unlink()
        self.assertIsNone(cache.load(archive, digest))

    def test_refused_parameters_are_not_pinned_as_acceptable(self):
        payload, rows = many_module_fixture(count=120)
        package, catalog = _write(self.root, "script.fls", payload, rows)
        # A catalog whose keys belong to no entry at all.
        catalog.write_text(
            json.dumps({str(i): {"keys": [0, 0, 0, 0, 0], "bounds": [1, 2, 3, 4]}
                        for i in range(120)}),
            encoding="utf-8",
        )
        cache = VerdictCache(self.root / "cache", "test-version")
        with ArchiveDocument(package) as archive:
            check = verified_with_cache(archive, catalog, cache, tool_version="test")
            self.assertFalse(check.accepted)
            self.assertTrue(check.refused_early)
            self.assertFalse(cache.path_for(archive.fingerprint()).exists())
        self.assertEqual(default_cache_root().name, "verdicts")
        self.assertEqual(len(policy_fingerprint()), 64)


class ProbeTests(_ArchiveCase):
    def test_mismatched_parameters_are_refused_from_the_probe(self):
        payload, rows = many_module_fixture(count=120)
        package, catalog = _write(self.root, "script.fls", payload, rows)
        catalog.write_text(
            json.dumps({str(i): {"keys": [0, 0, 0, 0, 0], "bounds": [1, 2, 3, 4]}
                        for i in range(120)}),
            encoding="utf-8",
        )
        with ArchiveDocument(package) as archive:
            seen = []
            original = module_paths.scan_script_paths

            def spy(source, ref, **kwargs):
                seen.append(kwargs.get("limit"))
                return original(source, ref, **kwargs)

            with patch.object(
                package_selfcheck, "scan_script_paths", side_effect=spy
            ):
                check = verify_with_catalog(archive, catalog)
        self.assertEqual(seen, [PROBE_ENTRIES])  # exactly one bounded pass
        self.assertFalse(check.accepted)
        self.assertTrue(check.refused_early)
        self.assertEqual(check.probed, PROBE_ENTRIES)
        self.assertIn("探测", check.report())

    def test_matching_parameters_always_get_the_complete_pass(self):
        payload, rows = many_module_fixture(count=120)
        package, catalog = _write(self.root, "script.fls", payload, rows)
        with ArchiveDocument(package) as archive:
            seen = []
            original = module_paths.scan_script_paths

            def spy(source, ref, **kwargs):
                seen.append(kwargs.get("limit"))
                return original(source, ref, **kwargs)

            with patch.object(
                package_selfcheck, "scan_script_paths", side_effect=spy
            ):
                check = verify_with_catalog(archive, catalog)
        self.assertEqual(seen, [PROBE_ENTRIES, None])  # probe, then the full pass
        self.assertTrue(check.accepted)
        self.assertEqual(check.probed, 0)
        self.assertEqual(check.total, 120)

    def test_small_packages_skip_the_probe(self):
        archive, catalog = self.archive(script_fixture(two_modules=False))
        with ArchiveDocument(archive.path) as reopened:
            check = verify_with_catalog(reopened, catalog)
        self.assertEqual(check.probed, 0)


class EngineResultProtocolTests(unittest.TestCase):
    def result(self, **overrides):
        base = {
            "engine_protocol": "mxsj-recovery/3",
            "source": "x = 1\n",
            "disassembly": "",
            "complete": True,
            "diagnostics": [],
            "truncated": {"source": False, "disassembly": False},
        }
        base.update(overrides)
        return base

    def test_current_and_previous_protocols_are_accepted(self):
        self.assertEqual(validate_result(self.result())["source"], "x = 1\n")
        self.assertTrue(
            validate_result(self.result(engine_protocol="mxsj-recovery/2"))["complete"]
        )

    def test_unknown_protocol_and_bad_truncation_report_are_refused(self):
        for bad in (
            self.result(engine_protocol="mxsj-recovery/9"),
            self.result(truncated={"source": "yes"}),
            self.result(truncated=[True, False]),
            self.result(diagnostics=[1]),
            self.result(complete="yes"),
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_result(bad)

    def test_text_budgets_are_enforced_at_the_new_ceiling(self):
        validate_result(self.result(source="x" * MAX_SOURCE_CHARS))
        with self.assertRaises(ValueError):
            validate_result(self.result(source="x" * (MAX_SOURCE_CHARS + 1)))
        with self.assertRaises(ValueError):
            validate_result(
                self.result(disassembly="x" * (MAX_DISASSEMBLY_CHARS + 1))
            )


class TruncationTests(unittest.TestCase):
    def test_worker_text_sinks_declare_truncation_instead_of_raising(self):
        from script_editor.data import recovery_worker

        sink = recovery_worker.BoundedText(4)
        self.assertEqual(sink.write("abc"), 3)
        self.assertFalse(sink.truncated)
        self.assertEqual(sink.write("defgh"), 1)
        self.assertTrue(sink.truncated)
        self.assertEqual(sink.getvalue(), "abcd")
        self.assertEqual(sink.write("more"), 0)
        self.assertTrue(sink.truncated)
        self.assertEqual(recovery_worker.ENGINE_PROTOCOL, "mxsj-recovery/3")
        self.assertGreaterEqual(recovery_worker.SOURCE_LIMIT, 8 * 1024 * 1024)


class SessionCacheTests(_ArchiveCase):
    def test_cache_is_bounded_and_returns_copies(self):
        cache = RecoverySessionCache(limit=2)
        cache.put(("a",), {"source": "1"})
        value = cache.get(("a",))
        value["source"] = "mutated"
        self.assertEqual(cache.get(("a",))["source"], "1")
        cache.put(("b",), {"source": "2"})
        cache.put(("c",), {"source": "3"})  # evicts everything at the bound
        self.assertEqual(len(cache), 1)
        self.assertIsNone(cache.get(("a",)))
        cache.clear()
        self.assertEqual(len(cache), 0)

    def test_core_recovery_does_not_cache_without_an_owner(self):
        import inspect

        from script_editor.core.services.module_browser import recover_standard

        signature = inspect.signature(recover_standard)
        self.assertIsNone(signature.parameters["cache"].default)


if __name__ == "__main__":
    unittest.main()
