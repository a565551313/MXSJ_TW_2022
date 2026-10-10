#!/usr/bin/env python3
"""Disassemble Python-2.x marshal blobs (decoded .fls entries) with a built-in
opcode table (2.7 superset; 2.4-2.6 compatible subset). No xdis needed.
Usage: pymarshal_dis.py <marshal.bin> [--max-code N] [--consts] [--code-only NAME]
"""
import struct, sys, marshal as _unused  # noqa (py3 marshal can't read py2)

# Game uses CPython 2.6 opcode numbering with an S-box on opcode bytes.
# (2.6: BUILD_MAP=104, LOAD_ATTR=105, COMPARE_OP=106; NO BUILD_SET.)
# _STD maps std-opnum -> (name, argkind). argkind: None(no arg), else
# 'const','name','varname','free','cell','cmp','jrel','jabs','nargs','nfwd'.
_STD = {
 1:('POP_TOP',None),2:('ROT_TWO',None),3:('ROT_THREE',None),4:('DUP_TOP',None),
 5:('ROT_FOUR',None),9:('NOP',None),10:('UNARY_POSITIVE',None),11:('UNARY_NEGATIVE',None),
 12:('UNARY_NOT',None),13:('UNARY_CONVERT',None),15:('UNARY_INVERT',None),
 16:('LIST_APPEND?',None),19:('BINARY_POWER',None),20:('BINARY_MULTIPLY',None),
 21:('BINARY_DIVIDE',None),22:('BINARY_MODULO',None),23:('BINARY_ADD',None),
 24:('BINARY_SUBTRACT',None),25:('BINARY_SUBSCR',None),26:('BINARY_FLOOR_DIVIDE',None),
 27:('BINARY_TRUE_DIVIDE',None),28:('INPLACE_FLOOR_DIVIDE',None),29:('INPLACE_TRUE_DIVIDE',None),
 30:('SLICE+0',None),31:('SLICE+1',None),32:('SLICE+2',None),33:('SLICE+3',None),
 40:('STORE_SLICE+0',None),41:('STORE_SLICE+1',None),42:('STORE_SLICE+2',None),43:('STORE_SLICE+3',None),
 50:('DELETE_SLICE+0',None),51:('DELETE_SLICE+1',None),52:('DELETE_SLICE+2',None),53:('DELETE_SLICE+3',None),
 54:('STORE_MAP',None),55:('INPLACE_ADD',None),56:('INPLACE_SUBTRACT',None),57:('INPLACE_MULTIPLY',None),
 58:('INPLACE_DIVIDE',None),59:('INPLACE_MODULO',None),60:('STORE_SUBSCR',None),61:('DELETE_SUBSCR',None),
 62:('BINARY_LSHIFT',None),63:('BINARY_RSHIFT',None),64:('BINARY_AND',None),65:('BINARY_XOR',None),
 66:('BINARY_OR',None),67:('INPLACE_POWER',None),68:('GET_ITER',None),69:('PRINT_EXPR',None),
 70:('PRINT_ITEM',None),71:('PRINT_NEWLINE',None),72:('PRINT_ITEM_TO',None),73:('PRINT_NEWLINE_TO',None),
 74:('INPLACE_LSHIFT',None),75:('INPLACE_RSHIFT',None),76:('INPLACE_AND',None),77:('INPLACE_XOR',None),
 78:('INPLACE_OR',None),79:('<?79>',None),80:('BREAK_LOOP',None),81:('WITH_CLEANUP',None),
 82:('LOAD_LOCALS',None),83:('RETURN_VALUE',None),
 84:('IMPORT_STAR',None),85:('EXEC_STMT',None),86:('YIELD_VALUE',None),87:('POP_BLOCK',None),
 88:('END_FINALLY',None),
 89:('BUILD_CLASS',None),90:('STORE_NAME','name'),91:('DELETE_NAME','name'),
 92:('UNPACK_SEQUENCE','nargs'),93:('FOR_ITER','jrel'),94:('STORE_ATTR','name'),
 95:('DELETE_ATTR','name'),96:('STORE_GLOBAL','name'),97:('DELETE_GLOBAL','name'),
 99:('DUP_TOPX','nargs'),100:('LOAD_CONST','const'),101:('LOAD_NAME','name'),
 102:('BUILD_TUPLE','nargs'),103:('BUILD_LIST','nargs'),104:('BUILD_MAP','nargs'),
 105:('LOAD_ATTR','name'),106:('COMPARE_OP','cmp'),107:('IMPORT_NAME','name'),
 108:('IMPORT_FROM','name'),110:('JUMP_FORWARD','jrel'),111:('JUMP_IF_FALSE_OR_POP','jabs'),
 112:('JUMP_IF_TRUE_OR_POP','jabs'),113:('JUMP_ABSOLUTE','jabs'),114:('POP_JUMP_IF_FALSE','jrel'),
 115:('POP_JUMP_IF_TRUE','jrel'),116:('LOAD_GLOBAL','name'),119:('CONTINUE_LOOP','jrel'),
 120:('SETUP_LOOP','jrel'),121:('SETUP_EXCEPT','jrel'),122:('SETUP_FINALLY','jrel'),
 124:('LOAD_FAST','varname'),125:('STORE_FAST','varname'),126:('DELETE_FAST','varname'),
 127:('SET_LINENO','nargs'),130:('RAISE_VARARGS','nargs'),131:('CALL_FUNCTION','nargs'),
 132:('MAKE_FUNCTION','nargs'),133:('BUILD_SLICE','nargs'),134:('MAKE_CLOSURE','nargs'),
 135:('LOAD_CLOSURE','cell'),136:('LOAD_DEREF','free'),137:('STORE_DEREF','free'),
 140:('CALL_FUNCTION_VAR','nargs'),141:('CALL_FUNCTION_KW','nargs'),142:('CALL_FUNCTION_VAR_KW','nargs'),
}
_CMP = ['<','<=','==','!=','>','>=','in','not in','is','is not','exception match','BAD']
import json as _json, os as _os
def _load_maps():
    for base in (_os.path.dirname(_os.path.abspath(__file__)), _os.getcwd()):
        for sub in ('work/dream-world-connect-login-map/notes/co_code_analysis',
                    '../work/dream-world-connect-login-map/notes/co_code_analysis'):
            for ver in ('mapping_table_v4.json', 'mapping_table_v3_corrected.json'):
                p = _os.path.join(base, sub, ver)
                if _os.path.exists(p):
                    t = _json.load(open(p)); return t.get('table_a',{}), t.get('table_b',{})
    # fallback: embedded high-confidence core
    A={'0x55':83,'0x85':101,'0x8F':100,'0xC1':124,'0xC4':90,'0x41':1,'0x71':125,
       '0x95':106,'0xB7':114,'0xE5':110,'0xD9':105,'0xDA':131,'0xDE':102,'0xCA':103,
       '0xE0':104,'0xC5':94,'0x37':92}
    B={'0x98':132,'0xFB':90,'0xAA':101,'0xBF':96,'0x91':116,'0x38':89,'0x42':1}
    return ({k:{'std':hex(v)} for k,v in A.items()},{k:{'std':hex(v)} for k,v in B.items()})
_TABLE_A, _TABLE_B = _load_maps()
def _sbox(enc, table):
    e=table.get(f'0x{enc:02X}') or table.get(f'0x{enc:02x}')
    if not e: return None
    s=e.get('std') if isinstance(e,dict) else e
    if s is None: return None
    try:
        return int(s,16) if isinstance(s,str) else int(s)
    except (ValueError, TypeError):
        return None  # uncertain std ("0x17?") -> treat as unknown

class R:
    """Thin wrapper over fls_batch_decoder.MarshalReader (handles all 4K+
    entries incl. edge cases), converting its dict-based AST into this
    module's ('tag', value) tuples for the disassembler below."""
    def __init__(self, d):
        from fls_batch_decoder import MarshalReader
        r = MarshalReader(bytes(d))
        self.root = _conv(r.read())
        self.code_objects = r.code_objects
    def rd(self):
        return self.root

def _conv(o):
    if isinstance(o, dict) and 'code' in o and 'consts' in o:
        f = {}
        for k in ('argcount','nlocals','stacksize','flags','firstlineno'):
            f[k] = o[k]
        for k in ('code','consts','names','varnames','freevars','cellvars',
                  'filename','name','lnotab'):
            f[k] = _conv(o[k])
        return ('code', f)
    if isinstance(o, bytes): return ('str', o)
    if isinstance(o, str): return ('ustr', o.encode('utf-8', 'replace'))
    if isinstance(o, bool): return (('true' if o else 'false'), o)
    if isinstance(o, int): return ('int', o)
    if isinstance(o, float): return ('float', o)
    if isinstance(o, tuple): return ('tuple', [_conv(x) for x in o])
    if isinstance(o, list): return ('list', [_conv(x) for x in o])
    if o is None: return ('none', None)
    if o is Ellipsis: return ('ellipsis', None)
    return ('other', repr(o)[:60])

def b2s(b):
    try: return bytes(b).decode('utf-8')
    except Exception: return bytes(b).decode('latin1')

def dis_code(f, indent=0, consts=False):
    pre='  '*indent
    code=f['code'][1]; consts_t=f['consts'][1]; names=[b2s(x[1]) for x in f['names'][1]]
    varnames=[b2s(x[1]) for x in f['varnames'][1]]
    out=[f"{pre}code {b2s(f['name'][1])} ({b2s(f['filename'][1])}:{f['firstlineno']}) a={f['argcount']} nloc={f['nlocals']} stk={f['stacksize']}"]
    if consts:
        for i,c in enumerate(consts_t):
            if c[0]!='code': out.append(f"{pre}  const[{i}] {c[0]} {repr(b2s(c[1]))[:90] if isinstance(c[1],(bytes,bytearray)) else repr(c[1])[:90]}")
    out.append(f"{pre}  names={names[:24]}{'...' if len(names)>24 else ''}")
    out.append(f"{pre}  varnames={varnames[:16]}{'...' if len(varnames)>16 else ''}")
    p=0
    while p < len(code):
        start=p; enc=code[p]; p+=1
        std=_sbox(enc,_TABLE_A)
        src='A'
        if std is None: std=_sbox(enc,_TABLE_B); src='B'
        if std is not None:
            nm,kind=_STD.get(std,(f'<std{std}>','nargs' if std>=90 else None))
        else:
            # unknown: size from override map else guess 3B
            sz=_SIZE_OVERRIDES.get(enc, 3)
            nm,kind=(f'<U:{enc:02X}>','nargs?' if sz==3 else None)
        arg=None
        if kind is not None:
            if p+1>=len(code): out.append(f"{pre}  {start:5d} {nm} <trunc>"); break
            arg=code[p]|(code[p+1]<<8); p+=2
        extra=''
        if kind=='const' and arg<len(consts_t):
            c=consts_t[arg]
            extra=" const[%d]="%arg+(repr(b2s(c[1]))[:60] if c[0] in ('str','ustr') else repr(c[1])[:60] if c[0]!='code' else "<code %s>"%b2s(c[1]['name'][1]))
        elif kind=='name':
            if arg<len(names): extra=f" {names[arg]}"
            else: extra=f" <name#{arg} OUT-OF-RANGE({len(names)})>"
        elif kind=='varname' and arg<len(varnames): extra=f" {varnames[arg]}"
        elif kind=='cmp' and arg<len(_CMP): extra=f" {_CMP[arg]}"
        elif kind=='nargs' and nm=='CALL_FUNCTION': extra=f" argc={arg&0xff} kw={arg>>8}"
        elif kind=='jrel': extra=f" -> {p+arg}"
        elif kind=='jabs': extra=f" -> {arg}"
        out.append(f"{pre}  {start:5d} {nm}{(' '+str(arg)) if arg is not None else ''}{extra}")
        if len(out)>4000: out.append(f"{pre}  ... (truncated)"); break
    for c in consts_t:
        if c[0]=='code': out.append(dis_code(c[1],indent+1,consts=consts))
    return '\n'.join(out)

# learned default sizes for unmapped bytes (v4); --sizes can override.
# 0x6c is dual (3B-UNPACK logic / 1B-BINARY data): default 3, use --sizes 6c:1 if desync.
_SIZE_OVERRIDES = {0xbb:3, 0x30:1, 0x5a:1, 0x05:1, 0x08:1, 0xad:3, 0x6c:3,
                   0x36:1, 0x3f:1, 0x09:1, 0x20:1, 0xe3:3, 0x23:1, 0x15:1,
                   0x43:1}
def main():
    global _SIZE_OVERRIDES
    a=sys.argv[1:]
    if not a: print(__doc__); return
    fn=a[0]; maxc=None; consts='--consts' in a; only=None
    if '--max-code' in a: maxc=int(a[a.index('--max-code')+1])
    if '--code-only' in a: only=a[a.index('--code-only')+1]
    if '--sizes' in a:
        for kv in a[a.index('--sizes')+1].split(','):
            k,v=kv.split(':'); _SIZE_OVERRIDES[int(k,16)]=int(v)
    d=open(fn,'rb').read()
    root=R(d).rd()
    if root[0]!='code': print('not a code object:',root[0]); return
    if only:
        found=[]
        def walk(f):
            if b2s(f['name'][1])==only: found.append(f)
            for c in f['consts'][1]:
                if c[0]=='code': walk(c[1])
        walk(root[1])
        for f in found[:maxc or 99]: print(dis_code(f,consts=consts))
    else:
        print(dis_code(root[1],consts=consts))

if __name__=='__main__': main()
