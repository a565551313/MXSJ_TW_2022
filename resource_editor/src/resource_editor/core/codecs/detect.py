"""条目内容嗅探：根据魔数/结构把条目内容分类，供 GUI 选择预览器。"""
from __future__ import annotations

import json
import zlib
from enum import Enum

from .sprite import SPRITE_MAGICS
from .wav import is_wav


class EntryKind(Enum):
    """条目内容类型。"""

    SPRITE = "sprite"          # I0/T0/I1 精灵
    PNG = "png"                # PNG 图片
    JSON = "json"              # JSON 文本（magicres5 配置/图集）
    TEXT = "text"              # 纯文本（含 IG 重定向记录）
    SCRIPT = "script"          # zlib 包装的脚本数据（内层仍含 XOR，不解碼）
    AUDIO = "audio"            # RIFF WAV 音频（sound.fls 整份存入）
    BINARY = "binary"          # 未识别二进制（含 effect 未破译条目）


KIND_LABELS = {
    EntryKind.SPRITE: "精灵",
    EntryKind.PNG: "PNG图片",
    EntryKind.JSON: "JSON",
    EntryKind.TEXT: "文本",
    EntryKind.SCRIPT: "脚本数据",
    EntryKind.AUDIO: "音频",
    EntryKind.BINARY: "二进制",
}


def sniff(content: bytes) -> EntryKind:
    """判断条目内容类型。content 应为完整的"内容视图"字节。"""
    return _sniff(content, complete=True)


def sniff_prefix(head: bytes) -> EntryKind:
    """只凭内容头部（至多前 512 字节）判断类型，供大包快速分类。

    与 :func:`sniff` 的区别仅在 JSON 分支：头部以 ``{``/``[`` 开头
    且可按 UTF-8 解码即判 JSON，不要求整段能解析完。
    """
    return _sniff(head, complete=False)


def _sniff(content: bytes, complete: bool) -> EntryKind:
    if len(content) >= 2 and content[:2] in SPRITE_MAGICS:
        return EntryKind.SPRITE
    if content[:4] == b"\x89PNG":
        return EntryKind.PNG
    if is_wav(content):
        return EntryKind.AUDIO
    is_zlib = (len(content) >= 2 and content[0] == 0x78
               and (content[0] * 256 + content[1]) % 31 == 0)
    if is_zlib:
        # zlib 头校验通过即可判型，避免对大包逐条全量解压
        try:
            zlib.decompressobj().decompress(content[:64])
            return EntryKind.SCRIPT
        except zlib.error:
            pass
    stripped = content.strip()
    if stripped[:1] in (b"{", b"["):
        if complete:
            try:
                json.loads(stripped.decode("utf-8"))
                return EntryKind.JSON
            except (ValueError, UnicodeDecodeError):
                pass
        else:
            try:
                stripped.decode("utf-8")
                return EntryKind.JSON
            except UnicodeDecodeError:
                pass
    if content and _looks_textual(content):
        return EntryKind.TEXT
    return EntryKind.BINARY


def _looks_textual(content: bytes) -> bool:
    """粗判是否为可读文本：可打印字节占绝对多数。"""
    sample = content[:512]
    printable = sum(1 for b in sample if b in (9, 10, 13) or 0x20 <= b < 0x7F)
    return printable >= int(len(sample) * 0.95)
