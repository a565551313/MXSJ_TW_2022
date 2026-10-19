"""颜色属性值的解析与回写（纯 Python，零 Qt 依赖）。

.dlg 里名字以 ``Color`` 结尾的属性（``iColor``/``lColor``/``sColor``/
``iNormalColor``…）在不同控件里写法不一：整数 ``0xRRGGBB``、带 alpha
的整数（负数或超过 24 位）、``"255,255,255"``、``"#RRGGBB"``、
``"#AARRGGBB"``、``"0xRRGGBB"``。取色器写回时**保持原来的表示
形式**（整数仍写整数、逗号串仍写逗号串），避免把一个 int 改成字符串
导致游戏加载异常。

本模块只处理值与字符串，颜色选择对话框留在界面层。
"""

from __future__ import annotations

import re

__all__ = [
    "is_color_key", "parse_color", "format_like", "to_text",
    "coerce_like", "has_alpha", "color_groups", "group_color",
    "set_group_color", "list_text",
]

_RGB_MAX = 0xFFFFFF


def is_color_key(key: str) -> bool:
    """属性名是否像颜色（``iColor``/``lNormalColor``/``sTxtColor``…）。"""
    return isinstance(key, str) and key.lower().endswith("color")


def has_alpha(value: object) -> bool:
    """原值是否带 alpha 通道（负数或超过 24 位的整数、8 位十六进制）。"""
    if isinstance(value, int) and not isinstance(value, bool):
        return value < 0 or value > _RGB_MAX
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("#"):
            return len(text) == 9
        if text.lower().startswith("0x"):
            return len(text) > 8
    return False


def parse_color(value: object) -> tuple[int, int, int, int] | None:
    """把任意写法解析成 ``(r, g, b, a)``；认不出返回 None。"""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        bits = value & 0xFFFFFFFF if value < 0 else value
        alpha = (bits >> 24) & 0xFF if has_alpha(value) else 255
        return ((bits >> 16) & 0xFF, (bits >> 8) & 0xFF, bits & 0xFF, alpha)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.startswith("#"):
        digits = text[1:]
        if len(digits) == 3:
            digits = "".join(ch * 2 for ch in digits)
        if len(digits) == 6:
            return _hex_rgb(digits, 255)
        if len(digits) == 8:  # #AARRGGBB
            return _hex_rgb(digits[2:], int(digits[:2], 16))
        return None
    if text.lower().startswith("0x"):
        digits = text[2:]
        if len(digits) == 6:
            return _hex_rgb(digits, 255)
        if len(digits) == 8:
            return _hex_rgb(digits[2:], int(digits[:2], 16))
        return None
    nums = [int(part) for part in re.split(r"[^0-9]+", text) if part]
    if len(nums) == 3 and all(0 <= n <= 255 for n in nums):
        return nums[0], nums[1], nums[2], 255
    if len(nums) == 4 and all(0 <= n <= 255 for n in nums):
        return nums[0], nums[1], nums[2], nums[3]
    return None


def _hex_rgb(digits: str, alpha: int) -> tuple[int, int, int, int] | None:
    try:
        value = int(digits, 16)
    except ValueError:
        return None
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF, alpha)


def format_like(original: object,
                rgba: tuple[int, int, int, int]) -> object:
    """按原值的表示形式回写颜色。

    - 整数：保持整数；原值带 alpha 时一并写回（负数仍写负数）。
    - ``"#RRGGBB"`` / ``"#AARRGGBB"`` / ``"0xRRGGBB"``：保持前缀与位数。
    - 分隔串：沿用原来的分隔符与逗号后的空格习惯。
    """
    r, g, b, a = (max(0, min(255, int(c))) for c in rgba)
    if isinstance(original, int) and not isinstance(original, bool):
        if not has_alpha(original):
            return (r << 16) | (g << 8) | b
        packed = (a << 24) | (r << 16) | (g << 8) | b
        if original < 0:
            packed -= 1 << 32
        return packed
    if not isinstance(original, str):
        return (r << 16) | (g << 8) | b
    text = original.strip()
    alpha = has_alpha(original)
    if text.startswith("#"):
        body = f"{a:02x}{r:02x}{g:02x}{b:02x}" if alpha \
            else f"{r:02x}{g:02x}{b:02x}"
        return "#" + body
    if text.lower().startswith("0x"):
        prefix = text[:2]
        body = f"{a:02x}{r:02x}{g:02x}{b:02x}" if alpha \
            else f"{r:02x}{g:02x}{b:02x}"
        return prefix + body
    match = re.search(r"[,;]", text)
    if match is not None:
        separator = match.group(0)
        gap = " " if re.search(rf"{separator}\s", text) else ""
    else:
        separator, gap = " ", ""
    parts = [r, g, b]
    if alpha or len(_numbers(text)) == 4:
        parts.append(a)
    return (separator + gap).join(str(part) for part in parts)


def _numbers(text: str) -> list[int]:
    return [int(part) for part in re.split(r"[^0-9]+", text) if part]


def to_text(value: object) -> str:
    """属性输入框里显示的文本。"""
    return str(value)


def coerce_like(original: object, text: str) -> object:
    """把输入框文本按原值类型转换；认不出时返回原值（不改动）。"""
    if isinstance(original, int) and not isinstance(original, bool):
        try:  # 纯数字/0x 十六进制：按整数原样收
            return int(text.strip(), 0)
        except ValueError:
            pass
        parsed = parse_color(text)
        if parsed is None:
            return original
        r, g, b, a = parsed
        packed = (a << 24) | (r << 16) | (g << 8) | b
        if has_alpha(original):
            return packed if original >= 0 else packed - (1 << 32)
        return (r << 16) | (g << 8) | b
    if isinstance(original, str):
        return text
    return original


# -- 列表形式的颜色（真实 .dlg 的主力写法） ---------------------------
# 原生属性面板把颜色当 iType 5，Code2Color 生成 3/6/9 个整数（1~3 组
# RGB）；实测真实布局里 lColor 就是 [r,g,b] / 两组 / 三组。这里按“每组
# 3 个整数”处理，容器类型（list/tuple）与长度保持不变。
_GROUP_SIZE = 3
_GROUP_LENGTHS = (3, 6, 9)


def color_groups(value: object) -> int | None:
    """列表颜色的组数：0=空表（可添加一组），3/6/9 个整数时为 1~3。

    不是可编辑的列表颜色（长度不对、含非整数、越界）返回 None，
    调用方应退回普通文本编辑器。
    """
    if not isinstance(value, (list, tuple)):
        return None
    if len(value) == 0:
        return 0
    if len(value) not in _GROUP_LENGTHS:
        return None
    for item in value:
        if isinstance(item, bool) or not isinstance(item, int):
            return None
        if not 0 <= item <= 255:
            return None
    return len(value) // _GROUP_SIZE


def group_color(value: object, index: int) -> tuple[int, int, int, int] | None:
    """取第 index 组 (r, g, b, 255)；越界返回 None。"""
    if not isinstance(value, (list, tuple)):
        return None
    start = index * _GROUP_SIZE
    if start < 0 or start + _GROUP_SIZE > len(value):
        return None
    return (value[start], value[start + 1], value[start + 2], 255)


def set_group_color(value: object, index: int,
                    rgba: tuple[int, int, int, int]) -> object:
    """改第 index 组并保持容器类型/长度；空表时补成一组 RGB。"""
    items = list(value) if isinstance(value, (list, tuple)) else []
    start = index * _GROUP_SIZE
    if start + _GROUP_SIZE > len(items):
        items.extend([0] * (start + _GROUP_SIZE - len(items)))
    red, green, blue, _alpha = (max(0, min(255, int(c))) for c in rgba)
    items[start:start + _GROUP_SIZE] = [red, green, blue]
    return tuple(items) if isinstance(value, tuple) else items


def list_text(value: object) -> str:
    """列表颜色在输入框里的文本（与普通序列编辑器同一写法）。"""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)
