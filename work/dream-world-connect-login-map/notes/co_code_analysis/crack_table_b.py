#!/usr/bin/env python3
"""
破解替换表B（类定义函数的映射表）
分析7个表B函数，破解新的opcode映射
"""

import struct
import json
from collections import Counter

# ========== Python 2.7 正确 opcode 表 ==========
OPNAME = {
    0x01: 'POP_TOP', 0x02: 'ROT_TWO', 0x03: 'ROT_THREE', 0x04: 'DUP_TOP',
    0x05: 'ROT_FOUR', 0x09: 'NOP', 0x0A: 'UNARY_POSITIVE', 0x0B: 'UNARY_NEGATIVE',
    0x0C: 'UNARY_NOT', 0x0F: 'UNARY_INVERT', 0x10: 'BINARY_POWER', 0x11: 'BINARY_MULTIPLY',
    0x13: 'BINARY_FLOOR_DIVIDE', 0x14: 'BINARY_TRUE_DIVIDE', 0x15: 'BINARY_MODULO',
    0x16: 'BINARY_ADD', 0x17: 'BINARY_SUBTRACT', 0x18: 'BINARY_SUBSCR',
    0x19: 'BINARY_LSHIFT', 0x1A: 'BINARY_RSHIFT', 0x1B: 'BINARY_AND',
    0x1C: 'BINARY_XOR', 0x1D: 'BINARY_OR', 0x1E: 'INPLACE_POWER',
    0x1F: 'INPLACE_MULTIPLY', 0x21: 'INPLACE_FLOOR_DIVIDE', 0x22: 'INPLACE_TRUE_DIVIDE',
    0x23: 'INPLACE_MODULO', 0x24: 'INPLACE_ADD', 0x25: 'INPLACE_SUBTRACT',
    0x26: 'INPLACE_LSHIFT', 0x27: 'INPLACE_RSHIFT', 0x28: 'INPLACE_AND',
    0x29: 'INPLACE_XOR', 0x2A: 'INPLACE_OR', 0x2B: 'SLICE+0', 0x2C: 'SLICE+1',
    0x2D: 'SLICE+2', 0x2E: 'SLICE+3', 0x2F: 'STORE_SLICE+0', 0x30: 'STORE_SLICE+1',
    0x31: 'STORE_SLICE+2', 0x32: 'STORE_SLICE+3', 0x33: 'DELETE_SLICE+0',
    0x34: 'DELETE_SLICE+1', 0x35: 'DELETE_SLICE+2', 0x36: 'DELETE_SLICE+3',
    0x37: 'STORE_MAP', 0x3C: 'RETURN_VALUE',  # 注意：Python 2.7 中 RETURN_VALUE = 83 = 0x53!
    0x3D: 'PRINT_EXPR', 0x3E: 'PRINT_ITEM', 0x3F: 'PRINT_NEWLINE',
    0x40: 'PRINT_ITEM_TO', 0x41: 'PRINT_NEWLINE_TO',
    0x42: 'BUILD_CLASS', 0x43: 'STORE_NAME', 0x44: 'DELETE_NAME',
    0x45: 'UNPACK_SEQUENCE', 0x46: 'FOR_ITER', 0x47: 'LIST_APPEND',
    0x48: 'STORE_ATTR', 0x49: 'DELETE_ATTR', 0x4A: 'STORE_GLOBAL',
    0x4B: 'DELETE_GLOBAL', 0x4C: 'DUP_TOPX', 0x4D: 'LOAD_CONST',
    0x4E: 'LOAD_NAME', 0x4F: 'BUILD_TUPLE', 0x50: 'BUILD_LIST',
    0x51: 'BUILD_MAP', 0x52: 'LOAD_ATTR', 0x53: 'COMPARE_OP',
    0x54: 'IMPORT_NAME', 0x55: 'IMPORT_FROM', 0x56: 'JUMP_FORWARD',
    0x57: 'JUMP_IF_FALSE', 0x58: 'JUMP_IF_TRUE', 0x59: 'JUMP_ABSOLUTE',
    0x5A: 'POP_JUMP_IF_FALSE', 0x5B: 'POP_JUMP_IF_TRUE', 0x5C: 'LOAD_GLOBAL',
    0x5D: 'CONTINUE_LOOP', 0x5E: 'SETUP_LOOP', 0x5F: 'SETUP_EXCEPT',
    0x60: 'SETUP_FINALLY', 0x61: 'LOAD_FAST', 0x62: 'STORE_FAST',
    0x63: 'DELETE_FAST', 0x64: 'RAISE_VARARGS', 0x65: 'CALL_FUNCTION',
    0x66: 'MAKE_FUNCTION', 0x67: 'BUILD_SLICE', 0x68: 'MAKE_CLOSURE',
    0x69: 'LOAD_CLOSURE', 0x6A: 'LOAD_DEREF', 0x6B: 'STORE_DEREF',
    0x6C: 'CALL_FUNCTION_VAR', 0x6D: 'CALL_FUNCTION_KW', 0x6E: 'CALL_FUNCTION_VAR_KW',
    0x6F: 'EXTENDED_ARG', 0x70: 'SETUP_WITH', 0x71: 'YIELD_VALUE',
    0x72: 'VIEW_ITER', 0x73: 'STORE_LOCALS',
}

# 修正：Python 2.7 官方 opcode 值
PY27_OPNAME = {
    1: 'POP_TOP', 2: 'ROT_TWO', 3: 'ROT_THREE', 4: 'DUP_TOP', 5: 'ROT_FOUR',
    9: 'NOP', 10: 'UNARY_POSITIVE', 11: 'UNARY_NEGATIVE', 12: 'UNARY_NOT',
    15: 'UNARY_INVERT', 19: 'BINARY_POWER', 20: 'BINARY_MULTIPLY',
    21: 'BINARY_DIVIDE', 22: 'BINARY_MODULO', 23: 'BINARY_ADD', 24: 'BINARY_SUBTRACT',
    25: 'BINARY_SUBSCR', 26: 'BINARY_FLOOR_DIVIDE', 27: 'BINARY_TRUE_DIVIDE',
    28: 'INPLACE_FLOOR_DIVIDE', 29: 'INPLACE_TRUE_DIVIDE',
    30: 'SLICE+0', 31: 'SLICE+1', 32: 'SLICE+2', 33: 'SLICE+3',
    40: 'STORE_SLICE+0', 41: 'STORE_SLICE+1', 42: 'STORE_SLICE+2', 43: 'STORE_SLICE+3',
    50: 'DELETE_SLICE+0', 51: 'DELETE_SLICE+1', 52: 'DELETE_SLICE+2', 53: 'DELETE_SLICE+3',
    54: 'STORE_MAP', 55: 'INPLACE_ADD', 56: 'INPLACE_SUBTRACT', 57: 'INPLACE_MULTIPLY',
    58: 'INPLACE_DIVIDE', 59: 'INPLACE_MODULO', 60: 'INPLACE_POWER', 61: 'GET_ITER',
    70: 'PRINT_EXPR', 71: 'PRINT_ITEM', 72: 'PRINT_NEWLINE', 73: 'PRINT_ITEM_TO',
    74: 'PRINT_NEWLINE_TO', 75: 'INPLACE_LSHIFT', 76: 'INPLACE_RSHIFT',
    77: 'INPLACE_AND', 78: 'INPLACE_XOR', 79: 'INPLACE_OR', 80: 'BREAK_LOOP',
    81: 'WITH_CLEANUP', 82: 'LOAD_LOCALS', 83: 'RETURN_VALUE', 84: 'IMPORT_STAR',
    85: 'EXEC_STMT', 86: 'YIELD_VALUE', 87: 'POP_BLOCK', 88: 'END_FINALLY',
    89: 'BUILD_CLASS',
    90: 'STORE_NAME', 91: 'DELETE_NAME', 92: 'UNPACK_SEQUENCE', 93: 'FOR_ITER',
    94: 'STORE_ATTR', 95: 'DELETE_ATTR', 96: 'STORE_GLOBAL', 97: 'DELETE_GLOBAL',
    98: 'DUP_TOPX', 100: 'LOAD_CONST', 101: 'LOAD_NAME', 102: 'BUILD_TUPLE',
    103: 'BUILD_LIST', 104: 'BUILD_MAP', 105: 'LOAD_ATTR', 106: 'COMPARE_OP',
    107: 'IMPORT_NAME', 108: 'IMPORT_FROM',
    110: 'JUMP_FORWARD', 111: 'JUMP_IF_FALSE', 112: 'JUMP_IF_TRUE',
    113: 'JUMP_ABSOLUTE', 114: 'POP_JUMP_IF_FALSE', 115: 'POP_JUMP_IF_TRUE',
    116: 'LOAD_GLOBAL', 119: 'CONTINUE_LOOP',
    120: 'SETUP_LOOP', 121: 'SETUP_EXCEPT', 122: 'SETUP_FINALLY',
    124: 'LOAD_FAST', 125: 'STORE_FAST', 126: 'DELETE_FAST',
    130: 'RAISE_VARARGS', 131: 'CALL_FUNCTION', 132: 'MAKE_FUNCTION',
    133: 'BUILD_SLICE', 134: 'MAKE_CLOSURE', 135: 'LOAD_CLOSURE',
    136: 'LOAD_DEREF', 137: 'STORE_DEREF',
    140: 'CALL_FUNCTION_VAR', 141: 'CALL_FUNCTION_KW', 142: 'CALL_FUNCTION_VAR_KW',
    143: 'SETUP_WITH', 144: 'EXTENDED_ARG',
}

# 无参数指令（1字节）— Python 2.7
NO_ARG_OPS = {
    1, 2, 3, 4, 5, 9, 10, 11, 12, 15, 19, 20, 21, 22, 23, 24, 25, 26, 27,
    28, 29, 30, 31, 32, 33, 40, 41, 42, 43, 50, 51, 52, 53, 54, 55, 56, 57,
    58, 59, 60, 61, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83,
    84, 85, 86, 87, 88, 89,  # BUILD_CLASS也是无参数！
}

# 有参数指令（3字节）— Python 2.7
HAS_ARG_OPS = {
    90, 91, 92, 93, 94, 95, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106,
    107, 108, 110, 111, 112, 113, 114, 115, 116, 119, 120, 121, 122, 124,
    125, 126, 130, 131, 132, 133, 134, 135, 136, 137, 140, 141, 142, 143, 144,
}

# ========== 已知映射（修正版）==========
# 注意：之前的映射中opcode值有系统性错误，这里修正为正确的Python 2.7值

# 表A映射（编码 → Python 2.7 标准opcode）
MAPPING_A = {
    0x41: 1,     # POP_TOP (1字节)
    0x55: 83,    # RETURN_VALUE (1字节)
    0x71: 125,   # STORE_FAST (3字节)
    0x85: 101,   # LOAD_NAME (3字节)
    0x8F: 100,   # LOAD_CONST (3字节)
    0x95: 106,   # COMPARE_OP (3字节)
    0xB7: 114,   # POP_JUMP_IF_FALSE (3字节)
    0xC1: 124,   # LOAD_FAST (3字节)
    0xC4: 90,    # STORE_NAME (3字节)
    0xC5: 94,    # STORE_ATTR (3字节)
    0xCA: 103,   # BUILD_LIST (3字节)
    0xD9: 105,   # LOAD_ATTR (3字节)
    0xDA: 131,   # CALL_FUNCTION (3字节)
    0xDE: 102,   # BUILD_TUPLE (3字节)
    0xE0: 104,   # BUILD_MAP (3字节)
    0xE5: 110,   # JUMP_FORWARD (3字节)
    0x37: 92,    # UNPACK_SEQUENCE (3字节)
    # 参数字节映射（小值恒等）
    0x00: 0x00, 0x01: 0x01, 0x02: 0x02,
}

# 表B新增映射（本次破解）
MAPPING_B = {
    0x98: 132,   # MAKE_FUNCTION (3字节) ✅ 高置信度
    0xFB: 90,    # STORE_NAME (3字节) ✅ 高置信度
    0xAA: 101,   # LOAD_NAME (3字节) ✅ 高置信度
    0xBF: 96,    # STORE_GLOBAL (3字节) 🔶 中高置信度
    0x91: 116,   # LOAD_GLOBAL (3字节) 🔶 中高置信度
    0x38: 89,    # BUILD_CLASS (1字节) 🔶 低置信度
}

# 合并映射
MAPPING = dict(MAPPING_A)
MAPPING.update(MAPPING_B)

# ========== 工具函数 ==========

def has_argument(std_op):
    """判断标准opcode是否有参数（3字节）或无参数（1字节）"""
    return std_op in HAS_ARG_OPS

def decode_bytecode(bytecode, mapping=None):
    """
    解码字节码，自动识别1字节/3字节指令
    返回指令列表: [(offset, encoded_op, std_op, opname, arg, length), ...]
    """
    if mapping is None:
        mapping = MAPPING
    
    instructions = []
    i = 0
    while i < len(bytecode):
        enc_op = bytecode[i]
        std_op = mapping.get(enc_op, enc_op)
        opname = PY27_OPNAME.get(std_op, f'UNKNOWN_0x{std_op:02X}')
        
        if has_argument(std_op):
            # 有参数：3字节
            if i + 2 < len(bytecode):
                arg = struct.unpack('<H', bytecode[i+1:i+3])[0]
                instructions.append((i, enc_op, std_op, opname, arg, 3))
                i += 3
            else:
                instructions.append((i, enc_op, std_op, opname, 0, 1))
                i += 1
        else:
            # 无参数：1字节
            instructions.append((i, enc_op, std_op, opname, None, 1))
            i += 1
    
    return instructions

def format_instruction(instr, names=None, varnames=None, consts=None):
    """格式化指令为可读文本"""
    offset, enc_op, std_op, opname, arg, length = instr
    
    arg_str = ''
    if arg is not None:
        if opname == 'LOAD_CONST' and consts and arg < len(consts):
            arg_str = f'  ; consts[{arg}]={consts[arg]!r}'
        elif opname in ('LOAD_NAME', 'STORE_NAME', 'LOAD_GLOBAL', 'STORE_GLOBAL',
                        'LOAD_ATTR', 'STORE_ATTR', 'IMPORT_NAME', 'IMPORT_FROM') \
                and names and arg < len(names):
            arg_str = f'  ; {names[arg]!r}'
        elif opname in ('LOAD_FAST', 'STORE_FAST', 'DELETE_FAST') \
                and varnames and arg < len(varnames):
            arg_str = f'  ; {varnames[arg]!r}'
        elif opname == 'MAKE_FUNCTION':
            flags = []
            if arg & 0x01: flags.append('defaults')
            if arg & 0x02: flags.append('closure')
            arg_str = f'  ; flags={"|".join(flags) if flags else "none"}'
        elif opname == 'CALL_FUNCTION':
            nargs = arg & 0xFF
            nkwargs = (arg >> 8) & 0xFF
            arg_str = f'  ; {nargs} args, {nkwargs} kwargs'
        elif opname in ('JUMP_FORWARD', 'FOR_ITER', 'SETUP_LOOP', 'SETUP_EXCEPT', 'SETUP_FINALLY'):
            arg_str = f'  ; → {offset + 3 + arg}'
        elif opname in ('JUMP_ABSOLUTE', 'POP_JUMP_IF_FALSE', 'POP_JUMP_IF_TRUE',
                        'JUMP_IF_FALSE', 'JUMP_IF_TRUE', 'CONTINUE_LOOP'):
            arg_str = f'  ; → {arg}'
        else:
            arg_str = f'  ; arg={arg}'
    
    return f"  [{offset:3d}] {opname:20s} {arg if arg is not None else '':>5}{arg_str}"

# ========== 主分析 ==========

def main():
    base = 'work/dream-world-connect-login-map/notes/co_code_analysis/'
    
    # 读取code objects
    with open(base + 'code_objects.json') as f:
        code_objects = json.load(f)
    obj_by_index = {obj['index']: obj for obj in code_objects}
    
    # 7个表B函数
    table_b_files = {
        'CReselectConnectMgr': ('bytecode_52_CReselectConnectMgr.bin', 52),
        'CMXNet': ('bytecode_33_CMXNet.bin', 33),
        'CConnectMgr': ('bytecode_40_CConnectMgr.bin', 40),
        'CRandomConnectMgr': ('bytecode_49_CRandomConnectMgr.bin', 49),
        'ShowConnectingDlg': ('bytecode_25_ShowConnectingDlg.bin', 25),
        'S2CServerRoleInfo': ('bytecode_26_S2CServerRoleInfo.bin', 26),
        '<module>': ('bytecode_58_<module>.bin', 58),
    }
    
    print('=' * 80)
    print('替换表B破解 — 7个类定义函数解码')
    print('=' * 80)
    
    results = {}
    
    for name, (filename, idx) in table_b_files.items():
        obj = obj_by_index.get(idx, {})
        names = obj.get('names', [])
        varnames = obj.get('varnames', [])
        consts = obj.get('consts', [])
        
        with open(base + filename, 'rb') as f:
            bytecode = f.read()
        
        instructions = decode_bytecode(bytecode)
        
        print(f"\n{'─'*70}")
        print(f"函数: {name} ({len(bytecode)}B, {len(instructions)}条指令)")
        print(f"  names ({len(names)}): {names[:10]}{'...' if len(names) > 10 else ''}")
        print(f"  varnames ({len(varnames)}): {varnames}")
        print(f"  consts ({len(consts)}): {consts[:5]}{'...' if len(consts) > 5 else ''}")
        print()
        
        for instr in instructions:
            print(format_instruction(instr, names, varnames, consts))
        
        results[name] = {
            'bytecode_size': len(bytecode),
            'instructions': [(i[0], i[1], i[2], i[3], i[4], i[5]) for i in instructions],
            'names': names,
            'varnames': varnames,
            'consts': consts,
        }
    
    # 保存结果
    output = {
        'mapping_table_b': {f'0x{k:02X}': v for k, v in sorted(MAPPING_B.items())},
        'mapping_table_b_names': {f'0x{k:02X}': PY27_OPNAME.get(v, f'0x{v:02X}') 
                                   for k, v in sorted(MAPPING_B.items())},
        'decoded_functions': results,
    }
    
    with open(base + 'table_b_cracked.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n{'='*70}")
    print("破解的表B映射:")
    for enc, std in sorted(MAPPING_B.items()):
        opname = PY27_OPNAME.get(std, f'0x{std:02X}')
        arg_type = '1字节' if std in NO_ARG_OPS else '3字节'
        print(f"  0x{enc:02X} → 0x{std:02X} ({std:3d}) {opname:20s} [{arg_type}]")
    
    print(f"\n结果已保存: {base}table_b_cracked.json")

if __name__ == '__main__':
    main()
