"""注册布局/混合编码回归；只解析字面量，不执行回传的布局文件。"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "reg_layout", HERE / "build_regform_dlg.py"
)
layout = importlib.util.module_from_spec(spec)
spec.loader.exec_module(layout)
sys.path.insert(0, str(ROOT / "ui_editor" / "src"))
from ui_editor.core.dlg_codec import parse_bytes  # noqa: E402

# 钉住真实回传原字节，防止乱码模板也被当作正常布局传下去。
TEMPLATE_SHA256 = {
    "chgpwd.dlg": "b20859a172a51cfecc3059f86618d8a28a40d84fbf99c343c11ac1a3d7408c7e",
    "confirm.dlg": "b53ac5347d413d76cdb7e4b0a58b5cc413826fda956425ba490ef965d3c2130c",
    "reg1.dlg": "244a6507decb4e300b0e02fe5d46f1beb6bd1450a3c2da55239f90009fe1c1da",
    "reg2.dlg": "64be77d148f853a99ba5f47c9e6d722012a4e77462c66263df1ee93b08ef043a",
    "service.dlg": "820f09a8cd4e8ff80494cffdfc6de042550f897f7747c6345de793fa68b46d26",
}


class RegistrationLayoutsTest(unittest.TestCase):
    def setUp(self):
        self.raw_form = layout.build_form()
        self.serialized = layout.serialize_ui(self.raw_form)
        self.form, _ = parse_bytes(self.serialized)
        self.by_name = {w["sName"]: w for w in self.form}

    def test_templates_are_exact_downloaded_bytes(self):
        for name, digest in TEMPLATE_SHA256.items():
            with self.subTest(name=name):
                data = (HERE / "templates" / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_terms_are_byte_identical_to_service(self):
        data = (HERE / "regterms.dlg").read_bytes()
        self.assertEqual(data, (HERE / "templates" / "service.dlg").read_bytes())
        widgets, _ = parse_bytes(data)
        self.assertIn("loc_msg", [w["sName"] for w in widgets])
        self.assertEqual(sorted(w["iMsgId"] for w in widgets if "iMsgId" in w), [1, 2])
        # 原生条款用的是 CTextButton，不可仅凭 CButton 类型去找按钮。
        buttons = [w for w in widgets if w.get("sWidgetType") == "CTextButton"]
        self.assertEqual([w["sText"] for w in buttons], ["同 意", "拒 絕"])

    def test_checked_in_form_is_reproducible(self):
        self.assertEqual((HERE / "regform.dlg").read_bytes(), self.serialized)

    def test_raw_byte_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "roundtrip.dlg"
            path.write_bytes(self.serialized)
            self.assertEqual(layout.load_ui(path), self.raw_form)

    def test_four_edits_and_unique_names(self):
        self.assertEqual(len(self.form), 21)
        self.assertEqual(len(self.by_name), len(self.form))
        for name, y in (("account", 254), ("pwd", 294), ("pwd2", 334), ("email", 374)):
            with self.subTest(name=name):
                box = self.by_name[name]
                self.assertEqual(box["sWidgetType"], "CBox")
                self.assertEqual((box["iX"], box["iY"]), (334, y))

    def test_display_text_decodes_as_big5(self):
        self.assertEqual(
            self.by_name["noname7"]["sText"],
            "輸入帳號\n輸入密碼\n確認密碼\n電子郵箱",
        )
        self.assertEqual(self.by_name["lbl_five"]["sText"], "註冊五個帳號")
        for name, text in (
            ("noname12", "確認註冊"),
            ("noname13", "上一步"),
            ("noname22", "返回首頁"),
        ):
            self.assertEqual(self.by_name[name]["sText"], text)
        raw_label = next(w for w in self.raw_form if w["sName"] == "lbl_five")
        self.assertEqual(
            raw_label["sText"].encode("latin-1"), "註冊五個帳號".encode("big5")
        )

    def test_skin_paths_preserve_gbk_template_bytes(self):
        original = layout.load_ui(HERE / "templates" / "chgpwd.dlg")
        original_paths = {w["sFileName"] for w in original if "sFileName" in w}
        for widget in self.raw_form:
            if "sFileName" in widget:
                self.assertIn(widget["sFileName"], original_paths)
        for widget in self.form:
            if widget.get("sWidgetType") == "CButton":
                self.assertEqual(widget["sFileName"], "combdialog\\按钮\\登陆按纽.igs")

    def test_three_buttons_with_distinct_message_ids(self):
        buttons = [w for w in self.form if w.get("sWidgetType") == "CButton"]
        self.assertEqual(sorted(w["iMsgId"] for w in buttons), [1, 2, 3])
        self.assertEqual(sorted(w["iY"] for w in buttons), [400, 457, 514])

    def test_checkbox_inside_frame_without_input_overlap(self):
        check = self.by_name["chk_five"]
        frame = self.by_name["noname3"]
        email = self.by_name["email"]
        self.assertEqual(check["sWidgetType"], "CBox")
        self.assertEqual((check["iWidth"], check["iHeight"]), (224, 24))
        self.assertGreater(check["iY"], email["iY"] + email["iHeight"])
        self.assertLessEqual(
            check["iX"] + check["iWidth"], frame["iX"] + frame["iWidth"]
        )
        self.assertLessEqual(
            check["iY"] + check["iHeight"], frame["iY"] + frame["iHeight"]
        )
        caption = self.by_name["lbl_five"]
        self.assertGreater(caption["iX"], check["iX"])
        self.assertLess(caption["iY"], check["iY"] + check["iHeight"])

    def test_native_factory_manual_message_four(self):
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "CIMGCHECKBOX"
        ]
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call.args[0].attr, "CImageCheckBox")
        self.assertEqual(ast.literal_eval(call.args[1]), "chk_five")
        self.assertTrue(ast.literal_eval(call.args[4]))
        self.assertEqual(ast.literal_eval(call.args[5]), 4)

    def test_no_old_reg2_controls_or_advertising(self):
        names = set(self.by_name)
        self.assertFalse(names.intersection({"email2", "edt_Code", "youxiang", "2980"}))
        self.assertFalse(any("reg2" in w.get("sFileName", "") for w in self.form))


if __name__ == "__main__":
    unittest.main()
