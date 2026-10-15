"""新实例重开自定义布局，以及旧包按路径只读找回。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtCore import QSettings
    from PySide6.QtWidgets import QApplication

    from ui_editor.ui.main_window import MainWindow

    HAS_QT = True
except ImportError:
    HAS_QT = False

from test_layout_import import layout, raw

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.layout_import import prepare_layout_import
from ui_editor.core.pack import FlsPack


@unittest.skipUnless(HAS_QT, "Qt unavailable")
class TestLayoutReopen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.settings = QSettings(str(self.root / "settings.ini"), QSettings.IniFormat)
        self.patch = mock.patch(
            "ui_editor.ui.main_window.QSettings",
            side_effect=lambda *args: self.settings,
        )
        self.patch.start()
        self.windows = []
        self.pkg = self.root / "saved.fls"
        self.path = "custom/imported.dlg"
        self.bytes = pack_build.build_archive(
            [raw(self.path, dlg_codec.dump_bytes(layout("Imported")))]
        )
        self.pkg.write_bytes(self.bytes)

    def tearDown(self):
        for window in self.windows:
            window.doc = None
            window.close()
        self.patch.stop()
        self.temp.cleanup()

    def window(self):
        window = MainWindow()
        self.windows.append(window)
        window.open_pack_file(str(self.pkg))
        return window

    def test_manual_recovery_is_read_only_and_persists_across_new_resolver(self):
        first = self.window()
        self.assertEqual(first.resolver.scan_layouts(str(self.pkg)), [])
        with mock.patch(
            "ui_editor.ui.main_window.QInputDialog.getText",
            return_value=(self.path, True),
        ):
            first.open_pack_path(str(self.pkg))
        self.assertEqual(first.doc.to_dicts(), layout("Imported"))
        self.assertEqual(self.pkg.read_bytes(), self.bytes)
        self.assertEqual(
            first.resource_panel._roots[("pack", str(self.pkg))].childCount(), 1
        )
        saved = subprocess.check_output(
            [
                sys.executable,
                "-c",
                "import json,sys; from PySide6.QtCore import QSettings; "
                "s=QSettings(sys.argv[1],QSettings.IniFormat); "
                "print(json.dumps(s.value('known_layout_paths',[])))",
                str(self.root / "settings.ini"),
            ],
            encoding="utf-8",
        )
        self.assertIn(self.path, json.loads(saved))  # 另一个进程读取，不靠会话缓存
        second = (
            self.window()
        )  # new MainWindow + AssetResolver, not same-session remember
        self.assertIn(self.path, second.resolver.scan_layouts(str(self.pkg)))
        second._open_pack_layout(str(self.pkg), self.path)
        self.assertEqual(second.doc.to_dicts(), layout("Imported"))

    def test_saved_new_layout_reopens_in_fresh_window(self):
        self.pkg.write_bytes(pack_build.build_archive([raw("image/keep.bin", b"KEEP")]))
        first = self.window()
        with FlsPack(self.pkg) as pack:
            doc, _ = prepare_layout_import(
                pack, self.path, dlg_codec.dump_bytes(layout("New"))
            )
        doc.source_pack = (str(self.pkg), self.path)
        first._set_document(doc)
        out = self.root / "new.fls"
        self.assertTrue(first.write_pack_copy(str(out))["ok"])
        second = self.window()
        second.open_pack_file(str(out))
        self.assertIn(self.path, second.resolver.scan_layouts(str(out)))
        second._open_pack_layout(str(out), self.path)
        self.assertEqual(second.doc.to_dicts(), layout("New"))

    def test_failed_lookup_does_not_persist_or_add_ghost(self):
        window = self.window()
        with (
            mock.patch(
                "ui_editor.ui.main_window.QInputDialog.getText",
                return_value=("wrong/not-present.dlg", True),
            ),
            mock.patch("ui_editor.ui.main_window.QMessageBox.warning") as warning,
        ):
            window.open_pack_path(str(self.pkg))
        warning.assert_called_once()
        self.assertIsNone(window.doc)
        self.assertEqual(self.settings.value("known_layout_paths", []), [])
        self.assertEqual(
            window.resource_panel._roots[("pack", str(self.pkg))].childCount(), 0
        )

    def test_registration_paths_recognized_without_prior_settings(self):
        data = pack_build.build_archive(
            [
                raw("login/regform.dlg", dlg_codec.dump_bytes(layout("Form"))),
                raw("login/regterms.dlg", dlg_codec.dump_bytes(layout("Terms"))),
            ]
        )
        self.pkg.write_bytes(data)
        window = self.window()
        self.assertEqual(
            set(window.resolver.scan_layouts(str(self.pkg))),
            {"login/regform.dlg", "login/regterms.dlg"},
        )
