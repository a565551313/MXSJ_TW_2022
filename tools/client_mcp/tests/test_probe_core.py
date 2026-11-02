"""Tests for the standalone probe, using only synthetic injected state."""
import importlib.util
import pathlib
import unittest

PATH = pathlib.Path(__file__).resolve().parents[1] / 'client_probe' / 'mxsj_probe.py'
SPEC = importlib.util.spec_from_file_location('standalone_probe', PATH)
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


class Runtime:
    version_info = (2, 5, 6, 'final', 0)
    modules = {'sys': object(), 'private_token': object(), 'time': object()}


class ProbeCoreTests(unittest.TestCase):
    def test_injected_state_is_allowlisted(self):
        state = {'pid': 42, 'thread_count': 3, 'main_loop_ticks': 7,
                 'password': 'sensitive', 'token': 'sensitive'}
        report = probe.get_report(state, Runtime())
        self.assertEqual(report['runtime'], {'python_version': [2, 5, 6],
                         'pid': 42, 'thread_count': 3, 'main_loop_ticks': 7})
        self.assertNotIn('sensitive', repr(report))
        self.assertNotIn('private_token', repr(report))
        self.assertEqual(report['native_api'], {'status': 'unknown', 'apis': []})

    def test_missing_or_invalid_values_are_unknown(self):
        result = probe.get_runtime({'pid': True, 'thread_count': -1,
                                    'main_loop_ticks': '123'}, object())
        self.assertEqual(result, {'python_version': None, 'pid': None,
                         'thread_count': None, 'main_loop_ticks': None})
        self.assertTrue(all(item['loaded'] is None
                            for item in probe.get_modules(object())['modules']))

    def test_module_snapshot_does_not_import_or_expose_other_names(self):
        before = Runtime.modules.copy()
        result = probe.get_modules(Runtime())
        self.assertEqual(result['modules'], [
            {'name': 'sys', 'loaded': True},
            {'name': 'time', 'loaded': True},
            {'name': 'os', 'loaded': False},
        ])
        self.assertEqual(Runtime.modules, before)

    def test_snapshots_are_independent(self):
        first = probe.get_report(runtime=Runtime())
        first['modules']['modules'][0]['loaded'] = False
        self.assertTrue(probe.get_report(runtime=Runtime())['modules']['modules'][0]['loaded'])

    def test_default_runtime(self):
        self.assertIsNotNone(probe.get_runtime()['python_version'])


if __name__ == '__main__':
    unittest.main()
