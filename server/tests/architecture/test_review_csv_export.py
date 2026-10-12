"""Pinned review export tests. Passing these does not prove native decoding."""
import csv
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('export_review_csv', ROOT/'server/tools/export_review_csv.py')
export = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(export)


class EncodingAndSafetyTests(unittest.TestCase):
    def test_lossless_nested_bytes_and_container_types(self):
        original = {3: (b'\x84\xff', [None, False, 1, '文字']), (2, b'x'): {b'n': b''}}
        result = export.restore(json.loads(json.dumps(export.lossless(original))))
        self.assertEqual(original, result)
        self.assertIs(type(result[3]), tuple)
        self.assertIs(type(result[3][1]), list)

    def test_lossless_rejects_unsupported_type_and_duplicate_keys(self):
        with self.assertRaises(ValueError):
            export.lossless(1.5)
        with self.assertRaises(ValueError):
            export.restore({'dict': [[1, 'a'], [1, 'b']]})

    def test_csv_preserves_newlines_quotes_markup_and_formula_strings(self):
        raw = '=1+2,"quoted"\n#R繁體字\t$level*10\r\n'
        data = export.encode_csv([('id', 'int'), ('description', 'str'), ('flag', 'bool')], [[1, raw, False]])
        self.assertEqual(list(csv.reader(io.StringIO(data.decode())))[1], ['1', raw, 'false'])
        self.assertFalse(data.startswith(b'\xef\xbb\xbf'))

    def test_csv_rejects_bad_width_type_and_control_character(self):
        for row in [[1], [True, 'ok'], [1, 'bad\x00']]:
            with self.subTest(row=row), self.assertRaises(ValueError):
                export.encode_csv([('id', 'int'), ('name', 'str')], [row])

    def test_text_never_replaces_invalid_cp950_bytes(self):
        with self.assertRaises(ValueError):
            export.text(b'\x84')
        self.assertEqual(export.text('終級命中'.encode('cp950')), '終級命中')

    def test_new_unexpected_schema_and_encoding_anomalies_are_quarantined(self):
        self.assertIn('schema_mismatch', export.classify_record(1945, 1, [b'x', b'y'], {}))
        self.assertIn('encoding_or_control_character', export.classify_record(1945, 1, (b'\x84', b'y'), {}))
        self.assertEqual(export.classify_record(1945, 1, (b'x', b'y'), {}), [])

    def test_whole_record_quarantine_is_policy_not_automatic_text_repair(self):
        row = {b'type': 1, b'name': b'x', b'desc': b'y', b'fpneed': b'0', b'mpneed': b'0', b'hpneed': b'0'}
        self.assertEqual(export.classify_record(3205, 719, row, {(3205, 719): 'unconfirmed'}), ['unconfirmed'])

    def test_output_protects_production_and_nonempty_paths(self):
        for path in [ROOT, ROOT/'data/new', ROOT/'tools/new', ROOT/'server/game_data/new',
                     ROOT/'.git/new', ROOT/'server/src/new']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                export.write_batch(path, {'test': b'x'})
        with tempfile.TemporaryDirectory() as tmp:
            export.write_batch(tmp, {'test': b'original'})
            with self.assertRaises(ValueError):
                export.write_batch(tmp, {'test': b'replacement'})
            self.assertEqual((Path(tmp)/'test').read_bytes(), b'original')

    def test_output_rejects_symlink_into_game_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp)/'linked'
            link.symlink_to(ROOT/'server/game_data', target_is_directory=True)
            with self.assertRaises(ValueError):
                export.write_batch(link, {'test': b'x'})


class RealBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.counts = export.build_batch()
        cls.manifest = json.loads(cls.files['manifest.json'])

    def rows(self, name):
        return list(csv.DictReader(io.StringIO(self.files[name].decode('utf-8'))))

    def test_all_committed_files_are_byte_identical_to_fresh_export(self):
        actual = {p.relative_to(export.DEFAULT_OUT).as_posix() for p in export.DEFAULT_OUT.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(self.files))
        for name, data in self.files.items():
            with self.subTest(name=name):
                self.assertEqual((export.DEFAULT_OUT/name).read_bytes(), data)

    def test_manifest_hashes_cover_all_outputs_except_itself(self):
        self.assertEqual(set(self.manifest['files']), set(self.files)-{'manifest.json'})
        for name, spec in self.manifest['files'].items():
            self.assertEqual(export.sha(self.files[name]), spec['sha256'])
            self.assertEqual(len(self.files[name]), spec['bytes'])
            if name.endswith('.csv'):
                rows = self.rows(name)
                self.assertEqual(len(rows), spec['rows'])
                self.assertEqual(list(rows[0]), [c['name'] for c in spec['columns']])

    def test_source_and_tool_hashes_match_current_files(self):
        for path, digest in {**self.manifest['inputs'], **self.manifest['tool_and_evidence_sha256']}.items():
            self.assertEqual(export.sha((ROOT/path).read_bytes()), digest)
        self.assertFalse(self.manifest['native_verified'])
        self.assertTrue(all(not p['automatic_bytecode_solver_enabled'] for p in self.manifest['profiles'].values()))

    def test_source_counts_and_quarantine_account_for_every_row(self):
        expected = {'1945': (6852, 6851, 1), '2027': (135, 135, 0), '2954': (132, 131, 1), '3205': (581, 579, 2)}
        for index, counts in expected.items():
            spec = self.counts['tables'][index]
            self.assertEqual(tuple(spec[k] for k in ['source_records', 'review_csv_records', 'quarantined_records']), counts)
            self.assertEqual(counts[0], counts[1]+counts[2])

    def test_four_quarantines_retain_original_candidate_values(self):
        quarantines = [json.loads(line) for line in self.files['quarantine.jsonl'].splitlines()]
        by_key = {(r['entry_index'], r['record_key']): r for r in quarantines}
        self.assertEqual(set(by_key), {(1945, 72548), (2954, 2800), (3205, 719), (3205, 4406)})
        item = export.restore(by_key[1945, 72548]['value_under_applied_profile'])
        self.assertEqual(item[0].hex(), 'c2f9a448a7a4c34dc5e9c5e784')
        apt = export.restore(by_key[2954, 2800]['value_under_applied_profile'])
        self.assertEqual(apt['法力資質'.encode('cp950')], 2130)
        self.assertEqual(apt['法力資質最大值'.encode('cp950')], 1989)
        for filename, field, excluded in [('items.csv', 'client_shape_id', {72548}),
                                         ('pet_aptitudes.csv', 'client_shape_id', {2800}),
                                         ('pet_skills.csv', 'skill_id', {719, 4406})]:
            self.assertTrue(excluded.isdisjoint({int(r[field]) for r in self.rows(filename)}))

    def test_missing_aptitude_rows_are_not_zero_filled(self):
        self.assertEqual({int(r['client_shape_id']) for r in self.rows('pet_aptitude_missing.csv')}, {3010, 4021, 4022})
        self.assertTrue({3010, 4021, 4022, 2800}.isdisjoint({int(r['client_shape_id']) for r in self.rows('pet_aptitudes.csv')}))

    def test_pet_skill_child_tables_and_ambiguity_are_preserved(self):
        self.assertEqual(len(self.rows('pet_skill_candidates.csv')), 458)
        self.assertEqual(len(self.rows('pet_required_skills.csv')), 26)
        self.assertEqual(len(self.rows('pet_skill_name_matches.csv')), 145)
        self.assertEqual(self.counts['pet_skill_names'], 143)
        self.assertEqual(self.counts['ambiguous_pet_skill_names'], {'高級命中': [229, 255], '終級命中': [329, 355]})
        pets = {r['client_shape_id'] for r in self.rows('pets.csv')}
        skills = {r['skill_id'] for r in self.rows('pet_skills.csv')}
        self.assertTrue(all(r['client_shape_id'] in pets for r in self.rows('pet_skill_candidates.csv')))
        self.assertTrue(all(r['skill_id'] in skills for r in self.rows('pet_skill_name_matches.csv')))

    def test_overwrites_preserve_both_values_and_source_order(self):
        self.assertEqual((self.counts['skill_write_count'], self.counts['skill_unique_count']), (590, 581))
        rows = self.rows('pet_skill_overwrites.csv')
        self.assertEqual(len(rows), 9)
        self.assertEqual([int(r['write_order']) for r in rows], list(range(352, 361)))
        self.assertEqual(sum(r['identical_values'] == 'false' for r in rows), 1)
        changed = next(r for r in rows if r['identical_values'] == 'false')
        self.assertEqual((changed['skill_id'], changed['old_name'], changed['new_name']), ('4573', '天魔返生術', '地魔返生術'))
        evidence = [json.loads(line) for line in self.files['overwrite_evidence.jsonl'].splitlines()]
        self.assertEqual(len(evidence), 9)
        self.assertEqual(export.restore(evidence[0]['old_value'])[b'name'].decode('cp950'), '天魔返生術')

    def test_item_41052_is_corroborated_candidate_not_original_bad_text(self):
        row = next(r for r in self.rows('items.csv') if r['client_shape_id'] == '41052')
        self.assertEqual(row['name'], '時空石')

    def test_map_sources_record_order_and_zero_ids_are_not_collapsed(self):
        a = self.rows('maps_npcs/npcposdata_records.csv')
        b = self.rows('maps_npcs/minimapnpcpos_pos_records.csv')
        self.assertEqual((len(a), len(b)), (1335, 1344))
        self.assertEqual((sum(r['npcid'] == '0' for r in a), sum(r['npcid'] == '0' for r in b)), (632, 631))
        for name, data in self.files.items():
            if name.startswith('maps_npcs/'):
                self.assertEqual(data, (ROOT/'server/docs/csv_checks/staging'/Path(name).name).read_bytes())

    def test_fresh_process_cli_check(self):
        completed = subprocess.run([sys.executable, '-B', str(ROOT/'server/tools/export_review_csv.py'), '--check'],
                                   cwd=ROOT, text=True, capture_output=True, timeout=60)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['mode'], 'check')


if __name__ == '__main__':
    unittest.main()
