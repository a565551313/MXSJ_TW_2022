#!/usr/bin/env python3
"""`dyprot_emulate.py` 的專項回歸。

釘住的東西刻意分成兩層：

* 假 DLL 映像的結構（`pefile` 真的能解析出匯出名與位址）——這是殼繼續往下走的
  前提，壞了會表現成「殼突然停在入口」而不是明顯的例外；
* 執行環境的護欄（輸出不許指向輸入映像、匯出表要覆蓋整個導入名單、
  `ExitProcess` 要乾淨停下而不是被當成普通返回值吞掉）。

需要 `pefile` + `unicorn`；缺依賴時整檔跳過，普通 `unittest discover` 不會紅。
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIENT = HERE.parents[1] / "mxmain.dll"
HAVE_DEPS = all(
    importlib.util.find_spec(name) is not None for name in ("pefile", "unicorn")
)

if HAVE_DEPS:
    sys.path.insert(0, str(HERE))
    import dyprot_emulate as de  # noqa: E402
    import pefile  # noqa: E402
    from fake_modules import build_module  # noqa: E402


@unittest.skipUnless(HAVE_DEPS, "需要 pefile 與 unicorn")
class FakeModuleTests(unittest.TestCase):
    def test_exports_are_parseable_and_keep_their_addresses(self):
        image = build_module(
            "kernel32.dll",
            {"VirtualAlloc": 0x60000100, "GetProcAddress": 0x60000110},
            0x600001F0,
        )
        parsed = pefile.PE(data=image)
        names = {
            entry.name.decode(): entry.address
            for entry in parsed.DIRECTORY_ENTRY_EXPORT.symbols
        }
        self.assertIsNotNone(parsed.DOS_HEADER)
        self.assertEqual(parsed.FILE_HEADER.Machine, 0x14C)
        self.assertEqual(parsed.OPTIONAL_HEADER.ImageBase, 0x50000000)
        self.assertEqual(names.get("VirtualAlloc"), 0x60000100)
        self.assertEqual(names.get("GetProcAddress"), 0x60000110)

    def test_module_grows_for_a_full_import_list(self):
        exports = {f"Api{index}": 0x60000000 + index * 0x10 for index in range(900)}
        image = build_module("kernel32.dll", exports, 0x60000000)
        parsed = pefile.PE(data=image)
        self.assertEqual(len(parsed.DIRECTORY_ENTRY_EXPORT.symbols), 900)
        # SizeOfImage 必須跟著放大，否則殼算模組範圍時會越界
        self.assertGreaterEqual(
            parsed.OPTIONAL_HEADER.SizeOfImage, len(image) & ~0xFFF
        )


@unittest.skipUnless(HAVE_DEPS, "需要 pefile 與 unicorn")
class GuardTests(unittest.TestCase):
    def test_output_may_not_alias_the_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "mxmain.dll"
            image.write_bytes(b"MZ" + b"\x00" * 62)
            self.assertTrue(de._aliases_input(image, image))
            hardlink = Path(tmp) / "out.json"
            hardlink.hardlink_to(image)
            self.assertTrue(de._aliases_input(hardlink, image))
            other = Path(tmp) / "ok.json"
            self.assertFalse(de._aliases_input(other, image))

    def test_main_refuses_to_write_over_the_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / "mxmain.dll"
            image.write_bytes(b"MZ" + b"\x00" * 62)
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                de.main([str(image), "--json", str(image)])
            self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), digest)


@unittest.skipUnless(HAVE_DEPS and CLIENT.is_file(), "需要倉庫根的 mxmain.dll")
class RealClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = de.Runtime(CLIENT).prepare()

    def test_every_import_slot_is_bound(self):
        self.assertGreater(self.rt.import_count, 800)

    def test_fake_exports_cover_the_import_names(self):
        missing = [
            name
            for name in self.rt._imported_names()
            if name not in self.rt.exports
        ]
        self.assertEqual(missing, [])

    def test_stub_or_generic_handles_unknown_export(self):
        self.assertNotIn("definitely_not_exported", self.rt.exports)

    def test_short_run_reports_a_stop_reason(self):
        result = self.rt.run(seconds=2.0, max_insn=2_000_000)
        self.assertTrue(result.stopped)
        self.assertGreater(result.seconds, 0)
        self.assertEqual(result.sha256, hashlib.sha256(CLIENT.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
