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


class TestCorruptionsAndErrors(unittest.TestCase):
    """Test behavior when files, hashes, headers, types, or keys are corrupted."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def _create_minimal_dataset(self, csv_content: str, columns: list[dict], pk: list[str], row_count: int):
        data = csv_content.encode("utf-8")
        sha = hashlib.sha256(data).hexdigest()
        byte_len = len(data)

        csv_file = self.base_path / "test.csv"
        csv_file.write_bytes(data)

        manifest = {
            "batch": "test_batch",
            "files": {
                "test.csv": {
                    "bytes": byte_len,
                    "sha256": sha,
                    "rows": row_count,
                    "primary_key": pk,
                    "columns": columns,
                }
            },
        }
        (self.base_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return manifest

    def test_missing_csv_file_raises_integrity_error(self):
        manifest = {
            "batch": "test_batch",
            "files": {
                "missing.csv": {
                    "bytes": 100,
                    "sha256": "fakehash",
                    "rows": 1,
                    "primary_key": ["id"],
                    "columns": [{"name": "id", "type": "int"}],
                }
            },
        }
        (self.base_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(self.base_path)

    def test_sha256_mismatch_raises_integrity_error(self):
        csv_content = '"id","name"\n"1","test"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        manifest = self._create_minimal_dataset(csv_content, cols, ["id"], 1)
        # Corrupt manifest sha
        manifest["files"]["test.csv"]["sha256"] = "0000000000000000000000000000000000000000000000000000000000000000"
        (self.base_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(self.base_path)

    def test_byte_size_mismatch_raises_integrity_error(self):
        csv_content = '"id","name"\n"1","test"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        manifest = self._create_minimal_dataset(csv_content, cols, ["id"], 1)
        # Corrupt byte size
        manifest["files"]["test.csv"]["bytes"] = 999999
        (self.base_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(self.base_path)

    def test_row_count_mismatch_raises_integrity_error(self):
        csv_content = '"id","name"\n"1","test"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        manifest = self._create_minimal_dataset(csv_content, cols, ["id"], 1)
        # Claim 2 rows when only 1 exists
        data = csv_content.encode("utf-8")
        manifest["files"]["test.csv"]["rows"] = 2
        manifest["files"]["test.csv"]["sha256"] = hashlib.sha256(data).hexdigest()
        manifest["files"]["test.csv"]["bytes"] = len(data)
        (self.base_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaises(CatalogIntegrityError):
            ReviewCatalog.load(self.base_path)

    def test_missing_column_in_header_raises_schema_error(self):
        # CSV header missing column 'name'
        csv_content = '"id"\n"1"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        self._create_minimal_dataset(csv_content, cols, ["id"], 1)

        with self.assertRaises(CatalogSchemaError):
            ReviewCatalog.load(self.base_path)

    def test_extra_column_in_header_raises_schema_error(self):
        # CSV header has extra column
        csv_content = '"id","name","extra"\n"1","test","extra_val"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        self._create_minimal_dataset(csv_content, cols, ["id"], 1)

        with self.assertRaises(CatalogSchemaError):
            ReviewCatalog.load(self.base_path)

    def test_invalid_type_conversion_raises_value_error(self):
        # Value "not_an_int" cannot be parsed as int
        csv_content = '"id","name"\n"not_an_int","test"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        self._create_minimal_dataset(csv_content, cols, ["id"], 1)

        with self.assertRaises(CatalogValueError):
            ReviewCatalog.load(self.base_path)

    def test_duplicate_primary_key_raises_key_error(self):
        # Duplicate key "1"
        csv_content = '"id","name"\n"1","test1"\n"1","test2"\n'
        cols = [{"name": "id", "type": "int"}, {"name": "name", "type": "str"}]
        self._create_minimal_dataset(csv_content, cols, ["id"], 2)

        with self.assertRaises(CatalogKeyError):
            ReviewCatalog.load(self.base_path)


if __name__ == "__main__":
    unittest.main()
