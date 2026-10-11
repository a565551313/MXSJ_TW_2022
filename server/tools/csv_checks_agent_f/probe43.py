import sys, json, zlib, struct, traceback
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

for label, k in [('SAVED', list(ks)), ('key1=11', [233, 11, 132, 105, 246]), ('key1=73', [233, 73, 132, 105, 246])]:
    print('===', label, k)
    try:
        co = load(list(base), k)
    except Exception as e:
        print('   load FAIL', type(e).__name__, e); continue
    print('   filename', co['filename'], 'names', len(co['names']), 'consts', len(co['consts']))
    # walk instructions fully
    code = co['code']
    at = 0; extension = 0; cnt = 0; err = None
    while at < len(code):
        start = at; op = code[at]; at += 1; arg = None
        if op >= 90:
            if at+2 > len(code):
                err = 'truncated at %d' % start; break
            arg = int.from_bytes(code[at:at+2], 'little') | extension
            at += 2
            if op == 143:
                extension = arg << 16; cnt += 1; continue
            extension = 0
        elif extension:
            err = 'EXTENDED_ARG before argument-free instruction at %d (op %d)' % (start, op); break
        cnt += 1
    print('   instructions walked:', cnt, 'error:', err)
    if err:
        continue
    for name in ('TYPE2NAME', 'ORDER', 'DATA', 'SITE', 'LAYER', 'DIDRANGE', 'SPE_HORSE_DATA'):
        try:
            v = extract(co, name)
            print('   %-16s -> %s len=%s' % (name, type(v).__name__, len(v)))
        except Exception as e:
            print('   %-16s -> FAIL %s: %s' % (name, type(e).__name__, e))
