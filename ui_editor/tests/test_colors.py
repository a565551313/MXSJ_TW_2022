"""颜色值解析/回写测试：整数、逗号串、十六进制、带 alpha 的整数。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import colors  # noqa: E402


class TestColorKeys(unittest.TestCase):
    def test_key_heuristic(self):
        for key in ("iColor", "lColor", "sColor", "iNormalColor",
                    "iSelectColor", "lTxtColor", "iEnterColor"):
            self.assertTrue(colors.is_color_key(key), key)
        for key in ("iColorTime", "sFileName", "bChangeColorFlag"):
            self.assertFalse(colors.is_color_key(key), key)


class TestParse(unittest.TestCase):
    def test_int(self):
        self.assertEqual(colors.parse_color(0xFF8000),
                         (255, 128, 0, 255))

    def test_negative_int_has_alpha(self):
        value = colors.parse_color(-0x7F010000)
        self.assertEqual(value, (255, 0, 0, 128))
        self.assertTrue(colors.has_alpha(-0x7F010000))

    def test_strings(self):
        self.assertEqual(colors.parse_color("255, 128, 0"),
                         (255, 128, 0, 255))
        self.assertEqual(colors.parse_color("#ff8000"), (255, 128, 0, 255))
        self.assertEqual(colors.parse_color("#80ff0000"),
                         (255, 0, 0, 128))
        self.assertEqual(colors.parse_color("0xff8000"), (255, 128, 0, 255))
        self.assertIsNone(colors.parse_color("combdialog\\a.png"))

    def test_alpha_detection(self):
        self.assertFalse(colors.has_alpha(0xFFFFFF))
        self.assertTrue(colors.has_alpha("#80ff0000"))
        self.assertTrue(colors.has_alpha("0x80ff0000"))
        self.assertFalse(colors.has_alpha("255,0,0"))


class TestFormat(unittest.TestCase):
    def test_int_stays_int(self):
        out = colors.format_like(0x112233, (255, 0, 0, 255))
        self.assertIsInstance(out, int)
        self.assertEqual(out, 0xFF0000)

    def test_int_with_alpha_keeps_alpha(self):
        out = colors.format_like(-0x7F010000, (0, 255, 0, 128))
        self.assertIsInstance(out, int)
        self.assertEqual(colors.parse_color(out), (0, 255, 0, 128))
        self.assertLess(out, 0)

    def test_comma_string_keeps_style(self):
        self.assertEqual(colors.format_like("255,255,255",
                                            (1, 2, 3, 255)),
                         "1,2,3")
        self.assertEqual(colors.format_like("255, 255, 255",
                                            (1, 2, 3, 255)),
                         "1, 2, 3")

    def test_hex_strings(self):
        self.assertEqual(colors.format_like("#ffffff", (1, 2, 3, 255)),
                         "#010203")
        self.assertEqual(colors.format_like("#80ffffff",
                                            (1, 2, 3, 128)),
                         "#80010203")
        self.assertEqual(colors.format_like("0xffffff", (1, 2, 3, 255)),
                         "0x010203")


class TestCoerce(unittest.TestCase):
    def test_int_input_accepts_decimal_and_hex(self):
        self.assertEqual(colors.coerce_like(0xFFFFFF, "255"), 0xFF)
        self.assertEqual(colors.coerce_like(0xFFFFFF, "#010203"), 0x010203)
        self.assertEqual(colors.coerce_like(0xFFFFFF, "abc"), 0xFFFFFF)

    def test_string_input_kept_verbatim(self):
        self.assertEqual(colors.coerce_like("255,0,0", "1, 2, 3"),
                         "1, 2, 3")


if __name__ == "__main__":
    unittest.main()
