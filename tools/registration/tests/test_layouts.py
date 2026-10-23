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

    def test_layout_checks_use_native_select_api(self):
        """2026-10-22 换版式：勾选框改成版式自带的三态按钮，走原生 .dlg 接口。

        loginin.py（entry 4806）在 OnMessage 里只读
        ``GetObject('chk_agree').IsSelected()``，从不自己翻——引擎负责翻。
        所以脚本里不能再出现脚本自建的 CIMGCHECKBOX（会和引擎各翻一次）。
        """
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        factory_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "CIMGCHECKBOX"
        ]
        self.assertEqual(factory_calls, [])
        attrs = {
            node.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
        }
        self.assertIn("SetSelect", attrs)
        # 2026-10-23 审查后：读状态走 getattr(obj, reader) 候选表，
        # 所以方法名在字符串常量里（_CHECK_READERS），不在属性节点上。
        readers = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "_CHECK_READERS"
                for target in node.targets
            )
        )
        self.assertEqual(
            ast.literal_eval(readers.value), ("IsSelected", "GetSelect", "IsCheck")
        )
        source = (HERE / "register.py").read_text(encoding="utf-8")
        self.assertIn('_layout_check("btn_fiveaccount")', source)
        self.assertIn('_layout_check("btn_isee")', source)
        # 同意是注册前置条件，必须在 DoCheck 里读 m_Consent。
        do_check = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "DoCheck"
        )
        used = {
            node.attr
            for node in ast.walk(do_check)
            if isinstance(node, ast.Attribute)
        }
        self.assertIn("m_Consent", {n.value.attr for n in ast.walk(do_check)
                                    if isinstance(n, ast.Attribute)
                                    and isinstance(n.value, ast.Attribute)})
        self.assertIn("Get", used)

    def test_2027_layouts_anchors_and_message_ids(self):
        """用户 2026-10-22 重新设计的两个布局：锚点与消息号钉住。"""
        terms, _ = parse_bytes((HERE / "templates/2027/agreement.dlg").read_bytes())
        self.assertIn("loc_msg", [w.get("sName") for w in terms])
        self.assertEqual(
            sorted(w["iMsgId"] for w in terms if "iMsgId" in w), [1, 2]
        )
        form, _ = parse_bytes((HERE / "templates/2027/register2027.dlg").read_bytes())
        by_name = {w.get("sName"): w for w in form}
        for name in ("edt_account", "edt_Pwd", "edt_Pwd_1", "edt_email",
                     "txt_Wrong", "btn_fiveaccount", "btn_isee",
                     "btn_register", "btn_Back"):
            self.assertIn(name, by_name, name)
        self.assertEqual(by_name["btn_Back"]["iMsgId"], 1)
        self.assertEqual(by_name["btn_register"]["iMsgId"], 2)
        # 两个勾选框在用户原稿里同号；脚本靠「只读引擎状态」容错。
        self.assertEqual(by_name["btn_fiveaccount"]["iMsgId"], 50)
        self.assertEqual(by_name["btn_isee"]["iMsgId"], 50)
        # 2026-10-22 用户实机定论：两个勾选的 iTeam **必须不同**，否则点不动。
        # 原稿和当年的交付稿都是 1/1（见下），所以那份 dlg 不再随包发布；
        # 脚本对同号消息/异号 iTeam 都容错，布局以用户本地版为准。
        self.assertEqual(by_name["btn_fiveaccount"]["iTeam"], 1)
        self.assertEqual(by_name["btn_isee"]["iTeam"], 1)
        fixed, _ = parse_bytes(
            (HERE / "templates/2027/register2027_msg.dlg").read_bytes()
        )
        fixed_by_name = {w.get("sName"): w for w in fixed}
        self.assertEqual(fixed_by_name["btn_fiveaccount"]["iMsgId"], 50)
        self.assertEqual(fixed_by_name["btn_isee"]["iMsgId"], 51)
        # 这份历史交付稿的 iTeam 仍是 1/1（正是用户实测点不动的原因），
        # 留在这里只作「除消息号外与原稿逐字节一致」的证据，不得再导入。
        self.assertEqual(fixed_by_name["btn_isee"]["iTeam"], 1)
        # 除了那一个消息号，交付稿与用户原稿必须完全一致（不偷偷改布局）。
        self.assertEqual(fixed_by_name["edt_email"], by_name["edt_email"])
        self.assertEqual(len(fixed), len(form))

    def test_terms_lines_get_native_line_break_marker(self):
        """条款/确认框的每一行都必须补 `#r`——原版是 `[s + '#r' for s in ...]`。

        2026-10-22 那版把反编译输出里的 `_[1]`（py2 列表推导的隐藏累加器）
        当成下标，写成 `line[1:]`，于是每行少一个首字符、也没有换行标记。
        2026-10-23 反汇编 entry 4007/4806 核实：`LOAD_CONST '#r'` + `BINARY_ADD`。
        """
        source = (HERE / "register.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        # 注释里会引用旧写法作说明，所以只钉「代码里出现这个切法」。
        self.assertNotIn("[1:] for line in", source)
        self.assertIn("[line + \"#r\" for line in lines]", source)
        rich = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_RichLines"
        )
        add = next(
            node
            for node in ast.walk(rich)
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add)
        )
        self.assertEqual(ast.literal_eval(add.right), "#r")
        self.assertIsInstance(add.left, ast.Name)
        # 两个加载器都必须走 _RichLines（含兜底路径），不能有一条漏了。
        for name in ("_LoadTermsLines", "_LoadConfirmLines"):
            func = next(
                node
                for node in tree.body
                if isinstance(node, ast.FunctionDef) and node.name == name
            )
            calls = [
                node.func.id
                for node in ast.walk(func)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            ]
            self.assertEqual(calls.count("_RichLines"), 2, (name, calls))

    def test_text_color_is_white_and_read_from_layout(self):
        """2026-10-22 实机：四框/提示行要白字。字色只认构造参数，不是 .dlg 属性。"""
        source = (HERE / "register.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        consts = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    consts[target.id] = node.value
        white = ast.literal_eval(consts["COLOR_TEXT_WHITE"])
        self.assertEqual(white, 16777215)  # 0xFFFFFF，与登录页 edt_Name/edt_Pwd 一致
        # 黑色兜底必须消失：旧版 _HintColor() 缺常量时返回 0。
        self.assertNotIn("_HintColor", source)
        # CEDIT 的 4 号参数（颜色）必须是 _LayoutColor(...)，不能再写死 0。
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "CEDIT"
        ]
        self.assertTrue(calls)
        for call in calls:
            self.assertEqual(len(call.args), 5, ast.dump(call))
            color_arg = call.args[3]
            self.assertIsInstance(color_arg, ast.Call)
            self.assertEqual(color_arg.func.id, "_LayoutColor")
        # CRICHTEXT（提示行）同理。
        rich = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "CRICHTEXT"
        ]
        self.assertTrue(rich)
        for call in rich:
            self.assertEqual(len(call.args), 6, ast.dump(call))
            color_arg = call.args[5]
            self.assertIsInstance(color_arg, ast.Call)
            self.assertEqual(color_arg.func.id, "_LayoutColor")
        # 版式取不到颜色/没有 GetColor() 时必须退回白字，不能退回黑。
        after_fallback = source.split("def _LayoutColor", 1)[1].split(
            "def _CreateFormEdit", 1
        )[0]
        self.assertIn("return COLOR_TEXT_WHITE", after_fallback)

    def test_consent_gate_fails_closed_without_anchor(self):
        """版式缺 btn_isee 时必须挡住提交（用户口径：未勾同意不得注册）。

        2026-10-23 PR #75 审查指出：旧写法 `m_Consent is not None and not Get()`
        在锚点缺失时直接跳过同意校验，等于放行。
        """
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        func = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == "DoCheck"
        )
        # DoCheck 里必须同时有 `is None` 分支与 `not ...Get()` 分支，且都返回提示。
        compares = [
            node
            for node in ast.walk(func)
            if isinstance(node, ast.Compare)
            and any(isinstance(op, ast.Is) for op in node.ops)
        ]
        self.assertTrue(compares, "DoCheck must branch on m_Consent is None")
        returns = [
            node
            for node in ast.walk(func)
            if isinstance(node, ast.Return) and node.value is not None
        ]
        self.assertGreaterEqual(len(returns), 2)
        # 缺锚点的分支必须先于「已勾则通过」的判断：源码里 is None 出现在 Get() 之前。
        source = ast.get_source_segment(
            (HERE / "register.py").read_text(encoding="utf-8"), func
        )
        self.assertLess(
            source.index("m_Consent is None"),
            source.index("m_Consent.Get()"),
        )
        self.assertIn(
            "consent anchor missing",
            (HERE / "register.py").read_text(encoding="utf-8"),
        )

    def test_fallback_toggle_only_when_native_read_missing(self):
        """读不到勾选状态时脚本才自己翻；正常客户端绝不再翻一次。"""
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        classes = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        }
        check_cls = classes["_LayoutCheck"]
        methods = {
            node.name: node
            for node in check_cls.body
            if isinstance(node, ast.FunctionDef)
        }
        self.assertIn("Toggle", methods)
        self.assertIn("Native", methods)
        # Toggle 只改脚本自己的状态，不得调用 SetSelect（那是引擎的活）。
        toggle_src = ast.get_source_segment(
            (HERE / "register.py").read_text(encoding="utf-8"), methods["Toggle"]
        )
        self.assertNotIn("SetSelect", toggle_src)
        form_cls = classes["CRegFormPanel"]
        form_methods = {
            node.name: node
            for node in form_cls.body
            if isinstance(node, ast.FunctionDef)
        }
        click_src = ast.get_source_segment(
            (HERE / "register.py").read_text(encoding="utf-8"),
            form_methods["_CheckClick"],
        )
        # 翻转必须挂在 Native() 的否定分支下。
        self.assertIn("not target.Native()", click_src)
        self.assertIn("target.Toggle()", click_src)
        # 共用消息号时靠 hover 认按钮：两个回调都要在。
        self.assertIn("OnButtonEnter", form_methods)
        self.assertIn("OnButtonLeave", form_methods)

    def test_harness_restores_get_color_before_priority_section(self):
        """harness 第 11 节删掉 GetColor 后必须还原，否则第 12 节测不到优先级。"""
        source = (HERE / "harness.py2").read_text(encoding="utf-8")
        self.assertIn("SAVED_GET_COLOR = FakeObj.__dict__['GetColor']", source)
        self.assertLess(
            source.index("SAVED_GET_COLOR = FakeObj.__dict__['GetColor']"),
            source.index("del FakeObj.GetColor"),
        )
        self.assertGreater(
            source.index("FakeObj.GetColor = SAVED_GET_COLOR"),
            source.index("del FakeObj.GetColor"),
        )
        # 第 12 节之后还有一次「去掉覆盖后必须用回版式色」的断言。
        self.assertGreater(
            source.index("edits12b['edt_Pwd'] == 0x00FF00"),
            source.index("FakeObj.GetColor = SAVED_GET_COLOR"),
        )

    def test_per_anchor_colour_override_is_first(self):
        """「只改某一个框」的落点是 COLOR_TEXT_BY_ANCHOR；版式属性只是次选。

        真 .dlg 里字色属性是 lColor（CTextFrame/CTextFrameEx）与
        lNormalColor（CButton）；本页五个锚点是 CBox，语料里没有任何 CBox
        带颜色属性，所以布局里加属性读不出来，代码里的覆盖表才可靠。
        """
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        consts = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                if isinstance(node.targets[0], ast.Name):
                    consts[node.targets[0].id] = node.value
        self.assertEqual(ast.literal_eval(consts["COLOR_TEXT_BY_ANCHOR"]), {})
        func = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_LayoutColor"
        )
        # 覆盖表必须排在 GetColor() 之前（源码顺序即执行顺序）。
        source = ast.get_source_segment(
            (HERE / "register.py").read_text(encoding="utf-8"), func
        )
        # 只看代码行（docstring 里也会提到 GetColor()，不能算数）。
        quote = chr(34) * 3
        parts = source.split(quote)
        code = parts[2] if len(parts) >= 3 else source
        self.assertLess(
            code.index("COLOR_TEXT_BY_ANCHOR.get"),
            code.index("GetColor()"),
        )
        self.assertLess(
            code.index("GetColor()"),
            code.index("return COLOR_TEXT_WHITE"),
        )

    def test_terms_page_handles_user_added_back_button(self):
        """btn_back 是用户在 agreement.dlg 本机加的；消息号必须从版式读。"""
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        by_name = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
        }
        self.assertIn("_LayoutMsgId", by_name)
        read = [
            node
            for node in ast.walk(by_name["_LayoutMsgId"])
            if isinstance(node, ast.Attribute) and node.attr == "m_MsgID"
        ]
        self.assertEqual(len(read), 1)  # 原生对象属性，不写死消息号
        terms_class = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name == "CRegTermsPanel"
        )
        terms = next(
            node
            for node in terms_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "OnMessage"
        )
        used = set()
        for node in ast.walk(terms):
            if isinstance(node, ast.Attribute):
                used.add(node.attr)
            elif isinstance(node, ast.Name):
                used.add(node.id)
        self.assertIn("m_BackMsgId", used)
        self.assertIn("_ReturnHome", used)
        # 撞号（btn_back=1 与「我同意」同号）必须在日志里留痕。
        self.assertIn(
            "conflicts with agree",
            (HERE / "register.py").read_text(encoding="utf-8"),
        )

    def test_check_msgids_match_delivered_layout(self):
        """交付版式：五个账号 50 / 同意 51（用户 2026-10-23 在 .dlg 里定的）。

        脚本不读 iTeam（它只决定引擎是否把两个勾选当同一组），只按 m_MsgID
        分派；这两个常量就是和版式的契约，改动会让两个勾选互相认错，
        或让同意永远点不到。
        """
        tree = ast.parse((HERE / "register.py").read_text(encoding="utf-8"))
        values = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name) and target.id in (
                    "ID_FIVE_CHECK",
                    "ID_CONSENT_CHECK",
                ):
                    values[target.id] = ast.literal_eval(node.value)
        self.assertEqual(values, {"ID_FIVE_CHECK": 50, "ID_CONSENT_CHECK": 51})

    def test_no_old_reg2_controls_or_advertising(self):
        names = set(self.by_name)
        self.assertFalse(names.intersection({"email2", "edt_Code", "youxiang", "2980"}))
        self.assertFalse(any("reg2" in w.get("sFileName", "") for w in self.form))


if __name__ == "__main__":
    unittest.main()
