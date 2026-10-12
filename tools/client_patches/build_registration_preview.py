#!/usr/bin/env python3
"""Build an out-of-place, version-pinned registration-UI smoke-test archive.

No recovered code is executed. Only fixed-width co_code spans are changed;
v2 also replaces two pinned literals without resizing them. Marshal layout, XOR
boundaries and every unrelated entry are retained.
This is NOT a working registration client or a network sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.decompiler.batch_decompile import PY25_MAP, XTABS, check_py25_co_code
from tools.fls_batch_decoder import MarshalReader

BASE_SHA256 = '8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72'
KEYS_SHA256 = '43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb'
INV = {value: key for key, value in PY25_MAP.items()}
TARGET_ENTRIES = {337, 4007}
STAGES = ('terms', 'form')
NETWORK_PATHS = {
    'CCheckCodeBox/RequestNewCode', 'CRegPanel2/DoNext',
    'CRegPanel2_2980/RequestPhoneValid', 'CRegPanel2_2980/RequestPhoneCode',
    'CRegPanel2_2980/RequestPhoneVoiceCode', 'CRegPanel2_2980/RequestEmailValid',
    'CRegPanel2_2980/DoRegist', 'CRegPanel2_2980/OnMessage', 'CRegPanel4/OnMessage',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def entries(archive):
    require(archive[:4] == b'0SLF', 'not a 0SLF archive')
    count, directory = struct.unpack_from('<II', archive, 4)
    require(directory + count * 16 == len(archive), 'unexpected directory layout')
    result = []
    for index in range(count):
        eid, r1, r2, r3 = struct.unpack_from('<IIII', archive, directory + index * 16)
        size = ((r1 * eid + 0xDF25E) & 0xFFFFFFFF) ^ r2
        pos = ((r2 * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ r3
        require(12 <= pos and pos + size <= directory, f'entry {index}: out-of-range payload')
        result.append(((eid, r1, r2, r3), archive[pos:pos + size]))
    return directory, result


def xor_payload(payload, metadata):
    edges = [0, *metadata['bounds'], len(payload)]
    require(len(edges) == 6 and all(a < b for a, b in zip(edges, edges[1:])), 'bad XOR boundaries')
    return b''.join(payload[edges[i]:edges[i + 1]].translate(XTABS[metadata['keys'][i]])
                    for i in range(5))


def tree(data):
    reader = MarshalReader(data)
    root = reader.read()
    require(reader.pos == len(data), 'marshal did not consume full payload')
    return root


def objects(co, prefix=''):
    name = co['name'].decode('ascii')
    path = f'{prefix}/{name}'.strip('/') if name != '<module>' else ''
    yield path, co
    for value in co['consts']:
        if isinstance(value, dict) and 'code' in value:
            yield from objects(value, path)


def assemble(*instructions):
    result = bytearray()
    for op, arg in instructions:
        encoded = INV[op]
        require((encoded >= 0x5F) == (op >= 90), 'opcode width mismatch')
        result.append(encoded)
        if op >= 90:
            result.extend(struct.pack('<H', arg))
        else:
            require(arg is None, 'unexpected opcode argument')
    return bytes(result)


def normalized(code):
    result = []
    at = 0
    while at < len(code):
        raw = code[at]
        require(raw in PY25_MAP, f'unknown opcode at {at}')
        size = 3 if raw >= 0x5F else 1
        require(at + size <= len(code), 'truncated opcode')
        arg = int.from_bytes(code[at + 1:at + 3], 'little') if size == 3 else None
        result.append((at, PY25_MAP[raw], arg))
        at += size
    return result


def valid_code(co, code):
    limits = (len(co['consts']), len(co['names']), len(co['varnames']),
              len(co['freevars']) + len(co['cellvars']), len(code))
    require(check_py25_co_code(code, limits)[0], 'invalid opcode or argument')
    sequence = normalized(code)
    starts = {at for at, _, _ in sequence} | {len(code)}
    for at, op, arg in sequence:
        if op in {113, 119}:
            require(arg in starts, f'unaligned absolute jump at {at}')
        elif op in {93, 110, 111, 112, 120, 121, 122}:
            require(at + 3 + arg in starts, f'unaligned relative jump at {at}')


def patch_payload(index, plain, metadata, stage='terms'):
    require(stage in STAGES, 'unsupported preview stage')
    co_by_path = dict(objects(tree(plain)))
    changed = bytearray(plain)
    changes = []
    allowed = set()
    changed_constants = {}

    def replace(path, offset, expected_ops, replacement, length=None):
        co = co_by_path[path]
        old = co['code']
        valid_code(co, old)
        size = len(replacement) if length is None else length
        require(len(replacement) <= size, 'patch is too long')
        sequence = normalized(old)
        require(offset in {at for at, _, _ in sequence}, 'patch start is not aligned')
        require(offset + size in {at for at, _, _ in sequence} | {len(old)}, 'patch end is not aligned')
        actual = [(op, arg) for at, op, arg in sequence if offset <= at < offset + size]
        if expected_ops is not None:
            require(actual == expected_ops, f'{path}: source instruction fingerprint mismatch')
        start = co['offset'] + 22 + offset  # c + four ints + s + string length
        require(plain[co['offset']] == ord('c') and plain[co['offset'] + 17] in (ord('s'), ord('t')),
                'unexpected code-object layout')
        require(plain[start:start + size] == old[offset:offset + size], 'raw co_code offset mismatch')
        require(not any(start <= b < start + size for b in metadata['bounds']),
                'patch spans an unverified XOR boundary')
        new = replacement + assemble((9, None)) * (size - len(replacement))
        changed[start:start + size] = new
        allowed.update(range(start, start + size))
        changes.append({'function': path, 'co_code_offset': offset, 'payload_offset': start,
                        'span_bytes': size, 'before_sha256': sha(plain[start:start + size]),
                        'after_sha256': sha(new)})

    def replace_constant(path, constant_index, expected_text, new_text):
        old = co_by_path[path]['consts'][constant_index]
        require(old == expected_text.encode('cp950'), 'constant fingerprint mismatch')
        value = new_text.encode('cp950')
        require(len(value) <= len(old), 'new literal is too long')
        value = value.ljust(len(old), b' ')
        # This pinned literal must have one actual string definition in the raw
        # marshal stream. Any unexpected shared reference will fail the tree diff.
        require(plain.count(old) == 1, 'literal occurrence is ambiguous')
        start = plain.index(old)
        require(start > co_by_path[path]['offset'] + 22 + len(co_by_path[path]['code']),
                'literal does not belong to target constant pool')
        require(plain[start - 5] in (ord('s'), ord('t'))
                and struct.unpack_from('<I', plain, start - 4)[0] == len(old),
                'literal is not an inline marshal string')
        require(not any(start <= b < start + len(old) for b in metadata['bounds']),
                'constant spans an unverified XOR boundary')
        changed[start:start + len(old)] = value
        allowed.update(range(start, start + len(old)))
        changed_constants[(path, constant_index)] = value
        changes.append({'function': path, 'kind': 'constant', 'constant_index': constant_index,
                        'payload_offset': start, 'span_bytes': len(old),
                        'before_sha256': sha(old), 'after_sha256': sha(value)})

    if index == 337:
        co = co_by_path['CMainPage/OnMessage']
        # Replace only the TW predicate's load/attribute/call with False + NOPs.
        # The existing conditional at 111 pops False at 202 and opens register at 203.
        replace('CMainPage/OnMessage', 102,
                [(124, co['varnames'].index(b'misc')), (105, co['names'].index(b'IsTWServer')), (131, 0)],
                assemble((116, co['names'].index(b'False'))), length=9)
        require((111, 111, 88) in normalized(co['code']), 'unexpected registration branch target')
        require((202, 1, None) in normalized(co['code']), 'missing predicate pop at branch target')
    elif index == 4007:
        path = 'CRegPanel1/OnMessage'
        co = co_by_path[path]
        if stage == 'terms':
            # v1: Agree takes the existing reject/return-home branch.
            replace(path, 13, [(116, co['names'].index(b'Step')), (100, co['consts'].index(1)),
                              (131, 1), (1, None)], assemble((113, 184)), length=10)
        else:
            # v2: retain original Step(1), but return before old click telemetry.
            require(co['code'][13:23] == assemble((116, co['names'].index(b'Step')),
                    (100, co['consts'].index(1)), (131, 1), (1, None)), 'Step(1) fingerprint changed')
            require(co['code'][336:] == assemble((100, co['consts'].index(None)), (83, None)),
                    'terms return fingerprint changed')
            replace(path, 23, None, assemble((113, 336)), length=65)
        # The return-home branch skips old sound/login telemetry, retaining the existing
        # try/except return-to-home path at 259, with no stack/exception-block changes.
        require(co['code'][184:194] == assemble((116, co['names'].index(b'Show')),
                (116, co['names'].index(b'False')), (131, 1), (1, None)), 'return-home fingerprint changed')
        require((259, 121, 29) in normalized(co['code']), 'missing original exception handler')
        replace(path, 194, None, assemble((113, 259)), length=65)
        observed = {path for path, co in co_by_path.items()
                    if {b'CHttpObject', b'OpenUrl'} & set(co['names'])}
        require(observed == NETWORK_PATHS, 'registration network-call inventory changed')
        # Defense in depth: direct HTTP / external-browser methods return None.
        # Keep the entire code span the same length, filling unreachable bytes with NOP.
        for path in sorted(NETWORK_PATHS):
            co = co_by_path[path]
            if stage == 'form' and path == 'CRegPanel2/DoNext':
                # Local dialog only: no validation/submission, credential read,
                # device lookup, telemetry or success state is performed.
                body = assemble(
                    (100, co['consts'].index(-1)), (100, co['consts'].index(None)),
                    (107, co['names'].index(b'commondialog')),
                    (125, co['varnames'].index(b'commondialog')),
                    (124, co['varnames'].index(b'commondialog')),
                    (105, co['names'].index(b'ShowNewMessageBox')),
                    (100, 10), (100, co['consts'].index('確定'.encode('cp950'))),
                    (131, 2), (1, None), (100, co['consts'].index(None)), (83, None))
                replace(path, 0, None, body, length=len(co['code']))
                replace_constant(path, 10, '正在註冊，請等待...', '離線預覽，未送出。')
            else:
                replace(path, 0, None, assemble((100, co['consts'].index(None)), (83, None)),
                        length=len(co['code']))
        if stage == 'form':
            # Back retains Step(0), but Save() cannot retain typed credentials.
            # Disable the alternate old email-registration flow as well.
            for path in ('CRegPanel2/Save', 'Register2980'):
                co = co_by_path[path]
                replace(path, 0, None, assemble((100, co['consts'].index(None)), (83, None)),
                        length=len(co['code']))
            # The former 2980 link uses the same local preview notice as Next.
            path = 'CRegPanel2/OnMessage'
            co = co_by_path[path]
            require(co['code'][90:100] == assemble((124, co['varnames'].index(b'self')),
                    (105, co['names'].index(b'DoNext')), (131, 0), (1, None)),
                    'form preview callback fingerprint changed')
            replace(path, 117, None, assemble((113, 90)), length=75)
            replace_constant('CRegPanel2/__init__', 4, '點擊註冊2980郵箱', '離線預覽說明')
    else:
        raise ValueError('unexpected patch entry')

    output = bytes(changed)
    require(len(output) == len(plain), 'payload size changed')
    require(all(n in allowed for n, (a, b) in enumerate(zip(plain, output)) if a != b), 'out-of-scope byte changed')
    after = dict(objects(tree(output)))
    require(after.keys() == co_by_path.keys(), 'code-object inventory changed')
    patched_functions = {c['function'] for c in changes}
    for path, original in co_by_path.items():
        current = after[path]
        # Compare local metadata without recursively comparing child code bodies.
        for key in ('offset', 'argcount', 'nlocals', 'stacksize', 'flags', 'names', 'varnames',
                    'freevars', 'cellvars', 'filename', 'name', 'firstlineno', 'lnotab'):
            require(original[key] == current[key], f'{path}: metadata changed: {key}')
        require(len(original['consts']) == len(current['consts']), 'constant count changed')
        for constant_index, (before_value, after_value) in enumerate(zip(original['consts'], current['consts'])):
            if not isinstance(before_value, dict):
                expected = changed_constants.get((path, constant_index), before_value)
                require(expected == after_value, f'{path}: unexpected literal changed')
        if path in patched_functions:
            valid_code(current, current['code'])
        else:
            require(original['code'] == current['code'], f'{path}: unrelated code changed')
    return output, changes


def repack(archive, replacements):
    directory, rows = entries(archive)
    if not replacements:
        return archive
    result = bytearray(archive)
    new_directory = bytearray(archive[directory:])
    # Leave all original compressed payloads in place; append only replacements.
    for index, compressed in sorted(replacements.items()):
        eid, r1, _, _ = rows[index][0]
        r2 = ((r1 * eid + 0xDF25E) & 0xFFFFFFFF) ^ len(compressed)
        r3 = ((r2 * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ len(result)
        struct.pack_into('<IIII', new_directory, index * 16, eid, r1, r2, r3)
        result.extend(compressed)
    struct.pack_into('<I', result, 8, len(result))
    result.extend(new_directory)
    return bytes(result)


def build(archive, key_bytes, stage='terms'):
    require(stage in STAGES, 'unsupported preview stage')
    require(sha(archive) == BASE_SHA256, 'unsupported source script.fls; refusing to patch')
    require(sha(key_bytes) == KEYS_SHA256, 'unsupported key database; refusing to patch')
    metadata = json.loads(key_bytes)
    _, rows = entries(archive)
    require(len(rows) == 5002, 'unexpected entry count')
    require(repack(archive, {}) == archive, 'no-op repack failed')
    replacements = {}
    patch_reports = []
    for index in sorted(TARGET_ENTRIES):
        encrypted = zlib.decompress(rows[index][1])
        plain = xor_payload(encrypted, metadata[str(index)])
        require(xor_payload(plain, metadata[str(index)]) == encrypted, 'XOR identity round trip failed')
        patched, changes = patch_payload(index, plain, metadata[str(index)], stage=stage)
        new_encrypted = xor_payload(patched, metadata[str(index)])
        require(xor_payload(new_encrypted, metadata[str(index)]) == patched, 'patched XOR round trip failed')
        replacements[index] = zlib.compress(new_encrypted, 9)
        patch_reports.append({'entry_index': index, 'payload_size_unchanged': len(patched), 'changes': changes})
    result = repack(archive, replacements)
    _, new_rows = entries(result)
    require(len(new_rows) == len(rows), 'archive entry count changed')
    changed = [i for i, (old, new) in enumerate(zip(rows, new_rows)) if old != new]
    require(set(changed) == TARGET_ENTRIES, 'unexpected archive entries changed')
    for index in TARGET_ENTRIES:
        require(new_rows[index][1] == replacements[index], 'wrong stored replacement')
        tree(xor_payload(zlib.decompress(new_rows[index][1]), metadata[str(index)]))
    report = {'kind': 'registration_first_page_preview_only', 'source_sha256': sha(archive),
              'output_sha256': sha(result), 'source_bytes': len(archive), 'output_bytes': len(result),
              'key_database_sha256': sha(key_bytes), 'changed_entries': changed,
              'untouched_entries_byte_identical': len(rows) - len(changed),
              'original_xor_boundaries_preserved': True, 'no_op_repack_byte_identical': True,
              'recovered_code_executed': False, 'native_windows_client_tested': False,
              'patches': patch_reports,
              'limits': ['Only the original registration first page is enabled.',
                         'Agree and Reject both return home; original Close still exits the game.',
                         'Direct CHttpObject/OpenUrl callers in register.py are disabled.',
                         'Not a working account-registration service or a client-wide network block.',
                         'Unchanged original code/resources may have pre-existing defects.']}
    if stage == 'form':
        report['kind'] = 'registration_form_offline_preview_only'
        report['limits'] = [
            'Agree opens the old form; Reject returns home; form Back returns to terms.',
            'Next and the preview-info link only show a local offline-preview notice.',
            'No real registration, success simulation, credential persistence or validation on Next.',
            'Form Save and Register2980 are disabled; all direct registration HTTP/browser callers are blocked.',
            'Only two fixed-width CP950 UI literals were changed; old input constraints and artwork remain.',
            'Not a client-wide network block. No native Windows v2 test has been performed.']
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/script.fls')
    parser.add_argument('--keys', type=Path, default=ROOT / 'tools/decompiler/script_fls_keys.json')
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--stage', choices=STAGES, default='terms',
                        help='terms: reproducible v1; form: offline data-entry preview v2')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    require(not out.is_relative_to(ROOT), 'write test artifacts outside the repository')
    require(not (out / 'data/script.fls').exists(), 'output already exists; refusing overwrite')
    original = args.source.read_bytes()
    result, report = build(original, args.keys.read_bytes(), stage=args.stage)
    require(out / 'data/script.fls' != args.source.resolve(), 'cannot overwrite original')
    (out / 'data').mkdir(parents=True, exist_ok=True)
    (out / 'data/script.fls').write_bytes(result)
    (out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    require(args.source.read_bytes() == original, 'original file changed during build')
    print(json.dumps({k: v for k, v in report.items() if k != 'patches'}, indent=2))


if __name__ == '__main__':
    main()
