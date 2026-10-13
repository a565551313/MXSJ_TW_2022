"""布局文档模型：控件树 + 新建控件工厂（零 Qt 依赖）。

控件的全部属性保存在 ``props`` 字典里（与 .dlg 的字典一一对应，
未知字段原样保留）；子控件从 ``lChildren`` 拆出为独立的
:class:`Widget` 列表，转回字典时再放回。这样属性面板与序列化
都不需要为每种控件类型写死结构。
"""

from __future__ import annotations

import copy

from .defaults_data import DEFAULT_PROPS

WIDGET_TYPES: tuple[str, ...] = tuple(sorted(DEFAULT_PROPS))

# 新建控件自动命名时用的前缀（去掉类型名的 C 前缀后小写）
_NAME_PREFIX_OVERRIDES = {
    "CMainFrame": "mainframe",
    "CTextButton": "textbutton",
    "CImagesFrame": "images",
}


def _int_prop(props: dict, key: str) -> int:
    value = props.get(key, 0)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


class Widget:
    """一个控件：属性字典 + 子控件列表 + 父指针。"""

    __slots__ = ("props", "children", "parent")

    def __init__(self, props: dict | None = None,
                 parent: Widget | None = None) -> None:
        self.props: dict = dict(props or {})
        self.children: list[Widget] = []
        self.parent = parent

    # -- 常用属性 -------------------------------------------------
    @property
    def wtype(self) -> str:
        return str(self.props.get("sWidgetType", ""))

    @property
    def name(self) -> str:
        return str(self.props.get("sName", ""))

    @name.setter
    def name(self, value: str) -> None:
        self.props["sName"] = value

    @property
    def x(self) -> int:
        return _int_prop(self.props, "iX")

    @property
    def y(self) -> int:
        return _int_prop(self.props, "iY")

    @property
    def width(self) -> int:
        return _int_prop(self.props, "iWidth")

    @property
    def height(self) -> int:
        return _int_prop(self.props, "iHeight")

    def set_geometry(self, x: int | None = None, y: int | None = None,
                     width: int | None = None, height: int | None = None
                     ) -> None:
        if x is not None:
            self.props["iX"] = int(x)
        if y is not None:
            self.props["iY"] = int(y)
        if width is not None:
            self.props["iWidth"] = max(0, int(width))
        if height is not None:
            self.props["iHeight"] = max(0, int(height))

    # -- 结构 -----------------------------------------------------
    @classmethod
    def from_dict(cls, data: dict, parent: Widget | None = None) -> Widget:
        props = {k: v for k, v in data.items() if k != "lChildren"}
        widget = cls(props, parent)
        children = data.get("lChildren") or []
        if isinstance(children, list):
            for child in children:
                if isinstance(child, dict):
                    widget.children.append(cls.from_dict(child, widget))
        return widget

    def to_dict(self) -> dict:
        data = dict(self.props)
        data["lChildren"] = [child.to_dict() for child in self.children]
        return data

    def walk(self):
        """深度优先遍历自身与全部后代。"""
        yield self
        for child in self.children:
            yield from child.walk()

    def clone(self) -> Widget:
        return Widget.from_dict(copy.deepcopy(self.to_dict()))


class LayoutDocument:
    """一个布局文档：顶层控件列表 + 来源信息 + 脏标记。"""

    def __init__(self, roots: list[Widget] | None = None,
                 md5: str | None = None) -> None:
        self.roots: list[Widget] = roots or []
        self.md5 = md5
        # 来源：本地 .dlg 路径，或 (包路径, 资源路径) 二元组（二选一）
        self.source_path: str | None = None
        self.source_pack: tuple[str, str] | None = None
        self.dirty = False

    @classmethod
    def from_dicts(cls, dicts: list[dict], md5: str | None) -> LayoutDocument:
        return cls([Widget.from_dict(d) for d in dicts], md5)

    def to_dicts(self) -> list[dict]:
        return [widget.to_dict() for widget in self.roots]

    def all_widgets(self) -> list[Widget]:
        result: list[Widget] = []
        for root in self.roots:
            result.extend(root.walk())
        return result

    # -- 编辑操作（调用方负责置 dirty 与刷新界面） ----------------
    def unique_name(self, wtype: str) -> str:
        """为新控件生成不重名的名字，如 ``button1``。"""
        prefix = _NAME_PREFIX_OVERRIDES.get(wtype)
        if prefix is None:
            base = wtype[1:] if wtype.startswith("C") else wtype
            prefix = base.lower()
        used = {w.name for w in self.all_widgets()}
        index = 1
        while f"{prefix}{index}" in used:
            index += 1
        return f"{prefix}{index}"

    def new_widget(self, wtype: str, parent: Widget | None = None,
                   index: int | None = None) -> Widget:
        """按默认模板新建一个控件并挂入文档，返回该控件。"""
        props = copy.deepcopy(DEFAULT_PROPS[wtype])
        widget = Widget(props, parent)
        widget.name = self.unique_name(wtype)
        siblings = parent.children if parent is not None else self.roots
        if index is None:
            siblings.append(widget)
        else:
            siblings.insert(index, widget)
        self.dirty = True
        return widget

    def remove_widget(self, widget: Widget) -> None:
        siblings = (widget.parent.children if widget.parent is not None
                    else self.roots)
        siblings.remove(widget)
        widget.parent = None
        self.dirty = True

    def siblings_of(self, widget: Widget) -> list[Widget]:
        return (widget.parent.children if widget.parent is not None
                else self.roots)

    @property
    def display_name(self) -> str:
        if self.source_path:
            return self.source_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if self.source_pack:
            return self.source_pack[1]
        return "未命名布局"
