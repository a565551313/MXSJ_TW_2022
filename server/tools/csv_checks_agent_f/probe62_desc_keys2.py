#!/usr/bin/env python3
"""Agent F probe 62 - entry 244: for every marshal string that decodes to real
Chinese text under the current segment key, list the other keys that also give
Chinese text.  Read-only."""
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
B = [18282, 36511, 54797, 73070]
K = [233, 11, 132, 105, 246]
edges = [0] + B + [len(exp)]
dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))
strings = []


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
        strings.append((p + 4, ln, dec[p + 4:p + 4 + ln])); return p + 4 + ln
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


def cjk(t):
    return sum(1 for c in t if '\u4e00' <= c <= '\u9fff')


bad = []
for off, ln, s in strings:
    if ln < 8:
        continue
    seg = sum(1 for b in B if b <= off)
    segkey = K[seg]
    try:
        base = s.translate(decoder.XTABS[segkey]).decode('cp950')
    except UnicodeDecodeError:
        bad.append((off, ln, seg, segkey, s))
        continue
    if cjk(base) < 4:
        continue
    others = []
    for k in range(256):
        if k == segkey:
            continue
        try:
            t = s.translate(decoder.XTABS[k]).decode('cp950')
        except UnicodeDecodeError:
            continue
        if cjk(t) >= 4:
            others.append((k, t))
    if others:
        print('off=%7d seg=%d segkey=%3d len=%3d base=%r' % (off, seg, segkey, ln, base[:50]))
        for k, t in others:
            print('        ALSO key %3d -> %r' % (k, t[:70]))
print()
print('strings that FAIL under their own segment key: %d' % len(bad))
for off, ln, seg, segkey, s in bad:
    print('  off=%7d seg=%d segkey=%3d len=%3d hex=%s' % (off, seg, segkey, ln, s.hex()))
