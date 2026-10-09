#!/usr/bin/env python3
"""
任务A: 破解 co_code 自定义编码 - 分析工具
基于成功解码的 marshal 数据，分析字节码特征

详细记录每一步分析过程
"""

import struct
import sys
import os
import json
import math
from collections import Counter

# ============================================================
# 成功的 Marshal 解析器（基于 decode_entry516.py）
# ============================================================

class MarshalReader:
    """Small Python 2.7 marshal reader with interned-string support."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.interned_strings = []
        self.code_objects = []
        self.strings = []

    def take(self, size: int) -> bytes:
        end = self.pos + size
        if end > len(self.data):
            raise ValueError(f"marshal truncated at 0x{self.pos:x}, need {size} bytes")
        result = self.data[self.pos:end]
        self.pos = end
        return result

    def byte(self) -> int:
        return self.take(1)[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def string_bytes(self, length: int) -> bytes:
        value = self.take(length)
        self.strings.append(value)
        return value

    def read(self):
        type_code = self.byte()

        if type_code == ord("0"):
            value = None
        elif type_code == ord("N"):
            value = None
        elif type_code == ord("F"):
            value = False
        elif type_code == ord("T"):
            value = True
        elif type_code == ord("S"):
            value = StopIteration
        elif type_code == ord("i"):
            value = self.i32()
        elif type_code == ord("I"):
            value = struct.unpack("<q", self.take(8))[0]
        elif type_code == ord("f"):
            value = float(self.take(self.u32()).decode("ascii"))
        elif type_code == ord("g"):
            value = struct.unpack("<d", self.take(8))[0]
        elif type_code in (ord("s"), ord("t"), ord("a"), ord("A")):
            value = self.string_bytes(self.u32())
            if type_code == ord("t"):
                self.interned_strings.append(value)
        elif type_code == ord("u"):
            value = self.take(self.u32()).decode("utf-8", "replace")
        elif type_code == ord("R"):
            index = self.u32()
            try:
                value = self.interned_strings[index]
            except IndexError as exc:
                raise ValueError(f"bad marshal string reference {index}") from exc
        elif type_code in (ord("("), ord("["), ord("<")):
            length = self.u32()
            items = [self.read() for _ in range(length)]
            value = tuple(items) if type_code == ord("(") else items
        elif type_code == ord("{"):
            value = {}
            while True:
                key = self.read()
                if key is None:
                    break
                value[key] = self.read()
        elif type_code == ord("c"):
            value = self.read_code_object()
        else:
            raise ValueError(
                f"unsupported marshal type 0x{type_code:02x} at 0x{self.pos - 1:x}"
            )
        return value

    def read_code_object(self):
        start = self.pos - 1
        argcount = self.i32()
        nlocals = self.i32()
        stacksize = self.i32()
        flags = self.i32()
        code = self.read()
        consts = self.read()
        names = self.read()
        varnames = self.read()
        freevars = self.read()
        cellvars = self.read()
        filename = self.read()
        name = self.read()
        firstlineno = self.i32()
        lnotab = self.read()
        
        # 确保 code 是 bytes
        if isinstance(code, str):
            code = code.encode('latin-1')
        elif not isinstance(code, (bytes, bytearray)):
            code = str(code).encode('latin-1')
        
        record = {
            "offset": start,
            "argcount": argcount,
            "nlocals": nlocals,
            "stacksize": stacksize,
            "flags": flags,
            "co_code": bytes(code),
            "code_len": len(code),
            "consts": consts,
            "names": names,
            "varnames": varnames,
            "freevars": freevars,
            "cellvars": cellvars,
            "filename": filename,
            "name": name,
            "firstlineno": firstlineno,
            "lnotab": lnotab,
        }
        self.code_objects.append(record)
        return record


# ============================================================
# Python 2.7 Opcode 表
# ============================================================

# 完整的 Python 2.7 opcode 映射
PYTHON27_OPCODES = {
    0x01: ('POP_TOP', 0), 0x02: ('ROT_TWO', 0), 0x03: ('ROT_THREE', 0),
    0x04: ('DUP_TOP', 0), 0x05: ('ROT_FOUR', 0), 0x09: ('NOP', 0),
    0x0a: ('UNARY_POSITIVE', 0), 0x0b: ('UNARY_NEGATIVE', 0),
    0x0c: ('UNARY_NOT', 0), 0x0f: ('UNARY_INVERT', 0),
    0x10: ('BINARY_POWER', 0), 0x11: ('BINARY_MULTIPLY', 0),
    0x12: ('BINARY_DIVIDE', 0), 0x13: ('BINARY_MODULO', 0),
    0x14: ('BINARY_ADD', 0), 0x15: ('BINARY_SUBTRACT', 0),
    0x16: ('BINARY_SUBSCR', 0), 0x17: ('BINARY_FLOOR_DIVIDE', 0),
    0x18: ('BINARY_TRUE_DIVIDE', 0), 0x19: ('INPLACE_FLOOR_DIVIDE', 0),
    0x1a: ('INPLACE_TRUE_DIVIDE', 0),
    0x1b: ('SLICE+0', 0), 0x1c: ('SLICE+1', 0), 0x1d: ('SLICE+2', 0), 0x1e: ('SLICE+3', 0),
    0x1f: ('STORE_SLICE+0', 0), 0x20: ('STORE_SLICE+1', 0),
    0x21: ('STORE_SLICE+2', 0), 0x22: ('STORE_SLICE+3', 0),
    0x23: ('DELETE_SLICE+0', 0), 0x24: ('DELETE_SLICE+1', 0),
    0x25: ('DELETE_SLICE+2', 0), 0x26: ('DELETE_SLICE+3', 0),
    0x28: ('BINARY_LSHIFT', 0), 0x29: ('BINARY_RSHIFT', 0),
    0x2a: ('BINARY_AND', 0), 0x2b: ('BINARY_XOR', 0), 0x2c: ('BINARY_OR', 0),
    0x2d: ('INPLACE_POWER', 0), 0x2e: ('GET_ITER', 0),
    0x2f: ('PRINT_EXPR', 0), 0x30: ('PRINT_ITEM', 0), 0x31: ('PRINT_NEWLINE', 0),
    0x32: ('PRINT_ITEM_TO', 0), 0x33: ('PRINT_NEWLINE_TO', 0),
    0x34: ('INPLACE_LSHIFT', 0), 0x35: ('INPLACE_RSHIFT', 0),
    0x36: ('INPLACE_AND', 0), 0x37: ('INPLACE_XOR', 0), 0x38: ('INPLACE_OR', 0),
    0x39: ('BREAK_LOOP', 0), 0x3a: ('WITH_CLEANUP', 0), 0x3b: ('LOAD_LOCALS', 0),
    0x3c: ('RETURN_VALUE', 0), 0x3d: ('IMPORT_STAR', 0), 0x3e: ('EXEC_STMT', 0),
    0x3f: ('YIELD_VALUE', 0), 0x40: ('POP_BLOCK', 0), 0x41: ('END_FINALLY', 0),
    0x42: ('BUILD_CLASS', 0), 0x43: ('STORE_NAME', 2), 0x44: ('DELETE_NAME', 2),
    0x45: ('UNPACK_SEQUENCE', 2), 0x46: ('FOR_ITER', 2), 0x47: ('LIST_APPEND', 2),
    0x48: ('STORE_ATTR', 2), 0x49: ('DELETE_ATTR', 2), 0x4a: ('STORE_GLOBAL', 2),
    0x4b: ('DELETE_GLOBAL', 2), 0x4c: ('DUP_TOPX', 2), 0x4d: ('LOAD_CONST', 2),
    0x4e: ('LOAD_NAME', 2), 0x4f: ('BUILD_TUPLE', 2), 0x50: ('BUILD_LIST', 2),
    0x51: ('BUILD_SET', 2), 0x52: ('BUILD_MAP', 2), 0x53: ('LOAD_ATTR', 2),
    0x54: ('COMPARE_OP', 2), 0x55: ('IMPORT_NAME', 2), 0x56: ('IMPORT_FROM', 2),
    0x57: ('JUMP_FORWARD', 2), 0x58: ('JUMP_IF_FALSE_OR_POP', 2),
    0x59: ('JUMP_IF_TRUE_OR_POP', 2), 0x5a: ('JUMP_ABSOLUTE', 2),
    0x5b: ('POP_JUMP_IF_FALSE', 2), 0x5c: ('POP_JUMP_IF_TRUE', 2),
    0x5d: ('LOAD_GLOBAL', 2), 0x5e: ('CONTINUE_LOOP', 2), 0x5f: ('SETUP_LOOP', 2),
    0x60: ('SETUP_EXCEPT', 2), 0x61: ('SETUP_FINALLY', 2),
    0x62: ('LOAD_FAST', 2), 0x63: ('STORE_FAST', 2), 0x64: ('DELETE_FAST', 2),
    0x65: ('RAISE_VARARGS', 2), 0x66: ('CALL_FUNCTION', 2),
    0x67: ('MAKE_FUNCTION', 2), 0x68: ('BUILD_SLICE', 2),
    0x69: ('MAKE_CLOSURE', 2), 0x6a: ('LOAD_CLOSURE', 2), 0x6b: ('LOAD_DEREF', 2),
    0x6c: ('STORE_DEREF', 2), 0x6d: ('DELETE_DEREF', 2),
    0x6e: ('CALL_FUNCTION_VAR', 2), 0x6f: ('CALL_FUNCTION_KW', 2),
    0x70: ('CALL_FUNCTION_VAR_KW', 2), 0x71: ('SETUP_WITH', 2),
    0x72: ('EXTENDED_ARG', 2), 0x73: ('SET_ADD', 2), 0x74: ('MAP_ADD', 2),
}

STANDARD_OPCODE_SET = set(PYTHON27_OPCODES.keys())


# ============================================================
# 字节码分析工具
# ============================================================

def analyze_bytecode(co_code: bytes, name: str = "unknown") -> dict:
    """详细分析字节码特征"""
    print(f"\n{'='*60}")
    print(f"分析代码对象: {name}")
    print(f"字节码长度: {len(co_code)}")
    print(f"前64字节: {co_code[:64].hex()}")
    
    # 统计字节分布
    byte_counts = Counter(co_code)
    print(f"\n字节值分布 (前20个最常见):")
    for byte, count in byte_counts.most_common(20):
        opcode_info = PYTHON27_OPCODES.get(byte)
        opcode_name = opcode_info[0] if opcode_info else '???'
        has_arg = ' (有参数)' if opcode_info and opcode_info[1] > 0 else ''
        print(f"  0x{byte:02X} ({byte:3d}): {count:4d} 次  [{opcode_name}]{has_arg}")
    
    # 检查非标准 opcode
    non_standard = [(b, c) for b, c in byte_counts.items() if b not in STANDARD_OPCODE_SET]
    standard = [(b, c) for b, c in byte_counts.items() if b in STANDARD_OPCODE_SET]
    
    print(f"\n标准 opcode: {len(standard)} 种, {sum(c for _, c in standard)} 个")
    print(f"非标准 opcode: {len(non_standard)} 种, {sum(c for _, c in non_standard)} 个")
    
    if non_standard:
        print(f"非标准 opcode 详细 (前20个):")
        for b, c in sorted(non_standard)[:20]:
            print(f"  0x{b:02X} ({b:3d}): {c} 次")
    
    # 计算熵
    entropy = 0
    for count in byte_counts.values():
        p = count / len(co_code)
        entropy -= p * math.log2(p)
    
    print(f"\n字节熵: {entropy:.2f} (最大8.0)")
    
    # 分析编码模式
    print(f"\n编码模式分析:")
    
    # 1. 检查简单XOR
    best_xor = None
    best_xor_ratio = 0
    for xor_key in range(1, 256):
        decoded = bytes(b ^ xor_key for b in co_code)
        standard_count = sum(1 for b in decoded if b in STANDARD_OPCODE_SET)
        ratio = standard_count / len(decoded)
        if ratio > best_xor_ratio:
            best_xor_ratio = ratio
            best_xor = xor_key
    
    if best_xor_ratio > 0.7:
        print(f"  ✅ 发现可能的XOR编码: key=0x{best_xor:02X}, 标准opcode比例={best_xor_ratio:.1%}")
    else:
        print(f"  ❌ 未发现简单XOR编码 (最佳: key=0x{best_xor:02X}, 比例={best_xor_ratio:.1%})")
    
    # 2. 检查字节替换（S盒）
    # 如果是一对一替换，频率分布应该相似
    print(f"  唯一字节值数量: {len(byte_counts)} (256表示完全随机)")
    
    # 3. 检查是否有周期性
    if len(co_code) > 16:
        # 检查是否每N个字节重复模式
        for period in [2, 3, 4, 8, 16]:
            matches = 0
            total = 0
            for i in range(len(co_code) - period):
                if co_code[i] == co_code[i + period]:
                    matches += 1
                total += 1
            if total > 0:
                ratio = matches / total
                if ratio > 0.3:
                    print(f"  周期{period}: 重复率 {ratio:.1%}")
    
    # 4. 分析 opcode 序列模式
    # 提取看起来像 opcode 的位置（每3字节一个，因为多数opcode有2字节参数）
    print(f"\n可能的opcode序列 (假设3字节一条指令):")
    for i in range(0, min(len(co_code), 60), 3):
        chunk = co_code[i:i+3]
        op = chunk[0]
        arg = struct.unpack('<H', chunk[1:3])[0] if len(chunk) >= 3 else 0
        opcode_info = PYTHON27_OPCODES.get(op)
        opcode_name = opcode_info[0] if opcode_info else f'???(0x{op:02X})'
        print(f"  [{i:4d}] {op:02X} {chunk[1:3].hex() if len(chunk)>=3 else '??'}  {opcode_name:<20} arg={arg}")
    
    return {
        'name': name,
        'length': len(co_code),
        'unique_bytes': len(byte_counts),
        'standard_count': len(standard),
        'non_standard_count': len(non_standard),
        'entropy': entropy,
        'best_xor': best_xor,
        'best_xor_ratio': best_xor_ratio,
        'byte_counts': dict(byte_counts),
        'non_standard': [(b, c) for b, c in non_standard],
    }


def try_disassemble(co_code: bytes, name: str = "unknown"):
    """尝试反汇编字节码"""
    print(f"\n{'─'*60}")
    print(f"尝试反汇编: {name}")
    print(f"{'─'*60}")
    
    pos = 0
    instructions = []
    
    while pos < len(co_code):
        op = co_code[pos]
        opcode_info = PYTHON27_OPCODES.get(op)
        
        if opcode_info:
            op_name, arg_size = opcode_info
            if arg_size > 0 and pos + 1 + arg_size <= len(co_code):
                arg_bytes = co_code[pos+1:pos+1+arg_size]
                arg = struct.unpack('<H', arg_bytes)[0] if arg_size == 2 else arg_bytes[0]
                instr = f"{op_name} {arg}"
                next_pos = pos + 1 + arg_size
            else:
                instr = op_name
                next_pos = pos + 1
        else:
            instr = f"??? (0x{op:02X})"
            next_pos = pos + 1
        
        instructions.append((pos, instr))
        print(f"  {pos:4d}: {instr}")
        pos = next_pos
    
    return instructions


# ============================================================
# 主分析流程
# ============================================================

def main():
    print("=" * 70)
    print("任务A: 破解 co_code 自定义编码 - 详细分析")
    print("目标: script\\login\\netserver.py (entry 516)")
    print("时间: 2026-10-10")
    print("=" * 70)
    
    # ================================================================
    # 步骤1: 加载 marshal 数据
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤1] 加载 marshal 数据")
    print(f"{'#'*70}")
    
    data_path = 'work/dream-world-connect-login-map/notes/decoder-artifacts/entry516-five-xor-marshal.bin'
    with open(data_path, 'rb') as f:
        data = f.read()
    
    print(f"  文件: {data_path}")
    print(f"  大小: {len(data)} 字节")
    print(f"  SHA256: (计算中...)")
    
    import hashlib
    sha = hashlib.sha256(data).hexdigest()
    print(f"  SHA256: {sha}")
    
    # ================================================================
    # 步骤2: 解析 marshal 树
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤2] 解析 Python 2.7 marshal 树")
    print(f"{'#'*70}")
    
    reader = MarshalReader(data)
    root = reader.read()
    
    print(f"  ✅ 解析成功!")
    print(f"  根对象类型: {type(root).__name__}")
    print(f"  读取位置: {reader.pos}/{len(data)} 字节")
    print(f"  Code object 数量: {len(reader.code_objects)}")
    print(f"  Interned strings: {len(reader.interned_strings)}")
    
    # ================================================================
    # 步骤3: 列出所有 code object
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤3] Code Object 清单")
    print(f"{'#'*70}")
    
    code_objects = reader.code_objects
    for i, code in enumerate(code_objects):
        name = code.get('name', b'')
        if isinstance(name, bytes):
            name = name.decode('utf-8', errors='replace')
        filename = code.get('filename', b'')
        if isinstance(filename, bytes):
            filename = filename.decode('utf-8', errors='replace')
        co_code = code.get('co_code', b'')
        
        print(f"  [{i+1:2d}] {name:<30} | {len(co_code):>4} 字节 | {filename}")
    
    # ================================================================
    # 步骤4: 详细分析每个 code object 的字节码
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤4] 字节码特征分析")
    print(f"{'#'*70}")
    
    analyses = []
    for i, code in enumerate(code_objects):
        name = code.get('name', b'')
        if isinstance(name, bytes):
            name = name.decode('utf-8', errors='replace')
        
        result = analyze_bytecode(code.get('co_code', b''), f"{i+1}.{name}")
        analyses.append((name, code, result))
    
    # ================================================================
    # 步骤5: 汇总分析 - 寻找编码模式
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤5] 汇总分析 - 寻找编码模式")
    print(f"{'#'*70}")
    
    # 收集所有字节码
    all_bytecode = b''
    for name, code, result in analyses:
        all_bytecode += code.get('co_code', b'')
    
    print(f"\n总字节码长度: {len(all_bytecode)}")
    
    # 整体分析
    overall = analyze_bytecode(all_bytecode, "ALL_COMBINED")
    
    # ================================================================
    # 步骤6: 尝试破解编码
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤6] 尝试破解编码")
    print(f"{'#'*70}")
    
    # 尝试各种转换
    transforms = []
    
    # 1. XOR with constant
    for key in range(1, 256):
        decoded = bytes(b ^ key for b in all_bytecode)
        ratio = sum(1 for b in decoded if b in STANDARD_OPCODE_SET) / len(decoded)
        if ratio > 0.6:
            transforms.append(('xor', key, ratio, decoded))
    
    # 2. NOT
    decoded = bytes(~b & 0xFF for b in all_bytecode)
    ratio = sum(1 for b in decoded if b in STANDARD_OPCODE_SET) / len(decoded)
    if ratio > 0.6:
        transforms.append(('not', 0, ratio, decoded))
    
    # 3. ADD/SUB constant
    for delta in range(1, 256):
        decoded = bytes((b + delta) & 0xFF for b in all_bytecode)
        ratio = sum(1 for b in decoded if b in STANDARD_OPCODE_SET) / len(decoded)
        if ratio > 0.6:
            transforms.append(('add', delta, ratio, decoded))
    
    # 4. 位旋转
    for shift in range(1, 8):
        decoded = bytes(((b << shift) | (b >> (8-shift))) & 0xFF for b in all_bytecode)
        ratio = sum(1 for b in decoded if b in STANDARD_OPCODE_SET) / len(decoded)
        if ratio > 0.6:
            transforms.append(('rot_left', shift, ratio, decoded))
        
        decoded = bytes(((b >> shift) | (b << (8-shift))) & 0xFF for b in all_bytecode)
        ratio = sum(1 for b in decoded if b in STANDARD_OPCODE_SET) / len(decoded)
        if ratio > 0.6:
            transforms.append(('rot_right', shift, ratio, decoded))
    
    # 按比例排序
    transforms.sort(key=lambda x: -x[2])
    
    print(f"\n发现 {len(transforms)} 种可能的转换:")
    for trans_type, param, ratio, decoded in transforms[:10]:
        print(f"  {trans_type}({param}): 标准opcode比例 {ratio:.1%}")
    
    # ================================================================
    # 步骤7: 保存分析结果
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤7] 保存分析结果")
    print(f"{'#'*70}")
    
    output_dir = 'work/dream-world-connect-login-map/notes/co_code_analysis'
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存所有 code object 的详细信息
    code_info = []
    for i, (name, code, result) in enumerate(analyses):
        co_code = code.get('co_code', b'')
        
        # 提取 names 和 varnames（这些通常是可读的字符串）
        names = code.get('names', [])
        if isinstance(names, (tuple, list)):
            names = [n.decode('utf-8', errors='replace') if isinstance(n, bytes) else str(n) for n in names]
        
        varnames = code.get('varnames', [])
        if isinstance(varnames, (tuple, list)):
            varnames = [n.decode('utf-8', errors='replace') if isinstance(n, bytes) else str(n) for n in varnames]
        
        # 提取 consts 中的字符串
        consts = code.get('consts', [])
        const_strings = []
        if isinstance(consts, (tuple, list)):
            for c in consts:
                if isinstance(c, bytes):
                    try:
                        const_strings.append(c.decode('utf-8'))
                    except:
                        const_strings.append(c.hex())
                elif isinstance(c, str):
                    const_strings.append(c)
        
        info = {
            'index': i + 1,
            'name': name,
            'filename': code.get('filename', b'').decode('utf-8', errors='replace') if isinstance(code.get('filename'), bytes) else str(code.get('filename', '')),
            'argcount': code.get('argcount', 0),
            'nlocals': code.get('nlocals', 0),
            'stacksize': code.get('stacksize', 0),
            'flags': code.get('flags', 0),
            'firstlineno': code.get('firstlineno', 0),
            'co_code_length': len(co_code),
            'co_code_hex': co_code.hex(),
            'names': names,
            'varnames': varnames,
            'const_strings': const_strings,
            'analysis': {
                'unique_bytes': result['unique_bytes'],
                'standard_opcode_types': result['standard_count'],
                'non_standard_opcode_types': result['non_standard_count'],
                'entropy': round(result['entropy'], 2),
                'best_xor_key': result['best_xor'],
                'best_xor_ratio': round(result['best_xor_ratio'], 4),
            }
        }
        code_info.append(info)
    
    # 保存 JSON
    with open(os.path.join(output_dir, 'code_objects.json'), 'w', encoding='utf-8') as f:
        json.dump(code_info, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ 已保存: {output_dir}/code_objects.json")
    
    # 保存每个字节码文件
    for i, (name, code, result) in enumerate(analyses):
        co_code = code.get('co_code', b'')
        safe_name = name.replace('/', '_').replace('\\', '_')[:50]
        with open(os.path.join(output_dir, f'bytecode_{i:02d}_{safe_name}.bin'), 'wb') as f:
            f.write(co_code)
    
    print(f"  ✅ 已保存 {len(analyses)} 个字节码文件")
    
    # 保存最佳转换结果
    if transforms:
        best_type, best_param, best_ratio, best_decoded = transforms[0]
        with open(os.path.join(output_dir, 'best_transform.bin'), 'wb') as f:
            f.write(best_decoded)
        
        with open(os.path.join(output_dir, 'transform_info.json'), 'w') as f:
            json.dump({
                'type': best_type,
                'param': best_param,
                'ratio': best_ratio,
            }, f, indent=2)
        
        print(f"  ✅ 最佳转换: {best_type}({best_param}), 比例={best_ratio:.1%}")
        print(f"     已保存: {output_dir}/best_transform.bin")
    
    # ================================================================
    # 步骤8: 生成详细分析报告
    # ================================================================
    print(f"\n{'#'*70}")
    print("[步骤8] 生成分析报告")
    print(f"{'#'*70}")
    
    report = []
    report.append("# 任务A: Co_code 自定义编码分析报告")
    report.append("")
    report.append(f"**生成时间**: 2026-10-10")
    report.append(f"**目标**: `script\\login\\netserver.py` (entry 516)")
    report.append(f"**数据来源**: `entry516-five-xor-marshal.bin`")
    report.append("")
    report.append("---")
    report.append("")
    report.append("## 1. 概述")
    report.append("")
    report.append(f"- **Marshal 数据大小**: {len(data)} 字节")
    report.append(f"- **Code Object 数量**: {len(code_objects)}")
    report.append(f"- **总字节码长度**: {len(all_bytecode)} 字节")
    report.append(f"- **平均字节熵**: {sum(r['entropy'] for _, _, r in analyses) / len(analyses):.2f}")
    report.append("")
    report.append("## 2. Code Object 清单")
    report.append("")
    report.append("| # | 名称 | 字节码长度 | 参数数 | 局部变量 | 栈大小 |")
    report.append("|---|------|-----------|--------|----------|--------|")
    for i, (name, code, result) in enumerate(analyses):
        report.append(f"| {i+1} | {name} | {result['length']} | {code.get('argcount', 0)} | {code.get('nlocals', 0)} | {code.get('stacksize', 0)} |")
    
    report.append("")
    report.append("## 3. 字节码特征分析")
    report.append("")
    
    for i, (name, code, result) in enumerate(analyses):
        report.append(f"### 3.{i+1} {name}")
        report.append("")
        report.append(f"- **字节码长度**: {result['length']}")
        report.append(f"- **唯一字节值**: {result['unique_bytes']} / 256")
        report.append(f"- **标准 Opcode 种类**: {result['standard_count']}")
        report.append(f"- **非标准 Opcode 种类**: {result['non_standard_count']}")
        report.append(f"- **字节熵**: {result['entropy']:.2f}")
        report.append(f"- **最佳 XOR 密钥**: 0x{result['best_xor']:02X} (比例: {result['best_xor_ratio']:.1%})")
        report.append("")
    
    report.append("## 4. 编码模式分析")
    report.append("")
    report.append("### 4.1 整体统计")
    report.append("")
    report.append(f"- **总字节码**: {len(all_bytecode)} 字节")
    report.append(f"- **唯一字节值**: {overall['unique_bytes']} / 256")
    report.append(f"- **非标准 Opcode 种类**: {overall['non_standard_count']}")
    report.append(f"- **整体熵**: {overall['entropy']:.2f}")
    report.append("")
    
    report.append("### 4.2 发现的转换")
    report.append("")
    if transforms:
        report.append("| 排名 | 转换类型 | 参数 | 标准Opcode比例 |")
        report.append("|------|---------|------|---------------|")
        for rank, (trans_type, param, ratio, _) in enumerate(transforms[:10], 1):
            report.append(f"| {rank} | {trans_type} | {param} | {ratio:.1%} |")
    else:
        report.append("未发现明显的简单转换模式。")
    
    report.append("")
    report.append("## 5. 结论与下一步")
    report.append("")
    report.append("### 5.1 当前发现")
    report.append("")
    if transforms:
        best_type, best_param, best_ratio, _ = transforms[0]
        report.append(f"1. **最可能的编码**: `{best_type}` with param `{best_param}`")
        report.append(f"2. **标准 Opcode 比例**: {best_ratio:.1%}")
        report.append(f"3. 这表明字节码可能经过了简单的 `{best_type}` 转换")
    else:
        report.append("1. 未发现简单的 XOR/ADD/ROT 转换")
        report.append("2. 可能是更复杂的编码（如 S盒替换、流密码、或自定义映射表）")
    
    report.append("")
    report.append("### 5.2 下一步行动")
    report.append("")
    report.append("1. **深入分析最佳转换**: 如果发现了可能的转换，应用到所有字节码并尝试反汇编")
    report.append("2. **寻找 S盒/映射表**: 在 mx.exe/mxmain.dll 中寻找可能的字节替换表")
    report.append("3. **分析加载器代码**: 找到执行前转换 co_code 的原生代码")
    report.append("4. **频率分析**: 对比标准 Python 字节码的 opcode 频率分布")
    report.append("5. **已知明文攻击**: 利用已知的函数名、变量名推测字节码模式")
    
    with open(os.path.join(output_dir, 'analysis_report.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"  ✅ 已保存: {output_dir}/analysis_report.md")
    
    # ================================================================
    # 完成
    # ================================================================
    print(f"\n{'='*70}")
    print("✅ 分析完成!")
    print(f"📁 结果保存在: {output_dir}/")
    print(f"{'='*70}")
    print(f"\n关键发现:")
    print(f"  - Code Object 数量: {len(code_objects)}")
    print(f"  - 总字节码长度: {len(all_bytecode)}")
    if transforms:
        best_type, best_param, best_ratio, _ = transforms[0]
        print(f"  - 最佳转换: {best_type}({best_param}), 比例={best_ratio:.1%}")
    else:
        print(f"  - 未发现简单转换，可能需要更复杂的分析")
    print(f"\n下一步: 根据分析结果继续破解编码")


if __name__ == '__main__':
    main()
