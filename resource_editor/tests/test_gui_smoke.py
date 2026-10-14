"""GUI 冒烟测试：目录工作区→文件树→打开包→分页网格→选中条目出详情。

无 PySide6 或无显示环境时自动跳过；本地可用
``QT_QPA_PLATFORM=offscreen`` 强制离屏运行。
"""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtWidgets import QApplication

    from resource_editor.gui.main_window import MainWindow

    HAS_QT = True
except Exception:  # 导入失败（缺 Qt 或系统库）时跳过整组
    HAS_QT = False

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
SKILL_FLS = DATA_DIR / "skill.fls"


@unittest.skipUnless(HAS_QT, "PySide6 不可用")
class TestToolbar(unittest.TestCase):
    """顶部工具栏：图标+两字短名，与菜单共用同一 QAction。"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_toolbar_shares_menu_actions(self):
        win = MainWindow()
        bar = win._toolbar
        self.assertIsNotNone(bar)
        actions = bar.actions()
        # 工具栏里的就是菜单里那批 QAction 本人（状态/置灰同步）
        for act in (win._act_save, win._act_open, win._act_import_path):
            self.assertIn(act, actions)
        for act in actions:
            if act.isSeparator():
                continue
            icon = act.icon()
            self.assertFalse(icon.isNull(), act.text())
            self.assertLessEqual(len(act.iconText()), 2, act.text())
        # 无文档时保存类动作置灰（工具栏按钮随之不可点）
        self.assertFalse(win._act_save.isEnabled())
        self.assertFalse(win._act_import_path.isEnabled())
        win.close()


@unittest.skipUnless(HAS_QT, "PySide6 不可用")
@unittest.skipUnless(SKILL_FLS.exists(), "缺少 data/skill.fls")
class TestGuiSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _pump_until(self, pred, timeout=30.0):
        t0 = time.time()
        while time.time() - t0 < timeout:
            self.app.processEvents()
            if pred():
                return True
            time.sleep(0.02)
        return False

    def test_workspace_grid_and_preview(self):
        win = MainWindow()
        # 设定目录：文件树列出目录内的 .fls（只显示文件名）
        win.set_workspace(DATA_DIR)
        names = {Path(k).name for k in win._dir_panel._items}
        self.assertIn("skill.fls", names)
        # 双击打开 skill.fls 到中间网格
        win.open_pack(str(SKILL_FLS))
        self.assertTrue(self._pump_until(lambda: win._doc is not None))
        self.assertEqual(win._doc.count, 342)
        # 默认每页 50 条，分页与翻页
        self.assertEqual(len(win._grid.page_entries()), 50)
        self.assertEqual(win._grid.page_count(), 7)
        win._grid.goto_page(1)
        self.assertEqual(win._grid.page_entries()[0], 50)
        win._grid.goto_page(0)
        # 打开后默认选中条目 0，右侧预览解码出精灵、检查器出详情
        self.assertTrue(
            self._pump_until(lambda: win._sprite is not None, timeout=20))
        self.assertGreaterEqual(win._sprite.frame_count, 1)
        self.assertEqual(win._inspector._fields["名称"].text(), "条目 0")
        # 单击网格条目切换右侧详情（精灵为后台解码，等检查器更新）
        win._select_entry(1)
        self.assertTrue(self._pump_until(
            lambda: win._inspector._fields["名称"].text() == "条目 1",
            timeout=20))
        win.close()

    def test_empty_directory_is_fine(self):
        win = MainWindow()
        with tempfile.TemporaryDirectory() as td:
            win.set_workspace(td)  # 没有 .fls 也能设定，不报错
            self.assertEqual(len(win._dir_panel._items), 0)
            self.assertIsNone(win._doc)
        win.close()


@unittest.skipUnless(HAS_QT, "PySide6 不可用")
class TestAudioPreview(unittest.TestCase):
    """音频预览页：WAV 出信息与播放钮，无后端时降级不崩。"""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_audio_page(self):
        from test_wav import _wav

        from resource_editor.gui.preview.audio_preview import AudioPreview

        page = AudioPreview()
        page.set_content(_wav(1, 8820))  # 0.1 秒 PCM
        self.assertIn("PCM", page._info.text())
        self.assertIn("WAV", page._info.text())
        # 播放后端在/不在都不许崩；停止恒可安全调用
        page.stop_playback()
        page.close()


if __name__ == "__main__":
    unittest.main()
