"""Regression tests for the Agent E map/NPC handover.

These tests pin the *independently reproducible* parts of
`server/docs/csv_checks/AGENT_E.md` (merged in PR #16) using the repository
tool `server/tools/map_npc_reproduction.py`. They do not validate anything
against the native game loader; the candidate framings stay candidates.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location(
    'map_npc_reproduction', ROOT / 'server/tools/map_npc_reproduction.py')
repro = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repro)


def _build(with_scan=False):
    archive = repro.Archive()
    evidence = repro.build_evidence(archive, with_scan=with_scan)
    return archive, evidence


class InputPinningTests(unittest.TestCase):
    """The checks are meaningless if the inputs drift silently."""

    @classmethod
    def setUpClass(cls):
        # with the archive-wide scan: this mirrors the committed evidence file
        cls.archive, cls.evidence = _build(with_scan=True)

    def test_input_hashes_match_the_handover_records(self):
        inputs = self.evidence['inputs']
        self.assertTrue(inputs['archive']['matches_expected'])
        self.assertTrue(inputs['key_database']['matches_expected'])
        self.assertEqual(inputs['archive']['sha256'], repro.EXPECTED_ARCHIVE_SHA256)
        self.assertEqual(inputs['key_database']['sha256'], repro.EXPECTED_KEYDB_SHA256)

    def test_evidence_file_matches_regeneration(self):
        saved = json.loads(
            (ROOT / 'server/docs/csv_checks/agent_e_reproduction.json').read_text())
        current = self.evidence
        self.assertEqual(current, saved,
                         'evidence JSON drifted; regenerate with '
                         'python3 server/tools/map_npc_reproduction.py '
                         '--out server/docs/csv_checks/agent_e_reproduction.json')

    def test_evidence_declares_candidate_status_not_loader_verified(self):
        self.assertIn('not_native_loader_verified',
                      self.evidence['tool']['status'])


class CandidateBoundsTests(unittest.TestCase):
    """The five main entries under candidate (or verified saved) parameters."""

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()
        cls.verdicts = cls.evidence['verifications']
        cls.analyses = {}
        for idx in (400, 1301, 1799, 2601, 2804, 4897):
            bounds = repro.CANDIDATE_BOUNDS.get(idx) or cls.archive.keydb[str(idx)]['bounds']
            cls.analyses[idx] = repro.EntryAnalysis(cls.archive, idx, bounds)

    def test_all_candidate_parameter_sets_verify(self):
        for entry, sets in self.verdicts.items():
            label = 'candidate' if entry != '1870' else 'saved'
            if 'candidate' not in sets and entry != '1870':  # entry 400: saved == correct
                label = 'saved'
            self.assertTrue(sets[label]['pass'],
                            f'entry {entry} {label}: {sets[label]}')

    def test_mapdata_rebuilds_104_rows_and_1071(self):
        data = self.analyses[1301].table(b'DATA')
        self.assertEqual(len(data), 104)
        self.assertTrue(all(type(k) is int for k in data))
        self.assertEqual(data[1071][b'name'], '加洛法師師道殿'.encode('cp950'))
        self.assertEqual((data[1071][b'w'], data[1071][b'h']), (1588, 1220))
        self.assertEqual(self.analyses[1301].table(b'MAP_ASCRIPTION'),
                         {1039: 1039, 1040: 1039, 1041: 1039,
                          1073: 1073, 1074: 1073, 1075: 1073})
        self.assertEqual(repro.text_errors(data), [])

    def test_sceneid2name_57_tuple_rows(self):
        data = self.analyses[400].table(b'DATA')
        self.assertEqual(len(data), 57)
        self.assertTrue(all(type(v) is tuple and len(v) == 4 for v in data.values()))
        self.assertEqual(data[1071][0], '加洛法師師道殿'.encode('cp950'))
        self.assertEqual(data[1071][1:], (2302, 1500, 2000))

    def test_alias_table_55_rows_texttable_clean(self):
        data = self.analyses[1799].table(b'DATA')
        self.assertEqual(len(data), 55)
        self.assertEqual(repro.text_errors(data), [])
        self.assertEqual(data['個人心法教師'.encode('cp950')], '元靈遊仙'.encode('cp950'))
        self.assertEqual(data['天選使者'.encode('cp950')], '明威'.encode('cp950'))
        self.assertEqual(self.analyses[1799].co['name'], b'<module>')

    def test_npcposdata_structure_counts_duplicates_kept(self):
        data = self.analyses[2601].table(b'DATA')
        records = [r for recs in data.values() for r in recs]
        self.assertEqual(len(data), 430)
        self.assertEqual(len(records), 1335)
        self.assertTrue(all(len(r) == 14 for r in records))
        self.assertEqual(sum(1 for r in records if r[2] == 0), 632)
        pairs = repro.npc_pair_index_flat(data)
        self.assertEqual(len(pairs), 665)
        self.assertEqual(multiplicity(pairs), {1: 653, 2: 3, 4: 5, 6: 4})
        # the 12 multi-record pairs are list-valued, never collapsed
        self.assertEqual(sum(1 for v in pairs.values() if len(v) > 1), 12)
        stats = self.evidence['npc_structure']['npcposdata_2601']
        self.assertEqual(stats['records_with_npcid_zero'], 632)
        self.assertEqual(stats['records'], 1335)

    def test_minimapnpcpos_pos_wenzi_and_no_data(self):
        analysis = self.analyses[2804]
        self.assertFalse(analysis.has_table(b'DATA'),
                         'the module has no DATA; asking for it was the survey bug')
        with self.assertRaises(KeyError):
            analysis.table(b'DATA')
        pos = analysis.table(b'DATA_POS')
        wenzi = analysis.table(b'DATA_WENZI')
        records = [r for inner in pos.values() for recs in inner.values() for r in recs]
        self.assertEqual(len(pos), 434)
        self.assertEqual(len(records), 1344)
        self.assertEqual(sum(1 for r in records if r[2] == 0), 631)
        self.assertEqual(len(wenzi), 165)
        self.assertEqual(sum(len(v) for v in wenzi.values()), 287)
        pairs = repro.npc_pair_index_nested(pos)
        self.assertEqual(len(pairs), 676)
        self.assertEqual(multiplicity(pairs), {1: 665, 2: 2, 4: 5, 6: 4})
        # the 11 multi-record pairs are list-valued, never collapsed
        self.assertEqual(sum(1 for v in pairs.values() if len(v) > 1), 11)
        self.assertEqual(analysis.co['consts'][544], '打漁老張'.encode('cp950'))

    def test_cross_scene_same_npcid_is_common_and_kept(self):
        reuse = self.evidence['semantics_recheck']['npcid_reuse']
        self.assertEqual(reuse['npcposdata']['distinct_npcids'], 336)
        self.assertEqual(reuse['npcposdata']['npcids_in_multiple_scenes'], 106)
        self.assertEqual(reuse['minimapnpcpos']['distinct_npcids'], 343)
        self.assertEqual(reuse['minimapnpcpos']['npcids_in_multiple_scenes'], 107)


class WrongParameterRejectionTests(unittest.TestCase):
    """Saved / delivered framings must fail LOUDLY - and never pass merely
    because the shifted text stays valid Chinese (cp950)."""

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()
        cls.verdicts = cls.evidence['verifications']
        cls.analyses = {}
        for idx in (1301, 1799, 2601, 2804, 4897):
            cls.analyses[idx] = repro.EntryAnalysis(
                cls.archive, idx, cls.archive.keydb[str(idx)]['bounds'])

    def test_delivered_wrong_map_key_is_detected(self):
        """The delivered artifact: boundary one byte early -> a text constant
        steals the place of integer key 1071."""
        analysis = repro.EntryAnalysis(self.archive, 1301, repro.ALT_1301_DELIVERED_SOLVER)
        data = analysis.table(b'DATA')
        non_int_keys = [k for k in data if not isinstance(k, int)]
        self.assertEqual(non_int_keys, ['兔坦卡門陵墓'.encode('cp950')])
        self.assertNotIn(1071, data)
        # the integer is left stranded in the const pool
        stranded = [analysis.co['consts'][i] for i in analysis.stranded_const_indices()]
        self.assertIn(1071, stranded)
        # the stranded record is the 加洛法師師道殿 row, and the stray key text
        # is the *name* of scene 1053 (which is why it looked plausible)
        self.assertEqual(data[non_int_keys[0]][b'name'], '加洛法師師道殿'.encode('cp950'))
        candidate_data = repro.EntryAnalysis(
            self.archive, 1301, repro.CANDIDATE_BOUNDS[1301]).table(b'DATA')
        self.assertEqual(candidate_data[1053][b'name'], non_int_keys[0])
        # the strict verdict rejects it even though every byte is valid cp950:
        # the mechanical checks pass and ONLY the witness fails
        verdict = self.verdicts['1301']['delivered_solver']
        self.assertFalse(verdict['pass'])
        self.assertEqual(repro.text_errors(data), [])
        self.assertTrue(verdict['checks']['cp950_clean']['ok'])
        self.assertEqual(verdict['witness_failures'], ['catalog'])

    def test_saved_db_bounds_fail_bytecode_for_1301_and_2601(self):
        v1301 = self.verdicts['1301']['saved']
        self.assertFalse(v1301['pass'])
        self.assertFalse(v1301['checks']['module_bytecode']['ok'])
        self.assertIn('unmapped custom opcode', v1301['checks']['module_bytecode']['detail'])
        v2601 = self.verdicts['2601']['saved']
        self.assertFalse(v2601['pass'])
        self.assertFalse(v2601['checks']['module_bytecode']['ok'])

    def test_wrong_slot3_cannot_pass_on_valid_chinese_2804(self):
        """saved slot3 -> const[544] = 蓮７導姒, perfectly valid cp950, 434+165
        rows, whole walk consumed: every mechanical check passes. Only the
        cross-table witness rejects it."""
        saved = list(self.archive.keydb['2804']['bounds'])
        bounds = repro.CANDIDATE_BOUNDS[2804][:3] + [saved[3]]
        analysis = repro.EntryAnalysis(self.archive, 2804, bounds)
        self.assertIsNone(analysis.error)
        self.assertEqual(analysis.co['consts'][544], '蓮７導姒'.encode('cp950'))
        self.assertEqual(len(analysis.table(b'DATA_POS')), 434)
        self.assertEqual(len(analysis.table(b'DATA_WENZI')), 165)
        self.assertEqual(repro.text_errors(analysis.table(b'DATA_POS')), [])
        verdict = self.verdicts['2804']['saved_slot3_only']
        self.assertFalse(verdict['pass'])
        self.assertEqual(verdict['witness_failures'], ['tables_and_constants'])
        mechanical = {k: v for k, v in verdict['checks'].items()
                      if not k.startswith('witness:')}
        self.assertTrue(all(v['ok'] for v in mechanical.values()))

    def test_wrong_slot3_cannot_pass_on_valid_structure_2601(self):
        """saved slot3 -> 谷雨鎮商人 gets npcid 4810 (exists in no table);
        structure and text still pass. Witness pins 4764 via entry 2804."""
        saved = list(self.archive.keydb['2601']['bounds'])
        bounds = repro.CANDIDATE_BOUNDS[2601][:3] + [saved[3]]
        analysis = repro.EntryAnalysis(self.archive, 2601, bounds)
        self.assertEqual(analysis.co['consts'][179], 4810)
        fisherman = [r for r in analysis.table(b'DATA')[1003]
                     if r[0] == '谷雨鎮商人'.encode('cp950')]
        self.assertIn(4810, [r[2] for r in fisherman])
        verdict = self.verdicts['2601']['saved_slot3_only']
        self.assertFalse(verdict['pass'])
        self.assertEqual(verdict['witness_failures'], ['structure_and_fisherman'])

    def test_saved_alias_bounds_corrupt_two_constants_and_co_name(self):
        analysis = self.analyses[1799]
        errors = repro.text_errors(analysis.table(b'DATA'))
        self.assertEqual({e['raw_hex'] for e in errors},
                         {'a4b8c646b9dc3acf', 'a4d1bfefa8197c1a'})
        self.assertNotEqual(analysis.co['name'], b'<module>')
        self.assertFalse(self.verdicts['1799']['saved']['pass'])

    def test_saved_4897_bounds_break_the_wenzi_literal(self):
        analysis = self.analyses[4897]
        failed = {f['name']: f['reason'] for f in analysis.failed_stores}
        self.assertIn(b'DATA_WENZI', failed)
        self.assertIn('unsupported opcode', failed[b'DATA_WENZI'])
        self.assertFalse(self.verdicts['4897']['saved']['pass'])


class ParameterComparisonTests(unittest.TestCase):
    """Saved/alternate vs candidate: the exact field/reference changes."""

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()
        cls.pc = cls.evidence['parameter_comparisons']

    def test_1301_changes_are_exactly_the_1071_key(self):
        diff = self.pc['1301']['delivered_solver']['table_changes']['DATA']
        self.assertEqual(len(diff['changed_keys']), 0)
        self.assertEqual([k['key'] for k in diff['added_keys']], [1071])
        self.assertEqual([k['key'] for k in diff['removed_keys']], ['兔坦卡門陵墓'])
        self.assertIn('加洛法師師道殿', diff['added_keys'][0]['after'])
        self.assertIn('加洛法師師道殿', diff['removed_keys'][0]['before'])

    def test_1799_changes_are_the_two_constants_and_co_name(self):
        row = self.pc['1799']['saved']
        diff = row['table_changes']['DATA']
        self.assertEqual(len(diff['changed_keys']), 1)
        self.assertEqual(diff['changed_keys'][0]['key'], '個人心法教師')
        self.assertIn('元靈遊仙', diff['changed_keys'][0]['after'])
        self.assertEqual([k['key'] for k in diff['added_keys']], ['天選使者'])
        self.assertEqual(row['co_name']['candidate'], '<module>')
        refs = {r['const_index']: r for r in row['reference_changes']}
        self.assertEqual(refs[31]['candidate'], '元靈遊仙')
        self.assertEqual(refs[74]['candidate'], '天選使者')
        self.assertEqual(refs[31]['before']['invalid_cp950_hex'], 'a4b8c646b9dc3acf')
        self.assertEqual(refs[74]['before']['invalid_cp950_hex'], 'a4d1bfefa8197c1a')

    def test_2601_slot3_change_is_one_record_in_scene_1003(self):
        row = self.pc['2601']['saved_slot3_only']
        diff = row['table_changes']['DATA']
        self.assertEqual([c['key'] for c in diff['changed_keys']], [1003])
        refs = row['reference_changes']
        self.assertEqual(refs[0]['before'], 4810)
        self.assertEqual(refs[0]['candidate'], 4764)

    def test_2601_all_saved_cannot_even_evaluate_data(self):
        self.assertEqual(self.pc['2601']['saved']['table_changes'],
                         {'DATA': 'only under candidate parameters'})

    def test_2804_saved_changes_are_exactly_two_scenes(self):
        row = self.pc['2804']['saved']
        self.assertEqual([c['key'] for c in row['table_changes']['DATA_POS']['changed_keys']],
                         [1020])
        self.assertEqual([c['key'] for c in row['table_changes']['DATA_WENZI']['changed_keys']],
                         [1022])
        refs = row['reference_changes']
        self.assertEqual(refs[0]['before'], '蓮７導姒')
        self.assertEqual(refs[0]['candidate'], '打漁老張')

    def test_4897_saved_loses_only_the_wenzi_table(self):
        self.assertEqual(self.pc['4897']['saved']['table_changes'],
                         {'DATA_WENZI': 'only under candidate parameters'})


class CrossTableWitnessTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()
        cls.wit = cls.evidence['cross_table_witnesses']

    def test_1071_association_reproduced(self):
        m = self.wit['mapdata_vs_sceneid2name']
        self.assertTrue(m['key_1071_in_mapdata'])
        self.assertEqual(m['minimap_keys_in_mapdata'], 57)
        self.assertEqual(m['minimap_keys'], 57)
        self.assertEqual(m['name_mismatches'], [])
        self.assertEqual(m['data_1071']['name'], '加洛法師師道殿')

    def test_pair_join_list_valued_both_semantics(self):
        j = self.wit['npcposdata_vs_minimapnpcpos']
        self.assertEqual((j['pairs_a'], j['pairs_b'], j['common_pairs']),
                         (665, 676, 664))
        # order-insensitive comparison reproduces the report's 656/8 split
        self.assertEqual(j['multiset_identical'], 656)
        self.assertEqual(len(j['content_differences']), 8)
        # sequence-sensitive comparison shows 9 more order-only differences
        self.assertEqual(j['sequence_identical'], 647)
        self.assertEqual(len(j['order_only_differences']), 9)
        self.assertEqual(j['only_in_a'], [[1179, 5020]])
        self.assertEqual(len(j['only_in_b']), 12)
        for detail in j['content_difference_detail']:
            self.assertTrue(detail['npcposdata'])
            self.assertTrue(detail['minimapnpcpos'])

    def test_2804_slot2_is_decided_by_the_4897_witness(self):
        sibling = self.wit['minimapnpcpos_vs_test_sibling']
        self.assertEqual(sibling['wenzi_identical_scenes'], 165)
        self.assertEqual(sibling['wenzi_scenes_2804'], 165)
        self.assertEqual(sibling['wenzi_scenes_4897'], 165)
        join = sibling['pair_join_vs_4897']
        self.assertEqual(join['common_pairs'], 674)
        self.assertEqual(join['sequence_identical'], 674)

    def test_alias_corroboration_and_single_mismatch_kept(self):
        a = self.wit['alias_table_vs_npcposdata']
        self.assertEqual(a['records_with_alias_in_1799'], 175)
        self.assertEqual(a['aliases_used'], 36)
        self.assertEqual(a['real_name_set_and_alias_in_1799'], 71)
        self.assertEqual(a['alias_realname_agreements'], 70)
        self.assertEqual(len(a['alias_realname_mismatches']), 1)
        self.assertEqual(a['alias_realname_mismatches'][0]['alias'], '藥店')
        self.assertEqual(a['alias_realname_mismatches'][0]['record_says'], '裝備店老闆')
        self.assertEqual(a['real_name_set_but_alias_not_in_1799'], 22)
        b = self.wit['alias_table_vs_minimapnpcpos']
        self.assertEqual(b['records_with_alias_in_1799'], 178)
        self.assertEqual(b['alias_realname_agreements'], 73)

    def test_fisher_name_attestation(self):
        f = self.wit['fisher_name_attestation']
        self.assertEqual(f['const544_of_2804'], '打漁老張')
        self.assertEqual(f['record_2601_1020_4229'][0][0], '打漁老張')
        self.assertEqual(f['record_2601_1020_4229'][0][2], 4229)
        self.assertEqual(f['record_2804_1020_4229'][0][0], '打漁老張')


class SemanticsRecheckTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()
        cls.sem = cls.evidence['semantics_recheck']

    def test_second_column_stays_unresolved_with_reproduced_numbers(self):
        col = self.sem['sceneid2name_second_column']
        self.assertEqual(col['status'], 'unresolved_meaning_not_established')
        self.assertEqual(col['rows_where_related_id_differs_from_key'], 17)
        self.assertEqual(col['related_id_that_is_also_a_catalog_key'], 43)
        self.assertEqual(col['of_those_name_agreements'], 40)
        self.assertEqual(col['those_keys'][:12], list(range(1061, 1073)))

    def test_size_frames_are_not_interchangeable(self):
        sizes = self.sem['size_pair_comparison']
        self.assertEqual(sizes['identical'], 0)
        self.assertEqual(len(sizes['axis_transposed']), 38)
        self.assertEqual(len(sizes['different_values']), 19)
        scale = self.sem['coordinate_scale_probe']
        self.assertEqual(scale['status'],
                         'no_single_scale_factor_coordinates_live_in_separate_frames')

    def test_runtime_mutation_is_consumer_side_evidence(self):
        ev = self.evidence['runtime_mutation_static_evidence']
        self.assertEqual(set(ev) - {'_scope'},
                         {'InitTestData', 'GetData', 'GetMapNpcNames', 'DelShenHeNpc'})
        self.assertIn('insert', ev['InitTestData']['names'])
        self.assertIn('DATA_POS', ev['InitTestData']['names'])
        self.assertIn(1054, ev['InitTestData']['first_constants'])
        self.assertIn('IsFreshManServer', ev['GetData']['names'])
        self.assertIn('DelShenHeNpc', ev['GetData']['names'])
        self.assertIn('IsShenHe', ev['DelShenHeNpc']['names'])
        self.assertIn('pre-mutation', ev['_scope'])

    def test_1870_stays_unresolved_with_corrupt_name_disclosed(self):
        entry = self.evidence['entry_1870']
        self.assertIn('unresolved', entry['note'])
        corrupt = [n for n in entry['co_names']
                   if isinstance(n, str) and not n.isidentifier()]
        self.assertEqual(corrupt, ['D~ChhiIha^ehcEeNpc'])
        self.assertIn('npcposdata', entry['co_names'])
        self.assertIn('minimapnpcpos', entry['co_names'])
        self.assertIn('DelShenHeNpc', entry['co_names'])


class ReaderRuleTests(unittest.TestCase):
    """The LOAD_NAME 'None' rule is a narrow, explicit reader feature."""

    # custom opcodes: LOAD_NAME(0xAA), LOAD_CONST(0x8F), BUILD_LIST(0xCA),
    # STORE_NAME(0x98) all take a 2-byte argument (custom HAVE_ARGUMENT = 0x5F)
    def test_load_name_none_placeholder_accepted(self):
        co = {'code': bytes([0xAA, 0x00, 0x00, 0x8F, 0x00, 0x00,
                             0xCA, 0x02, 0x00, 0x98, 0x01, 0x00]),
              # LOAD_NAME names[0]; LOAD_CONST 7; BUILD_LIST 2; STORE_NAME DATA
              'names': (b'None', b'DATA'), 'consts': (7,)}
        tables, failed = repro.extract_assignments(co)
        self.assertEqual(tables[b'DATA']['value'], [None, 7])
        self.assertEqual(failed, [])

    def test_any_other_name_load_is_rejected(self):
        co = {'code': bytes([0xBB, 0x00, 0x00, 0xAA, 0x00, 0x00, 0xCA, 0x02, 0x00,
                             0x98, 0x01, 0x00]),
              # BUILD_MAP 0; LOAD_NAME names[0]; BUILD_LIST 2; STORE_NAME names[1]
              'names': (b'ver2mask', b'DATA'), 'consts': ()}
        tables, failed = repro.extract_assignments(co)
        self.assertNotIn(b'DATA', tables)
        self.assertEqual(len(failed), 1)
        self.assertIn('only the exact None placeholder', failed[0]['reason'])

    def test_store_global_supported(self):
        co = {'code': bytes([0x8F, 0x00, 0x00, 0xC4, 0x00, 0x00]),
              'names': (b'DATA',), 'consts': ({7: 8},)}
        tables, _failed = repro.extract_assignments(co)
        self.assertEqual(tables[b'DATA']['value'], {7: 8})
        self.assertEqual(tables[b'DATA']['store_op'], 'STORE_GLOBAL')

    def test_duplicate_keys_are_never_silently_overwritten(self):
        # DATA = {}; DATA[1] = 'a'; DATA[1] = 'b'  (real emitter idiom:
        # DUP_TOP / LOAD_CONST value / ROT_TWO / LOAD_CONST key / STORE_SUBSCR)
        row1 = [0x30, 0x8F, 0x01, 0x00, 0x5A, 0x8F, 0x00, 0x00, 0x05]
        row2 = [0x30, 0x8F, 0x02, 0x00, 0x5A, 0x8F, 0x00, 0x00, 0x05]
        code = bytes([0xBB, 0x00, 0x00] + row1 + row2 + [0x98, 0x00, 0x00])
        co = {'code': code, 'names': (b'DATA',), 'consts': (1, b'a', b'b')}
        tables, failed = repro.extract_assignments(co)
        self.assertNotIn(b'DATA', tables)
        self.assertIn('duplicate dictionary key', failed[0]['reason'])

    def test_calls_and_imports_are_rejected(self):
        # LOAD_CONST f; LOAD_CONST x; CALL_FUNCTION 1; STORE_NAME DATA
        code = bytes([0x8F, 0x00, 0x00, 0x8F, 0x01, 0x00, 0xDA, 0x01, 0x00,
                      0x98, 0x00, 0x00])
        co = {'code': code, 'names': (b'DATA',), 'consts': (None, None)}
        _tables, failed = repro.extract_assignments(co)
        self.assertIn('unsupported opcode', failed[0]['reason'])


class StagingCsvTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.archive, cls.evidence = _build()

    def test_committed_csvs_match_regeneration(self):
        staging = ROOT / 'server/docs/csv_checks/staging'
        analyses = {k: repro.EntryAnalysis(
            self.archive, k,
            repro.CANDIDATE_BOUNDS.get(k) or self.archive.keydb[str(k)]['bounds'])
            for k in (400, 1301, 1799, 2601, 2804)}
        with tempfile.TemporaryDirectory() as tmp:
            written = repro.write_staging_csvs(analyses, tmp, archive=self.archive)
            for name in written:
                regenerated = (Path(tmp) / name).read_bytes()
                committed = (staging / name).read_bytes()
                self.assertEqual(regenerated, committed,
                                 f'{name} drifted; regenerate via '
                                 'python3 server/tools/map_npc_reproduction.py '
                                 '--csv-dir server/docs/csv_checks/staging')

    def test_agreement_csv_keeps_every_pair_and_marks_unresolved(self):
        rows = (ROOT / 'server/docs/csv_checks/staging/npc_2601_vs_2804_agreement.csv'
                ).read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(rows), 1 + 664 + 1 + 12)  # header + common + a-only + b-only
        body = rows[1:]
        self.assertEqual(sum('content_difference' in r for r in body), 8)
        self.assertEqual(sum('identical_multiset_different_order' in r for r in body), 9)

    def test_record_csvs_keep_zero_npcid_and_multiplicities(self):
        rows = (ROOT / 'server/docs/csv_checks/staging/npcposdata_records.csv'
                ).read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(rows), 1 + 1335)
        zero = sum(1 for r in rows[1:] if r.split(',')[4] == '0')
        self.assertEqual(zero, 632)
        pair_counts = {}
        for r in rows[1:]:
            cols = r.split(',')
            if cols[4] == '0':
                continue  # npcid==0 records are not pair-joinable
            pair_counts[(cols[0], cols[4])] = pair_counts.get((cols[0], cols[4]), 0) + 1
        self.assertEqual(len([p for p in pair_counts if pair_counts[p] > 1]), 12)


def multiplicity(pairs):
    hist = {}
    for records in pairs.values():
        hist[len(records)] = hist.get(len(records), 0) + 1
    return hist


if __name__ == '__main__':
    unittest.main()
