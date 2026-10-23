"""五段 XOR 的边界必须用原生算術，不能用研究目錄的測量值。

2026-10-23 的實事故：`registration_2027_layout_r4.zip`（sha `9cf8c5cd…`）在
脚本编辑器里「一个都打不开」。两个原因疊在一起：

1. 编辑器只给**已登記的完整包指紋**自動套用 XOR 參數表，派生包沒登記就一個
   條目都解不開（提示「请先为此script包选择并确认XOR目录」）。
2. 更隱蔽的一個：打包器當時用 `script_fls_keys.json` 裡的 `bounds`（研究目錄
   的測量值）加密，而 entry 4007 的目錄值 `[8966,17948,26868,35778]` 與原生
   算術 `[8966,17948,26868,35757]` 差 21 字節。模塊本體只有 32408 字節，
   全落在前四段，內容不受影響；但**填充區**被最後一段的密鑰錯位覆蓋，
   嚴格解碼器（`parse(..., zero_padding=True)`）就報
   `trailing/nonzero marshal data`，整個條目打不開。

修法：打包時按原生算術算邊界（`native_bounds`），目錄只作交叉核對；打包後
斷言填充區在原生密鑰下解回全零。
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "build_native_registration", HERE / "build_native_registration.py"
)
builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(builder)

# entry 4007（login/register）的密鑰與展開長度，取自
# tools/decompiler/script_fls_keys.json。
REGISTER_KEYS = [222, 84, 13, 219, 82]
REGISTER_SIZE = 44362
CATALOG_BOUNDS = [8966, 17948, 26868, 35778]
NATIVE_BOUNDS = (8966, 17948, 26868, 35757)


class NativeBoundsTests(unittest.TestCase):
    def test_register_entry_bounds_come_from_native_arithmetic(self):
        self.assertEqual(
            builder.native_bounds(REGISTER_KEYS, REGISTER_SIZE), NATIVE_BOUNDS
        )

    def test_catalog_row_differs_from_native(self):
        """目录值确实差 21 字节——这正是 r4 填充区错位的原因。"""
        self.assertEqual(len(CATALOG_BOUNDS), 4)
        diff = [a - b for a, b in zip(CATALOG_BOUNDS, NATIVE_BOUNDS, strict=True)]
        self.assertEqual(diff, [0, 0, 0, 21])
        self.assertNotEqual(list(NATIVE_BOUNDS), CATALOG_BOUNDS)

    def test_bounds_for_entry_prefers_native_and_reports_fallback(self):
        info = {"keys": REGISTER_KEYS, "bounds": CATALOG_BOUNDS}
        bounds, native = builder.bounds_for_entry(info, REGISTER_SIZE, 4007)
        self.assertEqual(bounds, NATIVE_BOUNDS)
        self.assertEqual(native, NATIVE_BOUNDS)
        # 推不出唯一種子的密鑰（entry 0 就是）要退回目錄值，不能硬算。
        broken = {"keys": [18, 18, 225, 225, 84], "bounds": [64, 166, 193, 295]}
        bounds, native = builder.bounds_for_entry(broken, 323, 0)
        self.assertEqual(bounds, tuple(broken["bounds"]))
        self.assertIsNone(native)

    def test_builder_packs_register_with_native_bounds(self):
        """静态钉子：换回 info['bounds'] 就会重现 r4 的填充区错位。"""
        source = (HERE / "build_native_registration.py").read_text(encoding="utf-8")
        self.assertIn("bounds_reg, _ = bounds_for_entry(", source)
        self.assertIn("list(bounds_reg),", source)
        self.assertIn("register padding is not all-zero under native bounds", source)

    def test_xor_round_trip(self):
        keys = tuple(REGISTER_KEYS)
        data = bytes(range(256)) * 40
        bounds = builder.native_bounds(keys, len(data))
        encrypted = builder._xor_segments(data, keys, bounds)
        self.assertNotEqual(encrypted, data)
        self.assertEqual(builder._xor_segments(encrypted, keys, bounds), data)


if __name__ == "__main__":
    unittest.main()
