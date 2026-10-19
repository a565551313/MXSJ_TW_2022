"""布局文档模型：控件树 + 新建控件工厂（零 Qt 依赖）。

控件的全部属性保存在 ``props`` 字典里（与 .dlg 的字典一一对应，
未知字段原样保留）；子控件从 ``lChildren`` 拆出为独立的
:class:`Widget` 列表，转回字典时再放回。这样属性面板与序列化
都不需要为每种控件类型写死结构。
"""

from __future__ import annotations

import copy

from .defaults_data import DEFAULT_PROPS
from .review import LayoutChange, layout_changes

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
        if "lChildren" not in data:
            children = []
        else:
            children = data["lChildren"]
            if not isinstance(children, list):
                raise ValueError("lChildren 必须是控件字典列表")
        for child in children:
            if not isinstance(child, dict):
                raise ValueError("lChildren 只能包含控件字典")
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
        self.text_encoding = "big5"
        self.source_bytes: bytes | None = None  # 解密后的原始布局，用于切换编码
        # 来源：本地 .dlg 路径，或 (包路径, 资源路径) 二元组（二选一）
        self.source_path: str | None = None
        self.source_pack: tuple[str, str] | None = None
        self.dirty = False
        self.pending_pack_import = False  # 未落到新包，即使撤销至导入状态仍待保存
        # 撤销/重做时间线：to_dicts() 快照列表，_h_index 指当前状态
        self._history: list[list[dict]] = []
        self._h_index = -1
        self._last_merge_key = None
        self._saved_state = self._snapshot()

    def begin_pack_import(self, previous: list[dict]) -> None:
        """导入以原包内容为清单基线；新增布局以空列表为基线。"""
        self._saved_state = copy.deepcopy(previous)
        self.pending_pack_import = True
        self.dirty = True

    def mark_saved(self) -> None:
        """仅成功写入后建立清单基线；保留撤销时间线。"""
        self._saved_state = self._snapshot()
        self.dirty = False
        self._last_merge_key = None

    def changes(self) -> list[LayoutChange]:
        return layout_changes(self._saved_state, self.to_dicts())

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
        self.dirty = bool(layout_changes(self._saved_state, state))

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

    def unique_variant_name(self, base: str,
                            used: set[str] | None = None) -> str:
        """复制粘贴用名：``BTN`` → ``BTN_1``、``BTN_1`` → ``BTN_1_1``。

        不重名时原样返回；重名则加 ``_n``（n 从 1 起，跳过已占用的
        编号）。``used`` 传已占用名字集合（调用方批量处理时自己维护）。
        空名字不参与改名（无名控件保持无名）。
        """
        if not base:
            return base
        names = used if used is not None else {w.name for w in self.all_widgets()}
        if base not in names:
            return base
        index = 1
        while f"{base}_{index}" in names:
            index += 1
        return f"{base}_{index}"

    def rename_copies(self, clones: list[Widget],
                      reserved: set[str] | None = None) -> list[int]:
        """给刚粘贴进来的控件（含子树）改掉重名的名字，返回改了几个。

        名字重名才改（不重名保持原样），规则见 :meth:`unique_variant_name`；
        子树里的重名子控件同样处理，避免与原件子控件撞名。
        """
        used = reserved
        if used is None:
            used = {w.name for w in self.all_widgets()}
        changed = 0
        for root in clones:
            for widget in root.walk():
                new_name = self.unique_variant_name(widget.name, used)
                if new_name != widget.name:
                    widget.name = new_name
                    changed += 1
                if widget.name:
                    used.add(widget.name)
        return changed

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

    # -- 父子级（置父 / 箭头升降级） ---------------------------------
    def reparent_reason(self, widget: Widget,
                        parent: Widget | None) -> str | None:
        """不能把 widget 挂到 parent 下的原因；可以则返回 None。

        防环（挂到自己或子孙下面）与锁定护栏：自身或子孙已锁定时不改
        结构，与删除护栏一致。
        """
        if parent is None:
            return None
        if parent is widget:
            return "不能把控件挂到它自己下面。"
        node: Widget | None = parent
        while node is not None:
            if node is widget:
                return "不能把控件挂到它自己的子孙下面。"
            node = node.parent
        if any(node.locked for node in widget.walk()):
            name = widget.name or "(未命名)"
            return f"「{name}」或它的子控件已锁定，先解锁再改父子级。"
        return None

    @staticmethod
    def clamp_into(box: tuple[int, int] | None, x: float, y: float,
                   width: int, height: int) -> tuple[int, int]:
        """把子控件左上角夹进父矩形（box=父的有效像素尺寸）。

        box 为 None 或某一维 <=0 表示尺寸未知（父控件宽高为 0、靠图片
        撑开但当前解析不到），只保证坐标非负、不按未知尺寸夹，避免把
        子控件压到左上角。
        """
        ix, iy = int(round(x)), int(round(y))
        if box is None:
            return max(ix, 0), max(iy, 0)
        box_w, box_h = box
        if box_w > 0:
            ix = min(max(ix, 0), max(0, box_w - width))
        else:
            ix = max(ix, 0)
        if box_h > 0:
            iy = min(max(iy, 0), max(0, box_h - height))
        else:
            iy = max(iy, 0)
        return ix, iy

    def set_parent(self, widget: Widget, parent: Widget | None,
                   index: int | None = None,
                   parent_size: tuple[int, int] | None = None) -> None:
        """把控件挂到 parent 下（None=顶级），父就是子的坐标系。

        子坐标换算为相对新父左上角的局部坐标，并夹进父矩形（超出部分
        自动挪进来），保证置父后子控件落在父"画布"内。
        """
        abs_x, abs_y = self.abs_position(widget)
        self.siblings_of(widget).remove(widget)
        px, py = self.abs_position(parent) if parent is not None else (0, 0)
        widget.parent = parent
        siblings = parent.children if parent is not None else self.roots
        if index is None:
            siblings.append(widget)
        else:
            siblings.insert(index, widget)
        box = parent_size
        if box is None and parent is not None:
            box = (parent.width, parent.height)
        x, y = self.clamp_into(box, abs_x - px, abs_y - py,
                               widget.width, widget.height)
        widget.set_geometry(x=x, y=y)
        self.dirty = True

    def indent_widget(self, widget: Widget, sizer=None) -> str | None:
        """降一级：挂成上一个同级控件的子控件；返回失败原因或 None。

        sizer(控件) 返回该控件的有效像素尺寸，用来把子控件夹进父矩形；
        不给则退回 ``iWidth/iHeight``。
        """
        siblings = self.siblings_of(widget)
        index = siblings.index(widget)
        if index == 0:
            return "它已经是同级第一个，没有可挂靠的上一个同级控件。"
        target = siblings[index - 1]
        reason = self.reparent_reason(widget, target)
        if reason is not None:
            return reason
        size = sizer(target) if sizer is not None else None
        self.set_parent(widget, target, parent_size=size)
        return None

    def outdent_widget(self, widget: Widget, sizer=None) -> str | None:
        """升一级：脱离父控件，成为父控件的下一个同级。"""
        parent = widget.parent
        if parent is None:
            return "它已经是顶级控件。"
        siblings = self.siblings_of(parent)
        new_parent = parent.parent
        size = (sizer(new_parent) if sizer is not None
                and new_parent is not None else None)
        self.set_parent(widget, new_parent,
                        index=siblings.index(parent) + 1, parent_size=size)
        return None

    @property
    def display_name(self) -> str:
        if self.source_path:
            return self.source_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if self.source_pack:
            return self.source_pack[1]
        return "未命名布局"
