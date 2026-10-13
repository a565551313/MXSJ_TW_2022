"""``ui.lst`` 样式注册表解析（字体表、按钮样式等）。

ui.lst 是 interface.fls 内的明文 INI 风格文件：``[Font]`` /
``[NewFont]`` 两节是字体表（每行 ``字体名 字号 字重 标记``），
``[TBStyle_000]`` 起是文字按钮样式（``键=值``，颜色为以空格分
隔的 RGB 三元组，6 个数表示上下渐变），其余节（List/Table/
Frame/Border…）是各控件类的样式参数。控件上的 ``iFont`` 是
字体表下标，``iStyle`` 是 TBStyle 下标。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_SECTION_RE = re.compile(r"^\[(.+)\]\s*$")
_TBSTYLE_RE = re.compile(r"^TBStyle_(\d+)$")

__all__ = ["FontDef", "StyleBook"]


@dataclass
class FontDef:
    """一条字体定义。"""

    name: str
    size: int
    weight: int


@dataclass
class StyleBook:
    """解析后的样式表。"""

    fonts: list[FontDef] = field(default_factory=list)
    new_fonts: list[FontDef] = field(default_factory=list)
    tbstyles: list[dict[str, str]] = field(default_factory=list)
    sections: dict[str, list[str]] = field(default_factory=dict)

    @property
    def loaded(self) -> bool:
        return bool(self.fonts or self.tbstyles)

    @classmethod
    def parse_text(cls, text: str) -> StyleBook:
        book = cls()
        current: str | None = None
        tb_map: dict[int, dict[str, str]] = {}
        for raw in text.splitlines():
            line = raw.strip()
            if not line:
                continue
            section_match = _SECTION_RE.match(line)
            if section_match:
                current = section_match.group(1)
                book.sections.setdefault(current, [])
                continue
            if current is None:
                continue
            book.sections[current].append(line)
            if current in ("Font", "NewFont"):
                font = _parse_font_line(line)
                if font is not None:
                    target = book.fonts if current == "Font" else book.new_fonts
                    target.append(font)
            else:
                style_match = _TBSTYLE_RE.match(current)
                if style_match and "=" in line:
                    key, _, value = line.partition("=")
                    entry = tb_map.setdefault(int(style_match.group(1)), {})
                    entry[key.strip()] = value.strip()
        if tb_map:
            book.tbstyles = [tb_map.get(i, {}) for i in range(max(tb_map) + 1)]
        return book

    @classmethod
    def parse_bytes(cls, data: bytes) -> StyleBook:
        """按节解码原始字节：字体名是 Big5，其余行以 GB18030 兜底。"""
        lines: list[str] = []
        section = ""
        for raw in data.splitlines():
            header = raw.strip()
            if header.startswith(b"[") and header.endswith(b"]"):
                section = header[1:-1].decode("ascii", "replace")
            codec = "big5" if section in ("Font", "NewFont") else "gb18030"
            lines.append(raw.decode(codec, "surrogateescape"))
        return cls.parse_text("\n".join(lines))

    def font(self, index: int) -> FontDef | None:
        """按 iFont 取字体：先 [Font] 后 [NewFont]，越界返回 None。"""
        if 0 <= index < len(self.fonts):
            return self.fonts[index]
        if 0 <= index < len(self.new_fonts):
            return self.new_fonts[index]
        return None

    def tbstyle(self, index: int) -> dict[str, str]:
        """按 iStyle 取文字按钮样式，越界返回空字典。"""
        if 0 <= index < len(self.tbstyles):
            return self.tbstyles[index]
        return {}


def _parse_font_line(line: str) -> FontDef | None:
    """解析 ``字体名 字号 字重 [标记]``（字体名可含空格）。

    从右往左找数值：末尾三个整数是（字号, 字重, 标记），两个则
    是（字号, 字重）。数值异常则返回 None，容错跳过。
    """
    tokens = line.split()
    if len(tokens) >= 4:
        try:
            size, weight = int(tokens[-3]), int(tokens[-2])
            int(tokens[-1])
        except ValueError:
            pass
        else:
            return FontDef(" ".join(tokens[:-3]), size, weight)
    if len(tokens) >= 3:
        try:
            size, weight = int(tokens[-2]), int(tokens[-1])
        except ValueError:
            return None
        return FontDef(" ".join(tokens[:-2]), size, weight)
    return None
