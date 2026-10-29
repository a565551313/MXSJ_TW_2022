"""ui.lst 样式解析测试。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.styles import StyleBook  # noqa: E402

FIXTURE = Path(__file__).parent / "fixtures" / "ui_mini.lst"


class TestStyleBook(unittest.TestCase):
    def setUp(self):
        self.book = StyleBook.parse_bytes(FIXTURE.read_bytes())

    def test_fonts(self):
        self.assertEqual(len(self.book.fonts), 2)
        self.assertEqual(self.book.fonts[0].name, "宋體")
        self.assertEqual(self.book.fonts[0].size, 12)
        self.assertEqual(self.book.font(1).weight, 700)
        self.assertIsNone(StyleBook().font(0))

    def test_font_falls_back_to_newfont(self):
        only_new = StyleBook.parse_text("[NewFont]\n宋体 12 400 0\n")
        self.assertIsNotNone(only_new.font(0))

    def test_extended_font_uses_native_field_positions(self):
        book = StyleBook.parse_text(
            "[Font]\n黑體 0 13 72 800 3 1 0\n"
            "方正蘭亭 0 34 72 0 0 0 4\n")
        first, second = book.fonts
        self.assertEqual((first.name, first.size, first.weight),
                         ("黑體", 13, 800))
        self.assertEqual((second.name, second.size, second.weight),
                         ("方正蘭亭", 34, 0))
        self.assertEqual(book.font(1), second)

    def test_tbstyles(self):
        self.assertEqual(len(self.book.tbstyles), 2)
        self.assertEqual(self.book.tbstyle(0)["ButtonFont"], "1")
        self.assertEqual(
            self.book.tbstyle(0)["ButtonNormalColor"],
            "255 255 180 255 171 121")
        self.assertEqual(self.book.tbstyle(42), {})


if __name__ == "__main__":
    unittest.main()
