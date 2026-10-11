#!/usr/bin/env python3
"""Agent F probe 63 - entry 244: test alternative boundary-3 / key-3 / key-4
combinations, scoring by how many marshal strings decode to valid CP950 text.
Read-only."""
import sys, json, zlib, struct
from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder

keys = json.loads((ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes())
arch = (ROOT / 'data/script.fls').read_bytes()
idx_off = struct.unpack_from('<I', arch, 8)[0]


def payload(index):
    entry_id, a, b, c = struct.unpack_from('<IIII', arch, idx_off + 16 * index)
    size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
    pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
    return zlib.decompress(arch[pos:pos + size])


exp = payload(244)


def build(B, K):
    edges = [0] + list(B) + [len(exp)]
    return b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))


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
    try:
        end = w(0)
    except Exception as e:
        return None, str(e)
    return (end == len(dec), out), 'ok'


def cjk(t):
    return sum(1 for c in t if '\u4e00' <= c <= '\u9fff')


def score(B, K):
    dec = build(B, K)
    res, err = strings_of(dec)
    if res is None:
        return 'WALK FAIL %s' % err
    ok, strs = res
    good = bad = 0
    for off, ln, s in strs:
        if ln < 4:
            continue
        try:
            t = s.decode('cp950')
        except UnicodeDecodeError:
            bad += 1
            continue
        if cjk(t) >= 2:
            good += 1
        else:
            bad += 1
    return 'walk_ok=%s strings=%d cjk_good=%d bad=%d' % (ok, len(strs), good, bad)


cands = [
    ('saved B3=73070 k3=105 k4=246', [18282, 36511, 54797, 73070], [233, 11, 132, 105, 246]),
    ('B3=73114 k3=159 k4=246', [18282, 36511, 54797, 73114], [233, 11, 132, 159, 246]),
    ('B3=73114 k3=105 k4=246', [18282, 36511, 54797, 73114], [233, 11, 132, 105, 246]),
    ('B3=73070 k3=159 k4=246', [18282, 36511, 54797, 73070], [233, 11, 132, 159, 246]),
    ('B3=73114 k3=105 k4=159', [18282, 36511, 54797, 73114], [233, 11, 132, 105, 159]),
    ('B3=73114 k3=105 k4=105', [18282, 36511, 54797, 73114], [233, 11, 132, 105, 105]),
    ('B3=73114 k3=105 k4=0', [18282, 36511, 54797, 73114], [233, 11, 132, 105, 0]),
]
for label, B, K in cands:
    print('%-32s %s' % (label, score(B, K)))
