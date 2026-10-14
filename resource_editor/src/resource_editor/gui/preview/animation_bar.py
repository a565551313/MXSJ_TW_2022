"""动画播放条：播放/暂停、帧滑杆、帧号与帧率控制。"""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QStyle,
    QToolButton,
    QWidget,
)


class AnimationBar(QWidget):
    """精灵动画控制条；frame_requested 发出目标帧号。"""

    frame_requested = Signal(int)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance)
        self._count = 0

        self._play_btn = QToolButton(self)
        self._play_btn.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))
        self._play_btn.setToolTip("播放/暂停（空格）")
        self._play_btn.clicked.connect(self.toggle_play)

        self._slider = QSlider(Qt.Horizontal, self)
        self._slider.setEnabled(False)
        self._slider.valueChanged.connect(self._on_slider)

        self._label = QLabel("0 / 0", self)
        self._fps = QSpinBox(self)
        self._fps.setRange(1, 60)
        self._fps.setValue(10)
        self._fps.setSuffix(" fps")
        self._fps.valueChanged.connect(self._apply_fps)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._play_btn)
        layout.addWidget(self._slider, 1)
        layout.addWidget(self._label)
        layout.addWidget(self._fps)

    # ---------------------------------------------------------- 接口 ----
    def set_frame_count(self, count: int) -> None:
        self._count = count
        self._slider.setEnabled(count > 1)
        self._slider.setRange(0, max(0, count - 1))
        self.set_current(0)
        if count <= 1:
            self.stop()

    def set_current(self, index: int) -> None:
        self._slider.blockSignals(True)
        self._slider.setValue(index)
        self._slider.blockSignals(False)
        self._label.setText(f"{index + 1 if self._count else 0} / {self._count}")

    @property
    def playing(self) -> bool:
        return self._timer.isActive()

    def toggle_play(self) -> None:
        if self.playing:
            self.stop()
        elif self._count > 1:
            self._apply_fps()
            self._timer.start()
            self._play_btn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))

    def stop(self) -> None:
        self._timer.stop()
        self._play_btn.setIcon(
            self.style().standardIcon(QStyle.SP_MediaPlay))

    # ---------------------------------------------------------- 内部 ----
    def _apply_fps(self) -> None:
        if self._timer.isActive():
            self._timer.setInterval(1000 // max(1, self._fps.value()))

    def _on_slider(self, value: int) -> None:
        self._label.setText(f"{value + 1} / {self._count}")
        self.frame_requested.emit(value)

    def _advance(self) -> None:
        if self._count <= 1:
            self.stop()
            return
        nxt = (self._slider.value() + 1) % self._count
        self.set_current(nxt)
        self.frame_requested.emit(nxt)
