"""Tests to ensure catalog callers cannot mutate loaded datasets."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mxsj_catalog.catalog import ReviewCatalog


class TestCatalogImmutability(unittest.TestCase):
    """Ensure catalog records cannot be modified in-place by consumers."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = ReviewCatalog.load()

    def test_direct_dataset_record_mutation_prevented(self):
        ds = self.catalog.get_dataset("items")
        with self.assertRaises(TypeError):
            # mappingproxy does not support item assignment
            ds.records[0]["name"] = "tampered_value"

    def test_get_record_copy_mutation_does_not_affect_catalog(self):
        rec = self.catalog.get_record("items", "11")
        self.assertIsNotNone(rec)
        original_name = rec["name"]
        rec["name"] = "tampered_name"

        # Verify underlying catalog record remained untouched
        rec_fresh = self.catalog.get_record("items", "11")
        self.assertEqual(rec_fresh["name"], original_name)

    def test_query_records_mutation_does_not_affect_catalog(self):
        recs, total = self.catalog.query_records("pets", limit=2)
        original_name = recs[0]["name"]
        recs[0]["name"] = "tampered_pet"

        ds = self.catalog.get_dataset("pets")
        self.assertEqual(ds.records[0]["name"], original_name)

    def test_batch_info_nested_mutation_does_not_affect_catalog(self):
        # Reproduce coordinator's mutation test
        info1 = self.catalog.get_batch_info()
        orig_check = info1["validation_summary"]["checks"]["csv_round_trip"]
        orig_1945_count = info1["tables_summary"]["1945"]["review_csv_records"]

        # Mutate nested dictionaries
        info1["validation_summary"]["checks"]["csv_round_trip"] = "CALLER_CHANGED"
        info1["tables_summary"]["1945"]["review_csv_records"] = -999

        # Verify fresh fetch is completely unaffected
        info2 = self.catalog.get_batch_info()
        self.assertEqual(info2["validation_summary"]["checks"]["csv_round_trip"], orig_check)
        self.assertEqual(info2["tables_summary"]["1945"]["review_csv_records"], orig_1945_count)

    def test_schema_source_entry_cannot_be_mutated(self):
        # Ensure schema.source_entry is an immutable tuple (or int) and cannot be appended to
        ds = self.catalog.get_dataset("npc_2601_vs_2804_agreement")
        source_entry = ds.schema.source_entry
        self.assertIsInstance(source_entry, tuple)
        self.assertEqual(source_entry, (2601, 2804))

        with self.assertRaises(AttributeError):
            source_entry.append(999)

    def test_list_datasets_mutation_does_not_affect_catalog(self):
        datasets = self.catalog.list_datasets()
        datasets[0]["id"] = "tampered_id"
        datasets[0]["columns"].append({"name": "extra", "type": "str"})

        # Subsequent call is fresh
        fresh = self.catalog.list_datasets()
        self.assertNotEqual(fresh[0]["id"], "tampered_id")
        self.assertNotIn("extra", [c["name"] for c in fresh[0]["columns"]])


if __name__ == "__main__":
    unittest.main()
