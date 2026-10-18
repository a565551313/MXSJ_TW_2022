"""Local PySide6 management window; local control is never subject to IP ACLs."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QEvent, QThreadPool, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from mxsj_web_server import __version__
from mxsj_web_server.core.configuration.settings import validate
from mxsj_web_server.core.content import render
from mxsj_web_server.core.publishing.versions import preview
from mxsj_web_server.gui.actions import create_actions
from mxsj_web_server.gui.dialogs.help import DialogMixin
from mxsj_web_server.gui.pages.content import ServersPage, TextPage
from mxsj_web_server.gui.pages.workspace import WorkspacePages
from mxsj_web_server.gui.tray import make_tray
from mxsj_web_server.gui.worker import Worker


class MainWindow(WorkspacePages, DialogMixin, QMainWindow):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.snapshot = None
        self.editor_revision = self.settings_revision = 0
        self.content_generation = self.settings_generation = 0
        self.dirty = self.settings_dirty = False
        self.loading = self.busy = self.exiting = self.allow_close = False
        self.tray_notified = False
        self.pool = QThreadPool(self)
        self.pool.setMaxThreadCount(1)
        self.worker = self.callback = None
        self.setWindowTitle(f"Web 服务管理器 {__version__}")
        self.setWindowIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        )
        self.resize(1180, 820)
        self.setMinimumSize(850, 600)
        self.status_label = QLabel("正在读取管理状态……")
        self.status_label.setWordWrap(True)
        self.navigation = QListWidget()
        self.navigation.addItems(
            [
                "总览",
                "新闻公告",
                "客服公告",
                "区服列表",
                "发布管理",
                "服务设置",
                "日志／审计",
            ]
        )
        self.navigation.setMaximumWidth(155)
        self.pages = QStackedWidget()
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.news, self.service = TextPage("新闻公告"), TextPage("客服公告")
        self.servers = ServersPage()
        for widget in (
            self._overview(),
            self.news,
            self.service,
            self.servers,
            self._versions(),
            self._settings(),
            self._logs(),
        ):
            self.pages.addWidget(widget)
        split = QSplitter()
        split.addWidget(self.navigation)
        split.addWidget(self.pages)
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.status_label)
        layout.addWidget(split)
        self.setCentralWidget(central)
        self.statusBar().showMessage(str(manager.store.directory))
        create_actions(self)
        self.tray = make_tray(self)
        self.news.editor.textChanged.connect(self.content_changed)
        self.service.editor.textChanged.connect(self.content_changed)
        self.servers.changed.connect(self.content_changed)
        for policy in self.policies.values():
            policy.changed.connect(self.settings_changed)
        self.navigate(0)
        self.timer = QTimer(self)
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.submit(manager.snapshot, self.load_editors)

    def navigate(self, index):
        self.navigation.setCurrentRow(index)
        if index == 6 and hasattr(self, "actions"):
            self.load_logs()

    def submit(self, function, callback=None):
        if self.busy or self.allow_close:
            self.statusBar().showMessage("当前操作尚未完成，请稍候。")
            return
        self.busy = True
        self.update_actions()
        self.callback = callback
        self.worker = Worker(function)
        self.worker.signals.done.connect(self.completed)
        self.pool.start(self.worker)

    def completed(self, value, error):
        callback = self.callback
        self.busy = False
        self.worker = self.callback = None
        if error:
            self.exiting = False
            self.timer.start()
            QMessageBox.warning(self, "操作未完成", error)
        elif callback:
            callback(value)
        if not self.allow_close:
            self.update_actions()

    def refresh(self):
        if not self.busy and not self.exiting:
            self.submit(self.manager.snapshot, self.update_snapshot)

    def update_snapshot(self, state):
        if self.snapshot:
            previous = self.snapshot
            if (
                self.editor_revision == previous["revision"]
                and previous["draft"] == state["draft"]
            ):
                self.editor_revision = state["revision"]
            if (
                self.settings_revision == previous["revision"]
                and previous["settings"] == state["settings"]
            ):
                self.settings_revision = state["revision"]
        self.snapshot = state
        services = state["services"]
        labels = {
            "running": "运行中",
            "paused": "已暂停",
            "stopped": "已停止",
            "starting": "启动中",
            "stopping": "停止中",
        }
        text = (
            f"公开服务：{labels[services['public']['status']]}　"
            f"后台：{labels[services['admin']['status']]}　"
            f"当前版本：{state['active'] or '未发布'}"
        )
        if state["logging"]["failures"]:
            text += f"　日志故障累计：{state['logging']['failures']}"
        self.status_label.setText(text)
        self.tray.setToolTip(text)
        self.overview.setPlainText(
            json.dumps(
                {
                    "services": services,
                    "configured": {
                        k: {f: v[f] for f in ("host", "port", "origin")}
                        for k, v in state["settings"].items()
                    },
                    "admin_password_configured": state["has_password"],
                    "sessions": state["sessions"],
                    "revision": state["revision"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        selected = self.selected_release()
        self.releases.clear()
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QListWidgetItem

        for release in state["releases"]:
            title = release["id"] + (
                " [当前]" if release["id"] == state["active"] else ""
            )
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, release["id"])
            self.releases.addItem(item)
            if release["id"] == selected:
                self.releases.setCurrentItem(item)
        self.update_actions()

    def load_editors(self, state):
        self.loading = True
        self.news.editor.setPlainText(state["draft"]["news"])
        self.service.editor.setPlainText(state["draft"]["service"])
        self.servers.apply(state["draft"]["groups"])
        for kind, widget in self.policies.items():
            widget.apply(state["settings"][kind])
        self.editor_revision = self.settings_revision = state["revision"]
        self.loading = self.dirty = self.settings_dirty = False
        self.update_snapshot(state)
        self.statusBar().showMessage("已读取草稿与设置；保存不等于发布。")

    def reload_editors(self):
        if (self.dirty or self.settings_dirty) and not self.confirm(
            "重新加载将放弃未保存修改，继续？"
        ):
            return
        self.submit(self.manager.snapshot, self.load_editors)

    def update_actions(self):
        if not self.snapshot:
            return
        for kind in ("public", "admin"):
            status = self.snapshot["services"][kind]["status"]
            for operation in ("start", "pause", "restart", "stop"):
                allowed = (
                    status == "stopped"
                    if operation == "start"
                    else status in {"running", "paused"}
                )
                self.actions[f"{kind}.{operation}"].setEnabled(
                    allowed and not self.busy
                )
            self.actions[f"{kind}.pause"].setText(
                "继续" if status == "paused" else "暂停"
            )
        for name in (
            "save",
            "build",
            "activate",
            "validate",
            "preview",
            "reload",
            "import",
            "export",
        ):
            self.actions[name].setEnabled(not self.busy)

    def content_changed(self):
        if not self.loading:
            self.content_generation += 1
            self.dirty = True
            self.statusBar().showMessage("内容有未保存修改。")

    def settings_changed(self):
        if not self.loading:
            self.settings_generation += 1
            self.settings_dirty = True

    def current_content(self):
        return {
            "news": self.news.editor.toPlainText(),
            "service": self.service.editor.toPlainText(),
            "groups": self.servers.value(),
        }

    def read_content(self):
        try:
            return self.current_content()
        except ValueError:
            QMessageBox.warning(
                self, "区服输入无效", "端口必须为整数，请检查区服表格。"
            )
            return None

    def save_content(self):
        raw = self.read_content()
        if raw is not None:
            revision = self.editor_revision
            generation = self.content_generation

            def saved(state):
                self.editor_revision = state["revision"]
                self.dirty = self.content_generation != generation
                self.update_snapshot(state)
                self.statusBar().showMessage(
                    "提交的草稿已保存；仍有新修改。"
                    if self.dirty
                    else "草稿已保存，尚未发布。"
                )

            self.submit(lambda: self.manager.save_draft(raw, revision), saved)

    def validate_content(self):
        raw = self.read_content()
        if raw is not None:
            self.submit(
                lambda: render(raw),
                lambda _: QMessageBox.information(
                    self, "校验通过", "基础结构与 Big5 编码通过；不是原生客户端验收。"
                ),
            )

    def preview_content(self):
        raw = self.read_content()
        if raw is not None:
            self.submit(
                lambda: preview(raw),
                lambda result: self.show_text("文本预览（非游戏原生效果）", result),
            )

    def selected_release(self):
        from PySide6.QtCore import Qt

        item = self.releases.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def build_release(self):
        if self.dirty:
            QMessageBox.information(
                self, "请先保存", "版本仅从已保存草稿生成，请先保存修改。"
            )
            return
        if self.snapshot:
            revision = self.snapshot["revision"]
            self.submit(
                lambda: self.manager.create_release(revision), self.update_snapshot
            )

    def inspect_release(self):
        identity = self.selected_release()
        if identity:
            self.submit(
                lambda: self.manager.inspect(identity),
                lambda value: self.show_text("版本与差异", value),
            )

    def activate_release(self):
        identity = self.selected_release()
        if identity and self.confirm(
            "确认将公开内容切换到选中版本？现有请求可完成，后续请求读取新版本。"
        ):
            revision = self.snapshot["revision"]
            self.submit(
                lambda: self.manager.activate(identity, revision), self.update_snapshot
            )

    def save_settings(self):
        try:
            settings = {kind: widget.value() for kind, widget in self.policies.items()}
        except (ValueError, AttributeError):
            QMessageBox.warning(
                self, "输入无效", "规则到期时间必须为整数，请补齐表格字段。"
            )
            return
        if not self.confirm(
            "保存后名单立即生效，空白名单会拒绝全部来源；监听变更需重启对应服务。继续？"
        ):
            return
        revision = self.settings_revision
        generation = self.settings_generation

        def saved(state):
            self.settings_revision = state["revision"]
            self.settings_dirty = self.settings_generation != generation
            self.update_snapshot(state)
            self.statusBar().showMessage("设置已保存；监听地址变更请重启对应服务。")

        self.submit(
            lambda: self.manager.save_settings(validate(settings), revision), saved
        )

    def service_action(self, kind, operation):
        if not self.snapshot:
            return
        if (
            operation == "pause"
            and self.snapshot["services"][kind]["status"] == "paused"
        ):
            operation = "resume"
        if operation in {"restart", "stop"} and not self.confirm(
            "确认操作该服务？关闭后台将使所有后台登录会话失效。"
        ):
            return
        self.submit(lambda: self.manager.control(kind, operation), self.update_snapshot)

    def reset_password(self):
        password, ok = QInputDialog.getText(
            self,
            "管理员密码",
            "设置 12..256 字符密码（不记录）：",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        repeated, ok = QInputDialog.getText(
            self, "确认管理员密码", "再次输入：", QLineEdit.EchoMode.Password
        )
        if not ok or password != repeated:
            QMessageBox.warning(self, "未修改", "两次输入不一致或已取消。")
            return
        self.submit(lambda: self.manager.set_password(password), self.update_snapshot)

    def revoke_sessions(self):
        if self.confirm("确认退出所有远程管理会话？"):
            self.submit(self.manager.revoke_sessions, self.update_snapshot)

    def load_logs(self):
        def read():
            return {
                "diagnostics": self.manager.events.snapshot(),
                "audit": self.manager.audit(),
            }

        def done(data):
            self.log_lines = [
                json.dumps(row, ensure_ascii=False)
                for row in data["diagnostics"]["rows"] + data["audit"]
            ]
            self.filter_logs()

        self.submit(read, done)

    def filter_logs(self):
        needle = self.log_filter.text()
        self.log_view.setPlainText(
            "\n".join(line for line in self.log_lines if needle in line)
        )

    def export_logs(self):
        name, _ = QFileDialog.getSaveFileName(
            self, "导出脱敏日志到新文件", "web-server-logs.json", "JSON (*.json)"
        )
        if name:
            self.submit(
                lambda: self.manager.export_logs(Path(name)),
                lambda _: self.statusBar().showMessage("日志已导出。"),
            )

    def import_content(self):
        if self.dirty and not self.confirm("导入将替换编辑区未保存内容，继续？"):
            return
        name, _ = QFileDialog.getOpenFileName(
            self, "导入 UTF-8 内容 JSON", "", "JSON (*.json)"
        )
        if not name:
            return

        def read():
            path = Path(name)
            if path.stat().st_size > 4 * 1024 * 1024:
                raise ValueError("文件过大")
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
            render(raw)
            return raw

        def done(raw):
            self.news.editor.setPlainText(raw["news"])
            self.service.editor.setPlainText(raw["service"])
            self.servers.apply(raw["groups"])
            self.content_changed()

        self.submit(read, done)

    def export_content(self):
        raw = self.read_content()
        if raw is None:
            return
        name, _ = QFileDialog.getSaveFileName(
            self, "导出草稿到新文件", "content.json", "JSON (*.json)"
        )
        if name:

            def write():
                render(raw)
                with Path(name).open("x", encoding="utf-8") as stream:
                    json.dump(raw, stream, ensure_ascii=False, indent=2)

            self.submit(write, lambda _: self.statusBar().showMessage("草稿已导出。"))

    def edit_action(self, method):
        widget = QApplication.focusWidget()
        if widget and hasattr(widget, method):
            getattr(widget, method)()

    def open_url(self, kind):
        if self.snapshot:
            active = self.snapshot["services"][kind]["active_config"]
            origin = (active or self.snapshot["settings"][kind])["origin"]
            QDesktopServices.openUrl(
                QUrl(origin + ("/news.txt" if kind == "public" else "/"))
            )

    def open_log_directory(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.manager.store.directory)))

    def confirm(self, text):
        return (
            QMessageBox.question(
                self,
                "确认操作",
                text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        )

    def restore_window(self):
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def hide_to_tray(self):
        if not self.tray.isSystemTrayAvailable():
            return False
        self.hide()
        if not self.tray_notified:
            self.tray.showMessage(
                "Web 服务管理器", "程序仍在运行。双击托盘图标恢复窗口。"
            )
            self.tray_notified = True
        return True

    def changeEvent(self, event):  # noqa: N802  # Qt hook.
        super().changeEvent(event)
        if (
            event.type() == QEvent.Type.WindowStateChange
            and self.isMinimized()
            and hasattr(self, "tray")
        ):
            self.hide_to_tray()

    def closeEvent(self, event):  # noqa: N802  # Qt hook.
        if self.allow_close:
            event.accept()
            return
        event.ignore()
        if self.busy:
            self.statusBar().showMessage("操作进行中，请等待完成后退出。")
            return
        box = QMessageBox(self)
        box.setWindowTitle("是否退出 Web 服务管理器？")
        box.setText(
            "退出会停止本程序的公开服务和管理后台。"
            + ("\n未保存修改将丢失。" if self.dirty or self.settings_dirty else "")
        )
        hide = box.addButton("隐藏到托盘", QMessageBox.ButtonRole.ActionRole)
        hide.setEnabled(self.tray.isSystemTrayAvailable())
        exit_button = box.addButton(
            "停止服务并退出", QMessageBox.ButtonRole.DestructiveRole
        )
        cancel = box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(cancel)
        box.exec()
        if box.clickedButton() == hide:
            self.hide_to_tray()
        elif box.clickedButton() == exit_button:
            self.exiting = True
            self.timer.stop()

            def finished(_):
                self.allow_close = True
                self.tray.hide()
                self.close()
                QApplication.instance().quit()

            self.submit(self.manager.close, finished)
