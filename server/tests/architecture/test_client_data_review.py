"""Read-only research regression checks, not game-data acceptance tests."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    'client_data_boundary_review', ROOT / 'server/tools/review_client_data_boundaries.py')
review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(review)


class LiteralReaderTests(unittest.TestCase):
    def test_rejects_calls(self):
        with self.assertRaisesRegex(ValueError, 'unsupported opcode'):
            review.evaluate_literals({'consts': (None,)}, [(0, 131, 0)])

    def test_rejects_underfilled_list(self):
        with self.assertRaisesRegex(ValueError, 'underflow'):
            review.evaluate_literals({'consts': ()}, [(0, 103, 1)])

    def test_rejects_duplicate_keys(self):
        co = {'consts': (b'name', 7)}
        seq = [(0, 104, 0)]
        for _ in range(2):
            seq += [(1, 4, None), (2, 100, 0), (3, 2, None),
                    (4, 100, 1), (5, 60, None)]
        seq.append((6, 90, 0))
        with self.assertRaisesRegex(ValueError, 'duplicate dictionary key'):
            review.evaluate_literals(co, seq)

    def test_invalid_text_preserves_bytes(self):
        self.assertEqual(review.readable(b'\x84')['invalid_cp950_hex'], '84')


class ClientBoundaryReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = review.Review().report()

    def test_report_reproducible(self):
        saved = json.loads((ROOT / 'server/docs/catalog/client_data_boundary_review.json').read_text())
        self.assertEqual(self.result, saved)

    def test_source_files_not_changed(self):
        for relative, field in [
            ('data/script.fls', 'archive_sha256'),
            ('tools/decompiler/script_fls_keys.json', 'key_database_sha256'),
        ]:
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(),
                             self.result[field])

    def test_candidates_stay_unapproved_and_local(self):
        probes = self.result['probes']
        self.assertEqual(len(probes), 4)
        for p in probes:
            self.assertEqual(p['status'], 'candidate_requires_independent_confirmation')
            self.assertEqual(p['count_before'], p['count_after'])
            changes = p.get('changed_keys', p.get('changed_list_indices'))
            self.assertEqual(changes, [p['record_id_or_list_index']])
        self.assertEqual(probes[2]['before'], 2280)
        self.assertEqual(probes[2]['after'], self.result['pet_table_differences']['petdata_2910'])
        self.assertEqual(probes[3]['before'], 64605)
        self.assertEqual(probes[3]['after'], 416)

    def test_unresolved_records_are_disclosed(self):
        baseline = {r['entry_index']: r for r in self.result['baseline']}
        self.assertEqual(len(baseline[1945]['text_errors']), 3)
        self.assertEqual(len(baseline[2027]['text_errors']), 2)
        self.assertEqual(baseline[3205]['status'], 'unresolved')
        self.assertIn('invalid_cp950_hex', self.result['unresolved_item_name']['value'])


if __name__ == '__main__':
    unittest.main()
