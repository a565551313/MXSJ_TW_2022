#!/usr/bin/env python3
"""Read-only, reproducible boundary probes; NOT a production data exporter.

Uses the repository's existing transpiler and marshal reader. No recovered code
is executed. Candidate boundaries are local hypotheses, not verified native
loader behavior. Neither script.fls nor the saved key database is modified.
Run from any directory: python3 server/tools/review_client_data_boundaries.py
The JSON report goes to stdout. Only the Python standard library is required.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder
from tools.fls_batch_decoder import MarshalReader


def instructions(co):
    """Walk normalized Python 2.5 bytecode without executing it."""
    code = co['code']
    at = 0
    extension = 0
    while at < len(code):
        start = at
        op = code[at]
        at += 1
        arg = None
        if op >= 90:
            if at + 2 > len(code):
                raise ValueError(f'truncated instruction at {start}')
            arg = int.from_bytes(code[at:at + 2], 'little') | extension
            at += 2
            if op == 143:
                extension = arg << 16
                continue
            extension = 0
        elif extension:
            raise ValueError('EXTENDED_ARG before argument-free instruction')
        yield start, op, arg
    if extension:
        raise ValueError('dangling EXTENDED_ARG')


def evaluate_literals(co, sequence):
    """Allowlist literal construction only; reject calls/imports/control flow."""
    stack = []
    for at, op, arg in sequence:
        if op == 100:  # LOAD_CONST
            stack.append(co['consts'][arg])
        elif op in (102, 103):  # BUILD_TUPLE / BUILD_LIST
            if arg > len(stack):
                raise ValueError(f'stack underflow at {at}')
            values = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(tuple(values) if op == 102 else list(values))
        elif op == 104:  # BUILD_MAP
            stack.append({})
        elif op == 4:  # DUP_TOP
            stack.append(stack[-1])
        elif op == 2:  # ROT_TWO
            stack[-2], stack[-1] = stack[-1], stack[-2]
        elif op == 60:  # STORE_SUBSCR
            key, target, value = stack.pop(), stack.pop(), stack.pop()
            if type(target) is not dict:
                raise ValueError(f'non-dictionary store at {at}')
            if key in target:
                raise ValueError(f'duplicate dictionary key {key!r} at {at}')
            target[key] = value
        elif op == 90:  # STORE_NAME
            if len(stack) != 1:
                raise ValueError(f'invalid final stack at {at}')
            return stack.pop()
        else:
            raise ValueError(f'unsupported opcode {op} at {at}')
    raise ValueError('missing final STORE_NAME')


def extract_table(co, name=b'DATA'):
    sequence = []
    for instruction in instructions(co):
        sequence.append(instruction)
        _, op, arg = instruction
        if op == 90:
            if co['names'][arg] == name:
                return evaluate_literals(co, sequence)
            sequence = []
    raise ValueError(f'table {name!r} not found')


def readable(value):
    if isinstance(value, bytes):
        try:
            return value.decode('cp950')
        except UnicodeDecodeError:
            return {'invalid_cp950_hex': value.hex(),
                    'escaped_preview': value.decode('cp950', 'backslashreplace')}
    if isinstance(value, (tuple, list)):
        return [readable(v) for v in value]
    if isinstance(value, dict):
        return {str(readable(k)): readable(v) for k, v in value.items()}
    return value


def text_errors(value, path='DATA'):
    errors = []
    if isinstance(value, bytes):
        try:
            value.decode('cp950')
        except UnicodeDecodeError as exc:
            errors.append({'path': path, 'byte_start': exc.start,
                           'byte_end': exc.end, 'raw_hex': value.hex()})
    elif isinstance(value, (tuple, list)):
        for i, child in enumerate(value):
            errors.extend(text_errors(child, f'{path}[{i}]'))
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(text_errors(key, f'{path}.key({key!r})'))
            errors.extend(text_errors(child, f'{path}[{key!r}]'))
    return errors


class Review:
    def __init__(self):
        self.archive = (ROOT / 'data/script.fls').read_bytes()
        self.key_bytes = (ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
        self.keys = json.loads(self.key_bytes)
        self.index_offset = struct.unpack_from('<I', self.archive, 8)[0]

    def payload(self, index):
        entry_id, a, b, c = struct.unpack_from(
            '<IIII', self.archive, self.index_offset + 16 * index)
        size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
        pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
        return zlib.decompress(self.archive[pos:pos + size])

    def load(self, index, bounds=None, use_solver=True):
        metadata = self.keys[str(index)]
        exp = self.payload(index)
        bounds = list(metadata['bounds'] if bounds is None else bounds)
        keys = metadata['keys']
        edges = [0] + bounds + [len(exp)]
        if len(bounds) != 4 or not all(a < b for a, b in zip(edges, edges[1:])):
            raise ValueError('invalid boundary ordering')
        dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[keys[i]])
                       for i in range(5))
        tr = decoder.Py25MarshalTranspiler(dec, exp, keys, bounds)
        if use_solver:
            tr.transpile_object()
        else:
            # Local probe only: don't let the heuristic solver overwrite the
            # boundary under test. This context restores the original function.
            with patch.object(decoder, 'solve_py25_co_span', return_value=None):
                tr.transpile_object()
        reader = MarshalReader(bytes(tr.out)[8:])
        co = reader.read()
        if reader.pos != len(reader.data):
            raise ValueError('marshal reader did not consume the full output')
        return co

    def scan_name_references(self):
        """Literal byte-string search; does not establish runtime use/absence."""
        count = struct.unpack_from('<I', self.archive, 4)[0]
        result = {'needle': 'mxpetdata', 'scanned': 0, 'matches': [], 'errors': [],
                  'limitation': 'Uses saved heuristic keys/bounds; dynamic imports and decoding errors may hide references.'}
        for index in range(count):
            try:
                meta = self.keys[str(index)]
                exp = self.payload(index)
                edges = [0] + meta['bounds'] + [len(exp)]
                dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[meta['keys'][i]])
                               for i in range(5))
                result['scanned'] += 1
                if b'mxpetdata' in dec:
                    result['matches'].append(index)
            except (ValueError, KeyError, IndexError, zlib.error, struct.error) as exc:
                result['errors'].append({'entry_index': index, 'error': str(exc)})
        return result

    def report(self):
        result = {
            'status': 'research_candidates_not_approved_game_data',
            'offset_units': 'zero-based offsets in decompressed XOR payload',
            'archive_sha256': hashlib.sha256(self.archive).hexdigest(),
            'key_database_sha256': hashlib.sha256(self.key_bytes).hexdigest(),
            'baseline': [], 'probes': [],
            'mxpetdata_reference_scan': self.scan_name_references(),
            'limitations': [
                'No recovered script execution or live-client comparison.',
                'The existing transpiler has heuristic repairs; a parsed table is not proof of correctness.',
                'Candidates are not installed in the saved key database or game_data.',
                'Valid CP950 is not sufficient evidence of correct text or numeric values.',
                'This covers selected tables, not the full client.',
            ],
        }
        tables = {}
        for index in (1945, 2027, 1115, 2242, 1698, 3205):
            name = b'SKILLIDLST' if index == 2242 else b'DATA'
            row = {'entry_index': index, 'table': name.decode(),
                   'saved_bounds': self.keys[str(index)]['bounds']}
            try:
                co = self.load(index)
                row['filename'] = readable(co['filename'])
                table = extract_table(co, name)
                tables[index] = table
                row.update(count=len(table), text_errors=text_errors(table),
                           status='literal_table_extracted_not_semantically_verified')
            except (ValueError, IndexError, KeyError, TypeError, struct.error) as exc:
                row.update(status='unresolved', error=f'{type(exc).__name__}: {exc}')
            result['baseline'].append(row)

        # Each probe changes just one boundary. Text candidates were found by
        # local scanning; they are NOT selected solely by a UTF-8/CP950 check.
        specs = [
            (1945, 0, 259583, True, 10424),
            (1945, 3, 1038307, True, 71700),
            (1115, 0, 828, False, 2910),
            (2242, 1, 264, True, 16),
        ]
        for index, boundary, candidate, use_solver, record in specs:
            bounds = self.keys[str(index)]['bounds'].copy()
            old = bounds[boundary]
            bounds[boundary] = candidate
            row = {'entry_index': index, 'boundary_index': boundary,
                   'saved_offset': old, 'candidate_offset': candidate,
                   'automatic_bytecode_solver_enabled': use_solver,
                   'record_id_or_list_index': record,
                   'status': 'candidate_requires_independent_confirmation'}
            try:
                name = b'SKILLIDLST' if index == 2242 else b'DATA'
                changed = extract_table(self.load(index, bounds, use_solver), name)
                baseline = tables[index]
                row.update(before=readable(baseline[record]), after=readable(changed[record]),
                           count_before=len(baseline), count_after=len(changed),
                           text_errors_after=text_errors(changed))
                if isinstance(changed, dict):
                    row['changed_keys'] = [k for k in baseline.keys() | changed.keys()
                                           if baseline.get(k) != changed.get(k)]
                else:
                    row['changed_list_indices'] = [i for i, pair in enumerate(zip(baseline, changed))
                                                   if pair[0] != pair[1]]
            except (ValueError, IndexError, KeyError, TypeError, struct.error) as exc:
                row.update(status='probe_failed', error=f'{type(exc).__name__}: {exc}')
            result['probes'].append(row)

        result['unresolved_item_name'] = {
            'entry_index': 1945, 'record_id': 72548,
            'value': readable(tables[1945][72548][0]),
            'note': 'Invalid final byte is not adjacent to any saved XOR boundary; do not trim or guess.',
        }
        if 1115 in tables and 2027 in tables:
            result['pet_table_differences'] = {
                'only_in_mxpetdata': sorted(tables[1115].keys() - tables[2027].keys()),
                'shared_id_4024': [readable(tables[1115][4024]),
                                  readable(tables[2027][4024][b'name'])],
                'petdata_2910': readable(tables[2027][2910][b'name']),
                'note': 'Cardinality and naming differences are not necessarily errors; caller semantics still unverified.',
            }
        return result


if __name__ == '__main__':
    print(json.dumps(Review().report(), ensure_ascii=False, indent=2))
