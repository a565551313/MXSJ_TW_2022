"""Inspect original code objects; never execute the game's modules or DLL."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "registration_edit_audit_builder", HERE / "build_native_registration.py"
)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class NativeEditContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        archive = ROOT / "data/script.fls"
        if not archive.is_file():
            raise unittest.SkipTest("read-only original script.fls unavailable")
        data = archive.read_bytes()
        if hashlib.sha256(data).hexdigest() != builder.BASE_SHA256:
            # 2026-10-23 起仓库里的 data/script.fls 是用户提交的派生包
            # （已换 337/4007），不再是原包。这里验的是「原包」的代码对象，
            # 拿派生包比对没有意义，直接跳过；原包行为由 r5 构建记录与
            # test_build_base 的纯函数用例守着。
            raise unittest.SkipTest(
                "data/script.fls 不是原包（派生包不发这份审计）"
            )
        cls.rows = builder.read_entries(data)
        cls.keys = json.loads(
            (ROOT / "tools/decompiler/script_fls_keys.json").read_text(encoding="utf-8")
        )

    def code_tree(self, index):
        data = builder.decrypt_entry(self.rows[index], self.keys)
        reader = builder.decoder.MarshalReader(data)
        result = reader.read()
        self.assertEqual(reader.pos, len(data))
        return result

    def test_cedit_alias_and_nine_argument_constructor(self):
        tree = self.code_tree(3564)
        self.assertEqual(tree["filename"], b"script\\combmacro.py")
        ops = builder.normalized(tree["code"])
        alias = next(i for i, (_, op, arg) in enumerate(ops)
                     if op == 90 and tree["names"][arg] == b"CEDIT")
        self.assertEqual(ops[alias - 1][1], 101)  # LOAD_NAME CreateEdit
        self.assertEqual(tree["names"][ops[alias - 1][2]], b"CreateEdit")
        edit = dict(builder.code_objects(tree))["CreateEdit"]
        self.assertEqual(edit["argcount"], 7)
        self.assertEqual(edit["varnames"][:7], (
            b"edit_class", b"objname", b"parent", b"color", b"font",
            b"linecolor", b"overstriking",
        ))
        instructions = {
            pc: (op, arg) for pc, op, arg in builder.normalized(edit["code"])
        }
        self.assertEqual(instructions[93], (124, 0))  # LOAD_FAST edit_class
        self.assertEqual(instructions[143], (131, 9))  # CALL_FUNCTION 9
        self.assertIn(b"GetPosOfDlg", edit["names"])
        self.assertIn(b"GetSize", edit["names"])

    def test_original_registration_uses_fontlt14_3_for_native_edit_factory(self):
        tree = self.code_tree(4007)
        self.assertEqual(tree["filename"], b"script\\login\\register.py")
        edits = dict(builder.code_objects(tree))["CRegPanel2/CreateEdits"]
        seq = builder.normalized(edits["code"])
        by_pc = {pc: (op, arg) for pc, op, arg in seq}
        self.assertEqual(by_pc[0], (116, edits["names"].index(b"combmacro")))
        self.assertEqual(by_pc[3], (105, edits["names"].index(b"CEDIT")))
        self.assertEqual(by_pc[18], (116, edits["names"].index(b"interface")))
        self.assertEqual(by_pc[21], (105, edits["names"].index(b"FontLT14_3")))
        # This source has no native FONT_EDIT dependency; its known edit font
        # also already worked in the user's terms COutput at runtime.
        self.assertNotIn(b"FONT_EDIT", edits["names"])

    def test_native_cedit_setlimit_is_real_not_an_invented_stub_method(self):
        tree = self.code_tree(3854)
        self.assertEqual(tree["filename"], b"script\\interface.py")
        codes = dict(builder.code_objects(tree))
        initializer = codes["CEdit/__init__"]
        self.assertEqual(initializer["argcount"], 10)  # self + nine arguments
        limit = codes["CEdit/SetLimit"]
        self.assertEqual(limit["names"], (b"m_Limit",))
        ops = builder.normalized(limit["code"])
        self.assertIn((95, 0), [(op, arg) for _, op, arg in ops])  # STORE_ATTR


if __name__ == "__main__":
    unittest.main()
