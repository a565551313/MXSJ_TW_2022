"""控件模型测试：字典往返、工厂命名、增删。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.model import WIDGET_TYPES, LayoutDocument, Widget  # noqa: E402


def sample_dicts():
    return [
        {"sWidgetType": "CMainFrame", "sName": "main", "iX": 0, "iY": 0,
         "lChildren": []},
        {"sWidgetType": "CBox", "sName": "box", "iX": 5, "iY": 6,
         "lChildren": [
             {"sWidgetType": "CTextFrame", "sName": "lab", "iX": 1, "iY": 2,
              "sText": "你好", "lChildren": []}]},
    ]


class TestWidgetDictRoundTrip(unittest.TestCase):
    def test_roundtrip(self):
        doc = LayoutDocument.from_dicts(sample_dicts(), "x" * 32)
        self.assertEqual(doc.to_dicts(), sample_dicts())

    def test_parent_links(self):
        doc = LayoutDocument.from_dicts(sample_dicts(), None)
        child = doc.roots[1].children[0]
        self.assertIs(child.parent, doc.roots[1])

    def test_unknown_fields_preserved(self):
        dicts = [{"sWidgetType": "CButton", "sName": "b", "iFuture": 9,
                  "lFuture": [1, 2]}]
        doc = LayoutDocument.from_dicts(dicts, None)
        self.assertEqual(doc.to_dicts()[0]["iFuture"], 9)


class TestFactory(unittest.TestCase):
    def test_widget_types_cover_corpus(self):
        self.assertGreaterEqual(len(WIDGET_TYPES), 38)

    def test_unique_names_and_defaults(self):
        doc = LayoutDocument()
        a = doc.new_widget("CButton")
        b = doc.new_widget("CButton")
        self.assertNotEqual(a.name, b.name)
        self.assertEqual(a.props["iVersion"], 7)
        self.assertIn(a, doc.roots)

    def test_add_child_and_remove(self):
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        child = doc.new_widget("CTextFrame", parent=frame)
        self.assertIn(child, frame.children)
        doc.remove_widget(child)
        self.assertEqual(frame.children, [])
        self.assertIsNone(child.parent)

    def test_move_to_root_keeps_absolute_position(self):
        doc = LayoutDocument()
        frame = doc.new_widget("CMainFrame")
        frame.set_geometry(x=100, y=50)
        button = doc.new_widget("CButton", parent=frame)
        button.set_geometry(x=10, y=5)
        doc.move_to_root(button)
        self.assertIsNone(button.parent)
        self.assertIn(button, doc.roots)
        self.assertEqual((button.x, button.y), (110, 55))  # 位置不变
        self.assertEqual(frame.children, [])
        roots = doc.to_dicts()
        self.assertEqual(len(roots), 2)  # 主窗口与按钮并列顶级

    def test_clone_is_deep(self):
        widget = Widget.from_dict(sample_dicts()[1])
        clone = widget.clone()
        clone.children[0].props["sText"] = "改"
        self.assertEqual(widget.children[0].props["sText"], "你好")


if __name__ == "__main__":
    unittest.main()


class TestHistory(unittest.TestCase):
    """撤销/重做快照时间线：逐步回退、合并、截断重做、上限。"""

    def _doc_with_button(self):
        doc = LayoutDocument()
        doc.new_widget("CMainFrame")
        doc.reset_history()
        return doc

    def test_undo_redo_roundtrip(self):
        doc = self._doc_with_button()
        initial = doc.to_dicts()
        button = doc.new_widget("CButton", parent=doc.roots[0])
        doc.checkpoint()
        button.props["sText"] = "確定"
        doc.checkpoint()
        after = doc.to_dicts()
        self.assertTrue(doc.can_undo)
        self.assertTrue(doc.undo())  # 退回只加了按钮（无改字）
        self.assertNotEqual(
            doc.roots[0].children[0].props.get("sText"), "確定")
        self.assertTrue(doc.undo())  # 退回初始
        self.assertEqual(doc.to_dicts(), initial)
        self.assertFalse(doc.can_undo)
        self.assertTrue(doc.redo())
        self.assertTrue(doc.redo())
        self.assertEqual(doc.to_dicts(), after)
        self.assertFalse(doc.can_redo)

    def test_merge_same_field_edits(self):
        doc = self._doc_with_button()
        button = doc.new_widget("CButton", parent=doc.roots[0])
        doc.checkpoint()
        for text in ("一", "二", "三", "四"):
            button.props["sText"] = text
            doc.checkpoint(("prop", id(button), "sText"))
        steps = 0
        while doc.undo():
            steps += 1
        # 加按钮一步 + 连续改字合并一步 = 2 步
        self.assertEqual(steps, 2)
        self.assertEqual(doc.roots[0].children, [])

    def test_new_edit_clears_redo(self):
        doc = self._doc_with_button()
        doc.new_widget("CButton", parent=doc.roots[0])
        doc.checkpoint()
        self.assertTrue(doc.undo())
        doc.new_widget("CButton", parent=doc.roots[0])
        doc.checkpoint()
        self.assertFalse(doc.can_redo)

    def test_history_limit(self):
        doc = self._doc_with_button()
        for _i in range(doc.HISTORY_LIMIT + 10):
            doc.new_widget("CButton", parent=doc.roots[0])
            doc.checkpoint()
        self.assertEqual(len(doc._history), doc.HISTORY_LIMIT)
        steps = 0
        while doc.undo():
            steps += 1
        self.assertEqual(steps, doc.HISTORY_LIMIT - 1)
