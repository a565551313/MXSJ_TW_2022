#!/usr/bin/env python3
"""Agent F probe 52 - entry 244: locate DATA record 29760's failing desc.

Read-only.  Finds the payload offset of the failing string, shows the
surrounding bytes under every XOR key, and dumps the whole record.
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


ENTRY = 244
m = keys[str(ENTRY)]
exp = payload(ENTRY)
ks = m['keys']
BOUNDS = [18282, 36511, 54797, 73070]
KEYLIST = [233, 11, 132, 105, 246]
edges = [0] + BOUNDS + [len(exp)]
dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[KEYLIST[i]]) for i in range(5))

# locate the failing string inside the decoded payload
needle = bytes.fromhex(
    '3a4a2732295f357e3ede5dfe5dfe5bf85bf83b38293e2ce525e32a445c672ef03bdf373c35252'
    'dd729312dd2b773b74ec4ad2372a169c3feabaca16aae78b07cb8cbb9a2a147b4bac65bb4d3aa'
    'ab2372a169aaabab7eb5a5afc5a16a312372a169bb73a740bbdda844a16a3730afc5a5a9a64ba4a7b34e')
pos = dec.find(needle)
print('failing desc found in decoded payload at dec offset', pos, 'len', len(needle))
print('segment index:', sum(1 for b in BOUNDS if b <= pos))
# find its marshal record: search backwards for the 's' tag + length
i = pos - 5
print('bytes before string: %r  (tag %r len %d)' % (dec[pos-5:pos], chr(dec[pos-5]),
      struct.unpack_from('<I', dec, pos-4)[0]))

def which(k):
    seg = 0
    for b in BOUNDS:
        if k >= b:
            seg += 1
    return seg

print()
print('--- decoded payload window [pos-16, pos+len+16] as hex ---')
w = dec[max(0, pos-16):pos+len(needle)+16]
print(w.hex())
print()
print('--- same window under every key (only bytes whose segment matches) ---')
for k in range(256):
    seg = which(pos)
    raw = dec[pos-16:pos+len(needle)+16].translate(decoder.XTABS[k])
    try:
        t = raw[16:16+len(needle)].decode('cp950')
    except UnicodeDecodeError:
        continue
    print('  key %3d -> %r' % (k, t[:200]))

print()
print('--- raw (still-encrypted) bytes of the same window ---')
start = pos - 16
end = pos + len(needle) + 16
print('  payload[%d:%d] = %s' % (start, end, exp[start:end].hex()))

print()
print('--- strict CP950 decode attempts of the raw needle with single-byte corrections ---')
bad_at = []
try:
    needle.decode('cp950')
except UnicodeDecodeError as e:
    print('first failure: start=%s end=%s reason=%s' % (e.start, e.end, e.reason))
    bad_at = [e.start]
