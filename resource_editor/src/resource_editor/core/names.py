"""0SLF 条目真名识别：哈希字典 + 布局引用扒取。

0SLF 包内不存文件名，目录里只有路径的 32 位哈希（见
:mod:`.mxhash`），哈希单向不可逆——想显示真名只能"猜中"：
拿一本已知路径字典逐条算哈希与目录 entry_id 对，对中即得名。

字典两级来源：

1. 随包的 ``data/known_paths.txt``：从客户端脚本收获的 2,901
   条 ``.dlg`` 布局路径（与 UI 编辑器同源），布局条目靠它命名；
2. 运行时扒取：已命名的 .dlg 条目解开文本后，里面明文写着它
   引用的图片路径（如 ``combdialog4\\...\\底板800.png``），把
   这些路径再算哈希反查目录，图片条目随之得名。

从未被任何脚本/布局引用过的条目无名可猜，调用方回退显示
序号——这是包格式决定的，不是识别能力问题。
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

from .mxhash import mx_hash

__all__ = [
    "build_name_map",
    "extract_resource_paths",
    "known_path_hashes",
    "unpack_dlg_text",
]

_KNOWN_CACHE: dict[int, str] | None = None
_IMAGE_EXTS = (b".png", b".jpg", b".jpeg", b".bmp", b".tga")
_QUOTED_RE = re.compile(rb'"((?:[^"\\]|\\.)*)"|\'((?:[^\'\\]|\\.)*)\'')
_DLG_HEADER = b"# -*- coding: gbk -*-"


def _catalog_file() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "known_paths.txt"


def known_path_hashes() -> dict[int, str]:
    """读取随包路径字典，返回 {路径哈希: 路径}（进程内缓存）。"""
    global _KNOWN_CACHE
    if _KNOWN_CACHE is None:
        table: dict[int, str] = {}
        try:
            lines = _catalog_file().read_text(
                encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            path = line.strip()
            if path and not path.startswith("#"):
                table.setdefault(
                    mx_hash(path.encode("gbk", "replace")), path)
        _KNOWN_CACHE = table
    return _KNOWN_CACHE


def _xor4(data: bytes, key: bytes) -> bytes:
    """4 字节循环 XOR（整数整体异或，比逐字节快两个数量级）。"""
    if not data:
        return data
    repeated = (key * (len(data) // 4 + 1))[:len(data)]
    return (int.from_bytes(data, "little")
            ^ int.from_bytes(repeated, "little")).to_bytes(
                len(data), "little")


def _recover_key_by_frequency(data: bytes) -> bytes:
    """文件头反推不成时，用列频率法恢复 4 字节 XOR 密钥。"""
    favourites = set(
        b" etaoinshrdlu=(){}_#'\"0123456789.,:[]\n\t<>")
    key = bytearray(4)
    for r in range(4):
        column = data[r::4][:2048]
        best_score, best = -1, 0
        for cand in range(256):
            score = sum(1 for b in column if (b ^ cand) in favourites)
            if score > best_score:
                best_score, best = score, cand
        key[r] = best
    return bytes(key)


def unpack_dlg_text(stored: bytes) -> bytes | None:
    """把包内 .dlg 存储字节还原为明文；不像 .dlg 时返回 None。

    .dlg 明文以 ``# -*- coding: gbk -*-`` 开头，存储形是它与
    逐条 4 字节 XOR 密钥的异或（密钥靠已知文件头反推）；明文
    存储的条目直接返回；文件头反推不成时再用列频率法兜底。
    """
    if stored.startswith(b"# -"):
        return stored
    if len(stored) < len(_DLG_HEADER):
        return None
    key = bytes(a ^ b for a, b in zip(stored[:4], b"# -*", strict=True))
    decoded = _xor4(stored, key)
    if decoded.startswith(_DLG_HEADER):
        return decoded
    decoded = _xor4(stored, _recover_key_by_frequency(stored))
    if decoded.startswith(b"# -") or b"sFileName" in decoded[:4096]:
        return decoded
    return None


def _unescape(raw: bytes) -> bytes:
    """还原引号字符串里的反斜杠转义（\\\\ → \\ 等）。"""
    out = bytearray()
    i = 0
    while i < len(raw):
        if raw[i] == 0x5C and i + 1 < len(raw):
            out.append(raw[i + 1])
            i += 2
        else:
            out.append(raw[i])
            i += 1
    return bytes(out)


def extract_resource_paths(data: bytes) -> list[str]:
    """从 .dlg 明文字节里扒出被引用的资源路径（图片为主）。

    .dlg 文本是类 JSON 结构：路径写在引号字符串里且反斜杠被
    转义成双写（``combdialog\\\\...\\\\x.png``），必须先按引号
    取出字符串、反转义成单反斜杠，算出的哈希才与包内条目对
    得上。路径字段是 GBK 字节，解码失败的候选丢弃。
    """
    found: list[str] = []
    seen: set[str] = set()
    for match in _QUOTED_RE.finditer(data):
        raw = match.group(1) if match.group(1) is not None \
            else match.group(2)
        if len(raw) < 5 or len(raw) > 240:
            continue
        token = _unescape(raw)
        if b"\\" not in token and b"/" not in token:
            continue
        if not token.lower().endswith(_IMAGE_EXTS):
            continue
        try:
            path = token.decode("gbk")
        except UnicodeDecodeError:
            continue
        if path not in seen:
            seen.add(path)
            found.append(path)
    return found


def build_name_map(entry_ids: list[int],
                   read_stored: Callable[[int], bytes],
                   known: dict[int, str] | None = None) -> dict[int, str]:
    """为一张目录表算出 {原始序号: 显示名}，未命中的不入表。

    ``read_stored(原始序号)`` 供扒取阶段读取种子 .dlg 的存储
    字节；读取/解码失败的种子静默跳过，命名永不阻塞打开。
    """
    if known is None:
        known = known_path_hashes()
    by_id: dict[int, int] = {}
    for index, entry_id in enumerate(entry_ids):
        by_id.setdefault(entry_id, index)
    result: dict[int, str] = {}
    seeds: list[int] = []
    for entry_id, path in known.items():
        index = by_id.get(entry_id)
        if index is not None:
            result[index] = path
            if path.lower().endswith(".dlg"):
                seeds.append(index)
    for index in seeds:
        try:
            plain = unpack_dlg_text(read_stored(index))
        except Exception:
            continue
        if plain is None:
            continue
        for candidate in extract_resource_paths(plain):
            target = by_id.get(
                mx_hash(candidate.encode("gbk", "replace")))
            if target is not None and target not in result:
                result[target] = candidate
    return result
