from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.compiler.profiles import PROFILES
from ..core.services.files import SourceRevision
from .code_editor import CodeEditor


class SourceTab(QWidget):
    candidate_requested = Signal(object)

    def __init__(
        self,
        path: Path,
        text: str,
        vm="py25",
        reference=False,
        source_kind=None,
        source_revision=None,
    ):
        super().__init__()
        self.path, self.reference, self.opened_text = path, reference, text
        self.source_revision = source_revision or SourceRevision.capture(path)
        self.source_kind = source_kind or ("reference" if reference else "authored")
        self.recovery = None
        self.draft_saved = path.is_file()
        self.editor = CodeEditor()
        self.editor.setPlainText(text)
        self.editor.setReadOnly(reference)
        self.editor.document().setModified(False)
        self.vm = QComboBox()
        for key, profile in PROFILES.items():
            self.vm.addItem(profile.label, key)
        self.vm.setCurrentIndex(self.vm.findData(vm))
        self.vm.setEnabled(not reference)
        self.vm.setToolTip("显式选择编译VM；不会自动转换源码或字节码")
        path_label = self.path_label = QLabel(str(path))
        path_label.setToolTip(str(path))
        path_label.setWordWrap(True)
        path_label.setTextFormat(Qt.TextFormat.PlainText)
        mode = self.mode_label = QLabel()
        self.update_mode()
        mode.setObjectName("sourceMode")
        header = QHBoxLayout()
        header.addWidget(mode)
        header.addStretch()
        header.addWidget(self.vm)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 2)
        layout.addLayout(header)
        if "# uncompyle6 version 3.9.3" in text[:1024]:
            warning = self.legacy_warning = QLabel(
                "旧恢复引擎可能把集合常量值写成下标。请保留修改，重新从包恢复后对比合并并核验；不自动覆盖此稿。"
            )
            warning.setWordWrap(True)
            warning.setTextFormat(Qt.TextFormat.PlainText)
            layout.addWidget(warning)
        layout.addWidget(path_label)
        self.target_label = QLabel()
        self.target_label.setTextFormat(Qt.TextFormat.PlainText)
        self.target_label.setWordWrap(True)
        self.target_label.hide()
        layout.addWidget(self.target_label)
        layout.addWidget(self.editor, 1)

    #: Verification states a fresh recovery draft can be in. "verified" means
    #: the module compiled and round-tripped byte for byte; it does not mean the
    #: decompiled logic is correct.
    BINDING_TEXT = {
        "verifying": "恢复稿 · 正在自动校验…",
        "verified": "可写包 · 已自动校验并绑定",
        "no-compiler": "恢复稿 · 未校验（先点工具栏「检查编译器」）",
        "unverified": "恢复稿 · 未校验",
        "failed": "恢复稿 · 自动校验未通过",
        "unbound": "恢复稿 · 已被同条目其它草稿取代绑定",
    }

    def set_binding_state(self, state, detail=""):
        self.binding_state = state
        self.binding_detail = detail
        self.update_mode()

    def update_mode(self):
        names = {
            "authored": "本机源码 · UTF-8",
            "reference": "只读参考 · 禁止编译",
            "recovered-draft": "恢复稿 · 可编辑",
            "recovered-reviewed": "可写包 · 已自动校验并绑定",
            "module-unavailable": "包内条目 · 尚不能恢复源码，详见模块信息",
        }
        state = getattr(self, "binding_state", "")
        text = self.BINDING_TEXT.get(state) if state else None
        if self.source_kind == "recovered-draft" and text is None:
            text = "恢复稿 · 可编辑（自动校验中…）"
        self.mode_label.setText(text or names[self.source_kind])
        detail = getattr(self, "binding_detail", "")
        if detail:
            self.mode_label.setToolTip(detail)
        color = {
            "verified": "#1e7d32",
            "failed": "#b3261e",
            "no-compiler": "#b35900",
        }.get(state, "")
        self.mode_label.setStyleSheet(f"color:{color};" if color else "")

    def attach_report(self, report):
        import json

        self.update_recovery_target(report)
        self.vm.setEnabled(False)
        self.path_label.setText(
            "恢复来源（原包）："
            f"{report.archive.name} · #{report.index} · {report.identity}\n"
            + repr(bytes.fromhex(report.filename_hex))
        )
        if report.corpus_manifest_sha256:
            status = (
                "与语料pyc全字节相等"
                if report.origin_verified
                else "未核验/不匹配，须先接通严格来源；不能直接采用"
            )
            self.path_label.setText(
                self.path_label.text() + "\n载入时原包严格来源：" + status
            )
        body = QTabWidget()
        self.layout().removeWidget(self.editor)
        body.addTab(self.editor, "恢复草稿" if report.source else "读取结果")
        for title, text in (
            (
                "反汇编",
                report.disassembly
                or "未生成标准字节码反汇编；请看模块信息中的具体原因。",
            ),
            ("模块信息", json.dumps(report.metadata(), ensure_ascii=False, indent=2)),
        ):
            pane = QPlainTextEdit()
            pane.setReadOnly(True)
            pane.setPlainText(text)
            body.addTab(pane, title)
        for index, candidate in enumerate(report.candidates):
            page = QWidget()
            layout = QVBoxLayout(page)
            label = QLabel(
                f"{candidate.engine} · {candidate.status} · 未核验语法/业务语义。"
                "另开候选不会覆盖当前编辑。"
            )
            label.setWordWrap(True)
            label.setTextFormat(Qt.TextFormat.PlainText)
            layout.addWidget(label)
            button = QPushButton("另开此候选为可编辑草稿（保留当前修改）")
            button.setObjectName("openCandidate_" + candidate.engine)
            button.setEnabled(bool(candidate.source))
            button.clicked.connect(
                lambda checked=False, i=index: self.candidate_requested.emit(
                    report.for_candidate(i)
                )
            )
            layout.addWidget(button)
            details = QTabWidget()
            for title, content in (
                ("候选源码", candidate.source),
                ("引擎输出", candidate.stdout.decode("utf-8", "backslashreplace")),
                (
                    "诊断",
                    "\n".join(candidate.diagnostics)
                    + "\n"
                    + candidate.stderr.decode("utf-8", "backslashreplace")
                    + "\n过程stdout：\n"
                    + candidate.trace_stdout.decode("utf-8", "backslashreplace"),
                ),
            ):
                pane = QPlainTextEdit()
                pane.setReadOnly(True)
                pane.setPlainText(content)
                details.addTab(pane, title)
            layout.addWidget(details)
            body.addTab(page, candidate.engine + " 候选")
        self.layout().addWidget(body, 1)
        self.module_pages = body

    def update_recovery_target(self, report):
        self.recovery = report
        self.target_label.setText(f"继续采用目标：{report.current_archive}")
        self.target_label.setVisible(report.target_archive is not None)
        self.path_label.setToolTip(
            f"源码：{self.path}\n恢复原包：{report.archive}\n"
            f"继续采用目标：{report.current_archive}"
        )
