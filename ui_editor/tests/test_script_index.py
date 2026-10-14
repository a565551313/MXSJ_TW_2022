"""脚本联动索引查询层：路径归一、关联展开、散装路径反查。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.script_index import ScriptIndex  # noqa: E402

_DATA = {
    "modules": [[4731, "script/login/accountinfo.py"],
                [12, "script/mxgame/main.py"]],
    "layouts": {
        "login/buy_card_record.dlg": {
            "m": [0],
            "o": {
                "prev": [[0, "CBuyCardRecord", "__init__", 1]],
                "lst_rec": [[0, "CBuyCardRecord", "OnMessage", 0]],
            },
            "s": {
                "prev": [[0, "CBuyCardRecord", "__init__",
                          "CLoginSmallButton", "login/btn_small.igs",
                          "上一頁", 5]],
            },
        },
        "dialog/buy_card_record.dlg": {"m": [1]},
    },
}


class TestScriptIndex(unittest.TestCase):
    def setUp(self):
        self.index = ScriptIndex(_DATA)

    def test_for_layout_normalizes_path(self):
        link = self.index.for_layout("LOGIN\\Buy_Card_Record.dlg")
        self.assertIsNotNone(link)
        assert link is not None
        self.assertEqual(link.modules,
                         [(4731, "script/login/accountinfo.py")])
        self.assertTrue(link.objects["prev"][0].anchor)
        self.assertFalse(link.objects["lst_rec"][0].anchor)
        skin = link.skins["prev"][0]
        self.assertEqual(skin.skin, "login/btn_small.igs")
        self.assertEqual(skin.text, "上一頁")
        self.assertEqual(skin.msgid, 5)
        self.assertEqual(skin.factory, "CLoginSmallButton")

    def test_missing_layout_and_empty_index(self):
        self.assertIsNone(self.index.for_layout("nope/none.dlg"))
        self.assertIsNone(self.index.for_layout(None))
        self.assertFalse(ScriptIndex(None))

    def test_skin_bindings_first_ref(self):
        bindings = self.index.skin_bindings("login/buy_card_record.dlg")
        self.assertEqual(set(bindings), {"prev"})
        self.assertEqual(bindings["prev"].skin, "login/btn_small.igs")
        self.assertEqual(self.index.skin_bindings("nope.dlg"), {})

    def test_match_loose_path(self):
        self.assertEqual(
            self.index.match_loose_path(
                "/games/client/login/buy_card_record.dlg"),
            "login/buy_card_record.dlg")
        # 同名两处且给的路径对不上任何一处：不猜
        self.assertIsNone(
            self.index.match_loose_path("nowhere/buy_card_record.dlg"))
        self.assertIsNone(self.index.match_loose_path(None))


class TestShippedIndex(unittest.TestCase):
    """随包索引要有 login 购买记录这条已知关联（生成器回归锚）。"""

    def test_login_buy_card_record(self):
        index = ScriptIndex.load_default()
        self.assertTrue(index)
        link = index.for_layout("login/buy_card_record.dlg")
        self.assertIsNotNone(link)
        assert link is not None
        self.assertIn("prev", link.skins)
        self.assertEqual(link.skins["prev"][0].skin,
                         "login/btn_small.igs")
        self.assertIn("lst_rec", link.objects)
        self.assertGreater(index.stats["modules_mined"], 4900)


if __name__ == "__main__":
    unittest.main()
