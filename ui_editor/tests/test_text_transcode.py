"""Big5 用户输入的简→繁规范化；保存编码与词彙本地化边界。"""
import unittest

from ui_editor.core.text_transcode import normalize_display_value


class TextTranscodeTests(unittest.TestCase):
    def test_big5_simplified_mixed_markup_and_ascii(self):
        cases = [
            ("注册账号", "註冊賬號"),
            ("里面的文字", "裡面的文字"),
            ("#Y注册#n", "#Y註冊#n"),
            ("繁體與简体", "繁體與簡體"),
            ("ASCII only", "ASCII only"),
        ]
        for source, expected in cases:
            with self.subTest(source=source):
                actual = normalize_display_value(source, "sText", "big5")
                self.assertEqual(actual, expected)
                actual.encode("big5")  # 这些样本必须能严格落盘

    def test_taiwan_glyphs_without_vocabulary_localization(self):
        self.assertEqual(normalize_display_value(
            "台服软件内存", "sText", "big5"), "臺服軟件內存")

    def test_only_big5_display_text_is_converted(self):
        for key in ("sText", "sTitle", "sTitles", "sTips"):
            with self.subTest(encoding="big5", key=key):
                self.assertEqual(normalize_display_value(
                    "注册账号", key, "big5"), "註冊賬號")
        for encoding in ("gbk", "utf-8"):
            for key in ("sText", "sTitle", "sTitles", "sTips"):
                with self.subTest(encoding=encoding, key=key):
                    self.assertEqual(normalize_display_value(
                        "注册账号", key, encoding), "注册账号")
        for key in ("sName", "sFileName", "iMsgId", None):
            with self.subTest(key=key):
                self.assertEqual(normalize_display_value(
                    "注册账号", key, "big5"), "注册账号")

    def test_nested_values_follow_codec_field_semantics(self):
        value = {"sText": ["注册", ("简体",)], "sName": "注册"}
        self.assertEqual(normalize_display_value(value, None, "big5"), {
            "sText": ["註冊", ("簡體",)], "sName": "注册"})

    def test_conversion_is_idempotent(self):
        once = normalize_display_value("臺服与台服，里面", "sTips", "big5")
        self.assertEqual(normalize_display_value(once, "sTips", "big5"), once)

    def test_surrogateescaped_source_bytes_are_not_masked(self):
        actual = normalize_display_value("\udcff注册", "sText", "big5")
        self.assertEqual(actual, "\udcff註冊")
        self.assertEqual(actual.encode("big5", "surrogateescape"),
                         b"\xff" + "註冊".encode("big5"))

    def test_unencodable_unicode_is_never_replaced(self):
        actual = normalize_display_value("注册😀", "sText", "big5")
        self.assertEqual(actual, "註冊😀")
        self.assertNotIn("?", actual)
        with self.assertRaises(UnicodeEncodeError):
            actual.encode("big5")


if __name__ == "__main__":
    unittest.main()
