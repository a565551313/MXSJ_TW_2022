#!/usr/bin/env python3
"""Independent, read-only verification of client static-config extraction.

REVISED after coordinator review (2026-10-11). Two earlier defects are fixed:

  1. Module-level table assignment was detected only via STORE_NAME (std 90).
     `PY25_MAP` maps Duoyi 0xC4 -> std 97 (STORE_GLOBAL), and entry 3205 assigns
     both ICON_MAPPING and DATA through STORE_GLOBAL. The old code therefore
     wrongly concluded that petskill.py had no module-level DATA table.
     Both opcodes are now recognised everywhere.

  2. The entry-3205 segment key was chosen by "fewest unmapped Duoyi opcodes".
     That metric measures instruction *alignment* only. It ranked keys[1]=218
     first, but 218 yields an unsupported opcode (80 / PRINT_ITEM) inside the
     DATA literal build, so DATA cannot be reconstructed at all. The decision
     metric is now **literal-build feasibility**: instruction alignment, operand
     references in range, stack discipline, and an actual reconstructed table.
     Both metrics are still reported so the difference is visible.

Evidence kinds, in increasing strength (see report section 7):
  structure_reconstructible < cross_entry_byte_identical
  < presumed_legitimate_difference < matches_native_client  (not achieved)

Constraints honoured: standard library only; `data/script.fls` and
`tools/decompiler/script_fls_keys.json` are only read; no recovered script is
executed (no exec/eval/runtime import); nothing is written to `server/game_data/`.

Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/verify_client_data_boundaries.py --write
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
from tools.decompiler import batch_decompile as decoder  # noqa: E402
from tools.fls_batch_decoder import MarshalReader  # noqa: E402

ARCHIVE = ROOT / 'data/script.fls'
KEYDB = ROOT / 'tools/decompiler/script_fls_keys.json'
OUT_PATH = ROOT / 'server/docs/catalog/client_data_independent_check.json'

DUOYI_HAVE_ARGUMENT = 0x5F
# Standard Python 2.5 opcode numbers.
STD_ROT_TWO, STD_DUP_TOP = 2, 4
STD_STORE_SUBSCR, STD_STORE_NAME = 60, 90
STD_STORE_GLOBAL = 97
STD_BUILD_TUPLE, STD_BUILD_LIST, STD_BUILD_MAP = 102, 103, 104
STD_LOAD_CONST = 100
STD_EXTENDED_ARG = 143  # PY25_MAP maps Duoyi 0x8B here (Duoyi's EXTENDED_ARG).
# Opcodes permitted while rebuilding a pure literal table.
LITERAL_ALLOWLIST = frozenset({STD_LOAD_CONST, STD_BUILD_TUPLE, STD_BUILD_LIST,
                               STD_BUILD_MAP, STD_DUP_TOP, STD_ROT_TWO,
                               STD_STORE_SUBSCR, STD_STORE_NAME, STD_STORE_GLOBAL})
STORE_OPS = frozenset({STD_STORE_NAME, STD_STORE_GLOBAL})


class Archive:
    """Read-only access to the 0SLF archive and the saved 5-segment key database."""

    def __init__(self):
        self.raw = ARCHIVE.read_bytes()
        self.keydb_raw = KEYDB.read_bytes()
        self.keys = json.loads(self.keydb_raw)
        self.index_offset = struct.unpack_from('<I', self.raw, 8)[0]
        self.entry_count = struct.unpack_from('<I', self.raw, 4)[0]
        self._payloads: dict[int, bytes] = {}
        self._decoded: dict[int, bytes] = {}

    @property
    def archive_sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()

    @property
    def keydb_sha256(self) -> str:
        return hashlib.sha256(self.keydb_raw).hexdigest()

    def payload(self, index: int) -> bytes:
        if index not in self._payloads:
            entry_id, a, b, c = struct.unpack_from(
                '<IIII', self.raw, self.index_offset + 16 * index)
            size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
            pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
            self._payloads[index] = zlib.decompress(self.raw[pos:pos + size])
        return self._payloads[index]

    def decode(self, index: int, bounds=None, keys=None) -> bytes:
        meta = self.keys[str(index)]
        bounds = list(meta['bounds'] if bounds is None else bounds)
        keys = list(meta['keys'] if keys is None else keys)
        exp = self.payload(index)
        edges = [0] + bounds + [len(exp)]
        if len(bounds) != 4 or not all(a < b for a, b in zip(edges, edges[1:])):
            raise ValueError(f'invalid boundary ordering for entry {index}')
        return b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[keys[i]])
                        for i in range(5))

    def corpus(self) -> dict[int, bytes]:
        if not self._decoded:
            for index in range(self.entry_count):
                try:
                    self._decoded[index] = self.decode(index)
                except (ValueError, KeyError, IndexError, zlib.error, struct.error):
                    continue
        return self._decoded

    def transpile(self, index: int, bounds=None, keys=None, use_solver=False):
        meta = self.keys[str(index)]
        bounds = list(meta['bounds'] if bounds is None else bounds)
        keys = list(meta['keys'] if keys is None else keys)
        exp = self.payload(index)
        dec = self.decode(index, bounds, keys)
        tr = decoder.Py25MarshalTranspiler(dec, exp, keys, bounds)
        if use_solver:
            tr.transpile_object()
        else:
            with patch.object(decoder, 'solve_py25_co_span', return_value=None):
                tr.transpile_object()
        reader = MarshalReader(bytes(tr.out)[8:])
        co = reader.read()
        if reader.pos != len(reader.data):
            raise ValueError(f'marshal reader did not consume entry {index} output')
        return co


# --------------------------------------------------------------------------- #
# structural helpers
# --------------------------------------------------------------------------- #
def duoyi_instructions(code: bytes, start: int, end: int):
    at = start
    while at < end:
        op = code[at]
        if op >= DUOYI_HAVE_ARGUMENT:
            if at + 3 > end:
                return
            yield at, op, struct.unpack_from('<H', code, at + 1)[0]
            at += 3
        else:
            yield at, op, None
            at += 1


def unmapped_opcode_positions(code: bytes, start: int, end: int) -> list[int]:
    return [off for off, op, _ in duoyi_instructions(code, start, end)
            if decoder.PY25_MAP.get(op) is None]


def std_instructions(co):
    """Walk standard bytecode, validating alignment and EXTENDED_ARG usage."""
    code, at, ext = co['code'], 0, 0
    while at < len(code):
        start, op = at, code[at]
        at += 1
        arg = None
        if op >= 90:
            if at + 2 > len(code):
                raise ValueError(f'truncated instruction at {start}')
            arg = int.from_bytes(code[at:at + 2], 'little') | ext
            at += 2
            ext = arg << 16 if op == STD_EXTENDED_ARG else 0
        elif ext:
            raise ValueError(f'EXTENDED_ARG before argument-free instruction at {start}')
        yield start, op, arg
    if ext:
        raise ValueError('dangling EXTENDED_ARG')


def std_walk_clean(code: bytes) -> bool:
    try:
        list(std_instructions({'code': code}))
        return True
    except ValueError:
        return False


def cp950_ok(value: bytes) -> bool:
    try:
        value.decode('cp950')
        return True
    except UnicodeDecodeError:
        return False


def dict_build_loop_signature(code: bytes, start: int, end: int):
    """Regularity of a literal-dict build loop inside co_code."""
    ops = list(duoyi_instructions(code, start, end))
    unmapped = [op for _, op, _ in ops if decoder.PY25_MAP.get(op) is None]
    indices = [arg for _, op, arg in ops
               if decoder.PY25_MAP.get(op) == STD_LOAD_CONST and arg is not None]
    contiguous = bool(indices) and all(b - a == 1 for a, b in zip(indices, indices[1:]))
    ratio = 1.0 - (len(unmapped) / len(ops)) if ops else 0.0
    return ratio, indices, contiguous


def find_stores(co, seq):
    """Every module-level assignment, STORE_NAME *and* STORE_GLOBAL."""
    out = {}
    for at, op, arg in seq:
        if op in STORE_OPS:
            out.setdefault(co['names'][arg], []).append(
                {'opcode': 'STORE_NAME' if op == STD_STORE_NAME else 'STORE_GLOBAL',
                 'std_opcode': op, 'offset': at})
    return out


def evaluate_literal(co, seq):
    """Rebuild a literal table under a strict allowlist.

    Records duplicate dictionary keys with offset, order and before/after value
    instead of raising, because silently dropping them would hide source data.
    """
    stack: list = []
    duplicates: list[dict] = []
    stores = 0
    for at, op, arg in seq:
        if op == STD_LOAD_CONST:
            if arg is None or arg >= len(co['consts']):
                raise ValueError(f'LOAD_CONST operand {arg} out of range '
                                 f'(co_consts has {len(co["consts"])}) at {at}')
            stack.append(co['consts'][arg])
        elif op in (STD_BUILD_TUPLE, STD_BUILD_LIST):
            if arg > len(stack):
                raise ValueError(f'stack underflow at {at}')
            values = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(tuple(values) if op == STD_BUILD_TUPLE else list(values))
        elif op == STD_BUILD_MAP:
            stack.append({})
        elif op == STD_DUP_TOP:
            if not stack:
                raise ValueError(f'DUP_TOP underflow at {at}')
            stack.append(stack[-1])
        elif op == STD_ROT_TWO:
            if len(stack) < 2:
                raise ValueError(f'ROT_TWO underflow at {at}')
            stack[-2], stack[-1] = stack[-1], stack[-2]
        elif op == STD_STORE_SUBSCR:
            if len(stack) < 3:
                raise ValueError(f'STORE_SUBSCR underflow at {at}')
            key, target, value = stack.pop(), stack.pop(), stack.pop()
            if type(target) is not dict:
                raise ValueError(f'non-dictionary store at {at}')
            if key in target:
                duplicates.append({'key': key, 'offset': at, 'store_order': stores,
                                   'previous_value': target[key], 'new_value': value,
                                   'records_identical': target[key] == value})
            target[key] = value
            stores += 1
        elif op in STORE_OPS:
            if len(stack) != 1:
                raise ValueError(f'invalid final stack depth {len(stack)} at {at}')
            return stack.pop(), duplicates, stores
        else:
            raise ValueError(f'unsupported opcode {op} at {at}')
    raise ValueError('no STORE_NAME/STORE_GLOBAL terminating the literal build')


def cross_entry_hits(corpus: dict[int, bytes], run: bytes, limit: int = 16):
    """At most one hit per entry, so the evidence shows how many independent key
    sets agree rather than how often one entry repeats the string."""
    hits = []
    for index, data in corpus.items():
        pos = data.find(run)
        if pos >= 0:
            hits.append({'entry_index': index, 'payload_offset': pos})
            if len(hits) >= limit:
                break
    return hits


def segment_of(arc: Archive, index: int, offset: int, length: int):
    edges = [0] + arc.keys[str(index)]['bounds'] + [len(arc.corpus()[index])]
    for k in range(5):
        if edges[k] <= offset and offset + length <= edges[k + 1]:
            return k
    return None


# --------------------------------------------------------------------------- #
# findings
# --------------------------------------------------------------------------- #
def finding(entry_index, table, record, field_path, payload_offset, original_bytes,
            old_boundary, candidate_boundary, old_value, candidate_value,
            classification, evidence, uncertainty, source_sha):
    return {
        'entry_index': entry_index,
        'table': table,
        'record_id_or_index': record,
        'field_path': field_path,
        'source_sha256': source_sha,
        'payload_offset': payload_offset,
        'original_bytes_hex': original_bytes.hex() if original_bytes is not None else '',
        'old_boundary': old_boundary,
        'candidate_boundary': candidate_boundary,
        'old_value': old_value,
        'candidate_value': candidate_value,
        'classification': classification,
        'evidence': evidence,
        'remaining_uncertainty': uncertainty,
    }


def verify_text_candidate(arc, corpus, entry_index, boundary_index, candidate,
                          record_id, field_path='description', table='DATA'):
    """Confirm a text boundary candidate by exact cross-entry byte identity."""
    meta = arc.keys[str(entry_index)]
    saved = meta['bounds'][boundary_index]
    bounds = list(meta['bounds'])
    bounds[boundary_index] = candidate
    lo, hi = min(saved, candidate), max(saved, candidate)
    run = arc.decode(entry_index, bounds)[lo:hi]
    corroborating = []
    for hit in cross_entry_hits(corpus, run):
        idx, off = hit['entry_index'], hit['payload_offset']
        if idx == entry_index and off == lo:
            continue
        seg = segment_of(arc, idx, off, len(run))
        if seg is not None:
            corroborating.append({'entry_index': idx, 'payload_offset': off,
                                  'xor_segment': seg,
                                  'segment_key': arc.keys[str(idx)]['keys'][seg],
                                  'entry_keys': arc.keys[str(idx)]['keys'],
                                  'entry_bounds': arc.keys[str(idx)]['bounds']})
    return finding(
        entry_index, table, record_id, field_path, lo,
        arc.payload(entry_index)[lo:hi], saved, candidate,
        arc.decode(entry_index)[lo:hi].decode('cp950', 'backslashreplace'),
        run.decode('cp950', 'backslashreplace') if cp950_ok(run) else run.hex(),
        'confirmed_extraction_bug' if corroborating else 'candidate',
        {'method': 'exact_cross_entry_byte_identity',
         'corrupt_run': [lo, hi],
         'delta_key_xor': meta['keys'][boundary_index] ^ meta['keys'][boundary_index + 1],
         'corroborated_by_independent_entries': corroborating},
        'Corroborating entries are themselves decoded with heuristically fitted keys; '
        'no native-client runtime comparison was performed.'
        if corroborating else 'No independent corroboration found.',
        arc.archive_sha256)


def verify_1115(arc):
    meta = arc.keys['1115']
    saved, candidate = meta['bounds'][0], 828
    out = {}
    for label, bound in (('saved', saved), ('candidate', candidate)):
        bounds = list(meta['bounds'])
        bounds[0] = bound
        code = arc.decode(1115, bounds)
        ratio, indices, contiguous = dict_build_loop_signature(code, 803, 842)
        ops = [(off, op, decoder.PY25_MAP.get(op)) for off, op, _
               in duoyi_instructions(code, 825, 831)]
        out[label] = {'boundary': bound, 'mapped_opcode_ratio': round(ratio, 4),
                      'unmapped_opcodes': [hex(op) for _, op, std in ops if std is None],
                      'load_const_indices': indices,
                      'load_const_indices_contiguous': contiguous}
    confirmed = (out['candidate']['mapped_opcode_ratio'] == 1.0
                 and out['candidate']['load_const_indices_contiguous']
                 and not out['saved']['load_const_indices_contiguous']
                 and out['saved']['mapped_opcode_ratio'] < 1.0)
    lo, hi = min(saved, candidate), max(saved, candidate)
    return finding(
        1115, 'DATA', 2910, 'name', lo, arc.payload(1115)[lo:hi],
        saved, candidate, 2280, '混沌騎士',
        'confirmed_extraction_bug' if confirmed else 'candidate',
        {'method': 'instruction_stream_structure',
         'note': 'Boundary lies inside co_code, not inside a string constant.',
         'saved': out['saved'], 'candidate': out['candidate']},
        'Decided on opcode validity and LOAD_CONST index continuity only; the name '
        'matching petdata 2910 is corroborating, not the basis.',
        arc.archive_sha256)


def verify_2242(arc, petskill_data_keys):
    """SKILLIDLST[16]: record alignment cannot discriminate, an independent table can."""
    meta = arc.keys['2242']
    saved, candidate = meta['bounds'][1], 264
    lo, hi = min(saved, candidate), max(saved, candidate)
    values = {}
    for label, bound in (('saved', saved), ('candidate', candidate)):
        bounds = list(meta['bounds'])
        bounds[1] = bound
        values[label] = struct.unpack_from('<i', arc.decode(2242, bounds), 262)[0]
    corpus = arc.corpus()
    elsewhere = [i for i, d in corpus.items()
                 if i != 2242 and b'i' + struct.pack('<I', 64605) in d]
    # Strongest evidence: the reconstructed petskill master table.
    in_master = values['candidate'] in petskill_data_keys
    master_has_old = values['saved'] in petskill_data_keys
    return finding(
        2242, 'SKILLIDLST', 16, 'SKILLIDLST[16]', lo, arc.payload(2242)[lo:hi],
        saved, candidate, values['saved'], values['candidate'],
        'confirmed_extraction_bug' if (in_master and not master_has_old) else 'candidate',
        {'method': 'independent_source_table_cross_reference',
         'structural_note': 'Boundaries 262..266 all keep the 5-byte TYPE_INT record '
                            'aligned, so alignment alone cannot discriminate.',
         'petskill_entry': 3205,
         'petskill_DATA_key_count': len(petskill_data_keys),
         'candidate_in_petskill_DATA': in_master,
         'saved_value_in_petskill_DATA': master_has_old,
         'other_entries_containing_int_64605': elsewhere},
        'Depends on the entry-3205 reconstruction, which itself needs a key correction '
        'that is not native-verified.',
        arc.archive_sha256)


def verify_item_72548(arc, corpus):
    needle = bytes.fromhex('730d000000c2f9a448a7a4c34dc5e9c5e7' '84')
    hits = []
    for index, data in corpus.items():
        pos = data.find(needle)
        if pos >= 0:
            meta = arc.keys[str(index)]
            hits.append({'entry_index': index, 'payload_offset': pos,
                         'keys': meta['keys'], 'bounds': meta['bounds'],
                         'method': meta['method']})
    distinct = {tuple(h['keys']) for h in hits}
    return finding(
        1945, 'DATA', 72548, 'DATA[72548][0]', 1100453,
        bytes.fromhex('c2f9a448a7a4c34dc5e9c5e784'), None, None,
        '雙人坐騎體驗\\x84', '雙人坐騎體驗\\x84',
        'confirmed_source_value' if len(distinct) >= 2 else 'unresolved',
        {'method': 'multi_entry_identical_pattern',
         'pattern_including_length_prefix_hex': needle.hex(),
         'occurrences': hits,
         'distinct_key_sets': [list(k) for k in sorted(distinct)],
         'reasoning': 'The identical 18-byte pattern, including the 4-byte marshal '
                      'length prefix 0d000000, decodes identically under three '
                      'different key sets. A boundary or key error cannot do that.'},
        'The client string really is 13 bytes ending in a lone CP950 lead byte 0x84. '
        'Do not trim or guess. "雙人坐騎體驗券" (14 bytes) is a different record.',
        arc.archive_sha256)


def scan_boundary_for_string(arc, corpus, entry_index, boundary_index, data_start,
                             data_len, window, record, field_path):
    meta = arc.keys[str(entry_index)]
    saved = meta['bounds'][boundary_index]
    solutions = []
    for offset in range(saved - window, saved + window + 1):
        bounds = list(meta['bounds'])
        bounds[boundary_index] = offset
        edges = [0] + bounds + [len(arc.payload(entry_index))]
        if not all(a < b for a, b in zip(edges, edges[1:])):
            continue
        value = arc.decode(entry_index, bounds)[data_start:data_start + data_len]
        if not cp950_ok(value):
            continue
        witnesses = []
        for hit in cross_entry_hits(corpus, value):
            idx, off = hit['entry_index'], hit['payload_offset']
            if idx == entry_index and off == data_start:
                continue  # the occurrence under test
            if segment_of(arc, idx, off, len(value)) is not None:
                witnesses.append({'entry_index': idx, 'payload_offset': off})
        solutions.append({'boundary': offset, 'text': value.decode('cp950'),
                          'independent_witnesses': witnesses})
    corroborated = [s for s in solutions if s['independent_witnesses']]
    chosen = corroborated[0]['boundary'] if len(corroborated) == 1 else None
    # Same evidence key as verify_text_candidate, so consumers can treat both.
    flat_witnesses = [
        {'entry_index': w['entry_index'], 'payload_offset': w['payload_offset'],
         'boundary': s['boundary'], 'text': s['text'],
         'xor_segment': segment_of(arc, w['entry_index'], w['payload_offset'],
                                   data_len)}
        for s in corroborated for w in s['independent_witnesses']]
    cur = arc.decode(entry_index)[data_start:data_start + data_len]
    if chosen is not None:
        classification = 'confirmed_extraction_bug'
        uncertainty = ('Corroborating entries use heuristically fitted keys; no '
                       'native-client comparison.')
    elif len(solutions) == 1:
        classification = 'candidate'
        uncertainty = 'Exactly one CP950-clean offset, but no independent corroboration.'
    elif solutions:
        classification = 'candidate'
        uncertainty = (f'{len(solutions)} offsets decode as valid CP950 and none is '
                       'independently corroborated; valid CP950 is not sufficient, '
                       'so no boundary is proposed.')
    else:
        classification = 'unresolved'
        uncertainty = 'No offset in the scanned window yields valid CP950.'
    return finding(
        entry_index, 'DATA', record, field_path, data_start,
        arc.payload(entry_index)[data_start:data_start + data_len],
        saved, chosen, cur.decode('cp950', 'backslashreplace'),
        next((s['text'] for s in solutions if s['boundary'] == chosen), None),
        classification,
        {'method': 'boundary_scan_plus_cross_entry_byte_identity',
         'scanned_window': [saved - window, saved + window],
         'cp950_clean_solution_count': len(solutions),
         'distinct_texts': sorted({s['text'] for s in solutions}),
         'corroborated_solutions': corroborated,
         'corroborated_by_independent_entries': flat_witnesses},
        uncertainty, arc.archive_sha256)


def strings_ending_on_boundary(arc, entry_index, max_len=8192):
    """Structural detector: a marshal string whose data ends exactly on a saved
    boundary has its tail decoded with the neighbouring segment's key whenever
    that boundary is wrong. This flags decodable-but-wrong text too, which a
    strict-CP950 scan cannot see."""
    data = arc.decode(entry_index)
    bounds = arc.keys[str(entry_index)]['bounds']
    out = []
    for j, b in enumerate(bounds):
        for p in range(max(0, b - 5 - max_len), b):
            if data[p] != 0x73:
                continue
            ln = struct.unpack_from('<I', data, p + 1)[0]
            if 0 < ln < max_len and p + 5 + ln == b:
                raw = data[p + 5:b]
                out.append({'boundary_index': j, 'boundary': b, 'header_offset': p,
                            'data_span': [p + 5, b], 'length': ln,
                            'cp950_valid': cp950_ok(raw),
                            'text': raw.decode('cp950', 'backslashreplace')})
    return out


def verify_3205(arc):
    """Compare saved / this-tool-218 / coordinator-D parameters on the metric that
    actually matters: can DATA be rebuilt under a strict allowlist?"""
    meta = arc.keys['3205']
    saved_keys, saved_bounds = list(meta['keys']), list(meta['bounds'])
    d_bounds = [18043, 36123, 54155, 72143]
    variants = [
        {'label': 'saved_key_database', 'keys': saved_keys, 'bounds': saved_bounds,
         'origin': 'tools/decompiler/script_fls_keys.json as committed'},
        {'label': 'superseded_218_proposal',
         'keys': [204, 218, 122, 74, 218], 'bounds': saved_bounds,
         'origin': 'this tool, previous revision (WITHDRAWN)'},
        {'label': 'coordinator_D_candidate',
         'keys': [204, 152, 122, 74, 218], 'bounds': d_bounds,
         'origin': 'coordinator / Agent D'},
        {'label': 'D_key_with_saved_bounds',
         'keys': [204, 152, 122, 74, 218], 'bounds': saved_bounds,
         'origin': 'control: isolates key vs boundary as the discriminator'},
    ]
    lo, hi = saved_bounds[0] + 3, saved_bounds[1] - 3
    results = []
    for v in variants:
        row = {'label': v['label'], 'origin': v['origin'],
               'keys': v['keys'], 'bounds': v['bounds']}
        try:
            co = arc.transpile(3205, v['bounds'], v['keys'])
        except (ValueError, IndexError, KeyError, TypeError, struct.error) as exc:
            row.update(transpile='failed', error=f'{type(exc).__name__}: {exc}')
            results.append(row)
            continue
        dec = arc.decode(3205, v['bounds'], v['keys'])
        cc_len = struct.unpack_from('<I', dec, 18)[0]
        row['metric_alignment_unmapped_opcodes'] = len(
            unmapped_opcode_positions(dec, 22, 22 + cc_len))
        try:
            seq = list(std_instructions(co))
            row['instruction_alignment'] = 'clean'
        except ValueError as exc:
            row.update(instruction_alignment='failed', error=str(exc))
            results.append(row)
            continue
        row['module_level_stores'] = {
            (k.decode('latin1') if isinstance(k, bytes) else str(k)): v2
            for k, v2 in find_stores(co, seq).items()}
        ic = next((i for i, (_, op, arg) in enumerate(seq)
                   if op == STD_STORE_GLOBAL and co['names'][arg] == b'ICON_MAPPING'), None)
        di = next((i for i, (_, op, arg) in enumerate(seq)
                   if op == STD_STORE_GLOBAL and co['names'][arg] == b'DATA'), None)
        if ic is None or di is None:
            row.update(literal_build='stores not found')
            results.append(row)
            continue
        start = next(i for i in range(ic + 1, di) if seq[i][1] == STD_BUILD_MAP)
        try:
            data, dups, stores = evaluate_literal(co, seq[start:di + 1])
        except ValueError as exc:
            row.update(literal_build='failed', error=str(exc))
            results.append(row)
            continue
        icon_start = next(i for i in range(0, ic) if seq[i][1] == STD_BUILD_MAP)
        icon, _, _ = evaluate_literal(co, seq[icon_start:ic + 1])
        row.update(literal_build='ok', store_subscr_count=stores,
                   unique_data_keys=len(data), data_key_min=min(data),
                   data_key_max=max(data),
                   duplicate_key_count=len(dups),
                   duplicate_keys=sorted(d['key'] for d in dups),
                   duplicate_detail=[
                       {'key': d['key'], 'offset': d['offset'],
                        'store_order': d['store_order'],
                        'records_identical': d['records_identical'],
                        'previous_name': _name(d['previous_value']),
                        'new_name': _name(d['new_value'])} for d in dups],
                   icon_mapping={str(k): v2 for k, v2 in icon.items()},
                   _data_keys=sorted(data))
        results.append(row)

    feasible = [r for r in results if r.get('literal_build') == 'ok']
    # More than one parameter set can be feasible; that is only useful if they
    # agree on the reconstructed table.
    agree = (len({(r['unique_data_keys'], tuple(r['duplicate_keys']))
                  for r in feasible}) <= 1)
    preferred = next((r for r in feasible if r['label'] == 'coordinator_D_candidate'),
                     feasible[0] if feasible else None)
    chosen = preferred if (feasible and agree) else (feasible[0] if len(feasible) == 1 else None)
    counts = {r['label']: r.get('metric_alignment_unmapped_opcodes') for r in results
              if r.get('metric_alignment_unmapped_opcodes') is not None}
    best = min(counts.values())
    tied = sorted(k for k, v in counts.items() if v == best)
    summary = {
        'variants': [{k: v for k, v in r.items() if k != '_data_keys'} for r in results],
        'alignment_metric_winner': {'unmapped_count': best, 'tied_labels': tied},
        'feasibility_winners': [r['label'] for r in feasible],
        'feasible_variants_agree_on_table': agree,
        'conclusion': (
            'The alignment metric (fewest unmapped Duoyi opcodes) and the '
            'feasibility metric (DATA actually rebuildable) disagree. Alignment '
            f'prefers a {len(tied)}-way tie ({", ".join(tied)}) and cannot separate them; '
            f'only {", ".join(r["label"] for r in feasible)} rebuilds DATA. '
            'Alignment is necessary but not sufficient.'),
        'key_vs_bounds': (
            'keys[1]=152 rebuilds DATA with either bounds set and both agree on the '
            'same 581 keys and 9 duplicate keys, so for this entry the discriminator '
            'is the key byte, not the boundary values.'),
    }
    data_keys = chosen['_data_keys'] if chosen else []
    f = finding(
        3205, 'co_code', '<module>', 'root co_code / DATA', saved_bounds[0],
        arc.payload(3205)[saved_bounds[0]:saved_bounds[0] + 16],
        f'keys[1]={saved_keys[1]}', f'keys[1]=152',
        'DATA not reconstructible', '581 unique skill ids',
        'confirmed_extraction_bug' if chosen else 'unresolved',
        dict(summary, method='literal_build_feasibility_vs_alignment'),
        'Not native-verified. Duplicate keys are recorded, not silently dropped.',
        arc.archive_sha256)
    return f, data_keys, (chosen or {})


def _name(value):
    if isinstance(value, dict) and b'name' in value:
        v = value[b'name']
        return v.decode('cp950', 'backslashreplace') if isinstance(v, bytes) else v
    return None


def verify_relations(arc, petskill):
    """Can the active-skill list, the master table and the icon map be linked?"""
    if not petskill:
        return {'status': 'unavailable'}
    icon = {int(k): v for k, v in petskill.get('icon_mapping', {}).items()}
    keys = set(petskill.get('_data_keys', []))
    meta = arc.keys['2242']
    bounds = list(meta['bounds'])
    bounds[1] = 264
    d = arc.decode(2242, bounds)
    skillidlst = [struct.unpack_from('<I', d, off + 1)[0]
                  for off in range(181, 421, 5) if d[off] == 0x69]
    return {
        'petskill_DATA_unique_ids': len(keys),
        'SKILLIDLST_from_2242': len(skillidlst),
        'SKILLIDLST_subset_of_petskill_DATA': set(skillidlst) <= keys,
        'SKILLIDLST_missing_from_DATA': sorted(set(skillidlst) - keys),
        'ICON_MAPPING_entries': len(icon),
        'ICON_MAPPING_values_subset_of_DATA': set(icon.values()) <= keys,
        'ICON_MAPPING_values_missing': sorted(set(icon.values()) - keys),
        'relation_note': (
            'ICON_MAPPING maps icon id -> skill id and every value is a key of DATA; '
            'every SKILLIDLST id from petactiveskilldata.py is also a DATA key. The '
            'three tables are mutually consistent under keys[1]=152.'),
    }


def verify_pet_tables(arc):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'rev', ROOT / 'server/tools/review_client_data_boundaries.py')
    rev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rev)
    co27 = arc.transpile(2027, use_solver=True)
    b1115 = list(arc.keys['1115']['bounds'])
    b1115[0] = 828
    co1115 = arc.transpile(1115, b1115)
    t27 = rev.extract_table(co27, b'DATA')
    t1115 = rev.extract_table(co1115, b'DATA')
    return {
        'petdata_2027_count': len(t27),
        'mxpetdata_1115_count': len(t1115),
        'only_in_mxpetdata': sorted(t1115.keys() - t27.keys()),
        'only_in_petdata': sorted(t27.keys() - t1115.keys()),
        'id_4024_mxpetdata': t1115[4024].decode('cp950'),
        'id_4024_petdata': t27[4024][b'name'].decode('cp950'),
        'id_2910_mxpetdata': t1115[2910].decode('cp950'),
        'id_2910_petdata': t27[2910][b'name'].decode('cp950'),
        'classification': 'unexplained_table_difference_presumed_legitimate',
        'note': 'Downgraded from "legitimate". The differences survive every check '
                'performed, but no positive evidence explains the extra 5106/5107 or '
                'the 4024 naming split. Absence of a counter-example is not proof '
                'that a difference is intended. Caller semantics remain unverified.',
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)

    arc = Archive()
    corpus = arc.corpus()

    f3205, petskill_keys, petskill_row = verify_3205(arc)
    findings = [
        verify_text_candidate(arc, corpus, 1945, 0, 259583, 10424),
        verify_text_candidate(arc, corpus, 1945, 3, 1038307, 71700),
        verify_1115(arc),
        verify_2242(arc, set(petskill_keys)),
        verify_item_72548(arc, corpus),
        # NEW: DATA[41052] name. Decodes cleanly as 晉怖肋 but the string ends
        # exactly on bounds[2]; only 778759 is independently corroborated.
        scan_boundary_for_string(arc, corpus, 1945, 2, 778758, 6, 90,
                                 41052, 'DATA[41052][0]'),
        scan_boundary_for_string(arc, corpus, 2027, 2, 16241, 36, 60,
                                 2600, "DATA[2600]['address']"),
        scan_boundary_for_string(arc, corpus, 2027, 3, 21747, 8, 60,
                                 4011, "DATA[4011]['maySkillLst'][3]"),
        scan_boundary_for_string(arc, corpus, 1698, 0, 461, 78, 240,
                                 10004, 'DATA[10004]'),
        f3205,
    ]

    # Detector applied to every focus entry, with the corroboration step that
    # separates real faults from strings that legitimately end on a boundary.
    detector = {}
    for idx in (1945, 2027, 1115, 2242, 1698):
        detector[str(idx)] = strings_ending_on_boundary(arc, idx)

    # 1698 additionally has two strings with a boundary in their interior that
    # decode as valid CP950 yet are visibly garbled.
    d1698 = arc.decode(1698)
    interior_1698 = []
    for j, b in enumerate(arc.keys['1698']['bounds']):
        for p in range(max(0, b - 5 - 200), b):
            if d1698[p] != 0x73:
                continue
            ln = struct.unpack_from('<I', d1698, p + 1)[0]
            if 0 < ln < 200 and p + 5 < b < p + 5 + ln:
                raw = d1698[p + 5:p + 5 + ln]
                interior_1698.append({'boundary_index': j, 'boundary': b,
                                      'header_offset': p, 'length': ln,
                                      'cp950_valid': cp950_ok(raw),
                                      'text': raw.decode('cp950', 'backslashreplace')})

    report = {
        'status': 'independent_check_research_evidence_not_approved_game_data',
        'revision': 'rev2-after-coordinator-review',
        'generated_by': 'server/tools/verify_client_data_boundaries.py',
        'inputs': {'archive': 'data/script.fls', 'archive_sha256': arc.archive_sha256,
                   'archive_size': len(arc.raw), 'entry_count': arc.entry_count,
                   'key_database': 'tools/decompiler/script_fls_keys.json',
                   'key_database_sha256': arc.keydb_sha256},
        'native_loader_status': {
            'pkgimport_va': '0x00457C20',
            'verified_by': '.rdata string block at VA 0x6B2260 contains '
                           '"MyPython.cpp", "data\\script.fls", "PkgImport"',
            'static_analysis': 'blocked',
            'reason': 'The function body ends in "jmp 0xA15DB4" inside the '
                      'DuoyiProtect _dyprot sections; the code is decrypted at '
                      'runtime only, so the native 5-segment rule cannot be '
                      'recovered statically.',
            'consequence': 'Saved bounds are heuristic fits (catalog / ltr* / '
                           'greedy-v7), not native-derived values.',
        },
        'errata': [
            {'withdrawn': '3205 petskill.py has no module-level DATA store; the pet '
                          'skill master table is not in this entry.',
             'cause': 'find_stores equivalent only matched STORE_NAME (std 90). '
                      'PY25_MAP maps Duoyi 0xC4 -> std 97 STORE_GLOBAL, and both '
                      'ICON_MAPPING and DATA are assigned that way.',
             'now': 'Both opcodes are recognised; DATA rebuilds to 581 unique ids.'},
            {'withdrawn': '3205 keys[1] = 218.',
             'cause': 'Ranked by fewest unmapped Duoyi opcodes, an alignment-only '
                      'metric. 218 aligns but emits opcode 80 (PRINT_ITEM) inside '
                      'the DATA literal build, so the table cannot be constructed.',
             'now': 'keys[1] = 152, selected by literal-build feasibility; both '
                    'metrics are reported side by side.'},
            {'withdrawn': 'itemdata needs only DATA[72548] isolated for CSV.',
             'cause': 'Only records failing strict CP950 were reviewed. '
                      'DATA[41052] decodes cleanly as 晉怖肋 yet is wrong; the '
                      'corroborated value is 時空石 at bounds[2]=778759.',
             'now': 'A structural detector (strings ending exactly on a saved '
                    'boundary) is applied to all focus entries, then corroborated.'},
            {'downgraded': 'petdata vs mxpetdata difference = legitimate_table_difference',
             'cause': 'Classified legitimate because no counter-example was found.',
             'now': 'unexplained_table_difference_presumed_legitimate'},
        ],
        'findings': findings,
        'boundary_terminating_string_detector': detector,
        'entry_1698_interior_suspects': interior_1698,
        'petskill_relations': verify_relations(arc, petskill_row),
        'pet_table_difference': verify_pet_tables(arc),
        'csv_admission': {
            'eligible_for_review_csv': [
                '1945 itemdata DATA - after boundary candidates 259583, 778759 and '
                '1038307; isolate DATA[72548][0]',
                '1115 mxpetdata DATA - after boundary candidate 828',
                '2027 petdata DATA - after boundary candidates 16264 and 21751',
                '2242 petactiveskilldata SKILLIDLST - after boundary candidate 264',
                '3205 petskill DATA (581 ids), ICON_MAPPING, AUTOFIGHTLIST, '
                'ShieldShortCutSkills - after keys[1]=152; record the 9 duplicate '
                'keys rather than silently keeping the last value',
            ],
            'must_be_isolated': [
                '1945 DATA[72548][0] - source value with an invalid CP950 trail byte',
                '3205 DATA duplicate keys 4236, 4573-4579, 4581 - keep both the '
                'overwritten and the surviving record; 4573 differs by name '
                '(天魔返生術 -> 地魔返生術)',
            ],
            'not_admissible_this_round': [
                '1698 itemext - DATA[10004] boundary undecided (10 CP950-valid '
                'offsets, none corroborated) and two further interior suspects',
                '1945 itemdata records not yet covered by the detector - the '
                'detector only flags strings ending exactly on a saved boundary, '
                'so records corrupted mid-string are not excluded by it',
            ],
            'missing_server_side_authority': [
                'petdata skill fields are names, not ids; name->id mapping now has a '
                'candidate source (3205 DATA) but is not native-verified',
            ],
        },
        'limitations': [
            'No recovered script was executed; no exec/eval/runtime import.',
            'data/script.fls and script_fls_keys.json were only read.',
            'Cross-entry corroboration uses the same heuristic key database for the '
            'corroborating entries; strong, but not native-client proof.',
            'Valid CP950 is treated as necessary, never sufficient.',
            'Nothing has been written to server/game_data/.',
        ],
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.write:
        OUT_PATH.write_text(text + '\n', encoding='utf-8')
        print(f'written: {OUT_PATH}', file=sys.stderr)
    print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
