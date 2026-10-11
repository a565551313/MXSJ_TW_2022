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
sys.path.insert(0, str(ROOT/'server/tools'))
from review_client_data_boundaries import instructions
ins = list(instructions(co))
names = co['names']; consts = co['consts']
STD = {2:'ROT_TWO',3:'ROT_THREE',4:'DUP_TOP',5:'ROT_FOUR',9:'NOP',60:'STORE_SUBSCR',
       90:'STORE_NAME',100:'LOAD_CONST',101:'LOAD_NAME',102:'BUILD_TUPLE',103:'BUILD_LIST',104:'BUILD_MAP'}
def show(a, b):
    for at, op, arg in ins:
        if a <= at < b:
            extra = ''
            if op == 100 and isinstance(arg, int) and arg < len(consts):
                extra = ' const=%r' % (consts[arg],)
            if op in (90, 101) and isinstance(arg, int) and arg < len(names):
                extra = ' name=%r' % (names[arg],)
            print('%7d  %-14s %s%s' % (at, STD.get(op, 'OP%d' % op), arg, extra))
print('--- around end of first inner dict ---')
show(2930, 3120)
