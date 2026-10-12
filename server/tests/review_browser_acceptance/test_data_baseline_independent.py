"""Phase 1 acceptance: the frozen review baseline, recomputed independently.

These assertions come from BATCH_001.md / AGENT_G_CONSOLIDATION.md /
validation.json and are recomputed here from the committed CSV/JSONL artefacts
through the acceptance suite's own reader (``batch_fixture.py``), so a value can
only pass if the artefacts really contain it. They are deliberately *not* part
of the 161 architecture tests, and they are also exposed as a standalone report
by ``server/tools/review_browser_checks/verify_data_baseline.py``.
"""
from __future__ import annotations

import collections
import csv
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import support  # noqa: E402,F401  (adds the acceptance tool directory to sys.path)

from batch_fixture import (  # noqa: E402
    CORE_CSVS, FIXED_EXPECTATIONS, MAP_NPC_CSVS, Batch, TypedJson, default_batch_dir,
)


class BaselineNumbers(unittest.TestCase):
    """The eleven frozen numbers from the acceptance brief."""

    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())

    def test_items_6851(self):
        ids = [row['client_shape_id'] for row in self.batch.rows('items.csv')]
        self.assertEqual(len(ids), 6851)
        self.assertEqual(len(set(ids)), 6851, 'client_shape_id must stay unique')
        self.assertNotIn('72548', ids)

    def test_pets_135(self):
        self.assertEqual(len(self.batch.rows('pets.csv')), 135)

    def test_aptitudes_131(self):
        self.assertEqual(len(self.batch.rows('pet_aptitudes.csv')), 131)

    def test_skills_579(self):
        self.assertEqual(len(self.batch.rows('pet_skills.csv')), 579)

    def test_candidate_skill_relations_458(self):
        self.assertEqual(len(self.batch.rows('pet_skill_candidates.csv')), 458)

    def test_required_skill_relations_26(self):
        self.assertEqual(len(self.batch.rows('pet_required_skills.csv')), 26)

    def test_referenced_skill_names_143(self):
        names = {row['skill_name_raw'] for row in self.batch.rows('pet_skill_candidates.csv')}
        names |= {row['skill_name_raw'] for row in self.batch.rows('pet_required_skills.csv')}
        self.assertEqual(len(names), 143)

    def test_skill_name_match_rows_145(self):
        rows = self.batch.rows('pet_skill_name_matches.csv')
        self.assertEqual(len(rows), 145)
        by_name = collections.Counter(row['skill_name_raw'] for row in rows)
        self.assertEqual(len(by_name), 143)
        self.assertEqual(sorted(by_name.values()).count(2), 2, 'exactly two names hit two ids')
        self.assertEqual(sum(1 for value in by_name.values() if value == 1), 141)

    def test_skill_overwrite_rows_9(self):
        self.assertEqual(len(self.batch.rows('pet_skill_overwrites.csv')), 9)
        self.assertEqual(len(self.batch.overwrite_evidence()), 9)

    def test_quarantined_records_4(self):
        self.assertEqual(len(self.batch.quarantine()), 4)

    def test_missing_aptitude_rows_3(self):
        self.assertEqual(len(self.batch.rows('pet_aptitude_missing.csv')), 3)

    def test_validation_json_matches_recomputation(self):
        validation = self.batch.validation()
        self.assertEqual(validation['skill_write_count'], 590)
        self.assertEqual(validation['skill_unique_count'], 581)
        self.assertEqual(validation['skill_unique_count'],
                         579 + 2, 'unique skill ids = 579 exported + 2 quarantined')
        self.assertEqual(validation['pet_skill_names'], 143)
        self.assertEqual(validation['quarantined_record_count'], 4)
        self.assertEqual(validation['missing_aptitude_count'], 3)
        self.assertEqual({key: value for key, value in validation['tables'].items()},
                         {'1945': {'quarantined_records': 1, 'review_csv_records': 6851,
                                   'source_records': 6852},
                          '2027': {'quarantined_records': 0, 'review_csv_records': 135,
                                   'source_records': 135},
                          '2954': {'quarantined_records': 1, 'review_csv_records': 131,
                                   'source_records': 132},
                          '3205': {'quarantined_records': 2, 'review_csv_records': 579,
                                   'source_records': 581}})
        self.assertTrue(all(value == 'pass' for value in validation['checks'].values()))


class SourceSeparation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())

    def test_source_entry_labels_are_explicit(self):
        for name, expected in sorted(FIXED_EXPECTATIONS['source_entries'].items()):
            rows = self.batch.rows(name)
            if 'source_entry' not in rows[0]:
                continue
            self.assertEqual({row['source_entry'] for row in rows}, {str(entry) for entry in expected}, name)

    def test_two_npc_sources_stay_separate(self):
        first = self.batch.rows('maps_npcs/npcposdata_records.csv')
        second = self.batch.rows('maps_npcs/minimapnpcpos_pos_records.csv')
        self.assertNotEqual([tuple(r) for r in first[:3]], [tuple(r) for r in second[:3]])
        files = self.batch.manifest()['files']
        self.assertEqual(files['maps_npcs/npcposdata_records.csv']['source_entry'], 2601)
        self.assertEqual(files['maps_npcs/minimapnpcpos_pos_records.csv']['source_entry'], 2804)
        self.assertEqual(files['maps_npcs/npc_2601_vs_2804_agreement.csv']['source_entry'], [2601, 2804])
        agreement = self.batch.rows('maps_npcs/npc_2601_vs_2804_agreement.csv')
        self.assertTrue(all(row['npcid'] != '0' for row in agreement))
        self.assertEqual(len(agreement), 677)

    def test_staging_bytes_are_unchanged(self):
        staging = Path(__file__).resolve().parents[3] / 'server/docs/csv_checks/staging'
        compared = 0
        for name in MAP_NPC_CSVS:
            staged = staging / Path(name).name
            if staged.exists():
                self.assertEqual(self.batch.read_bytes(name), staged.read_bytes(), name)
                compared += 1
        self.assertGreaterEqual(compared, 3)


class ZeroIdsDuplicatesAndOrder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())
        cls.first = cls.batch.rows('maps_npcs/npcposdata_records.csv')
        cls.second = cls.batch.rows('maps_npcs/minimapnpcpos_pos_records.csv')

    def test_zero_npc_id_records_are_kept(self):
        self.assertEqual(sum(1 for row in self.first if row['npcid'] == '0'), 632)
        self.assertEqual(sum(1 for row in self.second if row['npcid'] == '0'), 631)

    def test_records_are_not_deduplicated_by_scene_and_npc(self):
        for rows in (self.first, self.second):
            pairs = collections.Counter((row['scene_id'], row['npcid'])
                                        for row in rows if row['npcid'] != '0')
            repeated = {pair: count for pair, count in pairs.items() if count > 1}
            self.assertTrue(repeated, '(scene_id, npcid) duplicates must be preserved, not collapsed')

    def test_record_index_order_is_original(self):
        for rows in (self.first, self.second):
            per_scene = collections.defaultdict(list)
            for row in rows:
                per_scene[row['scene_id']].append(int(row['record_index']))
            for scene, indexes in per_scene.items():
                self.assertEqual(indexes, list(range(len(indexes))), scene)

    def test_source_record_counts(self):
        self.assertEqual(len(self.first), 1335)
        self.assertEqual(len(self.second), 1344)
        # 1335 and 1344 are record counts of two sources, never a unique NPC total.
        self.assertNotEqual(len({row['npcid'] for row in self.first if row['npcid'] != '0'}),
                            len(self.first))


class QuarantineAndMissingData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())
        cls.records = {(r['entry_index'], r['record_key']): r for r in Batch(default_batch_dir()).quarantine()}

    def test_quarantine_keys_and_reasons(self):
        self.assertEqual(sorted(self.records), [(1945, 72548), (2954, 2800), (3205, 719), (3205, 4406)])
        for record in self.records.values():
            self.assertFalse(record['native_verified'])
            self.assertTrue(record['reasons'])

    def test_2800_keeps_saved_values_and_is_not_1700(self):
        value = TypedJson.decode(self.records[2954, 2800]['value_under_applied_profile'])
        decoded = {TypedJson.text(key): item for key, item in value.items()}
        self.assertEqual(decoded['法力資質'], 2130)
        self.assertEqual(decoded['法力資質最大值'], 1989)
        ids = {row['client_shape_id'] for row in self.batch.rows('pet_aptitudes.csv')}
        self.assertNotIn('2800', ids)
        profile = self.batch.manifest()['profiles']['2954']
        self.assertEqual(profile['applied_bounds'], profile['saved_bounds'])
        self.assertNotIn(7979, profile['applied_bounds'])

    def test_72548_original_bytes_are_preserved(self):
        value = TypedJson.decode(self.records[1945, 72548]['value_under_applied_profile'])
        self.assertEqual(value[0].hex(), 'c2f9a448a7a4c34dc5e9c5e784')
        self.assertNotIn('72548', {row['client_shape_id'] for row in self.batch.rows('items.csv')})

    def test_quarantined_skills_are_excluded(self):
        ids = {row['skill_id'] for row in self.batch.rows('pet_skills.csv')}
        self.assertTrue({'719', '4406'}.isdisjoint(ids))

    def test_missing_aptitudes_are_not_zero_filled(self):
        missing = {row['client_shape_id'] for row in self.batch.rows('pet_aptitude_missing.csv')}
        self.assertEqual(missing, {'3010', '4021', '4022'})
        present = {row['client_shape_id'] for row in self.batch.rows('pet_aptitudes.csv')}
        self.assertTrue(missing.isdisjoint(present))
        for row in self.batch.typed('pet_aptitudes.csv'):
            values = [value for key, value in row.items() if '資質' in key]
            self.assertTrue(any(value != 0 for value in values), row['client_shape_id'])


class AmbiguousSkillNames(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())

    def _ids(self, name):
        return sorted(int(row['skill_id']) for row in self.batch.rows('pet_skill_name_matches.csv')
                      if row['skill_name_raw'] == name)

    def test_high_level_hit_keeps_229_and_255(self):
        self.assertEqual(self._ids('高級命中'), [229, 255])

    def test_final_level_hit_keeps_329_and_355(self):
        self.assertEqual(self._ids('終級命中'), [329, 355])

    def test_ambiguity_is_flagged_not_silently_resolved(self):
        rows = [row for row in self.batch.rows('pet_skill_name_matches.csv')
                if row['skill_name_raw'] in ('高級命中', '終級命中')]
        self.assertEqual(len(rows), 4)
        for row in rows:
            self.assertEqual(row['match_count'], '2')
            self.assertEqual(row['ambiguous'], 'true')


class FormatAndTextFidelity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.batch = Batch(default_batch_dir())

    def test_core_csvs_reencode_byte_identically(self):
        for name in CORE_CSVS:
            data = self.batch.read_bytes(name)
            self.assertFalse(data.startswith(b'\xef\xbb\xbf'), name)
            rows = list(csv.reader(io.StringIO(self.batch.csv_text(name), newline='')))
            sink = io.StringIO(newline='')
            writer = csv.writer(sink, quoting=csv.QUOTE_ALL, lineterminator='\n')
            writer.writerows(rows)
            self.assertEqual(sink.getvalue().encode('utf-8'), data, name)

    def test_maps_csvs_keep_crlf_minimal_quoting(self):
        for name in MAP_NPC_CSVS:
            data = self.batch.read_bytes(name)
            rows = list(csv.reader(io.StringIO(self.batch.csv_text(name), newline='')))
            sink = io.StringIO(newline='')
            writer = csv.writer(sink, quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
            writer.writerows(rows)
            self.assertEqual(sink.getvalue().encode('utf-8'), data, name)

    def test_traditional_text_is_preserved(self):
        text = ''.join(self.batch.csv_text(name) for name in CORE_CSVS + MAP_NPC_CSVS)
        for needle in ('終級命中', '高級命中', '時空石', '天魔返生術', '地魔返生術'):
            self.assertIn(needle, text)
        for forbidden in ('宠物', '资质', '技能书', '装备店', '时空石'):
            self.assertNotIn(forbidden, text)

    def test_manifest_hashes_cover_every_file(self):
        manifest = self.batch.manifest()
        for name, spec in manifest['files'].items():
            data = self.batch.read_bytes(name)
            self.assertEqual(len(data), spec['bytes'], name)
            import hashlib
            self.assertEqual(hashlib.sha256(data).hexdigest(), spec['sha256'], name)


if __name__ == '__main__':
    unittest.main()
