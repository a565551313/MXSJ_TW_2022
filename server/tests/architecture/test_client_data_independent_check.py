"""Regression tests for the independent client-data boundary check.

These assert that the *evidence* still holds and that the tool does not upgrade
weak evidence into a confirmation. They are not an acceptance certificate for
game data: nothing here compares against a running native client.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]

def _load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

verify = _load('verify_client_data_boundaries',
               'server/tools/verify_client_data_boundaries.py')
EVIDENCE = ROOT / 'server/docs/catalog/client_data_independent_check.json'


class InputIntegrityTests(unittest.TestCase):
    """The investigation must not have touched the client archive or key database."""

    def test_archive_and_keydb_match_recorded_hashes(self):
        saved = json.loads(EVIDENCE.read_text())
        self.assertEqual(
            hashlib.sha256((ROOT / 'data/script.fls').read_bytes()).hexdigest(),
            saved['inputs']['archive_sha256'])
        self.assertEqual(
            hashlib.sha256((ROOT / 'tools/decompiler/script_fls_keys.json')
                           .read_bytes()).hexdigest(),
            saved['inputs']['key_database_sha256'])

    def test_nothing_written_to_game_data(self):
        game_data = ROOT / 'server/game_data'
        self.assertTrue(game_data.is_dir())
        # The check must not publish candidates as configuration.
        for path in game_data.rglob('*'):
            self.assertFalse(path.is_file() and path.stat().st_size > 0
                             and 'client_data_independent' in path.name)


class StructuralDiscriminatorTests(unittest.TestCase):
    """The non-linguistic discriminators must behave as the report claims."""

    @classmethod
    def setUpClass(cls):
        cls.arc = verify.Archive()

    def test_1115_saved_boundary_yields_unmapped_opcodes_and_a_skipped_const(self):
        code = self.arc.decode(1115)
        _, indices, contiguous = verify.dict_build_loop_signature(code, 803, 842)
        self.assertFalse(contiguous)
        self.assertIn(176, set(range(indices[0], indices[-1] + 1)) - set(indices))
        unmapped = verify.unmapped_opcode_positions(code, 825, 831)
        self.assertTrue(unmapped, 'saved boundary should produce unmapped opcodes')

    def test_1115_candidate_boundary_is_fully_mapped_and_contiguous(self):
        bounds = list(self.arc.keys['1115']['bounds'])
        bounds[0] = 828
        code = self.arc.decode(1115, bounds)
        ratio, indices, contiguous = verify.dict_build_loop_signature(code, 803, 842)
        self.assertEqual(ratio, 1.0)
        self.assertTrue(contiguous)
        self.assertEqual(verify.unmapped_opcode_positions(code, 825, 831), [])

    def test_3205_fault_is_a_wrong_key_not_a_wrong_boundary(self):
        meta = self.arc.keys['3205']
        bounds = list(meta['bounds'])
        saved = self.arc.decode(3205)
        cc_len = int.from_bytes(saved[18:22], 'little')
        bad = verify.unmapped_opcode_positions(saved, 22, 22 + cc_len)
        self.assertGreater(len(bad), 2000)
        # Every bad position sits inside segment 1, which no boundary move can fix.
        self.assertEqual(min(bad), bounds[0])
        self.assertLess(max(bad), bounds[1] + 1)

    def test_3205_key_218_beats_every_other_key_byte(self):
        meta = self.arc.keys['3205']
        bounds, keys = list(meta['bounds']), list(meta['keys'])
        lo, hi = bounds[0] + 3, bounds[1] - 3
        scored = []
        for key in range(256):
            trial = list(keys)
            trial[1] = key
            dec = self.arc.decode(3205, bounds, trial)
            scored.append((len(verify.unmapped_opcode_positions(dec, lo, hi)), key))
        scored.sort()
        self.assertEqual(scored[0], (0, 218))
        self.assertGreater(scored[1][0], 0, 'the winner must be unique at zero')

    def test_std_walk_accepts_fixed_3205_and_rejects_saved(self):
        meta = self.arc.keys['3205']
        bounds = list(meta['bounds'])
        keys = list(meta['keys'])
        keys[1] = 218
        self.assertTrue(verify.std_walk_clean(
            self.arc.transpile(3205, bounds, keys)['code']))
        with self.assertRaises(ValueError):
            list(verify.std_instructions(
                self.arc.transpile(3205, bounds, list(meta['keys']))))


class EvidenceClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads(EVIDENCE.read_text())
        cls.by_key = {(f['entry_index'], f['record_id_or_index']): f
                      for f in cls.saved['findings']}

    def test_report_is_reproducible(self):
        arc = verify.Archive()
        corpus = arc.corpus()
        result3205 = verify.verify_3205_key(arc)
        autofight = result3205['autofightlist']
        fresh = [
            verify.verify_text_candidate(arc, corpus, 1945, 0, 259583, 10424),
            verify.verify_text_candidate(arc, corpus, 1945, 3, 1038307, 71700),
            verify.verify_1115(arc),
            verify.verify_2242(arc, autofight),
            verify.verify_item_72548(arc, corpus),
            verify.scan_boundary_for_string(arc, corpus, 2027, 2, 16241, 36, 60,
                                            2600, "DATA[2600]['address']"),
            verify.scan_boundary_for_string(arc, corpus, 2027, 3, 21747, 8, 60,
                                            4011, "DATA[4011]['maySkillLst'][3]"),
            verify.scan_boundary_for_string(arc, corpus, 1698, 0, 461, 78, 240,
                                            10004, 'DATA[10004]'),
            result3205['finding'],
        ]
        self.assertEqual(fresh, self.saved['findings'])

    def test_four_original_candidates_are_confirmed_with_independent_evidence(self):
        expected = {
            (1945, 10424): ('confirmed_extraction_bug', 259583),
            (1945, 71700): ('confirmed_extraction_bug', 1038307),
            (1115, 2910): ('confirmed_extraction_bug', 828),
            (2242, 16): ('confirmed_extraction_bug', 264),
        }
        for key, (classification, boundary) in expected.items():
            item = self.by_key[key]
            self.assertEqual(item['classification'], classification, key)
            self.assertEqual(item['candidate_boundary'], boundary, key)

    def test_two_text_candidates_have_boundary_free_cross_entry_witnesses(self):
        keydb = json.loads((ROOT / 'tools/decompiler/script_fls_keys.json').read_text())
        own_keys = keydb['1945']['keys']
        for record in (10424, 71700):
            witnesses = self.by_key[(1945, record)]['evidence'][
                'corroborated_by_independent_entries']
            self.assertTrue(witnesses, record)
            for witness in witnesses:
                # A witness is only useful if the run does not straddle a boundary there.
                self.assertIsNotNone(witness['xor_segment'], witness)
            # At least one witness must be an unrelated entry with unrelated keys.
            self.assertTrue(any(w['entry_index'] != 1945 and w['entry_keys'] != own_keys
                                for w in witnesses), record)

    def test_416_is_corroborated_by_an_independent_table_not_by_adjacency(self):
        evidence = self.by_key[(2242, 16)]['evidence']
        self.assertIn(416, evidence['petskill_AUTOFIGHTLIST'])
        self.assertNotIn(64605, evidence['petskill_AUTOFIGHTLIST'])
        self.assertEqual(evidence['other_entries_containing_int_64605'], [])
        self.assertEqual(evidence['petskill_entry'], 3205)

    def test_item_72548_is_a_source_value_found_under_multiple_key_sets(self):
        evidence = self.by_key[(1945, 72548)]['evidence']
        self.assertEqual(self.by_key[(1945, 72548)]['classification'],
                         'confirmed_source_value')
        self.assertGreaterEqual(len(evidence['distinct_key_sets']), 2)
        self.assertEqual(self.by_key[(1945, 72548)]['candidate_value'],
                         '雙人坐騎體驗\\x84')

    def test_newly_resolved_2027_fields_end_on_the_saved_boundary(self):
        for record, boundary_index, saved in ((2600, 2, 16277), (4011, 3, 21755)):
            item = self.by_key[(2027, record)]
            self.assertEqual(item['classification'], 'confirmed_extraction_bug')
            self.assertEqual(item['old_boundary'], saved)
            data_start = item['payload_offset']
            data_len = len(bytes.fromhex(item['original_bytes_hex']))
            self.assertEqual(data_start + data_len, saved,
                             'fault must terminate exactly on the saved boundary')

    def test_1698_is_not_confirmed_because_cp950_is_not_sufficient(self):
        """Negative control: many valid-CP950 offsets must NOT yield a confirmation."""
        item = self.by_key[(1698, 10004)]
        evidence = item['evidence']
        self.assertEqual(item['classification'], 'candidate')
        self.assertIsNone(item['candidate_boundary'])
        self.assertGreater(len(evidence['cp950_clean_solutions']), 1)
        self.assertEqual(evidence['corroborated_solutions'], [])


class PetTableDifferenceTests(unittest.TestCase):
    def test_difference_is_classified_legitimate_and_not_merged(self):
        saved = json.loads(EVIDENCE.read_text())
        diff = saved['pet_table_difference']
        self.assertEqual(diff['classification'], 'legitimate_table_difference')
        self.assertEqual(diff['only_in_mxpetdata'], [5106, 5107])
        self.assertEqual(diff['only_in_petdata'], [])
        self.assertEqual(diff['petdata_2027_count'], 135)
        self.assertEqual(diff['mxpetdata_1115_count'], 137)
        self.assertNotEqual(diff['id_4024_petdata'], diff['id_4024_mxpetdata'])
        self.assertEqual(diff['id_2910_petdata'], diff['id_2910_mxpetdata'])


class CsvAdmissionTests(unittest.TestCase):
    def test_isolation_list_is_present_and_non_empty(self):
        saved = json.loads(EVIDENCE.read_text())
        self.assertTrue(saved['csv_admission']['must_be_isolated'])
        self.assertTrue(saved['csv_admission']['not_recoverable_this_round'])
        self.assertTrue(saved['csv_admission']['missing_server_side_authority'])

    def test_native_loader_is_recorded_as_statically_blocked(self):
        saved = json.loads(EVIDENCE.read_text())
        self.assertEqual(saved['native_loader_status']['static_analysis'], 'blocked')
        self.assertEqual(saved['native_loader_status']['pkgimport_va'], '0x00457C20')


if __name__ == '__main__':
    unittest.main()
