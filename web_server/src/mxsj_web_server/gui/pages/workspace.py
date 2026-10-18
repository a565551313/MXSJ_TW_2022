"""Window page assembly, separated from lifecycle and editing actions."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from mxsj_web_server.gui.pages.settings import PolicyPage


class WorkspacePages:
    def _overview(self):
        widget, layout = QWidget(), QVBoxLayout()
        widget.setLayout(layout)
        self.overview = QTextEdit()
        self.overview.setReadOnly(True)
        layout.addWidget(self.overview)
        for title, callback in [
            ("打开公开访问地址", lambda: self.open_url("public")),
            ("打开后台登录页", lambda: self.open_url("admin")),
            ("设置／重置管理员密码", self.reset_password),
            ("强制退出全部后台会话", self.revoke_sessions),
        ]:
            button = QPushButton(title)
            button.clicked.connect(callback)
            layout.addWidget(button)
        layout.addWidget(
            QLabel("两个服务均默认停止。管理后台关闭后会话失效，公开服务不受影响。")
        )
        return widget

    def _versions(self):
        widget, layout = QWidget(), QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(
            QLabel("先保存草稿，再生成不可变版本；发布与回退都是切换版本。")
        )
        self.releases = QListWidget()
        layout.addWidget(self.releases)
        for label, callback in [
            ("生成版本", self.build_release),
            ("查看内容与差异", self.inspect_release),
            ("发布／回退至选中版本", self.activate_release),
        ]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            layout.addWidget(button)
        layout.addWidget(QLabel("原生更新清单、补丁包和断点续传：尚未实现。"))
        return widget

    def _settings(self):
        widget, layout = QWidget(), QVBoxLayout()
        widget.setLayout(layout)
        layout.addWidget(
            QLabel(
                "监听设置变更需重启，名单立即生效。填写域名不等于完成 DNS／证书部署。"
            )
        )
        tabs = QTabWidget()
        self.policies = {kind: PolicyPage() for kind in ("public", "admin")}
        tabs.addTab(self.policies["public"], "公开 Web 服务")
        tabs.addTab(self.policies["admin"], "管理后台")
        layout.addWidget(tabs)
        button = QPushButton("校验并保存设置")
        button.clicked.connect(self.save_settings)
        layout.addWidget(button)
        layout.addWidget(
            QLabel(
                "白名单为空时拒绝全部来源，本地 GUI 不受限。远程后台须用 HTTPS 代理。"
            )
        )
        return widget

    def _logs(self):
        widget, layout = QWidget(), QVBoxLayout()
        widget.setLayout(layout)
        row = QHBoxLayout()
        self.log_filter = QLineEdit()
        self.log_filter.setPlaceholderText("按事件／服务／时间／IP 筛选")
        self.log_filter.textChanged.connect(self.filter_logs)
        row.addWidget(self.log_filter)
        for label, callback in [
            ("刷新", self.load_logs),
            ("导出脱敏记录", self.export_logs),
            ("打开目录", self.open_log_directory),
        ]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_lines = []
        layout.addWidget(self.log_view)
        layout.addWidget(
            QLabel("诊断日志 5 MiB × 5 备份；审计存数据库，不宣称防篡改。")
        )
        return widget
