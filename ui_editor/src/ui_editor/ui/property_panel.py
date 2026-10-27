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
    QComboBox,
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

from ..core import colors, dir_base, prop_glossary
from ..core.defaults_data import DEFAULT_PROPS
from ..core.model import Widget
from ..core.painters import align_scheme

_LONG_TEXT_KEYS = {"sText", "sTitles", "sTips", "sTitle"}
_FILE_KEYS = {"sFileName", "sBarFileName", "sBgFileName", "sSoundPath"}
_DISPLAY_ORDER = (
    "sName", "iX", "iY", "iWidth", "iHeight", "sFileName", "sText",
    "sTitle", "sTitles", "iStyle", "iFont", "iMsgId", "bShow", "bLoad",
)
_CORE_KEYS = {"sWidgetType", "sName", "iX", "iY", "iWidth", "iHeight",
              "lChildren"}

# 普查模板（47,139 个真实控件）里真实出现过的属性键全集：添加属性
# 下拉的候选来源（用户确认 2026-10-26：普查并集）。
_CENSUS_KEYS = tuple(sorted({k for d in DEFAULT_PROPS.values() for k in d}))

# iAlign 取值下拉的文案（语义见 core/painters.text_align_flags 的证据注释）
_ALIGN_OLD_LABELS = ((0, "0 右对齐"), (1, "1 居中"), (2, "2 左对齐"))
_ALIGN_NINE_LABELS = (
    (0, "0 左上"), (1, "1 中上"), (2, "2 右上"),
    (3, "3 左中"), (4, "4 居中"), (5, "5 右中"),
    (6, "6 左下"), (7, "7 中下"), (8, "8 右下"),
)
_NEW_KEY_TIP_FALLBACK = (
    "下拉里是真实存在、但当前控件还没有的属性（普查模板并集）；"
    "可直接选，也可手输任意新名字。值填在右边「值」框。")


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


def make_export_handler(assets, fallback_parent):
    """导出副本处理函数（属性面板选图窗与资源浏览器共用，0.17.0 抽出）。

    ``QMessageBox`` / ``QFileDialog`` 用模块全局名：既有测试按本模块
    命名空间打补丁，局部 import 会让补丁落空、离屏弹真模态框。
    """
    def export_handler(paths: list[str], host=None) -> None:
        from pathlib import Path

        from ..core import dir_base
        from ..core.asset_export import (
            dir_piece_name,
            export_targets,
            family_prefixes,
            source_key,
        )
        from .busy import run_busy_or_plain
        from .image_export import export_image_files

        # 一批里有多个拼名族时加族名前缀（登录按钮-0l.png）。不加的话
        # 两族都写 0l.png，后一族会被批量去重改成看不出出处的 0l-2.png。
        prefixes = family_prefixes(paths)

        def one(path: str, dest_dir, dest_name=None, used_names=None,
                unavailable=None):
            prefix = prefixes.get(source_key(path), "")
            if dir_base.is_dir_base(path):
                # 拼名族按族内每块子图导出（与画布右键导出同一套命名）。
                written: list = []
                for _name, data, source in export_targets(
                        assets, path, unavailable, prefix):
                    written.extend(export_image_files(
                        source, data, assets.fetch_image(source), dest_dir,
                        dir_piece_name(source, path, prefix),
                        protected_paths=assets.pack_paths,
                        used_names=used_names))
                return written
            return export_image_files(
                path, assets.fetch_bytes(path),
                assets.fetch_image(path), dest_dir, dest_name,
                protected_paths=assets.pack_paths,
                used_names=used_names)

        parent = host or fallback_parent
        written: list = []
        rejected: list = []
        partial: list = []      # 族里有子图读不出（其余照常导出）
        try:
            if len(paths) == 1 and not dir_base.is_dir_base(paths[0]):
                base = paths[0].replace("\\", "/").split("/")[-1]
                chosen, _ = QFileDialog.getSaveFileName(
                    parent, "导出图片", base, "所有文件 (*)")
                if not chosen:
                    return
                target = Path(chosen)
                written = one(paths[0], target.parent, target.name)
            else:
                directory = QFileDialog.getExistingDirectory(
                    parent, "选择导出到的文件夹")
                if not directory:
                    return

                def bulk(h):
                    out: list = []
                    bad: list = []
                    short: list = []
                    used: set = set()   # 本批已占用文件名，同名加序号
                    total = len(paths)
                    for i, path in enumerate(paths, 1):
                        if h.cancelled:
                            # 已导出的保留，未导出的停
                            return out, bad, short
                        h.report(i - 1, total,
                                 f"导出 {path}（{i}/{total}）…")
                        unreadable: list = []
                        try:
                            out.extend(one(path, directory,
                                           used_names=used,
                                           unavailable=unreadable))
                        except (OSError, ValueError) as exc:
                            # 单个资源被拒绝只跳过它，其余照常导出。
                            bad.append((path, str(exc)))
                        if unreadable:
                            short.append(
                                f"{path}（子图读不出："
                                + "、".join(unreadable[:3]) + "）")
                    return out, bad, short

                written, rejected, partial = run_busy_or_plain(
                    host or parent, "批量导出图片…", bulk,
                    maximum=len(paths), cancellable=True,
                    cancellable_text="取消（已导出的保留）")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(parent, "导出失败", str(exc))
            return
        reject_note = ""
        if rejected:
            reject_note += (f"\n{len(rejected)} 个被拒绝，未写出：\n"
                            + "\n".join(path for path, _why
                                        in rejected[:3]))
        if partial:
            reject_note += (f"\n{len(partial)} 个族有子图读不出"
                            "（其余已导出）：\n"
                            + "\n".join(partial[:3]))
        if written:
            QMessageBox.information(
                parent, "导出完成",
                f"已导出 {len(written)} 个文件，第一个在：\n"
                f"{written[0]}{reject_note}")
        elif rejected:
            QMessageBox.warning(
                parent, "导出失败",
                f"{len(rejected)} 个资源被拒绝写入：\n"
                f"{rejected[0][1]}")
        elif partial:
            QMessageBox.warning(
                parent, "导出失败",
                f"{len(partial)} 个族的子图读不出：\n"
                f"{partial[0]}")
        else:
            QMessageBox.warning(
                parent, "导出失败", "这些资源在包里取不到内容。")

    return export_handler


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
        self._new_key = QComboBox()
        self._new_key.setEditable(True)
        self._new_key.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self._new_key.lineEdit().setPlaceholderText(
            "新属性名（下拉可选，也可手输）")
        self._new_key.setEnabled(False)
        self._new_key.currentTextChanged.connect(self._refresh_new_key_tip)
        self._refresh_new_key_tip("")
        self._new_value = QLineEdit()
        self._new_value.setPlaceholderText("值")
        add_button = QPushButton("添加属性")
        add_button.clicked.connect(self._add_property)
        # 用户反馈（0.19.0）：下拉太窄、值框太宽——两者默认宽度对调。
        # sizeHint 互换：下拉最小宽＝值框原宽、值框最大宽＝下拉原宽；
        # 面板拉宽时的富余空间归下拉（候选键长、值通常短）。
        key_hint = self._new_key.sizeHint().width()
        val_hint = self._new_value.sizeHint().width()
        self._new_key.setMinimumWidth(val_hint)
        self._new_value.setMaximumWidth(key_hint)
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
            self._refresh_key_candidates()
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
            self._refresh_key_candidates()
        finally:
            self._building = False

    def _refresh_key_candidates(self) -> None:
        """添加属性下拉候选 = 普查存在但当前控件没有的键（可编辑保留手输）。"""
        widget = self._widget
        if widget is None:
            self._new_key.clear()
            self._new_key.setEnabled(False)
            return
        current = self._new_key.currentText().strip()
        self._new_key.clear()
        self._new_key.addItems(
            [k for k in _CENSUS_KEYS
             if k not in widget.props and k != "lChildren"])
        # addItems 会把第 0 项设为当前项（可编辑下拉随即显示首个候选、
        # 占位符永远不露面）：清掉当前项，空输入显示占位符，敲过的才恢复。
        self._new_key.setCurrentIndex(-1)
        self._new_key.setEnabled(True)
        if current:
            self._new_key.setCurrentText(current)

    def _refresh_new_key_tip(self, text: str) -> None:
        tip = prop_glossary.tooltip(text.strip())
        try:
            self._new_key.setToolTip(
                f"{tip}\n{_NEW_KEY_TIP_FALLBACK}" if tip
                else _NEW_KEY_TIP_FALLBACK)
        except RuntimeError:      # 控件正在销毁：尾随信号，忽略
            pass

    @staticmethod
    def _ordered_keys(widget: Widget) -> list[str]:
        head = [k for k in _DISPLAY_ORDER if k in widget.props]
        tail = sorted(k for k in widget.props if k not in _DISPLAY_ORDER)
        return head + tail

    @staticmethod
    def _key_label(key: str) -> QLabel:
        """属性名标签：悬停显示中文释义（有依据才给，不编造）。"""
        label = QLabel(key)
        tip = prop_glossary.tooltip(key)
        if tip:
            label.setToolTip(tip)
        return label

    def _add_row(self, key: str, value: object) -> None:
        editor = self._make_editor(key, value)
        if editor is None:
            editor = QLabel(f"({type(value).__name__}，只读)")
        if key in _CORE_KEYS:
            self._form.addRow(self._key_label(key), editor)
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
        self._form.addRow(self._key_label(key), row)

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
        key = self._new_key.currentText().strip()
        if not key:
            return
        if key == "lChildren":
            QMessageBox.warning(self, "不能直接修改子树",
                                "请在控件树中新增/删除子控件。")
            return
        if not self._commit(key, _guess_scalar(self._new_value.text())):
            return
        self._new_key.setCurrentText("")
        self._new_value.clear()
        self._rebuild()

    # -- 各类型编辑器 -------------------------------------------------
    def _align_editor(self, key: str, value: int) -> QWidget | None:
        """iAlign 的具名下拉（旧三值 / 新九宫）；原生没覆盖的类型返回 None。"""
        scheme = align_scheme(self._widget.wtype
                              if self._widget is not None else "")
        if scheme is None:
            return None
        labels = _ALIGN_OLD_LABELS if scheme == "old" else _ALIGN_NINE_LABELS
        combo = QComboBox()
        for item, text in labels:
            combo.addItem(text, item)
        if value not in [item for item, _ in labels]:
            combo.addItem(f"{value}（原生取值外）", value)
        combo.setCurrentIndex(combo.findData(value))
        combo.setToolTip(
            "文本对齐方式；改完画布立即按新对齐重画。"
            "语义与原生一致（旧文本框三值 / 新文本框与按钮九宫）。")
        # 槽只捕值表不捕控件：面板重建销毁 combo 时若信号尾随触发，
        # 再碰 combo 就是 use-after-free（沙箱实测崩过堆）。
        values = [item for item, _ in labels] + (
            [] if value in [item for item, _ in labels] else [value])
        combo.currentIndexChanged.connect(
            lambda idx, k=key, vals=values:
            self._commit(k, vals[idx]) if 0 <= idx < len(vals) else None)
        return combo

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
        if (key == "iAlign" and isinstance(value, int)
                and not isinstance(value, bool)):
            editor = self._align_editor(key, value)
            if editor is not None:
                return editor
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
        allow_families = key != "sSoundPath"

        # 首次要解开全部已命名布局整理清单（完整客户端很慢）：
        # 放忙碌遮罩后跑，真实进度 `done/total`，不冻结界面。
        from .busy import run_busy_or_plain

        def keep(path: str) -> bool:
            # 目录型基路径没有扩展名，但按钮/边框/九宫格都靠它——
            # 只按扩展名过滤会让这类素材永远选不到。
            if allow_families and dir_base.is_dir_base(path):
                return True
            return path.lower().endswith(exts)

        def build_candidates(h):
            return [p for p in assets.candidates_with_staged(h.report)
                    if keep(p)]

        candidates = run_busy_or_plain(
            self.window(), "整理包内资源清单（首次较慢）…", build_candidates)

        def thumb(path: str):
            frames = assets.fetch_image(path)
            return frames[0] if frames else None

        # 三个回调都走 ``AssetResolver`` 的按路径缓存：729 个族一次 0.4 s，
        # 以前每开一次选图窗、每敲一个字都重算，第二次打开也不快。
        def family_label(path: str) -> str | None:
            return dir_base.describe(assets.family_plan(path))

        def family_pieces(path: str) -> list[str] | None:
            """这个基路径下**实际有哪些子图**（拼不成整族也逐个探出来）。

            返回**族目录内**的相对路径（``0l.png``、``top/left.png``）：
            九片每行的 ``left/middle/right`` 同名，只留文件名会让 130 个
            九片目录在提示里长得一模一样。
            """
            pieces = assets.family_pieces(path)
            if not pieces:
                return None
            prefix = path.replace("\\", "/").rstrip("/") + "/"
            relative: list[str] = []
            for piece in pieces:
                text = piece.replace("\\", "/")
                if text.startswith(prefix):
                    relative.append(text[len(prefix):])
                else:   # 兜底：路径形态对不上时至少保留文件名
                    relative.append(text.rsplit("/", 1)[-1])
            return relative

        def family_kind(path: str) -> str | None:
            """这个基路径按哪种拼名族拼（按钮横片/序号帧…）。"""
            chosen = assets.family_plan(path)
            return chosen.kind if chosen is not None else None

        export_handler = make_export_handler(assets, self)

        widget_type = None
        if self._widget is not None:
            widget_type = self._widget.props.get("sWidgetType")
        dialog = ResourcePickerDialog(
            self, "从包里选图片（选完保存会一起写进新包）",
            candidates, edit.text(),
            thumb if key != "sSoundPath" else None,
            on_stage=assets.stage_image,
            export_handler=export_handler,
            family_label=family_label,
            widget_type=widget_type if isinstance(widget_type, str) else None,
            exists=assets.resource_exists,
            family_pieces=family_pieces,
            family_kind=family_kind)
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
            "从包里选图片（首选，保存时连图一起写进新包）；\n"
            "包里没有的只能「只填包外文件名」——那种图不会写进包，"
            "换台机器就画不出来")

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
