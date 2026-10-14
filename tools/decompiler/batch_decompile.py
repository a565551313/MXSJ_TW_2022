#!/usr/bin/env python3
"""
《夢想世界》(MXSJ TW 2022) Python Bytecode Transpiler & Batch Decompiler
======================================================================

Supports both Duoyi custom Python VMs present in the client:
1. `data/data.fls` (or unpacked `.pyo` directory):
   - Engine: `exe/python27.dll` / `exe/python27_dy.dll` (Custom Python 2.7.13)
   - `HAVE_ARGUMENT = 0x5A` (90)
   - `PyCodeObject` marshal layout includes a 4-byte `co_extra` field before `co_code`,
     storing `op_stream_len` (uint32_le).
   - `co_code[:op_stream_len]` is the 1-byte opcode stream (padded with trailing `0x17` NOPs
     to a 2-byte boundary); `co_code[op_stream_len:]` is the `uint16_le` argument stream.
   - Jump targets (`ABS_JUMP_OPS` and `REL_JUMP_OPS`) use instruction indices (`i`) rather
     than byte offsets.
   - Transpiles to standard Python 2.7 `.pyc` (magic `03 f3 0d 0a`).

2. `data/script.fls`:
   - Engine: `mx.exe` / `mxmain.dll` (Embedded Custom Python 2.5)
   - `HAVE_ARGUMENT = 0x5F` (95)
   - `0SLF` archive + zlib + 5-segment XOR (`PkgImport` at VA `0x00457C20`).
   - Standard Python 2.5 `PyCodeObject` marshal layout (no `co_extra`), interleaved
     1-byte (`< 0x5F`) and 3-byte (`>= 0x5F`) instructions.
   - Transpiles to standard Python 2.5 `.pyc` (magic `b3 f2 0d 0a`).
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import multiprocessing as mp
import os
import re
import struct
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path
from typing import Any

# ============================================================================
# 1. Exact Opcode Mapping Tables (Extracted from Binary Jump Tables)
# ============================================================================

# VM #1: `mx.exe` / `mxmain.dll` (`data/script.fls`)
# Extracted from `PyEval_EvalFrameEx` (VA 0x004E7460), Jump Table at VA 0x004EA308,
# Index Table at VA 0x004EA490. `HAVE_ARGUMENT` = 0x5F (95).
PY25_MAP: dict[int, int] = {
    0x00: 9,    # NOP
    0x01: 75,   # INPLACE_LSHIFT
    0x03: 26,   # BINARY_FLOOR_DIVIDE
    0x05: 60,   # STORE_SUBSCR
    0x06: 3,    # ROT_THREE
    0x07: 28,   # INPLACE_FLOOR_DIVIDE
    0x08: 84,   # IMPORT_STAR
    0x09: 20,   # BINARY_MULTIPLY
    0x0A: 73,   # PRINT_ITEM_TO
    0x0B: 71,   # PRINT_ITEM
    0x0C: 30,   # SLICE+0
    0x0D: 31,   # SLICE+1
    0x0E: 32,   # SLICE+2
    0x0F: 33,   # SLICE+3
    0x10: 88,   # END_FINALLY
    0x11: 19,   # BINARY_POWER
    0x12: 10,   # UNARY_POSITIVE
    0x15: 12,   # UNARY_NOT
    0x18: 61,   # DELETE_SUBSCR
    0x19: 77,   # INPLACE_AND
    0x1A: 81,   # WITH_CLEANUP
    0x1B: 74,   # PRINT_NEWLINE_TO
    0x1D: 5,    # ROT_FOUR
    0x1F: 72,   # PRINT_NEWLINE
    0x20: 66,   # BINARY_OR
    0x21: 85,   # EXEC_STMT
    0x23: 24,   # BINARY_SUBTRACT
    0x24: 76,   # INPLACE_RSHIFT
    0x27: 65,   # BINARY_XOR
    0x28: 50,   # DELETE_SLICE+0
    0x29: 51,   # DELETE_SLICE+1
    0x2A: 52,   # DELETE_SLICE+2
    0x2B: 53,   # DELETE_SLICE+3
    0x2C: 13,   # UNARY_CONVERT
    0x30: 4,    # DUP_TOP
    0x32: 67,   # INPLACE_POWER
    0x33: 58,   # INPLACE_DIVIDE
    0x36: 68,   # GET_ITER
    0x37: 22,   # BINARY_MODULO
    0x38: 82,   # LOAD_LOCALS
    0x3A: 59,   # INPLACE_MODULO
    0x3B: 29,   # INPLACE_TRUE_DIVIDE
    0x3D: 21,   # BINARY_DIVIDE
    0x3E: 64,   # BINARY_AND
    0x3F: 23,   # BINARY_ADD
    0x40: 87,   # POP_BLOCK
    0x41: 1,    # POP_TOP
    0x42: 89,   # BUILD_CLASS
    0x43: 55,   # INPLACE_ADD
    0x44: 78,   # INPLACE_XOR
    0x45: 11,   # UNARY_NEGATIVE
    0x46: 63,   # BINARY_RSHIFT
    0x47: 80,   # BREAK_LOOP
    0x48: 40,   # STORE_SLICE+0
    0x49: 41,   # STORE_SLICE+1
    0x4A: 42,   # STORE_SLICE+2
    0x4B: 43,   # STORE_SLICE+3
    0x4C: 57,   # INPLACE_MULTIPLY
    0x4D: 18,   # LIST_APPEND
    0x4E: 27,   # BINARY_TRUE_DIVIDE
    0x53: 70,   # PRINT_EXPR
    0x54: 15,   # UNARY_INVERT
    0x55: 83,   # RETURN_VALUE
    0x56: 62,   # BINARY_LSHIFT
    0x57: 56,   # INPLACE_SUBTRACT
    0x58: 25,   # BINARY_SUBSCR
    0x5A: 2,    # ROT_TWO
    0x5B: 79,   # INPLACE_OR
    0x5E: 86,   # YIELD_VALUE
    # --- HAVE_ARGUMENT >= 0x5F (95) ---
    0x61: 98,   # DELETE_GLOBAL
    0x6C: 92,   # UNPACK_SEQUENCE
    0x71: 125,  # STORE_FAST
    0x72: 136,  # LOAD_DEREF
    0x7E: 133,  # BUILD_SLICE
    0x83: 126,  # DELETE_FAST
    0x85: 116,  # LOAD_GLOBAL
    0x8B: 143,  # EXTENDED_ARG
    0x8F: 100,  # LOAD_CONST
    0x90: 130,  # RAISE_VARARGS
    0x91: 135,  # LOAD_CLOSURE
    0x95: 106,  # COMPARE_OP
    0x98: 90,   # STORE_NAME
    0xA2: 113,  # JUMP_ABSOLUTE
    0xAA: 101,  # LOAD_NAME
    0xAD: 108,  # IMPORT_FROM
    0xAF: 93,   # FOR_ITER
    0xB7: 111,  # JUMP_IF_FALSE
    0xBB: 104,  # BUILD_MAP
    0xBC: 99,   # DUP_TOPX
    0xBF: 137,  # STORE_DEREF
    0xC1: 124,  # LOAD_FAST
    0xC4: 97,   # STORE_GLOBAL
    0xC5: 95,   # STORE_ATTR
    0xCA: 103,  # BUILD_LIST
    0xCD: 119,  # CONTINUE_LOOP
    0xCF: 121,  # SETUP_EXCEPT
    0xD3: 120,  # SETUP_LOOP
    0xD6: 122,  # SETUP_FINALLY
    0xD9: 105,  # LOAD_ATTR
    0xDA: 131,  # CALL_FUNCTION
    0xDB: 140,  # CALL_FUNCTION_VAR
    0xDC: 141,  # CALL_FUNCTION_KW
    0xDD: 142,  # CALL_FUNCTION_VAR_KW
    0xDE: 102,  # BUILD_TUPLE
    0xE0: 107,  # IMPORT_NAME
    0xE3: 112,  # JUMP_IF_TRUE
    0xE4: 91,   # DELETE_NAME
    0xE5: 110,  # JUMP_FORWARD
    0xF1: 96,   # DELETE_ATTR
    0xF2: 134,  # MAKE_CLOSURE
    0xFB: 132,  # MAKE_FUNCTION
}

# VM #2: `exe/python27.dll` / `exe/python27_dy.dll` (`data/data.fls`)
# Extracted from `PyEval_EvalFrame` (VA 0x1E12A380), Jump Table at VA 0x1E12CA48,
# Index Table at VA 0x1E12CBF8, and verified against `data.fls -> lib/opcode.pyo`.
# `HAVE_ARGUMENT` = 0x5A (90).
PY27_MAP: dict[int, int] = {
    0: 50,    # DELETE_SLICE+0
    1: 51,    # DELETE_SLICE+1
    2: 52,    # DELETE_SLICE+2
    3: 53,    # DELETE_SLICE+3
    4: 59,    # INPLACE_MODULO
    5: 68,    # GET_ITER
    6: 86,    # YIELD_VALUE
    7: 1,     # POP_TOP
    8: 75,    # INPLACE_LSHIFT
    9: 80,    # BREAK_LOOP
    11: 15,   # UNARY_INVERT
    12: 85,   # EXEC_STMT
    16: 10,   # UNARY_POSITIVE
    17: 63,   # BINARY_RSHIFT
    20: 66,   # BINARY_OR
    21: 87,   # POP_BLOCK
    22: 61,   # DELETE_SUBSCR
    23: 9,    # NOP
    24: 30,   # SLICE+0
    25: 31,   # SLICE+1
    26: 32,   # SLICE+2
    27: 33,   # SLICE+3
    28: 62,   # BINARY_LSHIFT
    29: 88,   # END_FINALLY
    30: 27,   # BINARY_TRUE_DIVIDE
    31: 73,   # PRINT_ITEM_TO
    32: 2,    # ROT_TWO
    33: 79,   # INPLACE_OR
    34: 19,   # BINARY_POWER
    35: 76,   # INPLACE_RSHIFT
    36: 4,    # DUP_TOP
    37: 5,    # ROT_FOUR
    39: 58,   # INPLACE_DIVIDE
    40: 40,   # STORE_SLICE+0
    41: 41,   # STORE_SLICE+1
    42: 42,   # STORE_SLICE+2
    43: 43,   # STORE_SLICE+3
    44: 57,   # INPLACE_MULTIPLY
    46: 84,   # IMPORT_STAR
    48: 28,   # INPLACE_FLOOR_DIVIDE
    49: 29,   # INPLACE_TRUE_DIVIDE
    50: 67,   # INPLACE_POWER
    51: 23,   # BINARY_ADD
    53: 24,   # BINARY_SUBTRACT
    55: 11,   # UNARY_NEGATIVE
    56: 72,   # PRINT_NEWLINE
    57: 20,   # BINARY_MULTIPLY
    58: 81,   # WITH_CLEANUP
    60: 78,   # INPLACE_XOR
    61: 89,   # BUILD_CLASS
    62: 25,   # BINARY_SUBSCR
    63: 77,   # INPLACE_AND
    65: 65,   # BINARY_XOR
    66: 42,   # STOP_CODE -> STORE_SLICE+2 alias
    67: 21,   # BINARY_DIVIDE
    69: 54,   # STORE_MAP
    70: 55,   # INPLACE_ADD
    71: 3,    # ROT_THREE
    72: 82,   # LOAD_LOCALS
    73: 13,   # UNARY_CONVERT
    74: 12,   # UNARY_NOT
    76: 60,   # STORE_SUBSCR
    80: 56,   # INPLACE_SUBTRACT
    81: 26,   # BINARY_FLOOR_DIVIDE
    82: 71,   # PRINT_ITEM
    83: 74,   # PRINT_NEWLINE_TO
    84: 83,   # RETURN_VALUE
    85: 70,   # PRINT_EXPR
    86: 22,   # BINARY_MODULO
    89: 64,   # BINARY_AND
    # --- HAVE_ARGUMENT >= 0x5A (90) ---
    90: 125,   # STORE_FAST
    91: 100,   # LOAD_CONST
    92: 103,   # BUILD_LIST
    93: 133,   # BUILD_SLICE
    95: 143,   # SETUP_WITH
    100: 147,  # MAP_ADD
    112: 90,   # STORE_NAME
    117: 93,   # FOR_ITER
    121: 134,  # MAKE_CLOSURE
    124: 107,  # IMPORT_NAME
    130: 95,   # STORE_ATTR
    135: 108,  # IMPORT_FROM
    136: 120,  # SETUP_LOOP
    137: 105,  # LOAD_ATTR
    138: 96,   # DELETE_ATTR
    139: 126,  # DELETE_FAST
    147: 110,  # JUMP_FORWARD
    154: 114,  # POP_JUMP_IF_FALSE
    155: 109,  # IMPORT_APPEND
    156: 137,  # STORE_DEREF
    158: 97,   # STORE_GLOBAL
    162: 111,  # JUMP_IF_FALSE_OR_POP
    163: 102,  # BUILD_TUPLE
    164: 101,  # LOAD_NAME
    166: 115,  # POP_JUMP_IF_TRUE
    172: 94,   # LIST_APPEND
    175: 131,  # CALL_FUNCTION
    176: 140,  # CALL_FUNCTION_VAR
    177: 141,  # CALL_FUNCTION_KW
    178: 142,  # CALL_FUNCTION_VAR_KW
    179: 146,  # SET_ADD
    183: 104,  # BUILD_MAP
    186: 92,   # UNPACK_SEQUENCE
    193: 112,  # JUMP_IF_TRUE_OR_POP
    194: 122,  # SETUP_FINALLY
    195: 130,  # RAISE_VARARGS
    200: 136,  # LOAD_DEREF
    218: 124,  # LOAD_FAST
    219: 98,   # DELETE_GLOBAL
    223: 121,  # SETUP_EXCEPT
    226: 113,  # JUMP_ABSOLUTE
    229: 132,  # MAKE_FUNCTION
    230: 106,  # COMPARE_OP
    231: 119,  # CONTINUE_LOOP
    233: 99,   # DUP_TOPX
    235: 135,  # LOAD_CLOSURE
    242: 145,  # EXTENDED_ARG
    246: 116,  # LOAD_GLOBAL
    247: 91,   # DELETE_NAME
}

PY27_ABS_JUMP_OPS = frozenset({0xE2, 0xE7, 0x9A, 0xA6, 0xA2, 0xC1})
PY27_REL_JUMP_OPS = frozenset({0x75, 0x93, 0x88, 0xDF, 0xC2, 0x5F})

PY25_MAGIC = b"\xb3\xf2\x0d\x0a\x00\x00\x00\x00"
PY27_MAGIC = b"\x03\xf3\x0d\x0a\x00\x00\x00\x00"

XTABS = [bytes(b ^ k for b in range(256)) for k in range(256)]


# ============================================================================
# 2. Python 2.7 (`data.fls` / `.pyo`) Split-Stream Bytecode Transpiler
# ============================================================================

def transpile_py27_code(co_code: bytes, op_stream_len: int) -> tuple[bytes, list[int]]:
    """
    Recombines Duoyi Python 2.7 split-stream `co_code` into standard Python 2.7 `co_code`.
    - `co_code[:op_stream_len]`: 1-byte opcodes (padded with trailing `0x17` NOPs).
    - `co_code[op_stream_len:]`: `uint16_le` arguments for opcodes `>= 0x5A`.
    - Converts instruction-index jump targets (`PY27_ABS_JUMP_OPS`, `PY27_REL_JUMP_OPS`)
      into standard Python 2.7 byte offsets.
    """
    ops = co_code[:op_stream_len]
    args = co_code[op_stream_len:]
    jump_ops = PY27_ABS_JUMP_OPS | PY27_REL_JUMP_OPS
    needed_args = sum((4 if b in jump_ops else 2) for b in ops if b >= 0x5A)
    while len(ops) > 0 and needed_args == len(args) and ops[-1] == 0x17:
        ops = ops[:-1]

    n_ops = len(ops)
    std_offsets = [0] * (n_ops + 1)
    cur = 0
    for i, b in enumerate(ops):
        std_offsets[i] = cur
        cur += 3 if b >= 0x5A else 1
    std_offsets[n_ops] = cur

    out = bytearray()
    ap = 0
    for i, b in enumerate(ops):
        std_op = PY27_MAP[b]
        out.append(std_op)
        if b >= 0x5A:
            arg = args[ap] | (args[ap + 1] << 8)
            ap += 4 if b in jump_ops else 2
            if b in PY27_ABS_JUMP_OPS:
                std_arg = std_offsets[arg] if arg <= n_ops else arg
            elif b in PY27_REL_JUMP_OPS:
                target_idx = i + 1 + arg
                if target_idx <= n_ops:
                    std_arg = std_offsets[target_idx] - std_offsets[i + 1]
                else:
                    std_arg = arg
            else:
                std_arg = arg
            out.append(std_arg & 0xFF)
            out.append((std_arg >> 8) & 0xFF)

    return bytes(out), std_offsets


def transpile_py27_lnotab(lnotab: bytes, std_offsets: list[int]) -> bytes:
    """Adjusts `co_lnotab` instruction-index deltas to standard byte-offset deltas."""
    if not lnotab or len(lnotab) % 2 != 0:
        return lnotab
    out = bytearray()
    cur_idx = 0
    cur_std = 0
    n_ops = len(std_offsets) - 1
    for j in range(0, len(lnotab), 2):
        d_idx = lnotab[j]
        d_line = lnotab[j + 1]
        cur_idx += d_idx
        new_std = std_offsets[min(cur_idx, n_ops)]
        d_std = new_std - cur_std
        cur_std = new_std
        while d_std > 255:
            out.extend((255, 0))
            d_std -= 255
        out.extend((d_std, d_line))
    return bytes(out)


class Py27MarshalTranspiler:
    """
    Parses a Duoyi Python 2.7 `.pyo` file (with 4-byte `co_extra` inside each `TYPE_CODE`),
    strips `co_extra`, transpiles `co_code` and `co_lnotab`, and emits standard Python 2.7 `.pyc`.
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 8  # Skip 8-byte .pyo header (magic + timestamp)
        self.out = bytearray(data[:8] if len(data) >= 8 else PY27_MAGIC)
        self.strings: list[bytes] = []

    def copy_bytes(self, n: int) -> bytes:
        chunk = self.data[self.pos : self.pos + n]
        self.pos += n
        self.out.extend(chunk)
        return chunk

    def read_raw_string_obj(self) -> tuple[int, bytes]:
        t = self.data[self.pos]
        self.pos += 1
        tc = chr(t)
        if tc in ("s", "t", "u"):
            ln = struct.unpack_from("<I", self.data, self.pos)[0]
            self.pos += 4
            s = self.data[self.pos : self.pos + ln]
            self.pos += ln
            if tc == "t":
                self.strings.append(s)
            return t, s
        if tc == "R":
            ref = struct.unpack_from("<I", self.data, self.pos)[0]
            self.pos += 4
            return t, self.strings[ref]
        raise ValueError(f"Expected string object in code object, got 0x{t:02x}")

    def transpile_object(self) -> None:
        t = self.data[self.pos]
        self.pos += 1
        self.out.append(t)
        tc = chr(t)
        if tc in ("0", "N", "F", "T", "S", "."):
            return
        if tc in ("i", "I", "g", "R"):
            self.copy_bytes(8 if tc in ("I", "g") else 4)
            return
        if tc == "l":
            raw_n = self.copy_bytes(4)
            n = abs(struct.unpack("<i", raw_n)[0])
            self.copy_bytes(n * 2)
            return
        if tc in ("s", "t", "u"):
            raw_ln = self.copy_bytes(4)
            ln = struct.unpack("<I", raw_ln)[0]
            s = self.copy_bytes(ln)
            if tc == "t":
                self.strings.append(s)
            return
        if tc in ("f", "x"):
            ln = self.copy_bytes(1)[0]
            self.copy_bytes(ln)
            return
        if tc in ("(", "[", "<", ">"):
            raw_n = self.copy_bytes(4)
            n = struct.unpack("<I", raw_n)[0]
            for _ in range(n):
                self.transpile_object()
            return
        if tc == "{":
            while True:
                if self.data[self.pos] == ord("0"):
                    self.pos += 1
                    self.out.append(ord("0"))
                    break
                self.transpile_object()
                self.transpile_object()
            return
        if tc == "c":
            # 16-byte header: argcount, nlocals, stacksize, flags
            self.copy_bytes(16)
            # Strip 4-byte Duoyi `co_extra` (`op_stream_len`)
            op_stream_len = struct.unpack_from("<I", self.data, self.pos)[0]
            self.pos += 4
            # Read `co_code` and transpile to standard Python 2.7 bytecode
            code_t, raw_code = self.read_raw_string_obj()
            std_code, std_offsets = transpile_py27_code(raw_code, op_stream_len)
            if chr(code_t) == "t":
                self.strings[-1] = std_code
                self.out.append(ord("t"))
            else:
                self.out.append(ord("s"))
            self.out.extend(struct.pack("<I", len(std_code)))
            self.out.extend(std_code)
            # Transpile co_consts, co_names, co_varnames, co_freevars, co_cellvars, co_filename, co_name
            for _ in range(7):
                self.transpile_object()
            # Copy co_firstlineno
            self.copy_bytes(4)
            # Read and transpile `co_lnotab`
            lno_t, raw_lnotab = self.read_raw_string_obj()
            std_lnotab = transpile_py27_lnotab(raw_lnotab, std_offsets)
            if chr(lno_t) == "t":
                self.strings[-1] = std_lnotab
                self.out.append(ord("t"))
            else:
                self.out.append(ord("s"))
            self.out.extend(struct.pack("<I", len(std_lnotab)))
            self.out.extend(std_lnotab)
            return
        raise ValueError(f"Unknown marshal type 0x{t:02x} at offset {self.pos - 1}")


def transpile_py27_pyo_bytes(data: bytes) -> bytes:
    tr = Py27MarshalTranspiler(data)
    tr.transpile_object()
    return bytes(tr.out)


# ============================================================================
# 3. Python 2.5 (`script.fls`) 5-Segment XOR + Bytecode Transpiler
# ============================================================================

PY25_NAME_OPS = {90, 91, 95, 96, 97, 98, 101, 105, 107, 108, 116}
PY25_FAST_OPS = {124, 125, 126}
PY25_DEREF_OPS = {135, 136, 137}
PY25_ABS_JUMPS = {113, 119}
PY25_REL_JUMPS = {93, 110, 111, 112, 120, 121, 122}


def check_py25_co_code(
    co: bytes,
    limits: tuple[int, int, int, int, int] | None = None,
) -> tuple[bool, int]:
    n = len(co)
    if n == 0:
        return False, 0
    i = 0
    while i < n:
        op = co[i]
        std_op = PY25_MAP.get(op)
        if std_op is None:
            return False, i
        if op >= 0x5F:
            if i + 3 > n:
                return False, i
            arg = co[i + 1] | (co[i + 2] << 8)
            if std_op == 106 and arg > 10:
                return False, i
            if limits is not None:
                n_consts, n_names, n_varnames, n_deref, n_code = limits
                if std_op == 100 and arg >= n_consts:
                    return False, i
                if std_op in PY25_NAME_OPS and arg >= n_names:
                    return False, i
                if std_op in PY25_FAST_OPS and arg >= n_varnames:
                    return False, i
                if std_op in PY25_DEREF_OPS and arg >= n_deref:
                    return False, i
                if std_op in PY25_ABS_JUMPS and arg >= n_code:
                    return False, i
                if std_op in PY25_REL_JUMPS and i + 3 + arg > n_code:
                    return False, i
            i += 3
        else:
            i += 1
    return True, n


def score_py25_co_window(
    co: bytes,
    start_i: int,
    end_i: int,
    limits: tuple[int, int, int, int, int] | None = None,
    base_offset: int = 0,
) -> int:
    i = start_i
    score = 0
    while i < end_i:
        op = co[i]
        std_op = PY25_MAP.get(op)
        if std_op is None:
            return -100000
        if op >= 0x5F:
            if i + 3 > end_i:
                return -100000
            lo_arg = co[i + 1]
            hi_arg = co[i + 2]
            arg = lo_arg | (hi_arg << 8)
            if std_op == 106 and arg > 10:
                return -100000
            if limits is not None:
                n_consts, n_names, n_varnames, n_deref, n_code = limits
                if std_op == 100 and arg >= n_consts:
                    return -100000
                if std_op in PY25_NAME_OPS and arg >= n_names:
                    return -100000
                if std_op in PY25_FAST_OPS and arg >= n_varnames:
                    return -100000
                if std_op in PY25_DEREF_OPS and arg >= n_deref:
                    return -100000
                if std_op in PY25_ABS_JUMPS and arg >= n_code:
                    return -100000
                if std_op in PY25_REL_JUMPS and base_offset + i + 3 + arg > n_code:
                    return -100000
            if hi_arg == 0:
                score += 6 if lo_arg < 32 else (4 if lo_arg < 96 else 2)
            elif hi_arg < 8:
                score += 1
            else:
                score -= 6
            i += 3
        else:
            if std_op == 9:  # NOP never emitted by Python 2.5 compiler
                score -= 6
            elif std_op in (1, 25, 83):
                score += 2
            else:
                score += 1
            i += 1
    return score if i == end_i else -100000


def solve_py25_co_span(
    exp_slice: bytes,
    seg_keys: list[int],
    rel_bounds: list[int],
    limits: tuple[int, int, int, int, int] | None = None,
) -> bytes | None:
    """Pinpoints exact segment transition boundaries inside a `co_code` span."""
    m = len(seg_keys)
    if m == 1:
        co = exp_slice.translate(XTABS[seg_keys[0]])
        return co if check_py25_co_code(co, limits)[0] else None
    n = len(exp_slice)
    decs = [exp_slice.translate(XTABS[k]) for k in seg_keys]
    cur_b = list(rel_bounds)
    for step in range(m - 1):
        prefix = b"".join(decs[j][0 if j == 0 else cur_b[j - 1] : cur_b[j]] for j in range(step))
        start_step = 0 if step == 0 else cur_b[step - 1]
        end_next = n if step + 1 == m - 1 else cur_b[step + 1]
        probe = prefix + decs[step][start_step:end_next]
        ok_p, crash_i = check_py25_co_code(probe[:end_next], limits)
        b_est = cur_b[step]
        if ok_p:
            lo = max(start_step, b_est - 16)
            hi = min(end_next, b_est + 16)
        else:
            lo = max(start_step, min(b_est - 24, crash_i - 24))
            hi = min(end_next, max(b_est + 24, crash_i + 12))
        pc = 0
        while pc < lo:
            op = probe[pc]
            nxt = pc + (3 if op >= 0x5F else 1)
            if nxt > lo:
                break
            pc = nxt
        sync_end = end_next
        best_b = None
        best_sc = -100000
        for b_try in range(max(pc, lo), min(hi, sync_end) + 1):
            sub = probe[pc:b_try] + decs[step + 1][b_try:sync_end]
            s = score_py25_co_window(sub, 0, len(sub), limits=limits, base_offset=pc)
            if s > best_sc:
                best_sc = s
                best_b = b_try
        if best_b is not None:
            cur_b[step] = best_b
    pts = [0] + cur_b + [n]
    final_co = b"".join(decs[j][pts[j] : pts[j + 1]] for j in range(m))
    return final_co if check_py25_co_code(final_co, limits)[0] else None


def transpile_py25_code(co: bytes) -> bytes:
    """Remaps Duoyi Python 2.5 opcodes (`HAVE_ARGUMENT = 0x5F`) to standard Python 2.5 opcodes."""
    out = bytearray(co)
    i = 0
    n = len(out)
    while i < n:
        op = out[i]
        out[i] = PY25_MAP.get(op, 9)  # fallback to NOP if corrupted byte
        i += 3 if op >= 0x5F else 1
    return bytes(out)


class Py25MarshalTranspiler:
    """
    Walks a 5-segment XOR-decrypted Python 2.5 marshal buffer from `data/script.fls`,
    applies `solve_py25_co_span` if any `co_code` straddles a segment boundary,
    remaps all `co_code` opcodes via `PY25_MAP`, and extracts `co_filename`.
    """

    def __init__(self, dec: bytes, exp: bytes, keys: list[int], bounds: list[int]) -> None:
        self.data = bytearray(dec)
        self.exp = exp
        self.keys = keys
        self.bounds = bounds
        self.pos = 0
        self.out = bytearray(PY25_MAGIC)
        self.filename: str | None = None

    def copy_bytes(self, n: int) -> bytes:
        chunk = bytes(self.data[self.pos : self.pos + n])
        self.pos += n
        self.out.extend(chunk)
        return chunk

    def read_str_val(self) -> tuple[int, bytes]:
        t = self.data[self.pos]
        self.pos += 1
        tc = chr(t)
        if tc in ("s", "t", "u"):
            ln = struct.unpack_from("<I", self.data, self.pos)[0]
            self.pos += 4
            s = bytes(self.data[self.pos : self.pos + ln])
            self.pos += ln
            return t, s
        if tc == "R":
            raw_ref = bytes(self.data[self.pos : self.pos + 4])
            self.pos += 4
            return t, raw_ref
        raise ValueError(f"Expected string tag, got 0x{t:02x} at {self.pos - 1}")

    def transpile_object(self) -> None:
        t = self.data[self.pos]
        self.pos += 1
        tc = chr(t)
        if tc in ("0", "N", "F", "T", "S", "."):
            self.out.append(t)
            return
        if tc in ("i", "I", "g", "R"):
            self.out.append(t)
            self.copy_bytes(8 if tc in ("I", "g") else 4)
            return
        if tc == "l":
            self.out.append(t)
            raw_n = self.copy_bytes(4)
            n = abs(struct.unpack("<i", raw_n)[0])
            self.copy_bytes(n * 2)
            return
        if tc in ("s", "t", "u"):
            self.out.append(t)
            raw_ln = self.copy_bytes(4)
            ln = struct.unpack("<I", raw_ln)[0]
            self.copy_bytes(ln)
            return
        if tc in ("f", "x"):
            self.out.append(t)
            ln = self.copy_bytes(1)[0]
            self.copy_bytes(ln)
            return
        if tc in ("(", "[", "<", ">"):
            self.out.append(t)
            raw_n = self.copy_bytes(4)
            n = struct.unpack("<I", raw_n)[0]
            for _ in range(n):
                self.transpile_object()
            return
        if tc == "{":
            self.out.append(t)
            while True:
                if self.data[self.pos] == ord("0"):
                    self.pos += 1
                    self.out.append(ord("0"))
                    break
                self.transpile_object()
                self.transpile_object()
            return
        if tc == "c":
            self.out.append(t)
            hdr_pos = self.pos
            hdr_out_pos = len(self.out)
            self.copy_bytes(16)
            ct = self.data[self.pos]
            clen = struct.unpack_from("<I", self.data, self.pos + 1)[0]
            cs = self.pos + 5
            ce = cs + clen
            self.pos = ce
            raw_co = bytes(self.data[cs:ce])
            self.out.append(ct)
            self.out.extend(struct.pack("<I", clen))
            co_out_pos = len(self.out)
            self.out.extend(raw_co)
            # co_consts, co_names, co_varnames, co_freevars, co_cellvars (always TYPE_TUPLE '(')
            tup_counts = []
            for _ in range(5):
                if self.data[self.pos] != ord("("):
                    self.data[self.pos] = ord("(")
                tup_counts.append(struct.unpack_from("<I", self.data, self.pos + 1)[0])
                self.transpile_object()
            n_varnames = tup_counts[2]
            argcount, nlocals, stacksize, flags = struct.unpack_from("<IIII", self.out, hdr_out_pos)
            if (
                nlocals != n_varnames
                or argcount > n_varnames
                or (flags & ~0x7F) != 0
                or argcount + ((flags >> 2) & 1) + ((flags >> 3) & 1) > n_varnames
            ):
                # A segment boundary fell inside the 16-byte PyCodeObject header; repair it
                for bi, b in enumerate(self.bounds):
                    if hdr_pos - 4 <= b <= hdr_pos + 20:
                        k_prev, k_next = self.keys[bi], self.keys[bi + 1]
                        exp_hdr = self.exp[hdr_pos : hdr_pos + 16]
                        for r_try in range(17):
                            cand = exp_hdr[:r_try].translate(XTABS[k_prev]) + exp_hdr[r_try:].translate(XTABS[k_next])
                            ca, cn, cs_sz, cf = struct.unpack("<IIII", cand)
                            if (
                                cn == n_varnames
                                and ca <= n_varnames
                                and 0 < cs_sz < 256
                                and (cf & ~0x7F) == 0
                                and ca + ((cf >> 2) & 1) + ((cf >> 3) & 1) <= n_varnames
                            ):
                                self.out[hdr_out_pos : hdr_out_pos + 16] = cand
                                break
            limits = (
                tup_counts[0],
                tup_counts[1],
                tup_counts[2],
                tup_counts[3] + tup_counts[4],
                clen,
            )
            s_lo = 0
            while s_lo < 4 and self.bounds[s_lo] < cs:
                s_lo += 1
            s_hi = 0
            while s_hi < 4 and self.bounds[s_hi] < ce:
                s_hi += 1
            if s_lo < s_hi:
                seg_ks = self.keys[s_lo : s_hi + 1]
                rel_bs = [self.bounds[s] - cs for s in range(s_lo, s_hi)]
                fixed = solve_py25_co_span(self.exp[cs:ce], seg_ks, rel_bs, limits=limits)
                if fixed is not None:
                    raw_co = fixed
            std_co = transpile_py25_code(raw_co)
            self.out[co_out_pos : co_out_pos + clen] = std_co
            # co_filename
            fn_t, fn_bytes = self.read_str_val()
            self.out.append(fn_t)
            if chr(fn_t) == "R":
                self.out.extend(fn_bytes)
            else:
                self.out.extend(struct.pack("<I", len(fn_bytes)))
                self.out.extend(fn_bytes)
                if self.filename is None and b".py" in fn_bytes:
                    self.filename = fn_bytes.decode("latin1", errors="replace").replace("\\", "/")
            # co_name
            self.transpile_object()
            # co_firstlineno
            self.copy_bytes(4)
            # co_lnotab
            self.transpile_object()
            return
        raise ValueError(f"Unknown Python 2.5 marshal tag 0x{t:02x} at {self.pos - 1}")


# ============================================================================
# 4. Big5 (`cp950`) String Literal Post-Processor & Decompiler Engine
# ============================================================================

_STR_TOKEN_RE = re.compile(r"""([uUbB]?[rR]?(?:'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|'[^'\n\\]*(?:\\.[^'\n\\]*)*'|\"[^\"\n\\]*(?:\\.[^\"\n\\]*)*\"))""")


def decode_big5_literals(src: str) -> str:
    r"""
    Converts `\xHH` Big5 (`cp950`) byte escape sequences inside Python string literals
    into readable Traditional Chinese UTF-8 source code while preserving syntax validity.
    """
    if "\\x" not in src:
        return src

    def _replace_match(m: re.Match[str]) -> str:
        lit = m.group(0)
        if "\\x" not in lit or lit[:2].lower() in ("r'", 'r"', "ur", "br"):
            return lit
        try:
            val = ast.literal_eval(lit)
            if isinstance(val, bytes):
                text = val.decode("cp950")
            elif isinstance(val, str):
                raw_b = val.encode("latin1")
                text = raw_b.decode("cp950")
            else:
                return lit
            # Only decode if it contains actual Chinese/CJK characters and no raw control chars
            if any(ord(ch) < 32 and ch not in "\r\n\t" for ch in text):
                return lit
            if not any("\u3000" <= ch <= "\u9fff" or "\uff00" <= ch <= "\uffef" for ch in text):
                return lit
            # Ensure no control characters break single-line literals
            escaped = (
                text.replace("\\", "\\\\")
                .replace("\r", "\\r")
                .replace("\n", "\\n")
                .replace("\t", "\\t")
            )
            if lit.startswith(("'''", '"""')):
                q = lit[:3]
                return f"{q}{escaped}{q}"
            q = "'" if "'" not in escaped or '"' in escaped else '"'
            if q == "'":
                escaped = escaped.replace("'", "\\'")
            else:
                escaped = escaped.replace('"', '\\"')
            return f"{q}{escaped}{q}"
        except Exception:
            return lit

    out = _STR_TOKEN_RE.sub(_replace_match, src)
    return "# -*- coding: utf-8 -*-\n" + out


def decompile_pyc_bytes(
    pyc_data: bytes,
    engine: str = "auto",
    decode_big5: bool = True,
) -> tuple[bool, str, str]:
    """
    Decompiles standard Python 2.5 / 2.7 `.pyc` bytes to Python source code.
    Returns `(success, used_engine, source_code)`.
    """
    with tempfile.NamedTemporaryFile(suffix=".pyc", delete=False) as tf:
        tf.write(pyc_data)
        tmp_path = tf.name

    try:
        u6_src = ""
        if engine in ("auto", "uncompyle6"):
            try:
                import contextlib
                import uncompyle6.main as u6_main
                buf = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    u6_main.decompile_file(tmp_path, outstream=buf)
                u6_src = buf.getvalue()
                if u6_src.strip() and "Parse error at" not in u6_src and "Error decompyling" not in u6_src:
                    if decode_big5:
                        u6_src = decode_big5_literals(u6_src)
                    return True, "uncompyle6", u6_src
            except Exception as e_u6:
                if engine == "uncompyle6":
                    return False, "uncompyle6", f"# uncompyle6 failed: {e_u6}\n"

        if engine in ("auto", "pycdc"):
            pycdc_bin = "/usr/local/bin/pycdc"
            if os.path.exists(pycdc_bin):
                proc = subprocess.run(
                    [pycdc_bin, tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    src = proc.stdout
                    if decode_big5:
                        src = decode_big5_literals(src)
                    return True, "pycdc", src
                if u6_src.strip():
                    if decode_big5:
                        u6_src = decode_big5_literals(u6_src)
                    return True, "uncompyle6(partial)", u6_src
                return False, "pycdc", f"# pycdc failed: {proc.stderr}\n{proc.stdout}\n"

        if u6_src.strip():
            if decode_big5:
                u6_src = decode_big5_literals(u6_src)
            return True, "uncompyle6(partial)", u6_src
        return False, "none", "# Decompilation failed in both uncompyle6 and pycdc\n"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ============================================================================
# 5. Archive Readers & Parallel Worker Tasks
# ============================================================================

def _worker_data_fls(task: tuple[str, bytes, str, str | None, str, bool]) -> dict[str, Any]:
    rel_path, raw_bytes, out_dir, pyc_dir, engine, decode_big5 = task
    rel_path = rel_path.replace("\\", "/")
    out_py = Path(out_dir) / Path(rel_path).with_suffix(".py")
    out_py.parent.mkdir(parents=True, exist_ok=True)
    try:
        pyc_data = transpile_py27_pyo_bytes(raw_bytes)
        if pyc_dir:
            p_pyc = Path(pyc_dir) / Path(rel_path).with_suffix(".pyc")
            p_pyc.parent.mkdir(parents=True, exist_ok=True)
            p_pyc.write_bytes(pyc_data)
        ok, used_eng, src = decompile_pyc_bytes(pyc_data, engine=engine, decode_big5=decode_big5)
        out_py.write_text(src, encoding="utf-8")
        return {"path": str(out_py), "rel": rel_path, "ok": ok, "engine": used_eng}
    except Exception as exc:
        return {"path": str(out_py), "rel": rel_path, "ok": False, "engine": "error", "error": str(exc)}


def _decode_segments(exp: bytes, keys: list[int], bounds: list[int]) -> bytes:
    pts = [0] + list(bounds) + [len(exp)]
    return b"".join(
        exp[pts[i] : pts[i + 1]].translate(XTABS[keys[i]]) for i in range(5)
    )


def _decode_pieces(exp: bytes, pieces: list[tuple[int, int]]) -> bytes:
    """按 [(起始偏移, 密钥), ...] 分段解密（段数不限）。"""
    pieces = sorted(pieces)
    pts = [start for start, _ in pieces] + [len(exp)]
    return b"".join(
        exp[pts[i] : pts[i + 1]].translate(XTABS[pieces[i][1]])
        for i in range(len(pieces))
    )


class _WalkFail(Exception):
    """严格步进在 pos 处撞上结构不可能的对象。"""

    def __init__(self, pos: int):
        super().__init__(pos)
        self.pos = pos


def _strict_walk(data: bytes) -> int:
    """按标准 Python 2.5 marshal 语法严格步进（每步做边界检查）。

    完整走完返回 len(data)；否则抛 _WalkFail(第一个不可能对象的偏移)。
    转译器的 pos 计数在长度字段异常时会飞出界外、无法当作进度，
    本函数专供接缝修复当“哪套边界更可信”的裁判。
    """
    n = len(data)
    pos = 0

    def take(k: int) -> None:
        nonlocal pos
        if pos + k > n:
            raise _WalkFail(pos)
        pos += k

    def u32() -> int:
        nonlocal pos
        if pos + 4 > n:
            raise _WalkFail(pos)
        v = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        return v

    def walk() -> None:
        nonlocal pos
        if pos >= n:
            raise _WalkFail(pos)
        start = pos
        t = data[pos]
        pos += 1
        tc = chr(t)
        if tc in "0NFTS.":
            return
        if tc in ("i", "R"):
            take(4)
            return
        if tc in ("I", "g"):
            take(8)
            return
        if tc == "l":
            digits = struct.unpack_from("<i", data, pos)[0] \
                if pos + 4 <= n else 0
            take(4 + abs(digits) * 2)
            return
        if tc in ("s", "t", "u"):
            ln = u32()
            if ln > n - pos:
                raise _WalkFail(start)
            take(ln)
            return
        if tc in ("f", "x"):
            if pos >= n:
                raise _WalkFail(pos)
            take(1 + data[pos])
            return
        if tc in ("(", "[", "<", ">"):
            cnt = u32()
            if cnt > n - pos:
                raise _WalkFail(start)
            for _ in range(cnt):
                walk()
            return
        if tc == "{":
            while True:
                if pos >= n:
                    raise _WalkFail(pos)
                if data[pos] == ord("0"):
                    pos += 1
                    return
                walk()
                walk()
        if tc == "c":
            take(16)
            walk()  # co_code
            for _ in range(5):  # consts/names/varnames/freevars/cellvars
                walk()
            walk()  # co_filename
            walk()  # co_name
            take(4)  # co_firstlineno
            walk()  # co_lnotab
            return
        raise _WalkFail(start)

    walk()
    return pos


def _strict_progress(dec: bytes) -> int:
    """完整步进给满分 len(dec)+1，否则给第一个失败对象的偏移。"""
    try:
        return _strict_walk(dec) + 1
    except _WalkFail as exc:
        return exc.pos


def _transpile_once(
    dec: bytes, exp: bytes, keys: list[int], bounds: list[int]
) -> tuple[bytes | None, str | None]:
    """转译一次；成功返回 (pyc, co_filename)。"""
    tr = Py25MarshalTranspiler(dec, exp, keys, bounds)
    try:
        tr.transpile_object()
    except Exception:
        return None, None
    if tr.pos != len(dec):
        return None, None
    return bytes(tr.out), tr.filename


def _decompile_ok(pyc: bytes, engine: str, decode_big5: bool) -> bool:
    ok, _used, _src = decompile_pyc_bytes(
        pyc, engine=engine, decode_big5=decode_big5)
    return ok


def _repair_by_shifting(
    exp: bytes, keys: list[int], bounds: list[int],
    engine: str, decode_big5: bool,
) -> tuple[bytes, str | None, list[int], list[int]] | None:
    """第 1 层修复：目录密钥可信、仅分段边界有偏差时逐缝移位。

    背景：script_fls_keys.json 的边界可有偏差（catalog 解法个位数、
    fallback 解法可达上千），缝口附近若干字节会被邻段密钥解密；
    一旦落在字符串长度/元组计数等结构字段上，步进即脱轨。以严格
    步进的完成度为裁判，逐缝在 ±1600 内按“离目录值由近及远”试
    移并取完成度最佳者，多缝损坏时多轮推进。仅在内存中进行，
    密钥数据库保持不变。转译尝试总次数按条目大小封顶，防止在
    无望的大条目上空耗。
    """
    cur = list(bounds)
    best = _strict_progress(_decode_segments(exp, keys, cur))
    per_seam = max(400, min(4000, 64_000_000 // max(1, len(exp))))
    for _round in range(5):
        improved = False
        for bi in range(4):
            attempts_left = per_seam
            lo = max(1, cur[bi] - 1600)
            hi = min(len(exp) - 1, cur[bi] + 1600)
            order = sorted(range(lo, hi + 1), key=lambda c: abs(c - cur[bi]))
            seam_best = (best, cur[bi])
            for cand_pos in order:
                if cand_pos == cur[bi] or attempts_left <= 0:
                    continue
                cand = list(cur)
                cand[bi] = cand_pos
                if any(cand[i] >= cand[i + 1] for i in range(3)):
                    continue
                attempts_left -= 1
                cand_dec = _decode_segments(exp, keys, cand)
                pyc, fname = _transpile_once(cand_dec, exp, keys, cand)
                if pyc is not None:
                    if _decompile_ok(pyc, engine, decode_big5):
                        return pyc, fname, list(keys), cand
                    continue
                score = _strict_progress(cand_dec)
                if score > seam_best[0]:
                    seam_best = (score, cand_pos)
            if seam_best[0] > best:
                best, cur[bi] = seam_best
                improved = True
        if not improved:
            return None
    return None


def _pieces_to_keys_bounds(
    pieces: list[tuple[int, int]], total: int
) -> tuple[list[int], list[int]] | None:
    """把逐段求解结果规整为转译器要求的 5 键 4 界形式。

    不足 5 段时在最长一段的中点补一个同钥虚分段点（解密结果
    不变）；超过 5 段则放弃。
    """
    pieces = sorted(pieces)
    while len(pieces) < 5:
        starts = [start for start, _ in pieces] + [total]
        spans = [(starts[i + 1] - starts[i], i) for i in range(len(pieces))]
        span, idx = max(spans)
        if span < 2:
            return None
        pieces.insert(idx + 1, (pieces[idx][0] + span // 2, pieces[idx][1]))
    if len(pieces) > 5:
        return None
    return [k for _, k in pieces], [start for start, _ in pieces[1:]]


def _try_keys_at(
    exp: bytes, pieces: list[tuple[int, int]], f: int
) -> tuple[int, int] | None:
    """在偏移 f 处逐一试 256 把钥匙，返回能续跑最远的 (f, 密钥)。"""
    best = (f, -1)
    for k in range(256):
        if k == pieces[-1][1]:
            continue
        run = _strict_progress(_decode_pieces(exp, pieces + [(f, k)]))
        if run > best[0]:
            best = (run, k)
    # 尾巴不足 5 字节时，完成度 len+1 也要认（不能被 +4 门槛误杀）
    if best[1] >= 0 and (best[0] > f + 4 or best[0] > len(exp)):
        return f, best[1]
    return None


def _resolve_segments(
    exp: bytes,
) -> tuple[list[int], list[int]] | None:
    """第 2 层修复：目录 (密钥, 边界) 整套不可信时从零逐段求解。

    模块流必以代码对象标签 'c' 开头，故第一把钥匙 = exp[0]^0x63。
    其后每当严格步进在 f 处脱轨，就在 f 处试遍 256 把钥匙、取续跑
    最远者作为下一段密钥（结构良好的续跑绵延数千字节，随机钥匙
    数百字节内必脱轨，故判别可靠）；若直接换钥无效，再在 f 附近
    小窗口内联合试 (分段点, 密钥)。
    """
    if not exp:
        return None
    pieces: list[tuple[int, int]] = [(0, exp[0] ^ 0x63)]
    for _stage in range(6):
        dec = _decode_pieces(exp, pieces)
        f = _strict_progress(dec)
        if f > len(exp):
            return _pieces_to_keys_bounds(pieces, len(exp))
        found = _try_keys_at(exp, pieces, f)
        if found is None and len(exp) <= 32768:
            win_best: tuple[int, tuple[int, int] | None] = (f, None)
            for sw in range(max(1, f - 32), min(len(exp) - 1, f + 9)):
                base = [pc for pc in pieces if pc[0] < sw]
                hit = _try_keys_at(exp, base, sw)
                if hit is not None:
                    run = _strict_progress(
                        _decode_pieces(exp, base + [hit]))
                    if run > win_best[0]:
                        win_best = (run, hit)
            found = win_best[1]
        if found is None:
            return None
        # 插入点可能早于上一投机段：弹掉其后的段，保持有序
        pieces = [pc for pc in pieces if pc[0] < found[0]] + [found]
    if _strict_progress(_decode_pieces(exp, pieces)) > len(exp):
        return _pieces_to_keys_bounds(pieces, len(exp))
    return None


def _refs_valid(data: bytes) -> bool:
    """校验驻留字符串引用：每个 'R' 的下标必须小于此前 't' 的个数。"""
    interned = 0
    pos = 0
    n = len(data)

    def walk() -> bool:
        nonlocal pos, interned
        if pos >= n:
            return False
        t = data[pos]
        pos += 1
        tc = chr(t)
        if tc in "0NFTS.":
            return True
        if tc == "i":
            pos += 4
            return True
        if tc == "R":
            if pos + 4 > n:
                return False
            ref = struct.unpack_from("<i", data, pos)[0]
            pos += 4
            return 0 <= ref < interned
        if tc in ("I", "g"):
            pos += 8
            return True
        if tc == "l":
            if pos + 4 > n:
                return False
            dg = struct.unpack_from("<i", data, pos)[0]
            pos += 4 + abs(dg) * 2
            return True
        if tc in ("s", "t", "u"):
            if pos + 4 > n:
                return False
            ln = struct.unpack_from("<I", data, pos)[0]
            pos += 4 + ln
            if pos > n:
                return False
            if tc == "t":
                interned += 1
            return True
        if tc in ("f", "x"):
            if pos >= n:
                return False
            pos += 1 + data[pos]
            return pos <= n
        if tc in ("(", "[", "<", ">"):
            if pos + 4 > n:
                return False
            cnt = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            return all(walk() for _ in range(cnt))
        if tc == "{":
            while True:
                if pos >= n or data[pos] == ord("0"):
                    pos += 1
                    return pos <= n
                if not (walk() and walk()):
                    return False
        if tc == "c":
            pos += 16
            for _ in range(8):
                if not walk():
                    return False
            pos += 4
            return walk()
        return False

    try:
        return walk() and pos == n
    except (IndexError, struct.error):
        return False


def _gbk_score(raw: bytes) -> int:
    """GBK/ASCII 文本合理性打分（缝口取舍时用）。"""
    score = 0
    i = 0
    while i < len(raw):
        b = raw[i]
        if b < 0x80:
            score += 1 if (b in (9, 10, 13) or b >= 0x20) else -2
            i += 1
        elif 0x81 <= b <= 0xFE and i + 1 < len(raw) \
                and 0x40 <= raw[i + 1] <= 0xFE and raw[i + 1] != 0x7F:
            score += 3
            i += 2
        else:
            score -= 3
            i += 1
    return score


def _refine_seams(
    exp: bytes, keys: list[int], bounds: list[int]
) -> list[int]:
    """缝口精修：步行裁判只能定位到“第一个坏对象”，真缝可能在
    其前数十字节内（藏在定长小对象或字符串尾部）。在每条缝
    ±(-64..+8) 内逐一试，取同时通过严格步进与驻留引用校验、
    且缝口两侧 GBK 文本最连贯的位置。"""
    bounds = list(bounds)
    for bi in range(4):
        cur = bounds[bi]
        k_prev, k_next = keys[bi], keys[bi + 1]
        span = 64 if len(exp) <= 65536 else 16
        lo = max((bounds[bi - 1] if bi else 0) + 1, cur - span)
        hi = cur + 8
        if bi < 3:
            hi = min(hi, bounds[bi + 1] - 1)
        best: tuple[tuple[int, int], int] | None = None
        for cand in range(lo, hi + 1):
            trial = list(bounds)
            trial[bi] = cand
            dec = _decode_segments(exp, keys, trial)
            if _strict_progress(dec) <= len(exp):
                continue
            if not _refs_valid(dec):
                continue
            win = exp[max(0, cand - 48) : cand].translate(XTABS[k_prev]) \
                + exp[cand : cand + 48].translate(XTABS[k_next])
            rank = (_gbk_score(win), -abs(cand - cur))
            if best is None or rank > best[0]:
                best = (rank, cand)
        if best is not None:
            bounds[bi] = best[1]
    return bounds


def _beam_resolve(
    exp: bytes, width: int = 200, eval_budget: int = 120000
) -> tuple[list[int], list[int]] | None:
    """第 2 层兜底：光束搜索逐段求解。

    逐段贪心会被“假长跑”带偏（错钥也能多走几十字节），光束
    按完成度全局保留最优的若干状态，微分段（十字节级）也能
    在下一步冲线时胜出。仅用于中小条目（步行评估成本可控）。
    """
    n = len(exp)
    if n > 65536:
        return None
    eval_budget = min(eval_budget, max(1500, 24_000_000 // max(1, n)))
    start = [(0, exp[0] ^ 0x63)]
    beam = [(_strict_progress(_decode_pieces(exp, start)), start)]
    seen = {tuple(start)}
    left = eval_budget
    for _stage in range(5):
        nxt: list[tuple[int, list[tuple[int, int]]]] = []
        for f, pieces in beam:
            if f > n:
                return _pieces_to_keys_bounds(pieces, n)
            if len(pieces) >= 5:
                continue
            cur_key = pieces[-1][1]
            for k in range(256):
                if k == cur_key or left <= 0:
                    continue
                left -= 1
                cand = pieces + [(f, k)]
                run = _strict_progress(_decode_pieces(exp, cand))
                if run > f + 4 or run > n:
                    nxt.append((run, cand))
        if not nxt or left <= 0:
            return None
        nxt.sort(key=lambda t: (t[0], -len(t[1])), reverse=True)
        beam = []
        for run, cand in nxt:
            sig = tuple(cand)
            if sig in seen:
                continue
            seen.add(sig)
            if run > n:
                return _pieces_to_keys_bounds(cand, n)
            beam.append((run, cand))
            if len(beam) >= width:
                break
    return None


def _transpile_with_repair(
    exp: bytes, keys: list[int], bounds: list[int],
    engine: str, decode_big5: bool,
) -> tuple[bytes, str | None, list[int], list[int], bool] | None:
    """转译入口：基线 → 第 1 层移缝修复 → 第 2 层整套重解。

    三者均以“完整转译 + 成功反编译”为验收。成功返回
    (pyc, co_filename, 实际密钥, 实际边界, 是否经修复)。
    """
    dec = _decode_segments(exp, keys, bounds)
    pyc, fname = _transpile_once(dec, exp, keys, bounds)
    if pyc is not None:
        return pyc, fname, list(keys), list(bounds), False
    shifted = _repair_by_shifting(exp, keys, bounds, engine, decode_big5)
    if shifted is not None:
        return *shifted, True
    solved = _resolve_segments(exp)
    if solved is None:
        solved = _beam_resolve(exp)
    if solved is not None:
        skeys, sbounds = solved
        sbounds = _refine_seams(exp, skeys, sbounds)
        dec = _decode_segments(exp, skeys, sbounds)
        pyc, fname = _transpile_once(dec, exp, skeys, sbounds)
        if pyc is not None and _decompile_ok(pyc, engine, decode_big5):
            return pyc, fname, skeys, sbounds, True
    return None


def _worker_script_fls(
    task: tuple[int, int, bytes, list[int], list[int], str, str | None, str, bool]
) -> dict[str, Any]:
    idx, entry_id, exp, keys, bounds, out_dir, pyc_dir, engine, decode_big5 = task
    try:
        got = _transpile_with_repair(exp, keys, bounds, engine, decode_big5)
        if got is None:
            raise ValueError("Python 2.5 marshal transpile failed")
        pyc_data, fname, _rkeys, _rbounds, repaired = got
        rel_path = fname or f"script/unknown/entry_{idx:04d}_{entry_id:08x}.py"
        if not rel_path.endswith(".py"):
            rel_path += ".py"
        out_py = Path(out_dir) / rel_path
        out_py.parent.mkdir(parents=True, exist_ok=True)
        if pyc_dir:
            p_pyc = Path(pyc_dir) / Path(rel_path).with_suffix(".pyc")
            p_pyc.parent.mkdir(parents=True, exist_ok=True)
            p_pyc.write_bytes(pyc_data)
        ok, used_eng, src = decompile_pyc_bytes(
            pyc_data, engine=engine, decode_big5=decode_big5)
        out_py.write_text(src, encoding="utf-8")
        return {"idx": idx, "path": str(out_py), "rel": rel_path, "ok": ok,
                "engine": used_eng, "repaired": repaired}
    except Exception as exc:
        rel_path = f"script/failed/entry_{idx:04d}_{entry_id:08x}.py"
        return {"idx": idx, "path": rel_path, "rel": rel_path, "ok": False,
                "engine": "marshal_err", "error": str(exc)}


def process_data_fls(
    input_path: Path,
    out_dir: Path,
    pyc_dir: Path | None,
    engine: str,
    decode_big5: bool,
    entry_filter: str | None,
    workers: int,
) -> dict[str, Any]:
    """Processes `data/data.fls` or an unpacked directory of `.pyo` files."""
    tasks = []
    if input_path.is_dir():
        for p in sorted(input_path.rglob("*.pyo")):
            rel = str(p.relative_to(input_path)).replace("\\", "/")
            if entry_filter and entry_filter not in rel:
                continue
            tasks.append((rel, p.read_bytes(), str(out_dir), str(pyc_dir) if pyc_dir else None, engine, decode_big5))
    else:
        with tempfile.TemporaryDirectory() as tmp_unpack:
            fls_tool = Path(__file__).resolve().parents[1] / "data-parser" / "universal_fls_tool.py"
            subprocess.run(
                [sys.executable, str(fls_tool), "unpack", str(input_path), tmp_unpack],
                check=True,
                capture_output=True,
            )
            tmp_root = Path(tmp_unpack)
            for p in sorted(tmp_root.rglob("*")):
                if not p.is_file():
                    continue
                rel = str(p.relative_to(tmp_root)).replace("\\", "/")
                if entry_filter and entry_filter not in rel:
                    continue
                raw = p.read_bytes()
                if p.suffix.lower() == ".pyo" and raw[:4] == b"\x03\xf3\x0d\x0a":
                    tasks.append((rel, raw, str(out_dir), str(pyc_dir) if pyc_dir else None, engine, decode_big5))
                else:
                    dst = out_dir / rel
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_bytes(raw)

    t0 = time.time()
    if workers > 1 and len(tasks) > 1:
        with mp.Pool(workers) as pool:
            results = pool.map(_worker_data_fls, tasks)
    else:
        results = [_worker_data_fls(t) for t in tasks]

    ok_cnt = sum(1 for r in results if r["ok"])
    print(f"[data.fls] Transpiled & decompiled {ok_cnt}/{len(results)} .pyo modules in {time.time() - t0:.2f}s")
    return {"total": len(results), "ok": ok_cnt, "results": results}


def process_script_fls(
    input_path: Path,
    out_dir: Path,
    pyc_dir: Path | None,
    engine: str,
    decode_big5: bool,
    entry_filter: str | None,
    limit: int | None,
    workers: int,
) -> dict[str, Any]:
    """Processes `data/script.fls` (5,002 Python 2.5 modules)."""
    keys_file = Path(__file__).resolve().parent / "script_fls_keys.json"
    solved_db: dict[str, dict[str, Any]] = json.loads(keys_file.read_text(encoding="utf-8"))

    catalog_csv = (
        Path(__file__).resolve().parents[2]
        / "work/dream-world-connect-login-map/notes/task-b-脚本分析/script-catalog.csv"
    )
    fn_map: dict[int, str] = {}
    if catalog_csv.exists():
        import csv
        for r in csv.DictReader(catalog_csv.open(encoding="utf-8")):
            fn_map[int(r["index"])] = r.get("filename", "")

    arch = input_path.read_bytes()
    entry_count = struct.unpack_from("<I", arch, 4)[0]
    idx_off = struct.unpack_from("<I", arch, 8)[0]

    tasks = []
    for idx in range(entry_count):
        if entry_filter:
            if entry_filter.isdigit():
                if idx != int(entry_filter):
                    continue
            else:
                cat_fn = fn_map.get(idx, "").replace("\\", "/")
                if entry_filter not in cat_fn:
                    continue
        raw = struct.unpack_from("<IIII", arch, idx_off + idx * 16)
        entry_id, r1, r2, r3 = raw
        clen = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ r2) & 0xFFFFFFFF
        doff = (((r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ r3) & 0xFFFFFFFF
        exp = zlib.decompress(arch[doff : doff + clen])
        info = solved_db[str(idx)]
        tasks.append(
            (
                idx,
                entry_id,
                exp,
                info["keys"],
                info["bounds"],
                str(out_dir),
                str(pyc_dir) if pyc_dir else None,
                engine,
                decode_big5,
            )
        )
        if limit and len(tasks) >= limit:
            break

    t0 = time.time()
    if workers > 1 and len(tasks) > 1:
        with mp.Pool(workers) as pool:
            results = pool.map(_worker_script_fls, tasks)
    else:
        results = [_worker_script_fls(t) for t in tasks]

    ok_cnt = sum(1 for r in results if r["ok"])
    fixed_cnt = sum(1 for r in results if r.get("repaired"))
    print(f"[script.fls] Transpiled & decompiled {ok_cnt}/{len(results)} modules in {time.time() - t0:.2f}s"
          + (f" (其中 {fixed_cnt} 条靠边界修复救回)" if fixed_cnt else ""))
    return {"total": len(results), "ok": ok_cnt, "results": results}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MXSJ TW 2022 Python Bytecode Transpiler & Batch Decompiler"
    )
    parser.add_argument("input", type=Path, help="Path to data.fls, script.fls, or unpacked .pyo directory")
    parser.add_argument("output", type=Path, help="Output directory for decompiled .py files")
    parser.add_argument("--emit-pyc", type=Path, default=None, help="Optional directory to write standard .pyc files")
    parser.add_argument("--engine", choices=["auto", "uncompyle6", "pycdc"], default="auto")
    parser.add_argument("--no-big5", action="store_true", help="Disable Big5 (cp950) string literal decoding")
    parser.add_argument("--entry", type=str, default=None, help="Filter by entry index (e.g. 516) or path substring (e.g. netserver)")
    parser.add_argument("--limit", type=int, default=None, help="Max entries to process (for script.fls)")
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4)), help="Parallel worker processes")
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    if args.emit_pyc:
        args.emit_pyc.mkdir(parents=True, exist_ok=True)

    is_script_fls = False
    if args.input.is_file():
        magic = args.input.open("rb").read(4)
        if magic == b"0SLF":
            is_script_fls = True

    if is_script_fls:
        process_script_fls(
            args.input,
            args.output,
            args.emit_pyc,
            args.engine,
            not args.no_big5,
            args.entry,
            args.limit,
            args.workers,
        )
    else:
        process_data_fls(
            args.input,
            args.output,
            args.emit_pyc,
            args.engine,
            not args.no_big5,
            args.entry,
            args.workers,
        )


if __name__ == "__main__":
    main()
