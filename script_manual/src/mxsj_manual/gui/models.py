from __future__ import annotations

from PySide6.QtCore import QAbstractTableModel, Qt

from ..core.render import review_label


class ModuleModel(QAbstractTableModel):
    HEADERS = ["包内路径", "负责人", "审核状态"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []

    def replace(self, rows):
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.rows)

    def columnCount(self, parent=None):
        return 0 if parent is not None and parent.isValid() else len(self.HEADERS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self.rows):
            return None
        row = self.rows[index.row()]
        if role == Qt.ItemDataRole.ToolTipRole:
            return f"{row['id']}\n{row['path_status']} · {row['vm']}"
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        return [
            row["path"] or f"路径不可读 · #{row['entry_index']}",
            row["owner"],
            review_label(row),
        ][index.column()]

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.HEADERS[section]
        return None
