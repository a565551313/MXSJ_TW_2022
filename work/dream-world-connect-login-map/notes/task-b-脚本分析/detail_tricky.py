#!/usr/bin/env python3
"""Detailed window analysis with counts for tricky entries."""
import struct, zlib, sys
from collections import Counter
sys.path.insert(0, 'work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import decode_directory, u32

arch = open('data/script.fls','rb').read()
count = u32(arch,4); idxoff = u32(arch,8)

def get_expanded(i):
    raw_offset = idxoff + i*16
    raw = struct.unpack_from("<IIII", arch, raw_offset)
    f1,f2,f3 = decode_directory(i, raw)
    comp = arch[f3:f3+f2]
    exp = zlib.decompress(comp)
    return raw,(f1,f2,f3),comp,exp

def detail(i, w=128):
    raw,dec,comp,exp = get_expanded(i)
    n = len(exp)
    print(f"\n=== entry {i} len={n} f1=0x{dec[0]:x} est_seg={n/5:.1f} ===")
    for start in range(0, n, w):
        chunk = exp[start:start+w]
        c = Counter(chunk)
        top = c.most_common(4)
        topstr = ' '.join(f"{b:02x}:{cnt}" for b,cnt in top)
        print(f"  0x{start:05x}: {topstr}")

detail(400)
detail(500)
detail(5)
detail(0, w=32)
detail(3300, w=32)
detail(3500, w=32)
