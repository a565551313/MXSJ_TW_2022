"""All filesystem, lifecycle and password work stays outside the Qt GUI thread."""

from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Result(QObject):
    done = Signal(object, object)


class Worker(QRunnable):
    def __init__(self, function):
        super().__init__()
        self.function = function
        self.signals = Result()

    @Slot()
    def run(self):
        try:
            value = self.function()
            self.signals.done.emit(value, None)
        except Exception as exc:
            message = (
                str(exc)
                if isinstance(exc, ValueError)
                else "操作失败，请检查文件权限、端口或诊断日志。"
            )
            self.signals.done.emit(None, message)
