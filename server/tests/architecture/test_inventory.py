"""Verify inventory completeness and truthful separation of analysis statuses."""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path
import struct
import unittest

SERVER = Path(__file__).resolve().parents[2]
REPO = SERVER.parent
DOCS = SERVER / 'docs'


class MaterialInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(s) for s in (DOCS/'catalog/script_entries.jsonl').read_text().splitlines()]
        cls.summary = json.loads((DOCS/'catalog/summary.json').read_text())
        cls.specs = json.loads((DOCS/'feature_specs.json').read_text())['features']
        cls.forward = json.loads((DOCS/'catalog/feature_material_map.json').read_text())
        cls.reverse = [json.loads(s) for s in (DOCS/'catalog/entry_feature_map.jsonl').read_text().splitlines()]

    def test_all_archive_entries_present_once(self):
        data = (REPO / self.summary['archive']).read_bytes()
        count = struct.unpack_from('<I', data, 4)[0]
        self.assertEqual(len(self.rows), count)
        self.assertEqual({r['entry_index'] for r in self.rows}, set(range(count)))
        self.assertEqual(hashlib.sha256(data).hexdigest(), self.summary['archive_sha256'])

    def test_summary_matches_records(self):
        for field, summary_key in [('current_check','current_checks'), ('path_quality','path_quality'),
                                   ('path_origin','path_origin'), ('heuristic_kind','heuristic_kinds')]:
            self.assertEqual(dict(collections.Counter(r[field] for r in self.rows)), self.summary[summary_key])
        self.assertEqual(sum(r['historical_filename_differs'] for r in self.rows), self.summary['historical_filename_changes'])

    def test_failed_and_missing_names_not_claimed_checked(self):
        for row in self.rows:
            status = row['current_check']
            if status == 'marshal_transpiled_filename_checked':
                self.assertTrue(row['current_filename'])
                self.assertEqual(row['path_origin'], 'current_archive')
            else:
                self.assertIn(status, {'unverified','marshal_transpiled_no_filename'})
                self.assertIsNone(row['current_filename'])
                self.assertEqual(row['path_origin'], 'historical_fallback')
            self.assertEqual(row['semantic_review'], 'not_reviewed_in_this_pass')

    def test_feature_owners_and_sources_exist(self):
        owners = {m['module'] for m in json.loads((DOCS/'source_map.json').read_text())['modules']}
        ids = {r['entry_index'] for r in self.rows}
        maps = {f['feature_id']: f for f in self.forward}
        self.assertEqual(set(maps), {f['feature_id'] for f in self.specs})
        for spec in self.specs:
            self.assertIn(spec['owner_module'], owners)
            self.assertTrue(set(maps[spec['feature_id']]['entry_indices']) <= ids)
            self.assertTrue(set(spec['primary_entries']) <= set(maps[spec['feature_id']]['entry_indices']))
            self.assertTrue((DOCS/'features'/f"{spec['feature_id']}.md").is_file())
            self.assertEqual(spec['interface_status'], 'design_only_not_typed_or_frozen')

    def test_forward_reverse_indexes_agree(self):
        expected = collections.defaultdict(set)
        for feature in self.forward:
            for idx in feature['entry_indices']:
                expected[idx].add(feature['feature_id'])
        self.assertEqual({r['entry_index'] for r in self.reverse}, {r['entry_index'] for r in self.rows})
        for row in self.reverse:
            self.assertEqual(set(row['feature_ids']), expected.get(row['entry_index'], set()))

    def test_unmapped_material_remains_visible(self):
        mapped = sum(bool(r['feature_ids']) for r in self.reverse)
        unmapped = len(self.reverse) - mapped
        report = (DOCS/'SUBSYSTEMS.md').read_text()
        self.assertIn(f'{mapped} 个不同条目', report)
        self.assertIn(f'{unmapped} 个尚未映射', report)
        self.assertEqual(mapped + unmapped, self.summary['entry_count'])

    def test_feature_card_links_exist(self):
        for spec in self.specs:
            module = SERVER/'src/mxsj_server/modules'/spec['owner_module']
            self.assertTrue((module/'FEATURES.md').exists())
            self.assertIn(spec['feature_id'], (module/'FEATURES.md').read_text())
            self.assertTrue((module/'design/README.md').exists())


if __name__ == '__main__':
    unittest.main()
