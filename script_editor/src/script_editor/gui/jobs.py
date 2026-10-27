from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


class Signals(QObject):
    done = Signal(object)
    failed = Signal(str)


class Job(QRunnable):
    def __init__(self, function):
        super().__init__()
        self.function = function
        self.signals = Signals()

    @Slot()
    def run(self):
        try:
            result = self.function()
        except Exception as exc:
            self.signals.failed.emit(str(exc))
        else:
            self.signals.done.emit(result)


class Progress:
    """Thread-safe progress counter shared between a worker and the GUI timer.

    Widgets may only be touched on the GUI thread. A worker therefore writes
    plain numbers here and a QTimer polls them; nothing in this class knows
    about Qt, so it can also be used by core-only tests.
    """

    def __init__(self):
        import threading

        self._lock = threading.Lock()
        self._done = 0
        self._total = 0
        self._phase = ""

    def update(self, done, total, phase=""):
        with self._lock:
            self._done = int(done)
            self._total = int(total)
            self._phase = str(phase)

    def finish(self):
        self.update(0, 0, "")

    def snapshot(self):
        with self._lock:
            return self._done, self._total, self._phase
