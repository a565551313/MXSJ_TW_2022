"""build_script_index 的挖掘逻辑测试（合成 code object，不依赖真实包）。"""

import struct
import unittest

from build_script_index import Code, decode_text, mine_code


def op(opcode, arg=None):
    if arg is None:
        return bytes([opcode])
    return bytes([opcode, arg & 0xFF, (arg >> 8) & 0xFF])


LOAD_CONST, LOAD_ATTR, CALL = 100, 105, 131


def make_code(name, consts=(), names=(), bytecode=b"", children=()):
    code = Code()
    code.name = name.encode()
    code.consts = tuple(consts)
    code.names = tuple(names)
    code.code = bytecode
    code.children = list(children)
    return code


class TestDecodeText(unittest.TestCase):
    def test_big5_and_ascii(self):
        self.assertEqual(decode_text("上一頁".encode("big5")), "上一頁")
        self.assertEqual(decode_text(b"login/a.dlg"), "login/a.dlg")


class TestMineCode(unittest.TestCase):
    def test_patterns(self):
        bytecode = b"".join([
            op(LOAD_CONST, 0),          # 'login/a.dlg'
            op(LOAD_ATTR, 0),           # GetObject
            op(LOAD_CONST, 1),          # 'prev'
            op(CALL, 1),
            op(LOAD_ATTR, 1),           # GetPos
            op(CALL, 0),
            op(LOAD_ATTR, 2),           # CLoginSmallButton
            op(LOAD_CONST, 2),          # 'login/btn.igs'
            op(LOAD_CONST, 3),          # '上一頁'
            op(LOAD_CONST, 4),          # 5
            op(CALL, 5),
        ])
        code = make_code(
            "__init__",
            consts=(b"login/a.dlg", b"prev", b"login/btn.igs",
                    "上一頁".encode("big5"), 5),
            names=(b"GetObject", b"GetPos", b"CLoginSmallButton"),
            bytecode=bytecode)
        facts = mine_code(code)
        self.assertEqual(facts.dlgs, ["login/a.dlg"])
        self.assertEqual(facts.objects, [{"name": "prev", "anchor": True}])
        self.assertEqual(len(facts.skins), 1)
        skin = facts.skins[0]
        self.assertEqual(skin["skin"], "login/btn.igs")
        self.assertEqual(skin["text"], "上一頁")
        self.assertEqual(skin["msgid"], 5)
        self.assertEqual(skin["anchor"], "prev")

    def test_getobject_without_getpos_is_not_anchor(self):
        bytecode = b"".join([
            op(LOAD_ATTR, 0), op(LOAD_CONST, 0), op(CALL, 1),
        ])
        code = make_code("OnMessage", consts=(b"lst_rec",),
                         names=(b"GetObject",), bytecode=bytecode)
        facts = mine_code(code)
        self.assertEqual(facts.objects,
                         [{"name": "lst_rec", "anchor": False}])


class TestMineModule(unittest.TestCase):
    def test_class_aggregation(self):
        init = make_code(
            "__init__",
            consts=(b"login/a.dlg", b"btn_ok"),
            names=(b"GetObject",),
            bytecode=b"".join([
                op(LOAD_CONST, 0),
                op(LOAD_ATTR, 0), op(LOAD_CONST, 1), op(CALL, 1),
            ]))
        on_msg = make_code(
            "OnMessage", consts=(b"btn_ok",), names=(b"GetObject",),
            bytecode=b"".join([
                op(LOAD_ATTR, 0), op(LOAD_CONST, 0), op(CALL, 1),
            ]))
        panel = make_code("CPanel", children=[init, on_msg])
        root = make_code("<module>", children=[panel])
        import build_script_index as bsi

        result = bsi._aggregate(99, "script/login/x.py", root)
        layout = result["layouts"]["login/a.dlg"]
        names = set(layout["objects"])
        self.assertEqual(names, {"btn_ok"})
        funcs = {ref["func"] for ref in layout["objects"]["btn_ok"]}
        self.assertEqual(funcs, {"__init__", "OnMessage"})
        classes = {ref["class"] for ref in layout["modules"]}
        self.assertEqual(classes, {"CPanel"})


class TestMarshalSynthetic(unittest.TestCase):
    """最小手工 marshal：根 code 带 interned 引用，解析后要对齐。"""

    def _w_str(self, raw, tag=b"t"):
        return tag + struct.pack("<i", len(raw)) + raw

    def _w_code(self, name, consts_marshal, names_marshal, code_bytes):
        out = [b"c"]
        out.append(struct.pack("<iiii", 0, 0, 0, 0))
        out.append(self._w_str(code_bytes, b"s"))
        out.append(consts_marshal)
        out.append(names_marshal)
        out.append(self._w_tuple([]))   # varnames
        out.append(self._w_tuple([]))   # freevars
        out.append(self._w_tuple([]))   # cellvars
        out.append(self._w_str(b"m.py"))
        out.append(self._w_str(name))
        out.append(struct.pack("<i", 1))
        out.append(self._w_str(b"", b"s"))
        return b"".join(out)

    def _w_tuple(self, items):
        return b"(" + struct.pack("<i", len(items)) + b"".join(items)

    def test_parse_with_ref(self):
        import build_script_index as bsi

        interned = self._w_str(b"shared")
        ref = b"R" + struct.pack("<i", 0)
        consts = self._w_tuple([interned, ref, self._w_str(b"x.dlg", b"s")])
        pyc = b"\xb3\xf2\x0d\x0a" + b"\x00" * 4 + self._w_code(
            b"<module>", consts, self._w_tuple([]), b"")
        root = bsi.parse_pyc(pyc)
        self.assertEqual(root.consts[0], b"shared")
        self.assertEqual(root.consts[1], b"shared")  # R 指回 interned
        self.assertEqual(root.consts[2], b"x.dlg")


if __name__ == "__main__":
    unittest.main()
