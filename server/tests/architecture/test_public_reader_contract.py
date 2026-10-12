"""Contract tests for the public client-data reader entry points.

These tests cover two defects found in coordinator review of the first phase:

1. The internal reader (`script_literal_reader.py`) was executed with
   `importlib` but never registered in `sys.modules`.  `dataclasses` resolves
   `cls.__module__` through `sys.modules`, so a *fresh* Python process that only
   imported `review_client_data_boundaries` crashed with
   `AttributeError: 'NoneType' object has no attribute '__dict__'`.
   The suite masked this because it imported the internal module first, so one
   test here starts a real subprocess and asserts the internal module is *not*
   loaded before the call.

2. `extract_table_report()` documented that it raises on an unsupported module
   structure but still returned a value when the table had already been
   published and the unsupported instruction came later.  The contract is now
   strict by default; partial results require an explicit `allow_partial=True`
   and are marked as unverified.

Only hand-written bytecode dictionaries are decoded here; no recovered game
script is executed and nothing is written to disk.
"""
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'server' / 'tools'


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module          # dataclass/reference resolution needs this
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


review = _load(TOOLS / 'review_client_data_boundaries.py', 'contract_review_boundaries')
reader = review._structural_reader()

# --- minimal inputs -------------------------------------------------------- #
# BUILD_MAP 0; STORE_GLOBAL 'DATA'; LOAD_CONST 0; RETURN_VALUE  -> DATA = {}
COMPLETE = {
    'code': bytes([104, 0, 0, 97, 0, 0, 100, 0, 0, 83]),
    'names': (b'DATA',),
    'consts': (None,),
}
# BUILD_MAP 0; STORE_GLOBAL 'DATA'; opcode 131 (not a literal op)  -> DATA published,
# then an instruction the reader cannot accept.
UNSUPPORTED_AFTER = {
    'code': bytes([104, 0, 0, 97, 0, 0, 131, 0, 0]),
    'names': (b'DATA',),
    'consts': (),
}
# opcode 131 first, then BUILD_MAP/STORE_GLOBAL -> the table is never published.
UNSUPPORTED_BEFORE = {
    'code': bytes([131, 0, 0, 104, 0, 0, 97, 0, 0]),
    'names': (b'DATA',),
    'consts': (),
}

FRESH_PROCESS_SCRIPT = textwrap.dedent(
    '''
    import sys, traceback
    sys.path.insert(0, {tools!r})
    import review_client_data_boundaries as r

    print("INTERNAL_LOADED_BEFORE:", "script_literal_reader" in sys.modules)
    complete = {{
        "code": bytes([104, 0, 0, 97, 0, 0, 100, 0, 0, 83]),
        "names": (b"DATA",),
        "consts": (None,),
    }}
    report = r.extract_table_report(complete)
    print("VALUE:", report["value"])
    print("STORE:", report["store"], "VERIFIED:", report["verified"],
          "PARTIAL:", report["partial"])
    print("INTERNAL_LOADED_AFTER:", "script_literal_reader" in sys.modules)

    late = {{
        "code": bytes([104, 0, 0, 97, 0, 0, 131, 0, 0]),
        "names": (b"DATA",),
        "consts": (),
    }}
    try:
        r.extract_table_report(late)
        print("STRICT: returned (WRONG)")
    except ValueError as exc:
        print("STRICT: raised", "allow_partial=True" in str(exc))
    partial = r.extract_table_report(late, allow_partial=True)
    print("PARTIAL_VALUE:", partial["value"], "VERIFIED:", partial["verified"],
          "VIOLATIONS:", len(partial["violations"]))

    reader = r._structural_reader()
    print("READ_ASSIGNMENT_VALUE:", reader.read_assignment(complete, b"DATA").value)
    try:
        reader.read_assignment(late, b"DATA")
        print("READ_ASSIGNMENT_STRICT: returned (WRONG)")
    except ValueError:
        print("READ_ASSIGNMENT_STRICT: raised")
    '''
)


class FreshProcessImportTest(unittest.TestCase):
    """Defect 1: the public entry point must work without pre-importing internals."""

    def test_fresh_process_call_does_not_need_the_internal_module(self):
        script = FRESH_PROCESS_SCRIPT.format(tools=str(TOOLS))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        result = subprocess.run([sys.executable, '-c', script], cwd=str(ROOT), env=env,
                                capture_output=True, text=True, timeout=300)
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertEqual(result.stderr, '')
        out = result.stdout
        # The whole point: the internal module is absent until the call and present
        # afterwards, i.e. the call itself imports it correctly.
        self.assertIn('INTERNAL_LOADED_BEFORE: False', out)
        self.assertIn('INTERNAL_LOADED_AFTER: True', out)
        self.assertIn('VALUE: {}', out)
        self.assertIn('STORE: STORE_GLOBAL VERIFIED: True PARTIAL: False', out)
        # The strict contract also holds in a fresh process.
        self.assertIn('STRICT: raised True', out)
        self.assertIn('PARTIAL_VALUE: {} VERIFIED: False VIOLATIONS: 1', out)
        self.assertIn('READ_ASSIGNMENT_VALUE: {}', out)
        self.assertIn('READ_ASSIGNMENT_STRICT: raised', out)
        self.assertNotIn('WRONG', out)


class StrictContractTest(unittest.TestCase):
    """Defect 2: a value published before an unsupported instruction is unverified."""

    def test_complete_module_is_reported_as_verified(self):
        report = review.extract_table_report(COMPLETE)
        self.assertEqual(report['value'], {})
        self.assertEqual(report['store'], 'STORE_GLOBAL')
        self.assertTrue(report['verified'])
        self.assertFalse(report['partial'])
        self.assertEqual(report['violations'], ())
        self.assertIsNone(report['warning'])

    def test_unsupported_instruction_after_the_table_is_rejected_by_default(self):
        with self.assertRaises(ValueError) as ctx:
            review.extract_table_report(UNSUPPORTED_AFTER)
        message = str(ctx.exception)
        self.assertIn('could not be read completely', message)
        self.assertIn("table b'DATA'", message)
        self.assertIn('at 6', message)              # the offending offset
        self.assertIn('allow_partial=True', message)

    def test_unsupported_instruction_before_the_table_is_rejected_by_default(self):
        with self.assertRaises(ValueError) as ctx:
            review.extract_table_report(UNSUPPORTED_BEFORE)
        message = str(ctx.exception)
        self.assertIn('not found', message)
        self.assertIn('first rejected shape', message)
        self.assertIn('at 0', message)
        # Partial mode cannot invent a table that was never published.
        with self.assertRaisesRegex(ValueError, 'not found'):
            review.extract_table_report(UNSUPPORTED_BEFORE, allow_partial=True)

    def test_partial_results_require_an_explicit_flag_and_stay_marked(self):
        report = review.extract_table_report(UNSUPPORTED_AFTER, allow_partial=True)
        self.assertEqual(report['value'], {})       # the prefix value is available ...
        self.assertFalse(report['verified'])        # ... but never as verified
        self.assertTrue(report['partial'])
        self.assertEqual(len(report['violations']), 1)
        violation = report['violations'][0]
        self.assertEqual((violation.at, violation.op), (6, 131))
        self.assertIn('partial result', report['warning'])
        self.assertIn('not fully verified', report['warning'])

    def test_scan_result_exposes_completeness(self):
        self.assertTrue(review.top_level_literal_assignments(COMPLETE).complete)
        late = review.top_level_literal_assignments(UNSUPPORTED_AFTER)
        self.assertFalse(late.complete)
        assignment = late.by_name(b'DATA')
        self.assertFalse(assignment.verified)
        self.assertTrue(assignment.partial)
        self.assertEqual([v.op for v in assignment.violations], [131])

    def test_unknown_duplicate_policy_is_still_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown duplicate_policy'):
            review.extract_table_report(COMPLETE, duplicate_policy='nonsense')


class ReadAssignmentParityTest(unittest.TestCase):
    """`read_assignment` must follow the same convention as `extract_table_report`."""

    def test_complete_module_returns_a_verified_assignment(self):
        assignment = reader.read_assignment(COMPLETE, b'DATA')
        self.assertIsNotNone(assignment)
        self.assertTrue(assignment.verified)
        self.assertEqual(assignment.value, {})
        self.assertEqual(assignment.violations, ())

    def test_partial_value_needs_allow_partial(self):
        with self.assertRaisesRegex(ValueError, 'unverified'):
            reader.read_assignment(UNSUPPORTED_AFTER, b'DATA')
        assignment = reader.read_assignment(UNSUPPORTED_AFTER, b'DATA', allow_partial=True)
        self.assertEqual(assignment.value, {})
        self.assertFalse(assignment.verified)
        self.assertTrue(assignment.partial)
        self.assertEqual([v.op for v in assignment.violations], [131])

    def test_absent_table_reports_the_reason(self):
        with self.assertRaisesRegex(ValueError, 'not found'):
            reader.read_assignment(UNSUPPORTED_BEFORE, b'DATA')
        # `allow_partial` cannot invent a table that was never published: there is
        # no partial value to inspect, and `None` stays reserved for "read
        # completely, genuinely absent".
        with self.assertRaisesRegex(ValueError, 'not found'):
            reader.read_assignment(UNSUPPORTED_BEFORE, b'DATA', allow_partial=True)
        self.assertIsNone(reader.read_assignment(
            {'code': bytes([100, 0, 0, 83]), 'names': (), 'consts': (None,)}, b'DATA'))


class SharedModuleInstanceTest(unittest.TestCase):
    """The loader must not define a second copy of the reader's classes."""

    def test_internal_loader_reuses_an_already_imported_module(self):
        sys.path.insert(0, str(TOOLS))
        try:
            import script_literal_reader as public
        finally:
            sys.path.remove(str(TOOLS))
        review._STRUCTURAL_READER = None      # force the lookup path
        try:
            loaded = review._structural_reader()
        finally:
            review._STRUCTURAL_READER = loaded
        self.assertIs(loaded, public)
        self.assertIs(loaded.Assignment, public.Assignment)
        self.assertIs(loaded.WriteEvent, public.WriteEvent)
        # Objects handed out through the public report use those same classes.
        # BUILD_MAP 0; DUP_TOP; LOAD_CONST 0 ('k'); ROT_TWO; LOAD_CONST 1 (1);
        # STORE_SUBSCR; STORE_GLOBAL 'DATA'   ->   DATA = {b'k': 1}
        # (opcodes below 90 take no argument bytes in this VM.)
        co = {
            'code': bytes([104, 0, 0, 4, 100, 0, 0, 2, 100, 1, 0, 60, 97, 0, 0]),
            'names': (b'DATA',),
            'consts': (b'k', 1),
        }
        writes = review.extract_table_report(co)['writes']
        self.assertEqual(len(writes), 1)
        self.assertIsInstance(writes[0], public.WriteEvent)
        self.assertIsInstance(loaded.read_assignment(co, b'DATA'), public.Assignment)


class RecoveredEntry3205UnaffectedTest(unittest.TestCase):
    """The strict default must not change the verified phase-1 result."""

    def test_entry_3205_still_reports_a_complete_verified_table(self):
        probe = _load(TOOLS / 'probe_script_entry_3205.py', 'contract_probe_entry_3205')
        archive = probe.Archive(probe.ARCHIVE_PATH.read_bytes())
        keydb = json.loads(probe.KEYDB_PATH.read_bytes())
        del keydb
        spec = [s for s in probe.PARAMETER_SETS if s['id'] == 'agent_d'][0]
        exp = archive.payload(3205)
        dec = probe.decrypt(exp, spec['keys'], spec['bounds'])
        co, _ = probe.transpile(exp, dec, spec['keys'], spec['bounds'])
        report = review.extract_table_report(co, b'DATA')
        self.assertTrue(report['verified'])
        self.assertFalse(report['partial'])
        self.assertEqual(report['violations'], ())
        self.assertEqual(len(report['value']), 581)
        self.assertEqual([w.key for w in report['overwrites']], list(range(4573, 4580)) + [4581, 4236])


if __name__ == '__main__':
    unittest.main()
