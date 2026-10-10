#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disassemble script.fls code objects with a hand-verified S-box map.

Guest interpreter: CPython **2.6** (proved by the presence of SET_LINENO=127,
removed in 2.7).  Opcode bytes are permuted through an S-box; the map below
came from:
  * notes/co_code_analysis/mapping_table_v4.json (statistically mined), and
  * hand verification while decoding netlogin.py (entry 4082).

Usage:  pydis26.py <marshal.bin> <func-name> [--all]
"""
import sys
sys.path.insert(0, '/home/user/MXSJ_TW_2022/tools')
from fls_batch_decoder import MarshalReader

# enc byte -> (std opcode, has_arg)
# std numbers are CPython 2.6
MAP = {
    0x41: (1,   0),   # POP_TOP            (verified: after CALL_FUNCTION)
    0x55: (83,  0),   # RETURN_VALUE       (verified: function tail)
    0x58: (25,  0),   # BINARY_SUBSCR      (verified: const[k])
    0x36: (68,  0),   # GET_ITER           (verified: for-loop head)
    0x40: (87,  0),   # POP_BLOCK          (verified: end of try body)
    0x10: (88,  0),   # END_FINALLY        (verified: 1B jumped over after except)
    0x06: (3,   0),   # ROT_THREE          (verified: a,b,c = x,y,z peephole)
    0x5A: (2,   0),   # ROT_TWO            (verified: same peephole)
    0x37: (22,  0),   # BINARY_MODULO      (verified: 'seed1:%x' % seed)
    0x05: (60,  0),   # STORE_SUBSCR       (verified: info['ID'] = UnpackInt(4))
    0x08: (84,  0),   # IMPORT_STAR
    0x38: (82,  0),   # LOAD_LOCALS
    0x42: (89,  0),   # BUILD_CLASS
    0x43: (23,  0),   # BINARY_ADD      (verified: CurCount += 1)
    0x09: (20,  0),   # BINARY_MULTIPLY (verified: pcinfo = '0' * 32)
    0x3E: (64,  0),   # BINARY_AND      (verified: adsid & 0xFFFFFFFF)
    0x46: (63,  0),   # BINARY_RSHIFT   (verified: adsid >> 32)
    0x5B: (66,  0),   # BINARY_OR       (verified: iScriptV1 | 128)
    0x0B: (70,  0),   # PRINT_ITEM      (verified: try/except print)
    0x1F: (71,  0),   # PRINT_NEWLINE   (verified: same)
    0x30: (104, 0),   # BUILD_MAP (1B, implicit empty) - dict literal head
    0xBC: (99,  1),   # DUP_TOPX        (verified: CurCount += 1)
    0x23: (24,  0),   # BINARY_SUBTRACT (v4 note: 23=SUBTRACT)
    0x3F: (24,  0),   # BINARY_SUBTRACT (4294967296 - seed)
    0x3D: (21,  0),   # BINARY_DIVIDE   (verified: seed/256%256, seed/65536%256)

    0x8F: (100, 1),   # LOAD_CONST
    0xBB: (100, 1),   # LOAD_CONST (2nd encoding, medium confidence)
    0x85: (101, 1),   # LOAD_NAME
    0xAA: (101, 1),   # LOAD_NAME  (2nd encoding)
    0xDE: (102, 1),   # BUILD_TUPLE
    0xCA: (103, 1),   # BUILD_LIST
    0xE0: (107, 1),   # IMPORT_NAME
    0xAD: (108, 1),   # IMPORT_FROM
    0xE5: (110, 1),   # JUMP_FORWARD
    0xB7: (114, 1),   # POP_JUMP_IF_FALSE
    0xE3: (115, 1),   # POP_JUMP_IF_TRUE
    0xA2: (113, 1),   # JUMP_ABSOLUTE
    0xC1: (124, 1),   # LOAD_FAST
    0x71: (125, 1),   # STORE_FAST
    0xCF: (127, 1),   # SET_LINENO      (2.6 only -- proves the 2.6 numbering)
    0xDA: (131, 1),   # CALL_FUNCTION
    0xFB: (132, 1),   # MAKE_FUNCTION
    0x6C: (92,  1),   # UNPACK_SEQUENCE
    0xD9: (105, 1),   # LOAD_ATTR
    0x95: (106, 1),   # COMPARE_OP
    0xAF: (93,  1),   # FOR_ITER
    0xD3: (120, 1),   # SETUP_LOOP
    0xC4: (90,  1),   # STORE_NAME
    0x98: (90,  1),   # STORE_NAME (2nd encoding)
    0xC5: (94,  1),   # STORE_ATTR
    0x91: (116, 1),   # LOAD_GLOBAL
    0xBF: (96,  1),   # STORE_GLOBAL
    0xEA: (101, 1),   # LOAD_? (LOAD_NAME-ish, medium confidence)
    0x72: (100, 1),   # LOAD_CONST? (medium)
}

# std -> (mnemonic, arg_renderer)
STD = {
    1: 'POP_TOP', 2: 'ROT_TWO', 3: 'ROT_THREE', 4: 'DUP_TOP', 5: 'ROT_FOUR',
    9: 'NOP', 10: 'UNARY_POSITIVE', 11: 'UNARY_NEGATIVE', 12: 'UNARY_NOT',
    13: 'UNARY_CONVERT', 15: 'UNARY_INVERT',
    19: 'BINARY_POWER', 20: 'BINARY_MULTIPLY', 21: 'BINARY_DIVIDE',
    22: 'BINARY_MODULO', 23: 'BINARY_ADD', 24: 'BINARY_SUBTRACT',
    25: 'BINARY_SUBSCR', 26: 'BINARY_FLOOR_DIVIDE', 27: 'BINARY_TRUE_DIVIDE',
    28: 'INPLACE_FLOOR_DIVIDE', 29: 'INPLACE_TRUE_DIVIDE',
    30: 'SLICE+0', 31: 'SLICE+1', 32: 'SLICE+2', 33: 'SLICE+3',
    40: 'STORE_SLICE+0', 41: 'STORE_SLICE+1', 42: 'STORE_SLICE+2',
    43: 'STORE_SLICE+3',
    50: 'DELETE_SLICE+0', 51: 'DELETE_SLICE+1', 52: 'DELETE_SLICE+2',
    53: 'DELETE_SLICE+3',
    54: 'STORE_MAP', 55: 'INPLACE_ADD', 56: 'INPLACE_SUBTRACT',
    57: 'INPLACE_MULTIPLY', 58: 'INPLACE_DIVIDE', 59: 'INPLACE_MODULO',
    60: 'STORE_SUBSCR', 61: 'DELETE_SUBSCR',
    62: 'BINARY_LSHIFT', 63: 'BINARY_RSHIFT', 64: 'BINARY_AND',
    65: 'BINARY_XOR', 66: 'BINARY_OR', 67: 'INPLACE_POWER',
    68: 'GET_ITER', 69: 'PRINT_EXPR', 70: 'PRINT_ITEM', 71: 'PRINT_NEWLINE',
    72: 'PRINT_ITEM_TO', 73: 'PRINT_NEWLINE_TO',
    74: 'INPLACE_LSHIFT', 75: 'INPLACE_RSHIFT', 76: 'INPLACE_AND',
    77: 'INPLACE_XOR', 78: 'INPLACE_OR',
    81: 'WITH_CLEANUP', 82: 'LOAD_LOCALS', 83: 'RETURN_VALUE',
    84: 'IMPORT_STAR', 85: 'EXEC_STMT', 86: 'YIELD_VALUE', 87: 'POP_BLOCK',
    88: 'END_FINALLY', 89: 'BUILD_CLASS',
    90: 'STORE_NAME', 91: 'DELETE_NAME', 92: 'UNPACK_SEQUENCE', 93: 'FOR_ITER',
    94: 'STORE_ATTR', 95: 'DELETE_ATTR', 96: 'STORE_GLOBAL',
    97: 'DELETE_GLOBAL', 99: 'DUP_TOPX',
    100: 'LOAD_CONST', 101: 'LOAD_NAME', 102: 'BUILD_TUPLE', 103: 'BUILD_LIST',
    104: 'BUILD_MAP', 105: 'LOAD_ATTR', 106: 'COMPARE_OP', 107: 'IMPORT_NAME',
    108: 'IMPORT_FROM', 110: 'JUMP_FORWARD', 111: 'JUMP_IF_FALSE_OR_POP',
    112: 'JUMP_IF_TRUE_OR_POP', 113: 'JUMP_ABSOLUTE',
    114: 'POP_JUMP_IF_FALSE', 115: 'POP_JUMP_IF_TRUE', 116: 'LOAD_GLOBAL',
    119: 'CONTINUE_LOOP', 120: 'SETUP_LOOP', 121: 'SETUP_EXCEPT',
    122: 'SETUP_FINALLY', 124: 'LOAD_FAST', 125: 'STORE_FAST',
    126: 'DELETE_FAST', 127: 'SET_LINENO',
    130: 'RAISE_VARARGS', 131: 'CALL_FUNCTION', 132: 'MAKE_FUNCTION',
    133: 'BUILD_SLICE', 134: 'MAKE_CLOSURE', 135: 'LOAD_CLOSURE',
    136: 'LOAD_DEREF', 137: 'STORE_DEREF',
    140: 'CALL_FUNCTION_VAR', 141: 'CALL_FUNCTION_KW',
    142: 'CALL_FUNCTION_VAR_KW',
}
CMP = ['<', '<=', '==', '!=', '>', '>=', 'in', 'not in', 'is', 'is not',
       'exception match', 'BAD']


def s(b):
    if isinstance(b, bytes):
        for enc in ('big5hkscs', 'gbk', 'utf-8', 'latin1'):
            try:
                return b.decode(enc)
            except Exception:
                continue
    return repr(b)


def short(c):
    if isinstance(c, dict) and 'code' in c:
        return '<code %s>' % s(c['name'])
    if isinstance(c, tuple):
        return '(' + ', '.join(short(x) for x in c) + ')'
    return repr(c)


class Dis:
    def __init__(self, o):
        self.o = o
        self.code = o['code']
        self.names = [s(x) for x in o['names']]
        self.varnames = [s(x) for x in o['varnames']]
        self.consts = o['consts']

    def arg_str(self, std, op, i):
        enc = self.code[i]
        a = op
        lo = op | (self.code[i + 2] << 8) if i + 2 < len(self.code) else op
        if std == 127:
            return 'line %d' % a
        if std in (100,):
            return '%d (%s)' % (a, short(self.consts[a]) if a < len(self.consts) else '?')
        if std in (101, 105, 107, 108, 90, 94, 96, 116, 91, 97):
            return '%d (%s)' % (a, self.names[a] if a < len(self.names) else '?')
        if std in (124, 125, 126):
            return '%d (%s)' % (a, self.varnames[a] if a < len(self.varnames) else '?')
        if std == 106:
            return '%d (%s)' % (a, CMP[a] if a < len(CMP) else '?')
        if std == 131:
            return '%d argc=%d kw=%d' % (a, a & 0xFF, a >> 8)
        if std in (110, 114, 115, 93, 120, 121, 122, 119):
            return '%d -> %d' % (a, i + 3 + a)
        if std == 113:
            return '%d -> %d' % (a, a)
        return str(a)

    def run(self):
        out = []
        i = 0
        n = len(self.code)
        while i < n:
            enc = self.code[i]
            if enc in MAP:
                std, has = MAP[enc]
                name = STD.get(std, '?%d' % std)
                if has:
                    op = self.code[i + 1] | (self.code[i + 2] << 8)
                    out.append('%4d  %-20s %s' % (i, name, self.arg_str(std, op, i)))
                    i += 3
                else:
                    out.append('%4d  %s' % (i, name))
                    i += 1
            else:
                out.append('%4d  <unk 0x%02x>' % (i, enc))
                i += 1
        return '\n'.join(out)


def walk(o):
    if isinstance(o, dict) and 'code' in o and 'consts' in o:
        yield o
        for c in o['consts']:
            if isinstance(c, dict) and 'code' in c:
                yield from walk(c)


def main():
    path = sys.argv[1]
    want = sys.argv[2] if len(sys.argv) > 2 else None
    r = MarshalReader(open(path, 'rb').read())
    root = r.read()
    for o in walk(root):
        nm = s(o['name'])
        if want and want not in nm:
            continue
        d = Dis(o)
        print('===== %s   arg=%d nloc=%d stack=%d  (len=%d)'
              % (nm, o['argcount'], o['nlocals'], o['stacksize'], len(d.code)))
        print(' names   :', d.names)
        print(' varnames:', d.varnames)
        print(' consts  :')
        for i, c in enumerate(d.consts):
            print('   [%2d] %s' % (i, short(c)))
        print(' ' + '-' * 70)
        print(d.run())
        print()


if __name__ == '__main__':
    main()
