#!/usr/bin/env python3
"""Agent F probe 57 - entry 244: exhaustive single-key scan of the 45 corrupt
leading bytes of DATA[29760].desc, plus a control run on a healthy string.
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
B = [18282, 36511, 54797, 73070]
K = [233, 11, 132, 105, 246]
edges = [0] + B + [len(exp)]
dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))
P, L = 73070, 119

print('--- control: healthy neighbour desc at 73210, first 45 bytes, all keys ---')
ctrl = dec[73210:73210 + 45]
hits = []
for k in range(256):
    try:
        t = ctrl.translate(decoder.XTABS[k]).decode('cp950')
        hits.append((k, t))
    except UnicodeDecodeError:
        pass
print('   keys giving valid CP950:', [h[0] for h in hits])
for k, t in hits:
    print('   key %3d -> %r' % (k, t))

print()
print('--- the 45 corrupt bytes of DATA[29760].desc, all keys ---')
bad = dec[P:P + 45]
hits = []
for k in range(256):
    try:
        t = bad.translate(decoder.XTABS[k]).decode('cp950')
        hits.append((k, t))
    except UnicodeDecodeError:
        pass
print('   keys giving valid CP950:', [h[0] for h in hits])
for k, t in hits:
    print('   key %3d -> %r' % (k, t))

print()
print('--- two-key scan over the corrupt region: split at X, keys (k1,k2) ---')
found = []
for X in range(P + 1, P + 45):
    a_region = dec[P:X]
    b_region = dec[X:P + 119]
    for k1 in range(256):
        try:
            t1 = a_region.translate(decoder.XTABS[k1]).decode('cp950')
        except UnicodeDecodeError:
            continue
        for k2 in range(256):
            try:
                t2 = b_region.translate(decoder.XTABS[k2]).decode('cp950')
            except UnicodeDecodeError:
                continue
            found.append((X, k1, k2, t1, t2))
            if len(found) > 40:
                break
        if len(found) > 40:
            break
    if len(found) > 40:
        break
print('   two-key solutions found:', len(found))
for X, k1, k2, t1, t2 in found[:10]:
    print('   X=%d k1=%d k2=%d -> %r | %r' % (X, k1, k2, t1, t2[:60]))
