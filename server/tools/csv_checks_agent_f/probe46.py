import sys, json, zlib, struct
from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder
keys = json.loads((ROOT/'tools/decompiler/script_fls_keys.json').read_bytes())
arch = (ROOT/'data/script.fls').read_bytes()
idx_off = struct.unpack_from('<I', arch, 8)[0]
def payload(index):
    entry_id, a, b, c = struct.unpack_from('<IIII', arch, idx_off + 16*index)
    size = ((a*entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
    pos = ((b*index*0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
    return zlib.decompress(arch[pos:pos+size])
ENTRY = 244
m = keys[str(ENTRY)]
exp = payload(ENTRY); ks = m['keys']; base = m['bounds']
def quality(key, a, b, start_aligned=True):
    reg = exp[a:b].translate(decoder.XTABS[key])
    i = 0; n = 0; um = 0
    while i < len(reg):
        op = reg[i]
        if op >= 0x5F:
            if i+3 > len(reg): break
            i += 3
        else:
            i += 1
        n += 1
        if op not in decoder.PY25_MAP:
            um += 1
    return n, um
print('quality(132, 34193, 47423) =', quality(132, 34193, 47423))
print('quality(11, 18282, 34193)  =', quality(11, 18282, 34193))
print('quality(132, 18282, 34193) =', quality(132, 18282, 34193))
print()
# instruction alignment check for B1 candidates
for B in (36508, 36509, 36510, 36511, 36512, 36513, 36514, 36515, 36516):
    reg = exp[18282:B].translate(decoder.XTABS[11])
    i = 0; last = None
    while i < len(reg):
        op = reg[i]
        last = (i, op)
        i += 3 if op >= 0x5F else 1
    print('B1=%d  parse of [18282,B1) with key11 ends exactly at boundary: %s (last instr start %s op %s)' % (
        B, i == len(reg), last[0] if last else None, last[1] if last else None))
