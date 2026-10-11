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
def quality(key, a, b):
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
best = []
for B in range(36000, 37200):
    n1, u1 = quality(11, 18282, B)
    n2, u2 = quality(132, B, 47423)
    best.append((u1+u2, B, u1, n1, u2, n2))
best.sort()
for row in best[:10]:
    print('total_unmapped=%d B1=%d (k11: %d/%d, k132: %d/%d)' % row)
print()
print('unmapped for [18282,47423) with key 11 alone:', quality(11, 18282, 47423))
print('unmapped for [18282,47423) with key 132 alone:', quality(132, 18282, 47423))
