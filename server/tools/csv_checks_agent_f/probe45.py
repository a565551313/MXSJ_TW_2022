import sys, json, zlib, struct
from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder
from tools.fls_batch_decoder import MarshalReader
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
def decode(bounds, keylist):
    edges = [0]+list(bounds)+[len(exp)]
    return b''.join(exp[edges[i]:edges[i+1]].translate(decoder.XTABS[keylist[i]]) for i in range(5))
def load(bounds, keylist):
    dec = decode(bounds, keylist)
    tr = decoder.Py25MarshalTranspiler(dec, exp, keylist, list(bounds))
    tr.transpile_object()
    r = MarshalReader(bytes(tr.out)[8:]); co = r.read()
    if r.pos != len(r.data):
        raise ValueError('marshal reader did not consume the full output')
    return co
sys.path.insert(0, str(ROOT/'server/tools'))
from review_client_data_boundaries import instructions, evaluate_literals
def extract(co, name):
    seg = []
    for at, op, arg in instructions(co):
        seg.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == name.encode('ascii'):
                return evaluate_literals(co, seg[:-1]+[(at, 90, arg)])
            seg = []
    raise ValueError('no ' + name)

def walk_strings(dec):
    out = []
    D = dec
    def w(p):
        t = D[p]; p += 1
        tc = chr(t)
        if tc in ('0','N','F','T','S','.'): return p
        if tc in ('i','I','g','R'): return p + (8 if tc in ('I','g') else 4)
        if tc == 'l':
            n = abs(struct.unpack_from('<i', D, p)[0]); return p+4+n*2
        if tc in ('s','t','u'):
            ln = struct.unpack_from('<I', D, p)[0]; out.append(D[p+4:p+4+ln]); return p+4+ln
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
            clen = struct.unpack_from('<I', D, p+1)[0]; p = p+5+clen
            for _ in range(5): p = w(p)
            p = w(p); p = w(p); p += 4; p = w(p)
            return p
        raise ValueError('tag %r at %d' % (tc, p-1))
    try:
        end = w(0)
    except Exception as e:
        return False, [], str(e)
    return end == len(dec), out, end

for label, b, k in [
    ('SAVED', list(base), list(ks)),
    ('B1=34193 key1=11', [18282, 34193, 54797, 73070], [233, 11, 132, 105, 246]),
    ('B1=36511 key1=11', [18282, 36511, 54797, 73070], [233, 11, 132, 105, 246]),
    ('B1=36511 key1=73', [18282, 36511, 54797, 73070], [233, 73, 132, 105, 246]),
]:
    print('===', label, b, k)
    dec = decode(b, k)
    ok, strs, info = walk_strings(dec)
    print('   marshal walk ok:', ok, info if not ok else '')
    if ok:
        good = bad = 0
        for s in strs:
            if not s: continue
            try:
                t = s.decode('cp950'); good += 1
                if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t): bad += 1
            except UnicodeDecodeError: bad += 1
        print('   strings=%d good=%d bad=%d' % (len(strs), good, bad))
    try:
        co = load(b, k)
    except Exception as e:
        print('   load FAIL', type(e).__name__, e); continue
    code = co['code']
    at = 0; extension = 0; cnt = 0; err = None
    while at < len(code):
        start = at; op = code[at]; at += 1
        if op >= 90:
            if at+2 > len(code): err = 'truncated at %d' % start; break
            arg = int.from_bytes(code[at:at+2], 'little') | extension
            at += 2
            if op == 143:
                extension = arg << 16; cnt += 1; continue
            extension = 0
        elif extension:
            err = 'EXTENDED_ARG before argument-free instruction at %d (op %d)' % (start, op); break
        cnt += 1
    print('   instructions walked:', cnt, 'error:', err)
    if err: continue
    for name in ('TYPE2NAME', 'ORDER', 'DATA', 'SITE', 'LAYER', 'DIDRANGE', 'SPE_HORSE_DATA'):
        try:
            v = extract(co, name)
            extra = ''
            if isinstance(v, dict) and v:
                k0 = list(v)[0]
                extra = ' first=%r' % (v[k0],)
            print('   %-16s -> %s len=%s%s' % (name, type(v).__name__, len(v), extra[:120]))
        except Exception as e:
            print('   %-16s -> FAIL %s: %s' % (name, type(e).__name__, e))
