#!/usr/bin/env python3
"""Debug entry 100 (len 1258) failure."""
import sys
sys.path.insert(0, 'tools')
sys.path.insert(0, 'work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import decode_directory, u32
from fls_batch_decoder import estimate_keys, mode_byte, _xtab, marshal_progress, marshal_try, _build_full
import struct, zlib
from collections import Counter

arch = open('data/script.fls','rb').read()
raw = struct.unpack_from("<IIII", arch, u32(arch,8)+100*16)
f1,f2,f3 = decode_directory(100, raw)
exp = zlib.decompress(arch[f3:f3+f2])
n = len(exp)
print(f"n={n} est={[(n*i)//5 for i in range(1,5)]}")
kc = estimate_keys(exp)
for s,c in enumerate(kc):
    print(f"seg{s} key cands: {[(hex(b),cnt) for b,cnt in c]}")

# fine-grained mode profile w=32
print("\nmode profile w=64:")
for start in range(0, n, 64):
    c = Counter(exp[start:start+64])
    print(f"  0x{start:04x}: {' '.join(f'{b:02x}:{cnt}' for b,cnt in c.most_common(3))}")

# 256-key search per segment by region zeros (using est regions)
print("\n256-key search (region zeros, est regions):")
for s in range(5):
    lo=(n*s)//5; hi=(n*(s+1))//5
    if s==0:
        print(f"  seg{s} [{lo},{hi}): exact {exp[0]^0x63:#04x}")
        continue
    tab_scores=[]
    for k in range(256):
        t=_xtab(k)
        z=exp[lo:hi].translate(t).count(0)
        tab_scores.append((z,k))
    tab_scores.sort(reverse=True)
    print(f"  seg{s} [{lo},{hi}): top5={[(hex(k),z) for z,k in tab_scores[:5]]}")
