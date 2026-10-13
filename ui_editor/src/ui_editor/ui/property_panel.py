"""属性面板：按值类型生成编辑器，直接读写控件属性字典。

未知字段也照常列出（int/float/bool/str/标量列表各有编辑器，
嵌套结构只读展示），不认识的字段不会在编辑中丢失。几何字段
与画布双向同步：画布拖动时本面板刷新数值，面板改值时画布
图元经主窗口回调刷新。
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..core.model import Widget

_LONG_TEXT_KEYS = {"sText", "sTitles", "sTips", "sTitle"}
_FILE_KEYS = {"sFileName", "sBarFileName", "sBgFileName", "sSoundPath"}
_DISPLAY_ORDER = (
    "sName", "iX", "iY", "iWidth", "iHeight", "sFileName", "sText",
    "sTitle", "sTitles", "iStyle", "iFont", "iMsgId", "bShow", "bLoad",
)
_CORE_KEYS = {"sWidgetType", "sName", "iX", "iY", "iWidth", "iHeight",
              "lChildren"}


class _TextEdit(QPlainTextEdit):
    """补上 editingFinished 信号的多行文本框（失焦时提交）。"""

    editingFinished = Signal()  # noqa: N815

    def focusOutEvent(self, event) -> None:  # noqa: N802
        self.editingFinished.emit()
        super().focusOutEvent(event)


def _guess_scalar(text: str):
    """把属性面板输入的文本猜成合适的标量值。"""
    text = text.strip()
    if text in ("True", "False"):
        return text == "True"
    try:
        return int(text)
    except ValueError:
        pass
    try:
        return float(text)
    except ValueError:
        return text


class PropertyPanel(QWidget):
    """选中控件的属性编辑器。"""

    changed = Signal(object, str)  # (控件, 属性名)

    def __init__(self) -> None:
        super().__init__()
        self._widget: Widget | None = None
        self._building = False
        self._getters: dict[str, object] = {}

        root = QVBoxLayout(self)
        self._header = QLabel("未选中控件")
        self._header.setWordWrap(True)
        root.addWidget(self._header)

        self._form_host = QWidget()
        self._form = QFormLayout(self._form_host)
        self._form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._form_host)
        root.addWidget(scroll, 1)

        add_row = QHBoxLayout()
        self._new_key = QLineEdit()
        self._new_key.setPlaceholderText("新属性名（如 iFoo）")
        self._new_value = QLineEdit()
        self._new_value.setPlaceholderText("值")
        add_button = QPushButton("添加属性")
        add_button.clicked.connect(self._add_property)
        add_row.addWidget(self._new_key)
        add_row.addWidget(self._new_value)
        add_row.addWidget(add_button)
        root.addLayout(add_row)

    # -- 对外接口 ---------------------------------------------------
    def set_widget(self, widget: Widget | None) -> None:
        self._widget = widget
        self._rebuild()

    def refresh_values(self, widget: Widget) -> None:
        """画布拖动后同步数值（不重建面板，避免打断编辑）。"""
        if widget is not self._widget or self._building:
            return
        self._building = True
        try:
            for key in ("iX", "iY", "iWidth", "iHeight"):
                getter = self._getters.get(key)
                if getter is not None:
                    getter(widget.props.get(key, 0))
        finally:
            self._building = False

    # -- 构建 -------------------------------------------------------
    def _rebuild(self) -> None:
        while self._form.rowCount():
            self._form.removeRow(0)
        self._getters = {}
        widget = self._widget
        if widget is None:
            self._header.setText("未选中控件")
            return
        child_note = f"，子控件 {len(widget.children)} 个"
        self._header.setText(
            f"<b>{widget.wtype}</b>　{widget.name or '(未命名)'}{child_note}")
        self._building = True
        try:
            for key in self._ordered_keys(widget):
                if key == "lChildren":
                    continue
                self._add_row(key, widget.props[key])
            if widget.children:
                self._form.addRow("子控件",
                                  QLabel(f"{len(widget.children)} 个"
                                         "（在控件树中管理）"))
        finally:
            self._building = False

    @staticmethod
    def _ordered_keys(widget: Widget) -> list[str]:
        head = [k for k in _DISPLAY_ORDER if k in widget.props]
        tail = sorted(k for k in widget.props if k not in _DISPLAY_ORDER)
        return head + tail

    def _add_row(self, key: str, value: object) -> None:
        editor = self._make_editor(key, value)
        if editor is None:
            editor = QLabel(f"({type(value).__name__}，只读)")
        if key in _CORE_KEYS:
            self._form.addRow(key, editor)
            return
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor, 1)
        delete = QToolButton()
        delete.setText("✕")
        delete.setToolTip("删除此属性")
        delete.clicked.connect(lambda _=False, k=key: self._remove_property(k))
        layout.addWidget(delete)
        self._form.addRow(key, row)

    def _commit(self, key: str, value: object) -> None:
        if self._building or self._widget is None:
            return
        if self._widget.props.get(key) == value and key in self._widget.props:
            return
        self._widget.props[key] = value
        self.changed.emit(self._widget, key)

    def _remove_property(self, key: str) -> None:
        if self._widget is None:
            return
        self._widget.props.pop(key, None)
        self.changed.emit(self._widget, key)
        self._rebuild()

    def _add_property(self) -> None:
        if self._widget is None:
            return
        key = self._new_key.text().strip()
        if not key:
            return
        self._widget.props[key] = _guess_scalar(self._new_value.text())
        self._new_key.clear()
        self._new_value.clear()
        self.changed.emit(self._widget, key)
        self._rebuild()

    # -- 各类型编辑器 -------------------------------------------------
    def _make_editor(self, key: str, value: object) -> QWidget | None:
        if isinstance(value, bool):
            box = QCheckBox()
            box.setChecked(value)
            box.toggled.connect(lambda on, k=key: self._commit(k, bool(on)))
            self._getters[key] = lambda v: box.setChecked(bool(v))
            return box
        if isinstance(value, int):
            spin = QSpinBox()
            spin.setRange(-2_000_000_000, 2_000_000_000)
            spin.setValue(value)
            spin.editingFinished.connect(
                lambda k=key, s=spin: self._commit(k, s.value()))
            self._getters[key] = lambda v: spin.setValue(int(v))
            return spin
        if isinstance(value, float):
            spin = QDoubleSpinBox()
            spin.setRange(-1e9, 1e9)
            spin.setDecimals(3)
            spin.setSingleStep(0.1)
            spin.setValue(value)
            spin.editingFinished.connect(
                lambda k=key, s=spin: self._commit(k, float(s.value())))
            self._getters[key] = lambda v: spin.setValue(float(v))
            return spin
        if isinstance(value, str):
            if key in _LONG_TEXT_KEYS:
                edit = _TextEdit()
                edit.setPlainText(value)
                edit.setMaximumHeight(72)
                edit.editingFinished.connect(
                    lambda k=key, e=edit: self._commit(k, e.toPlainText()))
                self._getters[key] = lambda v: edit.setPlainText(str(v))
                return edit
            edit = QLineEdit(value)
            edit.editingFinished.connect(
                lambda k=key, e=edit: self._commit(k, e.text()))
            self._getters[key] = lambda v: edit.setText(str(v))
            if key in _FILE_KEYS:
                return self._with_browse(key, edit)
            return edit
        if isinstance(value, (list, tuple)) and all(
                isinstance(v, (int, float, str)) and not isinstance(v, bool)
                for v in value):
            edit = QLineEdit(", ".join(str(v) for v in value))
            edit.setToolTip("逗号分隔，保存时按原元素类型与容器类型还原")
            edit.editingFinished.connect(
                lambda k=key, e=edit, raw=value:
                self._commit(k, _parse_sequence(e.text(), raw)))
            return edit
        return None

    def _with_browse(self, key: str, edit: QLineEdit) -> QWidget:
        host = QWidget()
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit, 1)
        browse = QToolButton()
        browse.setText("…")
        browse.setToolTip("从散装文件选择（只取文件名，包内资源请直接填路径）")

        def _pick() -> None:
            path, _ = QFileDialog.getOpenFileName(
                self, "选择图片文件", edit.text(),
                "图片 (*.igs *.png *.jpg *.jpeg *.bmp);;所有文件 (*)")
            if path:
                from pathlib import Path
                edit.setText(Path(path).name)
                self._commit(key, edit.text())

        browse.clicked.connect(_pick)
        layout.addWidget(browse)
        return host


def _parse_sequence(text: str, original: object):
    """把逗号文本按原序列的元素类型解析回 list/tuple。"""
    tokens = [tok.strip() for tok in text.split(",") if tok.strip() != ""]
    elem_type = type(original[0]) if isinstance(original, (list, tuple)) \
        and original else str
    result = []
    for tok in tokens:
        try:
            result.append(elem_type(tok))
        except (TypeError, ValueError):
            result.append(tok)
    if isinstance(original, tuple):
        return tuple(result)
    return result
