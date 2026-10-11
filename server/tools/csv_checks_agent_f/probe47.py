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
exp = payload(ENTRY); ks = m['keys']
BOUNDS = [18282, 36511, 54797, 73070]
KEYLIST = [233, 11, 132, 105, 246]
edges = [0]+BOUNDS+[len(exp)]
dec = b''.join(exp[edges[i]:edges[i+1]].translate(decoder.XTABS[KEYLIST[i]]) for i in range(5))
tr = decoder.Py25MarshalTranspiler(dec, exp, KEYLIST, BOUNDS)
tr.transpile_object()
r = MarshalReader(bytes(tr.out)[8:]); co = r.read()
print('filename', co['filename'], 'names', len(co['names']), 'consts', len(co['consts']))
sys.path.insert(0, str(ROOT/'server/tools'))
from review_client_data_boundaries import instructions, evaluate_literals
# collect all instructions
ins = list(instructions(co))
print('total instructions', len(ins))
# find STORE_NAME/STORE_GLOBAL positions
stores = [(at, op, arg, co['names'][arg]) for at, op, arg in ins if op in (90, 97)]
print('num stores', len(stores))
for at, op, arg, nm in stores:
    print('   STORE %-24s at %d' % (nm.decode(), at))
