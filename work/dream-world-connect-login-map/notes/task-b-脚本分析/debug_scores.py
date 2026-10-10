#!/usr/bin/env python3
"""Debug zero-score landscape around TRUE boundaries of entry 516."""
import sys
sys.path.insert(0, 'tools')
sys.path.insert(0, 'work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import decode_directory, u32, XOR_SEGMENTS
from fls_batch_decoder import zero_score, decode_with, marshal_try
import struct, zlib

arch = open('data/script.fls','rb').read()
idxoff = u32(arch,8)
raw = struct.unpack_from("<IIII", arch, idxoff+516*16)
f1,f2,f3 = decode_directory(516, raw)
exp = zlib.decompress(arch[f3:f3+f2])
n = len(exp)
true_keys = bytes([0xB1,0x44,0x30,0x41,0x20])
true_bounds = [3460,6989,10485,13948]
print(f"n={n} est={[(n*i)//5 for i in range(1,5)]} true={true_bounds}")

for i in range(4):
    tb = true_bounds[i]
    kL, kR = true_keys[i], true_keys[i+1]
    print(f"\n--- boundary {i} true={tb} kL=0x{kL:02x} kR=0x{kR:02x} ---")
    print(f"  raw[{tb-2}:{tb+3}] = {exp[tb-2:tb+3].hex(' ')}")
    # decoded with true keys around boundary
    dec = decode_with(exp, true_bounds, true_keys)
    print(f"  dec[{tb-4}:{tb+6}] = {dec[tb-4:tb+6].hex(' ')}")
    for W in (96, 256):
        scores = [(zero_score(exp, b, kL, kR, W), b) for b in range(tb-250, tb+251)]
        scores.sort(reverse=True)
        tru = zero_score(exp, tb, kL, kR, W)
        rank = sum(1 for s,_ in scores if s > tru) + 1
        top5 = scores[:5]
        print(f"  W={W}: true_score={tru} rank={rank}/{len(scores)} top5={[(b,s) for s,b in top5]}")
        # best's distance to true
        print(f"       best b={top5[0][1]} (dist {top5[0][1]-tb}), true rank details: {[ (b,s) for s,b in scores if abs(b-tb)<=6 ]}")
