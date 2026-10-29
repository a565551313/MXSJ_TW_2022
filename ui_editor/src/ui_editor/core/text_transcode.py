"""用户文字输入的目标编码字形规范化（不是整文件转码）。

Big5 布局在**属性提交**时把新输入的简体字转为台湾繁体字形；
资源路径、控件名与既有未编辑文档不经过这里。UTF-8/GBK 不做简繁
替换。落盘仍由 ``dlg_codec`` 与保存前检查严格验证目标编码，不能用
目标码页表示的字符绝不被替换为 ``?``。
"""

from __future__ import annotations

from functools import lru_cache

from opencc import OpenCC

from . import dlg_codec

__all__ = ["normalize_display_value"]


@lru_cache(maxsize=1)
def _simplified_to_taiwan() -> OpenCC:
    # s2tw 只转台湾标准字形；不用 s2twp，避免擅自替换地区词汇。
    return OpenCC("s2tw")


def normalize_display_value(value: object, key: str | None,
                            text_encoding: str) -> object:
    """规范化一次用户提交的值，保持容器类型与非显示字段不变。

    ``key`` 采用 ``dlg_codec`` 的字段语义：只有 sText/sTitle/sTitles/
    sTips（含其嵌套字符串）在 Big5 文档中转换。普通 ASCII 不启动
    OpenCC；无法编码的 Unicode 仍保留，交给现有严格保存闸门报告。
    """
    if text_encoding != "big5":
        return value
    if isinstance(value, str):
        if (key not in dlg_codec._BIG5_TEXT_KEYS
                or all(ord(char) < 128 for char in value)):
            return value
        return _simplified_to_taiwan().convert(value)
    if isinstance(value, dict):
        return {item_key: normalize_display_value(
                    item, str(item_key), text_encoding)
                for item_key, item in value.items()}
    if isinstance(value, list):
        return [normalize_display_value(item, key, text_encoding)
                for item in value]
    if isinstance(value, tuple):
        return tuple(normalize_display_value(item, key, text_encoding)
                     for item in value)
    return value
