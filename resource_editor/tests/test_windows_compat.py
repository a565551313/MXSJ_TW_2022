"""Windows 兼容性回归（在 Linux 上模拟 Windows 的两处约束）。

* ``os.pread`` 是 POSIX 专属、Windows 没有：把 ``readers._PREAD``
  置 None 强制走「加锁 seek+read」回退路径，验证定位读、流式
  拷贝与多线程并发读都正确（含会被文本模式毁坏的 0x1A/CRLF 字节）。
* Windows 上覆盖仍被读句柄占着的文件会 PermissionError：
  ``save_document`` 必须在替换前释放源句柄；这里验证「打开源
  文件 → 改一条 → 存回同一路径」成功，且替换失败时文档可恢复。
"""
import io
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from resource_editor.core.containers import fls0slf, readers  # noqa: E402
from resource_editor.core.containers.readers import FileReader  # noqa: E402
from resource_editor.core.errors import SaveError  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.services.saver import save_document  # noqa: E402


class TestReadAtWithoutPread(unittest.TestCase):
    """_PREAD=None 即 Windows 的代码路径。"""

    PAYLOAD = bytes(range(256)) * 9000  # >2MB，含 0x1A 与 CRLF 序列

    def _open_patched(self, path: Path) -> FileReader:
        patcher = mock.patch.object(readers, "_PREAD", None)
        patcher.start()
        self.addCleanup(patcher.stop)
        reader = FileReader(path)
        self.addCleanup(reader.close)
        return reader

    def test_read_at_and_copy_to_match(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.bin"
            path.write_bytes(self.PAYLOAD)
            reader = self._open_patched(path)
            self.assertEqual(reader.size, len(self.PAYLOAD))
            cases = [(0, 10), (255, 513), (1_000_000, 12345),
                     (len(self.PAYLOAD) - 7, 7), (len(self.PAYLOAD), 5)]
            for off, size in cases:
                self.assertEqual(reader.read_at(off, size),
                                 self.PAYLOAD[off:off + size])
            buf = io.BytesIO()
            reader.copy_to(123, len(self.PAYLOAD) - 123, buf)
            self.assertEqual(buf.getvalue(), self.PAYLOAD[123:])

    def test_concurrent_reads_without_pread(self):
        payload = os.urandom(512 * 1024)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "x.bin"
            path.write_bytes(payload)
            reader = self._open_patched(path)
            errors: list = []

            def worker(n: int) -> None:
                try:
                    for k in range(30):
                        off = (n * 9973 + k * 131) % (len(payload) - 300)
                        if reader.read_at(off, 300) != payload[off:off + 300]:
                            errors.append((n, k))
                except Exception as exc:  # 收集后统一断言
                    errors.append(exc)

            threads = [threading.Thread(target=worker, args=(n,))
                       for n in range(6)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            self.assertEqual(errors, [])


class TestSaveOverOpenSource(unittest.TestCase):
    """保存回正在打开的同一路径（Windows 句柄占用场景）。"""

    PAYLOADS = [b"alpha" * 10, b"bravo" * 20, bytes(range(256)) * 4]

    def _make_pack(self, td: str) -> tuple[Path, bytes]:
        metas = [fls0slf.EntryMeta(entry_id=i, r1=0)
                 for i in range(len(self.PAYLOADS))]
        original = fls0slf.build(self.PAYLOADS, metas)
        pack = Path(td) / "pack.fls"
        pack.write_bytes(original)
        return pack, original

    def test_save_back_to_same_path(self):
        with tempfile.TemporaryDirectory() as td:
            pack, original = self._make_pack(td)
            doc = PackDocument.open(pack)
            doc.replace_content(1, b"edited")
            report = save_document(doc, pack)
            self.assertTrue(report.ok, msg="; ".join(report.messages))
            # 备份是改前字节；文档已以新文件为基线、改动清零
            self.assertEqual(Path(td, "pack.fls.bak").read_bytes(), original)
            self.assertFalse(doc.is_modified)
            self.assertEqual(doc.content(1), b"edited")
            self.assertEqual(doc.content(2), self.PAYLOADS[2])
            doc.close()
            again = PackDocument.open(pack)
            self.assertEqual(again.content(0), self.PAYLOADS[0])
            self.assertEqual(again.content(1), b"edited")
            again.close()

    def test_failed_replace_keeps_document_usable(self):
        with tempfile.TemporaryDirectory() as td:
            pack, original = self._make_pack(td)
            doc = PackDocument.open(pack)
            doc.replace_content(1, b"edited")
            with mock.patch(
                "resource_editor.core.services.saver.os.replace",
                side_effect=PermissionError("denied"),
            ):
                with self.assertRaises(SaveError):
                    save_document(doc, pack)
            # 原文件未被动过；文档已按原路径重开且编辑状态保留
            self.assertEqual(pack.read_bytes(), original)
            self.assertTrue(doc.is_modified)
            self.assertEqual(doc.content(0), self.PAYLOADS[0])
            doc.close()


if __name__ == "__main__":
    unittest.main()
