#!/usr/bin/env python3
"""Map/NPC static-table reproduction checks (Agent E handover).

Read-only, reproducible verification of the map/scene/NPC findings merged in
PR #16 (`server/docs/csv_checks/AGENT_E.md`). The original probes lived in a
scratch directory that is gone; this module carries them inside the repository.

What it does (for script.fls entries 400, 1301, 1799, 2601, 2804 plus
witnesses 4897 and 1870):

* records the SHA-256 of every input it touches (archive, key database,
  shared decoder tables);
* decodes each entry payload with the *saved* key-database bounds and with
  the *candidate* bounds from the handover, applying four strict criteria
  (bytecode validity with per-code-object limits, marshal-walk consumption,
  allowlist literal evaluation with duplicate-key detection and cp950 text
  checks, cross-table witnesses);
* compares saved parameters against candidate parameters and reports field-
  and reference-level changes;
* supports module-level `STORE_NAME` and `STORE_GLOBAL` assignments;
* supports `LOAD_NAME` only for the single, exact placeholder name `None`
  (the exporter's absent-field idiom). Any other loaded name is a hard
  error - no name lookup or execution is ever attempted;
* can emit candidate staging CSVs (review material, never `server/game_data/`).

Safety constraints honoured: no recovered game script is executed, nothing is
imported from the client, `marshal.loads` is never called (an explicit
offset-tracking walker is used instead), `mock_server.py` is not started, the
key database / shared transpiler / original client files are never modified,
no ID or name is guessed, no record is dropped, no Simplified/Traditional
conversion is performed.

Only the Python standard library is required. The opcode map and XOR tables
are imported read-only from the repository's shared decoder
(`tools/decompiler/batch_decompile.py`); that file is hashed in the evidence
so any change to it invalidates the comparison visibly.

Determinism: `build_evidence()` output depends only on the input files.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Read-only use of the shared decoder's static data tables (binary-extracted
# custom opcode map and per-key XOR translation tables). Not modified here.
from tools.decompiler.batch_decompile import PY25_MAP, XTABS

TOOL_VERSION = '1.0.0'

EXPECTED_ARCHIVE_SHA256 = '8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72'
EXPECTED_KEYDB_SHA256 = '43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb'

# Candidate boundaries from the handover report (AGENT_E.md). "saved" bounds
# are read from the key database at runtime, never hard-coded here.
CANDIDATE_BOUNDS = {
    400: None,  # entry 400 was already correctly framed; saved bounds stand
    1301: [1616, 3239, 4884, 6553],
    1799: [528, 1093, 1652, 2202],
    2601: [18827, 37735, 56546, 75376],
    2804: [26695, 53365, 79989, 106619],
    4897: [26677, 53319, 79961, 106579],  # slot 0 (26677) left as saved: unresolved
    1870: None,  # framing not repaired; stays unresolved
}

# 1301 'delivered_solver': the survey pipeline's span-solver placement that
# produced the delivered anomaly (recorded in AGENT_E.md section 1; this tool
# intentionally contains no heuristic span solver, so the value is pinned).
ALT_1301_DELIVERED_SOLVER = [1615, 3239, 4884, 6553]

EXPECTED_FILENAME = {
    400: b'script\\data\\sceneid2name.py',
    1301: b'script\\data\\mapdata.py',
    1799: b'script\\data\\npcname2realnamedata.py',
    2601: b'script\\data\\npcposdata.py',
    2804: b'script\\data\\minimapnpcpos.py',
    4897: b'script\\data\\minimapnpcpos_test.py',
    1870: b'script\\taiwan\\npcpos_fix.py',
}

# ---------------------------------------------------------------------------
# archive access (same container format as the other repository tools)
# ---------------------------------------------------------------------------

def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Archive:
    def __init__(self, root=ROOT):
        self.archive_path = Path(root) / 'data/script.fls'
        self.keydb_path = Path(root) / 'tools/decompiler/script_fls_keys.json'
        self.decoder_path = Path(root) / 'tools/decompiler/batch_decompile.py'
        self.data = self.archive_path.read_bytes()
        self.keydb_bytes = self.keydb_path.read_bytes()
        self.keydb = json.loads(self.keydb_bytes)
        self.index_offset = struct.unpack_from('<I', self.data, 8)[0]

    def hashes(self):
        return {
            'script_fls': hashlib.sha256(self.data).hexdigest(),
            'script_fls_keys_json': hashlib.sha256(self.keydb_bytes).hexdigest(),
            'batch_decompile_py': sha256_file(self.decoder_path),
        }

    def payload(self, index):
        entry_id, a, b, c = struct.unpack_from(
            '<IIII', self.data, self.index_offset + 16 * index)
        size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
        pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
        return zlib.decompress(self.data[pos:pos + size])

    def entry_count(self):
        return struct.unpack_from('<I', self.data, 4)[0]


def xor_decode(payload, keys, bounds):
    """Plain 5-segment XOR with explicit boundaries. No heuristic repair."""
    edges = [0] + list(bounds) + [len(payload)]
    if len(bounds) != 4 or not all(x < y for x, y in zip(edges, edges[1:])):
        raise ValueError(f'invalid boundary ordering: {list(bounds)}')
    return b''.join(payload[edges[i]:edges[i + 1]].translate(XTABS[keys[i]])
                    for i in range(5))


# ---------------------------------------------------------------------------
# marshal walker (Python 2.5 layout, custom opcodes left untouched)
# ---------------------------------------------------------------------------

class MarshalWalkError(ValueError):
    pass


class Py25MarshalWalker:
    """Offset-tracking Python 2.5 marshal reader.

    `marshal.loads` is deliberately not used: we need absolute payload
    offsets (boundary diagnostics reference them) and we must never hand
    unchecked bytes to the runtime. Strings stay raw bytes (cp950 is applied
    only when rendering evidence). Interned ('t') strings populate the
    reference table resolved by TYPE_STRINGREF ('R'), matching CPython 2.5.
    """

    def __init__(self, data):
        self.d = data
        self.pos = 0
        self.interned = []
        self.code_objects = []

    def take(self, n):
        end = self.pos + n
        if end > len(self.d):
            raise MarshalWalkError(f'marshal truncated at {self.pos}, need {n}')
        chunk = self.d[self.pos:end]
        self.pos = end
        return chunk

    def read(self):
        pos = self.pos
        t = self.d[pos]
        self.pos = pos + 1
        if t in (0x30, 0x4E):      # NULL / None
            return None
        if t == 0x46:
            return False
        if t == 0x54:
            return True
        if t == 0x69:              # 'i'
            return struct.unpack('<i', self.take(4))[0]
        if t == 0x49:              # 'I'
            return struct.unpack('<q', self.take(8))[0]
        if t == 0x6C:              # 'l' long, 15-bit digits
            n = struct.unpack('<i', self.take(4))[0]
            neg = n < 0
            n = abs(n)
            value = 0
            for i in range(n):
                value |= struct.unpack('<H', self.take(2))[0] << (15 * i)
            return -value if neg else value
        if t == 0x66:              # 'f' text float
            ln = struct.unpack('<I', self.take(4))[0]
            return float(self.take(ln).decode('ascii'))
        if t == 0x67:              # 'g' binary float
            return struct.unpack('<d', self.take(8))[0]
        if t in (0x73, 0x74):      # 's' / interned 't'
            ln = struct.unpack('<I', self.take(4))[0]
            value = self.take(ln)
            if t == 0x74:
                self.interned.append(value)
            return value
        if t == 0x75:              # 'u' unicode: keep raw bytes
            ln = struct.unpack('<I', self.take(4))[0]
            return self.take(ln)
        if t == 0x52:              # 'R' string reference
            idx = struct.unpack('<I', self.take(4))[0]
            try:
                return self.interned[idx]
            except IndexError:
                raise MarshalWalkError(f'bad marshal string ref {idx}')
        if t in (0x28, 0x5B):      # '(' tuple / '[' list
            ln = struct.unpack('<I', self.take(4))[0]
            if ln > len(self.d):
                raise MarshalWalkError(
                    f'implausible container length {ln} at {pos}')
            items = [self.read() for _ in range(ln)]
            return tuple(items) if t == 0x28 else items
        if t == 0x7B:              # '{'
            value = {}
            while True:
                key = self.read()
                if key is None:
                    break
                value[key] = self.read()
            return value
        if t == 0x63:              # 'c' code object
            return self._read_code_object(pos)
        raise MarshalWalkError(f'unknown marshal tag 0x{t:02x} at {pos}')

    def _read_code_object(self, start):
        argcount = struct.unpack('<i', self.take(4))[0]
        nlocals = struct.unpack('<i', self.take(4))[0]
        stacksize = struct.unpack('<i', self.take(4))[0]
        flags = struct.unpack('<i', self.take(4))[0]
        code = self.read()
        consts = self.read()
        names = self.read()
        varnames = self.read()
        freevars = self.read()
        cellvars = self.read()
        filename = self.read()
        name = self.read()
        firstlineno = struct.unpack('<i', self.take(4))[0]
        lnotab = self.read()
        record = {'offset': start, 'argcount': argcount, 'nlocals': nlocals,
                  'stacksize': stacksize, 'flags': flags, 'code': code,
                  'consts': consts, 'names': names, 'varnames': varnames,
                  'freevars': freevars, 'cellvars': cellvars,
                  'filename': filename, 'name': name,
                  'firstlineno': firstlineno, 'lnotab': lnotab}
        self.code_objects.append(record)
        return record


# ---------------------------------------------------------------------------
# custom-opcode bytecode walk and strict validity (criterion 1)
# ---------------------------------------------------------------------------

CUSTOM_HAVE_ARGUMENT = 0x5F
OP_LOAD_CONST = 0x8F
OP_LOAD_NAME = 0xAA
OP_STORE_NAME = 0x98
OP_STORE_GLOBAL = 0xC4
OP_BUILD_MAP = 0xBB
OP_BUILD_LIST = 0xCA
OP_BUILD_TUPLE = 0xDE
OP_STORE_SUBSCR = 0x05
OP_DUP_TOP = 0x30
OP_ROT_TWO = 0x5A
OP_EXTENDED_ARG = 0x8B

# std opcode families used for argument-range validation
_STD_CONST_OPS = {100}                                  # LOAD_CONST
_STD_NAME_OPS = {90, 91, 95, 96, 97, 98, 101, 105, 107, 108, 116}
_STD_ABS_JUMPS = {111, 112, 113, 119}                   # JUMP_IF_*, ABS, CONTINUE_LOOP
_STD_REL_JUMPS = {93, 110, 120, 121, 122}               # FOR_ITER, JUMP_FORWARD, SETUP_*


def iter_custom(code):
    """Yield (offset, custom_opcode, arg) without executing anything."""
    at = 0
    extension = 0
    while at < len(code):
        start = at
        op = code[at]
        at += 1
        arg = None
        if op >= CUSTOM_HAVE_ARGUMENT:
            if at + 2 > len(code):
                raise ValueError(f'truncated instruction at {start}')
            arg = int.from_bytes(code[at:at + 2], 'little') | extension
            at += 2
            if op == OP_EXTENDED_ARG:
                extension = arg << 16
                continue
            extension = 0
        elif extension:
            raise ValueError('EXTENDED_ARG before argument-free instruction')
        yield start, op, arg
    if extension:
        raise ValueError('dangling EXTENDED_ARG')


def check_custom_code(co):
    """Criterion 1: mapped opcodes only; args within the code object's own
    limits (n_consts, n_names, code length). Returns (ok, detail)."""
    code = co['code']
    n_consts = len(co['consts'])
    n_names = len(co['names'])
    for at, op, arg in iter_custom(code):
        std = PY25_MAP.get(op)
        if std is None:
            return False, f'unmapped custom opcode 0x{op:02x} at {at}'
        if arg is None:
            continue
        if std in _STD_CONST_OPS and not 0 <= arg < n_consts:
            return False, f'LOAD_CONST arg {arg} outside n_consts {n_consts} at {at}'
        if std in _STD_NAME_OPS and not 0 <= arg < n_names:
            return False, f'name-operation arg {arg} outside n_names {n_names} at {at}'
        if std in _STD_ABS_JUMPS and not 0 <= arg < len(code):
            return False, f'absolute jump target {arg} outside code length {len(code)} at {at}'
        if std in _STD_REL_JUMPS and not 0 <= at + 3 + arg <= len(code):
            return False, f'relative jump target {at + 3 + arg} outside code length {len(code)} at {at}'
    return True, ''


# ---------------------------------------------------------------------------
# allowlist literal evaluation (criterion 3)
# ---------------------------------------------------------------------------

class LiteralReject(ValueError):
    pass


def evaluate_literal(co, sequence):
    """Evaluate one module-level literal segment.

    Allowlist: LOAD_CONST, LOAD_NAME 'None' (the exact placeholder only),
    BUILD_TUPLE, BUILD_LIST, BUILD_MAP, DUP_TOP, ROT_TWO, STORE_SUBSCR,
    terminating STORE_NAME / STORE_GLOBAL. Everything else - calls, imports,
    attribute access, control flow, or any other loaded name - is rejected.
    Duplicate dictionary keys are an error (never silently overwritten).
    """
    stack = []
    for at, op, arg in sequence:
        if op == OP_LOAD_CONST:
            stack.append(co['consts'][arg])
        elif op == OP_LOAD_NAME:
            name = co['names'][arg]
            if name != b'None':
                raise LiteralReject(
                    f'LOAD_NAME {name!r} at {at}: only the exact None placeholder is allowed')
            stack.append(None)
        elif op in (OP_BUILD_TUPLE, OP_BUILD_LIST):
            if arg > len(stack):
                raise LiteralReject(f'stack underflow at {at}')
            values = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(tuple(values) if op == OP_BUILD_TUPLE else list(values))
        elif op == OP_BUILD_MAP:
            stack.append({})
        elif op == OP_DUP_TOP:
            if not stack:
                raise LiteralReject(f'DUP_TOP on empty stack at {at}')
            stack.append(stack[-1])
        elif op == OP_ROT_TWO:
            if len(stack) < 2:
                raise LiteralReject(f'ROT_TWO underflow at {at}')
            stack[-2], stack[-1] = stack[-1], stack[-2]
        elif op == OP_STORE_SUBSCR:
            if len(stack) < 3:
                raise LiteralReject(f'STORE_SUBSCR underflow at {at}')
            key, target, value = stack.pop(), stack.pop(), stack.pop()
            if type(target) is not dict:
                raise LiteralReject(f'non-dictionary store at {at}')
            if key in target:
                raise LiteralReject(f'duplicate dictionary key {key!r} at {at}')
            target[key] = value
        elif op in (OP_STORE_NAME, OP_STORE_GLOBAL):
            if len(stack) != 1:
                raise LiteralReject(f'invalid final stack at {at}')
            return stack.pop()
        else:
            raise LiteralReject(
                f'unsupported opcode 0x{op:02x} (std {PY25_MAP.get(op)}) at {at}')
    raise LiteralReject('missing final STORE_NAME/STORE_GLOBAL')


def extract_assignments(co):
    """Collect every module-level literal store (STORE_NAME / STORE_GLOBAL).

    Returns (tables, failed_stores): tables maps name (bytes) to
    {'value', 'store_op', 'store_at', 'n_instructions'}; failed_stores lists
    the segments that are not pure literals (function definitions etc).
    """
    tables = {}
    failed = []
    sequence = []
    for ins in iter_custom(co['code']):
        sequence.append(ins)
        at, op, arg = ins
        if op in (OP_STORE_NAME, OP_STORE_GLOBAL):
            name = co['names'][arg]
            try:
                tables[name] = {'value': evaluate_literal(co, sequence),
                                'store_op': 'STORE_GLOBAL' if op == OP_STORE_GLOBAL else 'STORE_NAME',
                                'store_at': at,
                                'n_instructions': len(sequence)}
            except LiteralReject as exc:
                failed.append({'name': name, 'store_at': at, 'reason': str(exc)})
            sequence = []
    return tables, failed


# ---------------------------------------------------------------------------
# rendering and small analyses
# ---------------------------------------------------------------------------

def readable(value):
    """cp950 only; invalid byte sequences are preserved as hex, never guessed."""
    if isinstance(value, bytes):
        try:
            return value.decode('cp950')
        except UnicodeDecodeError:
            return {'invalid_cp950_hex': value.hex()}
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
            errors.append({'path': path, 'raw_hex': value.hex(),
                           'byte_start': exc.start, 'byte_end': exc.end})
    elif isinstance(value, (tuple, list)):
        for i, child in enumerate(value):
            errors.extend(text_errors(child, f'{path}[{i}]'))
    elif isinstance(value, dict):
        for key, child in value.items():
            errors.extend(text_errors(key, f'{path}.key({key!r})'))
            errors.extend(text_errors(child, f'{path}[{key!r}]'))
    return errors


def key_type_histogram(table):
    hist = collections.Counter()
    if isinstance(table, dict):
        for key in table:
            hist[type(key).__name__] += 1
    return dict(sorted(hist.items()))


def npc_pair_index_flat(data):
    """2601 shape: {scene -> [records]}. Returns {(scene, npcid): [records]}."""
    pairs = collections.defaultdict(list)
    for scene, records in data.items():
        for record in records:
            if record[2] != 0:
                pairs[(scene, record[2])].append(record)
    return pairs


def npc_pair_index_nested(data):
    """2804 shape: {scene -> {scene display name -> [records]}}."""
    pairs = collections.defaultdict(list)
    for scene, inner in data.items():
        for _name, records in inner.items():
            for record in records:
                if record[2] != 0:
                    pairs[(scene, record[2])].append(record)
    return pairs


def npc_stats(records):
    field_counts = collections.Counter(len(r) for r in records)
    zero = sum(1 for r in records if r[2] == 0)
    missing_pos = sum(1 for r in records if not isinstance(r[4], (tuple, list)))
    return {
        'records': len(records),
        'field_count_histogram': {str(k): v for k, v in sorted(field_counts.items())},
        'records_with_npcid_zero': zero,
        'records_without_xy_position': missing_pos,
        'field7_equals_255_in_all': all(r[7] == 255 for r in records),
        'distinct_shapes': len({r[8] for r in records}),
    }


def multiplicity_histogram(pairs):
    multi = collections.Counter(len(v) for v in pairs.values())
    return {str(k): v for k, v in sorted(multi.items())}


# ---------------------------------------------------------------------------
# entry analysis under one parameter set
# ---------------------------------------------------------------------------

class EntryAnalysis:
    def __init__(self, archive, index, bounds):
        self.archive = archive
        self.index = index
        self.bounds = list(bounds)
        self.error = None
        self.co = None
        self.walker = None
        self.tables = {}
        self.failed_stores = []
        self._run()

    def _run(self):
        try:
            payload = self.archive.payload(self.index)
            self.payload_sha256 = hashlib.sha256(payload).hexdigest()
            meta = self.archive.keydb[str(self.index)]
            decoded = xor_decode(payload, meta['keys'], self.bounds)
            self.decoded_sha256 = hashlib.sha256(decoded).hexdigest()
            walker = Py25MarshalWalker(decoded)
            co = walker.read()
            self.co, self.walker = co, walker
            self.headers_ok = {
                'walk_consumed': walker.pos == len(walker.d),
                'root_is_code': isinstance(co, dict) and 'code' in co,
                'co_name_is_module': co['name'] == b'<module>',
            }
            module_ok, module_detail = check_custom_code(co)
            nested_results = []
            for sub in walker.code_objects:
                if sub is co:
                    continue
                ok, detail = check_custom_code(sub)
                nested_results.append((ok, detail))
            self.code_validity = {
                'module': {'ok': module_ok, 'detail': module_detail},
                'nested_total': len(nested_results),
                'nested_ok': sum(1 for ok, _ in nested_results if ok),
                'first_nested_failure': next((d for ok, d in nested_results if not ok), None),
            }
            self.tables, self.failed_stores = extract_assignments(co)
        except (ValueError, IndexError, KeyError, TypeError, struct.error,
                zlib.error) as exc:
            self.error = f'{type(exc).__name__}: {exc}'

    # -- accessors used by the witnesses -----------------------------------
    def table(self, name):
        return self.tables[name]['value']

    def has_table(self, name):
        return name in self.tables

    def loaded_const_indices(self):
        if self.co is None:
            return set()
        return {arg for _at, op, arg in iter_custom(self.co['code'])
                if op == OP_LOAD_CONST}

    def stranded_const_indices(self):
        """Const indices never referenced by LOAD_CONST anywhere in the
        module code (including function-definition segments)."""
        if self.co is None:
            return []
        loaded = self.loaded_const_indices()
        return [i for i in range(len(self.co['consts'])) if i not in loaded]

    def summary(self):
        if self.error:
            return {'bounds': self.bounds, 'status': 'decode_error', 'error': self.error}
        tables = {}
        for name in sorted(self.tables):
            info = self.tables[name]
            value = info['value']
            row = {'rows': len(value) if hasattr(value, '__len__') else None,
                   'store_op': info['store_op'], 'store_at': info['store_at'],
                   'n_instructions': info['n_instructions'],
                   'key_types': key_type_histogram(value)}
            errors = text_errors(value, str(readable(name)))
            if errors:
                row['text_errors'] = errors
            tables[readable(name)] = row
        return {
            'bounds': self.bounds,
            'status': 'decoded',
            'payload_sha256': self.payload_sha256,
            'decoded_sha256': self.decoded_sha256,
            'co_filename': readable(self.co['filename']),
            'co_name_is_module': self.headers_ok['co_name_is_module'],
            'walk_consumed': self.headers_ok['walk_consumed'],
            'module_code_valid': self.code_validity['module'],
            'nested_code_objects': self.code_validity['nested_total'],
            'nested_code_valid': self.code_validity['nested_ok'],
            'first_nested_failure': self.code_validity['first_nested_failure'],
            'tables': tables,
            'failed_literal_stores': [
                {'name': readable(f['name']), 'reason': f['reason']}
                for f in self.failed_stores],
            'stranded_consts': len(self.stranded_const_indices()),
        }


# ---------------------------------------------------------------------------
# cross-table witnesses (criterion 4)
# ---------------------------------------------------------------------------

def compare_pair_join(pairs_a, pairs_b):
    """List-valued (scene, npcid) join with BOTH comparison semantics kept
    explicit: sequence-sensitive and order-insensitive (multiset)."""
    common = set(pairs_a) & set(pairs_b)
    seq_identical = sorted(k for k in common if pairs_a[k] == pairs_b[k])
    multiset_identical = sorted(k for k in common
                                if sorted(pairs_a[k]) == sorted(pairs_b[k]))
    order_only = [k for k in multiset_identical if k not in seq_identical]
    content_diff = [k for k in common if k not in multiset_identical]
    return {
        'pairs_a': len(pairs_a), 'pairs_b': len(pairs_b),
        'common_pairs': len(common),
        'sequence_identical': len(seq_identical),
        'multiset_identical': len(multiset_identical),
        'order_only_differences': sorted(map(list, order_only)),
        'content_differences': sorted(map(list, content_diff)),
        'only_in_a': sorted(map(list, set(pairs_a) - set(pairs_b))),
        'only_in_b': sorted(map(list, set(pairs_b) - set(pairs_a))),
    }


def witness_bundle(archive, analyses):
    """Cross-table checks under candidate bounds. `analyses` maps
    entry index -> EntryAnalysis at candidate bounds."""
    out = {}

    a1301 = analyses[1301]
    a400 = analyses[400]
    mapdata = a1301.table(b'DATA') if a1301.has_table(b'DATA') else {}
    minimap = a400.table(b'DATA') if a400.has_table(b'DATA') else {}
    shared = sorted(set(minimap) & set(mapdata))
    out['mapdata_vs_sceneid2name'] = {
        'minimap_keys': len(minimap),
        'mapdata_keys': len(mapdata),
        'minimap_keys_in_mapdata': len(shared),
        'key_1071_in_mapdata': 1071 in mapdata,
        'name_mismatches': sorted(k for k in shared
                                  if mapdata[k][b'name'] != minimap[k][0]),
        'data_1071': readable(mapdata.get(1071)),
        'map_ascription': readable(a1301.table(b'MAP_ASCRIPTION'))
        if a1301.has_table(b'MAP_ASCRIPTION') else None,
    }

    d2601 = analyses[2601].table(b'DATA')
    pos2804 = analyses[2804].table(b'DATA_POS')
    wz2804 = analyses[2804].table(b'DATA_WENZI')
    pairs2601 = npc_pair_index_flat(d2601)
    pairs2804 = npc_pair_index_nested(pos2804)
    join = compare_pair_join(pairs2601, pairs2804)
    join['content_difference_detail'] = [
        {'pair': list(k),
         'npcposdata': readable(pairs2601[k]),
         'minimapnpcpos': readable(pairs2804[k])}
        for k in map(tuple, join['content_differences'])]
    out['npcposdata_vs_minimapnpcpos'] = join

    # 4897 as witness for 2804 slot 2 and for the DATA_WENZI schema
    wz4897 = analyses[4897].table(b'DATA_WENZI')
    pos4897 = analyses[4897].table(b'DATA_POS')
    shared_wz = sorted(set(wz2804) & set(wz4897))
    out['minimapnpcpos_vs_test_sibling'] = {
        'wenzi_scenes_2804': len(wz2804),
        'wenzi_scenes_4897': len(wz4897),
        'wenzi_identical_scenes': sum(1 for s in shared_wz
                                      if wz2804[s] == wz4897[s]),
        'wenzi_only_in_2804': sorted(set(wz2804) - set(wz4897)),
        'pair_join_vs_4897': compare_pair_join(
            pairs2804, npc_pair_index_nested(pos4897)),
    }

    # 1799 alias table against both NPC tables (field 0 / field 11)
    alias = analyses[1799].table(b'DATA')

    def alias_check(flat_records):
        total_alias = 0
        aliases_used = set()
        f11_set = 0
        f11_and_alias = 0
        agree = 0
        mismatches = []
        for scene, rec in flat_records:
            if rec[0] in alias:
                total_alias += 1
                aliases_used.add(rec[0])
            if rec[11] is not None:
                f11_set += 1
                if rec[0] in alias:
                    f11_and_alias += 1
                    if alias[rec[0]] == rec[11]:
                        agree += 1
                    else:
                        mismatches.append({'scene': scene, 'npcid': rec[2],
                                           'alias': readable(rec[0]),
                                           'alias_table_says': readable(alias[rec[0]]),
                                           'record_says': readable(rec[11])})
        return {
            'records_with_alias_in_1799': total_alias,
            'aliases_used': len(aliases_used),
            'records_with_real_name_set': f11_set,
            'real_name_set_and_alias_in_1799': f11_and_alias,
            'alias_realname_agreements': agree,
            'alias_realname_mismatches': mismatches,
            'real_name_set_but_alias_not_in_1799': f11_set - f11_and_alias,
        }

    flat2601 = [(sc, r) for sc, recs in d2601.items() for r in recs]
    flat2804 = [(sc, r) for sc, inner in pos2804.items()
                for _nm, recs in inner.items() for r in recs]
    out['alias_table_vs_npcposdata'] = alias_check(flat2601)
    out['alias_table_vs_minimapnpcpos'] = alias_check(flat2804)

    # 2804's own DATA_POS must attest const[544] == 打漁老張, and so does 2601
    target = [r for r in d2601.get(1020, []) if r[2] == 4229]
    target_pos = [r for _nm, recs in pos2804.get(1020, {}).items()
                  for r in recs if r[2] == 4229]
    out['fisher_name_attestation'] = {
        'const544_of_2804': readable(analyses[2804].co['consts'][544]),
        'record_2601_1020_4229': readable(target),
        'record_2804_1020_4229': readable(target_pos),
    }
    return out


# ---------------------------------------------------------------------------
# saved vs candidate: explicit field- and reference-level changes
# ---------------------------------------------------------------------------

_MISSING = object()


def summarize_value(value, limit=160):
    text = json.dumps(readable(value), ensure_ascii=False, sort_keys=True,
                      default=str)
    return text if len(text) <= limit else text[:limit] + '…'


def compare_tables(before, after):
    """Row-level diff of two evaluated tables. Never merges, never drops:
    added/removed/changed top-level keys are all reported."""
    result = {'added_keys': [], 'removed_keys': [], 'changed_keys': []}
    if not isinstance(before, dict) or not isinstance(after, dict):
        result['note'] = 'comparison implemented for dict tables only'
        return result
    for key in sorted(set(after) - set(before), key=str):
        result['added_keys'].append({'key': readable(key),
                                     'after': summarize_value(after[key])})
    for key in sorted(set(before) - set(after), key=str):
        result['removed_keys'].append({'key': readable(key),
                                       'before': summarize_value(before[key])})
    for key in sorted(set(before) & set(after), key=str):
        if before[key] != after[key]:
            result['changed_keys'].append({'key': readable(key),
                                           'before': summarize_value(before[key]),
                                           'after': summarize_value(after[key])})
    return result


def build_parameter_comparisons(archive, parameter_sets):
    """For every entry with a candidate set, diff each non-candidate parameter
    set against the candidate one, and list reference-level changes (const
    pool entry, co_name) that sit outside the data tables themselves."""
    comparisons = {}
    reference_interest = {
        1301: [],  # the story is the DATA key set itself
        1799: [31, 74],
        2601: [179],
        2804: [544],
        4897: [],
    }
    for index, sets in parameter_sets.items():
        candidate = sets.get('candidate')
        if candidate is None:
            continue
        after = EntryAnalysis(archive, index, candidate)
        rows = {}
        for label, bounds in sets.items():
            if label == 'candidate':
                continue
            before = EntryAnalysis(archive, index, bounds)
            row = {'before_label': label, 'before_bounds': list(bounds)}
            if before.error:
                row['before_status'] = f'decode_error: {before.error}'
            else:
                row['before_status'] = 'decoded'
                table_diffs = {}
                names = sorted(set(after.tables) | set(before.tables))
                for name in names:
                    if name not in after.tables:
                        table_diffs[readable(name)] = 'only under before-parameters'
                    elif name not in before.tables:
                        table_diffs[readable(name)] = 'only under candidate parameters'
                    elif before.tables[name]['value'] != after.tables[name]['value']:
                        table_diffs[readable(name)] = compare_tables(
                            before.tables[name]['value'], after.tables[name]['value'])
                row['table_changes'] = table_diffs
                row['co_name'] = {'before': readable(before.co['name']),
                                  'candidate': readable(after.co['name'])}
                if index in reference_interest and reference_interest[index]:
                    refs = []
                    for ci in reference_interest[index]:
                        refs.append({'const_index': ci,
                                     'before': readable(before.co['consts'][ci]),
                                     'candidate': readable(after.co['consts'][ci])})
                    row['reference_changes'] = refs
            rows[label] = row
        comparisons[str(index)] = rows
    return comparisons


# ---------------------------------------------------------------------------
# semantics re-checks for the handover (business meaning, kept unresolved)
# ---------------------------------------------------------------------------

def semantics_bundle(mapdata, minimap, d2601, pos2804):
    out = {}

    # 400's second column (`related_id`): reproduced numbers only.
    diff_rows = {k: v for k, v in minimap.items() if v[1] != k}
    rel_in_catalog = [k for k, v in minimap.items() if v[1] in mapdata]
    agree = sum(1 for k in rel_in_catalog
                if mapdata[minimap[k][1]][b'name'] == minimap[k][0])
    out['sceneid2name_second_column'] = {
        'rows_where_related_id_differs_from_key': len(diff_rows),
        'those_keys': sorted(diff_rows),
        'related_values': {str(k): minimap[k][1] for k in sorted(diff_rows)},
        'related_id_that_is_also_a_catalog_key': len(rel_in_catalog),
        'of_those_name_agreements': agree,
        'status': 'unresolved_meaning_not_established',
    }

    # 400 vs 1301 size pairs
    swapped, identical, other = [], [], []
    for k in minimap:
        pair400 = (minimap[k][2], minimap[k][3])
        pair1301 = (mapdata[k][b'w'], mapdata[k][b'h'])
        if pair400 == pair1301:
            identical.append(k)
        elif pair400 == (pair1301[1], pair1301[0]):
            swapped.append(k)
        else:
            other.append(k)
    out['size_pair_comparison'] = {
        'identical': len(identical),
        'axis_transposed': sorted(swapped),
        'different_values': sorted(other),
        'status': 'tables_do_not_share_a_size_semantics_keep_both_columns',
    }

    # coordinate scale: no conversion factor exists (rough corroboration)
    ratios_w = []
    for scene, records in d2601.items():
        xs = [r[4][0] for r in records if isinstance(r[4], (tuple, list))]
        if scene in mapdata and xs and max(xs):
            ratios_w.append(mapdata[scene][b'w'] / max(xs))
    ratios_w.sort()
    out['coordinate_scale_probe'] = {
        'scenes_compared': len(ratios_w),
        'median_map_w_over_max_npc_x': round(ratios_w[len(ratios_w) // 2], 1)
        if ratios_w else None,
        'p10': round(ratios_w[len(ratios_w) // 10], 1) if ratios_w else None,
        'status': 'no_single_scale_factor_coordinates_live_in_separate_frames',
    }

    # npc id reuse across scenes
    def reuse(pairs):
        scenes_by_id = collections.defaultdict(set)
        for (scene, npcid) in pairs:
            scenes_by_id[npcid].add(scene)
        multi = sorted(nid for nid, scs in scenes_by_id.items() if len(scs) > 1)
        return {'distinct_npcids': len(scenes_by_id),
                'npcids_in_multiple_scenes': len(multi),
                'examples': multi[:12]}
    out['npcid_reuse'] = {'npcposdata': reuse(npc_pair_index_flat(d2601)),
                          'minimapnpcpos': reuse(npc_pair_index_nested(pos2804))}
    return out


# ---------------------------------------------------------------------------
# runtime-mutation static evidence (no execution)
# ---------------------------------------------------------------------------

def runtime_mutation_evidence(analysis2804):
    evidence = {}
    wanted = [b'InitTestData', b'GetData', b'GetMapNpcNames', b'DelShenHeNpc']
    for sub in analysis2804.walker.code_objects:
        if sub['name'] in wanted:
            consts = [readable(c) for c in sub['consts']
                      if not isinstance(c, dict) and c is not None][:24]
            evidence[sub['name'].decode()] = {
                'names': sorted(readable(n) for n in sub['names']),
                'first_constants': consts,
                'reading': {
                    'InitTestData': 'inserts a 14-field record (npcid 5025, 戰隊使者) into DATA_POS[1054]',
                    'GetData': 'rewrites map 1054 -> 1055 on freshman servers, then filters via DelShenHeNpc',
                    'GetMapNpcNames': 'applies the same 1054 -> 1055 freshman-server rewrite',
                    'DelShenHeNpc': 'filters the returned record lists when hero.IsShenHe()',
                }[sub['name'].decode()],
            }
    evidence['_scope'] = ('Static evidence only: these are nested code objects of entry 2804. '
                          'Whether and when they run is client behaviour; staged CSVs are the '
                          'pre-mutation state.')
    return evidence


def name_reference_scan(archive):
    """Heuristic byte-substring scan over XOR-decoded payloads (saved bounds).

    Presence evidence only; corrupted boundaries can hide references, and
    plain strings (not just co_names) can match. Documented as a lead that
    corroborates the consumer claims, not as proof of import."""
    needles = [b'mapdata', b'sceneid2name', b'npcname2realnamedata',
               b'npcposdata', b'minimapnpcpos', b'InitTestData',
               b'DelShenHeNpc', b'IsNeedDelShenHeNpc']
    hits = collections.defaultdict(list)
    errors = []
    for index in range(archive.entry_count()):
        meta = archive.keydb.get(str(index))
        if meta is None:
            errors.append(index)
            continue
        try:
            decoded = xor_decode(archive.payload(index), meta['keys'], meta['bounds'])
        except (ValueError, IndexError, KeyError, struct.error, zlib.error):
            errors.append(index)
            continue
        for needle in needles:
            if needle in decoded:
                hits[needle.decode()].append(index)
    return {
        'method': 'byte substring over XOR-decoded payload with saved bounds',
        'limitation': 'presence only; not co_names-verified; misframed entries may hide hits',
        'entries_scanned': archive.entry_count() - 0,
        'decode_failures': sorted(errors),
        'hits': {k: sorted(v) for k, v in sorted(hits.items())},
    }


# ---------------------------------------------------------------------------
# parameter-set verification (criteria 1-4 wrapped into one verdict)
# ---------------------------------------------------------------------------

def verify_entry(archive, index, bounds, witnesses=None):
    """Run the strict criteria for one entry under one parameter set.

    Returns a verdict dict. Criterion 4 (witnesses) are entry-specific
    expectations that a *correct* framing must satisfy; they are what stops a
    merely "valid cp950" misframe from passing."""
    a = EntryAnalysis(archive, index, bounds)
    verdict = {'entry': index, 'bounds': list(bounds), 'checks': {}, 'pass': False}
    if a.error:
        verdict['checks']['decode'] = {'ok': False, 'detail': a.error}
        return verdict
    verdict['checks']['marshal_walk_consumed'] = {'ok': a.headers_ok['walk_consumed']}
    verdict['checks']['module_bytecode'] = dict(a.code_validity['module'])
    verdict['checks']['nested_bytecode'] = {
        'ok': a.code_validity['nested_ok'] == a.code_validity['nested_total'],
        'ok_count': a.code_validity['nested_ok'],
        'total': a.code_validity['nested_total'],
        'first_failure': a.code_validity['first_nested_failure'],
    }
    literal_failures = [f for f in a.failed_stores
                        if f['name'] in (b'DATA', b'DATA_POS', b'DATA_WENZI',
                                         b'MAP_ASCRIPTION')]
    verdict['checks']['target_literals_evaluate'] = {
        'ok': not literal_failures,
        'failures': [{'name': readable(f['name']), 'reason': f['reason']}
                     for f in literal_failures]}
    texts = []
    for name, info in a.tables.items():
        if name in (b'DATA', b'DATA_POS', b'DATA_WENZI', b'MAP_ASCRIPTION'):
            texts.extend(text_errors(info['value'], str(readable(name))))
    verdict['checks']['cp950_clean'] = {'ok': not texts, 'errors': texts[:8]}

    witness_failures = []
    if witnesses:
        for label, fn in witnesses.items():
            try:
                ok, detail = fn(a)
            except (KeyError, IndexError, TypeError, ValueError) as exc:
                ok, detail = False, f'{type(exc).__name__}: {exc}'
            verdict['checks'][f'witness:{label}'] = {'ok': bool(ok), 'detail': detail}
            if not ok:
                witness_failures.append(label)
    verdict['witness_failures'] = witness_failures
    verdict['pass'] = all(c.get('ok') for c in verdict['checks'].values())
    return verdict


def _expect_400(a, ref):
    reasons = []
    data = a.table(b'DATA')
    if len(data) != 57:
        reasons.append(f'DATA rows {len(data)} != 57')
    if not all(type(k) is int for k in data):
        reasons.append('DATA has non-integer keys')
    if not all(type(v) is tuple and len(v) == 4 for v in data.values()):
        reasons.append('not every row is a 4-tuple constant')
    if 1071 not in data:
        reasons.append('key 1071 missing')
    return (not reasons), '; '.join(reasons) or 'ok'


def _expect_1301(a, ref):
    reasons = []
    data = a.table(b'DATA')
    expected_1071 = {b'name': '加洛法師師道殿'.encode('cp950'), b'w': 1588, b'h': 1220}
    if not all(type(k) is int for k in data):
        reasons.append('DATA has non-integer keys')
    if len(data) != 104:
        reasons.append(f'DATA rows {len(data)} != 104')
    if data.get(1071) != expected_1071:
        reasons.append('DATA[1071] is not the expected 加洛法師師道殿 record')
    stranded = [i for i in a.stranded_const_indices() if a.co['consts'][i] == 1071]
    if stranded:
        reasons.append(f'constant 1071 is stranded (const index {stranded})')
    names_ok = all(data[k][b'name'] == ref[400].table(b'DATA')[k][0]
                   for k in ref[400].table(b'DATA'))
    if not names_ok:
        reasons.append('scene names disagree with entry 400')
    return (not reasons), '; '.join(reasons) or 'ok'


def _expect_1799(a, ref):
    reasons = []
    data = a.table(b'DATA')
    if len(data) != 55:
        reasons.append(f'DATA rows {len(data)} != 55')
    if data.get('個人心法教師'.encode('cp950')) != '元靈遊仙'.encode('cp950'):
        reasons.append('個人心法教師 does not map to 元靈遊仙')
    if data.get('天選使者'.encode('cp950')) != '明威'.encode('cp950'):
        reasons.append('天選使者 does not map to 明威')
    if not a.headers_ok['co_name_is_module']:
        reasons.append('co_name is not <module>')
    if text_errors(data):
        reasons.append('invalid cp950 constants remain')
    return (not reasons), '; '.join(reasons) or 'ok'


def _expect_2601(a, ref):
    reasons = []
    data = a.table(b'DATA')
    records = [r for recs in data.values() for r in recs]
    if len(data) != 430:
        reasons.append(f'scenes {len(data)} != 430')
    if len(records) != 1335:
        reasons.append(f'records {len(records)} != 1335')
    if not all(len(r) == 14 for r in records):
        reasons.append('not every record has 14 fields')
    if sum(1 for r in records if r[2] == 0) != 632:
        reasons.append('npcid==0 count is not 632')
    pairs = npc_pair_index_flat(data)
    if len(pairs) != 665:
        reasons.append(f'distinct (scene, npcid) pairs {len(pairs)} != 665')
    fisherman = [r[2] for r in data.get(1003, []) if r[0] == '谷雨鎮商人'.encode('cp950')]
    if 4764 not in fisherman:
        reasons.append(f'谷雨鎮商人 npcid 4764 not attested (saw {fisherman})')
    if 4764 in fisherman and ref is not None and (1003, 4764) not in npc_pair_index_nested(
            ref[2804].table(b'DATA_POS')):
        reasons.append('(1003, 4764) not corroborated by entry 2804')
    return (not reasons), '; '.join(reasons) or 'ok'


def _expect_2804(a, ref):
    reasons = []
    if a.has_table(b'DATA'):
        reasons.append('module unexpectedly exposes DATA')
    pos = a.table(b'DATA_POS')
    wz = a.table(b'DATA_WENZI')
    records = [r for inner in pos.values() for recs in inner.values() for r in recs]
    if len(pos) != 434 or len(records) != 1344:
        reasons.append(f'DATA_POS shape {len(pos)}/{len(records)} != 434/1344')
    if len(wz) != 165 or sum(len(v) for v in wz.values()) != 287:
        reasons.append('DATA_WENZI shape != 165 scenes/287 entries')
    if a.co['consts'][544] != '打漁老張'.encode('cp950'):
        reasons.append(f'const[544] decodes to {readable(a.co["consts"][544])}, not 打漁老張')
    port = wz.get(1022, {}).get((28, 108))
    if port is None or port.get(b'npcID') != 2008:
        reasons.append(f'WENZI[1022][(28,108)] npcID is {port and readable(port.get(b"npcID"))}, not 2008')
    fisherman = [r for inner in pos.get(1020, {}).values()
                 for r in inner if r[2] == 4229]
    if not fisherman or fisherman[0][0] != '打漁老張'.encode('cp950'):
        reasons.append('DATA_POS does not attest 打漁老張 at (1020, 4229)')
    if ref is not None:
        wz4897 = ref[4897].table(b'DATA_WENZI')
        if any(wz[s] != wz4897.get(s) for s in wz):
            reasons.append('DATA_WENZI disagrees with the 4897 witness sibling')
    return (not reasons), '; '.join(reasons) or 'ok'


def _expect_4897(a, ref):
    reasons = []
    pos = a.table(b'DATA_POS')
    wz = a.table(b'DATA_WENZI')
    failed_names = {f['name'] for f in a.failed_stores}
    if b'DATA_WENZI' in failed_names:
        reasons.append('DATA_WENZI literal does not evaluate')
    if len(pos) != 433 or len(wz) != 165:
        reasons.append(f'shapes {len(pos)}/{len(wz)} != 433/165')
    return (not reasons), '; '.join(reasons) or 'ok'


# ---------------------------------------------------------------------------
# evidence assembly
# ---------------------------------------------------------------------------

def build_parameter_sets(archive):
    sets = {}
    for index in (400, 1301, 1799, 2601, 2804, 4897, 1870):
        saved = list(archive.keydb[str(index)]['bounds'])
        entry = {'saved': saved}
        if CANDIDATE_BOUNDS.get(index):
            entry['candidate'] = CANDIDATE_BOUNDS[index]
        if index == 1301:
            entry['delivered_solver'] = ALT_1301_DELIVERED_SOLVER
        if index == 2601:
            cand = CANDIDATE_BOUNDS[2601]
            entry['saved_slot3_only'] = cand[:3] + [saved[3]]
        if index == 2804:
            cand = CANDIDATE_BOUNDS[2804]
            entry['saved_slot2_only'] = saved[:3] + [cand[3]]
            entry['saved_slot3_only'] = cand[:3] + [saved[3]]
        sets[index] = entry
    return sets


def build_evidence(archive, with_scan=True):
    parameter_sets = build_parameter_sets(archive)

    candidate_analyses = {}
    for index in (400, 1301, 1799, 2601, 2804, 4897, 1870):
        bounds = parameter_sets[index]['candidate' if CANDIDATE_BOUNDS.get(index) else 'saved']
        candidate_analyses[index] = EntryAnalysis(archive, index, bounds)

    witnesses = {
        400: {'minimap_table': lambda a: _expect_400(a, candidate_analyses)},
        1301: {'catalog': lambda a: _expect_1301(a, candidate_analyses)},
        1799: {'alias_rows': lambda a: _expect_1799(a, candidate_analyses)},
        2601: {'structure_and_fisherman': lambda a: _expect_2601(a, candidate_analyses)},
        2804: {'tables_and_constants': lambda a: _expect_2804(a, candidate_analyses)},
        4897: {'test_sibling': lambda a: _expect_4897(a, candidate_analyses)},
    }

    verifications = {}
    analysis_summaries = {}
    for index, sets in parameter_sets.items():
        verifications[str(index)] = {}
        analysis_summaries[str(index)] = {}
        for label, bounds in sets.items():
            ref = candidate_analyses if witnesses.get(index) else None
            v = verify_entry(archive, index, bounds,
                             witnesses=witnesses.get(index))
            verifications[str(index)][label] = v
            analysis_summaries[str(index)][label] = EntryAnalysis(
                archive, index, bounds).summary()

    bundle = witness_bundle(archive, candidate_analyses)
    npc2601 = npc_stats([r for recs in candidate_analyses[2601].table(b'DATA').values()
                         for r in recs])
    rec2804 = [r for inner in candidate_analyses[2804].table(b'DATA_POS').values()
               for recs in inner.values() for r in recs]
    npc2804 = npc_stats(rec2804)

    evidence = {
        'tool': {'name': 'server/tools/map_npc_reproduction.py',
                 'version': TOOL_VERSION,
                 'status': 'candidates_reproduced_statically_not_native_loader_verified'},
        'inputs': {
            'archive': {'path': 'data/script.fls',
                        'sha256': archive.hashes()['script_fls'],
                        'expected_sha256': EXPECTED_ARCHIVE_SHA256,
                        'matches_expected': archive.hashes()['script_fls'] == EXPECTED_ARCHIVE_SHA256},
            'key_database': {'path': 'tools/decompiler/script_fls_keys.json',
                             'sha256': archive.hashes()['script_fls_keys_json'],
                             'expected_sha256': EXPECTED_KEYDB_SHA256,
                             'matches_expected': archive.hashes()['script_fls_keys_json'] == EXPECTED_KEYDB_SHA256},
            'shared_decoder': {'path': 'tools/decompiler/batch_decompile.py',
                               'sha256': archive.hashes()['batch_decompile_py'],
                               'used_read_only_for': ['PY25_MAP opcode table', 'XTABS xor tables']},
        },
        'parameter_sets': {str(k): v for k, v in parameter_sets.items()},
        'expected_co_filename': {str(k): readable(v) for k, v in EXPECTED_FILENAME.items()},
        'analyses_under_each_parameter_set': analysis_summaries,
        'verifications': verifications,
        'parameter_comparisons': build_parameter_comparisons(archive, parameter_sets),
        'npc_structure': {
            'npcposdata_2601': {**npc2601,
                                'distinct_pairs': len(npc_pair_index_flat(candidate_analyses[2601].table(b'DATA'))),
                                'multiplicity_histogram': multiplicity_histogram(npc_pair_index_flat(candidate_analyses[2601].table(b'DATA')))},
            'minimapnpcpos_2804': {**npc2804,
                                   'distinct_pairs': len(npc_pair_index_nested(candidate_analyses[2804].table(b'DATA_POS'))),
                                   'multiplicity_histogram': multiplicity_histogram(npc_pair_index_nested(candidate_analyses[2804].table(b'DATA_POS')))},
        },
        'cross_table_witnesses': bundle,
        'semantics_recheck': semantics_bundle(
            candidate_analyses[1301].table(b'DATA'),
            candidate_analyses[400].table(b'DATA'),
            candidate_analyses[2601].table(b'DATA'),
            candidate_analyses[2804].table(b'DATA_POS')),
        'runtime_mutation_static_evidence': runtime_mutation_evidence(candidate_analyses[2804]),
        'entry_1870': {
            'bounds_used': parameter_sets[1870]['saved'],
            'co_names': readable(candidate_analyses[1870].co['names'])
            if candidate_analyses[1870].co else None,
            'note': ('Framing NOT repaired (two clean placements for slot 0 could not be '
                     'discriminated). The corrupted co_names entry is displayed as evidence; '
                     'Fix() binding semantics must not be quoted. Stays unresolved.'),
        },
        'limitations': [
            'candidate framings are static reproductions; the native client loader was never run',
            'no recovered script executed; no exec/eval/marshal.loads; read-only on client files',
            'LOAD_NAME support is restricted to the exact placeholder name None',
            'no ID or name guessed; zero-npcid and duplicate records retained; no table merging',
        ],
    }
    if with_scan:
        evidence['consumer_name_reference_scan'] = name_reference_scan(archive)
    return evidence


# ---------------------------------------------------------------------------
# staging CSV emission (review material; never into server/game_data/)
# ---------------------------------------------------------------------------

NPC_FIELD_NAMES = ['display_name', 'secondary_name', 'npcid', 'type', 'x', 'y',
                   'field5', 'field6', 'field7_const255', 'shape', 'field9',
                   'field10', 'real_name', 'field12', 'field13']


def _cell(value):
    if value is None:
        return ''
    if isinstance(value, bytes):
        return value.decode('cp950')
    if isinstance(value, (tuple, list)):
        return '|'.join(str(v) for v in value)
    return value


def _npc_row(prefix, record):
    r = list(record)
    pos = r[4] if isinstance(r[4], (tuple, list)) else ('', '')
    values = r[:4] + [pos[0], pos[1]] + r[5:]
    return prefix + [_cell(v) for v in values]


def write_staging_csvs(analyses, out_dir, archive=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written = []

    def dump(name, header, rows):
        path = out / name
        with path.open('w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)
        written.append(name)

    mapdata = analyses[1301].table(b'DATA')
    ascription = analyses[1301].table(b'MAP_ASCRIPTION')
    dump('mapdata_scene_dictionary.csv', ['scene_id', 'name', 'w', 'h'],
         [[k, _cell(v[b'name']), v[b'w'], v[b'h']] for k, v in sorted(mapdata.items())])
    dump('mapdata_parent_scene.csv', ['scene_id', 'parent_scene_id'],
         [[k, v] for k, v in sorted(ascription.items())])

    minimap = analyses[400].table(b'DATA')
    dump('sceneid2name_minimap_scenes.csv',
         ['scene_id', 'name', 'related_id_unresolved', 'size_a', 'size_b'],
         [[k, _cell(v[0]), v[1], v[2], v[3]] for k, v in sorted(minimap.items())])

    alias = analyses[1799].table(b'DATA')
    dump('npcname2realnamedata_alias_to_realname.csv', ['alias', 'real_name'],
         [[_cell(k), _cell(v)] for k, v in sorted(alias.items())])

    d2601 = analyses[2601].table(b'DATA')
    rows = []
    for scene in sorted(d2601):
        for i, rec in enumerate(d2601[scene]):
            rows.append(_npc_row([scene, i], rec))
    dump('npcposdata_records.csv', ['scene_id', 'record_index'] + NPC_FIELD_NAMES, rows)

    pos2804 = analyses[2804].table(b'DATA_POS')
    rows = []
    for scene in sorted(pos2804):
        for disp in sorted(pos2804[scene]):
            for i, rec in enumerate(pos2804[scene][disp]):
                rows.append(_npc_row([scene, _cell(disp), i], rec))
    dump('minimapnpcpos_pos_records.csv',
         ['scene_id', 'scene_display_name', 'record_index'] + NPC_FIELD_NAMES, rows)

    wz2804 = analyses[2804].table(b'DATA_WENZI')
    rows = []
    for scene in sorted(wz2804):
        for (x, y) in sorted(wz2804[scene]):
            v = wz2804[scene][(x, y)]
            jp = v.get(b'jumpPos') or ('', '')
            rows.append([scene, x, y, _cell(v.get(b'name')), _cell(v.get(b'desc')),
                         jp[0] if jp != ('', '') else '', jp[1] if jp != ('', '') else '',
                         v.get(b'npcID'), _cell(v.get(b'npcName')),
                         v.get(b'servergrade')])
    dump('minimapnpcpos_wenzi_entries.csv',
         ['scene_id', 'x', 'y', 'name', 'desc', 'jump_x', 'jump_y', 'npcID',
          'npcName', 'servergrade'], rows)

    pairs2601 = npc_pair_index_flat(d2601)
    pairs2804 = npc_pair_index_nested(pos2804)
    all_pairs = sorted(set(pairs2601) | set(pairs2804))
    rows = []
    for pair in all_pairs:
        a, b = pairs2601.get(pair), pairs2804.get(pair)
        if a is None:
            agreement = 'only_in_minimapnpcpos_2804'
        elif b is None:
            agreement = 'only_in_npcposdata_2601'
        elif a == b:
            agreement = 'identical_sequence'
        elif sorted(a) == sorted(b):
            agreement = 'identical_multiset_different_order'
        else:
            agreement = 'content_difference'
        rows.append([pair[0], pair[1], len(a or []), len(b or []), agreement])
    dump('npc_2601_vs_2804_agreement.csv',
         ['scene_id', 'npcid', 'records_2601', 'records_2804', 'agreement'], rows)

    provenance = {
        'status': 'candidate_framing_not_confirmed_by_the_native_loader',
        'source_entries': {str(k): {'bounds': CANDIDATE_BOUNDS.get(k)
                                    if CANDIDATE_BOUNDS.get(k)
                                    else list((archive or Archive()).keydb[str(k)]['bounds'])}
                           for k in (400, 1301, 1799, 2601, 2804)},
        'rules': ['zero-npcid records kept', 'duplicate records kept',
                  'no table merging', 'no Simplified/Traditional conversion'],
    }
    # 显式写 LF 字节：write_text 在 Windows 会把 \n 翻成 \r\n，与提交版
    # （Linux 生成的 LF）对不上，E staging 字节比对随之失败
    # （docs/analysis/windows_acceptance_20261024.md §5.2）。
    (out / 'provenance.json').write_bytes(
        (json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True)
         + '\n').encode('utf-8'))
    written.append('provenance.json')
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', help='write the machine-readable evidence JSON here')
    parser.add_argument('--csv-dir', help='also emit candidate staging CSVs here '
                                          '(review material; never server/game_data/)')
    parser.add_argument('--check', action='store_true',
                        help='exit non-zero if any candidate verification fails')
    parser.add_argument('--no-scan', action='store_true',
                        help='skip the archive-wide consumer name scan')
    args = parser.parse_args(argv)

    archive = Archive()
    evidence = build_evidence(archive, with_scan=not args.no_scan)

    failed = []
    for entry, sets in evidence['verifications'].items():
        for label, verdict in sets.items():
            if label == 'candidate' and not verdict['pass']:
                failed.append((int(entry), label, verdict['witness_failures']))
    print(f"archive sha256 matches expected: "
          f"{evidence['inputs']['archive']['matches_expected']}")
    print(f"key database sha256 matches expected: "
          f"{evidence['inputs']['key_database']['matches_expected']}")
    for entry in ('400', '1301', '1799', '2601', '2804', '4897'):
        for label, verdict in evidence['verifications'][entry].items():
            tag = 'PASS' if verdict['pass'] else 'FAIL'
            line = f'  entry {entry:>5} {label:<18} {tag}'
            if not verdict['pass']:
                bad = [k for k, v in verdict['checks'].items() if not v.get('ok')]
                line += f'  (failed: {", ".join(bad)})'
            print(line)
    entry1870 = evidence['verifications'].get('1870', {}).get('saved', {})
    print(f"  entry  1870 saved            {'PASS' if entry1870.get('pass') else 'INFO'}"
          '  (framing untouched; report keeps it unresolved)')

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=1,
                                       sort_keys=True) + '\n', encoding='utf-8')
        print(f'evidence written to {out_path}')
    if args.csv_dir:
        analyses = {k: EntryAnalysis(archive, k, CANDIDATE_BOUNDS.get(k) or
                                     archive.keydb[str(k)]['bounds'])
                    for k in (400, 1301, 1799, 2601, 2804, 4897)}
        written = write_staging_csvs(analyses, args.csv_dir, archive=archive)
        print(f'staging CSVs written to {args.csv_dir}: {", ".join(written)}')
    if args.check:
        hashes_ok = (evidence['inputs']['archive']['matches_expected']
                     and evidence['inputs']['key_database']['matches_expected'])
        if failed or not hashes_ok:
            print(f'CHECK FAILED: {failed or "input hashes changed"}')
            return 1
        print('CHECK OK: all candidate parameter sets verify')
    return 0


if __name__ == '__main__':
    sys.exit(main())
