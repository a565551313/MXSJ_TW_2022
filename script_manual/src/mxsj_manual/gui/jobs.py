from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class JobSignals(QObject):
    finished = Signal(int, object, str)


class Job(QRunnable):
    def __init__(self, token, function):
        super().__init__()
        self.token, self.function = token, function
        self.signals = JobSignals()

    @Slot()
    def run(self):
        try:
            result = self.function()
        except Exception:
            self.signals.finished.emit(self.token, None, traceback.format_exc())
        else:
            self.signals.finished.emit(self.token, result, "")
