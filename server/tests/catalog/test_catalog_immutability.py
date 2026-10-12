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


if __name__ == "__main__":
    unittest.main()
