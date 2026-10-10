#!/usr/bin/env python3
"""Profile per-window most-common byte (estimated XOR key) for many entries."""
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

def profile(i, w=128):
    raw,dec,comp,exp = get_expanded(i)
    n = len(exp)
    segs = []
    for start in range(0, n, w):
        chunk = exp[start:start+w]
        c = Counter(chunk)
        (b,cnt) = c.most_common(1)[0]
        segs.append(f"{b:02x}:{cnt}")
    # compress consecutive same-key windows
    runs = []
    for j,s in enumerate(segs):
        k = s.split(':')[0]
        if runs and runs[-1][0]==k:
            runs[-1][1]+=1
        else:
            runs.append([k,1,j*w])
    runstr = ' '.join(f"{k}x{n}@0x{off:x}" for k,n,off in runs)
    print(f"entry {i:4d} len={n:6d} f1=0x{dec[0]:08x} k0=0x{exp[0]^0x63:02x} runs: {runstr}")

# diverse sample
for i in [0,1,2,3,4,5,10,50,100,200,300,400,500,516,517,518,600,800,1000,1500,1600,1700,2000,2500,3000,3300,3400,3500,4000,4500,4800,4900,4999,5000,5001]:
    profile(i)

# f1 distribution
print("\n--- f1 distribution sample (every 50) ---")
from collections import Counter as C
f1c = C()
for i in range(0,5002,50):
    raw,dec,comp,exp = get_expanded(i)
    f1c[dec[0]] += 1
for k,v in sorted(f1c.items()):
    print(f"  f1=0x{k:08x} ({k}): {v}")
