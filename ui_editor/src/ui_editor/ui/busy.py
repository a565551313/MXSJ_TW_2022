"""忙碌遮罩与后台跑批：黑色半透明罩 + 进度条 + 可选取消。

凡会让界面假死的重活（挂载资源包、整理包内清单、写包全量校验、
批量导出、转精灵）都经 :func:`BusyHostMixin.run_busy` 执行：

* 重活在**后台线程**跑，界面不冻结；进度/完成经 Qt 信号回到主线程；
* 整窗盖一层半透明黑罩，中间面板显示标题、进度条（能报数字显示
  ``done/total``，报不了用滚动样式）、详情与可选**取消**按钮；
* 遮罩期间主窗口输入被事件过滤器吞掉（取消按钮除外），防重入；
* ``run_busy`` 用本地事件循环**同步返回**结果，调用方保持直写风格；
  失败原样重抛异常，取消抛 :class:`core.errors.Cancelled`。

取消安全性由任务自己保证：只在「中断不产生半成品」的位置轮询
``handle.cancelled``（逐文件导出、逐条校验、纯转换），写包校验
被取消时调用方负责删除未验证产物。
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from typing import Any, TypeVar

from PySide6.QtCore import QEvent, QEventLoop, QObject, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..core.errors import Cancelled

__all__ = ["BusyHandle", "BusyOverlay", "BusyHostMixin", "run_busy"]

T = TypeVar("T")


class BusyHandle:
    """传给后台任务的进度/取消句柄（线程安全）。"""

    def __init__(self, bridge: _Bridge) -> None:
        self._bridge = bridge
        self._cancelled = threading.Event()

    def report(self, done: int, total: int, text: str = "") -> None:
        """回报进度：``total <= 0`` 表示总量未知（滚动样式）。"""
        self._bridge.progress.emit(done, total, text)

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    def request_cancel(self) -> None:
        self._cancelled.set()


class _Bridge(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(object)
    cancelled = Signal()


class BusyOverlay(QWidget):
    """盖住父窗口内容区的半透明罩；只随任务显示/隐藏。"""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self._bridge = _Bridge(self)
        self._handle = BusyHandle(self._bridge)
        self._panel = QFrame(self)
        self._panel.setObjectName("busyPanel")
        self._panel.setStyleSheet(
            "#busyPanel { background: #23272e; border: 1px solid #3a4150;"
            " border-radius: 6px; }")
        self._title = QLabel("", self._panel)
        self._bar = QProgressBar(self._panel)
        self._bar.setMinimumWidth(320)
        self._detail = QLabel("", self._panel)
        self._detail.setStyleSheet("color: #aab4c4;")
        self._cancel = QPushButton("取消", self._panel)
        self._cancel.clicked.connect(self._handle.request_cancel)
        self._cancel.hide()
        inner = QVBoxLayout(self._panel)
        inner.setContentsMargins(18, 16, 18, 14)
        inner.setSpacing(8)
        inner.addWidget(self._title)
        inner.addWidget(self._bar)
        inner.addWidget(self._detail)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(self._cancel)
        inner.addLayout(row)
        self.hide()

    # -- 任务生命周期 -------------------------------------------------
    def begin(self, title: str, *, maximum: int = 0,
              cancellable: bool = False) -> None:
        self._handle = BusyHandle(self._bridge)
        self._title.setText(title)
        self._detail.setText("")
        if maximum > 0:
            self._bar.setRange(0, maximum)
            self._bar.setValue(0)
        else:
            self._bar.setRange(0, 0)  # 滚动样式：总量未知
        self._cancel.setVisible(cancellable)
        self._cancel.setEnabled(True)
        self.setGeometry(self.parentWidget().rect())
        self.show()
        self.raise_()
        self._panel.adjustSize()
        self._center()
        self.repaint()

    def set_progress(self, done: int, total: int, text: str) -> None:
        if total > 0:
            if self._bar.maximum() != total:
                self._bar.setRange(0, total)
            self._bar.setValue(min(done, total))
        elif self._bar.maximum() != 0:
            self._bar.setRange(0, 0)
        if text:
            self._detail.setText(text)

    def end(self) -> None:
        self.hide()

    @property
    def handle(self) -> BusyHandle:
        return self._handle

    # -- 绘制/布局 ---------------------------------------------------
    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 140))
        painter.end()
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._center()

    def _center(self) -> None:
        pw = self._panel.width()
        ph = self._panel.height()
        self._panel.move((self.width() - pw) // 2, (self.height() - ph) // 2)


class _InputBlocker(QObject):
    """任务期间吞掉主窗口的键鼠输入（遮罩自身与取消按钮除外）。"""

    def __init__(self, overlay: BusyOverlay) -> None:
        super().__init__(overlay)
        self._overlay = overlay

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if not self._overlay.isVisible():
            return False
        kind = event.type()
        blocked = (
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.MouseButtonPress,
            QEvent.Type.MouseButtonRelease,
            QEvent.Type.MouseButtonDblClick,
            QEvent.Type.Wheel,
            QEvent.Type.ContextMenu,
        )
        if kind not in blocked:
            return False
        widget = obj if isinstance(obj, QWidget) else None
        if widget is not None and self._overlay.isAncestorOf(widget):
            return False
        return True


class BusyHostMixin:
    """主窗口混入：``self.run_busy(title, work, ...)`` 同步跑重活。"""

    def _ensure_busy(self) -> BusyOverlay:
        overlay = getattr(self, "_busy_overlay", None)
        if overlay is None:
            overlay = BusyOverlay(self)
            blocker = _InputBlocker(overlay)
            self.installEventFilter(blocker)
            self._busy_overlay = overlay
            self._busy_blocker = blocker
        return overlay

    def run_busy(
        self,
        title: str,
        work: Callable[[BusyHandle], Any],
        *,
        maximum: int = 0,
        cancellable: bool = False,
        cancellable_text: str = "取消",
    ) -> Any:
        """重活 ``work(handle)`` 放后台线程，同步返回其结果。

        抛出 ``work`` 的原异常；用户取消（或 ``work`` 内部检测到
        ``handle.cancelled`` 后抛 :class:`Cancelled`）时统一抛
        :class:`Cancelled`。
        """
        overlay = self._ensure_busy()
        if overlay.isVisible():
            # 已有任务在跑（不应发生：输入被吞）；直接串行执行防重入。
            return work(overlay.handle)
        overlay.begin(title, maximum=maximum, cancellable=cancellable)
        overlay._cancel.setText(cancellable_text)
        bridge = overlay._bridge
        handle = overlay.handle
        loop = QEventLoop(self)
        outcome: dict[str, Any] = {}

        def _on_progress(done: int, total: int, text: str) -> None:
            overlay.set_progress(done, total, text)

        def _on_finished(result: Any) -> None:
            outcome["result"] = result
            loop.quit()

        def _on_failed(exc: BaseException) -> None:
            outcome["error"] = exc
            loop.quit()

        def _on_cancelled() -> None:
            outcome["cancelled"] = True
            loop.quit()

        bridge.progress.connect(_on_progress)
        bridge.finished.connect(_on_finished)
        bridge.failed.connect(_on_failed)
        bridge.cancelled.connect(_on_cancelled)

        def _runner() -> None:
            try:
                result = work(handle)
            except Cancelled:
                bridge.cancelled.emit()
            except BaseException as exc:  # noqa: BLE001 回传给调用方
                bridge.failed.emit(exc)
            else:
                # 协作式取消：work 正常返回 = 结果照收（可含部分产物）；
                # 只有 work 自己抛 Cancelled 才走取消通道。
                bridge.finished.emit(result)

        thread = threading.Thread(target=_runner, daemon=True)
        thread.start()
        # 打开模态输入屏障后再进事件循环：输入全被吞，只有取消可点。
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            loop.exec()
        finally:
            QApplication.restoreOverrideCursor()
            bridge.progress.disconnect(_on_progress)
            bridge.finished.disconnect(_on_finished)
            bridge.failed.disconnect(_on_failed)
            bridge.cancelled.disconnect(_on_cancelled)
            overlay.end()
        if "error" in outcome:
            raise outcome["error"]
        if outcome.get("cancelled"):
            raise Cancelled("操作已取消")
        return outcome.get("result")


def run_busy(host: QWidget, title: str, work: Callable[[BusyHandle], Any],
             **kwargs: Any) -> Any:
    """函数式入口：``host`` 需混入 :class:`BusyHostMixin`。"""
    return host.run_busy(title, work, **kwargs)


class _PlainHandle:
    """无遮罩回退句柄：同步直跑、不报进度、不可取消。"""

    cancelled = False

    @staticmethod
    def report(done: int, total: int, text: str = "") -> None:
        return


PLAIN_HANDLE = _PlainHandle()


def run_busy_or_plain(host: Any, title: str,
                      work: Callable[[Any], Any], **kwargs: Any) -> Any:
    """``host`` 有 ``run_busy`` 就走忙碌遮罩，否则同步直跑（测试回退）。"""
    run = getattr(host, "run_busy", None)
    if run is None:
        return work(PLAIN_HANDLE)
    return run(title, work, **kwargs)
