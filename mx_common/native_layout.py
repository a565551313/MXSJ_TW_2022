"""Native package .dlg storage: path-derived XOR, with legacy READ compatibility.

**Single source of truth** (mx_common/); editors run a byte-identical copy made by
tools/devkit/vendor_core.py. Never execute layout code.
Evidence: notes/native_dlg_path_cipher.md. Header-derived keys are read-only aids,
not the game's decryption rule. Existing plaintext/wrong-key layouts can be edited
and are migrated to native storage when that layout is explicitly saved/imported.
"""

from __future__ import annotations

import ast
import struct
from pathlib import PureWindowsPath

from .mxhash import mx_hash

HEADER = b"# -*- coding: gbk -*-"
MASK32 = 0xFFFFFFFF


def path_bytes(path: str) -> bytes:
    value = path.strip().replace("\\", "/")
    if (
        not value
        or PureWindowsPath(value).drive
        or PureWindowsPath(value).is_absolute()
        or any(ord(char) < 32 or char in '<>:"|?*' for char in value)
        or any(part in ("", ".", "..") for part in value.split("/"))
    ):
        raise ValueError("布局必须使用包内相对路径")
    encoded = value.encode("gbk")  # Never replace unencodable filename bytes.
    if len(encoded) >= 256:
        raise ValueError("原生资源路径必须少于256字节")
    return encoded


def key_for_id(entry_id: int) -> bytes:
    if not 0 <= entry_id <= MASK32:
        raise ValueError("invalid entry ID")
    return struct.pack("<I", ((entry_id + 0x9234AB) & MASK32) ^ 0x937F4912)


def key_for_path(path: str) -> bytes:
    return key_for_id(mx_hash(path_bytes(path)))


def xor4(data: bytes, key: bytes) -> bytes:
    if len(key) != 4:
        raise ValueError("XOR key must be four bytes")
    repeated = (key * (len(data) // 4 + 1))[: len(data)]
    return (
        int.from_bytes(data, "little") ^ int.from_bytes(repeated, "little")
    ).to_bytes(len(data), "little")


def validate_plain(plain: bytes) -> None:
    """Literal-only syntax check, preserving all mixed Big5/GBK bytes verbatim."""
    if not plain.startswith(HEADER):
        raise ValueError("布局缺少原生GBK编码头")
    text = plain.decode("gb18030", "surrogateescape")
    text = "".join(
        f"\\u{ord(char):04x}" if 0xDC80 <= ord(char) <= 0xDCFF else char
        for char in text
    )
    try:
        tree = ast.parse(text)
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("布局字面量无法解析") from exc
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign):
        raise ValueError("布局只允许UI_INFO字面量赋值")
    assignment = tree.body[0]
    if (
        len(assignment.targets) != 1
        or not isinstance(assignment.targets[0], ast.Name)
        or assignment.targets[0].id != "UI_INFO"
        or not isinstance(assignment.value, ast.List)
        or not all(isinstance(item, ast.Dict) for item in assignment.value.elts)
    ):
        raise ValueError("UI_INFO必须是控件字典列表")
    allowed = (
        ast.List,
        ast.Dict,
        ast.Tuple,
        ast.Constant,
        ast.UnaryOp,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )
    if any(not isinstance(node, allowed) for node in ast.walk(assignment.value)):
        raise ValueError("布局包含非字面量内容，拒绝写入")
    if any(
        isinstance(node, ast.Dict) and None in node.keys
        for node in ast.walk(assignment.value)
    ):
        raise ValueError("布局不能包含字典解包")


def layout_hint(prefix: bytes) -> bool:
    """Cheap layout identification; never AST-parse a truncated source."""
    if prefix.startswith(HEADER):
        plain = prefix
    elif len(prefix) >= len(HEADER):
        old_key = bytes(a ^ b for a, b in zip(prefix[:4], b"# -*", strict=True))
        plain = xor4(prefix, old_key)
    else:
        return False
    return plain.startswith(HEADER) and b"UI_INFO" in plain


def plain_if_layout(data: bytes) -> bytes | None:
    """Recognize plaintext or header-derived legacy ciphertext, without execution.

    None means it is not recognized as .dlg. Recognized but malformed layouts raise
    ValueError rather than being silently treated as generic binary resources.
    """
    if data.startswith(HEADER):
        plain = data
    elif len(data) >= len(HEADER):
        old_key = bytes(a ^ b for a, b in zip(data[:4], b"# -*", strict=True))
        if not xor4(data[: len(HEADER)], old_key).startswith(HEADER):
            return None
        plain = xor4(data, old_key)
    else:
        return None
    if b"UI_INFO" not in plain:
        return None  # A GBK-coded generic text/module is not necessarily a layout.
    validate_plain(plain)
    return plain


def encode_layout(data: bytes, entry_id: int) -> bytes:
    """Accept plain/native/legacy .dlg; ALWAYS write the native key for this ID."""
    plain = plain_if_layout(data)
    if plain is None:
        raise ValueError("无法识别布局内容，拒绝写入.dlg路径")
    return xor4(plain, key_for_id(entry_id))


def decode_native(stored: bytes, entry_id: int) -> bytes:
    """Strict native readback: no header guessing or plaintext fallback."""
    plain = xor4(stored, key_for_id(entry_id))
    validate_plain(plain)
    return plain
