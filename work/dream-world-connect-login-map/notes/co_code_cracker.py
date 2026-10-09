#!/usr/bin/env python3
"""
任务A: 破解 co_code 自定义编码，完整反编译登录脚本
详细记录每一步分析过程

目标: script\login\netserver.py (entry 516)
当前状态: marshal 树已恢复，但 co_code 有第二层自定义编码
"""

import struct
import sys
import os
from collections import Counter

# ============================================================
# Python 2.7 Marshal 解析器（修复版，正确处理引用）
# ============================================================

FLAG_REF = 0x80

class MarshalReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0
        self.refs = []  # 引用表
    
    def read(self, n):
        if self.pos + n > len(self.data):
            raise EOFError(f"Unexpected end at {self.pos}+{n} > {len(self.data)}")
        result = self.data[self.pos:self.pos+n]
        self.pos += n
        return result
    
    def read_byte(self):
        return self.read(1)[0]
    
    def read_int32(self):
        return struct.unpack('<i', self.read(4))[0]
    
    def read_uint32(self):
        return struct.unpack('<I', self.read(4))[0]
    
    def read_int64(self):
        return struct.unpack('<q', self.read(8))[0]
    
    def read_double(self):
        return struct.unpack('<d', self.read(8))[0]
    
    def read_object(self):
        """读取一个 marshal 对象"""
        if self.pos >= len(self.data):
            raise EOFError("Unexpected end of data")
        
        type_byte = self.read_byte()
        has_ref = bool(type_byte & FLAG_REF)
        type_char = chr(type_byte & ~FLAG_REF)
        
        # 先读取对象，然后如果需要则加入引用表
        obj = self._read_by_type(type_char)
        
        if has_ref:
            self.refs.append(obj)
        
        return obj
    
    def _read_by_type(self, type_char):
        """根据类型读取对象"""
        if type_char == '0':  # NULL
            return None
        
        elif type_char == 'N':  # None
            return None
        
        elif type_char == 'F':  # False
            return False
        
        elif type_char == 'T':  # True
            return True
        
        elif type_char == 'S':  # StopIteration
            return StopIteration
        
        elif type_char == '.':  # Ellipsis
            return Ellipsis
        
        elif type_char == 'i':  # int32
            return self.read_int32()
        
        elif type_char == 'I':  # int64
            return self.read_int64()
        
        elif type_char == 'f':  # float (string format)
            length = self.read_byte()
            s = self.read(length).decode('ascii')
            return float(s)
        
        elif type_char == 'g':  # binary float
            return self.read_double()
        
        elif type_char == 'l':  # long
            n = self.read_int32()
            sign = 1 if n >= 0 else -1
            n = abs(n)
            val = 0
            for i in range(n):
                d = struct.unpack('<H', self.read(2))[0]
                val |= d << (i * 15)
            return sign * val
        
        elif type_char == 's':  # string (bytes)
            length = self.read_int32()
            return self.read(length)
        
        elif type_char == 't':  # interned string
            length = self.read_int32()
            return self.read(length).decode('utf-8', errors='replace')
        
        elif type_char == 'R':  # string ref (unused in py2)
            ref_idx = self.read_int32()
            return self.refs[ref_idx]
        
        elif type_char == '(':  # tuple
            n = self.read_int32()
            items = []
            for _ in range(n):
                items.append(self.read_object())
            return tuple(items)
        
        elif type_char == '[':  # list
            n = self.read_int32()
            items = []
            for _ in range(n):
                items.append(self.read_object())
            return items
        
        elif type_char == '{':  # dict
            obj = {}
            while True:
                # 检查是否结束（NULL标记）
                save_pos = self.pos
                type_byte = self.data[self.pos]
                if type_byte == ord('0'):  # NULL
                    self.pos += 1
                    break
                key = self.read_object()
                value = self.read_object()
                obj[key] = value
            return obj
        
        elif type_char == 'c':  # code object
            return self._read_code()
        
        elif type_char == 'u':  # unicode
            length = self.read_int32()
            return self.read(length).decode('utf-8', errors='replace')
        
        elif type_char == 'r':  # ref
            ref_idx = self.read_int32()
            return self.refs[ref_idx]
        
        elif type_char == '<':  # set
            n = self.read_int32()
            items = []
            for _ in range(n):
                items.append(self.read_object())
            return set(items)
        
        elif type_char == '>':  # frozenset
            n = self.read_int32()
            items = []
            for _ in range(n):
                items.append(self.read_object())
            return frozenset(items)
        
        else:
            raise ValueError(f"Unknown type: {type_char!r} (0x{ord(type_char):02x}) at pos {self.pos-1}")
    
    def _read_code(self):
        """读取 Python 2.7 code object"""
        code = {}
        
        code['argcount'] = self.read_int32()
        code['nlocals'] = self.read_int32()
        code['stacksize'] = self.read_int32()
        code['flags'] = self.read_int32()
        
        # co_code (bytecode) - 作为 string 对象读取
        code['co_code'] = self.read_object()
        
        # consts
        code['consts'] = self.read_object()
        # names
        code['names'] = self.read_object()
        # varnames
        code['varnames'] = self.read_object()
        # freevars
        code['freevars'] = self.read_object()
        # cellvars
        code['cellvars'] = self.read_object()
        
        # filename
        code['filename'] = self.read_object()
        # name
        code['name'] = self.read_object()
        
        # firstlineno
        code['firstlineno'] = self.read_int32()
        
        # lnotab
        code['lnotab'] = self.read_object()
        
        return code


# ============================================================
# 分析工具
# ============================================================

def find_all_code_objects(obj, path="root", results=None):
    """递归查找所有 code object"""
    if results is None:
        results = []
    
    if isinstance(obj, dict) and 'co_code' in obj:
        results.append((path, obj))
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            find_all_code_objects(value, f"{path}.{key}", results)
    elif isinstance(obj, (tuple, list)):
        for i, item in enumerate(obj):
            find_all_code_objects(item, f"{path}[{i}]", results)
    
    return results


def analyze_bytecode(co_code, name="unknown"):
    """分析字节码特征"""
    if isinstance(co_code, str):
        co_code = co_code.encode('latin-1')
    elif not isinstance(co_code, bytes):
        co_code = str(co_code).encode('latin-1')
    
    print(f"\n{'='*60}")
    print(f"分析代码对象: {name}")
    print(f"字节码长度: {len(co_code)}")
    print(f"前64字节: {co_code[:64].hex()}")
    
    # Python 2.7 标准 opcode 集合
    # 来源: Python 2.7 opcode.py
    standard_opcodes = {
        0x01: 'POP_TOP', 0x02: 'ROT_TWO', 0x03: 'ROT_THREE', 0x04: 'DUP_TOP',
        0x05: 'ROT_FOUR', 0x09: 'NOP', 0x0a: 'UNARY_POSITIVE', 0x0b: 'UNARY_NEGATIVE',
        0x0c: 'UNARY_NOT', 0x0f: 'UNARY_INVERT', 0x10: 'BINARY_POWER', 0x11: 'BINARY_MULTIPLY',
        0x12: 'BINARY_DIVIDE', 0x13: 'BINARY_MODULO', 0x14: 'BINARY_ADD', 0x15: 'BINARY_SUBTRACT',
        0x16: 'BINARY_SUBSCR', 0x17: 'BINARY_FLOOR_DIVIDE', 0x18: 'BINARY_TRUE_DIVIDE',
        0x19: 'INPLACE_FLOOR_DIVIDE', 0x1a: 'INPLACE_TRUE_DIVIDE', 0x1b: 'SLICE+0',
        0x1c: 'SLICE+1', 0x1d: 'SLICE+2', 0x1e: 'SLICE+3', 0x1f: 'STORE_SLICE+0',
        0x20: 'STORE_SLICE+1', 0x21: 'STORE_SLICE+2', 0x22: 'STORE_SLICE+3',
        0x23: 'DELETE_SLICE+0', 0x24: 'DELETE_SLICE+1', 0x25: 'DELETE_SLICE+2',
        0x26: 'DELETE_SLICE+3', 0x28: 'BINARY_LSHIFT', 0x29: 'BINARY_RSHIFT',
        0x2a: 'BINARY_AND', 0x2b: 'BINARY_XOR', 0x2c: 'BINARY_OR',
        0x2d: 'INPLACE_POWER', 0x2e: 'GET_ITER', 0x2f: 'PRINT_EXPR',
        0x30: 'PRINT_ITEM', 0x31: 'PRINT_NEWLINE', 0x32: 'PRINT_ITEM_TO',
        0x33: 'PRINT_NEWLINE_TO', 0x34: 'INPLACE_LSHIFT', 0x35: 'INPLACE_RSHIFT',
        0x36: 'INPLACE_AND', 0x37: 'INPLACE_XOR', 0x38: 'INPLACE_OR',
        0x39: 'BREAK_LOOP', 0x3a: 'WITH_CLEANUP', 0x3b: 'LOAD_LOCALS',
        0x3c: 'RETURN_VALUE', 0x3d: 'IMPORT_STAR', 0x3e: 'EXEC_STMT',
        0x3f: 'YIELD_VALUE', 0x40: 'POP_BLOCK', 0x41: 'END_FINALLY',
        0x42: 'BUILD_CLASS', 0x43: 'STORE_NAME', 0x44: 'DELETE_NAME',
        0x45: 'UNPACK_SEQUENCE', 0x46: 'FOR_ITER', 0x47: 'LIST_APPEND',
        0x48: 'STORE_ATTR', 0x49: 'DELETE_ATTR', 0x4a: 'STORE_GLOBAL',
        0x4b: 'DELETE_GLOBAL', 0x4c: 'DUP_TOPX', 0x4d: 'LOAD_CONST',
        0x4e: 'LOAD_NAME', 0x4f: 'BUILD_TUPLE', 0x50: 'BUILD_LIST',
        0x51: 'BUILD_SET', 0x52: 'BUILD_MAP', 0x53: 'LOAD_ATTR',
        0x54: 'COMPARE_OP', 0x55: 'IMPORT_NAME', 0x56: 'IMPORT_FROM',
        0x57: 'JUMP_FORWARD', 0x58: 'JUMP_IF_FALSE_OR_POP', 0x59: 'JUMP_IF_TRUE_OR_POP',
        0x5a: 'JUMP_ABSOLUTE', 0x5b: 'POP_JUMP_IF_FALSE', 0x5c: 'POP_JUMP_IF_TRUE',
        0x5d: 'LOAD_GLOBAL', 0x5e: 'CONTINUE_LOOP', 0x5f: 'SETUP_LOOP',
        0x60: 'SETUP_EXCEPT', 0x61: 'SETUP_FINALLY', 0x62: 'LOAD_FAST',
        0x63: 'STORE_FAST', 0x64: 'DELETE_FAST', 0x65: 'RAISE_VARARGS',
        0x66: 'CALL_FUNCTION', 0x67: 'MAKE_FUNCTION', 0x68: 'BUILD_SLICE',
        0x69: 'MAKE_CLOSURE', 0x6a: 'LOAD_CLOSURE', 0x6b: 'LOAD_DEREF',
        0x6c: 'STORE_DEREF', 0x6d: 'DELETE_DEREF', 0x6e: 'CALL_FUNCTION_VAR',
        0x6f: 'CALL_FUNCTION_KW', 0x70: 'CALL_FUNCTION_VAR_KW', 0x71: 'SETUP_WITH',
        0x72: 'EXTENDED_ARG', 0x73: 'SET_ADD', 0x74: 'MAP_ADD',
    }
    
    # 统计字节分布
    byte_counts = Counter(co_code)
    print(f"\n字节值分布 (前20个最常见):")
    for byte, count in byte_counts.most_common(20):
        opcode_name = standard_opcodes.get(byte, '???')
        print(f"  0x{byte:02X} ({byte:3d}): {count:4d} 次  [{opcode_name}]")
    
    # 检查非标准 opcode
    non_standard = [(b, c) for b, c in byte_counts.items() if b not in standard_opcodes]
    print(f"\n非标准 opcode: {len(non_standard)} 种")
    if non_standard:
        print(f"  详细: {[(hex(b), c) for b, c in sorted(non_standard)[:20]]}")
    
    # 分析可能的编码模式
    print(f"\n编码分析:")
    
    # 检查是否是简单的异或编码
    # 常见模式: 每个字节与固定值异或
    for xor_key in range(256):
        decoded = bytes(b ^ xor_key for b in co_code)
        standard_count = sum(1 for b in decoded if b in standard_opcodes)
        ratio = standard_count / len(decoded)
        if ratio > 0.8:  # 超过80%是标准opcode
            print(f"  可能的XOR密钥: 0x{xor_key:02X} (标准opcode比例: {ratio:.1%})")
    
    # 检查是否是字节替换（S盒）
    # 如果某些字节值完全没有出现，可能是替换编码
    missing_bytes = [b for b in range(256) if b not in byte_counts]
    print(f"  未出现的字节值: {len(missing_bytes)} 个")
    if len(missing_bytes) > 100:
        print(f"    前30个: {[hex(b) for b in missing_bytes[:30]]}")
    
    # 检查是否有重复模式（可能是加密的）
    # 计算字节熵
    import math
    entropy = 0
    for count in byte_counts.values():
        p = count / len(co_code)
        entropy -= p * math.log2(p)
    print(f"  字节熵: {entropy:.2f} (最大8.0，越高越随机)")
    
    return {
        'length': len(co_code),
        'unique_bytes': len(byte_counts),
        'non_standard_count': len(non_standard),
        'entropy': entropy,
        'byte_counts': byte_counts,
    }


def try_decode_with_transform(co_code, transform_func, name="transform"):
    """尝试用特定转换解码字节码"""
    if isinstance(co_code, str):
        co_code = co_code.encode('latin-1')
    
    try:
        decoded = transform_func(co_code)
        # 检查解码后的字节码是否合理
        standard_opcodes = set([
            0x01, 0x02, 0x03, 0x04, 0x05, 0x09, 0x0a, 0x0b, 0x0c, 0x0f,
            0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
            0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20, 0x21, 0x22, 0x23,
            0x28, 0x29, 0x2a, 0x2b, 0x2c, 0x2d, 0x2e, 0x2f,
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38,
            0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e, 0x3f, 0x40, 0x41,
            0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4a,
            0x4b, 0x4c, 0x4d, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x53,
            0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5a, 0x5b, 0x5c,
            0x5d, 0x5e, 0x5f, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65,
            0x66, 0x67, 0x68, 0x69, 0x6a, 0x6b, 0x6c, 0x6d, 0x6e,
            0x6f, 0x70, 0x71, 0x72, 0x73, 0x74,
        ])
        
        standard_count = sum(1 for b in decoded if b in standard_opcodes)
        ratio = standard_count / len(decoded) if decoded else 0
        
        return decoded, ratio
    except Exception as e:
        return None, 0


# ============================================================
# 主分析流程
# ============================================================

def main():
    print("=" * 70)
    print("任务A: 破解 co_code 自定义编码")
    print("目标: script\login\netserver.py (entry 516)")
    print("=" * 70)
    
    # 读取数据
    data_path = 'work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin'
    with open(data_path, 'rb') as f:
        data = f.read()
    
    print(f"\n[步骤1] 加载 marshal 数据")
    print(f"  文件: {data_path}")
    print(f"  大小: {len(data)} 字节")
    print(f"  前16字节: {data[:16].hex()}")
    
    # 解析 marshal
    print(f"\n[步骤2] 解析 Python 2.7 marshal 树")
    reader = MarshalReader(data)
    
    try:
        root = reader.read_object()
        print(f"  解析成功!")
        print(f"  根对象类型: {type(root).__name__}")
        print(f"  读取位置: {reader.pos}/{len(data)} 字节")
        print(f"  引用表大小: {len(reader.refs)}")
    except Exception as e:
        print(f"  ❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 查找所有 code object
    print(f"\n[步骤3] 查找所有 code object")
    code_objects = find_all_code_objects(root)
    print(f"  找到 {len(code_objects)} 个 code object")
    
    # 按名称排序
    code_objects.sort(key=lambda x: x[1].get('name', ''))
    
    for i, (path, code) in enumerate(code_objects):
        name = code.get('name', '?')
        filename = code.get('filename', '?')
        co_code = code.get('co_code', b'')
        if isinstance(co_code, str):
            co_code_len = len(co_code)
        else:
            co_code_len = len(co_code)
        print(f"  [{i+1:2d}] {name:<30} ({co_code_len:>4} 字节) - {filename}")
    
    # 详细分析每个 code object 的字节码
    print(f"\n[步骤4] 分析 co_code 字节码特征")
    
    analyses = []
    for path, code in code_objects:
        name = code.get('name', 'unknown')
        result = analyze_bytecode(code.get('co_code', b''), name)
        analyses.append((name, code, result))
    
    # 查找可能的编码模式
    print(f"\n[步骤5] 尝试识别编码模式")
    
    # 收集所有字节码
    all_bytecode = b''
    for name, code, result in analyses:
        co_code = code.get('co_code', b'')
        if isinstance(co_code, str):
            co_code = co_code.encode('latin-1')
        all_bytecode += co_code
    
    print(f"  总字节码长度: {len(all_bytecode)}")
    
    # 分析整体特征
    overall = analyze_bytecode(all_bytecode, "ALL_COMBINED")
    
    # 尝试各种转换
    print(f"\n[步骤6] 尝试各种解码转换")
    
    transforms = {
        'identity': lambda x: x,
        'xor_0xFF': lambda x: bytes(b ^ 0xFF for b in x),
        'xor_0xAA': lambda x: bytes(b ^ 0xAA for b in x),
        'xor_0x55': lambda x: bytes(b ^ 0x55 for b in x),
        'not': lambda x: bytes(~b & 0xFF for b in x),
        'add_1': lambda x: bytes((b + 1) & 0xFF for b in x),
        'sub_1': lambda x: bytes((b - 1) & 0xFF for b in x),
        'reverse_bits': lambda x: bytes(int(f'{b:08b}'[::-1], 2) for b in x),
        'rotate_left_1': lambda x: bytes(((b << 1) | (b >> 7)) & 0xFF for b in x),
        'rotate_right_1': lambda x: bytes(((b >> 1) | (b << 7)) & 0xFF for b in x),
    }
    
    for name, func in transforms.items():
        decoded, ratio = try_decode_with_transform(all_bytecode, func, name)
        if ratio > 0.5:
            print(f"  {name:<20}: 标准opcode比例 {ratio:.1%} ✅ 可能正确!")
        else:
            print(f"  {name:<20}: 标准opcode比例 {ratio:.1%}")
    
    # 保存分析结果
    print(f"\n[步骤7] 保存分析结果")
    output_dir = 'work/dream-world-connect-login-map/notes/co_code_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存所有 code object 的信息
    import json
    code_info = []
    for name, code, result in analyses:
        co_code = code.get('co_code', b'')
        if isinstance(co_code, str):
            co_code = co_code.encode('latin-1')
        
        info = {
            'name': name,
            'filename': code.get('filename', ''),
            'argcount': code.get('argcount', 0),
            'nlocals': code.get('nlocals', 0),
            'stacksize': code.get('stacksize', 0),
            'flags': code.get('flags', 0),
            'firstlineno': code.get('firstlineno', 0),
            'co_code_length': len(co_code),
            'co_code_hex': co_code.hex(),
            'names': list(code.get('names', [])) if isinstance(code.get('names'), (tuple, list)) else [],
            'varnames': list(code.get('varnames', [])) if isinstance(code.get('varnames'), (tuple, list)) else [],
            'consts_summary': [type(c).__name__ for c in code.get('consts', [])] if isinstance(code.get('consts'), (tuple, list)) else [],
            'analysis': {
                'unique_bytes': result['unique_bytes'],
                'non_standard_count': result['non_standard_count'],
                'entropy': result['entropy'],
            }
        }
        code_info.append(info)
    
    with open(os.path.join(output_dir, 'code_objects.json'), 'w', encoding='utf-8') as f:
        json.dump(code_info, f, indent=2, ensure_ascii=False)
    
    print(f"  已保存: {output_dir}/code_objects.json")
    
    # 保存原始字节码用于进一步分析
    for i, (name, code, result) in enumerate(analyses):
        co_code = code.get('co_code', b'')
        if isinstance(co_code, str):
            co_code = co_code.encode('latin-1')
        
        safe_name = name.replace('/', '_').replace('\\', '_')[:50]
        with open(os.path.join(output_dir, f'bytecode_{i:02d}_{safe_name}.bin'), 'wb') as f:
            f.write(co_code)
    
    print(f"  已保存 {len(analyses)} 个字节码文件")
    
    # 生成分析报告
    report = []
    report.append("# Co_code 自定义编码分析报告")
    report.append(f"\n生成时间: 2026-10-10")
    report.append(f"\n目标: script\\login\\netserver.py (entry 516)")
    report.append(f"\n## 概述")
    report.append(f"\n- 总 code object 数量: {len(code_objects)}")
    report.append(f"- 总字节码长度: {len(all_bytecode)}")
    report.append(f"- 平均字节熵: {sum(r['entropy'] for _, _, r in analyses) / len(analyses):.2f}")
    
    report.append(f"\n## Code Object 列表")
    for i, (name, code, result) in enumerate(analyses):
        report.append(f"\n### {i+1}. {name}")
        report.append(f"- 字节码长度: {result['length']}")
        report.append(f"- 唯一字节值: {result['unique_bytes']}")
        report.append(f"- 非标准opcode: {result['non_standard_count']} 种")
        report.append(f"- 字节熵: {result['entropy']:.2f}")
    
    with open(os.path.join(output_dir, 'analysis_report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"  已保存: {output_dir}/analysis_report.md")
    
    print(f"\n{'='*70}")
    print("分析完成!")
    print(f"结果保存在: {output_dir}/")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
