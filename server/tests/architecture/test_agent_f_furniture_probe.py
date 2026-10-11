"""Regression tests for the entry-244 structural/no-solver probe.

These tests validate scan boundaries and evidence separation only. Passing does
not certify the native client loader or choose between unresolved B0 candidates.
"""
import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PROBE_PATH = ROOT / 'server/tools/csv_checks_agent_f/probe65_final.py'


def _load_probe():
    spec = importlib.util.spec_from_file_location('agent_f_probe65_tests', PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


probe = _load_probe()


class CodeRangeTests(unittest.TestCase):
    def test_duoyi_scan_stops_at_derived_code_end_and_rejects_truncation(self):
        from tools.decompiler import batch_decompile as decoder
        mapped_with_arg = next(op for op in decoder.PY25_MAP if op >= 0x5F)
        # Bytes after [2,5) stand for a constant-pool pseudo-op. They are outside
        # co_code and must not be walked.
        payload = bytes([0x00, 0x00, mapped_with_arg, 0x00, 0x00,
                         0xFF, 0x00, 0x00])
        stats = probe.duoyi_opcode_stats(payload, 2, 5)
        self.assertEqual(stats['instruction_count'], 1)
        self.assertEqual(stats['unmapped_count'], 0)
        self.assertEqual(stats['unmapped_positions'], [])
        with self.assertRaisesRegex(ValueError, 'truncated Duoyi instruction'):
            probe.duoyi_opcode_stats(payload, 2, 4)
        with self.assertRaisesRegex(ValueError, 'exceeds payload length'):
            probe.duoyi_opcode_stats(payload, 2, len(payload) + 1)

    def test_constant_pool_pseudo_opcodes_do_not_change_code_statistics(self):
        from tools.decompiler import batch_decompile as decoder
        mapped_with_arg = next(op for op in decoder.PY25_MAP if op >= 0x5F)
        co_code = bytes([mapped_with_arg, 0x12, 0x34, 0x01])
        harmless_pool = bytes([0x00, 0x00, 0x00])
        pseudo_opcode_pool = bytes([0xFF, 0xFF, 0xFF])
        start = 3
        end = start + len(co_code)
        left = b'\x00' * start + co_code + harmless_pool
        right = b'\x00' * start + co_code + pseudo_opcode_pool
        self.assertEqual(probe.duoyi_opcode_stats(left, start, end),
                         probe.duoyi_opcode_stats(right, start, end))
        self.assertEqual(probe.duoyi_opcode_stats(right, start, end)['instruction_count'], 2)

    def test_root_code_range_is_derived_from_raw_marshal_structure(self):
        archive = probe.Archive()
        evidence = probe.root_code_evidence(
            archive,
            bounds=[18289, 36511, 54797, 73114],
            keys=[233, 11, 132, 105, 246],
        )
        span = evidence['span']
        self.assertEqual((span['code_start'], span['code_end']), (22, 47423))
        self.assertEqual(span['code_length'], len(evidence['root']['code']))
        self.assertEqual(evidence['decoded'][span['code_start']:span['code_end']],
                         evidence['root']['code'])
        self.assertEqual(evidence['stats']['unmapped_count'], 0)


class DataAndConstantPoolSeparationTests(unittest.TestCase):
    def test_targeted_literal_reader_accepts_none_but_rejects_other_name_loads(self):
        def instruction(opcode, argument=None):
            if opcode >= 90:
                argument = 0 if argument is None else argument
                return bytes([opcode, argument & 0xff, (argument >> 8) & 0xff])
            return bytes([opcode])

        # An unrelated prior STORE_NAME bounds the assignment segment. The DATA
        # value is constructed only from literal dict opcodes and LOAD_NAME None.
        code = b''.join([
            instruction(104, 0), instruction(90, 0),       # BUILD_MAP; ORDER
            instruction(104, 0), instruction(4),            # root DATA; DUP_TOP
            instruction(101, 2), instruction(2),            # LOAD_NAME None; ROT_TWO
            instruction(100, 0), instruction(60),           # DATA[b'field'] = None
            instruction(90, 1),                             # STORE_NAME DATA
        ])
        module = {
            'code': code,
            'names': (b'ORDER', b'DATA', b'None'),
            'consts': (b'field',),
        }
        report = probe.extract_data_assignment(module)
        self.assertEqual(report['value'], {b'field': None})
        self.assertTrue(report['assignment_complete'])
        self.assertFalse(report['module_verified'])
        self.assertEqual(report['writes'], 1)
        self.assertEqual(report['overwrites'], ())

        unsafe = dict(module)
        unsafe['names'] = (b'ORDER', b'DATA', b'factory')
        with self.assertRaisesRegex(ValueError, 'unsupported LOAD_NAME'):
            probe.extract_data_assignment(unsafe)

    def test_data_field_text_and_non_data_pool_are_reported_separately(self):
        archive = probe.Archive()
        result = probe.audit_candidate(
            archive,
            [18289, 36511, 54797, 73114],
            [233, 11, 132, 105, 246],
        )
        data = result['data_audit']
        pool = result['constant_pool_audit']
        self.assertTrue(result['data_report']['assignment_complete'])
        self.assertFalse(result['data_report']['module_verified'])
        self.assertEqual(result['data_report']['verification_scope'],
                         'bounded DATA assignment segment only')
        self.assertEqual(result['data_report']['writes'], 233)
        self.assertEqual(result['data_report']['overwrites'], ())
        self.assertEqual(result['data_report']['all_dictionary_overwrites'], ())
        self.assertEqual(data['record_count'], 233)
        self.assertEqual(data['field_count'], 20)
        self.assertEqual(data['data_byte_value_count'], 543)
        self.assertEqual(data['byte_values_by_field'], {
            'desc': 164, 'layer': 140, 'name': 233, 'pre': 1, 'stablepath': 5,
        })
        self.assertEqual(data['cp950_failure_count'], 0)
        self.assertEqual(data['control_value_count'], 0)
        self.assertEqual(pool['code_object_count'], 25)
        self.assertEqual(pool['byte_constant_occurrences'], 539)
        self.assertEqual(pool['data_value_matched_occurrences'], 403)
        self.assertEqual(pool['additional_pool_value_occurrences'], 136)
        self.assertEqual(pool['all_pool_issues'], [])
        self.assertIn('not proof of constant-source provenance',
                      pool['classification_note'])

    def test_two_no_solver_candidates_are_retained_when_data_differs(self):
        archive = probe.Archive()
        rows, candidates = probe.scan_first_boundary(archive)
        accepted = {item['bounds'][0]: item for item in candidates}
        self.assertEqual(set(accepted), {18289, 18290})
        self.assertEqual(len(rows), probe.SCAN_B0_END - probe.SCAN_B0_START)
        left = accepted[18289]['data_report']['value']
        right = accepted[18290]['data_report']['value']
        differences = probe.compare_data_tables(left, right)
        self.assertEqual([(item['record'], item['field']) for item in differences],
                         [(29251, 'pre')])
        self.assertIsInstance(left[29251][b'pre'], bytes)
        self.assertEqual(right[29251][b'pre'], 153)
        self.assertTrue(all(item['data_report']['assignment_complete'] for item in candidates))
        self.assertTrue(all(not item['data_report']['module_verified'] for item in candidates))
        self.assertTrue(all(item['raw']['stats']['unmapped_count'] == 0
                            for item in candidates))


if __name__ == '__main__':
    unittest.main()
