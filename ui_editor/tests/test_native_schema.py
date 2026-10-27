"""0.19.0：原生 schema 数据层与 2026-10-17 静态证据互检（无 Qt）。

``defaults_data`` 新增的三样东西全部要能对上游戏自带 UI 编辑器
（data/script.fls entry 3853 script/uieditor/widgetconfig.py）的证据转储
``docs/analysis/evidence/widgetconfig_20261017/native_tables.json``：

* ``NATIVE_TYPES`` == DEFAULT_VALUE 的 31 种类型；
* ``native_field_set`` 每种类型 == DEFAULT_VALUE 该型的键集；外部
  模板（DEFAULT_PROPS 多出的 7 种）返回 None；
* ``SIZE_IGNORED_NATIVE`` == 逐型逐维度算出的「原生默认值缺哪个
  尺寸键」映射（宽、高各自独立）：3 型宽高都不读（CButton/
  CSpriteFrame/CTextFrame）、9 型横排只读宽（不读高）、4 型竖排
  只读高（不读宽）、15 型两个都读（不在映射里）。
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ui_editor.core import defaults_data as dd  # noqa: E402

_EVIDENCE = (Path(__file__).resolve().parents[2] / "docs" / "analysis"
             / "evidence" / "widgetconfig_20261017" / "native_tables.json")

_EXTERNALS = {"CAutoDlgBase", "CBitmapFrame", "CBitmapHFrame",
              "CBitmapVFrame", "CDataWidget", "CEdit", "CTitleTableView"}


@unittest.skipUnless(_EVIDENCE.is_file(), "缺 native_tables.json 证据文件")
class NativeSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = json.loads(_EVIDENCE.read_text(encoding="utf-8"))
        cls.dv = raw["DEFAULT_VALUE"]

    # -- NATIVE_TYPES ---------------------------------------------------
    def test_native_types_match_evidence(self):
        self.assertEqual(dd.NATIVE_TYPES, frozenset(self.dv))
        self.assertEqual(len(dd.NATIVE_TYPES), 31)

    def test_defaults_props_covers_native_plus_externals(self):
        self.assertEqual(len(dd.DEFAULT_PROPS), 38)
        self.assertEqual(set(dd.DEFAULT_PROPS) - dd.NATIVE_TYPES, _EXTERNALS)
        self.assertTrue(dd.NATIVE_TYPES <= set(dd.DEFAULT_PROPS))

    # -- native_field_set -------------------------------------------------
    def test_field_sets_match_evidence_per_type(self):
        for wtype, defaults in self.dv.items():
            with self.subTest(wtype=wtype):
                self.assertEqual(dd.native_field_set(wtype),
                                 frozenset(defaults))

    def test_native_templates_field_parity_with_defaults_props(self):
        """31 种原生型的编辑端模板键集与游戏端默认值键集逐项相同。"""
        for wtype in dd.NATIVE_TYPES:
            with self.subTest(wtype=wtype):
                self.assertEqual(set(dd.DEFAULT_PROPS[wtype]),
                                 set(self.dv[wtype]))

    def test_external_templates_have_no_native_set(self):
        for wtype in _EXTERNALS:
            with self.subTest(wtype=wtype):
                self.assertIsNone(dd.native_field_set(wtype))

    def test_unknown_type_has_no_native_set(self):
        self.assertIsNone(dd.native_field_set("CNoSuchWidget"))

    # -- SIZE_IGNORED_NATIVE ---------------------------------------------
    def test_size_ignored_matrix_matches_evidence(self):
        expected = {}
        for wtype, defaults in self.dv.items():
            dims = tuple(
                name for name, key in (("width", "iWidth"),
                                       ("height", "iHeight"))
                if key not in defaults)
            if dims:
                expected[wtype] = dims
        self.assertEqual(dd.SIZE_IGNORED_NATIVE, expected)

    def test_size_ignored_pinned_cases(self):
        # 用户实测的主角：CButton 宽高都不读（真包 5309 例无一写宽高）
        self.assertEqual(dd.SIZE_IGNORED_NATIVE["CButton"],
                         ("width", "height"))
        self.assertEqual(dd.SIZE_IGNORED_NATIVE["CSpriteFrame"],
                         ("width", "height"))
        self.assertEqual(dd.SIZE_IGNORED_NATIVE["CTextFrame"],
                         ("width", "height"))
        # 横排类读宽不读高、竖排类读高不读宽
        self.assertEqual(dd.SIZE_IGNORED_NATIVE["CHFrame"], ("height",))
        self.assertEqual(dd.SIZE_IGNORED_NATIVE["CVScrollBar"], ("width",))
        # 两个尺寸都读的类型不进映射
        self.assertNotIn("CFrame", dd.SIZE_IGNORED_NATIVE)

    def test_size_ignored_split_counts(self):
        dims = list(dd.SIZE_IGNORED_NATIVE.values())
        self.assertEqual(len(dd.SIZE_IGNORED_NATIVE), 16)
        self.assertEqual(dims.count(("width", "height")), 3)
        self.assertEqual(dims.count(("height",)), 9)
        self.assertEqual(dims.count(("width",)), 4)


if __name__ == "__main__":
    unittest.main()
