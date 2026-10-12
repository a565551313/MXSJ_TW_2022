"""GUI 冒烟测试：离屏模式下打开真实包、解码首个精灵。

无 PySide6 或无显示环境时自动跳过；本地可用
``QT_QPA_PLATFORM=offscreen`` 强制离屏运行。
"""
import os
import sys
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
SKILL_FLS = REPO_ROOT / "data" / "skill.fls"


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

    def test_open_and_preview(self):
        win = MainWindow()
        win.open_file(str(SKILL_FLS))
        self.assertTrue(self._pump_until(lambda: win._doc is not None))
        self.assertEqual(win._doc.count, 342)
        self.assertTrue(
            self._pump_until(lambda: win._sprite is not None, timeout=20))
        self.assertGreaterEqual(win._sprite.frame_count, 1)
        win.close()


if __name__ == "__main__":
    unittest.main()
