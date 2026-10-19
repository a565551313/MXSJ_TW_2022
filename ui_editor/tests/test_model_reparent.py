"""父子级模型测试：置父坐标换算、夹进父矩形、防环、锁定、箭头升降级。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.model import LayoutDocument  # noqa: E402


def sample():
    return LayoutDocument.from_dicts([
        {"sWidgetType": "CMainFrame", "sName": "main",
         "iX": 100, "iY": 200, "iWidth": 400, "iHeight": 300,
         "lChildren": []},
        {"sWidgetType": "CBox", "sName": "box",
         "iX": 150, "iY": 260, "iWidth": 200, "iHeight": 100,
         "lChildren": []},
        {"sWidgetType": "CTextFrame", "sName": "lab",
         "iX": 390, "iY": 290, "iWidth": 80, "iHeight": 20,
         "lChildren": []},
    ], None)


class TestSetParent(unittest.TestCase):
    def test_coordinates_become_local_to_new_parent(self):
        doc = sample()
        main, box = doc.roots[0], doc.roots[1]
        doc.set_parent(box, main)
        self.assertIs(box.parent, main)
        self.assertIn(box, main.children)
        self.assertNotIn(box, doc.roots)
        # 绝对位置 (150,260) − 父 (100,200) = (50,60)
        self.assertEqual((box.x, box.y), (50, 60))
        self.assertEqual(doc.abs_position(box), (150, 260))
        self.assertTrue(doc.dirty)

    def test_child_is_clamped_into_parent_canvas(self):
        doc = sample()
        main, lab = doc.roots[0], doc.roots[2]
        lab.set_geometry(x=600, y=600)  # 父外部
        doc.set_parent(lab, main)
        # 绝对 (600,600) − 父 (100,200) = (500,400)；父内最大 (320,280)
        self.assertEqual((lab.x, lab.y), (320, 280))

    def test_parent_smaller_than_child_sticks_top_left(self):
        doc = sample()
        main, box, lab = doc.roots
        doc.set_parent(box, main)
        lab.set_geometry(x=600, y=600)
        doc.set_parent(lab, box)  # box 200x100：夹到 (120,80)
        self.assertEqual((lab.x, lab.y), (120, 80))
        small = doc.new_widget("CBox", parent=main)
        small.set_geometry(width=40, height=10)
        doc.set_parent(lab, small)  # 子比父大：贴左上角，不缩控件
        self.assertEqual((lab.x, lab.y), (0, 0))
        self.assertEqual((lab.width, lab.height), (80, 20))

    def test_to_root_keeps_absolute_position(self):
        doc = sample()
        main, box, _lab = doc.roots
        doc.set_parent(box, main)
        doc.set_parent(box, None)
        self.assertIsNone(box.parent)
        self.assertIn(box, doc.roots)
        self.assertEqual(doc.abs_position(box), (150, 260))

    def test_cycle_is_refused(self):
        doc = sample()
        main, box, _lab = doc.roots
        doc.set_parent(box, main)
        self.assertIsNotNone(doc.reparent_reason(main, box))
        self.assertIsNotNone(doc.reparent_reason(box, box))
        self.assertIsNone(doc.reparent_reason(box, main))

    def test_locked_subtree_is_refused(self):
        doc = sample()
        main, box, lab = doc.roots
        doc.set_parent(lab, box)
        lab.locked = True
        self.assertIsNotNone(doc.reparent_reason(box, main))
        self.assertIsNone(doc.reparent_reason(main, None))

    def test_untouched_when_refused_by_reason_only(self):
        doc = sample()
        main, box, _lab = doc.roots
        doc.set_parent(box, main)
        reason = doc.reparent_reason(main, box)
        self.assertTrue(reason)
        # reparent_reason 只回答原因，不改结构
        self.assertIsNone(main.parent)


class TestArrows(unittest.TestCase):
    def test_indent_becomes_child_of_previous_sibling(self):
        doc = sample()
        main = doc.roots[0]
        first = doc.new_widget("CBox", parent=main)
        second = doc.new_widget("CTextFrame", parent=main)
        first.set_geometry(x=10, y=10, width=100, height=60)
        second.set_geometry(x=120, y=80, width=60, height=20)
        self.assertIsNone(doc.indent_widget(second))
        self.assertIs(second.parent, first)
        self.assertNotIn(second, main.children)
        # 相对坐标 (110,70) 超出 100x60 的父，夹成 (40,40)
        self.assertEqual((second.x, second.y), (40, 40))
        self.assertEqual(doc.abs_position(second), (150, 250))

    def test_first_sibling_cannot_indent(self):
        doc = sample()
        main = doc.roots[0]
        child = doc.new_widget("CBox", parent=main)
        self.assertTrue(doc.indent_widget(child))

    def test_outdent_becomes_sibling_after_parent(self):
        doc = sample()
        main = doc.roots[0]
        outer = doc.new_widget("CBox", parent=main)
        inner = doc.new_widget("CBox", parent=outer)
        self.assertIsNone(doc.outdent_widget(inner))
        self.assertIs(inner.parent, main)
        self.assertEqual(main.children.index(inner),
                         main.children.index(outer) + 1)

    def test_top_level_cannot_outdent(self):
        doc = sample()
        self.assertTrue(doc.outdent_widget(doc.roots[0]))
        self.assertIsNone(doc.roots[0].parent)


if __name__ == "__main__":
    unittest.main()


class TestPasteNaming(unittest.TestCase):
    """粘贴重命名：BTN → BTN_1 → BTN_2；BTN_1 的副本 → BTN_1_1 → BTN_1_2。"""

    def _doc(self):
        doc = LayoutDocument()
        doc.new_widget("CMainFrame")
        return doc

    def test_plain_suffix_sequence(self):
        doc = self._doc()
        widget = doc.new_widget("CButton")
        widget.name = "BTN"
        used = {w.name for w in doc.all_widgets()}
        self.assertEqual(doc.unique_variant_name("BTN", used), "BTN_1")
        used.add("BTN_1")
        self.assertEqual(doc.unique_variant_name("BTN", used), "BTN_2")
        used.add("BTN_2")
        self.assertEqual(doc.unique_variant_name("BTN", used), "BTN_3")

    def test_suffix_base_accumulates(self):
        doc = self._doc()
        widget = doc.new_widget("CButton")
        widget.name = "BTN_1"
        used = {w.name for w in doc.all_widgets()}
        self.assertEqual(doc.unique_variant_name("BTN_1", used), "BTN_1_1")
        used.add("BTN_1_1")
        self.assertEqual(doc.unique_variant_name("BTN_1", used), "BTN_1_2")

    def test_free_name_is_kept(self):
        doc = self._doc()
        self.assertEqual(doc.unique_variant_name("FREE"), "FREE")

    def test_empty_name_kept(self):
        doc = self._doc()
        self.assertEqual(doc.unique_variant_name(""), "")

    def test_rename_copies_handles_subtree(self):
        doc = LayoutDocument.from_dicts([
            {"sWidgetType": "CMainFrame", "sName": "main", "lChildren": [
                {"sWidgetType": "CButton", "sName": "BTN", "lChildren": [
                    {"sWidgetType": "CTextFrame", "sName": "txt",
                     "lChildren": []},
                ]},
            ]},
        ], None)
        clone = doc.roots[0].children[0].clone()
        changed = doc.rename_copies([clone])
        self.assertEqual(changed, 2)
        self.assertEqual(clone.name, "BTN_1")
        self.assertEqual(clone.children[0].name, "txt_1")
        # 原控件没被动
        self.assertEqual(doc.roots[0].children[0].name, "BTN")

    def test_rename_copies_twice(self):
        doc = LayoutDocument.from_dicts([
            {"sWidgetType": "CMainFrame", "sName": "main", "lChildren": [
                {"sWidgetType": "CButton", "sName": "BTN", "lChildren": []},
            ]},
        ], None)
        original = doc.roots[0].children[0]
        first = original.clone()
        doc.rename_copies([first])
        doc.insert_widget(first, doc.roots[0])
        second = original.clone()
        doc.rename_copies([second])
        doc.insert_widget(second, doc.roots[0])
        self.assertEqual((first.name, second.name), ("BTN_1", "BTN_2"))
        self.assertEqual(original.name, "BTN")

    def test_group_paste_gets_distinct_names(self):
        doc = LayoutDocument.from_dicts([
            {"sWidgetType": "CMainFrame", "sName": "main", "lChildren": [
                {"sWidgetType": "CButton", "sName": "BTN", "lChildren": []},
                {"sWidgetType": "CButton", "sName": "BTN2", "lChildren": []},
            ]},
        ], None)
        clones = [child.clone() for child in doc.roots[0].children]
        doc.rename_copies(clones)
        self.assertEqual([c.name for c in clones], ["BTN_1", "BTN2_1"])
