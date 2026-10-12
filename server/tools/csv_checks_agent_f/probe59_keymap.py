#!/usr/bin/env python3
"""Agent F probe 59 - entry 244: sliding-window XOR key map over the whole
payload, using strict CP950 validity of the window as the signal.

Read-only.  A window is "clean" when every byte pair in it forms a valid CP950
character (a trailing single lead byte is tolerated).
"""
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
W = 240
STEP = 48
LO, HI = 47000, len(exp)
rows = []
p = LO
while p < HI:
    win = exp[p:p + W]
    good = []
    for k in range(256):
        t = win.translate(decoder.XTABS[k])
        try:
            t.decode('cp950')
            good.append(k)
        except UnicodeDecodeError:
            # tolerate a trailing lead byte
            if len(t) > 1:
                try:
                    t[:-1].decode('cp950')
                    good.append(k)
                except UnicodeDecodeError:
                    pass
    rows.append((p, good))
    p += STEP
# print a compact map: for each window list the keys
prev = None
for p, good in rows:
    tag = ''
    print('%7d  %s' % (p, ','.join(str(g) for g in good[:12]) + (' ...' if len(good) > 12 else '')))
