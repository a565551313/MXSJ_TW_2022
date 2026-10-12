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

    def home_methods(self):
        old = dict(base.objects(extract(self.baseline, self.metadata, 337)))
        new = dict(base.objects(extract(self.output, self.metadata, 337)))
        return old, new

    def instruction_meaning(self, co, at, op, arg):
        if op == 100:
            arg = visual.semantic(co['consts'][arg])
        elif op in visual.NAME_OPS:
            arg = co['names'][arg]
        elif op in visual.LOCAL_OPS:
            arg = co['varnames'][arg]
        return op, arg

    def test_home_caption_is_independent_of_register(self):
        _, new = self.home_methods()
        constructor = new['CMainPage/__init__']
        self.assertNotIn(b'register', constructor['names'])
        start, end = self.report['details']['homepage']['caption_span']
        self.assertEqual(end, len(constructor['code']))
        self.assertFalse(any(op == 107 for _, op, _ in base.normalized(constructor['code'][start:end])))
        self.assertEqual({constructor['names'][arg] for _, op, arg in base.normalized(constructor['code']) if op == 107},
                         {b'misc', b'main', b'cfg'})
        self.assertFalse(any(op == 107 and new['']['names'][arg] == b'register'
                             for _, op, arg in base.normalized(new['']['code'])))

    def test_click_contains_the_only_registration_import_and_no_legacy_url(self):
        _, new = self.home_methods()
        co = new['CMainPage/OnMessage']
        start, end = self.report['details']['homepage']['click_span']
        imports = [(at, co['names'][arg]) for at, op, arg in base.normalized(co['code']) if op == 107]
        registration = [at for at, name in imports if name == b'register']
        self.assertEqual(len(registration), 1)
        self.assertTrue(start <= registration[0] < end)
        fragment = base.normalized(co['code'][start:end])
        names = {co['names'][arg] for _, op, arg in fragment if op in visual.NAME_OPS}
        self.assertTrue({b'register', b'Show', b'Exception'} <= names)
        self.assertFalse({b'OpenUrl', b'gameurl', b'GetData', b'Save', b'net', b'loginin'} & names)

    def test_surviving_instructions_preserve_operands_and_jump_destinations(self):
        old, new = self.home_methods()
        for path, start, end, report_key in (
                ('CMainPage/__init__', 426, 575, 'caption_span'),
                ('CMainPage/OnMessage', 90, 263, 'click_span')):
            before, after = old[path], new[path]
            new_end = self.report['details']['homepage'][report_key][1]
            delta = new_end - end
            def moved(at):
                self.assertFalse(start < at < end)
                return at + delta if at >= end else at
            actual = {at: (op, arg) for at, op, arg in base.normalized(after['code'])}
            for at, op, arg in base.normalized(before['code']):
                if start <= at < end:
                    continue
                new_at = moved(at)
                new_op, new_arg = actual[new_at]
                self.assertEqual(op, new_op)
                if op in visual.ABS_JUMPS:
                    self.assertEqual(moved(arg), new_arg)
                elif op in visual.REL_JUMPS:
                    self.assertEqual(moved(at+3+arg), new_at+3+new_arg)
                else:
                    self.assertEqual(self.instruction_meaning(before, at, op, arg),
                                     self.instruction_meaning(after, new_at, new_op, new_arg))
            base.valid_code(after, after['code'])

    def test_msgid_two_branch_alone_enters_new_click_fragment(self):
        _, new = self.home_methods()
        co = new['CMainPage/OnMessage']
        seq = base.normalized(co['code'])
        # The original msgid==2 dispatch is immediately before our start=90.
        self.assertEqual([(at, self.instruction_meaning(co, at, op, arg)) for at, op, arg in seq if 77 <= at < 86],
                         [(77, (124, b'msgid')), (80, (100, 2)), (83, (106, 2))])
        self.assertIn((89, 1, None), seq)
        self.assertIn((90, 121, 29), seq)  # authored try: import register; Show(True)
        # False branch skips the full inserted fragment and its original exit jump.
        _, op, arg = next(item for item in seq if item[0] == 86)
        self.assertEqual(op, 111)
        self.assertEqual(86 + 3 + arg, self.report['details']['homepage']['click_span'][1] + 3)

    def test_home_serialization_keeps_original_budget_and_unrelated_methods(self):
        old, new = self.home_methods()
        allowed = {'', 'CMainPage', 'CMainPage/__init__', 'CMainPage/OnMessage'}
        for path in old.keys() - allowed:
            self.assertEqual(visual.semantic(old[path]), visual.semantic(new[path]))
        home_report = self.report['details']['homepage']
        self.assertEqual(home_report['payload_bytes'], 10335)
        self.assertGreater(home_report['padding_bytes'], 0)
        self.assertFalse(home_report['startup_imports_registration'])

    def test_reject_incoming_jump_to_replaced_interior(self):
        old, _ = self.home_methods()
        import copy
        co = copy.deepcopy(old['CMainPage/OnMessage'])
        co['code'] = base.assemble((113, 99)) + co['code'][3:]
        with self.assertRaisesRegex(ValueError, 'incoming jump'):
            visual.inline_fragment(co, 90, 263, visual.load_home_entry()[b'open_registration'])

    def test_frozen_home_fragments_have_no_closures_and_valid_opcodes(self):
        owned = visual.load_home_entry()
        self.assertEqual(set(owned), {b'install_caption', b'open_registration'})
        for co in owned.values():
            self.assertFalse(co['freevars'])
            self.assertFalse(co['cellvars'])
            base.valid_code(co, co['code'])

    def test_writer_float_roundtrip_for_untouched_home_constants(self):
        for value in (0.0, -0.0, 0.5, 1.5):
            self.assertEqual(base.tree(visual.Writer().write(value)), value)

    def test_cli_requires_explicit_candidate_opt_in(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'candidate'
            proc = subprocess.run([sys.executable, str(visual.HERE / 'build_visual_preview.py'),
                                   '--output-dir', str(output)], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn('explicit opt-in required', proc.stderr)
            self.assertFalse(output.exists())

    def test_report_calls_this_a_candidate_not_native_success(self):
        self.assertEqual(self.report['kind'], 'registration_visual_preview_v3_3_candidate')
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertEqual(len(self.report['startup_changes']), 4)


if __name__ == '__main__': unittest.main()
