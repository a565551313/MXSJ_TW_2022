"""``.dlg`` 布局文件的解析与序列化（保型往返）。

文件格式（游戏客户端与 UI 编辑器的交换格式）：

* 第 1 行 ``# -*- coding: gbk -*-``、第 2 行 ``# MD5: <32 位十六
  进制>``（编辑器侧校验标记，运行时 ``exec`` 时只是注释）、空行；
* ``UI_INFO = [ {...}, ... ]``：控件字典列表，子控件在
  ``lChildren`` 里递归嵌套；值为 int/float/bool/str/list/tuple。

序列化风格与原文件一致：制表符缩进、双引号字符串、每项一行且
逗号后带空格、非空容器多行展开。键序采用「常用键优先 + 其余
字母序」的固定顺序（运行时 ``exec`` 不依赖顺序）。字符串转义
后以 GBK 落盘（含 GBK 外字符时退回 GB18030，保证不崩）。

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


def parse_text(text: str) -> tuple[list[dict], str | None]:
    """解析 .dlg 文本，返回 (控件字典列表, MD5 或 None)。"""
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
    return value, md5


def parse_bytes(data: bytes) -> tuple[list[dict], str | None]:
    """解析 .dlg 字节（GBK/GB18030 文本）。"""
    try:
        text = data.decode("gb18030")
    except UnicodeDecodeError as exc:
        raise DlgError(f"文件不是 GBK 文本：{exc}") from exc
    return parse_text(text)


def dump_text(widgets: list[dict], md5: str | None = None) -> str:
    """把控件字典列表序列化为 .dlg 文本（不含最终编码）。"""
    body = "UI_INFO = " + _format_value(widgets, 0) + "\n"
    if md5 is None:
        md5 = hashlib.md5(body.encode("gb18030")).hexdigest()
    return f"{HEADER_LINE}\n# MD5: {md5}\n\n{body}\n"


def dump_bytes(widgets: list[dict], md5: str | None = None) -> bytes:
    """序列化为落盘字节：优先 GBK，外字符时退回 GB18030。"""
    text = dump_text(widgets, md5)
    try:
        return text.encode("gbk")
    except UnicodeEncodeError:
        return text.encode("gb18030")


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
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)
