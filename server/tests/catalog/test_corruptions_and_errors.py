"""Tests for data anomalies, corruptions, and integrity errors."""

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mxsj_catalog.catalog import ReviewCatalog
from mxsj_catalog.errors import (
    CatalogIntegrityError,
    CatalogKeyError,
    CatalogSchemaError,
    CatalogValueError,
)

ORIGINAL_BATCH_DIR = Path(__file__).resolve().parent.parent.parent / "docs" / "csv_checks" / "batch_001"


class TestCorruptionsAndErrors(unittest.TestCase):
    """Test behavior when files, hashes, headers, types, or keys are corrupted."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _copy_real_batch(self) -> Path:
        """Create a full working copy of batch_001 for negative mutation tests."""
        import uuid
        dest = self.base_path / f"batch_copy_{uuid.uuid4().hex[:8]}"
        shutil.copytree(ORIGINAL_BATCH_DIR, dest)
        return dest

    def test_missing_evidence_files_raises_integrity_error(self):
        # 1. Missing quarantine.jsonl
        batch_dir = self._copy_real_batch()
        (batch_dir / "quarantine.jsonl").unlink()
        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir)

        # 2. Missing overwrite_evidence.jsonl
        batch_dir2 = self._copy_real_batch()
        (batch_dir2 / "overwrite_evidence.jsonl").unlink()
        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir2)

        # 3. Missing validation.json
        batch_dir3 = self._copy_real_batch()
        (batch_dir3 / "validation.json").unlink()
        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir3)

        # 4. Missing maps_npcs/provenance.json
        batch_dir4 = self._copy_real_batch()
        (batch_dir4 / "maps_npcs" / "provenance.json").unlink()
        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir4)

    def test_tampered_quarantine_jsonl_raises_integrity_error(self):
        batch_dir = self._copy_real_batch()
        q_file = batch_dir / "quarantine.jsonl"
        lines = q_file.read_text(encoding="utf-8").splitlines()
        # Tamper record_key to 999999 without updating manifest hash
        tampered_line = lines[0].replace('"record_key": 72548', '"record_key": 999999')
        lines[0] = tampered_line
        q_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir)

    def test_missing_dataset_declaration_in_manifest_raises_integrity_error(self):
        # Delete items.csv declaration from manifest
        batch_dir = self._copy_real_batch()
        manifest_path = batch_dir / "manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest_data["files"]["items.csv"]
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir)

    def test_unknown_column_type_raises_schema_error(self):
        batch_dir = self._copy_real_batch()
        manifest_path = batch_dir / "manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        # Change column type in items.csv to unsupported type
        manifest_data["files"]["items.csv"]["columns"][0]["type"] = "unsupported_type"
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

        with self.assertRaises(CatalogSchemaError):
            ReviewCatalog.load(batch_dir)

    def test_path_traversal_in_manifest_raises_integrity_error(self):
        batch_dir = self._copy_real_batch()
        manifest_path = batch_dir / "manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        # Inject outside path
        manifest_data["files"]["../outside.csv"] = {
            "bytes": 10,
            "sha256": "0" * 64,
            "rows": 1,
            "columns": [{"name": "id", "type": "int"}],
            "primary_key": ["id"],
        }
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir)

    def test_corrupted_json_in_evidence_file_raises_integrity_error(self):
        batch_dir = self._copy_real_batch()
        val_file = batch_dir / "validation.json"
        val_file.write_bytes(b"{ broken json")
        # Update manifest bytes/sha to pass byte check, but JSON parsing should fail
        manifest_path = batch_dir / "manifest.json"
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_data["files"]["validation.json"]["bytes"] = len(b"{ broken json")
        manifest_data["files"]["validation.json"]["sha256"] = hashlib.sha256(b"{ broken json").hexdigest()
        manifest_path.write_text(json.dumps(manifest_data), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(batch_dir)


if __name__ == "__main__":
    unittest.main()
