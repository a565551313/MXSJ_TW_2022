#!/usr/bin/env python3
"""Agent F probe 65 — entry 244, structural/no-solver furniture verification.

All code and table evidence is recomputed from the raw XOR-decoded payload.
Every transpilation explicitly disables solve_py25_co_span. The root co_code
range is obtained by parsing the marshal object structure; constant-pool bytes
are never scanned as opcodes. Only the bounded DATA literal-assignment segment
is evaluated with a local allowlist; no recovered code runs, and the shared
public reader remains unchanged. DATA field strings are audited separately from
non-DATA constants.

This is extraction evidence only. Neither candidate boundary is native-loader
verified, and no data is written to server/game_data/.
"""
from __future__ import annotations

import collections
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'server/tools'))

from tools.decompiler import batch_decompile as decoder  # noqa: E402
from tools.fls_batch_decoder import MarshalReader  # noqa: E402
from verify_client_data_boundaries import Archive  # noqa: E402
from review_client_data_boundaries import instructions  # noqa: E402

ENTRY = 244
MODULE_NAME = b'<module>'
EXPECTED_FIELDS = frozenset({
    b'ani', b'base_cost', b'beauty', b'beauty_limit', b'bg_type', b'cost',
    b'desc', b'direct', b'grade', b'layer', b'lianxuplace', b'lv', b'name',
    b'pagename', b'pre', b'special', b'stablepath', b'subtype', b'type', b'zoff',
})

# These values are explicit inputs to a local candidate scan, not accepted
# native parameters. The first boundary is varied in a small, recorded window.
CANDIDATE_KEYS = [233, 11, 132, 105, 246]
CANDIDATE_REST_BOUNDS = [36511, 54797, 73114]
LEGACY_CANDIDATE_B0 = 18282
SCAN_B0_START = 18280
SCAN_B0_END = 18298  # exclusive; a bounded local scan, not an exhaustive search


class SpanTrackingMarshalReader(MarshalReader):
    """MarshalReader that records co_code byte ranges while parsing code objects.

    The start/end values are offsets in the *raw decrypted marshal payload*.
    They are derived from the TYPE_CODE and string-object structure, not from a
    hard-coded offset or from the transpiler's normalized output.
    """

    def __init__(self, data: bytes):
        super().__init__(data)
        self.code_spans: list[dict] = []

    def read_code_object(self):
        object_start = self.pos - 1
        argcount = struct.unpack('<i', self.take(4))[0]
        nlocals = struct.unpack('<i', self.take(4))[0]
        stacksize = struct.unpack('<i', self.take(4))[0]
        flags = struct.unpack('<i', self.take(4))[0]

        code_tag_at = self.pos
        code = self.read()
        code_tag = self.data[code_tag_at]
        if code_tag not in (ord('s'), ord('t'), ord('a'), ord('A')):
            raise ValueError(f'co_code is not a direct marshal string at {code_tag_at}')
        code_length = struct.unpack_from('<I', self.data, code_tag_at + 1)[0]
        code_start = code_tag_at + 5
        code_end = code_start + code_length
        if code_end != self.pos or not isinstance(code, bytes) or len(code) != code_length:
            raise ValueError(f'co_code marshal span mismatch at {code_tag_at}')

        consts = self.read()
        names = self.read()
        varnames = self.read()
        freevars = self.read()
        cellvars = self.read()
        filename = self.read()
        name = self.read()
        firstlineno = struct.unpack('<i', self.take(4))[0]
        lnotab = self.read()
        record = {
            'offset': object_start, 'argcount': argcount, 'nlocals': nlocals,
            'stacksize': stacksize, 'flags': flags, 'code': code,
            'consts': consts, 'names': names, 'varnames': varnames,
            'freevars': freevars, 'cellvars': cellvars, 'filename': filename,
            'name': name, 'firstlineno': firstlineno, 'lnotab': lnotab,
        }
        self.code_spans.append({
            'object_offset': object_start,
            'code_start': code_start,
            'code_end': code_end,
            'code_length': code_length,
            'name': name,
            'filename': filename,
        })
        self.code_objects.append(record)
        return record


def parse_raw_module(decoded: bytes):
    """Parse a raw decrypted marshal payload and return its derived root code span."""
    reader = SpanTrackingMarshalReader(decoded)
    root = reader.read()
    if reader.pos != len(reader.data):
        raise ValueError(f'marshal reader consumed {reader.pos} of {len(reader.data)} bytes')
    if not isinstance(root, dict) or root.get('name') != MODULE_NAME:
        raise ValueError(f'entry {ENTRY} root is not the expected module code object')
    matches = [item for item in reader.code_spans
               if item['object_offset'] == root['offset']]
    if len(matches) != 1:
        raise ValueError(f'expected one root co_code span, found {len(matches)}')
    span = matches[0]
    if decoded[span['code_start']:span['code_end']] != root['code']:
        raise ValueError('derived root co_code span does not match parsed co_code')
    return root, reader, span


def duoyi_opcode_stats(decoded: bytes, start: int, end: int) -> dict:
    """Count Duoyi instructions only inside a structurally-derived co_code span."""
    if not (0 <= start <= end <= len(decoded)):
        raise ValueError(f'co_code range [{start},{end}) exceeds payload length {len(decoded)}')
    at = start
    count = 0
    unmapped = []
    while at < end:
        op = decoded[at]
        width = 3 if op >= 0x5F else 1  # Duoyi HAVE_ARGUMENT
        if at + width > end:
            raise ValueError(f'truncated Duoyi instruction at {at} within [{start},{end})')
        if decoder.PY25_MAP.get(op) is None:
            unmapped.append(at)
        count += 1
        at += width
    if at != end:
        raise ValueError(f'Duoyi walk ended at {at}, expected {end}')
    return {'instruction_count': count, 'unmapped_positions': unmapped,
            'unmapped_count': len(unmapped)}


def locate_boundary(decoded: bytes, start: int, end: int, boundary: int) -> str:
    """Describe whether a key boundary is on an opcode or inside its operand."""
    if not start <= boundary <= end:
        return 'outside co_code'
    at = start
    while at < end:
        width = 3 if decoded[at] >= 0x5F else 1
        if boundary == at:
            return f'instruction start at {at}'
        if at < boundary < at + width:
            return f'operand byte {boundary - at} of instruction at {at}'
        at += width
    return 'co_code end' if boundary == end else 'not on walked instruction'


def root_code_evidence(archive: Archive, bounds=None, keys=None) -> dict:
    """Decrypt and structurally measure co_code without invoking any solver."""
    decoded = archive.decode(ENTRY, bounds=bounds, keys=keys)
    root, marshal_reader, span = parse_raw_module(decoded)
    stats = duoyi_opcode_stats(decoded, span['code_start'], span['code_end'])
    return {
        'decoded': decoded,
        'root': root,
        'marshal_reader': marshal_reader,
        'span': span,
        'stats': stats,
    }


def _display_value(value):
    if isinstance(value, bytes):
        try:
            text = value.decode('cp950')
        except UnicodeDecodeError:
            return f'bytes(len={len(value)}, invalid_cp950={value.hex()})'
        return f'bytes(len={len(value)}, cp950={text!r})'
    return repr(value)


def extract_data_assignment(co: dict, name: bytes = b'DATA') -> dict:
    """Safely evaluate only the selected DATA literal-assignment bytecode segment.

    This is intentionally not the public whole-module strict reader: the current
    module contains unrelated LOAD_NAME/MAKE_FUNCTION shapes. The segment starts
    immediately after the previous module-level name store, ends at STORE_NAME
    DATA, and accepts only literal-building opcodes plus the exact LOAD_NAME
    b'None'. It never executes recovered code. A successful result verifies only
    this bounded assignment, not the whole module or the native loader.
    """
    stream = list(instructions(co))
    stores = []
    names = co.get('names', ())
    for index, (at, op, arg) in enumerate(stream):
        if op not in (90, 97):  # STORE_NAME / STORE_GLOBAL
            continue
        if arg is None or not 0 <= arg < len(names):
            raise ValueError(f'invalid name index at {at}')
        stores.append((index, at, op, names[arg]))

    matches = [item for item in stores if item[2] == 90 and item[3] == name]
    if len(matches) != 1:
        raise ValueError(f'expected one STORE_NAME {name!r}, found {len(matches)}')
    target_index, target_at, target_op, target_name = matches[0]
    previous = [item for item in stores if item[0] < target_index]
    segment_start_index = previous[-1][0] + 1 if previous else 0
    segment = stream[segment_start_index:target_index + 1]
    if not segment:
        raise ValueError('empty DATA literal assignment segment')

    stack = []
    data_table = None
    data_writes = 0
    data_overwrites = []
    dictionary_overwrites = []
    consts = co.get('consts', ())
    for at, op, arg in segment:
        if op == 100:  # LOAD_CONST
            if arg is None or not 0 <= arg < len(consts):
                raise ValueError(f'invalid constant index at {at}')
            stack.append(consts[arg])
        elif op == 101:  # LOAD_NAME: permit only the literal spelling None
            if arg is None or not 0 <= arg < len(names) or names[arg] != b'None':
                raise ValueError(f'unsupported LOAD_NAME at {at}')
            stack.append(None)
        elif op in (102, 103):  # BUILD_TUPLE / BUILD_LIST
            if arg is None or arg > len(stack):
                raise ValueError(f'stack underflow at {at}')
            values = stack[-arg:] if arg else []
            if arg:
                del stack[-arg:]
            stack.append(tuple(values) if op == 102 else list(values))
        elif op == 104:  # BUILD_MAP
            value = {}
            if data_table is None and not stack:
                data_table = value
            stack.append(value)
        elif op == 4:  # DUP_TOP
            if not stack:
                raise ValueError(f'stack underflow at {at}')
            stack.append(stack[-1])
        elif op == 2:  # ROT_TWO
            if len(stack) < 2:
                raise ValueError(f'stack underflow at {at}')
            stack[-2], stack[-1] = stack[-1], stack[-2]
        elif op == 60:  # STORE_SUBSCR; mirror literal dict last-write behavior
            if len(stack) < 3:
                raise ValueError(f'stack underflow at {at}')
            key, target, value = stack.pop(), stack.pop(), stack.pop()
            if type(target) is not dict:
                raise ValueError(f'non-dictionary store at {at}')
            if key in target:
                item = {'key': _display_value(key), 'at': at,
                        'target_is_DATA': target is data_table}
                dictionary_overwrites.append(item)
                if target is data_table:
                    data_overwrites.append(item)
            if target is data_table:
                data_writes += 1
            target[key] = value
        elif op == target_op and at == target_at and op in (90, 97):
            if target_name != name or len(stack) != 1:
                raise ValueError(f'invalid final DATA stack at {at}')
            value = stack.pop()
            if value is not data_table or type(value) is not dict:
                raise ValueError(f'DATA assignment at {at} did not publish its root dict')
            return {
                'value': value,
                'store': 'STORE_NAME',
                'store_at': target_at,
                'segment_start': segment[0][0],
                'writes': data_writes,
                'overwrites': tuple(data_overwrites),
                'all_dictionary_overwrites': tuple(dictionary_overwrites),
                'assignment_complete': True,
                'module_verified': False,
                'verification_scope': 'bounded DATA assignment segment only',
            }
        else:
            raise ValueError(f'unsupported opcode {op} in DATA assignment at {at}')
    raise ValueError('missing final DATA store')


def audit_data_fields(data: dict) -> dict:
    """Validate all rows/fields and every bytes-valued DATA field independently."""
    errors = []
    if type(data) is not dict:
        return {'ok': False, 'errors': ['DATA is not a dict']}
    if len(data) != 233:
        errors.append(f'expected 233 records, got {len(data)}')

    field_types = collections.defaultdict(collections.Counter)
    byte_counts = collections.Counter()
    byte_values = []
    text_errors = []
    controls = []
    for record_id, row in data.items():
        if type(row) is not dict:
            errors.append(f'DATA[{record_id!r}] is not a dict')
            continue
        if set(row) != EXPECTED_FIELDS:
            errors.append(f'DATA[{record_id!r}] field set differs from expected 20 fields')
        for field, value in row.items():
            if not isinstance(field, bytes):
                errors.append(f'DATA[{record_id!r}] has non-bytes field key {field!r}')
                field_name = repr(field)
            else:
                try:
                    field_name = field.decode('ascii')
                except UnicodeDecodeError:
                    errors.append(f'DATA[{record_id!r}] has non-ASCII field key {field.hex()}')
                    field_name = field.hex()
            field_types[field_name][type(value).__name__] += 1
            if isinstance(value, bytes):
                byte_counts[field_name] += 1
                byte_values.append(value)
                try:
                    text = value.decode('cp950')
                except UnicodeDecodeError as exc:
                    text_errors.append({
                        'record': record_id, 'field': field_name,
                        'reason': 'invalid_cp950', 'start': exc.start,
                        'hex': value.hex(),
                    })
                    continue
                bad_chars = [ord(char) for char in text
                             if (ord(char) < 32 and char not in '\t\n\r')
                             or ord(char) == 127]
                if bad_chars:
                    controls.append({
                        'record': record_id, 'field': field_name,
                        'codepoints': bad_chars, 'hex': value.hex(),
                    })
    if text_errors:
        errors.append(f'{len(text_errors)} DATA field byte value(s) fail strict CP950')
    if controls:
        errors.append(f'{len(controls)} DATA field byte value(s) contain controls')
    return {
        'ok': not errors,
        'errors': errors,
        'record_count': len(data),
        'field_count': len(EXPECTED_FIELDS),
        'field_names': sorted(field.decode('ascii') for field in EXPECTED_FIELDS),
        'field_type_counts': {name: dict(counts)
                              for name, counts in sorted(field_types.items())},
        'byte_values_by_field': dict(sorted(byte_counts.items())),
        'data_byte_value_count': len(byte_values),
        'cp950_failure_count': len(text_errors),
        'cp950_failures': text_errors,
        'control_value_count': len(controls),
        'control_values': controls,
        'data_byte_values': byte_values,
    }


def _is_code_record(value) -> bool:
    return (isinstance(value, dict)
            and {'offset', 'code', 'consts', 'names', 'filename', 'name'} <= set(value))


def _iter_constant_bytes(value):
    if isinstance(value, bytes):
        yield value
    elif isinstance(value, (tuple, list, set, frozenset)):
        for item in value:
            yield from _iter_constant_bytes(item)
    elif isinstance(value, dict) and not _is_code_record(value):
        for key, item in value.items():
            yield from _iter_constant_bytes(key)
            yield from _iter_constant_bytes(item)


def audit_constant_pool(reader: SpanTrackingMarshalReader, data_byte_values: list[bytes]) -> dict:
    """Audit code-object co_consts separately; do not call it DATA text evidence."""
    pool_values = []
    for code_object in reader.code_objects:
        for constant in code_object['consts']:
            if not _is_code_record(constant):
                pool_values.extend(_iter_constant_bytes(constant))

    # This is a value-multiset comparison, not source provenance. It separates
    # byte values represented in DATA fields from additional co_consts values.
    remaining_data = collections.Counter(data_byte_values)
    data_value_matches = 0
    additional_pool_values = []
    issues = []
    for value in pool_values:
        is_data_value = remaining_data[value] > 0
        if is_data_value:
            remaining_data[value] -= 1
            data_value_matches += 1
        try:
            text = value.decode('cp950')
        except UnicodeDecodeError as exc:
            issues.append({
                'classification': 'DATA-value-matched' if is_data_value else 'additional-pool-value',
                'reason': 'invalid_cp950', 'start': exc.start, 'hex': value.hex(),
            })
            if not is_data_value:
                additional_pool_values.append(value)
            continue
        has_control = any((ord(char) < 32 and char not in '\t\n\r') or ord(char) == 127
                          for char in text)
        if has_control:
            issues.append({
                'classification': 'DATA-value-matched' if is_data_value else 'additional-pool-value',
                'reason': 'control_character', 'hex': value.hex(),
            })
        if not is_data_value:
            additional_pool_values.append(value)

    additional_issues = [issue for issue in issues
                         if issue['classification'] == 'additional-pool-value']
    data_matched_issues = [issue for issue in issues
                           if issue['classification'] == 'DATA-value-matched']
    return {
        'code_object_count': len(reader.code_objects),
        'byte_constant_occurrences': len(pool_values),
        'data_value_matched_occurrences': data_value_matches,
        'additional_pool_value_occurrences': len(additional_pool_values),
        'additional_pool_values_cp950_or_control_issues': additional_issues,
        'data_value_matched_cp950_or_control_issues': data_matched_issues,
        'all_pool_issues': issues,
        'classification_note': (
            'DATA-value-matched vs additional pool values is a byte-value multiset '
            'comparison, not proof of constant-source provenance. co_code and '
            'co_lnotab are not co_consts and are not treated as DATA text.'),
    }


def audit_candidate(archive: Archive, bounds: list[int], keys: list[int]) -> dict:
    """No-solver decode/transpile and bounded DATA plus field/pool audits."""
    raw = root_code_evidence(archive, bounds=bounds, keys=keys)
    if raw['stats']['unmapped_count']:
        raise ValueError(f"{raw['stats']['unmapped_count']} unmapped code-only opcode(s)")
    # Explicit on every call: do not let solve_py25_co_span rewrite this candidate.
    co = archive.transpile(ENTRY, bounds=bounds, keys=keys, use_solver=False)
    normalized_instructions = list(instructions(co))
    report = extract_data_assignment(co, b'DATA')
    data_audit = audit_data_fields(report['value'])
    if not data_audit['ok']:
        raise ValueError('; '.join(data_audit['errors']))
    if (report['writes'] != data_audit['record_count'] or report['overwrites']
            or report['all_dictionary_overwrites']):
        raise ValueError('DATA dictionary write count/overwrite audit failed')
    pool_audit = audit_constant_pool(raw['marshal_reader'], data_audit['data_byte_values'])
    return {
        'bounds': list(bounds), 'keys': list(keys),
        'raw': raw,
        'normalized_instruction_count': len(normalized_instructions),
        'data_report': report,
        'data_audit': data_audit,
        'constant_pool_audit': pool_audit,
    }


def _short_error(exc: Exception, limit: int = 112) -> str:
    text = f'{type(exc).__name__}: {exc}'.replace('\n', ' ')
    return text if len(text) <= limit else text[:limit - 3] + '...'


def scan_first_boundary(archive: Archive) -> tuple[list[dict], list[dict]]:
    """Run the bounded no-solver B0 scan and return rows plus fully checked candidates."""
    rows = []
    accepted = []
    for b0 in range(SCAN_B0_START, SCAN_B0_END):
        bounds = [b0, *CANDIDATE_REST_BOUNDS]
        try:
            raw = root_code_evidence(archive, bounds=bounds, keys=CANDIDATE_KEYS)
            stats = raw['stats']
            boundary = locate_boundary(raw['decoded'], raw['span']['code_start'],
                                       raw['span']['code_end'], b0)
        except Exception as exc:
            rows.append({'b0': b0, 'status': 'raw-parse-failed', 'error': _short_error(exc)})
            continue

        row = {
            'b0': b0,
            'instruction_count': stats['instruction_count'],
            'unmapped_count': stats['unmapped_count'],
            'unmapped_positions': stats['unmapped_positions'],
            'boundary_location': boundary,
        }
        try:
            checked = audit_candidate(archive, bounds, CANDIDATE_KEYS)
            row['status'] = 'target DATA assignment audited'
            row['data_records'] = checked['data_audit']['record_count']
            row['data_bytes'] = checked['data_audit']['data_byte_value_count']
            accepted.append(checked)
            row['checked_candidate'] = checked
        except Exception as exc:
            row['status'] = 'rejected: ' + _short_error(exc)
        rows.append(row)
    return rows, accepted


def compare_data_tables(left: dict, right: dict) -> list[dict]:
    differences = []
    for record_id in sorted(set(left) | set(right), key=repr):
        left_row, right_row = left.get(record_id), right.get(record_id)
        if not isinstance(left_row, dict) or not isinstance(right_row, dict):
            if left_row != right_row:
                differences.append({'record': record_id, 'field': '<row>',
                                    'left': _display_value(left_row),
                                    'right': _display_value(right_row)})
            continue
        for field in sorted(set(left_row) | set(right_row), key=repr):
            a, b = left_row.get(field), right_row.get(field)
            if a != b:
                differences.append({'record': record_id,
                                    'field': field.decode('ascii') if isinstance(field, bytes) else repr(field),
                                    'left': _display_value(a), 'right': _display_value(b)})
    return differences


def _print_stats(label: str, evidence: dict) -> None:
    span = evidence['span']
    stats = evidence['stats']
    first = stats['unmapped_positions'][:8]
    suffix = ' ...' if stats['unmapped_count'] > len(first) else ''
    print(f'{label}: raw root co_code=[{span["code_start"]},{span["code_end"]}) '
          f'len={span["code_length"]}; Duoyi instructions={stats["instruction_count"]}; '
          f'unmapped={stats["unmapped_count"]} first={first}{suffix}')


def print_code_statistics() -> None:
    """Small reusable code-only comparison for probe66; no solver/table evaluator."""
    archive = Archive()
    saved = archive.keys[str(ENTRY)]
    _print_stats('saved parameters', root_code_evidence(archive))
    old_bounds = [LEGACY_CANDIDATE_B0, *CANDIDATE_REST_BOUNDS]
    _print_stats('previous B0=18282 candidate',
                 root_code_evidence(archive, bounds=old_bounds, keys=CANDIDATE_KEYS))
    for b0 in (18289, 18290):
        bounds = [b0, *CANDIDATE_REST_BOUNDS]
        _print_stats(f'no-solver B0={b0} local candidate',
                     root_code_evidence(archive, bounds=bounds, keys=CANDIDATE_KEYS))


def run() -> None:
    archive = Archive()
    saved = archive.keys[str(ENTRY)]
    print('entry=244 (newfurnituredata.py) — structural/no-solver audit')
    print('solver: disabled; raw opcode stats use Archive.decode; the bounded '
          'DATA assignment uses an allowlisted non-executing literal reader')
    print('shared public whole-module reader and review/export inputs are unchanged')
    print('native_loader_confirmed=false; no files under server/game_data are written')
    print()

    _print_stats('saved parameters', root_code_evidence(archive))
    legacy_bounds = [LEGACY_CANDIDATE_B0, *CANDIDATE_REST_BOUNDS]
    _print_stats('previous candidate (B0=18282)',
                 root_code_evidence(archive, bounds=legacy_bounds, keys=CANDIDATE_KEYS))
    print('derived range is per decoded marshal structure; co_consts/co_lnotab are not opcode input')
    print()

    rows, candidates = scan_first_boundary(archive)
    print(f'bounded first-boundary scan B0=[{SCAN_B0_START},{SCAN_B0_END}) '
          '(candidate rows are not native verification):')
    for row in rows:
        if row.get('status') == 'raw-parse-failed':
            print(f'  {row["b0"]}: {row["status"]}: {row["error"]}')
            continue
        positions = row['unmapped_positions']
        print(f'  {row["b0"]}: opcodes={row["instruction_count"]} '
              f'unmapped={row["unmapped_count"]} positions={positions}; '
              f'boundary={row["boundary_location"]}; {row["status"]}')
    print()

    for candidate in candidates:
        b0 = candidate['bounds'][0]
        span = candidate['raw']['span']
        stats = candidate['raw']['stats']
        report = candidate['data_report']
        data = report['value']
        field_audit = candidate['data_audit']
        pool = candidate['constant_pool_audit']
        print(f'candidate B0={b0}: bounds={candidate["bounds"]} keys={candidate["keys"]}')
        print(f'  root co_code=[{span["code_start"]},{span["code_end"]}) '
              f'len={span["code_length"]}; instruction_count={stats["instruction_count"]}; '
              f'unmapped={stats["unmapped_count"]}')
        print(f'  bounded DATA assignment: complete={report["assignment_complete"]} '
              f'module_verified={report["module_verified"]} records={len(data)} '
              f'root_writes={report["writes"]} root_overwrites={len(report["overwrites"])} '
              f'all_dict_overwrites={len(report["all_dictionary_overwrites"])} '
              f'normalized_instructions={candidate["normalized_instruction_count"]}')
        print(f'  DATA field audit: rows={field_audit["record_count"]}, '
              f'fields/row={field_audit["field_count"]}, '
              f'bytes={field_audit["data_byte_value_count"]}, '
              f'CP950 failures={field_audit["cp950_failure_count"]}, '
              f'controls={field_audit["control_value_count"]}')
        print('  DATA byte-valued fields: ' + ', '.join(
            f'{name}={count}' for name, count in field_audit['byte_values_by_field'].items()))
        print(f'  full code-object co_consts byte audit (separate): '
              f'code_objects={pool["code_object_count"]}, '
              f'byte_constants={pool["byte_constant_occurrences"]}, '
              f'value-matched-to-DATA={pool["data_value_matched_occurrences"]}, '
              f'additional-pool-values={pool["additional_pool_value_occurrences"]}, '
              f'pool issues={len(pool["all_pool_issues"])}')
        print('  pool classification: ' + pool['classification_note'])
        print()

    if len(candidates) > 1:
        left, right = candidates[0], candidates[1]
        differences = compare_data_tables(left['data_report']['value'],
                                          right['data_report']['value'])
        print('surviving candidate DATA differences (not auto-resolved):')
        for item in differences:
            print(f'  DATA[{item["record"]}].{item["field"]}: '
                  f'B0={left["bounds"][0]} {item["left"]} <> '
                  f'B0={right["bounds"][0]} {item["right"]}')
        if not differences:
            print('  none; values agree across the checked candidates')
        print()

    print('scope/limitations: the bounded scan is not exhaustive; only the DATA '
          'literal-assignment segment was evaluated, not the whole module; assignment '
          'completeness and CP950 success do not prove native-client behavior.')


if __name__ == '__main__':
    run()
