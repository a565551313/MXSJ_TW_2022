"""置父坐标经真实散装/资源包保存链保留父相对值，并可正确重开。"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from PySide6.QtWidgets import QApplication

    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:  # pragma: no cover - 无 Qt 环境
    HAS_QT = False

from ui_editor.core import dlg_codec, pack_build  # noqa: E402
from ui_editor.core.assets import AssetResolver  # noqa: E402
from ui_editor.core.model import LayoutDocument  # noqa: E402
from ui_editor.core.mxhash import mx_hash  # noqa: E402


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class NativeCoordinateSaveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.window = MainWindow()
        self.window.new_layout()
        parent = self.window.doc.roots[0]
        parent.name = "A"
        parent.set_geometry(x=500, y=300, width=800, height=600)
        self.child = self.window.doc.new_widget("CBox", parent=parent)
        self.child.name = "B"
        self.child.set_geometry(x=10, y=10, width=100, height=100)
        self.window._refresh_structure()

    def tearDown(self):
        if self.window.doc is not None:
            self.window.doc.dirty = False
            self.window.doc.pending_pack_import = False
        self.window.close()
        self.window.deleteLater()
        self._app.processEvents()
        self.temp.cleanup()

    def _assert_native_payload(self, raw):
        child = raw[0]["lChildren"][0]
        self.assertEqual((child["iX"], child["iY"]), (10, 10))
        doc = LayoutDocument.from_native_dicts(raw, None)
        reopened = doc.roots[0].children[0]
        self.assertEqual((reopened.x, reopened.y), (10, 10))
        self.assertEqual(doc.abs_position(reopened), (510, 310))

    def test_loose_save_preserves_local_and_fresh_open_restores_it(self):
        target = self.root / "out.dlg"
        with mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog.exec",
                return_value=1), mock.patch(
                "ui_editor.ui.save_workflows.QMessageBox.warning") as warning:
            self.assertTrue(self.window.save_as(str(target)))
            warning.assert_not_called()
        raw, _ = dlg_codec.parse_bytes(target.read_bytes())
        self._assert_native_payload(raw)

        second = MainWindow()
        try:
            second.open_layout_file(str(target))
            child = second.doc.roots[0].children[0]
            self.assertEqual((child.x, child.y), (10, 10))
            self.assertEqual(second.doc.abs_position(child), (510, 310))
            self.assertEqual(second.doc.to_native_dicts(), raw)
        finally:
            if second.doc is not None:
                second.doc.dirty = False
            second.close()
            second.deleteLater()
            self._app.processEvents()

    def test_pack_save_also_writes_native_coordinates(self):
        source = self.root / "source.fls"
        entry_id = mx_hash(b"image/keep.bin")
        source.write_bytes(pack_build.build_archive([
            pack_build.RawEntry(entry_id, pack_build.fresh_r1(entry_id),
                                b"KEEP")
        ]))
        original = source.read_bytes()
        self.window.open_pack_file(str(source))
        resource_path = "custom/coordinates.dlg"
        self.window.doc.source_pack = (str(source), resource_path)
        self.window.doc.source_path = None
        self.window.doc.begin_pack_import([])
        output = self.root / "output.fls"
        report = self.window.write_pack_copy(str(output))
        self.assertTrue(report["ok"], report.get("error"))
        self.assertEqual(source.read_bytes(), original)

        resolver = AssetResolver()
        try:
            resolver.mount_pack(str(output))
            result = resolver.fetch_pack_dlg(str(output), resource_path)
            self.assertIsNotNone(result)
            self._assert_native_payload(result[0])
        finally:
            resolver.close()


if __name__ == "__main__":
    unittest.main()
