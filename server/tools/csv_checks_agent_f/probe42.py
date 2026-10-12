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
M = decoder.PY25_MAP
both = [k for k in M if (k ^ 0x42) in M]
print('duoyi opcodes k where both k and k^0x42 are mapped:', len(both), 'of', len(M))
print('sample:', [(k, M[k], k ^ 0x42, M[k ^ 0x42]) for k in sorted(both)[:12]])

def decode(bounds, keylist):
    edges = [0]+list(bounds)+[len(exp)]
    return b''.join(exp[edges[i]:edges[i+1]].translate(decoder.XTABS[keylist[i]]) for i in range(5))
def walk_strings(dec):
    out = []
    D = dec
    def w(p):
        t = D[p]; p += 1
        tc = chr(t)
        if tc in ('0','N','F','T','S','.'):
            return p
        if tc in ('i','I','g','R'):
            return p + (8 if tc in ('I','g') else 4)
        if tc == 'l':
            n = abs(struct.unpack_from('<i', D, p)[0]); return p+4+n*2
        if tc in ('s','t','u'):
            ln = struct.unpack_from('<I', D, p)[0]
            out.append(D[p+4:p+4+ln]); return p+4+ln
        if tc in ('f','x'):
            ln = D[p]; return p+1+ln
        if tc in ('(','[','<','>'):
            n = struct.unpack_from('<I', D, p)[0]; p += 4
            for _ in range(n): p = w(p)
            return p
        if tc == '{':
            while D[p] != ord('0'):
                p = w(p); p = w(p)
            return p+1
        if tc == 'c':
            p += 16
            clen = struct.unpack_from('<I', D, p+1)[0]
            p = p+5+clen
            for _ in range(5): p = w(p)
            p = w(p); p = w(p); p += 4; p = w(p)
            return p
        raise ValueError('tag %r at %d' % (tc, p-1))
    try:
        end = w(0)
    except Exception as e:
        return False, [], str(e)
    return end == len(dec), out, end
def score(bounds, keylist):
    dec = decode(bounds, keylist)
    ok, strs, info = walk_strings(dec)
    if not ok:
        return 'WALK FAIL: %s' % (info,)
    good = bad = 0
    for s in strs:
        if not s: continue
        try:
            t = s.decode('cp950'); good += 1
            if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t): bad += 1
        except UnicodeDecodeError:
            bad += 1
    return 'strs=%d good=%d bad=%d' % (len(strs), good, bad)

for label, k in [
    ('SAVED keys', list(ks)),
    ('key1=11', [233, 11, 132, 105, 246]),
    ('key1=73', [233, 73, 132, 105, 246]),
    ('key1=11,key2=198', [233, 11, 198, 105, 246]),
    ('key1=11,key2=11', [233, 11, 11, 105, 246]),
]:
    print('%-22s %s -> %s' % (label, k, score(list(base), k)))
