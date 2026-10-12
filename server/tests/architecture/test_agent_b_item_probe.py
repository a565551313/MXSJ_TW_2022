"""Regression checks for Agent B's machine-readable boundary evidence."""
import importlib.util
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PROBE_PATH = ROOT / 'server/tools/agent_b_item_probe.py'
EVIDENCE_PATH = ROOT / 'server/docs/csv_checks/agent_b_probe.json'


def _load_probe():
    spec = importlib.util.spec_from_file_location('agent_b_item_probe_tests', PROBE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(spec.name, None)
        raise
    return module


probe = _load_probe()


class Item41052CandidateEvidenceTests(unittest.TestCase):
    def test_locate_accepts_an_explicit_candidate_boundary(self):
        bounds = [259624, 519228, 778759, 1038363]
        needle = bytes.fromhex('aec9aac5a5db')
        hits = probe.locate(1945, needle, bounds=bounds)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0], {
            'payload_offset': 778758,
            'segment': 2,
            'key': 50,
            'raw_hex': '9cf89bf494ea',
            'decoded_hex': 'aec9aac5a5db',
        })

    def test_json_keeps_the_cross_corroborated_candidate_not_native_verified(self):
        evidence = json.loads(EVIDENCE_PATH.read_text(encoding='utf-8'))
        row = evidence['records']['1945/DATA/41052']
        candidate = row['candidate_boundary_evidence']
        self.assertEqual(candidate['status'],
                         'cross_corroborated_candidate_not_native_verified')
        self.assertFalse(candidate['native_loader_confirmed'])
        self.assertEqual(candidate['saved_boundary'], 778764)
        self.assertEqual(candidate['candidate_boundary'], 778759)
        self.assertEqual(candidate['candidate_name'], '時空石')
        self.assertEqual(candidate['changed_record_ids_vs_saved_raw_decode'], [41052])
        locations = candidate['cross_entry_byte_evidence']
        self.assertEqual(locations['entry_1182_saved_profile'][0]['payload_offset'], 863430)
        self.assertEqual(locations['entry_4924_saved_profile'][0]['payload_offset'], 125988)
        self.assertEqual(locations['entry_1182_saved_profile'][0]['decoded_hex'],
                         'aec9aac5a5db')
        self.assertEqual(locations['entry_4924_saved_profile'][0]['decoded_hex'],
                         'aec9aac5a5db')

    def test_72548_invalid_cp950_bytes_remain_intact_and_quarantined(self):
        evidence = json.loads(EVIDENCE_PATH.read_text(encoding='utf-8'))
        name = evidence['records']['1945/DATA/72548'][0]
        self.assertFalse(name['cp950_ok'])
        self.assertIsNone(name['text_if_clean'])
        self.assertEqual(name['decoded_hex'], 'c2f9a448a7a4c34dc5e9c5e784')
        self.assertEqual(name['payload_locations'][0]['raw_hex'],
                         'aa91cc20cfccab25ad81ad8fec')
        self.assertEqual(name['payload_locations'][0]['payload_offset'], 1100453)
        self.assertEqual(name['first_error_payload_offset'], 1100465)


if __name__ == '__main__':
    unittest.main()
