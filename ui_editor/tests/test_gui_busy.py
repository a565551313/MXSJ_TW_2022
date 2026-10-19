"""GUI 冒烟：忙碌遮罩配色（offscreen）。

回归：深色面板上标题与进度条百分比必须白字（0.9.1 用户实测
黑字看不清：「整理包内资源清单（首次较慢）…」标题与 %p% 文本）。
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class TestBusyOverlayColors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def test_title_and_percent_text_are_white(self):
        from PySide6.QtWidgets import QWidget

        from ui_editor.ui.busy import BusyOverlay

        host = QWidget()
        overlay = BusyOverlay(host)
        self.assertIn("#ffffff", overlay._title.styleSheet())
        bar_css = overlay._bar.styleSheet()
        self.assertIn("color: #ffffff", bar_css)
        # 只上 color 会让 chunk 不绘制：进度块与槽必须一起样式化
        self.assertIn("::chunk", bar_css)

    def test_detail_stays_light_on_dark_panel(self):
        from PySide6.QtWidgets import QWidget

        from ui_editor.ui.busy import BusyOverlay

        host = QWidget()  # 父控件要活着，否则子 QLabel 会被回收
        overlay = BusyOverlay(host)
        self.assertIn("color:", overlay._detail.styleSheet())


if __name__ == "__main__":
    unittest.main()
