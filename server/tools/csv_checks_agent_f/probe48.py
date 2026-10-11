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
from review_client_data_boundaries import instructions, evaluate_literals
ins = list(instructions(co))
names = co['names']; consts = co['consts']
STD = {0:'STOP_CODE',1:'POP_TOP',2:'ROT_TWO',3:'ROT_THREE',4:'DUP_TOP',5:'ROT_FOUR',9:'NOP',
       10:'UNARY_POSITIVE',11:'UNARY_NEGATIVE',12:'UNARY_NOT',13:'UNARY_CONVERT',15:'UNARY_INVERT',
       19:'BINARY_POWER',20:'BINARY_MULTIPLY',21:'BINARY_DIVIDE',22:'BINARY_MODULO',23:'BINARY_ADD',
       24:'BINARY_SUBTRACT',25:'BINARY_SUBSCR',26:'BINARY_LSHIFT',27:'BINARY_RSHIFT',28:'BINARY_AND',
       29:'BINARY_XOR',30:'BINARY_OR',31:'INPLACE_ADD',32:'INPLACE_SUBTRACT',
       60:'STORE_SUBSCR',61:'DELETE_SUBSCR',62:'BINARY_DIVIDE',63:'INPLACE_MODULO',
       70:'SLICE+0',71:'SLICE+1',72:'SLICE+2',73:'SLICE+3',
       80:'GET_ITER',81:'PRINT_EXPR',82:'PRINT_ITEM',83:'PRINT_NEWLINE',84:'INPLACE_DIVIDE',
       86:'LOAD_LOCALS',87:'RETURN_VALUE',88:'IMPORT_STAR',89:'POP_BLOCK',
       90:'STORE_NAME',91:'DELETE_NAME',92:'UNPACK_SEQUENCE',93:'FOR_ITER',94:'LIST_APPEND',
       95:'STORE_ATTR',96:'DELETE_ATTR',97:'STORE_GLOBAL',98:'BUILD_SLICE',99:'DELETE_ATTR',
       100:'LOAD_CONST',101:'LOAD_NAME',102:'BUILD_TUPLE',103:'BUILD_LIST',104:'BUILD_MAP',
       105:'LOAD_ATTR',106:'COMPARE_OP',107:'IMPORT_NAME',108:'IMPORT_FROM',110:'JUMP_FORWARD',
       111:'JUMP_IF_FALSE',112:'JUMP_IF_TRUE',113:'JUMP_ABSOLUTE',114:'FOR_LOOP',116:'LOAD_GLOBAL',
       119:'CALL_FUNCTION',120:'CALL_FUNCTION_VAR',121:'CALL_FUNCTION_KW',122:'CALL_FUNCTION_VAR_KW',
       124:'BUILD_FUNCTION',125:'MAKE_CLOSURE',126:'LOAD_DEREF',130:'SETUP_EXCEPT',131:'SETUP_FINALLY',
       132:'RAISE_VARARGS',133:'LOAD_LOCALS',134:'SET_LINENO',135:'EXTENDED_ARG',
       136:'DELETE_FAST',137:'STORE_FAST',140:'DELETE_GLOBAL',141:'LOAD_CLOSURE',142:'LOAD_DEREF',143:'EXTENDED_ARG'}
def name_of(op):
    return STD.get(op, 'OP%d' % op)
def show(a, b):
    for at, op, arg in ins:
        if a <= at < b:
            extra = ''
            if op == 100 and isinstance(arg, int) and arg < len(consts):
                extra = ' const=%r' % (consts[arg],)
            if op in (90, 97, 101, 116) and isinstance(arg, int) and arg < len(names):
                extra = ' name=%r' % (names[arg],)
            print('%7d  %-22s %s%s' % (at, name_of(op), arg, extra))
print('--- ORDER store region (2815..2840) ---')
show(2815, 2845)
print()
print('--- DATA build start (after ORDER store) ---')
show(2821, 3000)
