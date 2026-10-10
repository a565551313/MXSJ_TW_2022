#!/usr/bin/env python3
"""Detect XOR segment structure by analyzing raw expanded bytes."""
import struct, zlib, sys
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

def show_runs(i, window=64):
    raw,dec,comp,exp = get_expanded(i)
    n = len(exp)
    print(f"\n=== entry {i} len={n} ===")
    # Print histogram of byte values in sliding windows to detect key changes
    # For each 256-byte block, show most common byte and count
    bs = 256
    for start in range(0, n, bs):
        chunk = exp[start:start+bs]
        from collections import Counter
        c = Counter(chunk)
        top = c.most_common(5)
        topstr = ' '.join(f"{b:02x}:{cnt}" for b,cnt in top)
        print(f"  0x{start:05x}-0x{min(start+bs,n):05x}: {topstr}")
    # Also dump first 64 and around 1/5 boundaries
    for frac in [0, 0.2, 0.4, 0.6, 0.8]:
        pos = int(n*frac)
        lo = max(0,pos-8); hi=min(n,pos+24)
        print(f"  frac {frac}: pos {pos} (0x{pos:x}): {exp[lo:hi].hex(' ')}")

for i in [0, 1, 516, 517, 100]:
    show_runs(i)
