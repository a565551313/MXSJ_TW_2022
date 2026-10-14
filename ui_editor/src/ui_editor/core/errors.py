"""编辑器核心模块的统一异常。"""

from __future__ import annotations


class UiEditorError(Exception):
    """核心层全部异常的基类。"""


class PackError(UiEditorError):
    """资源包读取失败（魔数、目录越界等）。"""


class DlgError(UiEditorError):
    """ .dlg 文本解析/序列化失败。"""


class SpriteError(UiEditorError):
    """精灵字节解码失败或格式不受支持。"""
