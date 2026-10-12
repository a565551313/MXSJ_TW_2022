"""Offline patch checks only, not native Windows client acceptance."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_registration_preview as patch


class RegistrationPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (patch.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.metadata = json.loads(cls.keys)
        cls.output, cls.report = patch.build(cls.source, cls.keys)
        cls.rows = patch.entries(cls.source)[1]
        cls.new_rows = patch.entries(cls.output)[1]

    def plain(self, rows, index):
        return patch.xor_payload(patch.zlib.decompress(rows[index][1]), self.metadata[str(index)])

    def functions(self, rows, index):
        return dict(patch.objects(patch.tree(self.plain(rows, index))))

    def test_v1_published_binary_is_unchanged(self):
        self.assertEqual(patch.sha(self.output), '345918e9ac2eef95ea98140fdbb70606a493dc682fce11f4c24ce178d86291eb')

    def test_wrong_archive_refused(self):
        with self.assertRaisesRegex(ValueError, 'unsupported source'):
            patch.build(self.source[:-1] + bytes([self.source[-1] ^ 1]), self.keys)

    def test_wrong_keys_refused(self):
        with self.assertRaisesRegex(ValueError, 'key database'):
            patch.build(self.source, b'{}')

    def test_empty_patch_is_byte_identical(self):
        self.assertEqual(patch.repack(self.source, {}), self.source)

    def test_build_is_deterministic(self):
        output, report = patch.build(self.source, self.keys)
        self.assertEqual(output, self.output)
        self.assertEqual(report, self.report)

    def test_only_two_directory_entries_and_payloads_change(self):
        changed = [i for i, (a, b) in enumerate(zip(self.rows, self.new_rows)) if a != b]
        self.assertEqual(changed, [337, 4007])
        self.assertEqual(len(self.new_rows), 5002)
        self.assertEqual(self.report['untouched_entries_byte_identical'], 5000)

    def test_original_archive_retained_except_directory_pointer(self):
        self.assertEqual(self.output[:8], self.source[:8])
        self.assertEqual(self.output[12:len(self.source)], self.source[12:])
        self.assertGreater(len(self.output), len(self.source))

    def test_mainpage_predicate_is_false_without_global_region_change(self):
        before = self.functions(self.rows, 337)['CMainPage/OnMessage']
        after = self.functions(self.new_rows, 337)['CMainPage/OnMessage']
        self.assertEqual(after['code'][:102], before['code'][:102])
        self.assertEqual(after['code'][111:], before['code'][111:])
        self.assertEqual(after['code'][102:111], patch.assemble((116, after['names'].index(b'False')))
                         + patch.assemble((9, None)) * 6)
        seq = patch.normalized(after['code'])
        self.assertIn((111, 111, 88), seq)  # false jump to 202, then pop
        self.assertIn((202, 1, None), seq)
        self.assertIn((209, 107, after['names'].index(b'register')), seq)
        self.assertEqual(self.rows[3854], self.new_rows[3854])  # interface.TAIWAN unchanged
        self.assertEqual(self.rows[4806], self.new_rows[4806])  # login page unchanged

    def test_agree_and_reject_use_original_return_home_handler(self):
        before = self.functions(self.rows, 4007)['CRegPanel1/OnMessage']
        after = self.functions(self.new_rows, 4007)['CRegPanel1/OnMessage']
        seq = patch.normalized(after['code'])
        self.assertIn((13, 113, 184), seq)
        self.assertIn((194, 113, 259), seq)
        self.assertEqual(before['code'][184:194], after['code'][184:194])
        self.assertEqual(before['code'][259:], after['code'][259:])
        self.assertIn((259, 121, 29), seq)  # try/except stack remains valid
        self.assertIn((268, 107, after['names'].index(b'mainpage')), seq)

    def test_all_direct_registration_http_and_browser_callers_return_none(self):
        functions = self.functions(self.new_rows, 4007)
        callers = {path for path, co in functions.items() if {b'CHttpObject', b'OpenUrl'} & set(co['names'])}
        self.assertEqual(callers, patch.NETWORK_PATHS)
        for path in callers:
            co = functions[path]
            seq = patch.normalized(co['code'])
            self.assertEqual(seq[:2], [(0, 100, co['consts'].index(None)), (3, 83, None)])
            self.assertTrue(all(op == 9 for _, op, _ in seq[2:]), path)

    def test_layout_constants_and_all_other_functions_retained(self):
        for index in (337, 4007):
            before = self.functions(self.rows, index)
            after = self.functions(self.new_rows, index)
            changed = {x['function'] for report in self.report['patches']
                       if report['entry_index'] == index for x in report['changes']}
            for path in before:
                if path not in changed:
                    self.assertEqual(before[path]['code'], after[path]['code'])
                for key in ('names', 'varnames', 'firstlineno', 'lnotab', 'offset', 'stacksize'):
                    self.assertEqual(before[path][key], after[path][key])
            self.assertEqual(len(self.plain(self.rows, index)), len(self.plain(self.new_rows, index)))

    def test_xor_boundary_overlap_is_rejected(self):
        metadata = copy.deepcopy(self.metadata['337'])
        function = self.functions(self.rows, 337)['CMainPage/OnMessage']
        metadata['bounds'] = [function['offset'] + 22 + 104]
        with self.assertRaisesRegex(ValueError, 'XOR boundary'):
            patch.patch_payload(337, self.plain(self.rows, 337), metadata)

    def test_original_files_are_unchanged(self):
        self.assertEqual((patch.ROOT / 'data/script.fls').read_bytes(), self.source)
        self.assertEqual((patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes(), self.keys)

    def test_report_does_not_claim_native_acceptance(self):
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertFalse(self.report['recovered_code_executed'])


class RegistrationFormPreviewTests(unittest.TestCase):
    """v2 enables input widgets, never old registration submission."""
    @classmethod
    def setUpClass(cls):
        cls.source = (patch.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.metadata = json.loads(cls.keys)
        cls.output, cls.report = patch.build(cls.source, cls.keys, stage='form')
        cls.rows = patch.entries(cls.source)[1]
        cls.new_rows = patch.entries(cls.output)[1]

    plain = RegistrationPreviewTests.plain
    functions = RegistrationPreviewTests.functions

    def test_unknown_stage_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unsupported preview stage'):
            patch.build(self.source, self.keys, stage='online')

    def test_only_two_entries_change_and_build_is_deterministic(self):
        changed = [i for i, (a, b) in enumerate(zip(self.rows, self.new_rows)) if a != b]
        self.assertEqual(changed, [337, 4007])
        output, report = patch.build(self.source, self.keys, stage='form')
        self.assertEqual(output, self.output)
        self.assertEqual(report, self.report)
        self.assertEqual(patch.sha(output), '50e678f8e485691b0cc5d378d5cad255ff076aaba18c1e12ab9a6c277f9b057f')

    def test_first_page_agree_keeps_step_one_and_skips_telemetry(self):
        before = self.functions(self.rows, 4007)['CRegPanel1/OnMessage']
        after = self.functions(self.new_rows, 4007)['CRegPanel1/OnMessage']
        self.assertEqual(after['code'][13:23], before['code'][13:23])
        self.assertEqual(after['code'][13:23], patch.assemble((116, after['names'].index(b'Step')),
                         (100, after['consts'].index(1)), (131, 1), (1, None)))
        self.assertEqual(after['code'][23:26], patch.assemble((113, 336)))
        self.assertEqual(after['code'][336:], patch.assemble((100, after['consts'].index(None)), (83, None)))

    def test_reject_retains_v1_return_home_path(self):
        before = self.functions(self.rows, 4007)['CRegPanel1/OnMessage']
        after = self.functions(self.new_rows, 4007)['CRegPanel1/OnMessage']
        self.assertEqual(after['code'][184:194], before['code'][184:194])
        self.assertEqual(after['code'][194:197], patch.assemble((113, 259)))
        self.assertEqual(after['code'][259:], before['code'][259:])

    def test_form_back_keeps_step_zero_but_save_is_disabled(self):
        functions = self.functions(self.new_rows, 4007)
        before = self.functions(self.rows, 4007)['CRegPanel2/OnMessage']
        after = functions['CRegPanel2/OnMessage']
        self.assertEqual(after['code'][:104], before['code'][:104])
        self.assertIn((26, 100, after['consts'].index(0)), patch.normalized(after['code']))
        co = functions['CRegPanel2/Save']
        self.assertEqual(co['code'], patch.assemble((100, co['consts'].index(None)), (83, None))
                         + patch.assemble((9, None)) * (len(co['code']) - 4))

    def test_next_only_shows_local_offline_dialog(self):
        co = self.functions(self.new_rows, 4007)['CRegPanel2/DoNext']
        seq = patch.normalized(co['code'])
        names_used = [co['names'][arg] for _, op, arg in seq if op in {105, 107, 116}]
        self.assertEqual(names_used, [b'commondialog', b'ShowNewMessageBox'])
        self.assertEqual([arg for _, op, arg in seq if op == 131], [2])
        self.assertIn((10), [arg for _, op, arg in seq if op == 100])
        self.assertEqual(co['consts'][10].decode('cp950').strip(), '離線預覽，未送出。')
        # No GetText/Save/DoCheck/device/MD5/HTTP call; no store to any global.
        self.assertNotIn(97, [op for _, op, _ in seq])
        ret = next(i for i, (_, op, _) in enumerate(seq) if op == 83)
        self.assertTrue(all(op == 9 for _, op, _ in seq[ret + 1:]))

    def test_all_other_network_callers_and_alternate_registration_are_disabled(self):
        functions = self.functions(self.new_rows, 4007)
        for path in (patch.NETWORK_PATHS - {'CRegPanel2/DoNext'}) | {'Register2980'}:
            co = functions[path]
            seq = patch.normalized(co['code'])
            self.assertEqual(seq[:2], [(0, 100, co['consts'].index(None)), (3, 83, None)])
            self.assertTrue(all(op == 9 for _, op, _ in seq[2:]), path)

    def test_old_email_registration_link_is_local_preview_notice(self):
        functions = self.functions(self.new_rows, 4007)
        co = functions['CRegPanel2/OnMessage']
        self.assertEqual(co['code'][117:120], patch.assemble((113, 90)))
        self.assertIn((93, 105, co['names'].index(b'DoNext')), patch.normalized(co['code']))
        self.assertTrue(all(op == 9 for _, op, _ in patch.normalized(co['code'][120:192])))
        self.assertEqual(functions['CRegPanel2/__init__']['consts'][4].decode('cp950').strip(), '離線預覽說明')

    def test_field_construction_validation_and_password_masking_are_unchanged(self):
        before = self.functions(self.rows, 4007)
        after = self.functions(self.new_rows, 4007)
        for path in ('CRegPanel2/__init__', 'CRegPanel2/CreateEdits', 'CRegPanel2/DoCheck',
                     'CRegPanel2/OnEditChange', 'CRegPanel2/OnActive'):
            self.assertEqual(before[path]['code'], after[path]['code'])
        self.assertIn(b'm_IsPassword', after['CRegPanel2/CreateEdits']['names'])
        for path in ('CRegPanel2/__init__', 'CRegPanel2/CreateEdits'):
            self.assertFalse({b'CHttpObject', b'OpenUrl', b'RequestNewCode', b'DoNext', b'Register2980',
                              b'LoginLog'} & set(after[path]['names']))

    def test_only_two_fixed_width_literals_are_changed(self):
        before = self.functions(self.rows, 4007)
        after = self.functions(self.new_rows, 4007)
        changes = []
        for path in before:
            for i, (a, b) in enumerate(zip(before[path]['consts'], after[path]['consts'])):
                if not isinstance(a, dict) and a != b:
                    changes.append((path, i))
                    self.assertEqual(len(a), len(b))
                    b.decode('cp950')
        self.assertEqual(set(changes), {('CRegPanel2/__init__', 4), ('CRegPanel2/DoNext', 10)})
        self.assertEqual(len(self.plain(self.rows, 4007)), len(self.plain(self.new_rows, 4007)))

    def test_file_installation_guard_still_requires_original_not_v1(self):
        previous, _ = patch.build(self.source, self.keys)
        with self.assertRaisesRegex(ValueError, 'unsupported source'):
            patch.build(previous, self.keys, stage='form')

    def test_no_native_or_live_registration_claim(self):
        self.assertEqual(self.report['kind'], 'registration_form_offline_preview_only')
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertFalse(self.report['recovered_code_executed'])
        self.assertEqual((patch.ROOT / 'data/script.fls').read_bytes(), self.source)
        self.assertEqual((patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes(), self.keys)


class RegistrationBasicFormPreviewTests(unittest.TestCase):
    """Regression for user traceback: missing secondary-email UI placeholder."""
    @classmethod
    def setUpClass(cls):
        cls.source = (patch.ROOT / 'data/script.fls').read_bytes()
        cls.keys = (patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        cls.metadata = json.loads(cls.keys)
        cls.output, cls.report = patch.build(cls.source, cls.keys, stage='form-basic')
        cls.rows = patch.entries(cls.source)[1]
        cls.new_rows = patch.entries(cls.output)[1]
        cls.v2, _ = patch.build(cls.source, cls.keys, stage='form')
        cls.v2_rows = patch.entries(cls.v2)[1]

    plain = RegistrationPreviewTests.plain
    functions = RegistrationPreviewTests.functions
    test_agree_step_one = RegistrationFormPreviewTests.test_first_page_agree_keeps_step_one_and_skips_telemetry
    test_reject_returns_home = RegistrationFormPreviewTests.test_reject_retains_v1_return_home_path
    test_back_and_no_save = RegistrationFormPreviewTests.test_form_back_keeps_step_zero_but_save_is_disabled
    test_next_only_local_notice = RegistrationFormPreviewTests.test_next_only_shows_local_offline_dialog
    test_other_old_network_paths_disabled = RegistrationFormPreviewTests.test_all_other_network_callers_and_alternate_registration_are_disabled
    test_old_email_link_is_local_notice = RegistrationFormPreviewTests.test_old_email_registration_link_is_local_preview_notice

    @staticmethod
    def linear_path(co):
        # Inspect instruction addresses only; never execute recovered code or UI.
        # CreateEdits has no original conditional branches. Only v2.1 forward
        # jumps and the return are accepted, so NOP padding is unreachable.
        seq = {at: (op, arg) for at, op, arg in patch.normalized(co['code'])}
        result = []
        at = 0
        while True:
            op, arg = seq[at]
            result.append((at, op, arg))
            if op == 83:
                return result
            if op == 113:
                if arg <= at:
                    raise AssertionError('unexpected loop')
                at = arg
            else:
                if op in {93, 110, 111, 112, 119, 120, 121, 122}:
                    raise AssertionError('unexpected branch')
                at += 3 if op >= 90 else 1

    def test_raw_line_328_is_email2_not_password_confirmation(self):
        co = self.functions(self.rows, 4007)['CRegPanel2/CreateEdits']
        line = co['firstlineno']
        offset = 0
        positions = [(0, line)]
        for delta, increment in zip(co['lnotab'][::2], co['lnotab'][1::2]):
            offset += delta
            line += increment
            positions.append((offset, line))
        self.assertEqual([at for at, ln in positions if ln == 328], [241])
        self.assertEqual(next(ln for at, ln in reversed(positions) if at <= 268), 328)
        self.assertIn((250, 100, co['consts'].index(b'email2')), patch.normalized(co['code']))
        helper = self.functions(self.rows, 3564)['CreateEdit']
        self.assertIn((15, 105, helper['names'].index(b'GetObject')), patch.normalized(helper['code']))
        self.assertIn((51, 105, helper['names'].index(b'GetSize')), patch.normalized(helper['code']))

    def test_three_primary_controls_and_focus_cycle_are_unchanged(self):
        before = self.functions(self.rows, 4007)['CRegPanel2/CreateEdits']
        after = self.functions(self.new_rows, 4007)['CRegPanel2/CreateEdits']
        self.assertEqual(before['code'][:241], after['code'][:241])
        self.assertEqual(before['code'][377:434], after['code'][377:434])
        seq = self.linear_path(after)
        slots = []
        for i, (_, op, arg) in enumerate(seq):
            if op == 105 and after['names'][arg] == b'CEDIT':
                _, next_op, constant = seq[i + 2]
                self.assertEqual(next_op, 100)
                slots.append(after['consts'][constant])
        self.assertEqual(slots, [b'pwd', b'pwd2', b'email'])
        self.assertEqual(sum(op == 105 and after['names'][arg] == b'SetNextEdit'
                             for _, op, arg in seq), 3)

    def test_no_reachable_secondary_email_or_captcha_access(self):
        co = self.functions(self.new_rows, 4007)['CRegPanel2/CreateEdits']
        seq = self.linear_path(co)
        attrs = {co['names'][arg] for _, op, arg in seq if op in {95, 105, 116}}
        literals = {co['consts'][arg] for _, op, arg in seq if op == 100}
        self.assertFalse(attrs & {b'm_EmailEdit2', b'm_EditChange', b'm_CodeEdit', b'm_RefershCode'})
        self.assertFalse(literals & {b'email2', b'txt_Mail2', b'img_Mail2Bg', b'edt_Code',
                                    b'txt_Code', b'txt_CodeBg', b'txt_RefershCode'})
        self.assertIn((241, 113, 377), seq)
        self.assertIn((434, 113, 650), seq)
        self.assertEqual(seq[-2:], [(650, 100, co['consts'].index(None)), (653, 83, None)])

    def test_email_change_callback_cannot_touch_missing_widgets(self):
        co = self.functions(self.new_rows, 4007)['CRegPanel2/OnEditChange']
        seq = patch.normalized(co['code'])
        self.assertEqual(seq[:2], [(0, 100, co['consts'].index(None)), (3, 83, None)])
        self.assertTrue(all(op == 9 for _, op, _ in seq[2:]))

    def test_only_two_functions_differ_from_v2(self):
        before = self.functions(self.v2_rows, 4007)
        after = self.functions(self.new_rows, 4007)
        changed = {path for path in before if before[path]['code'] != after[path]['code']}
        self.assertEqual(changed, {'CRegPanel2/CreateEdits', 'CRegPanel2/OnEditChange'})
        for path in before:
            for a, b in zip(before[path]['consts'], after[path]['consts']):
                if not isinstance(a, dict):
                    self.assertEqual(a, b)
        self.assertEqual(self.v2_rows[337], self.new_rows[337])
        self.assertEqual(len(self.plain(self.v2_rows, 4007)), len(self.plain(self.new_rows, 4007)))

    def test_only_target_entries_change_and_originals_remain(self):
        self.assertEqual([i for i, (a, b) in enumerate(zip(self.rows, self.new_rows)) if a != b], [337, 4007])
        self.assertEqual(self.output[12:len(self.source)], self.source[12:])
        self.assertEqual((patch.ROOT / 'data/script.fls').read_bytes(), self.source)
        self.assertEqual((patch.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes(), self.keys)

    def test_basic_build_is_deterministic_and_keeps_v2_reproducible(self):
        output, report = patch.build(self.source, self.keys, stage='form-basic')
        self.assertEqual(output, self.output)
        self.assertEqual(report, self.report)
        self.assertEqual(patch.sha(output), 'ed40cbade80a42b6924b9a99edffefbaa4100dbf624ebd653a789d8b7283c0ba')
        self.assertEqual(patch.sha(self.v2), '50e678f8e485691b0cc5d378d5cad255ff076aaba18c1e12ab9a6c277f9b057f')

    def test_report_does_not_claim_native_fix_verified(self):
        self.assertFalse(self.report['native_windows_client_tested'])
        self.assertFalse(self.report['recovered_code_executed'])
        self.assertEqual(self.report['kind'], 'registration_basic_form_offline_preview_only')
        self.assertTrue(any('email2' in item for item in self.report['limits']))


if __name__ == '__main__':
    unittest.main()
