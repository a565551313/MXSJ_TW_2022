#!/usr/bin/env python3
"""Agent F probe 58 - entry 244: exhaustive two-key split scan of the
119-byte desc of DATA[29760] (dec 73070..73189).  Read-only."""
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
END = P + L

print('--- for every split X, keys that make [P,X) and [X,END) valid CP950 ---')
for X in range(P, END + 1):
    left = []
    for k in range(256):
        try:
            t = dec[P:X].translate(decoder.XTABS[k]).decode('cp950')
            left.append((k, t))
        except UnicodeDecodeError:
            pass
    right = []
    for k in range(256):
        try:
            t = dec[X:END].translate(decoder.XTABS[k]).decode('cp950')
            right.append((k, t))
        except UnicodeDecodeError:
            pass
    if left and right:
        for k1, t1 in left:
            for k2, t2 in right:
                # keep only combinations that look like Chinese prose
                cjk = sum(1 for c in t1 + t2 if '\u4e00' <= c <= '\u9fff')
                if cjk >= 15:
                    print('  X=%d (split %d bytes in) k1=%3d k2=%3d -> %r | %r'
                          % (X, X - P, k1, k2, t1, t2))
