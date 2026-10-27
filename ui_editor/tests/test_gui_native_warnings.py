"""0.19.0：原生 schema 警示——画布生效、游戏无效的两种情形直说后果。

用户实测（q2_diag=others_worked）：CButton 的宽、高与自加属性键在
画布里生效、进游戏无效。机理是游戏端控件类只读原生模板字段集
（script.fls entry 3853 widgetconfig），多余键忠实保留但引擎不认、
尺寸键缺位则由图片素材自身决定。用户拍板（q2_action=warn）：编辑器
不拦不改，只在状态栏把话说清楚：

* 属性面板写进原生字段集之外的键 → 「游戏会忽略它」；
* 画布缩放松手且动到的维度游戏不读 → 「该维度游戏内由图片素材
  自身决定」（CButton 宽高都不读、CHFrame 不读高、CVScrollBar
  不读宽、CFrame 两个都读所以全程安静）；
* 只挪位置、或动的维度游戏要读 → 不出警示。
"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtWidgets import QApplication, QGraphicsSceneMouseEvent

    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 沙箱缺 Qt 时跳过
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class NativeWarningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = MainWindow()
        self.window.new_layout()
        self.doc = self.window.doc
        self.frame = self.doc.roots[0]
        # 根控件在迷你包里是 0x0，给大画布免得缩放被父矩形夹住
        self.frame.set_geometry(width=400, height=300)
        self.msgs: list[str] = []
        patcher = mock.patch.object(
            self.window, "_update_status",
            side_effect=lambda text: self.msgs.append(text))
        patcher.start()
        self.addCleanup(patcher.stop)

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()

    # -- 帮手 -------------------------------------------------------------
    def _add(self, wtype):
        widget = self.doc.new_widget(wtype, parent=self.frame)
        widget.set_geometry(x=10, y=10, width=100, height=50)
        self.window._refresh_structure()
        return widget

    def _resize(self, widget, handle, dx, dy):
        """合成缩放手势：按住 handle 拖 (dx, dy) 松手（无吸附路径）。"""
        self.window._select_widget(widget)
        item = self.window.scene.item_for(widget)
        self.assertIsNotNone(item)
        item._press_geom = (widget.x, widget.y,
                            widget.width, widget.height)
        item._resize_handle = handle
        item._resize_start = (float(widget.x), float(widget.y),
                              float(widget.width), float(widget.height),
                              QPointF(0.0, 0.0))
        move = QGraphicsSceneMouseEvent()
        move.setButton(Qt.MouseButton.LeftButton)
        move.setScenePos(QPointF(dx, dy))
        item.mouseMoveEvent(move)
        release = QGraphicsSceneMouseEvent()
        release.setButton(Qt.MouseButton.LeftButton)
        item.mouseReleaseEvent(release)

    def _size_warnings(self):
        return [m for m in self.msgs if "不读" in m]

    def _key_warnings(self):
        return [m for m in self.msgs if "原生字段集" in m]

    # -- 自加属性键：原生字段集之外 ---------------------------------------
    def test_custom_key_outside_native_set_warns_but_keeps(self):
        button = self._add("CButton")
        self.window._select_widget(button)
        self.assertTrue(self.window.props_panel._commit("sMyKey", 1))
        # 忠实保留：警示不拦不改，键照旧写进 props（随 .dlg 往返）
        self.assertEqual(button.props["sMyKey"], 1)
        warn = self._key_warnings()
        self.assertEqual(len(warn), 1)
        self.assertIn("sMyKey", warn[0])
        self.assertIn("CButton", warn[0])
        self.assertIn("游戏会忽略", warn[0])

    def test_native_key_commit_is_silent(self):
        button = self._add("CButton")
        self.window._select_widget(button)
        self.assertTrue(self.window.props_panel._commit("sTips", "hi"))
        self.assertEqual(self._key_warnings(), [])

    def test_custom_key_removal_is_silent(self):
        """删键不警示——键已不在控件上，「会随 .dlg 保存」是误报（PR #90）。"""
        button = self._add("CButton")
        self.window._select_widget(button)
        self.assertTrue(self.window.props_panel._commit("sMyKey", 1))
        self.assertEqual(len(self._key_warnings()), 1)   # 写入时照常警示
        self.msgs.clear()
        self.window.props_panel._remove_property("sMyKey")
        self.assertNotIn("sMyKey", button.props)
        self.assertEqual(self._key_warnings(), [])

    def test_external_template_commit_is_silent(self):
        """CEdit 无原生模板（field set 为 None）→ 任何键都不妄下断语。"""
        edit = self._add("CEdit")
        self.window._select_widget(edit)
        self.assertTrue(self.window.props_panel._commit("sMyKey", 1))
        self.assertEqual(self._key_warnings(), [])

    # -- 缩放松手：游戏不读的维度 -----------------------------------------
    def test_cbutton_resize_warns_both_dims(self):
        button = self._add("CButton")
        self._resize(button, "se", 30, 20)
        self.assertEqual((button.width, button.height), (130, 70))
        warn = self._size_warnings()
        self.assertEqual(len(warn), 1)
        self.assertIn("不读宽、高", warn[0])
        self.assertIn("CButton", warn[0])
        self.assertIn("图片素材", warn[0])

    def test_cbutton_resize_height_only(self):
        button = self._add("CButton")
        self._resize(button, "s", 0, 20)
        self.assertEqual((button.width, button.height), (100, 70))
        warn = self._size_warnings()
        self.assertEqual(len(warn), 1)
        self.assertIn("不读高", warn[0])
        self.assertNotIn("宽", warn[0])

    def test_chframe_e_resize_is_silent(self):
        """横排类读宽：拖东把手只动宽 → 游戏要读，不警示。"""
        frame = self._add("CHFrame")
        self._resize(frame, "e", 30, 0)
        self.assertEqual((frame.width, frame.height), (130, 50))
        self.assertEqual(self._size_warnings(), [])

    def test_chframe_se_warns_height_only(self):
        frame = self._add("CHFrame")
        self._resize(frame, "se", 30, 20)
        self.assertEqual((frame.width, frame.height), (130, 70))
        warn = self._size_warnings()
        self.assertEqual(len(warn), 1)
        self.assertIn("不读高", warn[0])
        self.assertNotIn("宽", warn[0])

    def test_cframe_resize_is_silent(self):
        frame = self._add("CFrame")
        self._resize(frame, "se", 30, 20)
        self.assertEqual((frame.width, frame.height), (130, 70))
        self.assertEqual(self._size_warnings(), [])

    def test_move_only_is_silent(self):
        """只挪位置（非缩放路径松手）→ 尺寸警示不出。"""
        button = self._add("CButton")
        self.window._select_widget(button)
        item = self.window.scene.item_for(button)
        item._press_geom = (button.x, button.y,
                            button.width, button.height)
        button.set_geometry(x=60, y=60)   # 模拟拖动挪位
        release = QGraphicsSceneMouseEvent()
        release.setButton(Qt.MouseButton.LeftButton)
        release.setScenePos(QPointF(60, 60))
        item.mouseReleaseEvent(release)
        self.assertEqual(self._size_warnings(), [])

    # -- 回调契约 ---------------------------------------------------------
    def test_resize_commit_callback_contract(self):
        """场景回调只报「真变了的维度」，键序 (widget, dims 元组)。"""
        frame = self._add("CFrame")
        self.window._select_widget(frame)
        calls: list[tuple] = []
        self.window.scene.on_resize_commit = \
            lambda w, dims: calls.append((w, dims))
        self._resize(frame, "se", 30, 20)
        self.assertEqual(len(calls), 1)
        widget, dims = calls[0]
        self.assertIs(widget, frame)
        self.assertEqual(dims, ("width", "height"))

    def test_resize_commit_unchanged_dims_not_reported(self):
        frame = self._add("CFrame")
        self.window._select_widget(frame)
        calls: list[tuple] = []
        self.window.scene.on_resize_commit = \
            lambda w, dims: calls.append((w, dims))
        self._resize(frame, "e", 30, 0)   # 只宽变、高没变
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], ("width",))


if __name__ == "__main__":
    unittest.main()
