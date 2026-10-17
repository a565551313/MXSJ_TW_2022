"""显示文本可选编码，路径仍为 GBK；默认 Big5 的既有契约不变。"""
import unittest

from ui_editor.core import dlg_codec
from ui_editor.core.diagnostics import diagnose
from ui_editor.core.model import LayoutDocument


class TextEncodingTests(unittest.TestCase):
    def test_three_encodings_roundtrip_nested_fields(self):
        for encoding, text in (("big5", "設定繁體"), ("gbk", "设置简体"),
                               ("utf-8", "设置繁體🙂")):
            with self.subTest(encoding=encoding):
                values = [{"sWidgetType": "CMainFrame", "sTitle": text,
                           "sFileName": "图片/按钮.png", "lChildren": [
                               {"sText": text, "sTitles": [text, text],
                                "sTips": text}]}]
                data = dlg_codec.dump_bytes(values, text_encoding=encoding)
                self.assertIn(text.encode(encoding), data)
                self.assertIn("图片/按钮.png".encode("gbk"), data)
                self.assertEqual(dlg_codec.parse_bytes(
                    data, text_encoding=encoding)[0], values)

    def test_actual_gbk_literal_not_only_our_serializer(self):
        data = (b'# -*- coding: gbk -*-\nUI_INFO = [{"sWidgetType":"CTextFrameEx",'
                b'"sText":"' + "设置简体中文".encode("gbk") + b'"}]\n')
        self.assertEqual(dlg_codec.parse_bytes(data, text_encoding="gbk")[0][0]
                         ["sText"], "设置简体中文")
        self.assertNotEqual(dlg_codec.parse_bytes(data)[0][0]["sText"], "设置简体中文")

    def test_utf8_bom_and_plain_source(self):
        data = '\ufeff# coding: utf-8\nUI_INFO=[{"sText":"设置繁體🙂"}]'.encode()
        self.assertEqual(dlg_codec.parse_bytes(data, text_encoding="utf-8")[0],
                         [{"sText": "设置繁體🙂"}])

    def test_diagnostic_uses_document_codec(self):
        doc = LayoutDocument.from_dicts([{"sText": "简体设置"}], None)
        doc.text_encoding = "gbk"
        self.assertFalse([x for x in diagnose(doc) if x.code == "ENCODING"])
        doc.text_encoding = "big5"
        self.assertTrue([x for x in diagnose(doc) if x.code == "ENCODING"])

    def test_bad_codec_rejected(self):
        with self.assertRaises(ValueError):
            dlg_codec.parse_bytes(b"UI_INFO=[]", text_encoding="invalid")
        with self.assertRaises(ValueError):
            dlg_codec.dump_bytes([], text_encoding="invalid")

    def test_default_unchanged(self):
        data = [{"sText": "測試繁體"}]
        self.assertEqual(dlg_codec.dump_bytes(data),
                         dlg_codec.dump_bytes(data, text_encoding="big5"))
