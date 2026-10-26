"""核心：属性名中文释义表（0.17.0 功能 3）。"""
import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import prop_glossary
from ui_editor.core.defaults_data import DEFAULT_PROPS


class TestGlossary(unittest.TestCase):
    def test_known_key_description(self):
        self.assertIn("对齐", prop_glossary.describe("iAlign"))
        self.assertIn("相对父控件", prop_glossary.describe("iX"))

    def test_native_trad_names(self):
        # 与原生配置表证据（native_tables.json）抽查一致
        self.assertEqual(prop_glossary.native_name("iAlign"), "對齊")
        self.assertEqual(prop_glossary.native_name("sFileName"), "資源路徑")
        self.assertEqual(prop_glossary.native_name("iWidth"), "寬")

    def test_tooltip_combines_native_name(self):
        tip = prop_glossary.tooltip("iAlign")
        self.assertIn("对齐", tip)
        self.assertIn("原生名：對齊", tip)

    def test_unknown_key_no_tooltip(self):
        self.assertIsNone(prop_glossary.describe("iMadeUp"))
        self.assertIsNone(prop_glossary.tooltip("iMadeUp"))

    def test_census_coverage(self):
        """普查模板的每个键都要有释义（不许漏出裸英文键名）。"""
        missing = [k for d in DEFAULT_PROPS.values() for k in d
                   if prop_glossary.describe(k) is None]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
