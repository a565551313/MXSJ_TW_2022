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


if __name__ == '__main__':
    unittest.main()
