#!/usr/bin/env python3
"""Agent F probe 67 - recap of entries 2566 and 1919.

Re-derives, read-only, the exact payload offsets of the anomalous string
constants under the SAVED and the CORRECTED XOR segmentation, so the report can
quote byte-exact evidence.
"""
import sys, json, zlib, struct
from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder
from tools.fls_batch_decoder import MarshalReader

keys = json.loads((ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes())
arch = (ROOT / 'data/script.fls').read_bytes()
idx_off = struct.unpack_from('<I', arch, 8)[0]


def payload(index):
    entry_id, a, b, c = struct.unpack_from('<IIII', arch, idx_off + 16 * index)
    size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
    pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
    return zlib.decompress(arch[pos:pos + size])


sys.path.insert(0, str(ROOT / 'server/tools'))
from review_client_data_boundaries import instructions, evaluate_literals


def load(exp, B, K):
    edges = [0] + list(B) + [len(exp)]
    dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))
    tr = decoder.Py25MarshalTranspiler(dec, exp, K, list(B))
    tr.transpile_object()
    r = MarshalReader(bytes(tr.out)[8:]); co = r.read()
    if r.pos != len(r.data):
        raise ValueError('reader did not consume output')
    return co, dec


def extract(co, name):
    seg = []
    for at, op, arg in instructions(co):
        seg.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == name.encode('ascii'):
                return evaluate_literals(co, seg[:-1] + [(at, 90, arg)])
            seg = []
    raise ValueError('no ' + name)


def strings_of(dec):
    out = []

    def w(p):
        t = dec[p]; p += 1; tc = chr(t)
        if tc in ('0', 'N', 'F', 'T', 'S', '.'):
            return p
        if tc in ('i', 'I', 'g', 'R'):
            return p + (8 if tc in ('I', 'g') else 4)
        if tc == 'l':
            n = abs(struct.unpack_from('<i', dec, p)[0]); return p + 4 + n * 2
        if tc in ('s', 't', 'u'):
            ln = struct.unpack_from('<I', dec, p)[0]
            out.append((p + 4, ln, dec[p + 4:p + 4 + ln])); return p + 4 + ln
        if tc in ('f', 'x'):
            ln = dec[p]; return p + 1 + ln
        if tc in ('(', '[', '<', '>'):
            n = struct.unpack_from('<I', dec, p)[0]; p += 4
            for _ in range(n):
                p = w(p)
            return p
        if tc == '{':
            while dec[p] != ord('0'):
                p = w(p); p = w(p)
            return p + 1
        if tc == 'c':
            p += 16
            clen = struct.unpack_from('<I', dec, p + 1)[0]
            p = p + 5 + clen
            for _ in range(5):
                p = w(p)
            p = w(p); p = w(p); p += 4; p = w(p)
            return p
        raise ValueError('tag %r at %d' % (tc, p - 1))
    w(0)
    return out


def report(index, table, rows, saved_b, saved_k, corr_b, corr_k, targets):
    m = keys[str(index)]
    exp = payload(index)
    print('=== entry %d  payload=%d  sha256(payload)=%s'
          % (index, len(exp), __import__('hashlib').sha256(exp).hexdigest()))
    print('    filename: ', end='')
    co, dec = load(exp, saved_b, saved_k)
    print(co['filename'])
    print('    saved   bounds=%s keys=%s' % (saved_b, saved_k))
    print('    corr    bounds=%s keys=%s' % (corr_b, corr_k))
    for label, B, K in (('SAVED', saved_b, saved_k), ('CORRECTED', corr_b, corr_k)):
        co, dec = load(exp, B, K)
        strs = strings_of(dec)
        bad = []
        for off, ln, s in strs:
            if ln < 2:
                continue
            try:
                t = s.decode('cp950')
                if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t):
                    bad.append((off, ln, 'control-bytes'))
            except UnicodeDecodeError as e:
                bad.append((off, ln, 'cp950@%d' % e.start))
        print('    %s: %d strings, %d fail strict CP950: %s'
              % (label, len(strs), len(bad), bad[:6]))
    co, dec = load(exp, corr_b, corr_k)
    for name, rk in targets:
        v = extract(co, name)
        if rk is None:
            continue
        if isinstance(v, dict) and rk in v:
            val = v[rk]
            s = val if isinstance(val, (bytes, bytearray)) else (val[0] if isinstance(val, tuple) else val)
            # locate in payload
            off = None
            if isinstance(s, (bytes, bytearray)):
                off = dec.find(bytes(s))
            print('    %s[%s] = %r' % (name, rk, s))
            if off is not None and off >= 0:
                print('        decoded-payload offset %d, len %d, segment %d'
                      % (off, len(s), sum(1 for b in corr_b if b <= off)))


report(2566, 'DATA', None, [30130, 60297, 90430, 120649], [196, 147, 166, 249, 248],
       [30130, 60263, 90409, 120551], [196, 147, 166, 249, 248],
       [('DATA', 336), ('DATA', 877)])
print()
report(1919, 'PREVIEWDATA', None, [1907, 3840, 5925, 7698], [89, 39, 126, 150, 135],
       [1907, 3840, 5756, 7613], [89, 39, 126, 150, 135],
       [('CHANGESHAPE_PREVIEWDATA', 24), ('CHANGESHAPE_PREVIEWDATA', 34)])
