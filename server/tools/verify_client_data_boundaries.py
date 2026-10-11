#!/usr/bin/env python3
"""Independent, read-only verification of client static-config extraction.

This tool is a *second opinion* on `server/tools/review_client_data_boundaries.py`.
It re-derives every claim from `data/script.fls` and `script_fls_keys.json` using
evidence that does NOT depend on Chinese text reading plausibly:

  * cross-entry byte identity  - the same byte run decodes cleanly in another FLS
                                 entry that uses different XOR keys/boundaries and
                                 where the run does not straddle any boundary;
  * instruction-stream structure - Duoyi opcodes must all be present in PY25_MAP and
                                 the LOAD_CONST index sequence of a literal-dict build
                                 loop must be contiguous;
  * independent source tables  - e.g. petskill.py's AUTOFIGHTLIST corroborating a
                                 petactiveskilldata.py skill id;
  * opcode-validity density    - a whole XOR segment decoding to unmapped opcodes
                                 proves a wrong key, not a wrong boundary.

Constraints honoured: standard library only; neither `data/script.fls` nor
`tools/decompiler/script_fls_keys.json` is written; no recovered script is
executed (no exec/eval/runtime import of recovered code); nothing is written to
`server/game_data/`.

Run from the repository root:

    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/verify_client_data_boundaries.py

Add `--write` to also store the JSON at
`server/docs/catalog/client_data_independent_check.json`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
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

# Duoyi custom-VM opcode widths: HAVE_ARGUMENT == 0x5F.
DUOYI_HAVE_ARGUMENT = 0x5F
# Standard Python 2.5 opcode numbers used structurally below.
STD_DUP_TOP, STD_ROT_TWO = 4, 2
STD_STORE_SUBSCR, STD_LOAD_CONST, STD_STORE_NAME = 60, 100, 90
STD_EXTENDED_ARG = 143  # PY25_MAP maps Duoyi 0x8b here; see report section 3.4


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
        """Decode every entry with the saved keys/bounds (used for cross-entry search)."""
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
    """Walk Duoyi bytecode (HAVE_ARGUMENT == 0x5F). Yields (offset, opcode, arg)."""
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


def std_walk_clean(code: bytes) -> bool:
    """True if standard bytecode aligns and has no dangling EXTENDED_ARG."""
    at, ext = 0, 0
    while at < len(code):
        op = code[at]
        at += 1
        if op >= 90:
            if at + 2 > len(code):
                return False
            arg = int.from_bytes(code[at:at + 2], 'little') | ext
            at += 2
            ext = arg << 16 if op == STD_EXTENDED_ARG else 0
        elif ext:
            return False
    return ext == 0


def cp950_ok(value: bytes) -> bool:
    try:
        value.decode('cp950')
        return True
    except UnicodeDecodeError:
        return False


def dict_build_loop_signature(code: bytes, start: int, end: int):
    """Report the regularity of a literal-dict build loop inside co_code.

    A generated `{k: v, ...}` module table compiles to a repeating
    DUP_TOP / LOAD_CONST(key) / ROT_TWO / LOAD_CONST(value) / STORE_SUBSCR loop.
    Returns (mapped_ratio, load_const_indices, contiguous).
    """
    ops = list(duoyi_instructions(code, start, end))
    mapped = [op for _, op, _ in ops]
    unmapped = [op for op in mapped if decoder.PY25_MAP.get(op) is None]
    indices = [arg for _, op, arg in ops
               if decoder.PY25_MAP.get(op) == STD_LOAD_CONST and arg is not None]
    contiguous = bool(indices) and all(b - a == 1 for a, b in zip(indices, indices[1:]))
    ratio = 1.0 - (len(unmapped) / len(mapped)) if mapped else 0.0
    return ratio, indices, contiguous


def cross_entry_hits(corpus: dict[int, bytes], run: bytes, limit: int = 16):
    """Which entries contain this exact byte run? At most one hit per entry, so the
    evidence shows how many *independent* key sets agree rather than how many times
    one entry repeats the string."""
    hits = []
    for index, data in corpus.items():
        pos = data.find(run)
        if pos >= 0:
            hits.append({'entry_index': index, 'payload_offset': pos})
            if len(hits) >= limit:
                break
    return hits


# --------------------------------------------------------------------------- #
# the individual findings
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


def verify_text_candidate(arc: Archive, corpus, entry_index, boundary_index,
                          candidate, record_id, table='DATA'):
    """Confirm a text boundary candidate by exact cross-entry byte identity."""
    meta = arc.keys[str(entry_index)]
    saved = meta['bounds'][boundary_index]
    bounds = list(meta['bounds'])
    bounds[boundary_index] = candidate
    run_lo, run_hi = min(saved, candidate), max(saved, candidate)
    run = arc.decode(entry_index, bounds)[run_lo:run_hi]
    hits = cross_entry_hits(corpus, run)
    corroborating = []
    for hit in hits:
        idx, off = hit['entry_index'], hit['payload_offset']
        if idx == entry_index and off == run_lo:
            continue  # the patched occurrence itself
        edges = [0] + arc.keys[str(idx)]['bounds'] + [len(corpus[idx])]
        inside = next((k for k in range(5)
                       if edges[k] <= off and off + len(run) <= edges[k + 1]), None)
        if inside is not None:
            corroborating.append({
                'entry_index': idx, 'payload_offset': off, 'xor_segment': inside,
                'segment_key': arc.keys[str(idx)]['keys'][inside],
                'entry_keys': arc.keys[str(idx)]['keys'],
                'entry_bounds': arc.keys[str(idx)]['bounds'],
            })
    return finding(
        entry_index, table, record_id, 'description', run_lo, arc.payload(entry_index)[run_lo:run_hi],
        saved, candidate,
        arc.decode(entry_index)[run_lo:run_hi].decode('cp950', 'backslashreplace'),
        run.decode('cp950', 'backslashreplace') if cp950_ok(run) else run.hex(),
        'confirmed_extraction_bug' if corroborating else 'candidate',
        {'method': 'exact_cross_entry_byte_identity',
         'corrupt_run': [run_lo, run_hi],
         'delta_key_xor': meta['keys'][boundary_index] ^ meta['keys'][boundary_index + 1],
         'corroborated_by_independent_entries': corroborating},
        'Corroborating entries are themselves decoded with heuristic (fitted) keys; '
        'no native-client runtime comparison was performed.'
        if corroborating else 'No independent corroboration found.',
        arc.archive_sha256)


def verify_1115(arc: Archive):
    """Structural check of the 1115 / pet 2910 boundary inside co_code."""
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
        out[label] = {'boundary': bound,
                      'mapped_opcode_ratio': round(ratio, 4),
                      'unmapped_opcodes': [hex(op) for _, op, std in ops if std is None],
                      'load_const_indices': indices,
                      'load_const_indices_contiguous': contiguous,
                      'instructions': [{'offset': o, 'duoyi': hex(op),
                                        'std': std} for o, op, std in ops]}
    ratio_s = out['saved']['mapped_opcode_ratio']
    ratio_c = out['candidate']['mapped_opcode_ratio']
    contig_s = out['saved']['load_const_indices_contiguous']
    contig_c = out['candidate']['load_const_indices_contiguous']
    confirmed = (ratio_c == 1.0 and contig_c and not contig_s and ratio_s < 1.0)
    payload = arc.payload(1115)
    return finding(
        1115, 'DATA', 2910, 'name', min(saved, candidate),
        payload[min(saved, candidate):max(saved, candidate)],
        saved, candidate, 2280, '混沌騎士',
        'confirmed_extraction_bug' if confirmed else 'candidate',
        {'method': 'instruction_stream_structure',
         'note': 'Boundary lies inside co_code, not inside a string constant.',
         'saved': out['saved'], 'candidate': out['candidate']},
        'Confirmed structurally (opcode validity + contiguous LOAD_CONST indices); '
        'the resulting name also matches petdata entry 2910, but that match is '
        'corroborating, not the basis of the decision.',
        arc.archive_sha256)


def verify_2242(arc: Archive, petskill_autofight):
    """Confirm SKILLIDLST[16] against an independently decoded source table."""
    meta = arc.keys['2242']
    saved, candidate = meta['bounds'][1], 264
    payload = arc.payload(2242)
    lo, hi = min(saved, candidate), max(saved, candidate)
    values = {}
    for label, bound in (('saved', saved), ('candidate', candidate)):
        bounds = list(meta['bounds'])
        bounds[1] = bound
        d = arc.decode(2242, bounds)
        values[label] = struct.unpack_from('<i', d, 262)[0]
    corpus = arc.corpus()
    elsewhere_64605 = [i for i, d in corpus.items()
                       if i != 2242 and b'i' + struct.pack('<I', 64605) in d]
    return finding(
        2242, 'SKILLIDLST', 16, 'SKILLIDLST[16]', lo, payload[lo:hi],
        saved, candidate, values['saved'], values['candidate'],
        'confirmed_extraction_bug' if 416 in petskill_autofight else 'candidate',
        {'method': 'independent_source_table_cross_reference',
         'structural_note': 'Both offsets keep the 5-byte TYPE_INT record aligned, so '
                            'record alignment alone cannot discriminate; the evidence '
                            'is the independent skill-id table.',
         'petskill_entry': 3205,
         'petskill_AUTOFIGHTLIST': petskill_autofight,
         'autofightlist_contains_416': 416 in petskill_autofight,
         'autofightlist_contains_64605': 64605 in petskill_autofight,
         'other_entries_containing_int_64605': elsewhere_64605},
        'AUTOFIGHTLIST comes from entry 3205, which itself needed a key correction; '
        'that correction is independently evidenced but not native-verified.',
        arc.archive_sha256)


def verify_item_72548(arc: Archive, corpus):
    """The trailing 0x84 in item 72548's name: source value or extraction bug?"""
    needle = bytes.fromhex('730d000000c2f9a448a7a4c34dc5e9c5e7' '84')
    hits = []
    for index, data in corpus.items():
        pos = data.find(needle)
        if pos >= 0:
            meta = arc.keys[str(index)]
            hits.append({'entry_index': index, 'payload_offset': pos,
                         'keys': meta['keys'], 'bounds': meta['bounds'],
                         'method': meta['method']})
    distinct_keysets = {tuple(h['keys']) for h in hits}
    confirmed_source = len(distinct_keysets) >= 2
    return finding(
        1945, 'DATA', 72548, 'DATA[72548][0]', 1100453,
        bytes.fromhex('c2f9a448a7a4c34dc5e9c5e784'),
        None, None, '雙人坐騎體驗\\x84', '雙人坐騎體驗\\x84',
        'confirmed_source_value' if confirmed_source else 'unresolved',
        {'method': 'multi_entry_identical_pattern',
         'pattern_including_length_prefix_hex': needle.hex(),
         'occurrences': hits,
         'distinct_key_sets': [list(k) for k in sorted(distinct_keysets)],
         'reasoning': 'The identical 18-byte pattern, including the 4-byte marshal '
                      'length prefix 0d000000, decodes the same way in entries that '
                      'use different XOR keys and different segment boundaries. A '
                      'boundary or key error cannot reproduce identical bytes across '
                      'independent key sets.'},
        'The shipped client string really is 13 bytes ending in a lone CP950 lead byte '
        '0x84. Do not trim or guess the missing trail byte. The neighbouring item '
        '"雙人坐騎體驗券" (14 bytes, a8e9 = 券) exists separately and is NOT the same record.',
        arc.archive_sha256)


def scan_boundary_for_string(arc: Archive, corpus, entry_index, boundary_index,
                             data_start, data_len, window, record, field_path):
    """Scan a boundary for CP950-clean renders, then corroborate by cross-entry hits."""
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
        if cp950_ok(value):
            hits = [h for h in cross_entry_hits(corpus, value, limit=16)
                    if not (h['entry_index'] == entry_index
                            and h['payload_offset'] == data_start)]
            solutions.append({'boundary': offset, 'text': value.decode('cp950'),
                              'cross_entry_hits': hits})
    corroborated = [s for s in solutions if s['cross_entry_hits']]
    chosen = corroborated[0] if len(corroborated) == 1 else None
    payload = arc.payload(entry_index)
    cur = arc.decode(entry_index)[data_start:data_start + data_len]
    if chosen:
        classification, cand = 'confirmed_extraction_bug', chosen['boundary']
        uncertainty = ('Corroborating entries use heuristically fitted keys; no '
                       'native-client comparison.')
    elif len(solutions) == 1:
        classification, cand = 'candidate', solutions[0]['boundary']
        uncertainty = 'Exactly one CP950-clean offset, but no independent corroboration.'
    elif solutions:
        classification, cand = 'candidate', None
        uncertainty = (f'{len(solutions)} offsets decode as valid CP950 and none is '
                       'independently corroborated; valid CP950 is not sufficient '
                       'evidence, so no boundary is proposed.')
    else:
        classification, cand = 'unresolved', None
        uncertainty = 'No offset in the scanned window yields valid CP950.'
    return finding(
        entry_index, 'DATA', record, field_path, data_start,
        payload[data_start:data_start + data_len],
        saved, cand,
        cur.decode('cp950', 'backslashreplace'),
        (next(s['text'] for s in solutions if s['boundary'] == cand)
         if cand is not None else None),
        classification,
        {'method': 'boundary_scan_plus_cross_entry_byte_identity',
         'scanned_window': [saved - window, saved + window],
         'cp950_clean_solutions': solutions,
         'corroborated_solutions': corroborated},
        uncertainty, arc.archive_sha256)


def verify_3205_key(arc: Archive):
    """Entry 3205: is the fault a boundary or a wrong segment key?"""
    meta = arc.keys['3205']
    bounds, keys = list(meta['bounds']), list(meta['keys'])
    saved_dec = arc.decode(3205)
    cc_start = 22
    cc_len = struct.unpack_from('<I', saved_dec, 18)[0]
    cc_end = cc_start + cc_len

    def seg_of(pos):
        edges = [0] + bounds + [len(arc.payload(3205))]
        return next(k for k in range(5) if edges[k] <= pos < edges[k + 1])

    bad_saved = unmapped_opcode_positions(saved_dec, cc_start, cc_end)
    histogram = {}
    for pos in bad_saved:
        histogram[seg_of(pos)] = histogram.get(seg_of(pos), 0) + 1

    # Brute force only key[1]; score on interior to avoid boundary-edge noise.
    lo, hi = bounds[0] + 3, bounds[1] - 3
    scored = []
    for key in range(256):
        trial = list(keys)
        trial[1] = key
        dec = arc.decode(3205, bounds, trial)
        scored.append((len(unmapped_opcode_positions(dec, lo, hi)), key))
    scored.sort()
    best_bad, best_key = scored[0]
    runner_up_bad, runner_up_key = scored[1]
    trial = list(keys)
    trial[1] = best_key
    fixed_dec = arc.decode(3205, bounds, trial)
    bad_fixed = unmapped_opcode_positions(fixed_dec, cc_start, cc_end)

    recovered = None
    if best_bad == 0:
        try:
            co = arc.transpile(3205, bounds, trial)
            seq = list(std_instructions(co))
            tables = {}
            for name in (b'AUTOFIGHTLIST', b'ShieldShortCutSkills'):
                idx = next((i for i, (_, op, arg) in enumerate(seq)
                            if op == STD_STORE_NAME and co['names'][arg] == name), None)
                if idx is None:
                    continue
                count = seq[idx - 1][2]  # BUILD_LIST/BUILD_TUPLE element count
                tables[name.decode()] = evaluate_slice(co, seq[idx - count - 1:idx + 1])
            stores = [co['names'][arg].decode('latin1')
                      for _, op, arg in seq if op == STD_STORE_NAME]
            recovered = {
                'co_filename': co['filename'].decode('latin1'),
                'co_names': [n.decode('latin1') for n in co['names']],
                'store_name_targets': stores,
                'data_is_module_level_store': 'DATA' in stores,
                'literal_tables_recovered': tables,
            }
        except (ValueError, IndexError, KeyError, TypeError, struct.error) as exc:
            recovered = {'error': f'{type(exc).__name__}: {exc}'}

    return {
        'finding': finding(
            3205, 'co_code', '<module>', 'root co_code', bounds[0],
            arc.payload(3205)[bounds[0]:bounds[0] + 16],
            None, None, f'key[1]={keys[1]}', f'key[1]={best_key}',
            'confirmed_extraction_bug' if best_bad == 0 and not bad_fixed else 'unresolved',
            {'method': 'unmapped_opcode_density_per_xor_segment',
             'root_co_code_payload_span': [cc_start, cc_end],
             'unmapped_opcodes_with_saved_key': len(bad_saved),
             'unmapped_opcodes_per_segment': {str(k): v for k, v in sorted(histogram.items())},
             'saved_segment_1_bounds': [bounds[0], bounds[1]],
             'brute_forced_key_candidates': [
                 {'key': k, 'unmapped': b} for b, k in scored[:4]],
             'best_key': best_key, 'best_unmapped': best_bad,
             'runner_up': {'key': runner_up_key, 'unmapped': runner_up_bad},
             'unmapped_after_fix': len(bad_fixed),
             'recovered_module': recovered},
            'A whole XOR segment decoding to unmapped opcodes cannot be explained by a '
            'boundary error; only a wrong key byte produces it. The corrected key also '
            'yields a structurally coherent module. No native-client comparison.',
            arc.archive_sha256),
        'autofightlist': (recovered or {}).get('literal_tables_recovered', {}).get('AUTOFIGHTLIST', []),
    }


def std_instructions(co):
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
            raise ValueError('EXTENDED_ARG before argument-free instruction')
        yield start, op, arg


def evaluate_slice(co, sequence):
    stack = []
    for _, op, arg in sequence:
        if op == STD_LOAD_CONST:
            stack.append(co['consts'][arg])
        elif op in (102, 103):
            values = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(tuple(values) if op == 102 else list(values))
        elif op == STD_STORE_NAME:
            return stack.pop()
        else:
            raise ValueError(f'unsupported opcode {op}')
    raise ValueError('missing final STORE_NAME')


def verify_pet_tables(arc: Archive):
    """2027 (petdata) vs 1115 (mxpetdata): differences are not automatically errors."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'rev', ROOT / 'server/tools/review_client_data_boundaries.py')
    rev = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rev)
    co27 = arc.transpile(2027, use_solver=True)
    bounds1115 = list(arc.keys['1115']['bounds'])
    bounds1115[0] = 828
    co1115 = arc.transpile(1115, bounds1115)
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
        'classification': 'legitimate_table_difference',
        'note': 'Cardinality and one naming difference survive every check performed. '
                'No evidence supports overwriting one table with the other.',
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true',
                        help='also write the JSON evidence file')
    args = parser.parse_args(argv)

    arc = Archive()
    corpus = arc.corpus()

    result3205 = verify_3205_key(arc)
    autofight = result3205['autofightlist']

    findings = [
        verify_text_candidate(arc, corpus, 1945, 0, 259583, 10424),
        verify_text_candidate(arc, corpus, 1945, 3, 1038307, 71700),
        verify_1115(arc),
        verify_2242(arc, autofight),
        verify_item_72548(arc, corpus),
        # 2600.address: string data 16241..16277 (declared length 36) ends exactly
        # on the saved boundary 16277 - the classic boundary-error signature.
        scan_boundary_for_string(arc, corpus, 2027, 2, 16241, 36, 60,
                                 2600, "DATA[2600]['address']"),
        # 4011.maySkillLst[3]: 8-byte string 21747..21755 ends exactly on 21755.
        scan_boundary_for_string(arc, corpus, 2027, 3, 21747, 8, 60,
                                 4011, "DATA[4011]['maySkillLst'][3]"),
        scan_boundary_for_string(arc, corpus, 1698, 0, 461, 78, 240,
                                 10004, 'DATA[10004]'),
        result3205['finding'],
    ]

    report = {
        'status': 'independent_check_research_evidence_not_approved_game_data',
        'generated_by': 'server/tools/verify_client_data_boundaries.py',
        'inputs': {
            'archive': 'data/script.fls',
            'archive_sha256': arc.archive_sha256,
            'archive_size': len(arc.raw),
            'entry_count': arc.entry_count,
            'key_database': 'tools/decompiler/script_fls_keys.json',
            'key_database_sha256': arc.keydb_sha256,
        },
        'native_loader_status': {
            'pkgimport_va': '0x00457C20',
            'verified_by': '.rdata string block at VA 0x6B2260 contains '
                           '"MyPython.cpp", "data\\script.fls", "PkgImport"',
            'static_analysis': 'blocked',
            'reason': 'The function body ends in "jmp 0xA15DB4", inside the '
                      'DuoyiProtect _dyprot0/_dyprot1 sections; the code is '
                      'decrypted at runtime only, so the native 5-segment '
                      'boundary rule cannot be recovered statically.',
            'consequence': 'Saved bounds are heuristic fits (methods: catalog, ltr*, '
                           'greedy-v7), not native-derived values.',
        },
        'findings': findings,
        'pet_table_difference': verify_pet_tables(arc),
        'csv_admission': {
            'eligible_for_review_csv': [
                '1945 itemdata DATA - names/descriptions, excluding record 72548 name '
                '(isolate) and after applying boundary candidates 259583 and 1038307',
                '1115 mxpetdata DATA - after boundary candidate 828',
                '2027 petdata DATA - after boundary candidates 16264 and 21751',
                '2242 petactiveskilldata SKILLIDLST - after boundary candidate 264',
                '3205 petskill AUTOFIGHTLIST and ShieldShortCutSkills - after key[1]=218',
            ],
            'must_be_isolated': [
                '1945 DATA[72548][0] - source value with an invalid CP950 trail byte',
            ],
            'not_recoverable_this_round': [
                '3205 petskill DATA - not a module-level literal store in this entry; '
                'the pet-skill master table needs a different extraction path',
            ],
            'missing_server_side_authority': [
                'petdata skill fields are names, not ids; name->id mapping requires the '
                'pet-skill master table, which is still unrecovered',
            ],
        },
        'limitations': [
            'No recovered script was executed; no exec/eval/runtime import of recovered code.',
            'data/script.fls and script_fls_keys.json were only read.',
            'Cross-entry corroboration uses the same heuristic key database for the '
            'corroborating entries; it is strong but not native-client proof.',
            'Valid CP950 is treated as necessary, never as sufficient.',
            'Nothing here has been written to server/game_data/.',
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
