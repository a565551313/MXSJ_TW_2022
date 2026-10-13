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
_TOKEN_SPLIT = re.compile(rb"[\s\"'=<>()\[\]{},;|]+")
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
    return bytes(b ^ key[i & 3] for i, b in enumerate(data))


def unpack_dlg_text(stored: bytes) -> bytes | None:
    """把包内 .dlg 存储字节还原为明文；不像 .dlg 时返回 None。

    .dlg 明文以 ``# -*- coding: gbk -*-`` 开头，存储形是它与
    逐条 4 字节 XOR 密钥的异或（密钥靠已知文件头反推）；明文
    存储的条目直接返回。
    """
    if stored.startswith(b"# -"):
        return stored
    if len(stored) < len(_DLG_HEADER):
        return None
    key = bytes(a ^ b for a, b in zip(stored[:4], b"# -*", strict=True))
    decoded = _xor4(stored, key)
    return decoded if decoded.startswith(_DLG_HEADER) else None


def extract_resource_paths(data: bytes) -> list[str]:
    """从 .dlg 明文字节里扒出被引用的资源路径（图片为主）。

    路径在布局文本中以 GBK 字节明文出现；按分隔符切词后，保留
    含目录分隔符、且以图片扩展名结尾的词，GBK 解码失败丢弃。
    """
    found: list[str] = []
    seen: set[str] = set()
    for token in _TOKEN_SPLIT.split(data):
        if len(token) < 5 or len(token) > 240:
            continue
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
