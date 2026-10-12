#!/usr/bin/env python3
"""Independently replay authored v3/v3.2 startup fragments with CPython 2.5.6.

Never execute a recovered game module. Only the authored overlay, the changed
startup hook, and click-only registration entry run, against fake UI/modules.
The target client's native engine/crypto/image loading are NOT tested here.
"""
import argparse
import copy
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile

import build_visual_preview as visual
base = visual.base
HERE = Path(__file__).resolve().parent


def canonical(co):
    result = copy.deepcopy(co)
    result['code'] = b''.join(bytes([op]) + (struct.pack('<H', arg) if op >= 90 else b'')
                              for _, op, arg in base.normalized(co['code']))
    result['consts'] = tuple(canonical(v) if isinstance(v, dict) and 'code' in v else v for v in co['consts'])
    return result


def fragment(template, code, name, consts=None):
    result = copy.deepcopy(template)
    result['code'] = code
    result['filename'] = ('authored-audit/' + name).encode('ascii')
    result['name'] = name.encode('ascii')
    result['lnotab'] = b''
    result['firstlineno'] = 1
    if consts is not None:
        result['consts'] = consts
    return canonical(result)


def extract(archive, keys, index):
    compressed = base.entries(archive)[1][index][1]
    return base.tree(base.xor_payload(base.zlib.decompress(compressed), keys[str(index)]))


def fixtures(source, key_bytes, shipped=None):
    keys = json.loads(key_bytes)
    candidate, report = visual.build(source, key_bytes)
    root = extract(candidate, keys, 4007)
    # Carry only the used original scalar operands and the AUTHORED overlay.
    constants = tuple(v if i in (0, 1, 41) else None for i, v in enumerate(root['consts']))
    none_idx = next(i for i, v in enumerate(root['consts']) if v is None)
    ret = base.assemble((100, none_idx), (83, None))
    good = fragment(root, root['code'][488:513] + ret, 'fixed-overlay-invocation', constants)
    if shipped is not None:
        old = extract(shipped, keys, 4007)
        bad_code = old['code'][488:513]
        base.require(old['consts'][0] == -1 and old['consts'][1] is None, 'unexpected shipped constants')
    else:
        bad_code = base.assemble((100, 41), (100, 0), (100, 0), (85, None))
    bad = fragment(root, bad_code + ret, 'shipped-bad-namespace-operands', constants)
    home = dict(base.objects(extract(candidate, keys, 337)))
    init = home['CMainPage/__init__']
    def inline_case(co, span, name):
        start, end = span
        seq = base.normalized(co['code'][start:end])
        code = base.assemble(*[(op, arg-start if op in visual.ABS_JUMPS else arg) for _, op, arg in seq])
        base.valid_code(co, code)
        return fragment(co, code, name)
    hook = inline_case(init, report['details']['homepage']['caption_span'], 'independent-homepage-caption')
    message = home['CMainPage/OnMessage']
    click = inline_case(message, report['details']['homepage']['click_span'], 'lazy-registration-click')
    return {'bad': bad, 'good': good, 'hook': hook, 'click': click}, candidate, report


def run(python25, shipped_zip=None):
    source = (base.ROOT / 'data/script.fls').read_bytes()
    keys = (base.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes()
    shipped = None
    if shipped_zip:
        with zipfile.ZipFile(shipped_zip) as z:
            shipped = z.read('data/script.fls')
        base.require(base.sha(shipped) == 'b26af0973ac1fb28f0d2b482e2d24a710d682e4ff51b2ec1a586c219a75cc4a2',
                     'audit requires the actually shipped v3 archive')
    cases, candidate, report = fixtures(source, keys, shipped)
    with tempfile.TemporaryDirectory(prefix='visual-runtime-') as directory:
        for name, co in cases.items():
            Path(directory, name + '.marshal').write_bytes(visual.Writer().write(co))
        # Independently deserialize the COMPLETE artifact, but never execute it.
        plain = base.xor_payload(base.zlib.decompress(base.entries(candidate)[1][4007][1]), json.loads(keys)['4007'])
        Path(directory, 'parse-only.marshal').write_bytes(plain)
        home_plain = base.xor_payload(base.zlib.decompress(base.entries(candidate)[1][337][1]), json.loads(keys)['337'])
        Path(directory, 'parse-home-only.marshal').write_bytes(home_plain)
        proc = subprocess.run([python25, '-S', str(HERE / 'visual_runtime_harness.py2'), directory],
                              text=True, capture_output=True, timeout=30)
        base.require(proc.returncode == 0, 'CPython 2.5 audit failed:\n' + proc.stdout + proc.stderr)
    return {'python25_runtime_output': proc.stdout.splitlines(),
            'candidate_fls_sha256': base.sha(candidate), 'candidate_fls_bytes': len(candidate),
            'shipped_v3_fls_sha256': base.sha(shipped) if shipped is not None else None,
            'native_windows_client_tested': False,
            'scope': 'authored compiled startup/UI code and modified call fragments only; fake engine boundaries',
            'candidate_kind': report['kind']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--python25', required=True)
    parser.add_argument('--shipped-zip', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = run(args.python25, args.shipped_zip)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text)


if __name__ == '__main__':
    main()
