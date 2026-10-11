#!/usr/bin/env python3
"""Agent F probe 64 - entry 244: scan boundary 3 (keys 105 / 246) and report the
number of valid CP950 strings plus the reading of DATA[29760].desc.
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
    end = w(0)
    return end == len(dec), out


def cjk(t):
    return sum(1 for c in t if '\u4e00' <= c <= '\u9fff')


best = []
for B3 in range(73000, 73300):
    B = [18282, 36511, 54797, B3]
    K = [233, 11, 132, 105, 246]
    dec = build(B, K)
    try:
        ok, strs = strings_of(dec)
    except Exception:
        continue
    if not ok:
        continue
    good = bad = 0
    desc = None
    for off, ln, s in strs:
        if ln < 4:
            continue
        if off == 73070:
            try:
                desc = s.decode('cp950')
            except UnicodeDecodeError:
                desc = None
        try:
            t = s.decode('cp950')
            if cjk(t) >= 2:
                good += 1
            else:
                bad += 1
        except UnicodeDecodeError:
            bad += 1
    best.append((good, B3, bad, desc))
best.sort(reverse=True)
for good, B3, bad, desc in best[:12]:
    print('cjk_good=%d B3=%d bad=%d' % (good, B3, bad))
    if desc:
        print('     DATA[29760].desc = %r' % desc)
print()
print('--- saved B3=73070 for reference ---')
for good, B3, bad, desc in best:
    if B3 == 73070:
        print('cjk_good=%d B3=%d bad=%d desc=%r' % (good, B3, bad, desc))
