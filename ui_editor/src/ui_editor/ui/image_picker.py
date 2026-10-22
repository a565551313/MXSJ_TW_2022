"""从资源包选择媒体资源的对话框。

包内资源按引用路径列出（清单由 AssetResolver.media_candidates
从已命名布局扒取），支持子串搜索、缩略图懒加载（分批填充，
大包不卡死）、双击确认。选到的路径本来就在包里，布局保存
回资源包后游戏按路径哈希即可找到，不会丢图。对话框同时
保留"从外部文件…"入口，选外部图仍是旧行为（只填文件名，
图本身不进包）。
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from PySide6.QtCore import QBuffer, QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
)

from ..core import dir_base
from ..core.errors import Cancelled
from .busy import BusyHostMixin, run_busy_or_plain

_ROLE_PATH = Qt.ItemDataRole.UserRole
_THUMB_BATCH = 24

#: 新建族可选的拼名类型（顺序即下拉框顺序）
_FAMILY_KINDS = (
    ("h_state", "三态横片：0l/0c/0r，每 3 张一个态（按钮）"),
    ("nine_slice", "九片：top/left … bottom/right（9 张，边框/九宫格）"),
    ("h_slice", "横三片：left/middle/right（3 张，横向边框/进度条）"),
    ("v_slice", "竖三片：top/middle/bottom（3 张，纵向边框）"),
    ("frames", "序号帧：0/1/2…（N 张，一个序号一个态）"),
    ("single", "单图：bg（1 张）"),
)


def _basename(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").split("/")[-1]


def _stem(path: str) -> str:
    name = _basename(path)
    return name[:name.rfind(".")] if "." in name[1:] else name


def prepare_family_payloads(files: list[str]) -> tuple[dict[str, bytes], str]:
    """读取一族图片并统一扩展名：整组 ``.igs`` 原样，其余统一转 PNG。

    拼名族按"整组同扩展名"探测，混着写进包就拼不出来；普通图片统一转
    PNG 是因为游戏只认 ``.png``/``.igs``（jpg/bmp 原样写进去等于坏图）。
    真 PNG 字节原样保留，不重新编码。
    """
    paths = [Path(name) for name in files]
    igs = [path for path in paths if path.suffix.lower() == ".igs"]
    if igs and len(igs) != len(paths):
        raise ValueError(
            "不能把 .igs 和普通图片混成一族：整族要用同一种扩展名。")
    payloads: dict[str, bytes] = {}
    for path in paths:
        data = path.read_bytes()
        if path.suffix.lower() == ".igs":
            payloads[str(path)] = data
            continue
        if data[:4] == b"\x89PNG":
            payloads[str(path)] = data
            continue
        image = QImage(str(path))
        if image.isNull():
            raise ValueError(f"{path.name} 读不出图片（不是支持的图片格式）。")
        buffer = QBuffer()
        buffer.open(QBuffer.OpenModeFlag.WriteOnly)
        if not image.save(buffer, "PNG"):
            raise ValueError(f"{path.name} 转成 PNG 失败。")
        payloads[str(path)] = bytes(buffer.data())
    return payloads, (".igs" if igs else ".png")


class FamilyImportDialog(QDialog):
    """把一组图变成"一个按钮/边框"：目录型基路径 + 族内拼名。

    文件名本身能对上族内命名时（例如刚导出的 ``0l/0c/0r``、``top-left`` …）
    按**名字**对应，与选择顺序无关；对不上才按顺序分配，界面上逐条列出来
    让用户能看出错位。
    """

    def __init__(self, parent, files: list[str], base: str, kind: str | None,
                 ext: str, exists=None):
        super().__init__(parent)
        self.setWindowTitle("新建拼名族（多张图 = 一个按钮/边框）")
        self.resize(700, 480)
        self._files = list(files)
        self.ext = ext
        self._exists = exists
        self._matched = dir_base.match_kind([Path(f).name for f in self._files])
        self.base_path = ""
        self.pairs: list[tuple[str, str]] = []

        self._base = QLineEdit(base, self)
        self._base.setPlaceholderText(
            "这一族的目录路径，结尾带斜杠，如 "
            "combdialog4\\新登陆界面\\三态按钮\\登录按钮\\")
        self._base.textChanged.connect(self._refresh)

        self._kind = QComboBox(self)
        for value, label in _FAMILY_KINDS:
            self._kind.addItem(label, value)
        if kind:
            index = self._kind.findData(kind)
            if index >= 0:
                self._kind.setCurrentIndex(index)
        self._kind.currentIndexChanged.connect(self._refresh)

        self._hint = QLabel(self)
        self._hint.setWordWrap(True)
        self._preview = QPlainTextEdit(self)
        self._preview.setReadOnly(True)
        self._preview.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._note = QLabel(self)
        self._note.setWordWrap(True)

        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=self)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"选了 {len(self._files)} 张图：", self))
        layout.addWidget(self._hint)
        layout.addWidget(QLabel("族类型：", self))
        layout.addWidget(self._kind)
        layout.addWidget(QLabel("这一族的目录路径（包里没有它，运行时拼子图）：", self))
        layout.addWidget(self._base)
        layout.addWidget(QLabel("写进包的条目：", self))
        layout.addWidget(self._preview, 1)
        layout.addWidget(self._note)
        layout.addWidget(self._buttons)
        self._refresh()

    # ------------------------------------------------------------ 映射 ----
    def _family_pairs(self) -> tuple[list[tuple[str, str]], str | None]:
        """[(族内相对名, 本地文件)] 与错误说明。"""
        kind = self._kind.currentData()
        names = dir_base.piece_names(kind, len(self._files))
        if names is None:
            return [], (f"{len(self._files)} 张图对不上这种族；"
                        "换个族类型，或调整要导入的图片数量。")
        if self._matched == kind:
            by_name = {_stem(path).replace("-", "/"): path
                       for path in self._files}
            if set(by_name) == set(names):
                return [(name, by_name[name]) for name in names], None
        # names 与 files 都是 count 个（piece_names 已按张数校验）
        return list(zip(names, self._files, strict=True)), None

    def _normalised_base(self) -> tuple[str, str | None]:
        value = self._base.text().strip().replace("/", "\\")
        if not value:
            return "", "先填这一族的目录路径。"
        if not value.endswith("\\"):
            if value.lower().endswith((".png", ".igs", ".jpg", ".bmp")):
                return "", "这是文件名，不是目录：请填到目录为止并补上结尾斜杠。"
            value += "\\"
        if not dir_base.is_dir_base(value):
            return "", "目录路径要相对包内，并用结尾斜杠表示这是一个目录。"
        return value, None

    def _refresh(self) -> None:
        pairs, error = self._family_pairs()
        base, base_error = self._normalised_base()
        existing = []
        if base and self._exists is not None and not error:
            existing = [rel for rel, _path in pairs
                        if self._exists(base + rel.replace("/", "\\")
                                        + self.ext)]
        lines = [f"{rel.replace('/', chr(92))}{self.ext}   ←   {Path(path).name}"
                 for rel, path in pairs]
        self._preview.setPlainText("\n".join(lines))
        notes = []
        if self._matched is not None:
            label = dir_base.KIND_LABELS.get(self._matched, self._matched)
            notes.append(f"文件名对得上【{label}】，按名字对应（与选择顺序无关）。")
        elif error is None:
            notes.append("文件名认不出族内命名，按上图顺序分配。")
        if existing:
            notes.append(f"包里已有 {len(existing)} 个同名条目，保存回包时会替换。")
        problem = error or base_error
        if problem:
            notes.append(problem)
        self._hint.setText("\n".join(notes))
        self._note.setText(f"族目录：{base or '（未填）'}" if base else "")
        self._buttons.button(
            QDialogButtonBox.StandardButton.Ok).setEnabled(not problem)

    def accept(self) -> None:
        base, error = self._normalised_base()
        pairs, pair_error = self._family_pairs()
        if error or pair_error:
            self._refresh()
            return
        self.base_path = base
        self.pairs = pairs
        super().accept()


class ResourcePickerDialog(BusyHostMixin, QDialog):
    """包内资源选择窗：搜索过滤 + 网格缩略图 + 单选确认。"""

    def __init__(self, parent, title: str, paths: list[str],
                 current: str = "",
                 thumb_provider: Callable[[str], object] | None = None,
                 on_stage: Callable[[str, bytes], None] | None = None,
                 export_handler: Callable[[list[str], object], None] | None = None,
                 family_label: Callable[[str], str | None] | None = None,
                 widget_type: str | None = None,
                 exists: Callable[[str], bool] | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 540)
        self.external_requested = False
        self._thumb_provider = thumb_provider
        self._on_stage = on_stage
        self._export_handler = export_handler
        # 目录型基路径（拼名族）的一句话说明：回调返回 None 表示不是族。
        self._family_label = family_label
        self._widget_type = widget_type      # 新建族时按控件类型预选族类型
        self._exists = exists                # 判断包里是否已有同名条目
        self._staged_paths: set[str] = set()
        all_paths = list(paths)
        if current and current not in all_paths:
            all_paths.insert(0, current)  # 当前值不在清单也置顶可见
        self._all_paths = all_paths

        self._search = QLineEdit(self)
        self._search.setPlaceholderText("输入关键字过滤，如 底板800")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._refilter)
        self._only_families = QCheckBox("只看拼名族", self)
        self._only_families.setToolTip(
            "目录型基路径（按钮三态 0l/0c/0r、边框 left/middle/right、"
            "九宫格 top/left …）：包里没有这个条目，游戏运行时在其下拼子图。\n"
            "选中它会把这个目录路径写进属性。")
        self._only_families.toggled.connect(self._refilter)
        self._only_families.setVisible(
            any(dir_base.is_dir_base(path) for path in all_paths))
        self._count = QLabel(self)

        self._list = QListWidget(self)
        self._list.setViewMode(QListWidget.ViewMode.IconMode)
        self._list.setIconSize(QSize(72, 72))
        self._list.setGridSize(QSize(110, 118))
        self._list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._list.setMovement(QListWidget.Movement.Static)
        self._list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection)
        self._list.itemDoubleClicked.connect(lambda _i: self.accept())

        self._thumb_timer = QTimer(self)
        self._thumb_timer.setInterval(30)
        self._thumb_timer.timeout.connect(self._fill_thumbs)
        self._thumb_queue: list[QListWidgetItem] = []

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        bottom = QHBoxLayout()
        if self._export_handler is not None:
            export_btn = QPushButton("导出图片…", self)
            export_btn.setToolTip(
                "把选中图片存到电脑上（可 Ctrl/Shift 多选批量导出；"
                "精灵格式会转成能打开看的 PNG）")
            export_btn.clicked.connect(self._choose_export)
            bottom.addWidget(export_btn)
        if self._on_stage is not None:
            add_btn = QPushButton("添加新图到包…", self)
            add_btn.setToolTip(
                "从电脑选图片、给它写游戏里的名字；选完能直接用，"
                "保存回资源包时连图一起写进包")
            add_btn.clicked.connect(self._choose_add)
            bottom.addWidget(add_btn)
            family_btn = QPushButton("新建拼名族…", self)
            family_btn.setToolTip(
                "把几张图合成一个按钮/边框：选 3 张 = 三态横片 0l/0c/0r，"
                "9 张 = 九宫格，以此类推。\n"
                "图片按族内命名写进包（保存回包时一并写入），"
                "属性直接填成这一族的目录路径")
            family_btn.clicked.connect(self._choose_family)
            bottom.addWidget(family_btn)
        else:
            external_btn = QPushButton("从外部文件…", self)
            external_btn.setToolTip(
                "改走系统文件框（旧行为：只填文件名，图本身不进包）")
            external_btn.clicked.connect(self._choose_external)
            bottom.addWidget(external_btn)
        bottom.addStretch(1)
        bottom.addWidget(buttons)

        layout = QVBoxLayout(self)
        layout.addWidget(self._search)
        layout.addWidget(self._only_families)
        layout.addWidget(self._count)
        layout.addWidget(self._list, 1)
        layout.addLayout(bottom)

        self._refilter()
        if current:
            for row in range(self._list.count()):
                item = self._list.item(row)
                if item.data(_ROLE_PATH) == current:
                    self._list.setCurrentItem(item)
                    break

    # ---------------------------------------------------------- 结果 ----
    def selected_path(self) -> str | None:
        item = self._list.currentItem()
        return str(item.data(_ROLE_PATH)) if item is not None else None

    def _choose_external(self) -> None:
        self.external_requested = True
        self.reject()

    def chosen_paths(self) -> list[str]:
        """导出目标：多选中的条目（没有多选时退回当前条目）。"""
        selected = [item.data(_ROLE_PATH)
                    for item in self._list.selectedItems()]
        if selected:
            return [path for path in selected if path]
        current = self.selected_path()
        return [current] if current else []

    def _choose_export(self) -> None:
        if self._export_handler is None:
            return
        paths = self.chosen_paths()
        if paths:
            # 第二参数 = 忙碌遮罩宿主（本对话框），批量导出在遮罩后跑。
            self._export_handler(paths, self)

    def add_staged_path(self, res_path: str) -> None:
        """把一张刚加进来的新图并入列表并选中它。"""
        self._staged_paths.add(res_path)
        if res_path not in self._all_paths:
            self._all_paths.insert(0, res_path)
        self._search.setText("")
        self._refilter()
        for row in range(self._list.count()):
            item = self._list.item(row)
            if item.data(_ROLE_PATH) == res_path:
                self._list.setCurrentItem(item)
                break

    def _suggested_path(self, filename: str) -> str:
        """新名字的建议值：沿用当前选中项的目录 + 新文件名。"""
        current = self.selected_path()
        if current:
            sep = "\\" if "\\" in current else "/"
            parts = current.replace("\\", "/").split("/")
            if len(parts) > 1:
                return sep.join(parts[:-1]) + sep + filename
        return filename

    def _ask_new_image(self, default_path: str, multi: bool,
                       can_convert: bool) -> tuple[str, bool] | None:
        """问新图的名字与是否转精灵，返回 (资源路径, 转精灵)。"""
        dialog = QDialog(self)
        dialog.setWindowTitle("这张图在游戏里的名字")
        path_edit = QLineEdit(default_path, dialog)
        convert_box = QCheckBox(
            "转成游戏精灵格式（多张图 = 多帧动画，按文件名顺序成帧）",
            dialog)
        convert_box.setChecked(multi)
        convert_box.setEnabled(can_convert)
        note = QLabel(
            "游戏靠这个名字找图，如 combdialog4\\新登陆界面\\我的图.png。\n"
            "不转精灵则按原文件存（适合本来就是真 PNG 的图）。", dialog)
        note.setWordWrap(True)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("资源路径：", dialog))
        layout.addWidget(path_edit)
        layout.addWidget(convert_box)
        layout.addWidget(note)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        res_path = path_edit.text().strip()
        if not res_path:
            return None
        return res_path, convert_box.isChecked()

    def _stage_one(self, res_path: str, data: bytes) -> None:
        """登记一张新图（包里已有同名时先确认会在保存时替换）。"""
        if self._on_stage is None:
            return
        if (res_path in self._all_paths
                and res_path not in self._staged_paths):
            answer = QMessageBox.question(
                self, "这个名字已在包里",
                f"{res_path} 包里已经有了。\n"
                "继续的话，保存回资源包时会用新图替换它，确定吗？")
            if answer != QMessageBox.StandardButton.Yes:
                return
        try:
            self._on_stage(res_path, data)
        except ValueError as exc:
            # 0.11.0 起资源层直接拒绝绝对路径/`..`/GBK 不可编码等名字；
            # 必须在这里说出来，否则用户只看到「点确定没反应」。
            QMessageBox.warning(
                self, "这个名字不能用",
                f"{res_path}\n\n{exc}\n\n"
                "请换一个只用中文、英文、数字、下划线的包内相对路径。")
            return
        self.add_staged_path(res_path)

    def _suggested_family_path(self) -> str:
        """族目录的建议值：已选中族就沿用，否则用当前条目所在目录。"""
        current = self.selected_path()
        if not current:
            return ""
        if dir_base.is_dir_base(current):
            return current.replace("/", "\\")
        parts = current.replace("\\", "/").split("/")[:-1]
        return "\\".join(parts) + "\\" if parts else ""

    def _choose_family(self) -> None:
        """新建拼名族：几张图 → 一个按钮/边框（目录型基路径）。"""
        if self._on_stage is None:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择这一族的图片（3 张 = 一个按钮，9 张 = 九宫格）", "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.gif *.igs);;"
            "所有文件 (*)")
        if not files:
            return
        try:
            payloads, ext = prepare_family_payloads(files)
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "读图失败", str(exc))
            return
        kind = dir_base.match_kind([Path(f).name for f in files])
        if kind is None:
            kind = dir_base.guess_kind(len(files), self._widget_type)
        dialog = FamilyImportDialog(
            self, files, self._suggested_family_path(), kind, ext, self._exists)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        self._stage_family(dialog.base_path, dialog.pairs, payloads, dialog.ext)

    def _stage_family(self, base: str, pairs: list[tuple[str, str]],
                      payloads: dict[str, bytes], ext: str) -> None:
        """把一族子图逐张挂账，并把这个目录路径选中（确定后写进属性）。"""
        if self._on_stage is None:
            return
        staged, failed = [], []
        for rel, path in pairs:
            res_path = base + rel.replace("/", "\\") + ext
            try:
                self._on_stage(res_path, payloads[path])
            except ValueError as exc:
                failed.append(f"{res_path}：{exc}")
                continue
            staged.append(res_path)
        if failed:
            QMessageBox.warning(
                self, "有些图没能挂账",
                "下面这些没写进待入包清单：\n\n" + "\n".join(failed[:5]))
        if not staged:
            return
        self.add_staged_path(base)
        self._count.setText(
            f"已挂账 {len(staged)} 张子图，组成族：{base}（保存回包时写入）")

    def _choose_add(self) -> None:
        """添加新图：选文件 → 问名字/是否转精灵 → 挂账待写入。

        选多张图 = 一个多帧精灵（一份资源）；选一张则可选转成
        单帧精灵或按原文件存。
        """
        if self._on_stage is None:
            return
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择要加进包的图片（多选 = 多帧精灵）", "",
            "图片 (*.png *.jpg *.jpeg *.bmp *.tga *.gif);;"
            "所有文件 (*)")
        if not files:
            return
        image_exts = (".png", ".jpg", ".jpeg", ".bmp", ".tga", ".gif")
        can_convert = all(
            Path(f).suffix.lower() in image_exts for f in files)
        multi = len(files) > 1
        result = self._ask_new_image(
            self._suggested_path(Path(files[0]).name), multi, can_convert)
        if result is None:
            return
        res_path, convert = result
        if convert:
            from ..core import sprite_encode

            def work(h):
                return sprite_encode.sprite_bytes_from_files(
                    files, progress=h.report, cancelled=lambda: h.cancelled)

            try:
                data, count = run_busy_or_plain(
                    self, "多帧精灵转换…", work,
                    cancellable=True, cancellable_text="取消转换")
            except Cancelled:
                self._count.setText("已取消转换，未挂账任何文件。")
                return
            except Exception as exc:
                QMessageBox.warning(self, "转精灵失败", str(exc))
                return
            self._stage_one(res_path, data)
            self._count.setText(
                f"已把 {count} 帧转成精灵挂账：{res_path}"
                "（保存回资源包时写入）")
            return
        if multi:
            QMessageBox.information(
                self, "多张图需要转精灵",
                "一次选多张图时请勾选「转成游戏精灵格式」合成一个"
                "动画资源；不想转的话请一次只选一张。")
            return
        try:
            data = Path(files[0]).read_bytes()
        except OSError as exc:
            QMessageBox.warning(self, "读取失败", str(exc))
            return
        self._stage_one(res_path, data)

    def _family_note(self, path: str) -> str | None:
        """路径是拼名族时返回一句话说明，否则 None。"""
        if not dir_base.is_dir_base(path) or self._family_label is None:
            return None
        try:
            return self._family_label(path)
        except Exception:
            return None

    def _refilter(self) -> None:
        query = self._search.text().strip().lower()
        only_families = self._only_families.isChecked()
        visible = [p for p in self._all_paths
                   if (not query or query in p.lower())
                   and (not only_families or dir_base.is_dir_base(p))]
        self._thumb_timer.stop()
        self._list.clear()
        blank = QIcon(QPixmap(72, 72))
        families = 0
        for path in visible:
            text = _basename(path)
            note = self._family_note(path)
            if note:
                families += 1
                text += f"（{note}）"
            if path in self._staged_paths:
                text += "（新）"
            item = QListWidgetItem(text, self._list)
            item.setData(_ROLE_PATH, path)
            if dir_base.is_dir_base(path):
                item.setToolTip(
                    f"{path}\n拼名族：包里没有这个目录条目，游戏运行时在其下"
                    "拼子图；选它=把这个目录路径写进属性，导出时按族展开。")
            else:
                item.setToolTip(path)
            item.setIcon(blank)
        note = f"，含 {families} 个拼名族" if families else ""
        self._count.setText(
            f"共 {len(visible)} 个资源{note}（包内已有，选完保存回包不丢图）")
        self._thumb_queue = [self._list.item(r)
                             for r in range(self._list.count())]
        if self._thumb_provider is not None and self._thumb_queue:
            self._thumb_timer.start()

    def _fill_thumbs(self) -> None:
        """分批给当前列表补缩略图（精灵解码不便宜，避免一次卡死）。"""
        batch, self._thumb_queue = (self._thumb_queue[:_THUMB_BATCH],
                                    self._thumb_queue[_THUMB_BATCH:])
        for item in batch:
            path = str(item.data(_ROLE_PATH))
            try:
                image = self._thumb_provider(path)  # type: ignore[misc]
            except Exception:
                image = None
            if image is not None:
                pixmap = QPixmap.fromImage(image)  # type: ignore[arg-type]
                if not pixmap.isNull():
                    item.setIcon(QIcon(pixmap.scaled(
                        72, 72, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation)))
        if not self._thumb_queue:
            self._thumb_timer.stop()
