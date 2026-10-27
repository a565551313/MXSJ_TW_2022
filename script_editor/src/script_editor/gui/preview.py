from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QVBoxLayout,
)


class BuildPreview(QDialog):
    def __init__(self, plan, parent=None):
        super().__init__(parent)
        self.setWindowTitle("原生新包构建清单 · 单模块")
        self.resize(900, 650)
        box = QVBoxLayout(self)
        binding = plan.snapshot.binding
        unsaved = "是（写包不会保存.py）" if plan.snapshot.unsaved else "否"
        summary = QLabel(
            f"来源包：{binding.archive}\nVM：{binding.vm} · 下标：{binding.index} · "
            f"身份：{binding.identity}\n"
            f"源码：{binding.source}\n来源类型：{binding.source_kind}\n编辑区未保存：{unsaved}\n"
            f"存储负载：{plan.old_stored_size} → {plan.new_stored_size} B · "
            f"实际变化：{plan.payload_changed}\n"
            + (
                "\n本次条目长度会变化：已按新长度重算 XOR 分段（扩充定长槽位，实验）；"
                "本机自校验通过，但客户端加载行为未实机验收。"
                if plan.resized
                else ""
            )
            + "\n仅替换上述一个条目，其余逐条校验。"
            "尚未验证业务语义/游戏运行，不会新增模块。"
        )
        summary.setWordWrap(True)
        box.addWidget(summary)
        pages = QTabWidget()
        for title, text in [
            (
                "来源/摘要",
                f"包SHA256：{binding.fingerprint}\n"
                f"恢复来源标准pyc SHA：{binding.recovery_sha256 or '不适用'}\n"
                f"上次入包源码SHA：{binding.built_source_sha256 or '未知'}\n"
                f"本次源码SHA：{plan.source_sha256}\n"
                f"标准pyc SHA：{plan.standard_sha256}\n"
                f"嵌入文件名（原字节HEX）：{plan.filename.hex()}",
            ),
            ("源码差异", plan.diff or "与会话内上次成功构建源码一致"),
            (
                "关联/诊断线索",
                "\n".join(f"L{h.line} [{h.kind}] {h.text}" for h in plan.hints)
                or "没有静态线索；不代表不存在动态布局/控件引用。",
            ),
        ]:
            area = QPlainTextEdit()
            area.setReadOnly(True)
            area.setPlainText(text)
            pages.addTab(area, title)
        box.addWidget(pages)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "确认，选择新包输出…"
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            plan.payload_changed
        )
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setDefault(True)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        box.addWidget(buttons)
