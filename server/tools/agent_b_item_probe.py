#!/usr/bin/env python3
"""Agent B read-only probes for item / equipment / craft / gem / shop tables.

Scope: data/script.fls entries 17, 246, 293, 1381, 1698, 1945, 2338, 2409,
2455, 3791, 4924 (the item-related subset of Agent B's checklist).

What this does
  * Reads data/script.fls and tools/decompiler/script_fls_keys.json (read-only).
  * Reuses the repository's existing reader (server/tools/review_client_data_
    boundaries.py) for literal extraction, and the survey's STORE_GLOBAL
    extraction for tables assigned with STORE_GLOBAL.
  * Maps reader error offsets back to FLS payload offsets, and records the
    segment key that produced each byte.
  * Tests candidate XOR boundaries by full-table literal extraction and by
    cross-table / cross-copy agreement. Candidates are reported as evidence
    for Agent A only; nothing is applied, saved or exported.

What this does NOT do
  * It does not execute any recovered game script, import it, or call exec/eval.
  * It does not modify script.fls, the key database, game_data/ or the public
    transpiler.
  * It does not transliterate between simplified and traditional Chinese.

Usage (from the repository root; writes JSON to stdout unless --out is given):
  PYTHONDONTWRITEBYTECODE=1 python3 server/tools/agent_b_item_probe.py \
      --out server/docs/csv_checks/agent_b_probe.json
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import re
import struct
import sys
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parents[1]
sys.path.insert(0, str(TOOLS))
import review_client_data_boundaries as R  # noqa: E402

_spec = importlib.util.spec_from_file_location('survey_csv_readiness', TOOLS / 'survey_csv_readiness.py')
SURVEY = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SURVEY)

DEC = R.decoder
PY25_MAP = DEC.PY25_MAP
rv = R.Review()
ENTRY_COUNT = struct.unpack_from('<I', rv.archive, 4)[0]

# Standard opcode names, parsed (not imported) from the repository's copy.
_OPSRC = (ROOT / 'tools/decompiler/output/data_fls/lib/opcode.py').read_text(encoding='utf-8', errors='replace')
OPNAME = {int(n): k for k, n in re.findall(r"(?:def_op|name_op|jrel_op|jabs_op)\('([A-Z_]+)',\s*(\d+)\)", _OPSRC)}


def cp950_check(bs: bytes):
    """Return (strict_ok, first_error_index, has_control_chars, text_or_None)."""
    control = any((b < 32 and b not in (9, 10, 13)) or b == 127 for b in bs)
    try:
        text = bs.decode('cp950')
    except UnicodeDecodeError as ex:
        return False, ex.start, control, None
    return True, None, control, text


def clean_text(bs):
    if not isinstance(bs, bytes):
        return None
    ok, _, control, text = cp950_check(bs)
    return text if (ok and not control) else None


def payload(i: int) -> bytes:
    return rv.payload(i)


def layout(i: int, bounds=None):
    meta = rv.keys[str(i)]
    exp = payload(i)
    b = list(meta['bounds'] if bounds is None else bounds)
    return exp, [0] + b + [len(exp)], list(meta['keys'])


def bookkeeping_ok(i: int) -> bool:
    exp, edges, _ = layout(i)
    return len(edges) == 6 and all(a < c for a, c in zip(edges, edges[1:]))


def decoded(i: int, bounds=None) -> bytes:
    """Plain XOR per segment: decoded[p] == payload[p] ^ key_of_segment(p)."""
    exp, edges, keys = layout(i, bounds)
    out = bytearray()
    for s in range(5):
        out.extend(b ^ keys[s] for b in exp[edges[s]:edges[s + 1]])
    return bytes(out)


def seg_of(pos: int, edges) -> int:
    for s in range(5):
        if edges[s] <= pos < edges[s + 1]:
            return s
    raise IndexError(pos)


def locate(i: int, needle: bytes, bounds=None):
    """Where a decoded byte string sits in the payload, under selected boundaries.

    The default is the saved key-database profile. Passing bounds is an explicit
    local candidate decode; it does not alter the key database or archive.
    """
    exp, edges, keys = layout(i, bounds)
    dec = decoded(i, bounds)
    hits, start = [], 0
    while needle:
        p = dec.find(needle, start)
        if p < 0:
            break
        s = seg_of(p, edges)
        hits.append({'payload_offset': p, 'segment': s, 'key': keys[s],
                     'raw_hex': exp[p:p + len(needle)].hex(), 'decoded_hex': needle.hex()})
        start = p + 1
    return hits


def field_report(i: int, value):
    parts = value if isinstance(value, tuple) else (value,)
    rep = []
    for idx, part in enumerate(parts):
        if not isinstance(part, bytes):
            continue
        ok, err, control, text = cp950_check(part)
        locs = locate(i, part)
        entry = {'field_index': idx, 'decoded_hex': part.hex(), 'cp950_ok': ok,
                 'first_error_index': err, 'control_chars': control, 'text_if_clean': text,
                 'payload_locations': locs}
        if err is not None and locs:
            entry['first_error_payload_offset'] = locs[0]['payload_offset'] + err
        rep.append(entry)
    return rep


# ----------------------------------------------------------------- literals
def table(i: int, name=b'DATA', bounds=None, solver=True):
    """Literal extraction with the repository reader; solver on unless testing a candidate."""
    co = rv.load(i, bounds, use_solver=solver)
    try:
        return R.extract_table(co, name)
    except ValueError:
        return SURVEY.extract(co, name.decode())


def table_status(i: int, name=b'DATA', bounds=None, solver=True):
    try:
        return 'OK', table(i, name, bounds, solver), None
    except Exception as ex:  # reader rejection is data here, not a crash
        return 'FAIL', None, f'{type(ex).__name__}: {ex}'


def flagged_keys(t):
    out = []
    for k, v in t.items():
        for part in (v if isinstance(v, tuple) else (v,)):
            if isinstance(part, bytes):
                ok, _, control, _ = cp950_check(part)
                if not ok or control:
                    out.append(k)
                    break
    return sorted(out, key=repr)


def copy_name(i: int, key):
    st, t, _ = table_status(i, solver=True)
    if st != 'OK' or key not in t:
        return None
    return clean_text(first_part(t[key]))


def first_part(v):
    return v[0] if isinstance(v, tuple) else v


def changed_keys(a, b):
    return sorted([k for k in a if a[k] != b.get(k)], key=repr)


def digest(t):
    return hashlib.sha256(repr(sorted(((repr(k), repr(v)) for k, v in t.items()))).encode()).hexdigest()[:16]


# ------------------------------------------------- module code (opcode level)
def module_co_capture(i: int, bounds=None, solver=True):
    """Return (raw_co, offset_in_decoded) for the module-level code object.

    raw_co is the co_code handed to the public opcode mapper, i.e. after the
    solver when it is enabled. Nothing is executed.
    """
    meta = rv.keys[str(i)]
    exp = payload(i)
    b = list(meta['bounds'] if bounds is None else bounds)
    edges = [0] + b + [len(exp)]
    dec = b''.join(exp[edges[s]:edges[s + 1]].translate(DEC.XTABS[meta['keys'][s]]) for s in range(5))
    tr = DEC.Py25MarshalTranspiler(dec, exp, meta['keys'], b)
    captured = []
    orig = DEC.transpile_py25_code

    def spy(co):
        captured.append(bytes(co))
        return orig(co)

    patches = [patch.object(DEC, 'transpile_py25_code', side_effect=spy)]
    if not solver:
        patches.append(patch.object(DEC, 'solve_py25_co_span', return_value=None))
    for p in patches:
        p.start()
    try:
        tr.transpile_object()
    finally:
        for p in patches:
            p.stop()
    raw = max(captured, key=len)
    return raw, dec.find(raw[:64])


def opcode_site(i: int, co_offset: int, solver=True):
    _, cs = module_co_capture(i, solver=solver)
    exp, edges, keys = layout(i)
    pos = cs + co_offset
    s = seg_of(pos, edges)
    raw_byte = exp[pos]
    per_key = {}
    for seg in range(5):
        custom = raw_byte ^ keys[seg]
        std = PY25_MAP.get(custom)
        per_key[f'seg{seg}_key{keys[seg]}'] = {
            'custom_code': custom,
            'std_op': OPNAME.get(std, 'NOP') if std is not None else 'UNMAPPED_FALLBACK_NOP'}
    return {'entry_index': i, 'module_co_offset': co_offset, 'module_co_start_in_payload': cs,
            'payload_offset': pos, 'saved_segment': s, 'saved_key': keys[s],
            'saved_bounds': rv.keys[str(i)]['bounds'], 'solver_enabled': solver,
            'raw_byte_hex': f'{raw_byte:#04x}', 'per_key_reading': per_key}


# ------------------------------------------------------------ boundary probes
def shift_scan(i: int, start: int, length: int, radius: int):
    """Single-boundary shifts whose span decodes strictly. Evidence only."""
    exp, _, keys = layout(i)
    bounds = rv.keys[str(i)]['bounds']
    found = []
    for j in range(4):
        for d in range(-radius, radius + 1):
            nb = list(bounds)
            nb[j] = bounds[j] + d
            ed = [0] + nb + [len(exp)]
            if not all(a < c for a, c in zip(ed, ed[1:])):
                continue
            span = bytes(exp[off] ^ keys[seg_of(off, ed)] for off in range(start, start + length))
            ok, _, control, text = cp950_check(span)
            if ok and not control:
                found.append({'boundary_index': j, 'delta': d, 'text': text})
    return found


def verify_candidate(i: int, bounds, label: str):
    base_status, base, _ = table_status(i, solver=True)
    st, t, err = table_status(i, bounds=bounds, solver=False)
    row = {'label': label, 'bounds': list(bounds), 'solver_enabled': False, 'load_status': st}
    if st != 'OK':
        row['error'] = err
        # Solver-off failure may be unrelated to the candidate (e.g. a
        # segment that needs the solver). Report the solver-on outcome too,
        # with the caveat that the solver recomputes boundaries itself.
        st2, t2, err2 = table_status(i, bounds=bounds, solver=True)
        row['solver_on_with_candidate'] = {'load_status': st2, 'error': err2}
        if t2 is not None:
            row['solver_on_with_candidate'].update({'rows': len(t2), 'flagged_keys_after': flagged_keys(t2),
                                                   'changed_keys_vs_saved_solver_on': changed_keys(base, t2) if base is not None else None})
        return row
    row['rows'] = len(t)
    row['flagged_keys_after'] = flagged_keys(t)
    if base is not None:
        row['saved_flagged_keys_solver_on'] = flagged_keys(base)
        row['changed_keys_vs_saved_solver_on'] = changed_keys(base, t)
    return row


def window_text(i: int, start: int, length: int, bounds=None):
    exp, edges, keys = layout(i, bounds)
    span = bytes(exp[off] ^ keys[seg_of(off, edges)] for off in range(start, start + length))
    return span.hex(), cp950_check(span)[3]


# ------------------------------------------------------------------ main body
CANDIDATES = {
    '1945': [
        ('A: idx0 259583 + idx3 1038307', [259583, 519228, 778764, 1038307]),
        ('B: idx2 778764->778759', [259624, 519228, 778759, 1038363]),
        ('A+B', [259583, 519228, 778759, 1038307]),
    ],
    '17': [('idx2 5991->5980', [1959, 3924, 5980, 7998])],
    '1698': [('idx0 467->500', [500, 1078, 1548, 2036]),
             ('idx2 1548->1550', [467, 1078, 1550, 2036]),
             ('idx3 2036->2049', [467, 1078, 1548, 2049]),
             ('all three', [500, 1078, 1550, 2049])],
    '2455': [('idx3 5258->5261', [1324, 2660, 3977, 5261]),
             ('idx3 5258->5262', [1324, 2660, 3977, 5262])],
    '3791': [('idx1 1391->1397', [654, 1397, 2138, 2811]),
             ('idx2 2138->2142', [654, 1391, 2142, 2811]),
             ('both', [654, 1397, 2142, 2811])],
    '4924': [('idx0 39418->39419', [39419, 78762, 118145, 157482]),
             ('idx0 39418->39419 + idx2 118145->118143 + idx3 157482->157478', [39419, 78762, 118143, 157478])],
    '293': [('idx3 5194->5192', [1018, 2589, 3922, 5192])],
    '1381': [('idx0 2521->2524, idx1 4960->4963', [2524, 4963, 7372, 9864]),
             ('idx0 2521->2524, idx1 4960->4964', [2524, 4964, 7372, 9864]),
             ('idx0 2521->2525, idx1 4960->4963', [2525, 4963, 7372, 9864]),
             ('idx0 2521->2525, idx1 4960->4964', [2525, 4964, 7372, 9864])],
}


def build():
    out = {
        'status': 'agent_b_probe_evidence_only_no_candidate_applied',
        'inputs': {
            'script_fls_sha256': hashlib.sha256(rv.archive).hexdigest(),
            'key_database_sha256': hashlib.sha256(rv.key_bytes).hexdigest(),
            'script_fls_entry_count': ENTRY_COUNT,
            'saved_bounds_and_keys': {str(i): {'bounds': rv.keys[str(i)]['bounds'], 'keys': rv.keys[str(i)]['keys']}
                                       for i in (17, 246, 293, 1381, 1698, 1945, 2338, 2409, 2455, 3791, 4924)},
        },
        'limitations': [
            'Candidates are not verified against the native loader; they only show local consistency.',
            'Strict CP950 validity and tidy text do not prove correctness; cross-copy and cross-table agreement is weaker evidence.',
            'Reader outputs use the repository heuristic solver where noted; solver-off runs are a separate local probe.',
            'Only the item-related subset of entries is analysed here.',
        ],
    }

    # ---- bookkeeping
    bad = [i for i in range(ENTRY_COUNT) if not bookkeeping_ok(i)]
    out['bookkeeping'] = {'invalid_saved_boundary_entries': bad, 'count': len(bad)}

    # ---- 1945 item names / descriptions
    t1945 = table(1945, solver=True)
    rec = out.setdefault('records', {})
    rec['1945/DATA/10424'] = field_report(1945, t1945[10424])
    rec['1945/DATA/71700'] = field_report(1945, t1945[71700])
    rec['1945/DATA/72548'] = field_report(1945, t1945[72548])
    name_72548 = t1945[72548][0]
    rec['1945/DATA/72548/cross_copy_bytes'] = {
        'with_trailing_0x84': {str(i): locate(i, name_72548) for i in (1182, 1945, 4924)},
        'without_trailing_byte': {str(i): locate(i, name_72548[:-1]) for i in (1182, 1945, 4924)},
    }
    item_41052_candidate_bounds = list(rv.keys['1945']['bounds'])
    item_41052_candidate_bounds[2] = 778759
    t1945_saved_raw = table(1945, solver=False)
    t1945_41052_candidate = table(1945, bounds=item_41052_candidate_bounds, solver=False)
    t4924_41052_candidate = table(4924, bounds=[39419, 78762, 118143, 157478], solver=False)
    candidate_41052_name = first_part(t1945_41052_candidate[41052])
    rec['1945/DATA/41052'] = {
        'saved_fields': field_report(1945, t1945[41052]),
        'name_text_at_saved_boundaries': clean_text(first_part(t1945[41052])),
        'candidate_boundary_evidence': {
            'status': 'cross_corroborated_candidate_not_native_verified',
            'native_loader_confirmed': False,
            'boundary_index': 2,
            'saved_boundary': rv.keys['1945']['bounds'][2],
            'candidate_boundary': 778759,
            'candidate_bounds': item_41052_candidate_bounds,
            'candidate_name': clean_text(candidate_41052_name),
            'candidate_name_hex': candidate_41052_name.hex(),
            'candidate_name_locations': locate(1945, candidate_41052_name,
                                               item_41052_candidate_bounds),
            'changed_record_ids_vs_saved_raw_decode': changed_keys(t1945_saved_raw,
                                                                    t1945_41052_candidate),
            'table_rows': len(t1945_41052_candidate),
            'cross_entry_byte_evidence': {
                'entry_1182_saved_profile': locate(1182, candidate_41052_name),
                'entry_4924_saved_profile': locate(4924, candidate_41052_name),
            },
            'entry_4924_candidate_table_name': clean_text(first_part(t4924_41052_candidate[41052])),
            'note': ('Candidate decode is retained as cross-corroborated evidence only. '
                     'It is not native-loader confirmation or authorization to change '
                     'production data.'),
        },
        'copy_4924_name_candidate': clean_text(first_part(t4924_41052_candidate[41052])),
        'copy_1182_name': copy_name(1182, 41052),
    }

    # ---- 17 equipment attribute text
    t17 = table(17)
    attr_counter = collections.Counter(clean_text(v[2]) for v in t17.values() if clean_text(v[2]) is not None)
    rec['17/DATA/55010/attr'] = {
        'fields': field_report(17, t17[55010][2]),
        'top_clean_attr_texts_in_table': attr_counter.most_common(3),
    }

    # ---- 1698
    t1698 = table(1698)
    for k in (10004, 10020, 10026):
        rec[f'1698/DATA/{k}'] = field_report(1698, t1698[k])

    # ---- 2455 craft name
    t2455 = table(2455)
    rec['2455/DATA/25241/name'] = field_report(2455, t2455[25241][b'name'])

    # ---- 3791 pet items and child names
    t3791 = table(3791)
    t3791c = table(3791, b'CHILD_DATA')
    for k in (10191, 25670):
        rec[f'3791/DATA/{k}/name'] = field_report(3791, t3791[k])
    rec['3791/CHILD_DATA/72222/name'] = field_report(3791, t3791c[72222])

    # ---- 246 gem to equipment
    t246 = table(246, b'GEM2EQUIP')
    rec['246/GEM2EQUIP/72838'] = {'Name': clean_text(t246[72838][b'Name']),
                                  'EquipPos': t246[72838][b'EquipPos'], 'Desc': t246[72838][b'Desc']}

    # ---- 2409 shop
    t2409 = table(2409)
    rec['2409/DATA/8/itemid'] = field_report(2409, t2409[8][b'itemid'])

    # ---- 293 icon table: the two copies of the filename string
    rec['293/filename_copies'] = {
        'copy_at_4054_saved_bounds': window_text(293, 4054, 32),
        'copy_at_5187_saved_bounds': window_text(293, 5187, 32),
        'copy_at_5187_candidate_idx3_5192': window_text(293, 5187, 32, [1018, 2589, 3922, 5192]),
    }

    # ---- 2338 final boundary invariance
    inv = {}
    for b3 in (898, 1036):
        st, t, _ = table_status(2338, bounds=[295, 597, 897, b3], solver=False)
        inv[str(b3)] = {'status': st, 'rows': len(t) if t is not None else None,
                        'digest': digest(t) if t is not None else None}
    rec['2338/DATA/final_boundary_invariance'] = {'saved_bounds': rv.keys['2338']['bounds'], 'by_b3': inv}

    # ---- opcode-level sites
    out['opcode_sites'] = {
        '1381/co_offset_4938': opcode_site(1381, 4938, solver=True),
        '1381/co_offset_2499_solver_off': opcode_site(1381, 2499, solver=False),
        '4924/co_offset_39396': opcode_site(4924, 39396, solver=True),
        '4924/co_offset_39396_solver_off': opcode_site(4924, 39396, solver=False),
        # co 1000 is where the reader reports EXTENDED_ARG (a symptom: the
        # instruction walk is misaligned); co 1003 is the unmapped code 204 that
        # causes the misalignment. Per-key readings are instruction-start readings only
        # where the reader's own walk confirms an opcode start (see record notes).
        '293/co_offset_1000_reader_symptom': opcode_site(293, 1000, solver=True),
        '293/co_offset_1003_unmapped_root': opcode_site(293, 1003, solver=True),
    }

    # ---- boundary candidates (evidence only)
    out['boundary_candidates'] = {}
    for ident, rows in CANDIDATES.items():
        out['boundary_candidates'][ident] = [verify_candidate(int(ident), b, lab) for lab, b in rows]
    grid = {}
    grid_tables = {}
    for lab, b in CANDIDATES['1381']:
        st, t, _ = table_status(1381, bounds=b, solver=False)
        if t is not None:
            grid_tables[lab] = t
            grid[lab] = {'rows': len(t), 'digest': digest(t)}
    labels = list(grid_tables)
    if labels:
        ref = grid_tables[labels[0]]
        for lab in labels[1:]:
            t = grid_tables[lab]
            diffs = {}
            for k in sorted(set(ref) | set(t), key=repr):
                a, b2 = ref.get(k), t.get(k)
                if a != b2:
                    fields = sorted({f for f in (set(a) | set(b2)) if (a or {}).get(f) != (b2 or {}).get(f)}, key=repr) if isinstance(a, dict) and isinstance(b2, dict) else ['<whole row>']
                    diffs[repr(k)] = fields
            grid[lab]['rows_and_fields_differing_from_first_grid_point'] = {'first_grid_point': labels[0], 'count': len(diffs), 'detail': diffs}
    out['boundary_candidates']['1381_grid_detail'] = grid

    # Single-boundary scans over each flagged field's own bytes (computed from the records above).
    def field_ranges(key):
        recs = rec[key]
        recs = recs['fields'] if isinstance(recs, dict) else recs
        ranges = []
        for f in recs:
            if f.get('cp950_ok') is False or f.get('control_chars'):
                loc = f['payload_locations'][0]
                ranges.append((loc['payload_offset'], len(bytes.fromhex(f['decoded_hex']))))
        return ranges

    scans = {}
    for key, owner in [('1945/DATA/10424', 1945), ('1945/DATA/71700', 1945), ('1698/DATA/10004', 1698),
                       ('1698/DATA/10020', 1698), ('1698/DATA/10026', 1698), ('17/DATA/55010/attr', 17),
                       ('2455/DATA/25241/name', 2455), ('3791/DATA/10191/name', 3791),
                       ('3791/DATA/25670/name', 3791)]:
        scans[key] = [{'field_payload_offset': a, 'field_length': n,
                       'valid_single_boundary_shifts': shift_scan(owner, a, n, 64)}
                      for a, n in field_ranges(key)]
    out['boundary_candidates']['shift_scans_single_boundary'] = scans

    # ---- cross-table checks (names only; no value-structure comparison)
    item_name = {k: clean_text(first_part(v)) for k, v in t1945.items()}
    cross = {}
    cross['246_GEM2EQUIP_vs_1945_items'] = {
        'compared': sum(1 for k in t246 if k in t1945),
        'equal': sum(1 for k, v in t246.items() if k in t1945 and clean_text(v[b'Name']) == item_name.get(k)),
        'differ': [[k, clean_text(v[b'Name']), item_name.get(k)] for k, v in t246.items()
                   if k in t1945 and clean_text(v[b'Name']) != item_name.get(k)]}
    cross['3791_CHILD_DATA_vs_1945_items'] = {
        'compared': sum(1 for k in t3791c if k in t1945),
        'equal': sum(1 for k, v in t3791c.items() if k in t1945 and clean_text(v) == item_name.get(k)),
        'differ': [[k, clean_text(v), item_name.get(k)] for k, v in t3791c.items()
                   if k in t1945 and clean_text(v) != item_name.get(k)]}
    cross['2455_craft_vs_1945_items'] = {
        'compared': sum(1 for k in t2455 if k in t1945),
        'equal': sum(1 for k, v in t2455.items() if k in t1945 and clean_text(v[b'name']) == item_name.get(k)),
        'differ': [[k, clean_text(v[b'name']), item_name.get(k)] for k, v in t2455.items()
                   if k in t1945 and clean_text(v[b'name']) != item_name.get(k)]}
    cross['3791_DATA_vs_1945_items'] = {
        'compared': sum(1 for k in t3791 if k in t1945),
        'equal': sum(1 for k, v in t3791.items() if k in t1945 and clean_text(first_part(v)) == item_name.get(k)),
        'differ': [[k, clean_text(first_part(v)), item_name.get(k)] for k, v in t3791.items()
                   if k in t1945 and clean_text(first_part(v)) != item_name.get(k)]}
    shop = []
    for k, v in sorted(t2409.items()):
        iid = v[b'itemid']
        shop.append({'row': k, 'itemid_kind': 'int' if isinstance(iid, int) else 'bytes',
                     'itemid': iid if isinstance(iid, int) else clean_text(iid),
                     'in_item_table': isinstance(iid, int) and iid in t1945,
                     'shop_name': clean_text(v[b'name']),
                     'item_name': item_name.get(iid) if isinstance(iid, int) else None,
                     'type': v[b'type'], 'price': v[b'price'], 'num': v[b'num'],
                     'discount_text': clean_text(v[b'discount']) if isinstance(v[b'discount'], bytes) else v[b'discount']})
    cross['2409_shop_rows'] = shop

    t4924 = table(4924, bounds=[39419, 78762, 118143, 157478], solver=False)
    cross['1945_vs_4924_names_with_candidates'] = {
        'compared': len(t1945), 'equal': sum(1 for k in t1945 if first_part(t4924[k]) == first_part(t1945[k])),
        'differ': [k for k in t1945 if first_part(t4924[k]) != first_part(t1945[k])],
        'flagged_keys_4924_candidate': flagged_keys(t4924)}
    cross['1945_vs_4924_names_saved_bounds'] = {
        'compared': len(t1945)}
    try:
        t4924s = table(4924, bounds=[39418, 78762, 118145, 157482], solver=False)
        cross['1945_vs_4924_names_saved_bounds']['status'] = 'OK'
    except Exception as ex:
        cross['1945_vs_4924_names_saved_bounds']['status'] = f'FAIL {type(ex).__name__}: {ex}'
    t1945_ab = table(1945, bounds=[259583, 519228, 778759, 1038307], solver=False)
    cross['1945_A+B_vs_4924_candidate_names'] = {
        'compared': len(t1945_ab),
        'equal': sum(1 for k in t1945_ab if first_part(t4924[k]) == first_part(t1945_ab[k])),
        'differ': [k for k in t1945_ab if first_part(t4924[k]) != first_part(t1945_ab[k])],
        'flagged_keys_1945_A+B': flagged_keys(t1945_ab)}
    out['cross_checks'] = cross
    # 246 EquipPos value distribution (is 54 unique?) and 2338 flagged keys
    eq_counter = collections.Counter(x for v in t246.values() for x in (v[b'EquipPos'] if isinstance(v.get(b'EquipPos'), list) else []))
    rec['246/GEM2EQUIP/EquipPos_value_counts'] = dict(sorted(eq_counter.items()))
    st2338, t2338, err2338 = table_status(2338)
    rec['2338/DATA/saved_bounds_load'] = {'status': st2338, 'error': err2338,
                                          'note': 'saved boundary list is not strictly increasing; reader refuses it'}

    needles = ['雙人坐騎體驗', '隨機終級獸訣', '隨機特殊獸訣', '寶石附魔符', '寶石附魔', '神武項圈', '武神項圈',
               '白芒角樽', '雙技能英靈護符', '蜜香果燒肉', '一級彩虹果', '時空石', '晉怖肋', '飛蝗石']
    scan = {n: [] for n in needles}
    for i in range(ENTRY_COUNT):
        if not bookkeeping_ok(i):
            continue
        dec = decoded(i)
        for n in needles:
            if n.encode('cp950') in dec:
                scan[n].append(i)
    out['cross_checks']['global_name_presence_entries'] = scan
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', help='write JSON here instead of stdout')
    args = ap.parse_args(argv)
    text = json.dumps(build(), ensure_ascii=False, indent=2, sort_keys=True, default=str)
    if args.out:
        Path(args.out).write_text(text + '\n', encoding='utf-8')
    else:
        print(text)


if __name__ == '__main__':
    main()
