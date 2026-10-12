"""Read-only regression tests for the entry 3205 (`petskill.py`) parameter conflict.

These tests exist because a previous review concluded, from an opcode-density
score alone, that entry 3205 has no module-level `DATA` table and that its second
XOR key should be 218.  Both conclusions are wrong: `DATA` is published with
`STORE_GLOBAL`, and `keys[1] = 218` only reproduces the density score while
destroying the module structure.

The assertions below therefore check the *recovered structure and its links*, not
just a parameter value, and one test pins the wrong candidate as rejected.  No
recovered game script is executed; the reader builds plain containers from
`co_consts`.
"""
import hashlib
import importlib.util
import json
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ARCHIVE_SHA256 = '8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72'
KEYDB_SHA256 = '43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb'

DUPLICATE_KEYS = [4573, 4574, 4575, 4576, 4577, 4578, 4579, 4581, 4236]
OVERWRITE_ORDER = list(range(352, 361))
OVERWRITE_OFFSETS = [22409, 22472, 22535, 22598, 22661, 22724, 22787, 22850, 22913]


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Register before executing: dataclasses in the loaded module resolve
    # `cls.__module__` through sys.modules (see test_public_reader_contract.py).
    import sys
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module


probe = _load(ROOT / 'server/tools/probe_script_entry_3205.py', 'probe_entry_3205')
reader = probe.literal_reader
decoder = probe.decoder


_SCAN_CACHE = {}


def _scan(params, index=3205):
    """Decode + transpile + read one entry for one parameter set (no solver)."""
    archive = probe.Archive(probe.ARCHIVE_PATH.read_bytes())
    if params['keys'] is None or params['bounds'] is None:
        keydb = json.loads(probe.KEYDB_PATH.read_bytes())
        stored = keydb[str(index)]
        keys = list(stored['keys'] if params['keys'] is None else params['keys'])
        bounds = list(stored['bounds'] if params['bounds'] is None else params['bounds'])
    else:
        keys, bounds = list(params['keys']), list(params['bounds'])
    exp = archive.payload(index)
    dec = probe.decrypt(exp, keys, bounds)
    co, _ = probe.transpile(exp, dec, keys, bounds)
    return reader.scan_module(co), co, dec, exp


class Entry3205Shared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = {spec['id']: spec for spec in probe.PARAMETER_SETS}

    @classmethod
    def scan(cls, set_id, index=3205):
        if (set_id, index) not in _SCAN_CACHE:
            _SCAN_CACHE[(set_id, index)] = _scan(cls.specs[set_id], index)
        return _SCAN_CACHE[(set_id, index)]


class SavedParametersTest(Entry3205Shared):
    def test_saved_parameters_do_not_read_the_module(self):
        scan, _co, _dec, _exp = self.scan('saved')
        self.assertTrue(scan.violations)
        self.assertEqual(scan.first_violation.reason,
                         'EXTENDED_ARG before argument-free instruction')
        self.assertIsNone(scan.by_name(b'DATA'))
        self.assertEqual(scan.assignments, [])


class AgentDParametersTest(Entry3205Shared):
    def test_module_is_literal_and_publishes_store_global_tables(self):
        scan, co, _dec, _exp = self.scan('agent_d')
        self.assertEqual([v.as_dict() for v in scan.violations], [])
        self.assertEqual(co['filename'], b'script\\data\\petskill.py')
        by_name = {a.name: a for a in scan.assignments}
        # The petskill master table is a module-level *global*, not a local name.
        self.assertEqual(by_name[b'DATA'].store_kind, 'STORE_GLOBAL')
        self.assertEqual(by_name[b'ICON_MAPPING'].store_kind, 'STORE_GLOBAL')
        self.assertEqual(by_name[b'AUTOFIGHTLIST'].store_kind, 'STORE_NAME')
        self.assertEqual(by_name[b'ShieldShortCutSkills'].store_kind, 'STORE_NAME')

    def test_data_table_structure(self):
        scan, _co, _dec, _exp = self.scan('agent_d')
        data = scan.by_name(b'DATA').value
        self.assertEqual(len(data), 581)
        self.assertTrue(all(type(k) is int for k in data))
        self.assertEqual((min(data), max(data)), (101, 45432))
        schema = {frozenset(record.keys()) for record in data.values()}
        self.assertEqual(schema, {frozenset({b'name', b'desc', b'type',
                                             b'fpneed', b'mpneed', b'hpneed'})})
        for record in data.values():
            for value in record.values():
                if isinstance(value, bytes):
                    value.decode('cp950')      # no silent encoding breakage

    def test_duplicate_writes_are_recorded_with_position_old_new_and_order(self):
        scan, _co, _dec, _exp = self.scan('agent_d')
        assignment = scan.by_name(b'DATA')
        self.assertEqual(len(assignment.writes), 590)          # 581 inserts + 9
        self.assertEqual([w.key for w in assignment.overwrites], DUPLICATE_KEYS)
        self.assertEqual([w.order for w in assignment.overwrites], OVERWRITE_ORDER)
        self.assertEqual([w.at for w in assignment.overwrites], OVERWRITE_OFFSETS)
        self.assertTrue(all(w.kind == 'overwrite' for w in assignment.overwrites))
        # Both writes of every duplicated key are present and ordered, so the
        # overwritten value can be inspected instead of being lost.
        first = assignment.overwrites[0]
        self.assertEqual(first.old[b'name'].decode('cp950'), '天魔返生術')
        self.assertEqual(first.new[b'name'].decode('cp950'), '地魔返生術')
        self.assertEqual({k: v for k, v in first.old.items() if k != b'name'},
                         {k: v for k, v in first.new.items() if k != b'name'})
        for later in assignment.overwrites[1:]:
            self.assertEqual(later.old, later.new)
        # The table's own value keeps the last write, i.e. the runtime result.
        self.assertEqual(assignment.value[4573][b'name'].decode('cp950'), '地魔返生術')
        self.assertNotIn(64605, assignment.value)

    def test_cross_table_links_hold(self):
        scan, _co, _dec, _exp = self.scan('agent_d')
        data = scan.by_name(b'DATA').value
        self.assertEqual(list(scan.by_name(b'AUTOFIGHTLIST').value)[:9],
                         [407, 408, 409, 410, 411, 413, 414, 415, 416])
        auto = set(scan.by_name(b'AUTOFIGHTLIST').value)
        self.assertEqual(len(auto), 37)
        self.assertTrue(auto <= set(data))
        self.assertEqual(list(scan.by_name(b'ShieldShortCutSkills').value), [556])
        icon = scan.by_name(b'ICON_MAPPING').value
        self.assertEqual(len(icon), 12)
        self.assertTrue(set(icon) <= set(data) and set(icon.values()) <= set(data))

    def test_entry_2242_skillidlist_links_into_the_master_table(self):
        # 2242 has its own parameters (both PRs agree on bounds[1] = 264).
        params = {'id': 'skillidlist', 'keys': probe.SKILLIDLST_PARAMS['keys'],
                  'bounds': probe.SKILLIDLST_PARAMS['bounds'], 'changed_fields': ()}
        scan, _co, _dec, _exp = _scan(params, probe.SKILLIDLST_ENTRY)
        self.assertEqual([v.as_dict() for v in scan.violations], [])
        values = list(scan.by_name(b'SKILLIDLST').value)
        self.assertEqual(len(values), 48)
        self.assertEqual(values[16], 416)
        data = self.scan('agent_d')[0].by_name(b'DATA').value
        self.assertTrue(set(values) <= set(data))
        self.assertEqual(data[416][b'name'].decode('cp950'), '水擊')


class Pr18ParametersTest(Entry3205Shared):
    """The rejected candidate must fail on structure, not on text."""

    def test_candidate_passes_its_own_two_criteria(self):
        # Reproduce PR #18's evidence so the refutation cannot be dismissed as
        # "you measured it differently": zero unmapped Duoyi opcodes in co_code and
        # a clean standard instruction walk, exactly like the correct parameters.
        results = {}
        for set_id in ('agent_d', 'pr18'):
            scan, co, dec, _exp = self.scan(set_id)
            results[set_id] = {
                'unmapped': probe.unmapped_duoyi_opcodes(
                    dec, 22, 22 + struct.unpack_from('<I', dec, 18)[0])['count'],
                'instructions': len(list(reader.instructions(co))),
            }
        self.assertEqual(results['agent_d']['unmapped'], 0)
        self.assertEqual(results['pr18']['unmapped'], 0)          # metric cannot decide
        self.assertEqual(results['agent_d']['instructions'], 20776)
        self.assertEqual(results['pr18']['instructions'], 20776)  # same count too

    def test_candidate_is_rejected_structurally(self):
        scan, _co, _dec, _exp = self.scan('pr18')
        self.assertTrue(scan.violations)
        first = scan.first_violation
        self.assertEqual((first.at, first.op), (18021, 80))       # BREAK_LOOP
        self.assertIsNone(scan.by_name(b'DATA'))
        self.assertNotIn('DATA', [a.name for a in scan.assignments])
        histogram = reader.disallowed_opcode_histogram(_co)
        self.assertGreater(sum(histogram.values()), 1000)
        self.assertIn('opcode 80 (BREAK_LOOP)', histogram)
        self.assertIn('opcode 119 (CONTINUE_LOOP)', histogram)

    def test_candidate_breaks_the_literal_item_that_the_correct_key_completes(self):
        # Under the correct key, 18018..18024 is `LOAD_CONST key; STORE_SUBSCR`;
        # under keys[1]=218 the same bytes decode to `LOAD_CONST key; BREAK_LOOP`.
        correct, correct_co, _dec, _exp = self.scan('agent_d')
        self.assertEqual([v.as_dict() for v in correct.violations], [])
        correct_window = [(at, op) for at, op, _ in reader.instructions(correct_co)
                          if 18012 <= at <= 18021]
        self.assertEqual(correct_window, [(18012, 60), (18013, 4), (18014, 100),
                                          (18017, 2), (18018, 100), (18021, 60)])
        rejected, rejected_co, _dec, _exp = self.scan('pr18')
        rejected_window = [(at, op) for at, op, _ in reader.instructions(rejected_co)
                           if 18012 <= at <= 18021]
        self.assertEqual(rejected_window, [(18012, 60), (18013, 4), (18014, 100),
                                           (18017, 2), (18018, 100), (18021, 80)])


class PublicReaderSemanticsTest(unittest.TestCase):
    """The shared reader must keep STORE_GLOBAL and duplicates visible."""

    def test_strict_mode_still_refuses_to_silently_overwrite(self):
        scan, co, _dec, _exp = _scan({p['id']: p for p in probe.PARAMETER_SETS}['agent_d'])
        del scan
        with self.assertRaisesRegex(ValueError, 'duplicate dictionary key'):
            reader.read_assignment(co, b'DATA', duplicate_policy='error')
        recorded = reader.read_assignment(co, b'DATA')
        self.assertEqual(len(recorded.duplicate_keys), 9)

    def test_transpiler_does_not_shorten_the_bytecode(self):
        # Agent D's report claims the transpiler drops bytes for unmapped opcodes
        # and that this desynchronises everything after it.  The implementation
        # writes into a same-size buffer, so only the *reading* of the output is
        # ambiguous; the length never changes.
        raw = bytes([0x8C, 0x01, 0x00, 0x8F, 0x02, 0x00, 0x41])
        out = decoder.transpile_py25_code(raw)
        self.assertEqual(len(out), len(raw))
        self.assertEqual(out[0], 9)      # unmapped Duoyi opcode becomes NOP
        self.assertEqual(out[3], 100)    # mapped LOAD_CONST is preserved
        self.assertEqual(out[6], 1)      # POP_TOP is preserved


class InputsUnchangedTest(unittest.TestCase):
    def test_client_archive_and_key_database_unchanged(self):
        self.assertEqual(
            hashlib.sha256((ROOT / 'data/script.fls').read_bytes()).hexdigest(),
            ARCHIVE_SHA256)
        self.assertEqual(
            hashlib.sha256((ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()).hexdigest(),
            KEYDB_SHA256)

    def test_candidates_are_not_installed_in_the_key_database(self):
        stored = json.loads((ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes())['3205']
        self.assertEqual(stored['keys'][1], 23)
        self.assertEqual(stored['bounds'], [18043, 36122, 54130, 72108])


if __name__ == '__main__':
    unittest.main()
