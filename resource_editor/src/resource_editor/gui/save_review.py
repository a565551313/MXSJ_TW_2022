"""保存前只读改动清单。确认不修改源包，也不提前清历史。"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from ..core.changes import ResourceChange, counts


class SaveReviewDialog(QDialog):
    def __init__(self, changes: list[ResourceChange], target: Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存前改动清单 · 生成新包")
        self.resize(820, 460)
        layout = QVBoxLayout(self)
        summary = counts(changes)
        label = QLabel(
            f"输出：{target}\n"
            f"新增 {summary['新增']} · 修改 {summary['修改']} · "
            f"删除 {summary['删除']}\n"
            "只写新包，原包不动。表中为存储字节数（data.fls 为压缩后大小）。\n"
            "成功保存后建立新基线并清空本包撤销/重做；取消或失败保留编辑状态。"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.table = QTreeWidget()
        self.table.setHeaderLabels(["操作", "编号/文件名", "资源", "原大小", "新大小"])
        for change in changes:
            item = QTreeWidgetItem(
                [
                    change.operation,
                    change.identity,
                    change.name,
                    "—" if change.before_size is None else str(change.before_size),
                    "—" if change.after_size is None else str(change.after_size),
                ]
            )
            self.table.addTopLevelItem(item)
            for column in range(5):
                item.setToolTip(column, item.text(column))
        layout.addWidget(self.table)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("确认生成新包")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
