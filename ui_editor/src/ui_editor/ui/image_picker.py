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

from PySide6.QtCore import QSize, Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from ..core import dir_base
from ..core.errors import Cancelled
from .busy import BusyHostMixin, run_busy_or_plain

_ROLE_PATH = Qt.ItemDataRole.UserRole
_THUMB_BATCH = 24


def _basename(path: str) -> str:
    return path.replace("\\", "/").rstrip("/").split("/")[-1]


class ResourcePickerDialog(BusyHostMixin, QDialog):
    """包内资源选择窗：搜索过滤 + 网格缩略图 + 单选确认。"""

    def __init__(self, parent, title: str, paths: list[str],
                 current: str = "",
                 thumb_provider: Callable[[str], object] | None = None,
                 on_stage: Callable[[str, bytes], None] | None = None,
                 export_handler: Callable[[list[str], object], None] | None = None,
                 family_label: Callable[[str], str | None] | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(760, 540)
        self.external_requested = False
        self._thumb_provider = thumb_provider
        self._on_stage = on_stage
        self._export_handler = export_handler
        # 目录型基路径（拼名族）的一句话说明：回调返回 None 表示不是族。
        self._family_label = family_label
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
