"""核心：iAlign 对齐语义（0.17.0 功能 5，含文本类原生映射修复）。

证据：docs/analysis/native_widgetconfig_comparison_20261017.md §1
（旧 CTextFrame 0=右 1=中 2=左；新式与按钮 0–8 九宫）。
"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ui_editor.core.painters import align_scheme, text_align_flags

A = Qt.AlignmentFlag


class TestAlignSemantics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def test_old_text_frame_native_mapping(self):
        self.assertEqual(text_align_flags("CTextFrame", 0),
                         A.AlignRight | A.AlignTop)
        self.assertEqual(text_align_flags("CTextFrame", 1),
                         A.AlignHCenter | A.AlignTop)
        self.assertEqual(text_align_flags("CTextFrame", 2),
                         A.AlignLeft | A.AlignTop)
        # 原生：其余值取右侧偏移
        self.assertEqual(text_align_flags("CTextFrame", 7),
                         A.AlignRight | A.AlignTop)

    def test_new_text_frame_nine_grid(self):
        self.assertEqual(text_align_flags("CTextFrameEx", 0),
                         A.AlignLeft | A.AlignTop)
        self.assertEqual(text_align_flags("CTextFrameEx", 4),
                         A.AlignHCenter | A.AlignVCenter)
        self.assertEqual(text_align_flags("CRichTextFrame", 8),
                         A.AlignRight | A.AlignBottom)

    def test_button_nine_grid(self):
        self.assertEqual(text_align_flags("CButton", 2),
                         A.AlignRight | A.AlignTop)
        self.assertEqual(text_align_flags("CTextButton", 7),
                         A.AlignHCenter | A.AlignBottom)

    def test_button_absent_keeps_legacy(self):
        """按钮没写 iAlign 时保持历史画法（顶+水平居中），不偷改观感。"""
        self.assertEqual(text_align_flags("CButton", None),
                         A.AlignTop | A.AlignHCenter)
        self.assertEqual(text_align_flags("CTextFrame", None),
                         A.AlignTop | A.AlignLeft)

    def test_out_of_range_falls_back_center(self):
        self.assertEqual(text_align_flags("CButton", 9),
                         A.AlignHCenter | A.AlignVCenter)
        self.assertEqual(text_align_flags("CButton", -1),
                         A.AlignHCenter | A.AlignVCenter)

    def test_uncovered_type_legacy(self):
        self.assertEqual(align_scheme("CList"), None)
        self.assertEqual(text_align_flags("CList", 1),
                         A.AlignHCenter | A.AlignTop)

    def test_scheme_lookup(self):
        self.assertEqual(align_scheme("CTextFrame"), "old")
        self.assertEqual(align_scheme("CTextFrameEx"), "nine")
        self.assertEqual(align_scheme("CButton"), "nine")


if __name__ == "__main__":
    unittest.main()
