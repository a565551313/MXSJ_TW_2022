"""Tests for domain semantics and immutable review invariants."""

import sys
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from mxsj_catalog.catalog import ReviewCatalog


class TestReviewSemantics(unittest.TestCase):
    """Verify non-negotiable review semantics and boundary facts."""

    @classmethod
    def setUpClass(cls):
        cls.catalog = ReviewCatalog.load()

    def test_quarantine_records_integrity(self):
        # Exactly 4 quarantined records
        self.assertEqual(len(self.catalog._quarantine), 4)
        quarantine_map = {(q.entry_index, str(q.record_key)): q for q in self.catalog._quarantine}

        # Item 72548 (invalid cp950)
        self.assertIn((1945, "72548"), quarantine_map)
        q_item = quarantine_map[(1945, "72548")]
        self.assertFalse(q_item.native_verified)
        self.assertIn("invalid_cp950_source_name_bytes_preserved", q_item.reasons)
        raw_val = q_item.value_under_applied_profile
        # Preserved raw hex: c2f9a448a7a4c34dc5e9c5e784
        hex_data = raw_val["tuple"][0]["bytes_hex"]
        self.assertEqual(hex_data, "c2f9a448a7a4c34dc5e9c5e784")

        # Aptitude 2800 (法力資質 2130 > 1989)
        self.assertIn((2954, "2800"), quarantine_map)
        q_apt = quarantine_map[(2954, "2800")]
        self.assertFalse(q_apt.native_verified)
        self.assertIn("aptitude_value_exceeds_named_maximum_unresolved", q_apt.reasons)

        # Skill 719 and 4406
        self.assertIn((3205, "719"), quarantine_map)
        self.assertIn((3205, "4406"), quarantine_map)

    def test_missing_aptitudes_distinguished_and_not_zero_filled(self):
        missing = self.catalog.get_missing_aptitudes()
        self.assertEqual(len(missing), 3)
        missing_ids = {m["client_shape_id"] for m in missing}
        self.assertEqual(missing_ids, {3010, 4021, 4022})

        # Check they do not exist in pet_aptitudes dataset
        apt_ds = self.catalog.get_dataset("pet_aptitudes")
        for mid in [3010, 4021, 4022]:
            self.assertIsNone(apt_ds.get_by_pk(str(mid)))

    def test_skill_name_ambiguity_preserved(self):
        ambiguous = self.catalog.get_ambiguous_skills()
        self.assertEqual(len(ambiguous), 4)

        gaoji = [s["skill_id"] for s in ambiguous if s["skill_name_raw"] == "高級命中"]
        self.assertEqual(sorted(gaoji), [229, 255])

        zhongji = [s["skill_id"] for s in ambiguous if s["skill_name_raw"] == "終級命中"]
        self.assertEqual(sorted(zhongji), [329, 355])

        # All must have ambiguous=True
        for s in ambiguous:
            self.assertTrue(s["ambiguous"])
            self.assertEqual(s["match_count"], 2)

    def test_skill_overwrites_evidence(self):
        self.assertEqual(len(self.catalog._overwrites), 9)
        overwrites_ds = self.catalog.get_dataset("pet_skill_overwrites")
        self.assertEqual(len(overwrites_ds.records), 9)

        # Verify entry 4573 rename
        rec_4573 = [r for r in overwrites_ds.records if r["skill_id"] == 4573]
        self.assertEqual(len(rec_4573), 1)
        self.assertEqual(rec_4573[0]["old_name"], "天魔返生術")
        self.assertEqual(rec_4573[0]["new_name"], "地魔返生術")
        self.assertFalse(rec_4573[0]["identical_values"])

    def test_map_npc_source_separation_and_zero_ids(self):
        # 2601 POS records
        ds_2601 = self.catalog.get_dataset("npcposdata_records")
        self.assertEqual(len(ds_2601.records), 1335)
        # Check zero npcid records count
        zero_npcid_2601 = [r for r in ds_2601.records if r["npcid"] == 0]
        self.assertEqual(len(zero_npcid_2601), 632)

        # 2804 POS records
        ds_2804 = self.catalog.get_dataset("minimapnpcpos_pos_records")
        self.assertEqual(len(ds_2804.records), 1344)
        zero_npcid_2804 = [r for r in ds_2804.records if r["npcid"] == 0]
        self.assertEqual(len(zero_npcid_2804), 631)

        # Composite PK uniqueness
        self.assertEqual(len(ds_2601.index_by_pk), 1335)
        self.assertEqual(len(ds_2804.index_by_pk), 1344)


if __name__ == "__main__":
    unittest.main()
