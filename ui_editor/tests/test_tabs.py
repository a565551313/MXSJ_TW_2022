"""多标签会话状态（ui/tabs.py）——无 Qt 依赖的单元回归。

锁住：来源身份（同键=同一布局切标签而非重开）、标签星标、
关闭确认条件、切走时的选择/缩放快照。
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core.model import LayoutDocument  # noqa: E402
from ui_editor.ui.tabs import EditorSession  # noqa: E402


class _FakeView:
    """最小视图替身：只提供 transform()。"""

    def __init__(self) -> None:
        self._t = "zoom-150"

    def transform(self):
        return self._t


class TestEditorSession(unittest.TestCase):
    def test_key_of_tracks_source_identity(self):
        loose = LayoutDocument()
        loose.source_path = "a\\b\\x.dlg"
        self.assertEqual(EditorSession.key_of(loose), ("file", "a\\b\\x.dlg"))
        packed = LayoutDocument()
        packed.source_pack = ("interface.fls", "dialog/x.dlg")
        self.assertEqual(EditorSession.key_of(packed),
                         ("pack", "interface.fls", "dialog/x.dlg"))
        self.assertIsNone(EditorSession.key_of(LayoutDocument()))
        self.assertIsNone(EditorSession.key_of(None))

    def test_label_marks_unsaved_and_pending(self):
        clean = LayoutDocument()
        clean.source_path = "x.dlg"
        session = EditorSession(clean, ("file", "x.dlg"))
        self.assertEqual(session.label(), "x.dlg")
        self.assertFalse(session.needs_confirm())
        clean.dirty = True
        self.assertEqual(session.label(), "x.dlg*")
        self.assertTrue(session.needs_confirm())
        clean.dirty = False
        clean.pending_pack_import = True
        self.assertTrue(session.needs_confirm())
        self.assertEqual(session.label(), "x.dlg*")

    def test_label_unnamed_and_snapshot(self):
        view = _FakeView()
        doc = LayoutDocument()
        doc.dirty = True
        session = EditorSession(doc, None, view)
        self.assertEqual(session.label(), "未命名布局*")
        self.assertEqual(EditorSession(LayoutDocument(), None).label(),
                         "未命名布局")
        widget = object()
        session.snapshot(widget, [0, 2, 1])
        self.assertIs(session.selected, widget)
        self.assertEqual(session.selection_anchor, [0, 2, 1])
        self.assertEqual(session.transform, "zoom-150")

    def test_pending_import_needs_confirm(self):
        doc = LayoutDocument()
        doc.source_pack = ("new.fls", "dialog/p.dlg")
        doc.pending_pack_import = True
        session = EditorSession(doc, ("pack", "new.fls", "dialog/p.dlg"))
        self.assertTrue(session.needs_confirm())
        self.assertTrue(session.label().endswith("*"))


if __name__ == "__main__":
    unittest.main()
