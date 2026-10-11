"""Regression tests for the independent client-data boundary check.

These assert that the *evidence* still holds and that the tool does not upgrade
weak evidence into a confirmation. They are not an acceptance certificate for
game data: nothing here compares against a running native client.

REVISED after coordinator review. Two of these tests exist specifically because
the previous revision was wrong and nothing caught it:

  * ``STORE_GLOBAL`` was never counted, so a module-level ``DATA`` table was
    reported as absent.  -> PetskillStoreOpcodeTests
  * The entry-3205 key was picked by "fewest unmapped opcodes", an
    alignment-only metric that ranks keys[1]=218 first even though 218 cannot
    build the table at all.  -> KeySelectionIsNotAlignmentTests
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

_CACHE: dict = {}


def _archive():
    if 'arc' not in _CACHE:
        _CACHE['arc'] = verify.Archive()
    return _CACHE['arc']


def _corpus():
    if 'corpus' not in _CACHE:
        _CACHE['corpus'] = _archive().corpus()
    return _CACHE['corpus']


def _petskill():
    """verify_3205 is the expensive part; run it once for the whole suite.

    Returns (finding, data_keys, winning_variant_row). The comparison table lives
    on the finding's ``evidence``; per-variant measurements live on the row.
    """
    if 'petskill' not in _CACHE:
        _CACHE['petskill'] = verify.verify_3205(_archive())
    return _CACHE['petskill']


def _evidence():
    return _petskill()[0]['evidence']


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
        saved = json.loads(EVIDENCE.read_text())
        self.assertEqual(saved['status'],
                         'independent_check_research_evidence_not_approved_game_data')
        self.assertTrue(game_data.exists())
        for item in game_data.rglob('*'):
            if item.name in ('itemdata.json', 'petdata.json', 'petskill.json'):
                self.fail(f'independent check must not write {item}')


class PetskillStoreOpcodeTests(unittest.TestCase):
    """Regression: STORE_GLOBAL (std 97) must be recognised, not just STORE_NAME."""

    def test_py25_map_emits_store_global(self):
        from tools.decompiler import batch_decompile as decoder
        self.assertEqual(decoder.PY25_MAP[0xC4], 97)
        self.assertIn(97, verify.STORE_OPS)
        self.assertIn(90, verify.STORE_OPS)

    def test_3205_assigns_data_and_icon_mapping_through_store_global(self):
        _finding, _keys, row = _petskill()
        stores = row['module_level_stores']
        self.assertIn('DATA', stores,
                      'the previous revision reported DATA as absent from this entry')
        self.assertIn('ICON_MAPPING', stores)
        self.assertEqual(stores['DATA'][0]['std_opcode'], 97)
        self.assertEqual(stores['ICON_MAPPING'][0]['std_opcode'], 97)
        self.assertEqual(stores['DATA'][0]['opcode'], 'STORE_GLOBAL')

    def test_module_level_store_set_includes_store_name_assignments(self):
        _finding, _keys, row = _petskill()
        stores = row['module_level_stores']
        by_kind = {}
        for name, entries in stores.items():
            by_kind.setdefault(entries[0]['opcode'], set()).add(name)
        self.assertEqual(by_kind['STORE_GLOBAL'], {'DATA', 'ICON_MAPPING'})
        self.assertIn('AUTOFIGHTLIST', by_kind['STORE_NAME'])
        self.assertIn('ShieldShortCutSkills', by_kind['STORE_NAME'])


class KeySelectionIsNotAlignmentTests(unittest.TestCase):
    """Regression: alignment alone cannot pick the segment key."""

    def test_alignment_ties_the_withdrawn_218_with_the_correct_152(self):
        _finding, _keys, row = _petskill()
        by_label = {v['label']: v for v in _evidence()['variants']}
        self.assertEqual(by_label['superseded_218_proposal']
                         ['metric_alignment_unmapped_opcodes'], 0)
        self.assertEqual(by_label['coordinator_D_candidate']
                         ['metric_alignment_unmapped_opcodes'], 0)
        self.assertIn('superseded_218_proposal',
                      _evidence()['alignment_metric_winner']['tied_labels'])

    def test_218_aligns_but_cannot_build_the_table(self):
        _finding, _keys, row = _petskill()
        by_label = {v['label']: v for v in _evidence()['variants']}
        self.assertEqual(by_label['superseded_218_proposal']['instruction_alignment'],
                         'clean')
        self.assertEqual(by_label['superseded_218_proposal']['literal_build'], 'failed')
        self.assertIn('unsupported opcode 80', by_label['superseded_218_proposal']['error'])

    def test_only_the_152_variants_reconstruct_data_and_they_agree(self):
        _finding, keys, row = _petskill()
        self.assertEqual(_evidence()['feasibility_winners'],
                         ['coordinator_D_candidate', 'D_key_with_saved_bounds'])
        self.assertTrue(_evidence()['feasible_variants_agree_on_table'])
        self.assertEqual(keys[0], 101)
        self.assertEqual(len(set(keys)), 581)

    def test_saved_key_database_is_rejected_by_the_instruction_walk(self):
        _finding, _keys, row = _petskill()
        by_label = {v['label']: v for v in _evidence()['variants']}
        self.assertEqual(by_label['saved_key_database']['instruction_alignment'], 'failed')
        self.assertGreater(by_label['saved_key_database']
                           ['metric_alignment_unmapped_opcodes'], 2000)


class PetskillLiteralBuildTests(unittest.TestCase):
    def test_data_rebuilds_to_581_ids_under_strict_stack_rules(self):
        _finding, _keys, row = _petskill()
        self.assertEqual(row['literal_build'], 'ok')
        self.assertEqual(row['unique_data_keys'], 581)
        self.assertEqual(row['store_subscr_count'], 4130)

    def test_duplicate_keys_are_recorded_not_silently_dropped(self):
        _finding, _keys, row = _petskill()
        detail = row['duplicate_detail']
        self.assertEqual(row['duplicate_key_count'], 9)
        self.assertEqual(sorted(d['key'] for d in detail),
                         [4236, 4573, 4574, 4575, 4576, 4577, 4578, 4579, 4581])
        for d in detail:
            self.assertIn('offset', d)
            self.assertIn('store_order', d)
            self.assertIn('previous_name', d)
            self.assertIn('new_name', d)
            self.assertIn('records_identical', d)
        orders = [d['store_order'] for d in detail]
        self.assertEqual(orders, sorted(orders), 'store order must be monotonically '
                                                 'recorded so overwrite direction is known')

    def test_exactly_one_duplicate_changes_the_record(self):
        _finding, _keys, row = _petskill()
        changed = [d for d in row['duplicate_detail'] if not d['records_identical']]
        self.assertEqual(len(changed), 1)
        self.assertEqual(changed[0]['key'], 4573)
        self.assertEqual((changed[0]['previous_name'], changed[0]['new_name']),
                         ('天魔返生術', '地魔返生術'))


class PetskillRelationTests(unittest.TestCase):
    def test_the_three_skill_tables_are_mutually_consistent(self):
        saved = json.loads(EVIDENCE.read_text())
        rel = saved['petskill_relations']
        self.assertTrue(rel['SKILLIDLST_subset_of_petskill_DATA'])
        self.assertEqual(rel['SKILLIDLST_missing_from_DATA'], [])
        self.assertTrue(rel['ICON_MAPPING_values_subset_of_DATA'])
        self.assertEqual(rel['ICON_MAPPING_values_missing'], [])
        self.assertEqual(rel['petskill_DATA_unique_ids'], 581)

    def test_416_is_a_key_of_the_master_table(self):
        _finding, keys, _row = _petskill()
        self.assertIn(416, set(keys))
        self.assertNotIn(64605, set(keys))


class StructuralDiscriminatorTests(unittest.TestCase):
    """The non-linguistic discriminators must behave as the report claims."""

    def test_1115_saved_boundary_yields_unmapped_opcodes_and_a_skipped_const(self):
        code = _archive().decode(1115)
        _, indices, contiguous = verify.dict_build_loop_signature(code, 803, 842)
        self.assertFalse(contiguous)
        self.assertIn(176, set(range(indices[0], indices[-1] + 1)) - set(indices))
        self.assertTrue(verify.unmapped_opcode_positions(code, 825, 831),
                        'saved boundary should produce unmapped opcodes')

    def test_1115_candidate_boundary_is_fully_mapped_and_contiguous(self):
        bounds = list(_archive().keys['1115']['bounds'])
        bounds[0] = 828
        code = _archive().decode(1115, bounds)
        ratio, indices, contiguous = verify.dict_build_loop_signature(code, 803, 842)
        self.assertEqual(ratio, 1.0)
        self.assertTrue(contiguous)
        self.assertEqual(verify.unmapped_opcode_positions(code, 825, 831), [])

    def test_3205_fault_is_a_wrong_key_not_a_wrong_boundary(self):
        arc = _archive()
        bounds = arc.keys['3205']['bounds']
        saved = arc.decode(3205)
        cc_len = int.from_bytes(saved[18:22], 'little')
        bad = verify.unmapped_opcode_positions(saved, 22, 22 + cc_len)
        self.assertGreater(len(bad), 2000)
        # Every bad position sits inside segment 1, which no boundary move can fix.
        self.assertEqual(min(bad), bounds[0])
        self.assertLess(max(bad), bounds[1] + 1)

    def test_std_walk_accepts_152_and_rejects_saved(self):
        arc = _archive()
        bounds = list(arc.keys['3205']['bounds'])
        keys = list(arc.keys['3205']['keys'])
        keys[1] = 152
        self.assertTrue(verify.std_walk_clean(arc.transpile(3205, bounds, keys)['code']))
        with self.assertRaises(ValueError):
            list(verify.std_instructions(
                arc.transpile(3205, bounds, list(arc.keys['3205']['keys']))))


class BoundaryTerminatingStringDetectorTests(unittest.TestCase):
    """A string ending exactly on a saved boundary has its tail decoded with the
    neighbouring key whenever that boundary is wrong - including when the result
    is still perfectly valid CP950."""

    def test_detector_flags_all_four_known_text_faults_plus_the_new_one(self):
        saved = json.loads(EVIDENCE.read_text())
        det = saved['boundary_terminating_string_detector']
        flagged = {(e, h['boundary_index'], h['boundary'])
                   for e, hits in det.items() for h in hits}
        self.assertIn(('1945', 0, 259624), flagged)
        self.assertIn(('1945', 2, 778764), flagged)
        self.assertIn(('1945', 3, 1038363), flagged)
        self.assertIn(('2027', 2, 16277), flagged)
        self.assertIn(('2027', 3, 21755), flagged)
        self.assertIn(('1945', 1, 519228), flagged)
        self.assertEqual(len(flagged), 6)

    def test_detector_hits_are_not_all_faults_so_corroboration_is_required(self):
        """bounds[1]=519228 is flagged but correct: 十級強化打造設計圖 has
        boundary-free witnesses in 1182 and 4924. The detector is a filter, not a
        verdict."""
        arc, corpus = _archive(), _corpus()
        value = arc.decode(1945)[519210:519228]
        self.assertEqual(value.decode('cp950'), '十級強化打造設計圖')
        witnesses = []
        for hit in verify.cross_entry_hits(corpus, value):
            if hit['entry_index'] == 1945:
                continue
            if verify.segment_of(arc, hit['entry_index'],
                                 hit['payload_offset'], len(value)) is not None:
                witnesses.append(hit['entry_index'])
        self.assertIn(1182, witnesses)
        self.assertIn(4924, witnesses)

    def test_itemdata_41052_decodes_cleanly_but_wrongly_and_is_corrected(self):
        saved = json.loads(EVIDENCE.read_text())
        by_key = {(x['entry_index'], x['record_id_or_index']): x
                  for x in saved['findings']}
        f = by_key[(1945, 41052)]
        self.assertEqual(f['old_boundary'], 778764)
        self.assertEqual(f['candidate_boundary'], 778759)
        self.assertEqual(f['old_value'], '晉怖肋')
        self.assertEqual(f['candidate_value'], '時空石')
        self.assertEqual(f['classification'], 'confirmed_extraction_bug')
        self.assertEqual(sorted(w['entry_index'] for w in
                                f['evidence']['corroborated_by_independent_entries']),
                         [1182, 4924])
        # 181 offsets decode as valid CP950 across 7 distinct texts; exactly one
        # is corroborated. This is the count that separates the fix from a guess.
        self.assertEqual(f['evidence']['cp950_clean_solution_count'], 181)
        self.assertEqual(len(f['evidence']['distinct_texts']), 7)
        self.assertEqual(f['evidence']['scanned_window'], [778674, 778854])

    def test_the_wrong_41052_text_is_valid_cp950_so_encoding_checks_miss_it(self):
        self.assertTrue(verify.cp950_ok('晉怖肋'.encode('cp950')))

    def test_entry_1698_has_valid_cp950_but_garbled_interior_strings(self):
        saved = json.loads(EVIDENCE.read_text())
        suspects = saved['entry_1698_interior_suspects']
        self.assertEqual(len(suspects), 3)
        valid = [s for s in suspects if s['cp950_valid']]
        self.assertEqual(len(valid), 2,
                         'valid CP950 text that is still visibly corrupted')


class EvidenceClassificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads(EVIDENCE.read_text())
        cls.by_key = {(f['entry_index'], f['record_id_or_index']): f
                      for f in cls.saved['findings']}

    def test_report_is_reproducible(self):
        arc, corpus = _archive(), _corpus()
        f3205, keys, _row = _petskill()
        fresh = [
            verify.verify_text_candidate(arc, corpus, 1945, 0, 259583, 10424),
            verify.verify_text_candidate(arc, corpus, 1945, 3, 1038307, 71700),
            verify.verify_1115(arc),
            verify.verify_2242(arc, set(keys)),
            verify.verify_item_72548(arc, corpus),
            verify.scan_boundary_for_string(arc, corpus, 1945, 2, 778758, 6, 90,
                                            41052, 'DATA[41052][0]'),
            verify.scan_boundary_for_string(arc, corpus, 2027, 2, 16241, 36, 60,
                                            2600, "DATA[2600]['address']"),
            verify.scan_boundary_for_string(arc, corpus, 2027, 3, 21747, 8, 60,
                                            4011, "DATA[4011]['maySkillLst'][3]"),
            verify.scan_boundary_for_string(arc, corpus, 1698, 0, 461, 78, 240,
                                            10004, 'DATA[10004]'),
            f3205,
        ]
        self.assertEqual(fresh, self.saved['findings'])

    def test_confirmed_findings_carry_independent_evidence(self):
        expected = {
            (1945, 10424): 259583,
            (1945, 71700): 1038307,
            (1115, 2910): 828,
            (2242, 16): 264,
            (1945, 41052): 778759,
            (2027, 2600): 16264,
            (2027, 4011): 21751,
        }
        for key, boundary in expected.items():
            f = self.by_key[key]
            self.assertEqual(f['classification'], 'confirmed_extraction_bug', key)
            self.assertEqual(f['candidate_boundary'], boundary, key)

    def test_confirmed_text_findings_have_boundary_free_cross_entry_witnesses(self):
        for key in ((1945, 10424), (1945, 71700), (1945, 41052),
                    (2027, 2600), (2027, 4011)):
            f = self.by_key[key]
            witnesses = f['evidence']['corroborated_by_independent_entries']
            self.assertTrue(witnesses, key)
            for w in witnesses:
                self.assertIsNotNone(w['xor_segment'], key)

    def test_416_is_corroborated_by_the_master_table_not_by_adjacency(self):
        f = self.by_key[(2242, 16)]
        self.assertTrue(f['evidence']['candidate_in_petskill_DATA'])
        self.assertFalse(f['evidence']['saved_value_in_petskill_DATA'])
        self.assertEqual(f['evidence']['other_entries_containing_int_64605'], [])

    def test_item_72548_is_a_source_value_found_under_multiple_key_sets(self):
        f = self.by_key[(1945, 72548)]
        self.assertEqual(f['classification'], 'confirmed_source_value')
        self.assertEqual(f['candidate_boundary'], None)
        self.assertGreaterEqual(len(f['evidence']['distinct_key_sets']), 2)

    def test_1698_is_not_confirmed_because_cp950_is_not_sufficient(self):
        f = self.by_key[(1698, 10004)]
        self.assertEqual(f['classification'], 'candidate')
        self.assertIsNone(f['candidate_boundary'])
        self.assertGreaterEqual(f['evidence']['cp950_clean_solution_count'], 10)

    def test_every_finding_has_the_fourteen_required_columns(self):
        required = {'entry_index', 'table', 'record_id_or_index', 'field_path',
                    'source_sha256', 'payload_offset', 'original_bytes_hex',
                    'old_boundary', 'candidate_boundary', 'old_value',
                    'candidate_value', 'classification', 'evidence',
                    'remaining_uncertainty'}
        for f in self.saved['findings']:
            self.assertEqual(required, set(f))
        allowed = {'confirmed_extraction_bug', 'confirmed_source_value',
                   'legitimate_table_difference', 'candidate', 'unresolved'}
        for f in self.saved['findings']:
            self.assertIn(f['classification'], allowed)


class PetTableDifferenceTests(unittest.TestCase):
    def test_difference_is_downgraded_to_unexplained_and_not_merged(self):
        diff = json.loads(EVIDENCE.read_text())['pet_table_difference']
        self.assertEqual(diff['classification'],
                         'unexplained_table_difference_presumed_legitimate')
        self.assertEqual(diff['only_in_mxpetdata'], [5106, 5107])
        self.assertEqual(diff['only_in_petdata'], [])
        self.assertEqual(diff['petdata_2027_count'], 135)
        self.assertEqual(diff['mxpetdata_1115_count'], 137)
        self.assertNotEqual(diff['id_4024_petdata'], diff['id_4024_mxpetdata'])
        self.assertEqual(diff['id_2910_petdata'], diff['id_2910_mxpetdata'])


class ErrataTests(unittest.TestCase):
    """The two withdrawn conclusions must be recorded, not quietly overwritten."""

    def test_both_withdrawn_3205_claims_are_recorded(self):
        errata = json.loads(EVIDENCE.read_text())['errata']
        text = ' '.join(e.get('withdrawn', '') for e in errata)
        self.assertIn('no module-level DATA store', text)
        self.assertIn('keys[1] = 218', text)
        self.assertIn('itemdata needs only DATA[72548]', text)

    def test_superseded_218_is_marked_withdrawn_in_the_comparison_table(self):
        _f, _k, row = _petskill()
        v = {x['label']: x for x in _evidence()['variants']}
        self.assertIn('WITHDRAWN', v['superseded_218_proposal']['origin'])
        self.assertIn('coordinator', v['coordinator_D_candidate']['origin'])


class CsvAdmissionTests(unittest.TestCase):
    def test_admission_lists_are_present(self):
        admission = json.loads(EVIDENCE.read_text())['csv_admission']
        self.assertTrue(admission['eligible_for_review_csv'])
        self.assertTrue(admission['must_be_isolated'])
        self.assertTrue(admission['not_admissible_this_round'])
        self.assertTrue(admission['missing_server_side_authority'])

    def test_petskill_data_is_now_admissible_with_duplicates_flagged(self):
        admission = json.loads(EVIDENCE.read_text())['csv_admission']
        joined = ' '.join(admission['eligible_for_review_csv'])
        self.assertIn('3205 petskill DATA (581 ids)', joined)
        self.assertIn('4573', ' '.join(admission['must_be_isolated']))

    def test_itemdata_admission_requires_the_new_41052_fix(self):
        admission = json.loads(EVIDENCE.read_text())['csv_admission']
        self.assertIn('778759', ' '.join(admission['eligible_for_review_csv']))

    def test_native_loader_is_recorded_as_statically_blocked(self):
        saved = json.loads(EVIDENCE.read_text())
        self.assertEqual(saved['native_loader_status']['static_analysis'], 'blocked')
        self.assertEqual(saved['native_loader_status']['pkgimport_va'], '0x00457C20')


if __name__ == '__main__':
    unittest.main()
