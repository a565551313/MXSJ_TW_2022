"""属性面板：按值类型生成编辑器，直接读写控件属性字典。

未知字段也照常列出（int/float/bool/str/标量列表各有编辑器，
嵌套结构只读展示），不认识的字段不会在编辑中丢失。几何字段
与画布双向同步：画布拖动时本面板刷新数值，面板改值时画布
图元经主窗口回调刷新。
"""

from __future__ import annotations

from html import escape

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..core import colors
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
        # 主窗口注入资源解析器：文件字段优先从资源包里选
        self.assets = None
        # 修改前同步护栏：返回 False 则不触碰 props、不发 changed。
        self.before_change = None

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

    def refresh_label(self, widget: Widget) -> None:
        """改名后同步标题，不销毁正在提交的属性编辑器。"""
        if widget is not self._widget:
            return
        child_note = f"，子控件 {len(widget.children)} 个"
        self._header.setText(
            f"<b>{escape(widget.wtype)}</b>　"
            f"{escape(widget.name or '(未命名)')}{child_note}")

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
        # removeRow 可能触发旧编辑器失焦，必须先挡住提交。
        self._building = True
        while self._form.rowCount():
            self._form.removeRow(0)
        self._getters = {}
        widget = self._widget
        if widget is None:
            self._header.setText("未选中控件")
            self._building = False
            return
        self.refresh_label(widget)
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

    def _allowed(self, key: str, value: object) -> bool:
        if self._widget is None:
            return False
        return (self.before_change is None
                or self.before_change(self._widget, key, value))

    def _commit(self, key: str, value: object) -> bool:
        if self._building or self._widget is None:
            return False
        if self._widget.props.get(key) == value and key in self._widget.props:
            return True
        if not self._allowed(key, value):
            self._rebuild()  # 撤回编辑器中的候选文本
            return False
        self._widget.props[key] = value
        self.changed.emit(self._widget, key)
        return True

    def _remove_property(self, key: str) -> None:
        if self._building or self._widget is None or key in _CORE_KEYS:
            return
        if key not in self._widget.props or not self._allowed(key, None):
            return
        self._widget.props.pop(key)
        self.changed.emit(self._widget, key)
        self._rebuild()

    def _add_property(self) -> None:
        if self._widget is None or self._building:
            return
        key = self._new_key.text().strip()
        if not key:
            return
        if key == "lChildren":
            QMessageBox.warning(self, "不能直接修改子树",
                                "请在控件树中新增/删除子控件。")
            return
        if not self._commit(key, _guess_scalar(self._new_value.text())):
            return
        self._new_key.clear()
        self._new_value.clear()
        self._rebuild()

    # -- 各类型编辑器 -------------------------------------------------
    def _make_editor(self, key: str, value: object) -> QWidget | None:
        if colors.is_color_key(key):
            if (not isinstance(value, bool) and isinstance(value, (int, str))
                    and colors.parse_color(value) is not None):
                return self._color_editor(key, value)
            if colors.color_groups(value) is not None:
                return self._color_editor(key, value)
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

    def _build_color_dialog(self, initial: QColor,
                            title: str) -> QColorDialog:
        """颜色对话框：用 Qt 自己的实现（非系统原生）。

        Windows 原生颜色对话框没有屏幕吸管；Qt 版本自带
        「吸管 / Pick Screen Color」，可以从屏幕上任意位置吸取颜色。
        """
        dialog = QColorDialog(initial, self)
        dialog.setWindowTitle(title)
        dialog.setOption(
            QColorDialog.ColorDialogOption.ShowAlphaChannel, True)
        dialog.setOption(
            QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
        return dialog

    @staticmethod
    def _eyedropper_button(dialog: QColorDialog):
        """对话框里的吸管按钮（不同 Qt 翻译文案不同，按英文原文找）。"""
        from PySide6.QtWidgets import QPushButton

        for button in dialog.findChildren(QPushButton):
            text = button.text().replace("&", "").strip().lower()
            if "pick screen color" in text or "screen color" in text:
                return button
        return None

    def _pick_color(self, initial: QColor, title: str,
                    *, start_with_eyedropper: bool = False) -> QColor | None:
        """弹颜色对话框；start_with_eyedropper 时直接进入吸管状态。"""
        dialog = self._build_color_dialog(initial, title)
        if start_with_eyedropper:
            button = self._eyedropper_button(dialog)
            if button is not None:
                QTimer.singleShot(0, button.click)
        accepted = dialog.exec() == QDialog.DialogCode.Accepted
        chosen = dialog.currentColor()
        dialog.deleteLater()
        if not accepted or not chosen.isValid():
            return None
        return chosen

    def _color_editor(self, key: str, value: object) -> QWidget:
        """颜色属性：输入框 + 每组一个色块取色器。

        两类真实写法都支持：
        * 标量（``iColor`` 整数、``"255,0,0"``、``"#RRGGBB"``）——写回保持
          原表示形式，避免把一个 int 改成字符串后游戏读不了；
        * 列表（真实 .dlg 的主力：``lColor`` = 3/6/9 个整数，即 1~3 组
          RGB，与原生 Code2Color 一致）——一组一个色块，写回保持容器类型
          与长度；空表给一个色块，选色后补成一组 RGB。
        """
        groups = colors.color_groups(value)
        is_list = groups is not None
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        if is_list:
            edit = QLineEdit(colors.list_text(value))
            edit.setToolTip(
                "逗号分隔的整数：每组 3 个数是一色（与游戏格式一致）；"
                "右侧色块按组改色")
        else:
            edit = QLineEdit(colors.to_text(value))
            edit.setToolTip(
                "选择颜色（写回时保持原来的写法：整数/逗号串/十六进制）")
        swatch_count = 1 if not is_list else max(1, groups)
        swatches = []
        droppers = []
        for index in range(swatch_count):
            button = QToolButton()
            button.setFixedSize(30, 22)
            if is_list:
                if groups == 0:
                    button.setText("＋")
                    button.setToolTip("当前为空，点此添加一组颜色")
                else:
                    button.setToolTip(
                        f"第 {index + 1} 组颜色（R,G,B）；旁边💧可吸屏幕颜色")
            else:
                button.setToolTip(
                    "选择颜色（旁边💧可从屏幕吸取；写回保持原写法）")
            swatches.append(button)
            layout.addWidget(button)
            dropper = QToolButton()
            dropper.setText("💧")  # 吸管
            dropper.setFixedSize(24, 22)
            dropper.setToolTip(
                "吸管：直接从屏幕吸取颜色"
                + ("" if not is_list else f"（写入第 {index + 1} 组）"))
            droppers.append(dropper)
            layout.addWidget(dropper)

        def current_value():
            if self._widget is not None and key in self._widget.props:
                return self._widget.props[key]
            return value

        def paint_swatches() -> None:
            current = current_value()
            for index, button in enumerate(swatches):
                if is_list:
                    rgba = colors.group_color(current, index)
                    if rgba is not None:
                        button.setText("")
                else:
                    rgba = colors.parse_color(current)
                if rgba is None:
                    button.setStyleSheet("")
                    continue
                red, green, blue, _alpha = rgba
                button.setStyleSheet(
                    "QToolButton{border:1px solid #7a8291;border-radius:3px;"
                    f"background:rgb({red},{green},{blue});}}")

        def commit_text() -> None:
            if is_list:
                new_value = _parse_sequence(edit.text(), value)
                if not self._commit(key, new_value):
                    return
                if colors.color_groups(new_value) != groups:
                    self._rebuild()  # 组数变了，色块要重排
                    return
            else:
                new_value = colors.coerce_like(value, edit.text())
                if not self._commit(key, new_value):
                    return
            edit.setText(colors.list_text(new_value) if is_list
                         else colors.to_text(new_value))
            paint_swatches()

        def make_pick(index: int, use_eyedropper: bool = False):
            def pick() -> None:
                current = current_value()
                if is_list:
                    rgba = colors.group_color(current, index)
                else:
                    rgba = (colors.parse_color(edit.text())
                            or colors.parse_color(current))
                initial = (QColor(*rgba) if rgba is not None
                           else QColor("white"))
                title = (f"选择颜色：{key}" if not is_list
                         else f"选择颜色：{key} 第 {index + 1} 组")
                chosen = self._pick_color(
                    initial, title, start_with_eyedropper=use_eyedropper)
                if chosen is None:
                    return
                chosen_rgba = (chosen.red(), chosen.green(), chosen.blue(),
                               chosen.alpha())
                if is_list:
                    new_value = colors.set_group_color(
                        current_value(), index, chosen_rgba)
                else:
                    new_value = colors.format_like(current, chosen_rgba)
                if not self._commit(key, new_value):
                    return
                edit.setText(colors.list_text(new_value) if is_list
                             else colors.to_text(new_value))
                paint_swatches()
            return pick

        edit.editingFinished.connect(commit_text)
        for index, button in enumerate(swatches):
            button.clicked.connect(make_pick(index))
        for index, dropper in enumerate(droppers):
            dropper.clicked.connect(make_pick(index, use_eyedropper=True))
        layout.addWidget(edit, 1)
        paint_swatches()
        return row

    _IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif",
                   ".igs")
    _AUDIO_EXTS = (".wav", ".mp3", ".ogg")

    def _browse_from_pack(self, key: str, edit: QLineEdit) -> bool:
        """优先从已挂载资源包里选（返回 False 表示改走外部文件）。

        包里选的路径本来就在包内，布局保存回资源包后游戏按
        路径哈希即可找到，不丢图。没有挂载包、或用户在选择窗
        里点了"从外部文件…"时返回 False 落到旧外部流程。
        """
        assets = self.assets
        if assets is None or not assets._packs:
            return False
        from .image_picker import ResourcePickerDialog

        exts = self._AUDIO_EXTS if key == "sSoundPath" else self._IMAGE_EXTS

        # 首次要解开全部已命名布局整理清单（完整客户端很慢）：
        # 放忙碌遮罩后跑，真实进度 `done/total`，不冻结界面。
        from .busy import run_busy_or_plain

        def build_candidates(h):
            return [p for p in assets.candidates_with_staged(h.report)
                    if p.lower().endswith(exts)]

        candidates = run_busy_or_plain(
            self.window(), "整理包内资源清单（首次较慢）…", build_candidates)

        def thumb(path: str):
            frames = assets.fetch_image(path)
            return frames[0] if frames else None

        def export_handler(paths: list[str], host=None) -> None:
            from pathlib import Path

            from .busy import run_busy_or_plain
            from .image_export import export_image_files

            def one(path: str, dest_dir, dest_name=None, used_names=None):
                return export_image_files(
                    path, assets.fetch_bytes(path),
                    assets.fetch_image(path), dest_dir, dest_name,
                    protected_paths=assets.pack_paths,
                    used_names=used_names)

            written: list = []
            rejected: list = []
            try:
                if len(paths) == 1:
                    base = paths[0].replace("\\", "/").split("/")[-1]
                    chosen, _ = QFileDialog.getSaveFileName(
                        self, "导出图片", base, "所有文件 (*)")
                    if not chosen:
                        return
                    target = Path(chosen)
                    written = one(paths[0], target.parent, target.name)
                else:
                    directory = QFileDialog.getExistingDirectory(
                        self, "选择导出到的文件夹")
                    if not directory:
                        return

                    def bulk(h):
                        out: list = []
                        bad: list = []
                        used: set = set()   # 本批已占用文件名，同名加序号
                        total = len(paths)
                        for i, path in enumerate(paths, 1):
                            if h.cancelled:
                                return out, bad  # 已导出的保留，未导出的停
                            h.report(i - 1, total,
                                     f"导出 {path}（{i}/{total}）…")
                            try:
                                out.extend(one(path, directory,
                                               used_names=used))
                            except (OSError, ValueError) as exc:
                                # 单个资源被拒绝只跳过它，其余照常导出。
                                bad.append((path, str(exc)))
                        return out, bad

                    written, rejected = run_busy_or_plain(
                        host or self, "批量导出图片…", bulk,
                        maximum=len(paths), cancellable=True,
                        cancellable_text="取消（已导出的保留）")
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "导出失败", str(exc))
                return
            reject_note = (f"\n{len(rejected)} 个被拒绝，未写出：\n"
                           + "\n".join(path for path, _why in rejected[:3])
                           if rejected else "")
            if written:
                QMessageBox.information(
                    self, "导出完成",
                    f"已导出 {len(written)} 个文件，第一个在：\n"
                    f"{written[0]}{reject_note}")
            elif rejected:
                QMessageBox.warning(
                    self, "导出失败",
                    f"{len(rejected)} 个资源被拒绝写入：\n"
                    f"{rejected[0][1]}")
            else:
                QMessageBox.warning(
                    self, "导出失败", "这些资源在包里取不到内容。")

        dialog = ResourcePickerDialog(
            self, "从资源包选择（选完保存回包不丢图）",
            candidates, edit.text(),
            thumb if key != "sSoundPath" else None,
            on_stage=assets.stage_image,
            export_handler=export_handler)
        if (dialog.exec() == QDialog.DialogCode.Accepted
                and dialog.selected_path()):
            edit.setText(dialog.selected_path())
            self._commit(key, edit.text())
            return True
        return dialog.external_requested is not True

    def _with_browse(self, key: str, edit: QLineEdit) -> QWidget:
        host = QWidget()
        layout = QHBoxLayout(host)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit, 1)
        browse = QToolButton()
        browse.setText("…")
        browse.setToolTip(
            "从资源包选择（优先）；包内没有的也可改选外部文件"
            "（只取文件名，图本身不进包）")

        def _pick() -> None:
            if self._browse_from_pack(key, edit):
                return  # 已在包内选择窗处理完（选定或取消）
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
