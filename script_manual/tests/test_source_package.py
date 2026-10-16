from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location(
    "manual_source_package",
    Path(__file__).resolve().parents[1] / "make_source_package.py",
)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class SourcePackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name)
        self.repo = self.parent / "中文 space"
        self.repo.mkdir()
        self.tracked = []
        self.write("script_manual/src/example.py", b"# synthetic tool\n")
        self.evidence = "evidence/passive.txt"
        raw = b"synthetic evidence, never executed\n"
        self.write(self.evidence, raw)
        self.annotation = "script_manual/annotations/login/example.json"
        self.record = {
            "entry_index": 1,
            "sources": [
                {"path": self.evidence, "sha256": hashlib.sha256(raw).hexdigest()}
            ],
        }
        self.write(self.annotation, json.dumps(self.record).encode())
        # Tracked but unrelated material must not get swept into the ZIP.
        self.write("unrelated/private.txt", b"synthetic excluded fixture")

    def write(self, name, raw):
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        if name not in self.tracked:
            self.tracked.append(name)

    def test_external_evidence_manifest_and_deterministic_zip(self):
        outputs = [self.parent / f"package{i}.zip" for i in range(2)]
        for output in outputs:
            manifest = package.build_package(
                self.repo, self.tracked, output, "synthetic-commit"
            )
            self.assertIn(self.evidence, manifest["files"])
            self.assertNotIn("unrelated/private.txt", manifest["files"])
            with zipfile.ZipFile(output) as archive:
                stored = json.loads(
                    archive.read(package.PACKAGE_ROOT + "/PACKAGE_MANIFEST.json")
                )
                self.assertEqual(stored, manifest)
                self.assertIsNone(archive.testzip())
        self.assertEqual(outputs[0].read_bytes(), outputs[1].read_bytes())

    def test_task_guide_bytes_survive_source_package_whitelist(self):
        guide = "script_manual/guides/synthetic.json"
        raw = b'{"synthetic": "guide package inclusion only"}\n'
        self.write(guide, raw)
        output = self.parent / "guide-package.zip"
        manifest = package.build_package(self.repo, self.tracked, output, "fixture")
        self.assertEqual(
            manifest["files"][guide]["sha256"], hashlib.sha256(raw).hexdigest()
        )
        with zipfile.ZipFile(output) as archive:
            self.assertEqual(archive.read(package.PACKAGE_ROOT + "/" + guide), raw)

    def test_mismatched_or_missing_evidence_is_not_packaged(self):
        for missing in (False, True):
            with self.subTest(missing=missing):
                record = dict(self.record)
                record["sources"] = [{"path": self.evidence, "sha256": "0" * 64}]
                self.write(self.annotation, json.dumps(record).encode())
                tracked = [
                    p for p in self.tracked if not (missing and p == self.evidence)
                ]
                output = self.parent / "bad.zip"
                with self.assertRaises(ValueError):
                    package.build_package(self.repo, tracked, output, "synthetic")
                self.assertFalse(output.exists())

    def test_rejects_in_repo_output_and_never_overwrites(self):
        with self.assertRaises(ValueError):
            package.build_package(
                self.repo, self.tracked, self.repo / "bad.zip", "synthetic"
            )
        output = self.parent / "existing.zip"
        output.write_bytes(b"preserve original")
        with self.assertRaises(FileExistsError):
            package.build_package(self.repo, self.tracked, output, "synthetic")
        self.assertEqual(output.read_bytes(), b"preserve original")

    def test_paths_and_symlinks_are_rejected(self):
        for name in ("../private.txt", "a/../escape.py", "C:\\private.py"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                package.safe_file(self.repo, name)
        # No Windows symlink privilege needed for this negative control.
        with patch.object(Path, "is_symlink", return_value=True):
            with self.assertRaises(ValueError):
                package.safe_file(self.repo, self.evidence)
