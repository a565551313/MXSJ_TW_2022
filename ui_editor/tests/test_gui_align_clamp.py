"""对齐/等距分布结果夹回父矩形（A 方案）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


class TestAlignClampIntoParent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        from ui_editor.ui.main_window import MainWindow
        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        self.frame.set_geometry(x=0, y=0, width=400, height=300)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    def _child(self, name, x, y, w, h):
        widget = self.doc.new_widget("CButton", parent=self.frame)
        widget.props["sName"] = name
        widget.set_geometry(x=x, y=y, width=w, height=h)
        self.window._refresh_structure()
        return widget

    def _select(self, widgets):
        self.window._refresh_structure()
        for item in self.window.scene.items():
            if getattr(item, "widget", None) in widgets:
                item.setSelected(True)

    def test_right_align_never_leaves_parent(self):
        ref = self._child("REF", x=350, y=10, w=40, h=20)
        big = self._child("BIG", x=0, y=50, w=400, h=20)
        self.window._select_widget(ref)
        self._select([ref, big])
        self.window.apply_alignment("right")
        # 右对齐本会算出 x=-50；夹回父内后是 0，且不出父
        self.assertEqual(big.x, 0)
        self.assertGreaterEqual(big.x + big.width, 0)
        self.assertLessEqual(big.x, self.frame.width - 1)
        self.assertIn("父控件边界", self.window.statusBar().currentMessage())

    def test_align_inside_parent_is_untouched_and_unnoted(self):
        ref = self._child("REF", x=10, y=10, w=40, h=20)
        other = self._child("OTHER", x=200, y=100, w=40, h=20)
        self.window._select_widget(ref)
        self._select([ref, other])
        self.window.apply_alignment("left")
        self.assertEqual(other.x, 10)
        self.assertNotIn("父控件边界",
                         self.window.statusBar().currentMessage())

    def test_bottom_align_clamped(self):
        ref = self._child("REF", x=10, y=280, w=40, h=20)
        tall = self._child("TALL", x=100, y=0, w=40, h=300)
        self.window._select_widget(ref)
        self._select([ref, tall])
        self.window.apply_alignment("bottom")
        self.assertEqual(tall.y, 0)

    def test_distribute_keeps_inside_parent(self):
        a = self._child("A", x=0, y=10, w=20, h=20)
        b = self._child("B", x=100, y=10, w=400, h=20)
        c = self._child("C", x=380, y=10, w=20, h=20)
        self.window._select_widget(a)
        self._select([a, b, c])
        self.window.apply_distribute("x")
        for widget in (a, b, c):
            self.assertLessEqual(widget.x, self.frame.width - 1)

    def test_root_widgets_never_go_negative(self):
        root_a = self.doc.new_widget("CButton")
        root_a.set_geometry(x=-30, y=-10, width=40, height=20)
        root_b = self.doc.new_widget("CButton")
        root_b.set_geometry(x=100, y=100, width=40, height=20)
        self.window._refresh_structure()
        self.window._select_widget(root_a)
        self._select([root_a, root_b])
        self.window.apply_alignment("left")
        self.assertEqual(root_b.x, -30)  # 顶级没有父框，保持严格对齐


if __name__ == "__main__":
    unittest.main()
