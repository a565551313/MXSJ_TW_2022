"""CSV survey regression, not validation against the native game loader."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location('csv_survey', ROOT/'server/tools/survey_csv_readiness.py')
survey = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(survey)


class CsvSurveyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = survey.survey()
        cls.tables = {(r['entry_index'], r['table']): r for r in cls.result['tables']}

    def test_reproducible_report_and_scope(self):
        saved = json.loads((ROOT/'server/docs/catalog/csv_readiness_survey.json').read_text())
        self.assertEqual(self.result, saved)
        self.assertEqual(self.result['entries_selected'], 33)
        self.assertEqual(self.result['tables_requested'], 48)
        self.assertEqual(self.result['tables_recovered'], 38)

    def test_decode_success_does_not_hide_controls(self):
        self.assertEqual(survey.inspect_text(b'hello\x17')[0]['kind'], 'control_character')
        self.assertEqual(survey.inspect_text(b'\x84')[0]['kind'], 'encoding')
        self.assertEqual(survey.inspect_text(b'line\r\nnext\ttext'), [])
        self.assertEqual(self.tables[17, 'DATA']['flagged_keys'], [55010])

    def test_row_level_isolation_not_silent_field_dropping(self):
        for ident, total, flagged in [(1945, 6852, 3), (2027, 135, 2), (2954, 132, 1), (1301, 104, 1)]:
            row = self.tables[ident, 'DATA']
            self.assertEqual(row['count'], total)
            self.assertEqual(row['flagged_row_count'], flagged)
            self.assertEqual(row['not_flagged_by_these_checks'], total-flagged)
            self.assertTrue(row['schema_checked'])

    def test_semantic_warnings_survive_valid_encoding(self):
        self.assertEqual(self.tables[2954, 'DATA']['flagged_keys'], [2800])
        self.assertEqual(self.tables[2409, 'DATA']['flagged_keys'], [7, 8, 9])
        self.assertEqual(self.tables[246, 'GEM2EQUIP']['issues'][0]['kind'], 'name_difference')
        self.assertEqual(self.tables[2242, 'SKILLIDLST']['issues'][0]['approved'], False)

    def test_global_store_supported_without_execution(self):
        co = {'code': bytes([100, 0, 0, 97, 0, 0]), 'names': (b'DATA',), 'consts': ({7: b'name'},)}
        self.assertEqual(survey.extract(co, 'DATA'), {7: b'name'})
        co['code'] = bytes([131, 0, 0, 97, 0, 0])
        with self.assertRaisesRegex(ValueError, 'unsupported opcode'):
            survey.extract(co, 'DATA')

    def test_reference_checks_and_failures_disclosed(self):
        self.assertEqual(self.result['cross_checks']['aptitude_pet_ids']['pets_without_aptitude'], [3010, 4021, 4022])
        self.assertEqual(self.result['cross_checks']['children_unresolved_shape_refs'], [])
        for ident in [3205, 454, 3075, 2338]:
            row = self.tables[ident, 'DATA']
            self.assertNotIn('count', row)
            self.assertIn('error', row)


if __name__ == '__main__':
    unittest.main()
