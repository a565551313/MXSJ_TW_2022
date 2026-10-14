"""WAV 音频预览：头信息 + 播放/停止。

解码交给系统多媒体后端（QtMultimedia → Windows 媒体基础），
编辑器自己不带音频解码器：PCM / IMA-ADPCM 一般可直接播，
GSM 6.10 等冷门编码能否播取决于系统装没装对应解码器，播不了
时界面明说，并提示可导出 ``.wav`` 用系统播放器打开。条目内容
先落一份临时 ``.wav`` 再喂后端（按扩展名识别格式最稳妥），
切换条目时覆盖同一临时文件。
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ...core.codecs.wav import parse_wav_info

try:
    from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
except Exception:  # 无多媒体后端（缺库/精简环境）时降级为只看信息
    QAudioOutput = QMediaPlayer = None  # type: ignore[assignment]


def _fmt_ms(ms: int) -> str:
    sec = max(0, ms) / 1000
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


class AudioPreview(QWidget):
    """音频条目预览页：格式说明、播放/停止、进度条。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._info = QLabel(self)
        self._info.setWordWrap(True)
        self._state = QLabel(self)
        self._state.setWordWrap(True)
        self._play_btn = QPushButton("播放", self)
        self._stop_btn = QPushButton("停止", self)
        self._stop_btn.setEnabled(False)
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setRange(0, 0)
        row = QHBoxLayout()
        row.addWidget(self._play_btn)
        row.addWidget(self._stop_btn)
        row.addWidget(self._slider, 1)
        layout = QVBoxLayout(self)
        layout.addWidget(self._info)
        layout.addLayout(row)
        layout.addWidget(self._state)
        layout.addStretch(1)
        self._player = None
        self._audio_out = None
        self._tmp_path = (Path(tempfile.gettempdir())
                          / "resource_editor_preview.wav")
        self._play_btn.clicked.connect(self._on_play)
        self._stop_btn.clicked.connect(self.stop_playback)
        self._slider.sliderMoved.connect(self._on_seek)

    # ---------------------------------------------------------- 内容 ----
    def set_content(self, content: bytes) -> None:
        self.stop_playback()
        info = parse_wav_info(content)
        try:
            self._tmp_path.write_bytes(content)
            stored = True
        except OSError:
            stored = False
        if info is not None:
            self._info.setText(info.describe())
        else:
            self._info.setText("WAV（头解析不完整）")
        if QMediaPlayer is None:
            self._play_btn.setEnabled(False)
            self._state.setText(
                "当前环境没有可用的多媒体后端（QtMultimedia 未能"
                "加载），无法在编辑器内播放；可导出 .wav 后用系统"
                "播放器打开。")
        elif not stored:
            self._play_btn.setEnabled(False)
            self._state.setText("临时文件写入失败，无法播放。")
        else:
            self._play_btn.setEnabled(True)
            self._state.setText(
                "点「播放」试听。编码能否解码由系统多媒体后端决定"
                "（PCM 最稳，GSM 6.10 等冷门编码不一定有解码器）；"
                "播不了可导出 .wav 用系统播放器试。")

    # ---------------------------------------------------------- 播放 ----
    def stop_playback(self) -> None:
        if self._player is not None:
            try:
                self._player.stop()
            except Exception:
                pass
        self._stop_btn.setEnabled(False)

    def _ensure_player(self) -> bool:
        if QMediaPlayer is None:
            return False
        if self._player is None:
            try:
                self._player = QMediaPlayer(self)
                self._audio_out = QAudioOutput(self)
                self._player.setAudioOutput(self._audio_out)
                self._player.durationChanged.connect(
                    lambda ms: self._slider.setRange(0, max(0, ms)))
                self._player.positionChanged.connect(self._on_position)
                self._player.errorOccurred.connect(self._on_error)
                self._player.playbackStateChanged.connect(
                    self._on_state)
            except Exception as exc:  # 后端初始化失败也只降级不崩
                self._player = None
                self._state.setText(f"播放器初始化失败：{exc}")
                return False
        return True

    def _on_play(self) -> None:
        if not self._ensure_player():
            return
        assert self._player is not None
        self._player.setSource(QUrl.fromLocalFile(str(self._tmp_path)))
        self._player.play()
        self._stop_btn.setEnabled(True)

    def _on_seek(self, ms: int) -> None:
        if self._player is not None:
            self._player.setPosition(ms)

    def _on_position(self, ms: int) -> None:
        if not self._slider.isSliderDown():
            self._slider.setValue(ms)
        if self._player is not None:
            total = self._player.duration()
            self._state.setText(
                f"播放中 {_fmt_ms(ms)} / {_fmt_ms(total)}")

    def _on_state(self, state) -> None:
        playing = (self._player is not None
                   and state == self._player.PlaybackState.PlayingState)
        self._stop_btn.setEnabled(playing)
        if (self._player is not None
                and state == self._player.PlaybackState.StoppedState
                and self._player.position() == 0):
            pass  # 停稳即可，状态文字保留最后一次提示

    def _on_error(self, _error, message: str) -> None:
        self._state.setText(
            f"播放失败：{message or '系统后端无法解码此编码'}。"
            "可导出 .wav 后用系统播放器打开。")
