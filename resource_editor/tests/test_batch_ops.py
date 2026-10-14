"""批量导出（真名目录树）与网格多选/右键信号。"""
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_names import DLG_PATH, IMG_REF, _archive, _dlg_stored  # noqa: E402

from resource_editor.core import names  # noqa: E402
from resource_editor.core.containers import fls0slf  # noqa: E402
from resource_editor.core.model.document import PackDocument  # noqa: E402
from resource_editor.core.mxhash import mx_hash  # noqa: E402
from resource_editor.core.services import exporter  # noqa: E402


class TestExportEntries(unittest.TestCase):
    def test_tree_naming_and_unnamed_fallback(self):
        raw, payloads = _archive()
        known = {mx_hash(DLG_PATH.encode("gbk")): DLG_PATH}
        with mock.patch.object(names, "_KNOWN_CACHE", known):
            doc = PackDocument.from_bytes(raw)
            i_img = doc.index_by_path(IMG_REF)
            i_rest = next(i for i, m in enumerate(doc.archive.extra_metas)
                          if m.entry_id == 0xDEADBEEF)
            assert i_img is not None
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                report = exporter.export_entries(doc, [0, 1, 2], out)
                self.assertEqual(report["failed"], [])
                self.assertEqual(report["entries"], 3)
                # .dlg 按真名落盘且已解密为明文
                dlg_file = out / "dialog" / "test.dlg"
                self.assertTrue(dlg_file.exists())
                self.assertTrue(dlg_file.read_bytes().startswith(
                    b"# -*- coding: gbk -*-"))
                # 图片按真名目录树落盘，内容逐字节一致
                img_file = out.joinpath(
                    *IMG_REF.replace("\\", "/").split("/"))
                self.assertTrue(img_file.exists())
                self.assertEqual(img_file.read_bytes(), payloads[i_img])
                # 无名条目回退 unnamed/<包名>_<序号>.bin
                unnamed = list((out / "unnamed").glob(f"*_{i_rest:04d}.bin"))
                self.assertEqual(len(unnamed), 1)
                self.assertEqual(unnamed[0].read_bytes(), payloads[i_rest])
            doc.close()


class TestExportFallbacks(unittest.TestCase):
    """导出兜底：解不开的精灵回退原始字节、无名 .dlg 按内容导出。

    真实 interface.fls 的条目 1163（本机解码器未覆盖的精灵变体）
    曾因导出先试解码而连原始字节都导不出来，样本回传无门。
    """

    def _doc(self, payload: bytes, entry_id: int) -> PackDocument:
        raw = fls0slf.build(
            [payload], [fls0slf.EntryMeta(entry_id=entry_id, r1=3)])
        return PackDocument.from_bytes(raw)

    def test_broken_sprite_exports_raw_bin(self):
        import struct

        # 魔数是精灵、帧目录却远超数据长度（1163 的失败形态）
        payload = struct.pack("<2sHHHHHH", b"I0", 1, 300, 8, 8, 0, 0)
        payload += b"\x00" * 32
        doc = self._doc(payload, 0x12345678)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = exporter.export_entries(doc, [0], out)
            self.assertEqual(report["failed"], [])
            self.assertEqual(report["entries"], 1)
            got = list((out / "unnamed").glob("*_0000.bin"))
            self.assertEqual(len(got), 1)
            self.assertEqual(got[0].read_bytes(), payload)
        doc.close()

    def test_wav_exports_with_wav_extension(self):
        import struct

        payload = (b"RIFF" + struct.pack("<I", 28) + b"WAVE"
                   b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, 44100,
                                         88200, 2, 16)
                   + b"data" + struct.pack("<I", 0))
        doc = self._doc(payload, 0x0BADF00E)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            report = exporter.export_entries(doc, [0], out)
            self.assertEqual(report["failed"], [])
            got = list((out / "unnamed").glob("*_0000.wav"))
            self.assertEqual(len(got), 1)
            self.assertEqual(got[0].read_bytes(), payload)
        doc.close()

    def test_unnamed_dlg_exports_decrypted(self):
        doc = self._doc(_dlg_stored(), 0x0BADF00D)
        with mock.patch.object(names, "_KNOWN_CACHE", {}):
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                report = exporter.export_entries(doc, [0], out)
                self.assertEqual(report["failed"], [])
                got = list((out / "unnamed").glob("*_0000.dlg"))
                self.assertEqual(len(got), 1)
                self.assertTrue(got[0].read_bytes().startswith(
                    b"# -*- coding: gbk -*-"))
        doc.close()


try:
    from PySide6.QtWidgets import QApplication

    from resource_editor.gui.grid_panel import EntryGridPanel

    HAS_QT = True
except Exception:
    HAS_QT = False


@unittest.skipUnless(HAS_QT, "PySide6 不可用")
class TestGridSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _panel(self) -> EntryGridPanel:
        from resource_editor.core.codecs.detect import EntryKind

        raw, _ = _archive()
        known = {mx_hash(DLG_PATH.encode("gbk")): DLG_PATH}
        with mock.patch.object(names, "_KNOWN_CACHE", known):
            doc = PackDocument.from_bytes(raw)
            doc.resolve_names()  # 名称缓存进文档，面板直接可用
        panel = EntryGridPanel()
        panel.set_document(doc, [EntryKind.BINARY] * doc.count)
        return panel

    def test_search_by_name_substring(self):
        panel = self._panel()
        assert panel._doc is not None
        i_img = panel._doc.index_by_path(IMG_REF)
        i_dlg = panel._doc.index_by_path(DLG_PATH)
        panel._search_edit.setText("底板800")
        self.assertEqual(panel._view, [i_img])
        panel._search_edit.setText("TEST.DLG")  # 不分大小写
        self.assertEqual(panel._view, [i_dlg])
        panel._search_edit.setText("不存在的名字xyz")
        self.assertEqual(panel._view, [])
        panel._search_edit.setText("")  # 清空恢复全部
        self.assertEqual(panel._view, [0, 1, 2])
        panel.close()

    def test_search_by_index(self):
        panel = self._panel()
        panel._search_edit.setText("2")
        self.assertEqual(panel._view, [2])
        panel.close()


@unittest.skipUnless(HAS_QT, "PySide6 不可用")
class TestGridSelection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _panel(self) -> EntryGridPanel:
        from resource_editor.core.codecs.detect import EntryKind

        raw, _ = _archive()
        doc = PackDocument.from_bytes(raw)
        panel = EntryGridPanel()
        panel.set_document(doc, [EntryKind.BINARY] * doc.count)
        return panel

    def test_selection_mode_toggle_and_collect(self):
        panel = self._panel()
        self.assertFalse(panel.selection_mode)
        self.assertEqual(panel.selected_indexes(), [])
        panel.set_selection_mode(True)
        self.assertTrue(panel.selection_mode)
        items = [panel._list.item(r) for r in range(panel._list.count())]
        items[0].setSelected(True)
        items[2].setSelected(True)
        self.app.processEvents()
        self.assertEqual(panel.selected_indexes(), [0, 2])
        self.assertEqual(panel._select_btn.text(), "选择 (2)")
        items[0].setSelected(False)
        self.app.processEvents()
        self.assertEqual(panel.selected_indexes(), [2])
        panel.set_selection_mode(False)  # 退出清空
        self.assertEqual(panel.selected_indexes(), [])
        self.assertEqual(panel._select_btn.text(), "选择")
        panel.close()

    def test_selection_survives_page_refill(self):
        panel = self._panel()
        panel.set_selection_mode(True)
        item = panel._list.item(1)
        item.setSelected(True)
        self.app.processEvents()
        panel._fill_page()  # 翻页/刷新不应吞掉已选
        self.assertEqual(panel.selected_indexes(), [1])
        panel.close()

    def test_context_menu_signal(self):
        panel = self._panel()
        got = []
        panel.context_menu_requested.connect(
            lambda idx, pos: got.append(idx))
        item = panel._list.item(2)
        rect = panel._list.visualItemRect(item)
        panel._on_context_menu(rect.center())
        self.assertEqual(got, [2])
        panel.close()


if __name__ == "__main__":
    unittest.main()
