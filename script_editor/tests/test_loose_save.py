"""Loose mode ("write back to the original package") at the core level.

Synthetic packages only. These tests pin the three properties that matter:
a loose save writes exactly the changed entries into the original file, the
previous bytes survive in a rolling ``.bak``, and every strict guarantee still
runs before the swap (a failed build leaves the package untouched).
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from native_fixtures import minimal_pyc, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import Compiler
from script_editor.core.inspection.native import inspect_module
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import CatalogRef, ProjectState
from script_editor.core.services.client_install import (
    client_root_for,
    is_client_install,
)
from script_editor.core.services.loose_save import (
    MAX_LOOSE_ENTRIES,
    batch_summary,
    changed_bindings,
    rejection,
)
from script_editor.core.services.native_build import BACKUP_SUFFIX
from script_editor.core.services.workflow import (
    Snapshot,
    prepare_package,
    publish_package,
)


def binding_for(archive, fingerprint, index, identity, source):
    return Binding(
        archive, fingerprint, "py25", index, identity, source, "", "", "authored", ""
    )


class Fixture:
    """Two-module synthetic script package plus fake compiler plumbing."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mxscript-loose-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        raw, catalog = script_fixture(two_modules=True)
        self.archive = self.root / "script.fls"
        self.archive.write_bytes(raw)
        self.before = raw
        self.catalog_file = self.root / "catalog.json"
        self.catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
        self.digest = hashlib.sha256(raw).hexdigest()
        self.catalog = CatalogRef(
            self.archive,
            self.digest,
            self.catalog_file,
            hashlib.sha256(self.catalog_file.read_bytes()).hexdigest(),
        )
        self.compiler = Compiler(Path(sys.executable), "py25", "unit-test", 64, "t")
        with ArchiveDocument(self.archive) as doc:
            identities = {i: doc.entries[i].identity for i in (0, 1)}
        self.bindings = []
        for index in (0, 1):
            source = self.root / f"module{index}.py"
            source.write_text(f"VALUE = {index}\n", encoding="utf-8")
            self.bindings.append(
                binding_for(
                    self.archive, self.digest, index, identities[index], source
                )
            )
        self.state = ProjectState(tuple(self.bindings), (self.catalog,))
        self.seeds = {}

    def fake_compile(self, seeds):
        """Compile stub: source text decides the pyc, so re-saves are stable."""
        self.seeds = dict(seeds)
        fallback = [100]

        def compile_standard(compiler, source, filename, destination, protected=()):
            seed = self.seeds.get(source)
            if seed is None:
                fallback[0] += 1
                seed = fallback[0]
            pyc = minimal_pyc("py25", seed)
            destination.write_bytes(pyc)
            return hashlib.sha256(pyc).hexdigest()

        return compile_standard

    def patches(self, seeds):
        return (
            patch(
                "script_editor.core.services.workflow.compile_standard",
                self.fake_compile(seeds),
            ),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch("script_editor.core.services.native_build.audit_standard"),
        )

    def run_patched(self, seeds, function):
        first, second, third = self.patches(seeds)
        with first, second, third:
            return function()

    def snapshots(self, bindings, texts):
        return [
            Snapshot(binding, texts[binding.index], "py25") for binding in bindings
        ]

    def prepare(self, texts, bindings=None, catalog=None, seeds=None):
        """``texts`` maps entry index -> source text; ``seeds`` picks the pyc."""
        targets = bindings or self.bindings
        mapping = seeds or {texts[index]: index + 1 for index in texts}
        return self.run_patched(
            mapping,
            lambda: prepare_package(
                self.snapshots(targets, texts), self.compiler, catalog or self.catalog
            ),
        )

    def publish(self, plan, state=None, **options):
        return self.run_patched(
            {},
            lambda: publish_package(plan, state or self.state, **options),
        )


class LooseSaveTests(Fixture, unittest.TestCase):
    def test_both_changed_modules_are_written_in_one_loose_save(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        self.assertEqual(plan.indexes, (0, 1))
        report, state = self.publish(plan, in_place=True)
        self.assertEqual(report.modified_indexes, (0, 1))
        self.assertEqual(report.output, self.archive)
        self.assertEqual(
            hashlib.sha256(self.archive.read_bytes()).hexdigest(), report.output_sha256
        )
        for binding in state.bindings:
            self.assertEqual(binding.archive, self.archive)
            self.assertEqual(binding.fingerprint, report.output_sha256)
        self.assertEqual(state.catalogs[0].fingerprint, report.output_sha256)

    def test_previous_bytes_survive_in_one_rolling_backup(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        first_report, _ = self.publish(plan, in_place=True)
        backup = self.archive.with_name(self.archive.name + BACKUP_SUFFIX)
        self.assertEqual(backup.read_bytes(), self.before)
        first = self.archive.read_bytes()

        digest = first_report.output_sha256
        state = ProjectState(
            tuple(
                binding_for(self.archive, digest, b.index, b.identity, b.source)
                for b in self.bindings
            ),
            (CatalogRef(self.archive, digest, self.catalog_file, self.catalog.sha256),),
        )
        texts = {0: "VALUE = 101\n", 1: "VALUE = 201\n"}
        plan = self.prepare(
            texts,
            bindings=state.bindings,
            catalog=state.catalogs[0],
            seeds={texts[0]: 7, texts[1]: 8},
        )
        self.publish(plan, state=state, in_place=True)
        self.assertEqual(backup.read_bytes(), first)
        self.assertEqual(
            sorted(p.name for p in self.root.iterdir() if p.suffix in {".fls", ".bak"}),
            ["script.fls", "script.fls" + BACKUP_SUFFIX],
        )

    def test_written_modules_reopen_with_the_new_fingerprint(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        report, state = self.publish(plan, in_place=True)
        with ArchiveDocument(self.archive) as doc:
            self.assertEqual(doc.fingerprint(), report.output_sha256)
            for index in (0, 1):
                _, filename, _ = inspect_module(doc, index, state.catalogs[0])
                self.assertTrue(filename)

    def test_only_the_changed_module_is_rewritten(self):
        texts = {0: "VALUE = 100\n", 1: "VALUE = 200\n"}
        # Seed the package so both modules hold known pycs.
        self.publish(self.prepare(texts), in_place=True)
        with ArchiveDocument(self.archive) as doc:
            digest = doc.fingerprint()
        state = ProjectState(
            tuple(
                binding_for(self.archive, digest, b.index, b.identity, b.source)
                for b in self.bindings
            ),
            (CatalogRef(self.archive, digest, self.catalog_file, self.catalog.sha256),),
        )
        with ArchiveDocument(self.archive) as doc:
            untouched = doc.read_stored(1)
        changed = {0: "VALUE = 999\n", 1: "VALUE = 200\n"}
        plan = self.prepare(
            changed,
            bindings=state.bindings,
            catalog=state.catalogs[0],
            # Entry 1 keeps the pyc it already has, so only entry 0 changes.
            seeds={changed[0]: 9, changed[1]: 2},
        )
        self.assertEqual(plan.indexes, (0,))
        self.assertEqual(plan.unchanged, (1,))
        self.publish(plan, state=state, in_place=True)
        with ArchiveDocument(self.archive) as doc:
            self.assertEqual(doc.read_stored(1), untouched)

    def test_identical_payload_is_refused_instead_of_rewriting(self):
        texts = {0: "VALUE = 100\n", 1: "VALUE = 200\n"}
        report, _ = self.publish(self.prepare(texts), in_place=True)
        digest = report.output_sha256
        state = ProjectState(
            tuple(
                binding_for(self.archive, digest, b.index, b.identity, b.source)
                for b in self.bindings
            ),
            (CatalogRef(self.archive, digest, self.catalog_file, self.catalog.sha256),),
        )
        with self.assertRaises(ValueError) as caught:
            self.prepare(texts, bindings=state.bindings, catalog=state.catalogs[0])
        self.assertIn("没有需要写回的改动", str(caught.exception))

    def test_mixed_packages_are_rejected(self):
        other = self.root / "other.fls"
        other.write_bytes(script_fixture()[0])
        foreign = binding_for(
            other, "0" * 64, 0, "00000000", self.bindings[1].source
        )
        with self.assertRaises(ValueError) as caught:
            self.prepare(
                {0: "VALUE = 1\n", 1: "VALUE = 2\n"},
                bindings=[self.bindings[0], foreign],
            )
        self.assertIn("同一个包", str(caught.exception))

    def test_failed_verification_leaves_the_package_untouched(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        with patch(
            "script_editor.core.services.native_build.verify_output",
            side_effect=ValueError("independent native readback differs"),
        ):
            with self.assertRaises(ValueError):
                self.publish(plan, in_place=True)
        self.assertEqual(self.archive.read_bytes(), self.before)
        self.assertFalse(
            self.archive.with_name(self.archive.name + BACKUP_SUFFIX).exists()
        )
        self.assertFalse(list(self.root.glob(".mxscript-build-*")))
        self.assertFalse(list(self.root.glob(".mxscript-bak-*")))


class StrictPublishTests(Fixture, unittest.TestCase):
    def test_new_file_destination_still_works_and_is_never_overwritten(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        target = self.root / "out.fls"
        report, state = self.publish(plan, destination=target)
        self.assertEqual(report.output, target)
        self.assertEqual(state.bindings[0].archive, target)
        self.assertEqual(self.archive.read_bytes(), self.before)
        with self.assertRaises(ValueError):
            self.publish(
                self.prepare(
                    {0: "VALUE = 7\n", 1: "VALUE = 8\n"},
                    bindings=state.bindings,
                    catalog=state.catalogs[0],
                ),
                state=state,
                destination=target,
            )

    def test_strict_publish_without_destination_is_refused(self):
        plan = self.prepare({0: "VALUE = 100\n", 1: "VALUE = 200\n"})
        with self.assertRaises(ValueError) as caught:
            self.publish(plan)
        self.assertIn("必须指定新的输出包名", str(caught.exception))


class ClientInstallTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mxscript-client-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_install_root_is_found_from_the_data_directory(self):
        (self.root / "mx.exe").write_bytes(b"MZ")
        (self.root / "data").mkdir()
        package = self.root / "data" / "script.fls"
        package.write_bytes(b"x")
        self.assertEqual(client_root_for(package), self.root.resolve())
        self.assertTrue(is_client_install(package))

    def test_scratch_directory_is_not_a_client(self):
        package = self.root / "script.fls"
        package.write_bytes(b"x")
        self.assertIsNone(client_root_for(package))

    def test_similar_file_name_does_not_count(self):
        (self.root / "mx.exe.bak").write_bytes(b"MZ")
        (self.root / "data").mkdir()
        package = self.root / "data" / "script.fls"
        package.write_bytes(b"x")
        self.assertIsNone(client_root_for(package))

    def test_far_above_the_install_root_is_not_a_client(self):
        (self.root / "mx.exe").write_bytes(b"MZ")
        deep = self.root / "a" / "b" / "c"
        deep.mkdir(parents=True)
        package = deep / "script.fls"
        package.write_bytes(b"x")
        self.assertIsNone(client_root_for(package))

    def test_missing_path_is_not_an_error(self):
        self.assertIsNone(client_root_for(self.root / "nope" / "script.fls"))


class LooseCandidateTests(unittest.TestCase):
    """Which bindings a loose save would write, without any Qt or file I/O."""

    def setUp(self):
        # Relative, platform-neutral paths: these bindings are never opened.
        self.archive = Path("pkg") / "script.fls"
        self.vm = "py25"

    def binding(self, index, baseline="", archive=None):
        binding = binding_for(
            archive or self.archive,
            "0" * 64,
            index,
            "00000000",
            Path("src") / f"m{index}.py",
        )
        return replace(binding, built_source_sha256=baseline)

    def run_candidates(self, mapping, archive=None):
        """``mapping``: binding -> text or the exception its read raises."""
        bindings = list(mapping)

        def read_text(binding):
            value = mapping[binding]
            if isinstance(value, Exception):
                raise value
            return value

        target = SimpleNamespace(path=self.archive, vm=self.vm)
        return changed_bindings(bindings, target, read_text)

    def test_only_changed_bindings_are_candidates(self):
        same = "VALUE = 1\n"
        baseline = hashlib.sha256(same.encode("utf-8")).hexdigest()
        unchanged = self.binding(0, baseline)
        never_written = self.binding(1)
        candidates, problems = self.run_candidates(
            {unchanged: same, never_written: "VALUE = 2\n"}
        )
        self.assertEqual([c.binding.index for c in candidates], [1])
        self.assertEqual(problems, ())

    def test_unreadable_source_is_reported_not_written(self):
        broken = self.binding(0)
        candidates, problems = self.run_candidates({broken: OSError("missing")})
        self.assertEqual(candidates, ())
        self.assertEqual(len(problems), 1)
        self.assertIn("missing", problems[0].reason)
        self.assertIn("没有「已关联且内容有变动」", rejection(candidates, problems))

    def test_bindings_of_another_package_or_vm_are_ignored(self):
        mine = self.binding(0)
        foreign = self.binding(1, archive=Path("other") / "script.fls")
        other_vm = replace(self.binding(2), vm="py27")
        candidates, _ = self.run_candidates(
            {mine: "VALUE = 2\n", foreign: "VALUE = 3\n", other_vm: "VALUE = 4\n"}
        )
        self.assertEqual([c.binding.index for c in candidates], [0])

    def test_rejection_is_empty_when_something_will_be_written(self):
        self.assertEqual(rejection((object(),), ()), "")

    def test_batch_summary_lists_entries_and_truncates(self):
        mapping = {}
        for index in range(25):
            mapping[self.binding(index)] = "x"
        candidates, problems = self.run_candidates(mapping)
        text = batch_summary(candidates, problems, lambda b: b.source.name)
        self.assertEqual(text.count("· #"), 20)
        self.assertIn("另有 5 条", text)

    def test_batch_summary_refuses_oversized_batches(self):
        mapping = {}
        for index in range(MAX_LOOSE_ENTRIES + 1):
            mapping[self.binding(index)] = "x"
        candidates, problems = self.run_candidates(mapping)
        with self.assertRaises(ValueError) as caught:
            batch_summary(candidates, problems, lambda b: b.source.name)
        self.assertIn("上限", str(caught.exception))

    def test_batch_summary_mentions_skipped_problems(self):
        good = self.binding(0)
        broken = self.binding(1)
        candidates, problems = self.run_candidates(
            {good: "VALUE = 2\n", broken: OSError("nope")}
        )
        text = batch_summary(candidates, problems, lambda b: b.source.name)
        self.assertIn("未纳入 1 条", text)


if __name__ == "__main__":
    unittest.main()
