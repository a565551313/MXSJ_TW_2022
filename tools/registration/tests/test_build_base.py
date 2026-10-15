"""构建器基线护栏回归：337 補丁窗口三态判定 + 基线 SHA 钉住的行为。

只跑纯函数与一条真归档条目，不启动 CPython 2.5（编译/烟测由 test_runtime.py 负责）。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location(
    "reg_build", HERE / "build_native_registration.py"
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

ARCHIVE = ROOT / "data/script.fls"
KEYS = ROOT / "tools/decompiler/script_fls_keys.json"


def fake_code(before: bytes, window: bytes, after: bytes) -> bytes:
    return before + window + after


class TwPredicateWindowTest(unittest.TestCase):
    NAMES = [b"False", b"IsTWServer"]
    VARNAMES = [b"self", b"misc"]

    def window_bytes(self) -> bytes:
        return (
            build.encode_ins(build.STD_LOAD_FAST, 1)
            + build.encode_ins(build.STD_LOAD_ATTR, 1)
            + build.encode_ins(build.STD_CALL_FUNCTION, 0)
        )

    def replacement_bytes(self) -> bytes:
        rep = build.encode_ins(build.STD_LOAD_GLOBAL, 0)
        pad = build.encode_ins(build.STD_NOP, None) * (build.TW_PATCH_LEN - len(rep))
        return rep + pad

    def test_clean_baseline_is_reported_patchable(self):
        code = fake_code(b"\x00" * build.TW_PATCH_AT, self.window_bytes(), b"\x00" * 8)
        state, replacement = build.tw_predicate_window(code, self.NAMES, self.VARNAMES)
        self.assertEqual(state, "clean")
        self.assertEqual(len(replacement), build.TW_PATCH_LEN)

    def test_already_patched_baseline_is_recognised(self):
        """客户机基线常是上一版产物：窗口已是补丁形态，必须判成 patched。"""
        code = fake_code(
            b"\x00" * build.TW_PATCH_AT, self.replacement_bytes(), b"\x00" * 8
        )
        state, replacement = build.tw_predicate_window(code, self.NAMES, self.VARNAMES)
        self.assertEqual(state, "patched")
        self.assertEqual(replacement, self.replacement_bytes())

    def test_unknown_bytes_fail_loudly(self):
        code = fake_code(b"\x00" * build.TW_PATCH_AT, b"\x11" * build.TW_PATCH_LEN, b"")
        with self.assertRaises(ValueError) as ctx:
            build.tw_predicate_window(code, self.NAMES, self.VARNAMES)
        self.assertIn("fingerprint mismatch", str(ctx.exception))
        self.assertIn("拒絕盲目重打包", str(ctx.exception))


@unittest.skipUnless(ARCHIVE.is_file() and KEYS.is_file(), "缺 data/script.fls")
class MainpageRealArchiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys_db = json.loads(KEYS.read_text(encoding="utf-8"))
        cls.arch = ARCHIVE.read_bytes()

    def decrypted(self, idx: int) -> bytes:
        ioff = struct.unpack_from("<I", self.arch, 8)[0]
        rows = struct.unpack_from("<IIII", self.arch, ioff + idx * 16)
        dec = build.pack.decode_0slf_entry(idx, rows)
        exp = zlib.decompress(
            self.arch[dec["data_offset"] : dec["data_offset"] + dec["comp_len"]]
        )
        info = self.keys_db[str(idx)]
        pts = [0] + list(info["bounds"]) + [len(exp)]
        tabs = build.batch.XTABS
        keys = info["keys"]
        return b"".join(
            bytes(exp[pts[j] : pts[j + 1]]).translate(tabs[keys[j]]) for j in range(5)
        )

    def test_repo_baseline_mainpage_still_needs_the_patch(self):
        payload = self.decrypted(build.ENTRY_MAINPAGE)
        patched, lo, hi, state = build.patch_mainpage(payload)
        self.assertEqual(state, "patched")
        self.assertEqual(hi - lo, build.TW_PATCH_LEN)
        self.assertNotEqual(patched, payload)
        moved = [i for i in range(len(payload)) if patched[i] != payload[i]]
        self.assertTrue(moved)
        self.assertTrue(all(lo <= i < hi for i in moved), "diff 逃出補丁窗口")

    def test_already_patched_payload_is_kept_verbatim(self):
        payload = self.decrypted(build.ENTRY_MAINPAGE)
        patched, _lo, _hi, state = build.patch_mainpage(payload)
        kept, lo, hi, state2 = build.patch_mainpage(patched)
        self.assertEqual(state2, "kept")
        self.assertEqual(kept, patched)
        self.assertEqual(hi - lo, build.TW_PATCH_LEN)


class BaseShaGuardTest(unittest.TestCase):
    def test_foreign_base_is_rejected_with_actionable_hint(self):
        with tempfile.TemporaryDirectory(prefix="mx-reg-guard-") as tmp:
            bogus = Path(tmp) / "other.fls"
            bogus.write_bytes(b"0SLF" + b"\x00" * 64)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(HERE / "build_native_registration.py"),
                    "--archive",
                    str(bogus),
                    "--python25",
                    sys.executable,
                    "--output",
                    str(Path(tmp) / "out" / "script.fls"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            blob = proc.stdout + proc.stderr
            self.assertIn("base archive sha256 mismatch", blob)
            # 把实测 SHA 直接回显出来，省得使用者另开工具算
            self.assertIn("--base-sha256", blob)

    def test_pinned_default_hash_matches_repo_baseline(self):
        if not ARCHIVE.is_file():
            self.skipTest("data/script.fls 不在")
        self.assertEqual(
            hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(), build.BASE_SHA256
        )


if __name__ == "__main__":
    unittest.main()
