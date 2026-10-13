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

    def test_clone_is_deep(self):
        widget = Widget.from_dict(sample_dicts()[1])
        clone = widget.clone()
        clone.children[0].props["sText"] = "改"
        self.assertEqual(widget.children[0].props["sText"], "你好")


if __name__ == "__main__":
    unittest.main()
