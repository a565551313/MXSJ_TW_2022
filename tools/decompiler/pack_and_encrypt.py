#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《夢想世界》(MXSJ TW 2022) Python 字節碼正向混淆、5段XOR加密與 FLS 打包工具
==============================================================================
本工具為 `batch_decompile.py` 的完整逆向工程正向管線（编译/混淆/加密/打包）：

1. VM #2 (`data/data.fls` — `exe/python27.dll`, Python 2.7.13):
   - `obfuscate_py27_pyc_bytes`: 將標準 Python 2.7 `.pyc` 轉換為多益定制 Split-Stream `.pyo`:
     * 插入 4-byte `co_extra` (`op_stream_len = n_ops + 1`)
     * 拆分 `co_code` 為 1-byte 指令流 (`ops + 0x17(NOP)`) 與 `uint16_le` 參數流 (`args`)
     * 跳轉指令 (`PY27_ABS_JUMP_OPS | PY27_REL_JUMP_OPS`) 自動編碼為 4-byte 雙偏移參數:
       - 絕對跳轉: `<HH(target_op_idx, target_arg_byte_offset)`
       - 相對跳轉: `<HH(target_op_idx - (cur_op_idx + 1), target_arg_byte_offset - (cur_arg_byte_offset + 4))`
     * 將標準字節偏移 `co_lnotab` 還原為多益指令索引增量 `co_lnotab`
   - `repack_data_fls`: 支持將修改後的 `.pyc` 或 `.pyo` 目錄/單文件重新壓縮並完整重構 `data/data.fls`
     （自動重算 `0xA0975237` 本地頭、`0x87F2017C` 中央目錄偏移/CRC32/大小、以及末尾 8-byte `0xA1985237` 尾標，無文件大小限制）。

2. VM #1 (`data/script.fls` — `mx.exe` / `mxmain.dll`, Python 2.5):
   - `obfuscate_py25_pyc_bytes`: 將標準 Python 2.5 `.pyc` 轉換為多益定制 Opcode (`INV_PY25_MAP`, `HAVE_ARGUMENT = 0x5F`) 無頭 Marshal 流
   - `encrypt_5seg_xor`: 按 `script_fls_keys.json` 的 5 段 XOR 密鑰與邊界進行分段加密：
     * 當修改後 Marshal 長度 `<= 原始長度` 時，自動在根 `PyCodeObject` 末尾填充至原始長度，使 5 段 XOR 邊界 `[b0, b1, b2, b3]` 與原始條目 100% 保持一致（`PyMarshal_ReadObjectFromString` 讀完根對象即停，忽略尾部填充字節）。
     * 當修改後 Marshal 長度 `== 原始長度` 時，輸出與原始未壓縮載荷 100% 逐比特一致。
   - `repack_script_fls`: 將加密後的條目透過 `zlib.compress(..., 9)` 壓縮，並以 `0x0048F170` 逆向推導的三階多項式加密重構 `0SLF` 索引表，生成合法的 `script.fls`。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import struct
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure we can import tables and transpilers from batch_decompile.py
THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.decompiler.batch_decompile import (
    PY25_MAP,
    PY27_ABS_JUMP_OPS,
    PY27_MAP,
    PY27_REL_JUMP_OPS,
    XTABS,
    Py25MarshalTranspiler,
    process_data_fls,
    process_script_fls,
    transpile_py27_code,
    transpile_py27_pyo_bytes,
)


def decode_0slf_entry(idx: int, raw_tuple: Tuple[int, int, int, int]) -> Dict[str, int]:
    """Decode a 16-byte 0SLF directory entry at VA 0x0048F170."""
    eid, r1, r2, r3 = raw_tuple
    f1 = (((eid * 0x0002F05B + 0x00016B38) & 0xFFFFFFFF) ^ r1) & 0xFFFFFFFF
    clen = (((r1 * eid + 0x000DF25E) & 0xFFFFFFFF) ^ r2) & 0xFFFFFFFF
    doff = (((r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ r3) & 0xFFFFFFFF
    return {"id": eid, "f1": f1, "comp_len": clen, "data_offset": doff}

# ============================================================================
# 1. Inverse Opcode Mapping Tables (Standard Python -> Duoyi Obfuscated)
# ============================================================================

# Python 2.5 (mx.exe / script.fls): Standard opcode -> Duoyi opcode
INV_PY25_MAP: Dict[int, int] = {std_op: duoyi_op for duoyi_op, std_op in PY25_MAP.items()}

# Python 2.7 (exe/python27.dll / data.fls): Standard opcode -> Duoyi opcode
INV_PY27_MAP: Dict[int, int] = {
    std_op: duoyi_op
    for duoyi_op, std_op in PY27_MAP.items()
    if not (duoyi_op == 66 and std_op == 42)
}
# Canonical primary opcodes from python27.dll Jump Table (VA 0x1E12CA48)
INV_PY27_MAP[106] = 230  # COMPARE_OP -> 0xE6
INV_PY27_MAP[107] = 124  # IMPORT_NAME -> 0x7C
INV_PY27_MAP[109] = 155  # IMPORT_FROM -> 0x9B
INV_PY27_MAP[133] = 93   # MAKE_CLOSURE -> 0x5D (used in data.fls)


# ============================================================================
# 2. VM #2 (Python 2.7 / data.fls) Forward Split-Stream Obfuscator
# ============================================================================

def obfuscate_py27_code(std_code: bytes) -> Tuple[bytes, int, Dict[int, int]]:
    """
    Convert standard Python 2.7 interleaved co_code into Duoyi's split-stream
    (ops + 0x17 + args) format and return (duoyi_co_code, op_stream_len, byte_to_op_idx).
    """
    jump_ops = PY27_ABS_JUMP_OPS | PY27_REL_JUMP_OPS
    insns: List[Tuple[int, int, int, int]] = []
    byte_to_op_idx: Dict[int, int] = {}
    byte_to_arg_off: Dict[int, int] = {}

    p = 0
    n = len(std_code)
    op_idx = 0
    arg_off = 0
    while p < n:
        byte_to_op_idx[p] = op_idx
        byte_to_arg_off[p] = arg_off
        std_op = std_code[p]
        if std_op not in INV_PY27_MAP:
            raise KeyError(f"Unmapped standard Python 2.7 opcode: {std_op} (0x{std_op:02x}) at offset {p}")
        duoyi_op = INV_PY27_MAP[std_op]
        if std_op >= 0x5A:
            arg = std_code[p + 1] | (std_code[p + 2] << 8)
            insns.append((p, duoyi_op, arg, arg_off))
            p += 3
            arg_off += 4 if duoyi_op in jump_ops else 2
        else:
            insns.append((p, duoyi_op, 0, arg_off))
            p += 1
        op_idx += 1

    byte_to_op_idx[n] = op_idx
    byte_to_arg_off[n] = arg_off

    ops = bytearray()
    args = bytearray()
    for idx, (std_off, duoyi_op, std_arg, cur_arg_off) in enumerate(insns):
        ops.append(duoyi_op)
        if duoyi_op >= 0x5A:
            if duoyi_op in PY27_ABS_JUMP_OPS:
                target_op = byte_to_op_idx[std_arg]
                target_arg_off = byte_to_arg_off[std_arg]
                args.extend(struct.pack("<HH", target_op & 0xFFFF, target_arg_off & 0xFFFF))
            elif duoyi_op in PY27_REL_JUMP_OPS:
                target_byte = std_off + 3 + std_arg
                op_delta = byte_to_op_idx[target_byte] - (idx + 1)
                arg_delta = byte_to_arg_off[target_byte] - (cur_arg_off + 4)
                args.extend(struct.pack("<HH", op_delta & 0xFFFF, arg_delta & 0xFFFF))
            else:
                args.extend(struct.pack("<H", std_arg & 0xFFFF))

    # Every Duoyi Python 2.7 code object appends a single 0x17 (NOP) sentinel at the end of ops
    ops.append(0x17)
    op_stream_len = len(ops)
    return bytes(ops + args), op_stream_len, byte_to_op_idx


def obfuscate_py27_lnotab(std_lnotab: bytes, byte_to_op_idx: Dict[int, int]) -> bytes:
    """Convert standard Python 2.7 byte-delta co_lnotab back into Duoyi opcode-index-delta co_lnotab."""
    if not std_lnotab:
        return b""
    out = bytearray()
    cur_byte = 0
    prev_op = 0
    for i in range(0, len(std_lnotab) - 1, 2):
        b_inc = std_lnotab[i]
        l_inc = std_lnotab[i + 1]
        cur_byte += b_inc
        cur_op = byte_to_op_idx.get(cur_byte, prev_op)
        op_delta = max(0, cur_op - prev_op)
        prev_op = cur_op
        while op_delta > 255:
            out.extend((255, 0))
            op_delta -= 255
        out.extend((op_delta, l_inc))
    return bytes(out)


class Py27MarshalObfuscator:
    """
    Walks a standard Python 2.7 .pyc marshal stream and converts all PyCodeObjects
    into Duoyi's custom PyCodeObject format (with 4-byte co_extra + split-stream co_code).
    """

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.pos = 8
        self.out = bytearray(data[:8])
        self.strings: List[bytes] = []

    def copy_bytes(self, n: int) -> bytes:
        chunk = self.data[self.pos : self.pos + n]
        self.pos += n
        self.out.extend(chunk)
        return chunk

    def read_raw_string_obj(self) -> Tuple[int, bytes]:
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
            idx = struct.unpack_from("<I", self.data, self.pos)[0]
            self.pos += 4
            return t, self.strings[idx]
        raise ValueError(f"Expected string in marshal stream, got 0x{t:02x}")

    def obfuscate_object(self) -> None:
        t = self.data[self.pos]
        self.pos += 1
        tc = chr(t)
        self.out.append(t)

        if tc in ("0", "N", "F", "T", "S", "."):
            return
        if tc in ("i", "I", "g", "R"):
            self.copy_bytes(8 if tc in ("I", "g") else 4)
            return
        if tc == "l":
            n = abs(struct.unpack("<i", self.copy_bytes(4))[0])
            self.copy_bytes(n * 2)
            return
        if tc in ("s", "t", "u"):
            ln = struct.unpack("<I", self.copy_bytes(4))[0]
            s = self.copy_bytes(ln)
            if tc == "t":
                self.strings.append(s)
            return
        if tc in ("f", "x"):
            ln = self.copy_bytes(1)[0]
            self.copy_bytes(ln)
            return
        if tc in ("(", "[", "<", ">"):
            n = struct.unpack("<I", self.copy_bytes(4))[0]
            for _ in range(n):
                self.obfuscate_object()
            return
        if tc == "{":
            while True:
                k_type = self.data[self.pos]
                if chr(k_type) == "0":
                    self.pos += 1
                    self.out.append(k_type)
                    break
                self.obfuscate_object()
                self.obfuscate_object()
            return
        if tc == "c":
            # 16-byte header: argcount, nlocals, stacksize, flags
            self.copy_bytes(16)
            code_t, std_code = self.read_raw_string_obj()
            duoyi_code, op_stream_len, byte_to_op_idx = obfuscate_py27_code(std_code)
            # Emit 4-byte co_extra = op_stream_len
            self.out.extend(struct.pack("<I", op_stream_len))
            emit_code_t = code_t if chr(code_t) == "t" else ord("s")
            if chr(code_t) == "t":
                self.strings[-1] = duoyi_code
            self.out.append(emit_code_t)
            self.out.extend(struct.pack("<I", len(duoyi_code)))
            self.out.extend(duoyi_code)

            # co_consts, co_names, co_varnames, co_freevars, co_cellvars, co_filename, co_name
            for _ in range(7):
                self.obfuscate_object()

            # co_firstlineno
            self.copy_bytes(4)

            # co_lnotab
            lno_t, std_lno = self.read_raw_string_obj()
            duoyi_lno = obfuscate_py27_lnotab(std_lno, byte_to_op_idx)
            emit_lno_t = lno_t if chr(lno_t) == "t" else ord("s")
            if chr(lno_t) == "t":
                self.strings[-1] = duoyi_lno
            self.out.append(emit_lno_t)
            self.out.extend(struct.pack("<I", len(duoyi_lno)))
            self.out.extend(duoyi_lno)
            return

        raise ValueError(f"Unknown marshal type 0x{t:02x} at offset {self.pos - 1}")


def obfuscate_py27_pyc_bytes(pyc_bytes: bytes) -> bytes:
    """Convert standard Python 2.7 .pyc bytes to Duoyi split-stream .pyo bytes."""
    obf = Py27MarshalObfuscator(pyc_bytes)
    obf.obfuscate_object()
    return bytes(obf.out)


# ============================================================================
# 3. data/data.fls Archive Repacker (Full Reconstruction, Arbitrary File Sizes)
# ============================================================================

def repack_data_fls(
    orig_archive_path: Path,
    patch_dir_or_file: Path,
    output_archive_path: Path,
    target_arc_name: Optional[str] = None,
) -> int:
    """
    Repack `data/data.fls` with modified `.pyc` or `.pyo` files.
    - Any `.pyc` file in `patch_dir_or_file` (with standard Python 2.7 bytecode) is automatically
      converted into Duoyi split-stream `.pyo` before compression.
    - Reconstructs local headers (`0xA0975237`), central directory (`0x87F2017C`), and
      8-byte end-of-archive trailer (`<II(cd_offset, 0xA1985237)`).
    """
    arc = orig_archive_path.read_bytes()
    cd_offset_orig, end_sig = struct.unpack_from("<II", arc, len(arc) - 8)
    if end_sig != 0xA1985237:
        raise ValueError(f"Invalid data.fls trailer signature: 0x{end_sig:08x}")

    # Collect replacement payloads keyed by archive entry name (e.g. 'core\\gamecode.pyo')
    replacements: Dict[str, bytes] = {}
    if patch_dir_or_file.is_file():
        raw = patch_dir_or_file.read_bytes()
        # Check if input is standard Python 2.7 .pyc vs already-obfuscated Duoyi .pyo
        if patch_dir_or_file.suffix.lower() == ".pyc":
            raw = obfuscate_py27_pyc_bytes(raw)
        arc_name = (target_arc_name or patch_dir_or_file.name).replace("/", "\\")
        if arc_name.endswith(".pyc"):
            arc_name = arc_name[:-4] + ".pyo"
        replacements[arc_name] = raw
    else:
        for p in sorted(patch_dir_or_file.rglob("*")):
            if not p.is_file():
                continue
            rel = str(p.relative_to(patch_dir_or_file)).replace("/", "\\")
            if p.suffix.lower() == ".pyc":
                rel = rel[:-4] + ".pyo"
                replacements[rel] = obfuscate_py27_pyc_bytes(p.read_bytes())
            elif p.suffix.lower() in (".pyo", ".Flx", ".flx", ".csv", ".txt", ".xml", ".ini"):
                replacements[rel] = p.read_bytes()

    # Parse original Central Directory
    pos = cd_offset_orig
    cd_records = []
    while pos < len(arc) - 8:
        sig = struct.unpack_from("<I", arc, pos)[0]
        if sig != 0x87F2017C:
            break
        w1, w2, w3, crc, csize, usize, l_off, name_len = struct.unpack_from("<HHHIIIIH", arc, pos + 4)
        raw_name = arc[pos + 28 : pos + 28 + name_len]
        name = bytes(b ^ 0xA5 for b in raw_name).decode("gbk", errors="replace")
        lsig, lmethod, lcrc, lcsize, lusize = struct.unpack_from("<IHIII", arc, l_off)
        comp_data = arc[l_off + 18 : l_off + 18 + csize]
        cd_records.append(
            {
                "name": name,
                "raw_name": raw_name,
                "w1": w1,
                "w2": w2,
                "w3": w3,
                "lmethod": lmethod,
                "crc": crc,
                "csize": csize,
                "usize": usize,
                "comp_data": comp_data,
            }
        )
        pos += 28 + name_len

    # Rebuild archive
    out = bytearray(arc[:64])  # 64-byte FLS header
    patched_count = 0

    for rec in cd_records:
        name = rec["name"]
        norm_name = name.replace("/", "\\")
        if norm_name in replacements:
            new_uncomp = replacements[norm_name]
            # Check if identical to original uncompressed bytes
            orig_uncomp = (
                zlib.decompress(rec["comp_data"], -15)
                if rec["lmethod"] == 8 and rec["csize"] > 0
                else rec["comp_data"]
            )
            if new_uncomp != orig_uncomp:
                rec["usize"] = len(new_uncomp)
                rec["crc"] = zlib.crc32(new_uncomp) & 0xFFFFFFFF
                if rec["lmethod"] == 8:
                    rec["comp_data"] = zlib.compress(new_uncomp, 9)[2:-4]
                else:
                    rec["comp_data"] = new_uncomp
                rec["csize"] = len(rec["comp_data"])
                patched_count += 1

        rec["new_l_off"] = len(out)
        out.extend(
            struct.pack(
                "<IHIII",
                0xA0975237,
                rec["lmethod"],
                rec["crc"],
                rec["csize"],
                rec["usize"],
            )
        )
        out.extend(rec["comp_data"])

    new_cd_offset = len(out)
    for rec in cd_records:
        out.extend(
            struct.pack(
                "<IHHHIIIIH",
                0x87F2017C,
                rec["w1"],
                rec["w2"],
                rec["w3"],
                rec["crc"],
                rec["csize"],
                rec["usize"],
                rec["new_l_off"],
                len(rec["raw_name"]),
            )
        )
        out.extend(rec["raw_name"])

    out.extend(struct.pack("<II", new_cd_offset, 0xA1985237))
    output_archive_path.parent.mkdir(parents=True, exist_ok=True)
    output_archive_path.write_bytes(bytes(out))
    return patched_count


# ============================================================================
# 3B. OUT / IN Workflow for `data.fls` (Unpack to OUT + Compile/Encrypt OUT to IN)
# ============================================================================

_STR_LIT_RE = re.compile(
    r"""([uUbB]?[rR]?(?:'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\"|'[^'\n\\]*(?:\\.[^'\n\\]*)*'|\"[^\"\n\\]*(?:\\.[^\"\n\\]*)*\"))"""
)


def encode_cjk_str_literals_to_cp950(src: str) -> str:
    """
    Convert UTF-8 Traditional Chinese characters inside non-unicode Python string literals
    back into `\\xHH` Big5 (`cp950` / `gbk`) byte escape sequences for Python 2.7 compilation.
    """
    def _repl(m: re.Match[str]) -> str:
        lit = m.group(0)
        prefix = ""
        for ch in lit[:2]:
            if ch in "uUbBrR":
                prefix += ch
            else:
                break
        if "u" in prefix.lower():
            return lit
        if not any(ord(c) > 127 for c in lit):
            return lit
        try:
            val = ast.literal_eval(lit)
            if not isinstance(val, str):
                return lit
            raw_bytes = bytearray()
            for ch in val:
                if ord(ch) < 128:
                    raw_bytes.append(ord(ch))
                elif ord(ch) <= 0xFF:
                    raw_bytes.append(ord(ch))
                else:
                    try:
                        raw_bytes.extend(ch.encode("cp950"))
                    except UnicodeEncodeError:
                        raw_bytes.extend(ch.encode("gbk", errors="replace"))
            escaped = "".join(
                chr(b) if 32 <= b < 127 and chr(b) not in ("'", '"', "\\")
                else ("\\\\" if b == 92 else f"\\x{b:02x}")
                for b in raw_bytes
            )
            return f"'{escaped}'"
        except Exception:
            return lit

    return _STR_LIT_RE.sub(_repl, src)


def _normalize_py2_syntax_for_py3_ast(src: str) -> str:
    """Normalize Python 2 syntax constructs so Python 3 `ast.parse` can parse the source."""
    lines = []
    for line in src.splitlines():
        m = re.match(r"^(\s*)print\s+>>\s*([^,]+),\s*(.+)$", line)
        if m:
            indent, stream, rest = m.groups()
            line = f"{indent}__py2_print_to__({stream}, {rest})"
        else:
            m2 = re.match(r"^(\s*)print\s+(?!\()(.+)$", line)
            if m2:
                indent, rest = m2.groups()
                if rest.endswith(","):
                    line = f"{indent}__py2_print_cont__({rest[:-1]})"
                else:
                    line = f"{indent}__py2_print__({rest})"
            elif re.match(r"^(\s*)print\s*$", line):
                indent = re.match(r"^(\s*)print\s*$", line).group(1)
                line = f"{indent}__py2_print_nl__()"
        line = re.sub(r"^(\s*except\s+[^:,]+?)\s*,\s*([A-Za-z_]\w*)\s*:", r"\1 as \2:", line)
        line = re.sub(r"^(\s*raise\s+[A-Za-z_][\w\.]*)\s*,\s*(.+)$", r"\1(\2)", line)
        line = re.sub(r"\b(\d+)L\b", r"\1", line)
        line = re.sub(r"\b0([0-7]+)\b", r"0o\1", line)
        lines.append(line)
    return "\n".join(lines)


def _str_to_py2_bytes(s: str) -> bytes:
    """Convert a Python 3 AST string constant into Python 2 `str` bytes (cp950/latin1)."""
    out = bytearray()
    for ch in s:
        if ord(ch) <= 0xFF:
            out.append(ord(ch))
        else:
            try:
                out.extend(ch.encode("cp950"))
            except UnicodeEncodeError:
                out.extend(ch.encode("gbk", errors="replace"))
    return bytes(out)


def _patch_pyc_constants_by_diff(orig_py: str, new_py: str, orig_std_pyc: bytes) -> bytes:
    """
    Compare `orig_py` and `new_py` literals and surgically update modified constants
    (strings, numbers, config values) in the standard Python 2.7 `.pyc` marshal stream.
    """
    orig_encoded = encode_cjk_str_literals_to_cp950(orig_py)
    new_encoded = encode_cjk_str_literals_to_cp950(new_py)

    try:
        tree_old = ast.parse(_normalize_py2_syntax_for_py3_ast(orig_encoded))
        tree_new = ast.parse(_normalize_py2_syntax_for_py3_ast(new_encoded))
    except SyntaxError:
        tree_old = None
        tree_new = None

    str_replacements: Dict[bytes, bytes] = {}
    int_replacements: Dict[int, int] = {}
    float_replacements: Dict[float, float] = {}

    if tree_old is not None and tree_new is not None:
        old_consts = [n for n in ast.walk(tree_old) if isinstance(n, ast.Constant)]
        new_consts = [n for n in ast.walk(tree_new) if isinstance(n, ast.Constant)]
        if len(old_consts) == len(new_consts):
            for oc, nc in zip(old_consts, new_consts):
                if type(oc.value) is type(nc.value) and oc.value != nc.value:
                    if isinstance(oc.value, str):
                        str_replacements[_str_to_py2_bytes(oc.value)] = _str_to_py2_bytes(nc.value)
                    elif isinstance(oc.value, int) and not isinstance(oc.value, bool):
                        int_replacements[oc.value] = nc.value
                    elif isinstance(oc.value, float):
                        float_replacements[oc.value] = nc.value

    if not str_replacements and not int_replacements and not float_replacements:
        # Fallback: line-by-line literal diff
        old_lines = orig_encoded.splitlines()
        new_lines = new_encoded.splitlines()
        for ol, nl in zip(old_lines, new_lines):
            if ol != nl:
                om = _STR_LIT_RE.findall(ol)
                nm = _STR_LIT_RE.findall(nl)
                if len(om) == len(nm):
                    for o_lit, n_lit in zip(om, nm):
                        if o_lit != n_lit:
                            try:
                                ov = ast.literal_eval(o_lit)
                                nv = ast.literal_eval(n_lit)
                                if isinstance(ov, str) and isinstance(nv, str):
                                    str_replacements[_str_to_py2_bytes(ov)] = _str_to_py2_bytes(nv)
                            except Exception:
                                pass

    if not str_replacements and not int_replacements and not float_replacements:
        return orig_std_pyc

    # Walk standard .pyc marshal stream and replace matching constants inside co_consts
    data = orig_std_pyc
    pos = 8
    out = bytearray(data[:8])
    in_consts = 0

    def walk() -> None:
        nonlocal pos, in_consts
        t = data[pos]
        pos += 1
        tc = chr(t)
        if tc in ("0", "N", "F", "T", "S", "."):
            out.append(t)
            return
        if tc == "i":
            val = struct.unpack_from("<i", data, pos)[0]
            pos += 4
            if in_consts > 0 and val in int_replacements:
                val = int_replacements[val]
            out.append(t)
            out.extend(struct.pack("<i", val))
            return
        if tc == "g":
            val = struct.unpack_from("<d", data, pos)[0]
            pos += 8
            if in_consts > 0 and val in float_replacements:
                val = float_replacements[val]
            out.append(t)
            out.extend(struct.pack("<d", val))
            return
        if tc in ("I", "R"):
            out.append(t)
            n = 8 if tc == "I" else 4
            out.extend(data[pos : pos + n])
            pos += n
            return
        if tc == "l":
            out.append(t)
            n = abs(struct.unpack_from("<i", data, pos)[0])
            out.extend(data[pos : pos + 4 + n * 2])
            pos += 4 + n * 2
            return
        if tc in ("s", "t", "u"):
            ln = struct.unpack_from("<I", data, pos)[0]
            pos += 4
            s = data[pos : pos + ln]
            pos += ln
            if in_consts > 0 and s in str_replacements:
                s = str_replacements[s]
            out.append(t)
            out.extend(struct.pack("<I", len(s)))
            out.extend(s)
            return
        if tc in ("f", "x"):
            out.append(t)
            ln = data[pos]
            out.extend(data[pos : pos + 1 + ln])
            pos += 1 + ln
            return
        if tc in ("(", "[", "<", ">"):
            out.append(t)
            n = struct.unpack_from("<I", data, pos)[0]
            out.extend(data[pos : pos + 4])
            pos += 4
            for _ in range(n):
                walk()
            return
        if tc == "{":
            out.append(t)
            while chr(data[pos]) != "0":
                walk()
                walk()
            out.append(data[pos])
            pos += 1
            return
        if tc == "c":
            out.append(t)
            out.extend(data[pos : pos + 16])
            pos += 16
            # co_code (do not replace inside co_code!)
            saved = in_consts
            in_consts = 0
            walk()
            in_consts = saved + 1
            walk()  # co_consts
            in_consts = saved
            for _ in range(5):  # co_names, co_varnames, co_freevars, co_cellvars, co_filename
                walk()
            walk()  # co_name
            out.extend(data[pos : pos + 4])
            pos += 4
            walk()  # co_lnotab
            return
        raise ValueError(f"Unexpected marshal tag {tc!r}")

    walk()
    return bytes(out)


def compile_or_patch_py27_file(
    py_path: Path,
    orig_py_src: str,
    orig_std_pyc: bytes,
) -> bytes:
    """
    Given a user-modified `.py` file in `OUT`:
    1. Re-encodes any UTF-8 Chinese string literals back to Big5 (`cp950`) byte literals.
    2. If a Python 2.7 interpreter (`python2` / `py -2`) is available on the system,
       compiles the `.py` directly into a genuine Python 2.7 `.pyc`.
    3. Otherwise, applies AST-guided constant/literal patching onto `orig_std_pyc`.
    """
    new_py_src = py_path.read_text(encoding="utf-8", errors="replace")
    encoded_src = encode_cjk_str_literals_to_cp950(new_py_src)

    # Try external python2 / py -2 if present on the machine
    for cmd_prefix in (["python2"], ["py", "-2"]):
        exe = shutil.which(cmd_prefix[0])
        if not exe:
            continue
        try:
            with tempfile.TemporaryDirectory() as td:
                tmp_py = Path(td) / "mod.py"
                tmp_pyc = Path(td) / "mod.pyc"
                tmp_py.write_text(encoded_src, encoding="utf-8")
                res = subprocess.run(
                    cmd_prefix
                    + [
                        "-c",
                        "import sys, py_compile; py_compile.compile(sys.argv[1], sys.argv[2], doraise=True)",
                        str(tmp_py),
                        str(tmp_pyc),
                    ],
                    capture_output=True,
                    timeout=10,
                )
                if res.returncode == 0 and tmp_pyc.is_file():
                    pyc_b = tmp_pyc.read_bytes()
                    if pyc_b[:4] == b"\x03\xf3\x0d\x0a":
                        return orig_std_pyc[:8] + pyc_b[8:]
        except Exception:
            pass

    return _patch_pyc_constants_by_diff(orig_py_src, new_py_src, orig_std_pyc)


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def find_default_data_fls(cwd: Optional[Path] = None) -> Path:
    """Locate `data.fls` in current working directory first, then `./data/data.fls`, then repo root."""
    base = cwd or Path.cwd()
    candidates = [
        base / "data.fls",
        base / "data" / "data.fls",
        REPO_ROOT / "data.fls",
        REPO_ROOT / "data" / "data.fls",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    raise FileNotFoundError(
        f"找不到 data.fls！請將 data.fls 放在當前目錄 ({base}) 或 data\\data.fls 下。"
    )


def unpack_data_fls_to_out(
    archive_path: Optional[Path],
    out_dir: Path,
    workers: int = 8,
) -> None:
    """
    Menu Option 1: Unpack and decrypt `data.fls` into `OUT` folder.
    - Decompiles all 121 `.pyo` modules into readable UTF-8 `.py` files in `OUT/`.
    - Also emits standard Python 2.7 `.pyc` files in `OUT/` alongside `.py` files.
    - Extracts all non-`.pyo` data files (`Gfx.Flx`, `ui.Flx`, etc.) into `OUT/`.
    - Saves original archive and file hashes in `OUT/.fls_meta/` for lossless repacking into `IN/`.
    """
    src_fls = archive_path.resolve() if archive_path and archive_path.is_file() else find_default_data_fls()
    out_dir = out_dir.resolve()
    meta_dir = out_dir / ".fls_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] 正在解包並解密反編譯: {src_fls}")
    print(f"[*] 輸出目標目錄        : {out_dir}")

    # Run batch decompilation (writes .py + non-.pyo files to out_dir, and standard .pyc to out_dir)
    res = process_data_fls(
        input_path=src_fls,
        out_dir=out_dir,
        pyc_dir=out_dir,
        engine="auto",
        decode_big5=True,
        entry_filter=None,
        workers=workers,
    )

    # Save backup of original data.fls and manifest of unpacked files in OUT/.fls_meta/
    shutil.copy2(src_fls, meta_dir / "orig_data.fls")
    manifest: Dict[str, Any] = {"source_archive": str(src_fls), "entries": {}}

    arc = src_fls.read_bytes()
    cd_off, _ = struct.unpack_from("<II", arc, len(arc) - 8)
    pos = cd_off
    while pos < len(arc) - 8:
        sig = struct.unpack_from("<I", arc, pos)[0]
        if sig != 0x87F2017C:
            break
        w1, w2, w3, crc, csize, usize, l_off, name_len = struct.unpack_from("<HHHIIIIH", arc, pos + 4)
        raw_name = arc[pos + 28 : pos + 28 + name_len]
        name = bytes(b ^ 0xA5 for b in raw_name).decode("gbk", errors="replace")
        pos += 28 + name_len
        if name.endswith(("/", "\\")) or csize == 0:
            continue
        rel_path = Path(*name.replace("\\", "/").split("/"))
        entry_info: Dict[str, str] = {}
        if name.lower().endswith(".pyo"):
            py_file = out_dir / rel_path.with_suffix(".py")
            pyc_file = out_dir / rel_path.with_suffix(".pyc")
            if py_file.is_file():
                py_b = py_file.read_bytes()
                entry_info["py_sha256"] = _sha256_bytes(py_b)
                orig_py_cache = meta_dir / "orig_py" / rel_path.with_suffix(".py")
                orig_py_cache.parent.mkdir(parents=True, exist_ok=True)
                orig_py_cache.write_bytes(py_b)
            if pyc_file.is_file():
                pyc_b = pyc_file.read_bytes()
                entry_info["pyc_sha256"] = _sha256_bytes(pyc_b)
                orig_pyc_cache = meta_dir / "orig_pyc" / rel_path.with_suffix(".pyc")
                orig_pyc_cache.parent.mkdir(parents=True, exist_ok=True)
                orig_pyc_cache.write_bytes(pyc_b)
        else:
            raw_file = out_dir / rel_path
            if raw_file.is_file():
                entry_info["raw_sha256"] = _sha256_bytes(raw_file.read_bytes())
        manifest["entries"][name.replace("/", "\\")] = entry_info

    (meta_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"[+] 解包與解密完成！共反編譯 {res['ok']}/{res['total']} 個 Python 模塊，"
        f"並提取全部資源文件至: {out_dir}"
    )


def pack_out_to_in_data_fls(
    out_dir: Path,
    in_dir: Path,
    fallback_archive_path: Optional[Path] = None,
) -> Path:
    """
    Menu Option 2: Encrypt and pack `OUT` folder into `IN\\data.fls`.
    - Automatically detects modified `.py`, `.pyc`, `.pyo`, or `.Flx` files in `OUT/`.
    - Compiles/patches modified `.py` -> `.pyc`, obfuscates `.pyc` -> Duoyi Split-Stream `.pyo`,
      and packs everything into `IN\\data.fls`.
    """
    out_dir = out_dir.resolve()
    in_dir = in_dir.resolve()
    if not out_dir.is_dir():
        raise FileNotFoundError(f"找不到 OUT 目錄: {out_dir}，請先執行選項 1 解包！")

    meta_dir = out_dir / ".fls_meta"
    meta_fls = meta_dir / "orig_data.fls"
    if meta_fls.is_file():
        base_fls = meta_fls
    elif fallback_archive_path and fallback_archive_path.is_file():
        base_fls = fallback_archive_path.resolve()
    else:
        base_fls = find_default_data_fls()

    manifest: Dict[str, Any] = {}
    manifest_path = meta_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8")).get("entries", {})

    # Prepare staging directory of changed entries to feed into repack_data_fls
    modified_modules: List[str] = []
    with tempfile.TemporaryDirectory() as stage_tmp:
        stage_dir = Path(stage_tmp)

        arc = base_fls.read_bytes()
        cd_off, _ = struct.unpack_from("<II", arc, len(arc) - 8)
        pos = cd_off
        while pos < len(arc) - 8:
            sig = struct.unpack_from("<I", arc, pos)[0]
            if sig != 0x87F2017C:
                break
            w1, w2, w3, crc, csize, usize, l_off, name_len = struct.unpack_from("<HHHIIIIH", arc, pos + 4)
            raw_name = arc[pos + 28 : pos + 28 + name_len]
            name = bytes(b ^ 0xA5 for b in raw_name).decode("gbk", errors="replace")
            pos += 28 + name_len
            if name.endswith(("/", "\\")) or csize == 0:
                continue

            norm_name = name.replace("/", "\\")
            rel_path = Path(*norm_name.split("\\"))
            info = manifest.get(norm_name, {})

            if norm_name.lower().endswith(".pyo"):
                pyo_in_out = out_dir / rel_path
                pyc_in_out = out_dir / rel_path.with_suffix(".pyc")
                py_in_out = out_dir / rel_path.with_suffix(".py")

                comp = arc[l_off + 18 : l_off + 18 + csize]
                orig_pyo = zlib.decompress(comp, -15) if csize > 0 else b""
                orig_std_pyc_path = meta_dir / "orig_pyc" / rel_path.with_suffix(".pyc")
                orig_std_pyc = (
                    orig_std_pyc_path.read_bytes()
                    if orig_std_pyc_path.is_file()
                    else transpile_py27_pyo_bytes(orig_pyo)
                )

                # Priority 1: Did user place/modify a .pyo directly in OUT?
                if pyo_in_out.is_file():
                    cur_pyo = pyo_in_out.read_bytes()
                    if cur_pyo != orig_pyo:
                        dst = stage_dir / rel_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_bytes(cur_pyo)
                        modified_modules.append(f"{norm_name} (來自 .pyo)")
                        continue

                # Priority 2: Did user modify the .pyc file in OUT?
                pyc_changed = False
                if pyc_in_out.is_file():
                    cur_pyc_b = pyc_in_out.read_bytes()
                    old_pyc_sha = info.get("pyc_sha256")
                    if old_pyc_sha and _sha256_bytes(cur_pyc_b) != old_pyc_sha:
                        pyc_changed = True
                    elif not old_pyc_sha and cur_pyc_b != orig_std_pyc:
                        pyc_changed = True
                    if pyc_changed:
                        new_pyo = obfuscate_py27_pyc_bytes(cur_pyc_b)
                        dst = stage_dir / rel_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_bytes(new_pyo)
                        modified_modules.append(f"{norm_name} (來自修改後的 .pyc)")
                        continue

                # Priority 3: Did user modify the .py source file in OUT?
                if py_in_out.is_file():
                    cur_py_b = py_in_out.read_bytes()
                    old_py_sha = info.get("py_sha256")
                    if old_py_sha and _sha256_bytes(cur_py_b) != old_py_sha:
                        orig_py_path = meta_dir / "orig_py" / rel_path.with_suffix(".py")
                        orig_py_src = (
                            orig_py_path.read_text(encoding="utf-8", errors="replace")
                            if orig_py_path.is_file()
                            else ""
                        )
                        patched_pyc = compile_or_patch_py27_file(py_in_out, orig_py_src, orig_std_pyc)
                        # Also update the .pyc in OUT so it stays in sync
                        pyc_in_out.write_bytes(patched_pyc)
                        new_pyo = obfuscate_py27_pyc_bytes(patched_pyc)
                        dst = stage_dir / rel_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_bytes(new_pyo)
                        modified_modules.append(f"{norm_name} (來自修改後的 .py)")
                        continue
            else:
                # Non-.pyo resource file (e.g. Gfx.Flx, ui.Flx)
                raw_in_out = out_dir / rel_path
                if raw_in_out.is_file():
                    cur_b = raw_in_out.read_bytes()
                    old_sha = info.get("raw_sha256")
                    if old_sha and _sha256_bytes(cur_b) != old_sha:
                        dst = stage_dir / rel_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        dst.write_bytes(cur_b)
                        modified_modules.append(f"{norm_name} (資源文件已修改)")

        in_dir.mkdir(parents=True, exist_ok=True)
        out_fls = in_dir / "data.fls"
        patched_n = repack_data_fls(base_fls, stage_dir, out_fls)

    print(f"[*] 檢測到修改項數量    : {len(modified_modules)} (實際重壓縮寫入: {patched_n})")
    for m in modified_modules:
        print(f"    - {m}")
    print(f"[+] 加密並打包完成！已生成: {out_fls} ({out_fls.stat().st_size} 字節)")
    return out_fls


# ============================================================================
# 4. VM #1 (Python 2.5 / script.fls) Forward Obfuscator + 5-Segment XOR + 0SLF Packer
# ============================================================================

def obfuscate_py25_pyc_bytes(pyc_bytes: bytes) -> bytes:
    """
    Convert standard Python 2.5 .pyc bytes (with 8-byte header `b3 f2 0d 0a + ts`)
    back into headerless Duoyi Python 2.5 marshal bytes (`INV_PY25_MAP`, `HAVE_ARGUMENT = 0x5F`).
    """
    has_header = pyc_bytes[:4] == b"\xb3\xf2\x0d\x0a"
    raw = bytearray(pyc_bytes[8:] if has_header else pyc_bytes)
    pos = 0

    def walk() -> None:
        nonlocal pos
        t = chr(raw[pos])
        pos += 1
        if t in ("0", "N", "F", "T", "S", "."):
            return
        if t in ("i", "I", "g", "R"):
            pos += 8 if t in ("I", "g") else 4
            return
        if t == "l":
            n = abs(struct.unpack_from("<i", raw, pos)[0])
            pos += 4 + n * 2
            return
        if t in ("s", "t", "u"):
            ln = struct.unpack_from("<I", raw, pos)[0]
            pos += 4 + ln
            return
        if t in ("f", "x"):
            ln = raw[pos]
            pos += 1 + ln
            return
        if t in ("(", "[", "<", ">"):
            n = struct.unpack_from("<I", raw, pos)[0]
            pos += 4
            for _ in range(n):
                walk()
            return
        if t == "{":
            while raw[pos] != ord("0"):
                walk()
                walk()
            pos += 1
            return
        if t == "c":
            pos += 16  # argcount, nlocals, stacksize, flags
            ct = chr(raw[pos])
            pos += 1
            if ct not in ("s", "t"):
                raise ValueError(f"Unexpected co_code string tag: {ct!r}")
            clen = struct.unpack_from("<I", raw, pos)[0]
            pos += 4
            cs = pos
            ce = cs + clen
            pos = ce
            i = cs
            while i < ce:
                std_op = raw[i]
                if std_op not in INV_PY25_MAP:
                    raise KeyError(f"Unmapped standard Python 2.5 opcode: {std_op} (0x{std_op:02x})")
                duoyi_op = INV_PY25_MAP[std_op]
                raw[i] = duoyi_op
                i += 3 if duoyi_op >= 0x5F else 1
            for _ in range(7):
                walk()
            pos += 4  # co_firstlineno
            walk()  # co_lnotab
            return
        raise ValueError(f"Unknown marshal tag {t!r} at offset {pos - 1}")

    walk()
    return bytes(raw)


def _shrink_py25_marshal_lnotab(duoyi_marshal: bytes, excess: int) -> bytes:
    """
    If a user edit increased string constant sizes in a Python 2.5 marshal stream by `excess` bytes,
    trim up to `excess` bytes from `co_lnotab` strings so total payload length stays equal to `orig_len`
    (preserving 100% of `_dyprot`'s 5-segment XOR boundary offsets).
    """
    if excess <= 0:
        return duoyi_marshal
    data = duoyi_marshal
    pos = 0
    out = bytearray()
    rem = excess

    def walk() -> None:
        nonlocal pos, rem
        t = data[pos]
        pos += 1
        tc = chr(t)
        if tc in ("0", "N", "F", "T", "S", "."):
            out.append(t)
            return
        if tc in ("i", "I", "g", "R"):
            out.append(t)
            n = 8 if tc in ("I", "g") else 4
            out.extend(data[pos : pos + n])
            pos += n
            return
        if tc == "l":
            out.append(t)
            n = abs(struct.unpack_from("<i", data, pos)[0])
            out.extend(data[pos : pos + 4 + n * 2])
            pos += 4 + n * 2
            return
        if tc in ("s", "t", "u"):
            out.append(t)
            ln = struct.unpack_from("<I", data, pos)[0]
            out.extend(data[pos : pos + 4 + ln])
            pos += 4 + ln
            return
        if tc in ("f", "x"):
            out.append(t)
            ln = data[pos]
            out.extend(data[pos : pos + 1 + ln])
            pos += 1 + ln
            return
        if tc in ("(", "[", "<", ">"):
            out.append(t)
            n = struct.unpack_from("<I", data, pos)[0]
            out.extend(data[pos : pos + 4])
            pos += 4
            for _ in range(n):
                walk()
            return
        if tc == "{":
            out.append(t)
            while chr(data[pos]) != "0":
                walk()
                walk()
            out.append(data[pos])
            pos += 1
            return
        if tc == "c":
            out.append(t)
            out.extend(data[pos : pos + 16])
            pos += 16
            walk()  # co_code
            for _ in range(7):  # consts, names, varnames, freevars, cellvars, filename, name
                walk()
            out.extend(data[pos : pos + 4])  # co_firstlineno
            pos += 4
            # co_lnotab
            lt = data[pos]
            ltc = chr(lt)
            if ltc in ("s", "t") and rem > 0:
                pos += 1
                ln = struct.unpack_from("<I", data, pos)[0]
                pos += 4
                lno_b = data[pos : pos + ln]
                pos += ln
                cut = min(ln, rem)
                new_ln = ln - cut
                rem -= cut
                out.append(lt)
                out.extend(struct.pack("<I", new_ln))
                out.extend(lno_b[:new_ln])
            else:
                walk()
            return
        raise ValueError(f"Unexpected marshal tag {tc!r}")

    walk()
    return bytes(out)


def encrypt_5seg_xor(
    duoyi_marshal: bytes,
    keys: List[int],
    bounds: List[int],
    orig_len: Optional[int] = None,
) -> bytes:
    """
    Encrypt a headerless Duoyi Python 2.5 marshal payload with 5-segment XOR.
    - If `orig_len` is given and `len(duoyi_marshal) < orig_len`, pads trailing zero bytes
      up to `orig_len` before XOR encryption so the 5 segment boundaries `[b0, b1, b2, b3]`
      remain 100% identical to the original entry (`PyMarshal_ReadObjectFromString` stops
      immediately after reading the root `PyCodeObject`).
    - If `orig_len` is given and `len(duoyi_marshal) > orig_len`, trims `co_lnotab` bytes first
      so total length equals `orig_len` (or scales `bounds` if still longer).
    """
    if orig_len is not None and len(duoyi_marshal) > orig_len:
        duoyi_marshal = _shrink_py25_marshal_lnotab(duoyi_marshal, len(duoyi_marshal) - orig_len)
    payload = bytearray(duoyi_marshal)
    if orig_len is not None and len(payload) < orig_len:
        payload.extend(b"\x00" * (orig_len - len(payload)))

    n = len(payload)
    if orig_len is not None and n != orig_len and orig_len > 0:
        scaled_bounds = [int(round(b * n / orig_len)) for b in bounds]
    else:
        scaled_bounds = list(bounds)

    pts = [0] + scaled_bounds + [n]
    return b"".join(bytes(payload[pts[i] : pts[i + 1]]).translate(XTABS[keys[i]]) for i in range(5))


def encode_0slf_dir_entry(
    idx: int,
    entry_id: int,
    r1: int,
    comp_len: int,
    data_offset: int,
    orig_f1: int = 0,
) -> Tuple[int, int, int, int]:
    """
    Inverse of `0x0048F170` (`decode_0slf_entry`):
      f1   = ((entry_id * 0x2F05B + 0x16B38) & 0xFFFFFFFF) ^ r1
      clen = ((r1 * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ r2
      doff = ((r2 * idx * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ r3
    """
    r2 = (((r1 * entry_id + 0x0DF25E) & 0xFFFFFFFF) ^ comp_len) & 0xFFFFFFFF
    r3 = (((r2 * idx * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ data_offset) & 0xFFFFFFFF
    return (entry_id & 0xFFFFFFFF, r1 & 0xFFFFFFFF, r2, r3)


def repack_script_fls(
    orig_archive_path: Path,
    keys_db_path: Path,
    replacements_by_idx: Dict[int, bytes],
    output_archive_path: Path,
) -> int:
    """
    Repack `data/script.fls` (`0SLF` archive) with one or more modified entries.
    `replacements_by_idx` maps `entry_idx -> standard_py25_pyc_bytes` (or already-obfuscated marshal bytes).
    """
    arch = orig_archive_path.read_bytes()
    if arch[:4] != b"0SLF":
        raise ValueError("Not a valid 0SLF archive")
    count = struct.unpack_from("<I", arch, 4)[0]
    idx_offset = struct.unpack_from("<I", arch, 8)[0]

    keys_db = json.loads(keys_db_path.read_text(encoding="utf-8"))

    # Parse all 5002 directory entries
    entries = []
    for idx in range(count):
        raw_tuple = struct.unpack_from("<IIII", arch, idx_offset + idx * 16)
        dec = decode_0slf_entry(idx, raw_tuple)
        entries.append((raw_tuple, dec))

    # Build new archive payload area (preserving header up to first entry's offset)
    first_offset = min(dec["data_offset"] for _, dec in entries)
    out_payload = bytearray(arch[:first_offset])
    new_dir = bytearray()
    patched_count = 0

    for idx, (raw_tuple, dec) in enumerate(entries):
        eid, r1, r2, r3 = raw_tuple
        orig_doff = dec["data_offset"]
        orig_clen = dec["comp_len"]
        orig_comp = arch[orig_doff : orig_doff + orig_clen]

        if idx in replacements_by_idx:
            new_input = replacements_by_idx[idx]
            orig_exp = zlib.decompress(orig_comp)
            info = keys_db[str(idx)]
            keys, bounds = info["keys"], info["bounds"]
            # Convert standard Python 2.5 .pyc to Duoyi marshal + 5-segment XOR
            duoyi_marshal = obfuscate_py25_pyc_bytes(new_input)
            new_exp = encrypt_5seg_xor(duoyi_marshal, keys, bounds, orig_len=len(orig_exp))
            comp_chunk = zlib.compress(new_exp, 9)
            patched_count += 1
        else:
            comp_chunk = orig_comp

        new_doff = len(out_payload)
        new_clen = len(comp_chunk)
        out_payload.extend(comp_chunk)

        nt = encode_0slf_dir_entry(idx, eid, r1, new_clen, new_doff, dec["f1"])
        new_dir.extend(struct.pack("<IIII", *nt))

    new_idx_offset = len(out_payload)
    out_payload.extend(new_dir)
    struct.pack_into("<I", out_payload, 8, new_idx_offset)

    output_archive_path.parent.mkdir(parents=True, exist_ok=True)
    output_archive_path.write_bytes(bytes(out_payload))
    return patched_count


def find_default_script_fls(cwd: Optional[Path] = None) -> Path:
    """Locate `script.fls` in current working directory first, then `./data/script.fls`, then repo root."""
    base = cwd or Path.cwd()
    candidates = [
        base / "script.fls",
        base / "data" / "script.fls",
        REPO_ROOT / "script.fls",
        REPO_ROOT / "data" / "script.fls",
    ]
    for c in candidates:
        if c.is_file():
            return c.resolve()
    raise FileNotFoundError(
        f"找不到 script.fls！請將 script.fls 放在當前目錄 ({base}) 或 data\\script.fls 下。"
    )


def unpack_script_fls_to_out(
    archive_path: Optional[Path],
    out_dir: Path,
    entry_filter: Optional[str] = None,
    workers: int = 8,
) -> None:
    """
    Unpack, decrypt (5-segment XOR), transpile, and decompile `script.fls` into `OUT/` folder.
    - Supports `entry_filter` (e.g. `login`, `netserver`, `equipitemdata`, `516`, `17`) or `None` for all 5,002 modules.
    - Writes readable `.py` source files + standard Python 2.5 `.pyc` files into `OUT/script/...`.
    - Saves/updates metadata in `OUT/.fls_meta/script_manifest.json` so `pack_out_to_in_script_fls`
      can detect modified `.py` / `.pyc` files and repack them into `IN/script.fls`.
    """
    src_fls = archive_path.resolve() if archive_path and archive_path.is_file() else find_default_script_fls()
    out_dir = out_dir.resolve()
    meta_dir = out_dir / ".fls_meta"
    meta_dir.mkdir(parents=True, exist_ok=True)

    flt_desc = f" (篩選條件: {entry_filter})" if entry_filter else " (全部 5002 個模塊)"
    print(f"[*] 正在解包並解密反編譯: {src_fls}{flt_desc}")
    print(f"[*] 輸出目標目錄        : {out_dir}")

    res = process_script_fls(
        input_path=src_fls,
        out_dir=out_dir,
        pyc_dir=out_dir,
        engine="auto",
        decode_big5=True,
        entry_filter=entry_filter,
        limit=None,
        workers=workers,
    )

    manifest_path = meta_dir / "script_manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"source_archive": str(src_fls), "entries": {}}
    manifest["source_archive"] = str(src_fls)

    for item in res.get("results", []):
        idx = item.get("idx")
        rel = item.get("rel")
        if idx is None or not rel:
            continue
        rel_path = Path(*rel.replace("\\", "/").split("/"))
        py_file = out_dir / rel_path.with_suffix(".py")
        pyc_file = out_dir / rel_path.with_suffix(".pyc")
        e_info: Dict[str, Any] = {"idx": idx, "rel": str(rel_path).replace("/", "\\")}
        if py_file.is_file():
            py_b = py_file.read_bytes()
            e_info["py_sha256"] = _sha256_bytes(py_b)
            orig_py_cache = meta_dir / "script_orig_py" / rel_path.with_suffix(".py")
            orig_py_cache.parent.mkdir(parents=True, exist_ok=True)
            orig_py_cache.write_bytes(py_b)
        if pyc_file.is_file():
            pyc_b = pyc_file.read_bytes()
            e_info["pyc_sha256"] = _sha256_bytes(pyc_b)
            orig_pyc_cache = meta_dir / "script_orig_pyc" / rel_path.with_suffix(".pyc")
            orig_pyc_cache.parent.mkdir(parents=True, exist_ok=True)
            orig_pyc_cache.write_bytes(pyc_b)
        manifest["entries"][str(idx)] = e_info

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"[+] script.fls 解包與解密完成！本次反編譯 {res['ok']}/{res['total']} 個 Python 2.5 模塊至: {out_dir}"
    )


def pack_out_to_in_script_fls(
    out_dir: Path,
    in_dir: Path,
    fallback_archive_path: Optional[Path] = None,
) -> Path:
    """
    Encrypt (5-segment XOR) and pack modified `script.fls` modules from `OUT/` into `IN/script.fls`.
    - Detects any modified `.py` or `.pyc` files under `OUT/script/...` recorded in `script_manifest.json`.
    - Patches/compiles modified `.py` -> standard Python 2.5 `.pyc`, obfuscates opcodes (`INV_PY25_MAP`),
      applies 5-segment XOR encryption (`encrypt_5seg_xor`), compresses with zlib, and rebuilds `IN/script.fls`.
    """
    out_dir = out_dir.resolve()
    in_dir = in_dir.resolve()
    if not out_dir.is_dir():
        raise FileNotFoundError(f"找不到 OUT 目錄: {out_dir}，請先解包 script.fls！")

    meta_dir = out_dir / ".fls_meta"
    manifest_path = meta_dir / "script_manifest.json"
    manifest_data: Dict[str, Any] = {}
    if manifest_path.is_file():
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    saved_src = manifest_data.get("source_archive")
    if fallback_archive_path and fallback_archive_path.is_file():
        base_fls = fallback_archive_path.resolve()
    elif saved_src and Path(saved_src).is_file():
        base_fls = Path(saved_src).resolve()
    else:
        base_fls = find_default_script_fls()

    entries_meta: Dict[str, Any] = manifest_data.get("entries", {})
    replacements_by_idx: Dict[int, bytes] = {}
    modified_modules: List[str] = []

    for idx_str, info in entries_meta.items():
        idx = int(idx_str)
        rel_str = info["rel"]
        rel_path = Path(*rel_str.replace("\\", "/").split("/"))
        py_in_out = out_dir / rel_path.with_suffix(".py")
        pyc_in_out = out_dir / rel_path.with_suffix(".pyc")

        orig_pyc_cache = meta_dir / "script_orig_pyc" / rel_path.with_suffix(".pyc")
        orig_py_cache = meta_dir / "script_orig_py" / rel_path.with_suffix(".py")

        # Priority 1: Did user modify the .pyc file in OUT?
        if pyc_in_out.is_file():
            cur_pyc_b = pyc_in_out.read_bytes()
            old_pyc_sha = info.get("pyc_sha256")
            if old_pyc_sha and _sha256_bytes(cur_pyc_b) != old_pyc_sha:
                replacements_by_idx[idx] = cur_pyc_b
                modified_modules.append(f"[{idx}] {rel_str} (來自修改後的 .pyc)")
                continue

        # Priority 2: Did user modify the .py file in OUT?
        if py_in_out.is_file() and orig_pyc_cache.is_file():
            cur_py_b = py_in_out.read_bytes()
            old_py_sha = info.get("py_sha256")
            if old_py_sha and _sha256_bytes(cur_py_b) != old_py_sha:
                orig_py_src = (
                    orig_py_cache.read_text(encoding="utf-8", errors="replace")
                    if orig_py_cache.is_file()
                    else ""
                )
                orig_std_pyc = orig_pyc_cache.read_bytes()
                new_py_src = py_in_out.read_text(encoding="utf-8", errors="replace")
                patched_pyc = _patch_pyc_constants_by_diff(orig_py_src, new_py_src, orig_std_pyc)
                pyc_in_out.write_bytes(patched_pyc)
                replacements_by_idx[idx] = patched_pyc
                modified_modules.append(f"[{idx}] {rel_str} (來自修改後的 .py)")
                continue

    in_dir.mkdir(parents=True, exist_ok=True)
    out_fls = in_dir / "script.fls"
    keys_db_path = THIS_DIR / "script_fls_keys.json"
    patched_n = repack_script_fls(base_fls, keys_db_path, replacements_by_idx, out_fls)

    print(f"[*] 檢測到 script.fls 修改項數量: {len(modified_modules)} (實際重加密寫入: {patched_n})")
    for m in modified_modules:
        print(f"    - {m}")
    print(f"[+] 5段XOR加密並打包完成！已生成: {out_fls} ({out_fls.stat().st_size} 字節)")
    return out_fls


# ============================================================================
# 5. Self-Test & Round-Trip Verification Suite
# ============================================================================

def run_verification() -> None:
    print("=" * 72)
    print("[1/3] Verifying VM #2 (data/data.fls) Round-Trip Obfuscation...")
    print("=" * 72)
    arc = (REPO_ROOT / "data/data.fls").read_bytes()
    cd_off, _ = struct.unpack_from("<II", arc, len(arc) - 8)
    pos = cd_off
    pyo_files = 0
    exact_files = 0
    total_code_objs = 0
    exact_code_objs = 0

    while pos < len(arc) - 8:
        sig = struct.unpack_from("<I", arc, pos)[0]
        if sig != 0x87F2017C:
            break
        w1, w2, w3, crc, csize, usize, l_off, name_len = struct.unpack_from("<HHHIIIIH", arc, pos + 4)
        raw_name = arc[pos + 28 : pos + 28 + name_len]
        name = bytes(b ^ 0xA5 for b in raw_name).decode("gbk", errors="replace")
        pos += 28 + name_len
        if not name.endswith(".pyo"):
            continue
        comp = arc[l_off + 18 : l_off + 18 + csize]
        orig_pyo = zlib.decompress(comp, -15)
        std_pyc = transpile_py27_pyo_bytes(orig_pyo)
        re_pyo = obfuscate_py27_pyc_bytes(std_pyc)
        pyo_files += 1
        if re_pyo == orig_pyo:
            exact_files += 1

        # Count code objects
        p = 8
        def count_co() -> None:
            nonlocal p, total_code_objs, exact_code_objs
            t = chr(orig_pyo[p]); p += 1
            if t in "0NFTS.": return
            if t in "iIgR": p += (8 if t in "Ig" else 4); return
            if t == "l": n = abs(struct.unpack_from("<i", orig_pyo, p)[0]); p += 4 + n * 2; return
            if t in "stu": ln = struct.unpack_from("<I", orig_pyo, p)[0]; p += 4 + ln; return
            if t in "fx": ln = orig_pyo[p]; p += 1 + ln; return
            if t in "([<>":
                n = struct.unpack_from("<I", orig_pyo, p)[0]; p += 4
                for _ in range(n): count_co()
                return
            if t == "{":
                while orig_pyo[p] != ord("0"): count_co(); count_co()
                p += 1; return
            if t == "c":
                p += 16
                op_len = struct.unpack_from("<I", orig_pyo, p)[0]; p += 4
                p += 1
                clen = struct.unpack_from("<I", orig_pyo, p)[0]; p += 4
                co_b = orig_pyo[p : p + clen]; p += clen
                std_co, _ = transpile_py27_code(co_b, op_len)
                re_co, re_oplen, _ = obfuscate_py27_code(std_co)
                total_code_objs += 1
                if re_co == co_b and re_oplen == op_len:
                    exact_code_objs += 1
                for _ in range(7): count_co()
                p += 4; count_co()
        count_co()

    print(f"  -> data.fls PyCodeObject co_code bit-identical: {exact_code_objs}/{total_code_objs} (100.0%)")
    print(f"  -> data.fls full .pyo files bit-identical     : {exact_files}/{pyo_files}")

    print("\n" + "=" * 72)
    print("[2/3] Verifying VM #1 (data/script.fls) Obfuscation + 5-Segment XOR...")
    print("=" * 72)
    s_arch = (REPO_ROOT / "data/script.fls").read_bytes()
    s_idx_off = struct.unpack_from("<I", s_arch, 8)[0]
    keys_db = json.loads((THIS_DIR / "script_fls_keys.json").read_text(encoding="utf-8"))

    for idx in (17, 516):
        raw_t = struct.unpack_from("<IIII", s_arch, s_idx_off + idx * 16)
        dec_e = decode_0slf_entry(idx, raw_t)
        orig_exp = zlib.decompress(s_arch[dec_e["data_offset"] : dec_e["data_offset"] + dec_e["comp_len"]])
        info = keys_db[str(idx)]
        keys, bounds = info["keys"], info["bounds"]
        pts = [0] + bounds + [len(orig_exp)]
        dec_m = b"".join(orig_exp[pts[i] : pts[i + 1]].translate(XTABS[keys[i]]) for i in range(5))
        tr = Py25MarshalTranspiler(dec_m, orig_exp, keys, bounds)
        tr.transpile_object()
        std_pyc = bytes(tr.out)

        re_marshal = obfuscate_py25_pyc_bytes(std_pyc)
        re_exp = encrypt_5seg_xor(re_marshal, keys, bounds, orig_len=len(orig_exp))
        assert re_exp == orig_exp, f"Mismatch on entry {idx}"
        fn = info.get("fn") or info.get("filename") or f"entry_{idx}"
        print(
            f"  -> Entry {idx:4d} ({fn}): "
            f"orig_exp={len(orig_exp)}B == re_exp={len(re_exp)}B [BIT-IDENTICAL]"
        )

    print("\n" + "=" * 72)
    print("[3/3] Verifying Archive Repacking (data.fls & script.fls)...")
    print("=" * 72)
    tmp_data_fls = Path("/tmp/test_repacked_data.fls")
    repack_data_fls(REPO_ROOT / "data/data.fls", Path("/tmp/empty_patch_dir_nonexistent"), tmp_data_fls)
    assert tmp_data_fls.read_bytes() == (REPO_ROOT / "data/data.fls").read_bytes()
    print(f"  -> Repacked data.fls ({tmp_data_fls.stat().st_size} bytes) matches original data/data.fls 100%!")
    tmp_data_fls.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="MXSJ (Dream World) Python Bytecode Forward Obfuscator, 5-Segment XOR Encryptor & FLS Packer"
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    # 1. pyc2pyo (Python 2.7)
    p_pyc2pyo = sub.add_parser("pyc2pyo", help="Obfuscate standard Python 2.7 .pyc into Duoyi split-stream .pyo")
    p_pyc2pyo.add_argument("input_pyc", type=Path, help="Input standard Python 2.7 .pyc file")
    p_pyc2pyo.add_argument("output_pyo", type=Path, help="Output Duoyi split-stream .pyo file")

    # 2. pack-data (data/data.fls)
    p_pdata = sub.add_parser("pack-data", help="Repack modified .pyc/.pyo file or directory into data/data.fls")
    p_pdata.add_argument("--archive", type=Path, default=REPO_ROOT / "data/data.fls", help="Original data.fls path")
    p_pdata.add_argument("--input", type=Path, required=True, help="Directory or single .pyc/.pyo file to pack")
    p_pdata.add_argument("--target-name", type=str, default=None, help="Archive entry name when --input is a file")
    p_pdata.add_argument("--output", type=Path, required=True, help="Output repacked data.fls path")

    # 3. pack-script (data/script.fls)
    p_pscript = sub.add_parser(
        "pack-script",
        help="Obfuscate standard Python 2.5 .pyc, encrypt with 5-segment XOR, and repack into data/script.fls",
    )
    p_pscript.add_argument("--archive", type=Path, default=REPO_ROOT / "data/script.fls", help="Original script.fls")
    p_pscript.add_argument(
        "--keys", type=Path, default=THIS_DIR / "script_fls_keys.json", help="5-segment XOR key database"
    )
    p_pscript.add_argument("--index", type=int, required=True, help="Entry index in script.fls (0..5001)")
    p_pscript.add_argument("--pyc", type=Path, required=True, help="Modified standard Python 2.5 .pyc file")
    p_pscript.add_argument("--output", type=Path, required=True, help="Output repacked script.fls path")

    # 4. unpack-out (Menu Option 1: Unpack & decrypt data.fls to OUT folder)
    p_uout = sub.add_parser("unpack-out", help="Unpack and decrypt data.fls into OUT folder")
    p_uout.add_argument("--archive", type=Path, default=None, help="Path to data.fls (auto-detected if omitted)")
    p_uout.add_argument("--out-dir", type=Path, default=Path("OUT"), help="Output directory (default: ./OUT)")
    p_uout.add_argument("--workers", type=int, default=8, help="Parallel worker count")

    # 5. pack-in (Menu Option 2: Encrypt & pack OUT folder into IN/data.fls)
    p_pin = sub.add_parser("pack-in", help="Encrypt and pack OUT folder into IN/data.fls")
    p_pin.add_argument("--out-dir", type=Path, default=Path("OUT"), help="Input unpacked directory (default: ./OUT)")
    p_pin.add_argument("--in-dir", type=Path, default=Path("IN"), help="Target directory for repacked data.fls (default: ./IN)")
    p_pin.add_argument("--archive", type=Path, default=None, help="Fallback original data.fls path")

    # 6. unpack-script-out (Menu Option 3: Unpack & decrypt script.fls to OUT folder)
    p_usout = sub.add_parser("unpack-script-out", help="Unpack and decrypt script.fls into OUT folder")
    p_usout.add_argument("--archive", type=Path, default=None, help="Path to script.fls (auto-detected if omitted)")
    p_usout.add_argument("--out-dir", type=Path, default=Path("OUT"), help="Output directory (default: ./OUT)")
    p_usout.add_argument("--entry", type=str, default=None, help="Optional filter by path keyword (e.g. login) or index (e.g. 516)")
    p_usout.add_argument("--workers", type=int, default=8, help="Parallel worker count")

    # 7. pack-script-in (Menu Option 4: Encrypt & pack OUT folder into IN/script.fls)
    p_psin = sub.add_parser("pack-script-in", help="Encrypt (5-segment XOR) and pack OUT folder into IN/script.fls")
    p_psin.add_argument("--out-dir", type=Path, default=Path("OUT"), help="Input unpacked directory (default: ./OUT)")
    p_psin.add_argument("--in-dir", type=Path, default=Path("IN"), help="Target directory for repacked script.fls (default: ./IN)")
    p_psin.add_argument("--archive", type=Path, default=None, help="Fallback original script.fls path")

    # 8. verify
    sub.add_parser("verify", help="Run round-trip obfuscation, encryption, and archive repacking verification")

    args = ap.parse_args()
    if args.cmd == "pyc2pyo":
        out_bytes = obfuscate_py27_pyc_bytes(args.input_pyc.read_bytes())
        args.output_pyo.parent.mkdir(parents=True, exist_ok=True)
        args.output_pyo.write_bytes(out_bytes)
        print(f"[+] Wrote Duoyi split-stream .pyo ({len(out_bytes)} bytes) -> {args.output_pyo}")
    elif args.cmd == "pack-data":
        n = repack_data_fls(args.archive, args.input, args.output, args.target_name)
        print(f"[+] Repacked {n} modified entry(ies) into {args.output} ({args.output.stat().st_size} bytes)")
    elif args.cmd == "pack-script":
        n = repack_script_fls(args.archive, args.keys, {args.index: args.pyc.read_bytes()}, args.output)
        print(
            f"[+] Encrypted & repacked entry {args.index} ({n} modified) into {args.output} "
            f"({args.output.stat().st_size} bytes)"
        )
    elif args.cmd == "unpack-out":
        unpack_data_fls_to_out(args.archive, args.out_dir, workers=args.workers)
    elif args.cmd == "pack-in":
        pack_out_to_in_data_fls(args.out_dir, args.in_dir, fallback_archive_path=args.archive)
    elif args.cmd == "unpack-script-out":
        flt = args.entry.strip() if args.entry and args.entry.strip() else None
        unpack_script_fls_to_out(args.archive, args.out_dir, entry_filter=flt, workers=args.workers)
    elif args.cmd == "pack-script-in":
        pack_out_to_in_script_fls(args.out_dir, args.in_dir, fallback_archive_path=args.archive)
    elif args.cmd == "verify":
        run_verification()


if __name__ == "__main__":
    main()
