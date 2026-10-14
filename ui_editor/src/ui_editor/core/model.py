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
    """一个控件：属性字典 + 子控件列表 + 父指针。

    ``locked`` 是编辑器专属状态（布局时防手滑），只存在内存里：
    不进 ``props``、不写回 .dlg，复制/粘贴出的克隆默认未锁定。
    """

    __slots__ = ("props", "children", "parent", "locked")

    def __init__(self, props: dict | None = None,
                 parent: Widget | None = None) -> None:
        self.props: dict = dict(props or {})
        self.children: list[Widget] = []
        self.parent = parent
        self.locked = False

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

    HISTORY_LIMIT = 50  # 撤销时间线最多保留的步数

    def __init__(self, roots: list[Widget] | None = None,
                 md5: str | None = None) -> None:
        self.roots: list[Widget] = roots or []
        self.md5 = md5
        # 来源：本地 .dlg 路径，或 (包路径, 资源路径) 二元组（二选一）
        self.source_path: str | None = None
        self.source_pack: tuple[str, str] | None = None
        self.dirty = False
        # 撤销/重做时间线：to_dicts() 快照列表，_h_index 指当前状态
        self._history: list[list[dict]] = []
        self._h_index = -1
        self._last_merge_key = None

    # -- 撤销/重做（快照时间线，设计见 notes/ui_editor_phase2） ----
    def _snapshot(self) -> list[dict]:
        return copy.deepcopy(self.to_dicts())

    def reset_history(self) -> None:
        """打开/新建文档后调用：时间线只含当前状态。"""
        self._history = [self._snapshot()]
        self._h_index = 0
        self._last_merge_key = None

    def checkpoint(self, merge_key=None) -> None:
        """一次编辑提交后记一步。

        同 merge_key 且位于时间线末端时，把新状态并入末端步
        （连续改同一字段只算一步）；否则截断重做尾巴并追加，
        超过 HISTORY_LIMIT 丢最老状态。
        """
        state = self._snapshot()
        if not self._history:
            self._history = [state]
            self._h_index = 0
            self._last_merge_key = merge_key
            return
        if (merge_key is not None
                and merge_key == self._last_merge_key
                and self._h_index == len(self._history) - 1):
            self._history[self._h_index] = state
        else:
            del self._history[self._h_index + 1:]
            self._history.append(state)
            while len(self._history) > self.HISTORY_LIMIT:
                self._history.pop(0)
            self._h_index = len(self._history) - 1
        self._last_merge_key = merge_key

    @property
    def can_undo(self) -> bool:
        return self._h_index > 0

    @property
    def can_redo(self) -> bool:
        return 0 <= self._h_index < len(self._history) - 1

    def _apply_state(self, state: list[dict]) -> None:
        self.roots = [Widget.from_dict(d)
                      for d in copy.deepcopy(state)]
        self._last_merge_key = None
        self.dirty = True

    def undo(self) -> bool:
        """回退一步；成功返回 True（roots 已重建，选中需重解析）。"""
        if not self.can_undo:
            return False
        self._h_index -= 1
        self._apply_state(self._history[self._h_index])
        return True

    def redo(self) -> bool:
        """前进一步；成功返回 True。"""
        if not self.can_redo:
            return False
        self._h_index += 1
        self._apply_state(self._history[self._h_index])
        return True

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

    def insert_widget(self, widget: Widget, parent: Widget | None = None,
                      index: int | None = None) -> Widget:
        """把已有控件（克隆/粘贴来的）挂进文档，返回该控件。"""
        widget.parent = parent
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

    def abs_position(self, widget: Widget) -> tuple[int, int]:
        """累加各级父控件偏移，得到画布上的绝对位置。"""
        x, y = widget.x, widget.y
        node = widget.parent
        while node is not None:
            x += node.x
            y += node.y
            node = node.parent
        return x, y

    def move_to_root(self, widget: Widget, index: int | None = None) -> None:
        """把控件提升为顶级控件；坐标换算成绝对位置，视觉不跳位。"""
        if widget.parent is None:
            return
        abs_x, abs_y = self.abs_position(widget)
        widget.parent.children.remove(widget)
        widget.parent = None
        if index is None:
            self.roots.append(widget)
        else:
            self.roots.insert(index, widget)
        widget.set_geometry(x=abs_x, y=abs_y)
        self.dirty = True

    @property
    def display_name(self) -> str:
        if self.source_path:
            return self.source_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if self.source_pack:
            return self.source_pack[1]
        return "未命名布局"
