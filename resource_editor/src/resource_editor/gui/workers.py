"""后台任务：把打开包、批量导图、保存等耗时操作放到线程池。

约定任务函数签名为 ``fn(progress)``，progress(done, total) 回报进度；
结果经信号回主线程，异常转为中文字符串经 error 信号回传。
"""
from __future__ import annotations

import traceback
from collections.abc import Callable

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class JobSignals(QObject):
    """任务信号（QRunnable 本身不是 QObject，信号单独承载）。"""

    finished = Signal(object)
    error = Signal(str)
    progress = Signal(int, int)


class Job(QRunnable):
    """通用后台任务。"""

    def __init__(self, fn: Callable, description: str = ""):
        super().__init__()
        self._fn = fn
        self.description = description
        self.signals = JobSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(self.signals.progress.emit)
        except Exception:
            self.signals.error.emit(traceback.format_exc(limit=3))
            return
        self.signals.finished.emit(result)
