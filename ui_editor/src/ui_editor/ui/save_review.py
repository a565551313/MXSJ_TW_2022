"""布局保存前改动、图片写入/跳过与静态风险清单。"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from ..core.diagnostics import Diagnostic
from ..core.review import LayoutChange, path_label


class SaveReviewDialog(QDialog):
    def __init__(
        self,
        target: str,
        changes: list[LayoutChange],
        issues: list[Diagnostic],
        images: list[tuple[str, str, int]],
        *,
        to_pack: bool,
        parent=None,
        layout_notice: str = "",
    ):
        super().__init__(parent)
        self.setWindowTitle("保存前改动清单")
        self.resize(920, 540)
        layout = QVBoxLayout(self)
        operation = "生成新资源包（原包不动）" if to_pack else "写入散装 .dlg"
        summary = QLabel(
            f"{operation}\n输出：{target}\n布局改动 {len(changes)} 项 · "
            f"图片清单 {len(images)} 项。\n"
            "布局按树位置比较，重排/移动会表现为字段与增删差异；未知字段也列出。\n"
            "散装布局不会嵌入图片；静态未发现引用不等于无引用。取消不改变编辑状态。"
        )
        if to_pack:
            summary.setText(
                summary.text()
                + "\n目标条目会按编辑器版式重写（即使没改任何属性，序列化"
                  "也会归一化字段顺序与写法）；除目标条目、本次写入的图片与"
                  "明确迁移的旧存储外，其它条目逐字节保持原样。"
                  "旧明文/错误密钥会在本次保存时迁移为原生路径密钥。")
        if layout_notice:
            summary.setText(summary.text() + "\n" + layout_notice)
        summary.setWordWrap(True)
        layout.addWidget(summary)
        tabs = QTabWidget()
        self.changes_table = QTreeWidget()
        self.changes_table.setHeaderLabels(
            ["操作", "位置/控件", "字段", "原值", "新值"]
        )
        for change in changes:
            row = QTreeWidgetItem(
                [
                    change.operation,
                    f"{path_label(change.path)} · {change.name}",
                    change.field,
                    change.before,
                    change.after,
                ]
            )
            for column in range(5):
                row.setToolTip(column, row.text(column))
            self.changes_table.addTopLevelItem(row)
        tabs.addTab(self.changes_table, "布局改动")
        self.images_table = QTreeWidget()
        self.images_table.setHeaderLabels(["操作", "资源路径", "存储字节数"])
        for kind, name, size in images:
            row = QTreeWidgetItem([kind, name, str(size)])
            row.setToolTip(1, name)
            self.images_table.addTopLevelItem(row)
        tabs.addTab(self.images_table, "图片写入/跳过")
        self.issues_table = QTreeWidget()
        self.issues_table.setHeaderLabels(["级别", "规则", "说明"])
        for issue in issues:
            message = (
                f"{path_label(issue.path)} · {issue.field}："
                if issue.path is not None
                else ""
            ) + issue.message
            row = QTreeWidgetItem([issue.severity, issue.code, message])
            row.setToolTip(2, message)
            self.issues_table.addTopLevelItem(row)
        tabs.addTab(self.issues_table, "诊断（全部，不采用面板隐藏项）")
        layout.addWidget(tabs)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        save = buttons.button(QDialogButtonBox.StandardButton.Save)
        save.setText("确认生成新包" if to_pack else "确认保存布局")
        if any(issue.code == "ENCODING" for issue in issues):
            save.setEnabled(False)
            summary.setText(
                summary.text() + "\n编码错误：请先修正，避免非原生编码回退。"
            )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
