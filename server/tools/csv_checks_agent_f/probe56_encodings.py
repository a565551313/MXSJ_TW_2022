#!/usr/bin/env python3
"""Agent F probe 56 - entry 244: characterise the 45 corrupt leading bytes of
DATA[29760].desc.  Read-only; tries alternative start offsets and codecs."""
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
P = 73070
L = 119
raw = dec[P:P + L]
print('raw string len %d' % len(raw))
print('garbage part (%d bytes): %s' % (45, raw[:45].hex()))
print('valid tail: %r' % raw[45:].decode('cp950'))
print()
print('--- alternative start offsets (same length window) ---')
for off in (-3, -2, -1, 0, 1, 2, 3):
    s = dec[P + off:P + off + L]
    try:
        print('  start %+d -> %r' % (off, s.decode('cp950')))
    except UnicodeDecodeError as e:
        print('  start %+d -> CP950 fail at %d' % (off, e.start))
print()
print('--- codecs on the 45 garbage bytes ---')
for codec in ('cp950', 'big5', 'gbk', 'gb18030', 'utf-8', 'utf-16-le', 'utf-16-be',
              'shift_jis', 'euc_jp', 'euc_kr', 'latin-1'):
    try:
        t = raw[:45].decode(codec)
        print('  %-10s -> %r' % (codec, t))
    except UnicodeDecodeError as e:
        print('  %-10s -> fail at %d (%s)' % (codec, e.start, e.reason))
print()
print('--- codecs on the whole 119-byte string ---')
for codec in ('cp950', 'big5', 'gbk', 'gb18030', 'utf-8', 'utf-16-le'):
    try:
        t = raw.decode(codec)
        print('  %-10s -> %r' % (codec, t))
    except UnicodeDecodeError as e:
        print('  %-10s -> fail at %d' % (codec, e.start))
print()
print('--- byte histogram of the garbage ---')
from collections import Counter
c = Counter(raw[:45])
print(sorted(c.items()))
print()
print('--- is the garbage region XOR of plausible CP950 text with a fixed byte? ---')
# neighbour 29761 desc for reference
ref = dec[73210:73210 + 119]
print('neighbour desc len %d: %r' % (len(ref), ref.decode('cp950')))
print('neighbour hex head: %s' % ref[:45].hex())
