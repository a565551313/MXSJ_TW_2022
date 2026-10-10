#!/usr/bin/env python3
"""Task B step 0: explore FLS entries to understand XOR generalization."""
import struct, zlib, sys
sys.path.insert(0, 'work/dream-world-connect-login-map/notes/decoder-artifacts')
from decode_entry516 import decode_directory, u32, XOR_SEGMENTS

arch = open('data/script.fls','rb').read()
count = u32(arch,4)
idxoff = u32(arch,8)
print(f"count={count} idxoff={hex(idxoff)}")

def get_expanded(i):
    raw_offset = idxoff + i*16
    raw = struct.unpack_from("<IIII", arch, raw_offset)
    f1,f2,f3 = decode_directory(i, raw)
    comp = arch[f3:f3+f2]
    exp = zlib.decompress(comp)
    return raw,(f1,f2,f3),comp,exp

# sample entries: 0,1,2,516,517,100,1000,2000,4000,5001
for i in [0,1,2,3,4,5,10,100,500,516,517,518,1000,2000,3000,4000,4999,5000,5001]:
    raw,dec,comp,exp = get_expanded(i)
    print(f"--- entry {i}: id=0x{raw[0]:08x} f1=0x{dec[0]:08x} clen={dec[1]} off=0x{dec[2]:x} explen={len(exp)} comphead={comp[:4].hex()} exphead={exp[:16].hex()} exptail={exp[-8:].hex() if len(exp)>=8 else ''}")

# check entry 516 XOR hypothesis: exp[0] ^ 0x63 should be 0xB1
raw,dec,comp,exp = get_expanded(516)
print(f"\n516 exp[0]=0x{exp[0]:02x} ^0x63 = 0x{exp[0]^0x63:02x} (expect 0xB1)")
# check boundaries: bytes around 0x0D84
for off in [0x0D83,0x0D84,0x0D85,0x1B4C,0x1B4D,0x1B4E,0x28F4,0x28F5,0x28F6,0x367B,0x367C,0x367D,0x4350,0x4351]:
    print(f"  off 0x{off:04x}: raw 0x{exp[off]:02x}")

# For other entries, try assuming first key = exp[0]^0x63 and see distribution
print("\n--- first-byte XOR key hypothesis (exp[0] ^ 'c'=0x63) ---")
from collections import Counter
keys=[]
for i in range(0,5002,100):
    raw,dec,comp,exp = get_expanded(i)
    k = exp[0]^0x63
    keys.append(k)
    print(f"entry {i}: explen={len(exp):6d} exp0=0x{exp[0]:02x} key=0x{k:02x}")
print(Counter(keys))
