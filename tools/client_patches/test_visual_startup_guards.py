"""Regression tests for the v3 module-vs-function None-index startup bug."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_visual_preview as visual
from audit_visual_runtime import extract
base = visual.base


class StartupGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (base.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (base.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.baseline, _ = base.build(cls.source, cls.keys, stage='form-validate')
        cls.output, cls.report = visual.build(cls.source, cls.keys)
        cls.metadata = json.loads(cls.keys)

    def test_actual_module_zero_is_minus_one_not_none(self):
        co = extract(self.source, self.metadata, 4007)
        self.assertEqual(co['consts'][0], -1)
        self.assertIsNone(co['consts'][1])
        body = visual.overlay_invocation(co)
        values = [co['consts'][arg] for _, op, arg in base.normalized(body) if op == 100]
        self.assertEqual(values[0]['name'], b'CRegPanel2_2980')
        self.assertIsNone(values[1])
        self.assertIsNone(values[2])

    def test_none_lookup_not_hardcoded_to_one_either(self):
        co = {'consts': (-1, b'other', {'code': b''}, None)}
        self.assertEqual(base.normalized(visual.overlay_invocation(co, 2)),
                         [(0, 100, 2), (3, 100, 3), (6, 100, 3), (9, 85, None)])

    def test_missing_or_ambiguous_none_is_rejected(self):
        for consts in ((-1, {'code': b''}), (None, {'code': b''}, None)):
            with self.assertRaisesRegex(ValueError, 'exactly one None'):
                visual.overlay_invocation({'consts': consts}, 1)

    def test_actual_artifact_exec_operands_are_none(self):
        root = extract(self.output, self.metadata, 4007)
        seq = base.normalized(root['code'][488:513])
        self.assertEqual(seq[:4], [(0, 100, 41), (3, 100, 1), (6, 100, 1), (9, 85, None)])
        self.assertIsNone(root['consts'][seq[1][2]])
        self.assertIsNone(root['consts'][seq[2][2]])
        self.assertEqual(root['consts'][41]['name'], b'_registration_visual_overlay')

    def test_home_constructor_guard_and_unrelated_spans(self):
        old = dict(base.objects(extract(self.baseline, self.metadata, 337)))['CMainPage/__init__']
        new = dict(base.objects(extract(self.output, self.metadata, 337)))['CMainPage/__init__']
        self.assertEqual(old['code'][:426], new['code'][:426])
        self.assertEqual(old['code'][571:], new['code'][571:])
        seq = base.normalized(new['code'])
        self.assertIn((426, 121, 123), seq)  # import is INSIDE the exception region
        self.assertIn((548, 87, None), seq)
        self.assertIn((549, 110, 19), seq)
        self.assertIn((552, 1, None), seq)
        self.assertIn((556, 71, None), seq)
        self.assertIn((557, 71, None), seq)
        self.assertIn((558, 72, None), seq)
        self.assertIn((560, 110, 8), seq)
        base.valid_code(new, new['code'])

    def test_transition_swaps_only_two_complete_calls(self):
        old = dict(base.objects(extract(self.baseline, self.metadata, 337)))['CMainPage/OnMessage']
        new = dict(base.objects(extract(self.output, self.metadata, 337)))['CMainPage/OnMessage']
        self.assertEqual(new['code'][:215], old['code'][:215])
        self.assertEqual(new['code'][215:238], old['code'][225:238] + old['code'][215:225])
        self.assertEqual(new['code'][238:], old['code'][238:])
        base.valid_code(new, new['code'])

    def test_cli_requires_explicit_candidate_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'candidate'
            proc = subprocess.run([sys.executable, str(visual.HERE / 'build_visual_preview.py'),
                                   '--output-dir', str(output)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('explicit opt-in required', proc.stderr)
            self.assertFalse(output.exists())

    def test_report_calls_this_a_candidate_not_native_success(self):
        self.assertEqual(self.report['kind'], 'registration_visual_preview_v3_1_candidate')
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertEqual(len(self.report['startup_changes']), 4)


if __name__ == '__main__': unittest.main()
