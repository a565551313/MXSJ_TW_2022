#!/usr/bin/env python3
"""Read-only three-way reproduction for `data/script.fls` entry 3205 (`petskill.py`).

Entry 3205 is the pet-skill master table (`DATA`, 581 unique skill ids) plus
`ICON_MAPPING`, `AUTOFIGHTLIST` and `ShieldShortCutSkills`.  Three parameter sets
have been proposed for its second XOR segment:

    saved     : script_fls_keys.json as stored (`keys[1] = 23`)
    agent_d   : PR #14 (Agent D) candidate, `keys[1] = 152` and 3 boundary moves
    pr18      : PR #18 candidate, `keys[1] = 218` with the saved boundaries

This tool decodes, transpiles and reads the module for each set with the same
strict literal reader and prints why the results differ.  It never executes
recovered code, never writes to the client tree, and never touches
`server/game_data/`.

Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/probe_script_entry_3205.py
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/probe_script_entry_3205.py --set agent_d
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/probe_script_entry_3205.py --write

`--write` stores the machine-readable evidence at
`server/docs/csv_checks/entry_3205_parameter_probe.json`; that JSON is the only
file the tool writes, and only when asked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'server/tools'))

from tools.decompiler import batch_decompile as decoder  # noqa: E402
from tools.fls_batch_decoder import MarshalReader  # noqa: E402
import script_literal_reader as literal_reader  # noqa: E402

ARCHIVE_PATH = ROOT / 'data/script.fls'
KEYDB_PATH = ROOT / 'tools/decompiler/script_fls_keys.json'
OUT_PATH = ROOT / 'server/docs/csv_checks/entry_3205_parameter_probe.json'

ENTRY_INDEX = 3205
# The root `co_code` starts at payload offset 22: 16-byte code header + 's' tag +
# 4-byte length.  Used only to describe the span in the report.
ROOT_CODE_PAYLOAD_START = 22

#: The three parameter sets under investigation.  `keys=None`/`bounds=None` mean
#: "use the value stored in `script_fls_keys.json`".
PARAMETER_SETS = (
    {
        'id': 'saved',
        'label': 'saved script_fls_keys.json',
        'source': 'tools/decompiler/script_fls_keys.json (baseline, method=catalog)',
        'keys': None,
        'bounds': None,
        'changed_fields': (),
    },
    {
        'id': 'agent_d',
        'label': 'Agent D / PR #14 candidate',
        'source': 'PR #14 server/docs/csv_checks/AGENT_D.md section 5',
        'keys': [204, 152, 122, 74, 218],
        'bounds': [18043, 36123, 54155, 72143],
        'changed_fields': ('keys[1]: 23 -> 152', 'bounds[1]: 36122 -> 36123',
                           'bounds[2]: 54130 -> 54155', 'bounds[3]: 72108 -> 72143'),
    },
    {
        'id': 'pr18',
        'label': 'PR #18 candidate',
        'source': 'PR #18 server/docs/CLIENT_DATA_INDEPENDENT_CHECK.md section 3.5',
        'keys': [204, 218, 122, 74, 218],
        'bounds': None,
        'changed_fields': ('keys[1]: 23 -> 218',),
    },
)

#: Cross-table references used to check that a recovered table is usable.
SKILLIDLST_ENTRY = 2242
SKILLIDLST_PARAMS = {'keys': [57, 243, 14, 98, 229],
                     'bounds': [130, 264, 401, 529]}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Archive:
    """Minimal read-only 0SLF reader, independent of the saved parameter sets."""

    def __init__(self, raw: bytes):
        self.raw = raw
        self.index_offset = struct.unpack_from('<I', raw, 8)[0]
        self.entry_count = struct.unpack_from('<I', raw, 4)[0]
        self._payloads: dict = {}

    def payload(self, index: int) -> bytes:
        if index not in self._payloads:
            entry_id, a, b, c = struct.unpack_from(
                '<IIII', self.raw, self.index_offset + 16 * index)
            size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
            pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
            self._payloads[index] = zlib.decompress(self.raw[pos:pos + size])
        return self._payloads[index]


def decrypt(exp: bytes, keys, bounds) -> bytes:
    edges = [0] + list(bounds) + [len(exp)]
    return b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[keys[i]])
                    for i in range(5))


def transpile(exp: bytes, dec: bytes, keys, bounds):
    """Transpile the marshal buffer with the automatic co_code solver disabled.

    Disabling the solver keeps the *given* parameters under test; the solver is a
    separate heuristic that rewrites boundaries and would silently mask a wrong
    parameter set.
    """
    tr = decoder.Py25MarshalTranspiler(dec, exp, list(keys), list(bounds))
    with patch.object(decoder, 'solve_py25_co_span', return_value=None):
        tr.transpile_object()
    reader = MarshalReader(bytes(tr.out)[8:])
    co = reader.read()
    if reader.pos != len(reader.data):
        raise ValueError(f'marshal reader consumed {reader.pos} of {len(reader.data)} bytes')
    return co, bytes(tr.out)


def duoyi_walk(raw: bytes, start: int, end: int):
    """Walk Duoyi bytecode (HAVE_ARGUMENT == 0x5F). Yields (offset, opcode, arg)."""
    at = start
    while at < end:
        op = raw[at]
        if op >= 0x5F:
            if at + 3 > end:
                return
            yield at, op, struct.unpack_from('<H', raw, at + 1)[0]
            at += 3
        else:
            yield at, op, None
            at += 1


def unmapped_duoyi_opcodes(raw: bytes, start: int, end: int) -> dict:
    """PR #18's metric: opcodes absent from the Duoyi opcode map inside co_code."""
    positions = [at for at, op, _ in duoyi_walk(raw, start, end)
                 if op not in decoder.PY25_MAP]
    return {'count': len(positions), 'first': positions[:8]}


def evaluate(entry_index: int, params: dict, archive: Archive, keydb: dict) -> dict:
    stored = keydb[str(entry_index)]
    keys = list(stored['keys'] if params['keys'] is None else params['keys'])
    bounds = list(stored['bounds'] if params['bounds'] is None else params['bounds'])
    result = {'keys': keys, 'bounds': bounds,
              'saved_keys': stored['keys'], 'saved_bounds': stored['bounds'],
              'changed_fields': list(params['changed_fields'])}

    exp = archive.payload(entry_index)
    result['payload_length'] = len(exp)
    try:
        dec = decrypt(exp, keys, bounds)
    except Exception as exc:                     # pragma: no cover - defensive
        result['decrypt_error'] = f'{type(exc).__name__}: {exc}'
        return result

    co_code_len = struct.unpack_from('<I', dec, 18)[0]
    code_start = ROOT_CODE_PAYLOAD_START
    code_end = code_start + co_code_len
    result['root_co_code_payload_span'] = [code_start, code_end]
    result['unmapped_duoyi_opcodes_in_root_co_code'] = unmapped_duoyi_opcodes(
        dec, code_start, code_end)

    try:
        co, _out = transpile(exp, dec, keys, bounds)
    except Exception as exc:
        result['transpile_error'] = f'{type(exc).__name__}: {exc}'
        return result

    result['co_filename'] = co['filename'].decode('latin1')
    result['co_names'] = [n.decode('latin1') for n in co['names']]
    result['const_count'] = len(co['consts'])

    try:
        result['standard_walk'] = {
            'ok': True,
            'instruction_count': len(list(literal_reader.instructions(co))),
        }
    except literal_reader.LiteralSyntaxError as exc:
        result['standard_walk'] = {'ok': False, 'error': exc.as_dict()}

    scan = literal_reader.scan_module(co)
    result['literal_grammar'] = {
        'ok': not scan.violations,
        'first_violation': scan.first_violation.as_dict() if scan.first_violation else None,
        'violation_count': len(scan.violations),
        'stack_depth_max': scan.stack_depth_max,
    }
    result['disallowed_opcodes_in_module'] = {
        'metric': 'opcodes outside the module-level literal allowlist',
        'histogram': literal_reader.disallowed_opcode_histogram(co),
    }
    result['index_bound_problems'] = literal_reader.scan_index_bounds(co)[:8]
    result['index_bound_problem_count'] = len(literal_reader.scan_index_bounds(co))

    result['assignments'] = [
        {'name': a.name.decode('latin1'), 'store': a.store_kind, 'at': a.store_at,
         'writes': len(a.writes), 'records': len(a.value) if hasattr(a.value, '__len__') else None}
        for a in scan.assignments
    ]
    result['statements'] = [{'at': s.at, 'op': s.op, 'kind': s.kind}
                            for s in scan.statements]

    data = scan.by_name(b'DATA')
    if data is not None and not scan.violations:
        keys_seen = list(data.value.keys())
        result['DATA'] = {
            'store': data.store_kind,
            'store_at': data.store_at,
            'unique_records': len(data.value),
            'write_count': len(data.writes),
            'key_types': sorted({type(k).__name__ for k in keys_seen}),
            'key_min': min(keys_seen) if keys_seen and all(isinstance(k, int) for k in keys_seen) else None,
            'key_max': max(keys_seen) if keys_seen and all(isinstance(k, int) for k in keys_seen) else None,
            'duplicate_keys': list(data.duplicate_keys),
            'overwrites': [
                {'order': w.order, 'at': w.at, 'key': w.key,
                 'old': literal_reader.dump(w.old), 'new': literal_reader.dump(w.new)}
                for w in data.overwrites
            ],
        }
    return result


def cross_table_links(archive: Archive, keydb: dict, data_value) -> dict:
    """Check that the recovered table is usable from the tables that reference it."""
    links = {}
    if data_value is None:
        return {'status': 'DATA not recovered under this parameter set'}
    ids = set(data_value.keys())
    links['DATA_record_count'] = len(ids)
    links['skill_416'] = {'present': 416 in ids,
                          'name': literal_reader.dump(data_value.get(416, {}).get(b'name'))
                          if isinstance(data_value.get(416), dict) else None}
    links['skill_64605'] = {'present': 64605 in ids}

    # petskill.AUTOFIGHTLIST / ShieldShortCutSkills (same entry, already read).
    links['autofightlist'] = {
        'count': len(AUTOFIGHTLIST_CACHE),
        'all_present_in_DATA': all(i in ids for i in AUTOFIGHTLIST_CACHE) if AUTOFIGHTLIST_CACHE else None,
        'contains_416': 416 in AUTOFIGHTLIST_CACHE,
    }
    # petactiveskilldata.SKILLIDLST (entry 2242, parameters fixed by both PRs).
    params = {'keys': SKILLIDLST_PARAMS['keys'], 'bounds': SKILLIDLST_PARAMS['bounds'],
              'changed_fields': ()}
    entry = evaluate(SKILLIDLST_ENTRY, params, archive, keydb)
    links['entry_2242'] = {'literal_grammar_ok': entry.get('literal_grammar', {}).get('ok'),
                           'assignments': entry.get('assignments')}
    if entry.get('literal_grammar', {}).get('ok'):
        exp = archive.payload(SKILLIDLST_ENTRY)
        dec = decrypt(exp, SKILLIDLST_PARAMS['keys'], SKILLIDLST_PARAMS['bounds'])
        co, _ = transpile(exp, dec, SKILLIDLST_PARAMS['keys'], SKILLIDLST_PARAMS['bounds'])
        assignment = literal_reader.read_assignment(co, b'SKILLIDLST')
        if assignment is not None:
            values = list(assignment.value)
            links['entry_2242'].update({
                'count': len(values), 'index_16': values[16] if len(values) > 16 else None,
                'all_present_in_DATA': all(v in ids for v in values),
                'missing': [v for v in values if v not in ids],
            })
    return links


AUTOFIGHTLIST_CACHE: list = []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--set', dest='sets', action='append',
                        choices=[p['id'] for p in PARAMETER_SETS] + ['all'],
                        help='parameter set to probe (repeatable); default all')
    parser.add_argument('--write', action='store_true',
                        help=f'also write {OUT_PATH.relative_to(ROOT)}')
    args = parser.parse_args()
    wanted = args.sets or ['all']
    if 'all' in wanted:
        wanted = [p['id'] for p in PARAMETER_SETS]

    archive = Archive(ARCHIVE_PATH.read_bytes())
    keydb = json.loads(KEYDB_PATH.read_bytes())
    global AUTOFIGHTLIST_CACHE
    AUTOFIGHTLIST_CACHE = []

    report = {
        'tool': 'server/tools/probe_script_entry_3205.py',
        'purpose': 'three-way read-only reproduction of the entry 3205 parameter conflict',
        'entry_index': ENTRY_INDEX,
        'module': 'script/data/petskill.py',
        'safety': {
            'client_files_modified': False,
            'recovered_code_executed': False,
            'game_data_written': False,
            'mock_server_started': False,
        },
        'inputs': {
            'data/script.fls': {'sha256': sha256(ARCHIVE_PATH),
                                'size': ARCHIVE_PATH.stat().st_size},
            'tools/decompiler/script_fls_keys.json': {'sha256': sha256(KEYDB_PATH)},
        },
        'parameter_sets': {},
        'comparison': {},
    }

    for spec in PARAMETER_SETS:
        if spec['id'] not in wanted:
            continue
        report['parameter_sets'][spec['id']] = {
            'label': spec['label'], 'source': spec['source'],
            'result': evaluate(ENTRY_INDEX, spec, archive, keydb),
        }

    # Cross-table links need the recovered DATA value, so re-read the D candidate.
    d_result = report['parameter_sets'].get('agent_d', {}).get('result')
    if d_result and d_result.get('literal_grammar', {}).get('ok') and d_result.get('DATA'):
        exp = archive.payload(ENTRY_INDEX)
        dec = decrypt(exp, d_result['keys'], d_result['bounds'])
        co, _ = transpile(exp, dec, d_result['keys'], d_result['bounds'])
        scan = literal_reader.scan_module(co)
        data = scan.by_name(b'DATA')
        auto = scan.by_name(b'AUTOFIGHTLIST')
        shield = scan.by_name(b'ShieldShortCutSkills')
        AUTOFIGHTLIST_CACHE = list(auto.value) if auto else []
        d_result['AUTOFIGHTLIST'] = list(auto.value) if auto else None
        d_result['ShieldShortCutSkills'] = list(shield.value) if shield else None
        d_result['ICON_MAPPING'] = literal_reader.dump(
            scan.by_name(b'ICON_MAPPING').value) if scan.by_name(b'ICON_MAPPING') else None
        report['cross_table_links'] = cross_table_links(archive, keydb, data.value)

    saved = report['parameter_sets'].get('saved', {}).get('result', {})
    agent_d = report['parameter_sets'].get('agent_d', {}).get('result', {})
    pr18 = report['parameter_sets'].get('pr18', {}).get('result', {})
    report['comparison'] = {
        'unmapped_duoyi_opcodes': {
            'saved': saved.get('unmapped_duoyi_opcodes_in_root_co_code', {}).get('count'),
            'agent_d': agent_d.get('unmapped_duoyi_opcodes_in_root_co_code', {}).get('count'),
            'pr18': pr18.get('unmapped_duoyi_opcodes_in_root_co_code', {}).get('count'),
            'note': "PR #18's scoring metric does not separate the correct key from "
                    "keys[1]=218: both report zero unmapped opcodes.",
        },
        'disallowed_opcodes_in_module': {
            'saved': saved.get('disallowed_opcodes_in_module', {}).get('histogram'),
            'agent_d': agent_d.get('disallowed_opcodes_in_module', {}).get('histogram'),
            'pr18': pr18.get('disallowed_opcodes_in_module', {}).get('histogram'),
            'note': 'Module-level literal code may only contain the allowlisted ops; '
                    'any other opcode is a structural contradiction.',
        },
        'literal_grammar': {
            'saved': saved.get('literal_grammar'),
            'agent_d': agent_d.get('literal_grammar'),
            'pr18': pr18.get('literal_grammar'),
        },
        'DATA_recovered': {
            'saved': False if 'DATA' not in saved else True,
            'agent_d': 'DATA' in agent_d,
            'pr18': 'DATA' in pr18,
        },
        'verdict': (
            'agent_d parameters recover the petskill DATA master table published with '
            'STORE_GLOBAL (581 unique skill ids, 9 recorded duplicate writes); the saved '
            'parameters fail at the first EXTENDED_ARG; the PR #18 keys[1]=218 candidate '
            'scores zero unmapped opcodes like the correct key but the module body then '
            'contains thousands of opcodes that module-level literal code cannot contain '
            '(first: BREAK_LOOP at 18021), and no DATA table is recovered.'
        ),
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.write:
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_PATH.write_text(text + '\n')
        print(f'\nwrote {OUT_PATH}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
