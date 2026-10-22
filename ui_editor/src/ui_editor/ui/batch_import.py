"""批量导入本地布局到资源包：选多个文件 / 整个文件夹，逐行核对包内路径。

设计约束（0.15.0）：

* 只在**对话框里**决定「哪个文件写到包内哪个路径」，不在这里读包、
  不在这里写包——真正的写入仍然走保存链（原包只读，保存生成新包）。
* 包内路径保留文件夹里的相对结构：选 ``ui/login/regform.dlg`` 时默认
  写 ``login/regform.dlg``，认不出相对关系时才退回文件名。
* 同名冲突当场标出来（表里两行同一路径 / 与包内已有布局同名），
  不允许带着错误点确定。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ..core.layout_import import validate_layout_path

__all__ = ["BatchImportDialog", "ImportRow", "derive_pack_path"]


def derive_pack_path(local: str | Path, base_dir: str | Path | None = None) -> str:
    """本地文件 → 包内默认路径。

    给了 ``base_dir``（选文件夹时）就用相对路径，保留子目录；否则只用
    文件名。分隔符统一成 ``/``，与包内路径写法一致。
    """
    path = Path(local)
    if base_dir is not None:
        try:
            relative = path.relative_to(Path(base_dir))
        except ValueError:
            relative = Path(path.name)
    else:
        relative = Path(path.name)
    return "/".join(part for part in relative.parts if part not in ("", "."))


@dataclass
class ImportRow:
    """表格里的一行：本地文件 + 包内路径 + 当前判定。"""

    local: Path
    path: str
    status: str = "新增"

    def text(self) -> str:
        return f"{self.local.name} → {self.path}（{self.status}）"


class BatchImportDialog(QDialog):
    """多个本地 .dlg 一次导进某个资源包。"""

    COLUMNS = ("本地文件", "包内路径", "状态")

    def __init__(self, pack_path: str, known_paths: list[str], parent=None,
                 *, start_dir: str = "") -> None:
        super().__init__(parent)
        self._pack_path = str(pack_path)
        self._known = {path.casefold(): path for path in known_paths}
        self._start_dir = start_dir
        self.rows: list[ImportRow] = []
        self.setWindowTitle("把本地布局放进这个包（可多选）")
        self.resize(860, 460)
        layout = QVBoxLayout(self)
        head = QLabel(
            f"目标资源包：{Path(pack_path).name}\n"
            "选文件可多选，选文件夹会连子目录一起收（默认按相对路径写进包）。\n"
            "这里只排队，不动源包；保存时一次全部写进新包。"
        )
        head.setTextFormat(Qt.TextFormat.PlainText)
        head.setWordWrap(True)
        layout.addWidget(head)

        buttons = QHBoxLayout()
        self.add_files_btn = QPushButton("添加文件…（可多选）", self)
        self.add_files_btn.clicked.connect(self.add_files_dialog)
        self.add_dir_btn = QPushButton("添加文件夹…（含子目录）", self)
        self.add_dir_btn.clicked.connect(self.add_dir_dialog)
        self.remove_btn = QPushButton("移除选中", self)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.clear_btn = QPushButton("清空", self)
        self.clear_btn.clicked.connect(self.clear_rows)
        for button in (self.add_files_btn, self.add_dir_btn,
                       self.remove_btn, self.clear_btn):
            buttons.addWidget(button)
        buttons.addStretch(1)
        layout.addLayout(buttons)

        prefix_row = QHBoxLayout()
        prefix_row.addWidget(QLabel("统一前缀：", self))
        self.prefix_edit = QLineEdit(self)
        self.prefix_edit.setPlaceholderText("例如 gameui/（可留空）")
        prefix_row.addWidget(self.prefix_edit, 1)
        self.apply_prefix_btn = QPushButton("加到所有行", self)
        self.apply_prefix_btn.clicked.connect(self.apply_prefix)
        prefix_row.addWidget(self.apply_prefix_btn)
        layout.addLayout(prefix_row)

        self.table = QTableWidget(0, len(self.COLUMNS), self)
        self.table.setHorizontalHeaderLabels(list(self.COLUMNS))
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table, 1)

        self.summary = QLabel("还没有添加文件。", self)
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel, parent=self)
        self.ok_button = self.buttons.button(
            QDialogButtonBox.StandardButton.Ok)
        self.buttons.button(
            QDialogButtonBox.StandardButton.Cancel).setText("取消")
        self.ok_button.setText("导入 0 个布局")
        self.ok_button.setEnabled(False)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    # -- 添加/移除 ---------------------------------------------------
    def add_files_dialog(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择本地布局文件（可多选）", self._start_dir,
            "布局文件 (*.dlg);;所有文件 (*)")
        if files:
            self._start_dir = str(Path(files[0]).parent)
            self.add_local_files(files)

    def add_dir_dialog(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "选择装着 .dlg 的文件夹", self._start_dir)
        if folder:
            self._start_dir = folder
            self.add_local_dir(folder)

    def add_local_files(self, files: list[str],
                        base_dir: str | Path | None = None) -> int:
        """加一批文件，返回真正新增的行数（重复文件不重复排队）。"""
        existing = {str(row.local.resolve()).casefold() for row in self.rows}
        added = 0
        for name in files:
            path = Path(name)
            key = str(path.resolve()).casefold()
            if key in existing:
                continue
            existing.add(key)
            self.rows.append(ImportRow(path, derive_pack_path(path, base_dir)))
            added += 1
        self._refresh()
        return added

    def add_local_dir(self, folder: str | Path) -> int:
        """递归收文件夹里的 .dlg（按名字排序，保证表格顺序稳定）。"""
        root = Path(folder)
        files = sorted((path for path in root.rglob("*.dlg") if path.is_file()),
                       key=lambda p: str(p).casefold())
        return self.add_local_files([str(path) for path in files],
                                    base_dir=root)

    def remove_selected(self) -> None:
        indexes = sorted({index.row() for index in
                          self.table.selectedIndexes()}, reverse=True)
        for row in indexes:
            if 0 <= row < len(self.rows):
                self.rows.pop(row)
        self._refresh()

    def clear_rows(self) -> None:
        self.rows = []
        self._refresh()

    # -- 前缀 ---------------------------------------------------------
    def apply_prefix(self) -> None:
        prefix = self.prefix_edit.text().strip().replace("\\", "/")
        prefix = prefix.strip("/")
        if not prefix:
            return
        for row in self.rows:
            row.path = f"{prefix}/{row.path}"
        self._refresh()

    # -- 表格同步 -----------------------------------------------------
    def _refresh(self) -> None:
        # 包内路径先规范化（去首尾空格、反斜杠转 /）：表格里看到什么，
        # 写包时用的就是什么。不规范化的话，状态判定用的是规范路径，
        # 写后校验却拿原始字符串算哈希，会误报「条目集合不符」。
        for row in self.rows:
            try:
                row.path = validate_layout_path(row.path)
            except (ValueError, UnicodeEncodeError):
                pass                      # 留给状态列去报「无效路径」
        self.table.blockSignals(True)
        self.table.setRowCount(len(self.rows))
        self._statuses = self.compute_statuses()
        for index, row in enumerate(self.rows):
            cell_local = QTableWidgetItem(str(row.local))
            cell_local.setToolTip(str(row.local))
            cell_local.setFlags(cell_local.flags()
                                & ~Qt.ItemFlag.ItemIsEditable)
            cell_path = QTableWidgetItem(row.path)
            cell_path.setToolTip(row.path)
            status = self._statuses[index]
            cell_status = QTableWidgetItem(status)
            cell_status.setFlags(cell_status.flags()
                                 & ~Qt.ItemFlag.ItemIsEditable)
            if status in ("重复", "无效路径"):
                # 有错的行必须一眼看见：红字 + 提示怎么改
                cell_status.setForeground(QColor("#c0392b"))
                cell_status.setToolTip(
                    "包内路径无效或与别的行重复，改好才能导入")
            elif status == "替换":
                cell_status.setForeground(QColor("#b9770e"))
                cell_status.setToolTip("包里已经有同名布局，保存时会替换掉它")
            self.table.setItem(index, 0, cell_local)
            self.table.setItem(index, 1, cell_path)
            self.table.setItem(index, 2, cell_status)
        self.table.blockSignals(False)
        valid = sum(1 for status in self._statuses
                    if status in ("新增", "替换"))
        self.ok_button.setText(f"导入 {valid} 个布局")
        self.ok_button.setEnabled(valid > 0)
        self.summary.setText(self._summary_text(valid))

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        if item.column() != 1 or not (0 <= item.row() < len(self.rows)):
            return
        self.rows[item.row()].path = item.text()
        self._refresh()

    def compute_statuses(self) -> list[str]:
        """每行判定：新增 / 替换 / 重复 / 无效（与包内已有布局比较）。"""
        seen: dict[str, int] = {}
        statuses: list[str] = []
        for row in self.rows:
            try:
                path = validate_layout_path(row.path)
            except (ValueError, UnicodeEncodeError):
                statuses.append("无效路径")
                continue
            key = path.casefold()
            if key in seen:
                statuses.append("重复")
                continue
            seen[key] = len(statuses)
            statuses.append("替换" if key in self._known else "新增")
        return statuses

    def _summary_text(self, valid: int) -> str:
        bad = [(index, status) for index, status in
               enumerate(getattr(self, "_statuses", []))
               if status not in ("新增", "替换")]
        parts = [f"共 {len(self.rows)} 行，可导入 {valid} 个。"]
        if bad:
            sample = "；".join(
                f"第 {index + 1} 行{status}" for index, status in bad[:6])
            if len(bad) > 6:
                sample += f"；……共 {len(bad)} 行"
            parts.append("需要先改好：" + sample)
        parts.append("保存时写进新包，原包一个字节不动。")
        return "".join(parts)

    # -- 结果 ---------------------------------------------------------
    def entries(self) -> list[tuple[Path, str]]:
        """校验通过后的 (本地文件, 包内路径) 列表；路径已规范化。"""
        return [(self.rows[index].local,
                 validate_layout_path(self.rows[index].path))
                for index, status in enumerate(self._statuses)
                if status in ("新增", "替换")]

    def accept(self) -> None:  # noqa: D102 - Qt 覆盖
        self._statuses = self.compute_statuses()
        bad = [index for index, status in enumerate(self._statuses)
               if status not in ("新增", "替换")]
        if bad:
            QMessageBox.warning(
                self, "还有没改好的行",
                "这些行的包内路径要改好才能导入：\n"
                + "\n".join(f"第 {index + 1} 行：{self._statuses[index]}"
                            for index in bad[:12])
                + ("\n……" if len(bad) > 12 else ""))
            return
        if not self.rows:
            return
        self._statuses = self.compute_statuses()
        super().accept()
