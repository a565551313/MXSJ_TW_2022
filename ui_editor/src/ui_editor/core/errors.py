"""编辑器核心模块的统一异常。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceIssue:
    """资源解析失败的可见记录，不把损坏输入伪装成普通缺图。"""

    code: str
    path: str
    message: str


class UiEditorError(Exception):
    """核心层全部异常的基类。"""


class PackError(UiEditorError):
    """资源包读取失败（魔数、目录越界等）。"""


class DlgError(UiEditorError):
    """ .dlg 文本解析/序列化失败。"""


class SpriteError(UiEditorError):
    """精灵字节解码失败或格式不受支持。"""


class Cancelled(UiEditorError):
    """长操作被用户取消（结果作废，由调用方决定清理产物）。"""
