#!/usr/bin/env python3
"""Test: are XOR boundaries at clen/5 multiples in COMPRESSED domain?"""
import struct, zlib, sys
sys.path.insert(0, 'work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import decode_directory, u32, XOR_SEGMENTS

arch = open('data/script.fls','rb').read()
count = u32(arch,4); idxoff = u32(arch,8)

def get_entry(i):
    raw_offset = idxoff + i*16
    raw = struct.unpack_from("<IIII", arch, raw_offset)
    f1,f2,f3 = decode_directory(i, raw)
    comp = arch[f3:f3+f2]
    exp = zlib.decompress(comp)
    return raw,(f1,f2,f3),comp,exp

# For entry 516, map compressed offsets -> expanded offsets by incremental decompress
raw,dec,comp,exp = get_entry(516)
clen = len(comp); elen = len(exp)
print(f"516: clen={clen} elen={elen}")
print(f"true expanded boundaries: {[s for s,e,k in XOR_SEGMENTS]} + end {XOR_SEGMENTS[-1][1]}")

# incremental: feed byte by byte (slow but one-time), record out len at each in-pos
d = zlib.decompressobj()
outlen_at = []
out = 0
for pos in range(clen):
    chunk = d.decompress(comp[pos:pos+1])
    out += len(chunk)
    outlen_at.append(out)
out += len(d.flush())

for i in range(1,5):
    cpos = (clen*i)//5
    epos = outlen_at[cpos]
    trueb = XOR_SEGMENTS[i][0]
    print(f"  seg{i} start: compressed {cpos} (clen*{i}//5) -> expanded {epos}, true={trueb}, diff={epos-trueb}")

# also try round-half variants
print("\nwith (clen*i+2)//5 :")
for i in range(1,5):
    cpos = (clen*i+2)//5
    print(f"  seg{i}: cpos {cpos} -> expanded {outlen_at[cpos]}, true={XOR_SEGMENTS[i][0]}")
