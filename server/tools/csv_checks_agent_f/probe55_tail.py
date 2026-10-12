#!/usr/bin/env python3
"""Agent F probe 55 - entry 244: decode the tail of record 29760's desc and the
neighbouring marshal strings to characterise the anomaly.  Read-only."""
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

needle = bytes.fromhex(
    '3a4a2732295f357e3ede5dfe5dfe5bf85bf83b38293e2ce525e32a445c672ef03bdf373c35252'
    'dd729312dd2b773b74ec4ad2372a169c3feabaca16aae78b07cb8cbb9a2a147b4bac65bb4d3aa'
    'ab2372a169aaabab7eb5a5afc5a16a312372a169bb73a740bbdda844a16a3730afc5a5a9a64ba4a7b34e')
P = dec.find(needle)
print('desc[29760] at dec %d..%d' % (P, P + len(needle)))
print('first 45 bytes (garbage): %s' % needle[:45].hex())
print('tail from offset 45:')
tail = needle[45:]
try:
    print('   %r' % tail.decode('cp950'))
except UnicodeDecodeError as e:
    print('   still fails at %d: %s' % (e.start, e.reason))
    print('   %r' % tail[:e.start].decode('cp950'))
    print('   bad byte 0x%02x' % tail[e.start])

print()
print('--- marshal strings immediately around the anomaly ---')
for off in range(P - 40, P + len(needle) + 40):
    pass
# re-walk to list strings with offsets near P
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
        out.append((p - 1, p + 4, ln, dec[p + 4:p + 4 + ln])); return p + 4 + ln
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
for tag, dataoff, ln, s in out:
    if P - 80 <= dataoff <= P + len(needle) + 80:
        try:
            t = s.decode('cp950')
            print('  tag@%d data@%d len=%d -> %r' % (tag, dataoff, ln, t))
        except UnicodeDecodeError:
            print('  tag@%d data@%d len=%d -> !!CP950-FAIL!! %s' % (tag, dataoff, ln, s.hex()))
