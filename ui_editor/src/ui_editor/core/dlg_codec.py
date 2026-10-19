"""``.dlg`` 布局文件的解析与序列化（保型往返）。

文件格式（游戏客户端与 UI 编辑器的交换格式）：

* 第 1 行 ``# -*- coding: gbk -*-``、第 2 行 ``# MD5: <32 位十六
  进制>``（编辑器侧校验标记，运行时 ``exec`` 时只是注释）、空行；
* ``UI_INFO = [ {...}, ... ]``：控件字典列表，子控件在
  ``lChildren`` 里递归嵌套；值为 int/float/bool/str/list/tuple。

序列化风格与原文件一致：制表符缩进、双引号字符串、每项一行且
逗号后带空格、非空容器多行展开。键序采用「常用键优先 + 其余
字母序」的固定顺序（运行时 ``exec`` 不依赖顺序）。

编码是混合的，不能整文件按一种编码处理：经 2,706 个真实文件
统计，显示文本（``sText/sTitle/sTitles/sTips``）为 Big5 字节，
资源路径（``sFileName/sBarFileName/sBgFileName/sSoundPath``）
为 GBK 字节。解析时先以 GB18030 还原源代码形态，再按字段把
原始字节分别按 Big5/GBK 解码；序列化时反向处理。这样界面上
看到和编辑的是正确繁体文本，落盘字节仍与游戏资源约定一致。

显示文本可由 text_encoding 选择 Big5（默认）/GBK/UTF-8；只作用于
sText/sTitle/sTitles/sTips（含嵌套容器），资源路径仍为 GBK。读写必须
使用同一文档编码；这不是全文件转码，也不是简繁转换。

验收口径：2,706 个已解密布局应全部通过「解析 → 序列化 →
再解析」的结构一致性（见 tests/test_codec.py 的语料库测试）。
"""

from __future__ import annotations

import ast
import hashlib
import re

from .errors import DlgError

HEADER_LINE = "# -*- coding: gbk -*-"
_MD5_RE = re.compile(r"^#\s*MD5:\s*([0-9a-fA-F]{32})\s*$", re.MULTILINE)

# 序列化时排在前面的常用键，其余键按字母序。
_PREFERRED_KEYS = (
    "sWidgetType", "sName", "iX", "iY", "iWidth", "iHeight",
    "sFileName", "sText", "sTitle", "iStyle", "iFont",
    "iMsgId", "bShow", "bLoad", "lChildren",
)

__all__ = ["parse_bytes", "parse_text", "dump_bytes", "dump_text"]

# 台服显示文本默认 Big5，可选择简体 GBK/UTF-8；资源路径固定 GBK。
TEXT_ENCODINGS = ("big5", "gbk", "utf-8")


def _validate_encoding(encoding: str) -> None:
    if encoding not in TEXT_ENCODINGS:
        raise ValueError(f"不支持的布局文本编码：{encoding}")


_BIG5_TEXT_KEYS = frozenset({"sText", "sTitle", "sTitles", "sTips"})
_GBK_PATH_KEYS = frozenset(
    {"sFileName", "sBarFileName", "sBgFileName", "sSoundPath"})


def parse_text(text: str, *, text_encoding: str = "big5"
               ) -> tuple[list[dict], str | None]:
    """解析按 GB18030 解开的 .dlg 源文本，返回 (控件字典列表, MD5)。

    这里解析出的字符串先按字段做 Big5/GBK 还原，调用方拿到的是
    可直接显示、编辑的 Unicode 文本。
    """
    _validate_encoding(text_encoding)
    # ast.literal_eval 无法直接吃带 surrogate 的源码文本，故把
    # 挂起字节写成 \uXXXX 字面转义；解析后字符串里仍是挂起字符，
    # 由 _decode_value 按字段还原为原始字节。
    text = "".join(
        f"\\u{ord(ch):04x}" if 0xDC80 <= ord(ch) <= 0xDCFF else ch
        for ch in text)
    match = _MD5_RE.search(text)
    md5 = match.group(1).lower() if match else None
    marker = text.find("UI_INFO")
    if marker < 0:
        raise DlgError("文件中找不到 UI_INFO")
    eq = text.find("=", marker)
    if eq < 0:
        raise DlgError("UI_INFO 后缺少 = 号")
    try:
        value = ast.literal_eval(text[eq + 1:].strip())
    except (SyntaxError, ValueError) as exc:
        raise DlgError(f"UI_INFO 字面量解析失败：{exc}") from exc
    if not isinstance(value, list) or not all(
            isinstance(item, dict) for item in value):
        raise DlgError("UI_INFO 应为控件字典组成的列表")
    return [_decode_value(item, text_encoding=text_encoding) for item in value], md5


def parse_bytes(data: bytes, *, text_encoding: str = "big5"
                ) -> tuple[list[dict], str | None]:
    """解析 .dlg 字节（源代码形态按 GB18030 还原，内容按字段解码）。"""
    # surrogateescape：少数 Big5 字节组合在 GB18030 里非法，
    # 先把这类字节挂起，后续按字段解码时再还原，保证不丢字节。
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("gb18030", "surrogateescape")
    return parse_text(text, text_encoding=text_encoding)


def dump_text(widgets: list[dict], md5: str | None = None, *,
              text_encoding: str = "big5") -> str:
    """把控件字典列表序列化成源文本形态（字段已按目标编码预处理）。"""
    _validate_encoding(text_encoding)
    prepared = [_encode_value(widget, text_encoding=text_encoding)
                for widget in widgets]
    body = "UI_INFO = " + _format_value(prepared, 0) + "\n"
    if md5 is None:
        md5 = hashlib.md5(body.encode("gb18030", "surrogateescape")).hexdigest()
    return f"{HEADER_LINE}\n# MD5: {md5}\n\n{body}\n"


def dump_bytes(widgets: list[dict], md5: str | None = None, *,
               text_encoding: str = "big5") -> bytes:
    """序列化为落盘字节；字段字节已由 dump_text 预处理成源形态。"""
    return dump_text(widgets, md5, text_encoding=text_encoding).encode(
        "gb18030", "surrogateescape")


def _decode_value(value: object, key: str | None = None, *,
                  text_encoding: str = "big5") -> object:
    """递归地把源字符串按字段还原为正确的 Unicode 文本。"""
    if isinstance(value, str):
        return _decode_string(value, key, text_encoding)
    if isinstance(value, dict):
        return {str(k): _decode_value(v, str(k), text_encoding=text_encoding)
                for k, v in value.items()}
    if isinstance(value, list):
        return [_decode_value(item, key, text_encoding=text_encoding) for item in value]
    if isinstance(value, tuple):
        return tuple(_decode_value(item, key, text_encoding=text_encoding)
                     for item in value)
    return value


def _decode_string(value: str, key: str | None, text_encoding: str) -> str:
    if all(ord(ch) < 128 for ch in value):
        return value
    codec = None
    if key in _BIG5_TEXT_KEYS:
        codec = text_encoding
    elif key in _GBK_PATH_KEYS:
        codec = "gbk"
    if codec is None:
        return value
    # value 是 GB18030 解开的源形态；先还原该字段的原始字节再按
    # 字段编码解码。surrogateescape 保留极少数未收录码位，不丢字节。
    raw = value.encode("gb18030", "surrogateescape")
    return raw.decode(codec, "surrogateescape")


def _encode_value(value: object, key: str | None = None, *,
                  text_encoding: str = "big5") -> object:
    """递归地把 Unicode 文本按字段编码回源字符串形态。"""
    if isinstance(value, str):
        return _encode_string(value, key, text_encoding)
    if isinstance(value, dict):
        return {str(k): _encode_value(v, str(k), text_encoding=text_encoding)
                for k, v in value.items()}
    if isinstance(value, list):
        return [_encode_value(item, key, text_encoding=text_encoding) for item in value]
    if isinstance(value, tuple):
        return tuple(_encode_value(item, key, text_encoding=text_encoding)
                     for item in value)
    return value


def _encode_string(value: str, key: str | None, text_encoding: str) -> str:
    if all(ord(ch) < 128 for ch in value):
        return value
    if key in _BIG5_TEXT_KEYS:
        codec = text_encoding
    elif key in _GBK_PATH_KEYS:
        codec = "gbk"
    else:
        return value
    # surrogateescape 保留原始文件中无法按 GB18030 解码的字节；
    # 目标编码无法表示普通 Unicode 字符时仍直接抛错，不做 GB18030 回退。
    raw = value.encode(codec, "surrogateescape")
    return raw.decode("gb18030", "surrogateescape")


def _ordered_keys(d: dict) -> list[str]:
    head = [k for k in _PREFERRED_KEYS if k in d]
    tail = sorted(k for k in d if k not in _PREFERRED_KEYS)
    return head + tail


def _format_value(value: object, level: int) -> str:
    """按原版式格式化一个值；level 为闭括号所在缩进层（制表符数）。"""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return _format_string(value)
    if value is None:
        return "None"
    if isinstance(value, dict):
        if not value:
            return "{}"
        parts = ["{"]
        for key in _ordered_keys(value):
            parts.append(
                "\t" * (level + 1)
                + _format_string(str(key)) + ": "
                + _format_value(value[key], level + 1) + ", "
            )
        parts.append("\t" * level + "}")
        return "\n".join(parts)
    if isinstance(value, (list, tuple)):
        if not value:
            return "[]" if isinstance(value, list) else "()"
        open_c, close_c = ("[", "]") if isinstance(value, list) else ("(", ")")
        parts = [open_c]
        for item in value:
            parts.append(
                "\t" * (level + 1) + _format_value(item, level + 1) + ", ")
        parts.append("\t" * level + close_c)
        return "\n".join(parts)
    raise DlgError(f"不支持的值类型：{type(value).__name__}")


def _format_string(text: str) -> str:
    """双引号字符串字面量：转义引号、反斜杠与控制字符，其余原样。"""
    out = ['"']
    for ch in text:
        code = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\x{code:02x}")
        elif 0xDC80 <= code <= 0xDCFF:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)
