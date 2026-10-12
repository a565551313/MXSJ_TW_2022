"""Tests for catalog loading and strict type conversions."""

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
from mxsj_catalog.errors import CatalogValueError
from mxsj_catalog.loader import convert_value, load_raw_dataset


class TestCatalogLoaderAndTypes(unittest.TestCase):
    """Verify loading of batch_001 and strict type conversion behavior."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = ReviewCatalog.load()

    def test_load_all_17_datasets(self):
        datasets = self.catalog.list_datasets()
        self.assertEqual(len(datasets), 17)
        ids = {d["id"] for d in datasets}
        expected_ids = {
            "items",
            "pets",
            "pet_skill_candidates",
            "pet_required_skills",
            "pet_aptitudes",
            "pet_aptitude_missing",
            "pet_skills",
            "pet_skill_overwrites",
            "pet_skill_name_matches",
            "mapdata_parent_scene",
            "mapdata_scene_dictionary",
            "minimapnpcpos_pos_records",
            "minimapnpcpos_wenzi_entries",
            "npc_2601_vs_2804_agreement",
            "npcname2realnamedata_alias_to_realname",
            "npcposdata_records",
            "sceneid2name_minimap_scenes",
        }
        self.assertEqual(ids, expected_ids)

    def test_strict_bool_conversion(self):
        # "true" -> True
        self.assertIs(convert_value("true", "bool", "test_col", 1), True)
        self.assertIs(convert_value("True", "bool", "test_col", 1), True)
        self.assertIs(convert_value("TRUE", "bool", "test_col", 1), True)

        # "false" -> False (strictly False, not Python truthy)
        self.assertIs(convert_value("false", "bool", "test_col", 1), False)
        self.assertIs(convert_value("False", "bool", "test_col", 1), False)
        self.assertIs(convert_value("FALSE", "bool", "test_col", 1), False)

        # Non-booleans must raise CatalogValueError
        with self.assertRaises(CatalogValueError):
            convert_value("1", "bool", "test_col", 1)
        with self.assertRaises(CatalogValueError):
            convert_value("0", "bool", "test_col", 1)
        with self.assertRaises(CatalogValueError):
            convert_value("yes", "bool", "test_col", 1)
        with self.assertRaises(CatalogValueError):
            convert_value("", "bool", "test_col", 1)

    def test_strict_int_and_empty_conversion(self):
        self.assertEqual(convert_value("123", "int", "test_col", 1), 123)
        self.assertEqual(convert_value("-45", "int", "test_col", 1), -45)
        with self.assertRaises(CatalogValueError):
            convert_value("12.3", "int", "test_col", 1)
        with self.assertRaises(CatalogValueError):
            convert_value("", "int", "test_col", 1)
        with self.assertRaises(CatalogValueError):
            convert_value("abc", "int", "test_col", 1)

        # int_or_empty
        self.assertIsNone(convert_value("", "int_or_empty", "test_col", 1))
        self.assertEqual(convert_value("99", "int_or_empty", "test_col", 1), 99)
        with self.assertRaises(CatalogValueError):
            convert_value("abc", "int_or_empty", "test_col", 1)

    def test_map_npc_blank_values_convention(self):
        ds = self.catalog.get_dataset("minimapnpcpos_pos_records")
        # Check that empty cells in int_or_empty are None (e.g. field12, field13, or unpositioned x/y)
        records_with_none = [r for r in ds.records if r.get("field12") is None or r.get("x") is None]
        self.assertTrue(len(records_with_none) > 0)
        # Check that empty strings in str fields remain empty string ""
        records_with_empty_str = [r for r in ds.records if r.get("secondary_name") == ""]
        self.assertTrue(len(records_with_empty_str) > 0)

    def test_no_formula_eval(self):
        # Skills descriptions and formula fields must remain raw strings
        ds = self.catalog.get_dataset("pet_skills")
        for r in ds.records[:10]:
            self.assertIsInstance(r["description_raw"], str)
            self.assertIsInstance(r["fpneed_raw"], str)
            self.assertIsInstance(r["mpneed_raw"], str)
            self.assertIsInstance(r["hpneed_raw"], str)

    def test_csv_text_streaming_multiline_and_special_characters(self):
        # Test that embedded newlines (\n, \r\n, \r), quotes, commas, and formula prefixes
        # are preserved faithfully without being mangled by premature splitlines().
        temp_dir = tempfile.mkdtemp()
        try:
            base_path = Path(temp_dir)
            expected_text = "first\nsecond\r\nthird\rfourth"
            formula_text = "=SUM(1, 2) + @test - 100"
            csv_content = (
                '"id","desc","formula"\n'
                f'"1","{expected_text}","{formula_text}"\n'
            )
            raw_bytes = csv_content.encode("utf-8")
            (base_path / "test.csv").write_bytes(raw_bytes)

            meta = {
                "bytes": len(raw_bytes),
                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "rows": 1,
                "primary_key": ["id"],
                "columns": [
                    {"name": "id", "type": "int"},
                    {"name": "desc", "type": "str"},
                    {"name": "formula", "type": "str"},
                ],
            }

            dataset = load_raw_dataset("test.csv", meta, base_path)
            self.assertEqual(len(dataset.records), 1)
            record = dataset.records[0]
            # Ensure newlines were not squashed or stripped
            self.assertEqual(record["desc"], expected_text)
            self.assertEqual(record["formula"], formula_text)
            # Ensure not evaluated
            self.assertIsInstance(record["formula"], str)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
