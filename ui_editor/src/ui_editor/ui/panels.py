"""左侧资源树、控件树面板与控件面板（调色板）。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..core.catalog import (
    GENERATION_CURRENT,
    GENERATION_TRANSITIONAL,
    generation_of,
)
from ..core.model import WIDGET_TYPES, LayoutDocument, Widget

_COLOR_CURRENT = QBrush(QColor("#1a7f37"))
_COLOR_TRANSITIONAL = QBrush(QColor("#9a6700"))
_COLOR_MISSING = QBrush(QColor("#8a8a8a"))


def _style_leaf(item: QTreeWidgetItem, res_path: str,
                missing: bool = False) -> None:
    """按代际给布局叶子着色；包内缺失的灰色斜体。"""
    if missing:
        item.setForeground(0, _COLOR_MISSING)
        font = item.font(0)
        font.setItalic(True)
        item.setFont(0, font)
        item.setToolTip(
            0, "内置目录中有此布局，但该资源包里没有"
               "（死引用或热更新资源）；双击会提示打不开。")
        return
    gen = generation_of(res_path)
    if gen == GENERATION_CURRENT:
        item.setForeground(0, _COLOR_CURRENT)
        item.setToolTip(0, "现役新 UI（dialog4 / login_new / 新系统目录）")
    elif gen == GENERATION_TRANSITIONAL:
        item.setForeground(0, _COLOR_TRANSITIONAL)
        item.setToolTip(0, "第三代布局（dialog3，过渡层）")


class ResourceTreePanel(QWidget):
    """资源树：已挂载的包/散装目录做根节点，下挂其布局。

    根节点累加不替换：从资源包打开、从资源目录打开、打开散装
    布局目录都会往树上追加。双击包内布局发 open_pack_layout，
    双击散装 .dlg 发 open_loose_file。散装目录严格过滤：只有
    .dlg 文件与（递归地）含有 .dlg 的文件夹才出现。
    """

    open_pack_layout = Signal(str, str)  # (包路径, 资源路径)
    import_pack_layout = Signal(str)    # 包根右键导入
    open_loose_file = Signal(str)        # 散装 .dlg 路径
    choose_resource_dir = Signal()
    choose_loose_dir = Signal()

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        res_btn = QPushButton("打开资源目录…")
        res_btn.setToolTip("挂载整个资源目录，并把其中每个包及其布局挂到树上")
        res_btn.clicked.connect(self.choose_resource_dir)
        loose_btn = QPushButton("打开布局目录…")
        loose_btn.setToolTip("把散装 .dlg 目录挂到树上（已解密布局目录用这个）")
        loose_btn.clicked.connect(self.choose_loose_dir)
        bar.addWidget(res_btn, 1)
        bar.addWidget(loose_btn, 1)
        layout.addLayout(bar)
        self._search = QLineEdit()
        self._search.setPlaceholderText("按名称查找布局（如 service）…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_search)
        layout.addWidget(self._search)
        hint = QLabel("双击布局即可切换打开；包节点右键可导入本地布局（待存新包）。"
                      "绿色为现役新 UI，橙色为第三代，灰色斜体为包内缺失。")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)
        self._pending_item: QTreeWidgetItem | None = None
        layout.addWidget(self._tree, 1)
        self._roots: dict[tuple[str, str], QTreeWidgetItem] = {}

    def _show_context_menu(self, pos) -> None:
        item = self._tree.itemAt(pos)
        data = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        if not data or data[0] != "packroot":
            return
        menu = QMenu(self)
        action = menu.addAction("导入布局文件…")
        action.triggered.connect(lambda: self.import_pack_layout.emit(data[1]))
        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def clear_pending(self) -> None:
        if self._pending_item is not None:
            root = self._pending_item.parent()
            root.takeChild(root.indexOfChild(self._pending_item))
            self._pending_item = None

    def show_pending(self, pack_path: str, res_path: str) -> None:
        """仅单文档待入包叶子；取消/切换时删除，不假装已在源包里。"""
        self.clear_pending()
        self.add_pack(pack_path, [])
        root = self._roots[("pack", pack_path)]
        leaf = QTreeWidgetItem([res_path + "（待入新包）"])
        leaf.setData(0, Qt.ItemDataRole.UserRole, ("pending", pack_path, res_path))
        leaf.setToolTip(0, "当前编辑文档，尚未写入资源包；保存只生成新包。")
        root.addChild(leaf)
        self._pending_item = leaf
        self._search.clear()
        root.setExpanded(True)
        root.setHidden(False)
        self._tree.scrollToItem(leaf)
        self.reveal_selection(("pending", pack_path, res_path))

    # -- 根节点管理 -------------------------------------------------
    def add_pack(self, pack_path: str | Path, layouts: list[str],
                 missing: list[str] | tuple[str, ...] = ()) -> None:
        """把一个资源包挂到树上。已在树上则原样保留：不重建节点、

        不改位置与展开状态。否则每次双击打开布局，包节点都会被
        拆掉重挂到末尾并收起，树看起来就会「跳来跳去」。
        """
        key = ("pack", str(pack_path))
        if key in self._roots:
            return
        name = Path(pack_path).name
        label = f"{name}（{len(layouts)} 个布局"
        if missing:
            label += f"，另 {len(missing)} 个包内缺失"
        root = QTreeWidgetItem([label + "）"])
        root.setToolTip(0, str(pack_path))
        root.setData(0, Qt.ItemDataRole.UserRole, ("packroot", str(pack_path)))
        for res_path in layouts:
            leaf = QTreeWidgetItem([res_path])
            leaf.setData(0, Qt.ItemDataRole.UserRole,
                         ("pack", str(pack_path), res_path))
            _style_leaf(leaf, res_path)
            root.addChild(leaf)
        for res_path in missing:
            leaf = QTreeWidgetItem([res_path])
            leaf.setData(0, Qt.ItemDataRole.UserRole,
                         ("pack", str(pack_path), res_path))
            _style_leaf(leaf, res_path, missing=True)
            root.addChild(leaf)
        self._tree.addTopLevelItem(root)
        root.setExpanded(False)
        self._roots[key] = root

    def add_loose_dir(self, dir_path: str | Path) -> None:
        """把一个散装 .dlg 目录挂到树上（只保留 .dlg 与含它的目录）。"""
        key = ("dir", str(dir_path))
        if key in self._roots:
            return
        root = QTreeWidgetItem([f"📁 {Path(dir_path).name}（散装目录）"])
        root.setToolTip(0, str(dir_path))
        root.setData(0, Qt.ItemDataRole.UserRole, ("dirroot", str(dir_path)))
        self._fill_loose(root, Path(dir_path), "")
        if root.childCount() == 0:
            return  # 目录里没有 .dlg，不挂空节点
        self._tree.addTopLevelItem(root)
        self._roots[key] = root

    def _fill_loose(self, parent: QTreeWidgetItem, folder: Path,
                    rel: str) -> int:
        """递归填充，只收 .dlg 文件与非空文件夹，返回收录数。"""
        try:
            entries = sorted(folder.iterdir(),
                             key=lambda p: (p.is_file(), p.name.lower()))
        except OSError:
            return 0
        count = 0
        for entry in entries:
            child_rel = f"{rel}/{entry.name}" if rel else entry.name
            if entry.is_dir():
                node = QTreeWidgetItem([entry.name])
                if self._fill_loose(node, entry, child_rel) > 0:
                    parent.addChild(node)
                    count += 1
            elif entry.suffix.lower() == ".dlg":
                leaf = QTreeWidgetItem([entry.name])
                leaf.setData(0, Qt.ItemDataRole.UserRole,
                             ("file", str(entry)))
                _style_leaf(leaf, child_rel)
                parent.addChild(leaf)
                count += 1
        return count

    def root_count(self) -> int:
        return self._tree.topLevelItemCount()

    def expand_pack(self, pack_path: str | Path) -> None:
        """展开指定包节点并滚动到它（刚从文件对话框选包时用）。"""
        root = self._roots.get(("pack", str(pack_path)))
        if root is not None:
            root.setExpanded(True)
            self._tree.scrollToItem(root)

    # -- 名称搜索 -----------------------------------------------------
    _saved_expansion: dict[int, bool] | None = None

    def _apply_search(self, keyword: str) -> None:
        """按名称过滤：命中布局及其祖先可见，搜索时自动展开。"""
        kw = keyword.strip().casefold()
        roots = [self._tree.topLevelItem(i)
                 for i in range(self._tree.topLevelItemCount())]
        if not kw:
            if self._saved_expansion is not None:
                saved, self._saved_expansion = self._saved_expansion, None
                for root in roots:
                    _restore_filter(root, saved)
            else:
                for root in roots:
                    _restore_filter(root, {})
            return
        if self._saved_expansion is None:
            self._saved_expansion = {}
            for root in roots:
                _record_expansion(root, self._saved_expansion)
        for root in roots:
            _filter_item(root, kw)

    # -- 交互 ---------------------------------------------------------
    def _on_double_click(self, item: QTreeWidgetItem) -> None:
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(data, tuple) or not data:
            return
        if data[0] in ("pack", "pending"):
            self.open_pack_layout.emit(data[1], data[2])
        elif data[0] == "file":
            self.open_loose_file.emit(data[1])

    def reveal_selection(self, data: tuple) -> None:
        """把树当前项同步到指定布局（打开后高亮定位用）。"""

        def visit(item: QTreeWidgetItem) -> bool:
            if item.data(0, Qt.ItemDataRole.UserRole) == data:
                self._tree.setCurrentItem(item)
                return True
            return any(visit(item.child(i)) for i in range(item.childCount()))

        for i in range(self._tree.topLevelItemCount()):
            if visit(self._tree.topLevelItem(i)):
                break


class WidgetTreePanel(QWidget):
    """布局的控件层级树，与画布/属性面板联动选择。

    每行第二列是锁定开关：灰色开锁=未锁定，橙色挂锁=已锁定，
    点击切换，与画布的锁定（工具栏/Ctrl+L/右键菜单）同一状态。
    """

    widget_selected = Signal(object)
    lock_toggled = Signal(object, bool)  # (控件, 目标锁定状态)
    add_child_requested = Signal()
    add_root_requested = Signal()
    promote_requested = Signal()
    delete_requested = Signal()
    reorder_requested = Signal(object, int)  # (控件, -1 上移/+1 下移)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        bar = QHBoxLayout()
        self._add_btn = QPushButton("加子控件")
        self._add_btn.setToolTip("把调色板里选中的控件类型加为当前控件的子控件")
        add_root_btn = QPushButton("加顶级")
        add_root_btn.setToolTip(
            "把调色板里选中的控件类型加为顶级控件（不挂在任何控件下面）")
        add_root_btn.clicked.connect(self.add_root_requested)
        promote_btn = QPushButton("设为顶级")
        promote_btn.setToolTip(
            "把当前控件提升为顶级控件（脱离父控件，位置不变）")
        promote_btn.clicked.connect(self.promote_requested)
        self._del_btn = QPushButton("删除")
        up_btn = QToolButton()
        up_btn.setText("↑")
        up_btn.setToolTip("上移（绘制更靠前）")
        down_btn = QToolButton()
        down_btn.setText("↓")
        down_btn.setToolTip("下移")
        self._add_btn.clicked.connect(self.add_child_requested)
        self._del_btn.clicked.connect(self.delete_requested)
        up_btn.clicked.connect(lambda: self._reorder(-1))
        down_btn.clicked.connect(lambda: self._reorder(1))
        for btn in (self._add_btn, add_root_btn, promote_btn,
                    self._del_btn, up_btn, down_btn):
            bar.addWidget(btn)
        layout.addLayout(bar)
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(2)
        self._tree.setColumnWidth(1, 24)
        self._tree.header().setStretchLastSection(False)
        self._tree.currentItemChanged.connect(self._on_current_changed)
        self._tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self._tree, 1)
        self._items: dict[int, QTreeWidgetItem] = {}
        self._widgets: dict[int, Widget] = {}
        self._current: Widget | None = None
        self._syncing = False

    def build(self, doc: LayoutDocument | None) -> None:
        self._tree.clear()
        self._items = {}
        self._widgets = {}
        self._current = None
        if doc is None:
            return

        def add(parent_item: QTreeWidgetItem | QTreeWidget, widget: Widget):
            label = f"{widget.name or '(未命名)'} · {widget.wtype}"
            item = QTreeWidgetItem(parent_item, [label, ""])
            item.setData(0, Qt.ItemDataRole.UserRole, id(widget))
            self._items[id(widget)] = item
            self._widgets[id(widget)] = widget
            self._apply_lock_icon(item, widget)
            for child in widget.children:
                add(item, child)
            item.setExpanded(True)

        for root in doc.roots:
            add(self._tree, root)

    def update_label(self, widget: Widget) -> None:
        item = self._items.get(id(widget))
        if item is not None:
            item.setText(0, f"{widget.name or '(未命名)'} · {widget.wtype}")

    # -- 锁定小图标（第二列，与画布锁定同一状态） ------------------
    def _apply_lock_icon(self, item: QTreeWidgetItem,
                         widget: Widget) -> None:
        from . import icons

        if widget.locked:
            item.setIcon(1, icons.icon_lock())
            item.setToolTip(1, "已锁定（点此解锁）")
        else:
            item.setIcon(1, icons.icon_lock_open())
            item.setToolTip(1, "未锁定（点此锁定）")

    def set_lock_icon(self, widget: Widget) -> None:
        """画布侧改了锁定后，把树上这一行的图标同步过来。"""
        item = self._items.get(id(widget))
        if item is not None:
            self._apply_lock_icon(item, widget)

    def refresh_locks(self) -> None:
        """全树刷新锁图标（撤销重建对象后用新对象状态对齐）。"""
        for widget_id, item in self._items.items():
            widget = self._widgets.get(widget_id)
            if widget is not None:
                self._apply_lock_icon(item, widget)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        if column != 1 or item is None:
            return
        widget = self._find(item.data(0, Qt.ItemDataRole.UserRole))
        if widget is not None:
            self.lock_toggled.emit(widget, not widget.locked)

    def select_widget(self, widget: Widget | None) -> None:
        self._current = widget
        item = self._items.get(id(widget)) if widget is not None else None
        self._syncing = True
        self._tree.setCurrentItem(item)
        self._syncing = False

    def current_widget(self) -> Widget | None:
        return self._current

    def _reorder(self, delta: int) -> None:
        if self._current is not None:
            self.reorder_requested.emit(self._current, delta)

    def _on_current_changed(self, item: QTreeWidgetItem | None) -> None:
        if self._syncing:
            return
        widget_id = item.data(0, Qt.ItemDataRole.UserRole) if item else None
        self._current = self._find(widget_id)
        self.widget_selected.emit(self._current)

    def _find(self, widget_id: int | None) -> Widget | None:
        if widget_id is None:
            return None
        return self._widgets.get(widget_id)


class PalettePanel(QWidget):
    """控件调色板：双击或点按钮把控件加到选中控件/根级。"""

    add_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("控件类型（双击添加）："))
        self._list = QListWidget()
        for wtype in WIDGET_TYPES:
            self._list.addItem(QListWidgetItem(wtype))
        self._list.itemDoubleClicked.connect(
            lambda item: self.add_requested.emit(item.text()))
        layout.addWidget(self._list, 1)
        add = QPushButton("添加选中类型")
        add.clicked.connect(self._emit_current)
        layout.addWidget(add)
        hint = QLabel("目标：控件树/画布中选中的控件为父级，"
                      "未选中则加到根级。")
        hint.setWordWrap(True)
        layout.addWidget(hint)

    def _emit_current(self) -> None:
        item = self._list.currentItem()
        if item is not None:
            self.add_requested.emit(item.text())

    def current_type(self) -> str | None:
        item = self._list.currentItem()
        return item.text() if item is not None else None


def _record_expansion(item: QTreeWidgetItem, saved: dict[int, bool]) -> None:
    saved[id(item)] = item.isExpanded()
    for i in range(item.childCount()):
        _record_expansion(item.child(i), saved)


def _restore_filter(item: QTreeWidgetItem,
                    saved: dict[int, bool]) -> None:
    item.setHidden(False)
    if id(item) in saved:
        item.setExpanded(saved[id(item)])
    for i in range(item.childCount()):
        _restore_filter(item.child(i), saved)


def _show_subtree(item: QTreeWidgetItem) -> None:
    item.setHidden(False)
    for i in range(item.childCount()):
        _show_subtree(item.child(i))


def _filter_item(item: QTreeWidgetItem, kw: str) -> bool:
    """返回该项是否应可见：自身命中则整棵子树显示。"""
    if kw in item.text(0).casefold():
        _show_subtree(item)
        return True
    any_child = False
    for i in range(item.childCount()):
        if _filter_item(item.child(i), kw):
            any_child = True
    item.setHidden(not any_child)
    if any_child:
        item.setExpanded(True)
    return any_child
