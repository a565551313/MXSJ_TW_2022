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
import struct
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
    import win32_env as we  # noqa: E402
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
        # AddressOfFunctions 存 RVA；殼算 base + RVA 才會落在樁上。
        self.assertEqual(names.get("VirtualAlloc"), 0x60000100 - 0x50000000)
        self.assertEqual(names.get("GetProcAddress"), 0x60000110 - 0x50000000)

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

    def test_unknown_arity_raises_instead_of_corrupting_the_stack(self):
        """既沒實作、也不在 `ARG_COUNTS` 裡的導入名要當場報錯。

        以前 `argc` 缺省當 0，`ESP` 只加 4，stdcall 的參數留在棧上，之後整條
        執行流都被歪掉且沒有任何提示——比停下來難查得多。
        """
        from unicorn.x86_const import UC_X86_REG_ESP

        unknown = next(
            name
            for name in self.rt._imported_names()
            if name not in self.rt.procs and name not in we.ARG_COUNTS
        )
        esp = we.STACK + 0x1000
        self.rt.uc.reg_write(UC_X86_REG_ESP, esp)
        self.rt.uc.mem_write(esp, struct.pack("<I", we.SENTINEL))
        with self.assertRaises(de.UnknownArity) as caught:
            self.rt.uc.emu_start(self.rt.stub_for(unknown), we.SENTINEL)
        self.assertEqual(caught.exception.name, unknown)

    def test_exports_without_semantics_declare_their_arity(self):
        """在 `EXTRA_EXPORTS` 裡有名字、卻沒有語意實作的，參數個數要查得到。"""
        expected = {"HeapFree": 3, "CreateFileA": 7, "ReadFile": 5, "LoadLibraryExA": 3}
        self.assertEqual({k: we.ARG_COUNTS.get(k) for k in expected}, expected)
        for name in expected:
            self.assertIn(name, we.EXTRA_EXPORTS)
            self.assertNotIn(name, self.rt.procs)

    def test_stub_arity_matches_the_python_signature(self):
        """`@stdcall(n)` 的 n 就是清棧要彈幾個——不能跟函式簽名對不上。"""
        mismatched = {
            name: (getattr(fn, "argc", None), fn.__code__.co_argcount)
            for name, fn in self.rt.procs.items()
            if getattr(fn, "argc", None) != fn.__code__.co_argcount
        }
        self.assertEqual(mismatched, {})

    def test_code_hook_is_registered_with_a_range(self):
        """`UC_HOOK_CODE` 若不限範圍，每條指令都回 Python，慢一個數量級。

        這裡直接截 `Uc.hook_add` 的實參，而不是只比對常數——否則 `_install_hooks`
        退回無範圍註冊時測試照樣綠。
        """
        from unicorn import Uc

        recorded = []
        original = Uc.hook_add

        def spy(self, htype, callback, *args, **kwargs):
            recorded.append((htype, kwargs))
            return original(self, htype, callback, *args, **kwargs)

        Uc.hook_add = spy
        try:
            de.Runtime(CLIENT)  # 只需要 __init__ 裡的 _install_hooks
        finally:
            Uc.hook_add = original
        code_hooks = [kw for htype, kw in recorded if htype == de.UC_HOOK_CODE]
        expected = [{"begin": de.STUB, "end": de.STUB + de.STUB_SIZE}]
        self.assertEqual(code_hooks, expected)

    def test_run_reaches_the_shells_own_error_dialog(self):
        """匯出表寫成 RVA 之後，殼才解析得到樁、並彈出自己的錯誤文案。

        這條同時釘住 `fake_modules` 的 RVA 編碼：寫絕對位址時殼在彈框之前就跳飛，
        `messages` 會是空的。
        """
        rt = de.Runtime(CLIENT).prepare()
        result = rt.run(seconds=5.0)
        self.assertEqual(
            [(m["title"], m["message"]) for m in result.messages],
            [("mxmain.dll", "Initialization error 3")],
        )
        for entry in rt.pe.DIRECTORY_ENTRY_IMPORT:
            for imp in entry.imports:
                value = struct.unpack("<I", rt.uc.mem_read(imp.address, 4))[0]
                if value:
                    self.assertIn(value, range(de.STUB, de.STUB + de.STUB_SIZE))

    def test_trace_tail_records_the_last_instructions(self):
        """`--trace-tail` 是追停因時唯一的「從哪跳過來」證據，不能啞掉。"""
        traced = de.Runtime(CLIENT, trace_tail=4).prepare()
        traced.run(seconds=0.5, max_insn=20_000)
        steps = traced.tail_trace()
        self.assertEqual(len(steps), 4)
        for step in steps:
            self.assertTrue(step["va"].startswith("0x"))
            self.assertTrue(step["bytes"])

    def test_short_run_reports_a_stop_reason(self):
        result = self.rt.run(seconds=2.0, max_insn=2_000_000)
        self.assertTrue(result.stopped)
        self.assertGreater(result.seconds, 0)
        self.assertEqual(result.sha256, hashlib.sha256(CLIENT.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
