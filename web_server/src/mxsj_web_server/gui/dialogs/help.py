"""Read-only previews and help; never render user-provided HTML."""

from __future__ import annotations

import json

from PySide6.QtWidgets import QDialog, QPushButton, QTextEdit, QVBoxLayout

from mxsj_web_server import __version__


class DialogMixin:
    def show_text(self, title, value):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(850, 650)
        layout = QVBoxLayout(dialog)
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setPlainText(
            value
            if isinstance(value, str)
            else json.dumps(value, ensure_ascii=False, indent=2)
        )
        layout.addWidget(editor)
        close = QPushButton("关闭")
        close.clicked.connect(dialog.accept)
        layout.addWidget(close)
        dialog.exec()

    def help_dialog(self):
        self.show_text(
            f"Web 服务管理器 {__version__}",
            "本地 GUI 与浏览器后台共用管理核心。\n\n"
            "公开服务暂停返回 503；后台暂停只读，停止会使会话失效。\n"
            "最小化进入托盘；双击恢复；退出需确认并停止两项服务。\n"
            "保存草稿→生成版本→查看差异→发布，旧版本可回退。\n\n"
            "后台密码仅在本地初始化；远程访问使用 HTTPS 反向代理。\n"
            "域名和可信代理须正确配置，白名单不替代密码。\n\n"
            "原生更新包／清单与 Windows 客户端验收尚未完成。\n"
            "日志不是防篡改账本；公网部署必须增加代理限制。",
        )
