"""编码切换、来源刷新与树右键导出；使用合成布局/包，不写客户端源包。"""
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QPoint, QSettings  # noqa: E402
from PySide6.QtGui import QColor, QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from ui_editor.core import dlg_codec, pack_build  # noqa: E402
from ui_editor.core.layout_import import prepare_layout_import  # noqa: E402
from ui_editor.core.mxhash import path_hash  # noqa: E402
from ui_editor.core.native_layout import encode_layout  # noqa: E402
from ui_editor.core.pack import FlsPack  # noqa: E402
from ui_editor.ui.main_window import MainWindow  # noqa: E402


def raw_text(text, encoding="gbk"):
    return dlg_codec.dump_bytes([{"sWidgetType": "CTextFrameEx", "sName": "text",
                                  "iWidth": 100, "iHeight": 30, "sText": text}],
                                text_encoding=encoding)


def package(path, entries):
    items = []
    for name, data in entries.items():
        eid = path_hash(name)
        stored = encode_layout(data, eid) if name.endswith(".dlg") else data
        items.append(pack_build.RawEntry(eid, 123, stored))
    path.write_bytes(pack_build.build_archive(sorted(items, key=lambda x: x.entry_id)))


class SourceActionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.settings = QSettings(str(self.root / "settings.ini"), QSettings.IniFormat)
        self.patch = mock.patch("ui_editor.ui.main_window.QSettings",
                                return_value=self.settings)
        self.patch.start()
        self.window = MainWindow()
        self.file = self.root / "test.dlg"
        self.data = raw_text("设置简体中文")
        self.file.write_bytes(self.data)
        self.pack = self.root / "test.fls"
        self.name = "dialog/cateroom.dlg"

    def tearDown(self):
        self.window.doc = None
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.patch.stop()
        self.tmp.cleanup()

    def choose(self, codec):
        self.window.change_text_encoding(codec)

    def checked(self):
        return [codec for codec, action in self.window._encoding_actions.items()
                if action.isChecked()]

    def text(self):
        return self.window.doc.roots[0].props["sText"]

    def open_pack(self):
        package(self.pack, {self.name: self.data})
        self.window.open_pack_file(str(self.pack))
        self.window._open_pack_layout(str(self.pack), self.name)

    def test_toolbar_choices_and_refresh(self):
        self.assertEqual(list(self.window._encoding_actions),
                         ["big5", "gbk", "utf-8"])
        self.assertEqual(self.checked(), ["big5"])
        self.assertIn(self.window._act_reload, self.window._toolbar.actions())
        self.assertEqual(self.window._act_reload.shortcut().toString(), "F5")

    def test_switch_redecodes_original_bytes_and_does_not_write(self):
        self.window.open_layout_file(str(self.file))
        self.assertNotEqual(self.text(), "设置简体中文")
        self.choose("gbk")
        self.assertEqual(self.text(), "设置简体中文")
        self.assertFalse(self.window.doc.dirty)
        self.choose("big5")
        self.choose("gbk")
        self.assertEqual(self.text(), "设置简体中文")
        self.assertEqual(self.file.read_bytes(), self.data)
        self.assertEqual(self.window.props_panel._widget, None)

    def test_pack_switch_and_selected_codec_on_next_open(self):
        self.open_pack()
        before = self.pack.read_bytes()
        self.choose("gbk")
        self.assertEqual(self.text(), "设置简体中文")
        self.window.open_layout_file(str(self.file))
        self.assertEqual(self.text(), "设置简体中文")
        self.assertEqual(self.pack.read_bytes(), before)

    def test_switch_cancel_retains_document_history_and_choice(self):
        self.window.open_layout_file(str(self.file))
        old = self.window.doc
        old.dirty = True
        with mock.patch.object(self.window, "_confirm_discard", return_value=False):
            self.choose("gbk")
        self.assertIs(self.window.doc, old)
        self.assertTrue(old.dirty)
        self.assertEqual(self.checked(), ["big5"])

    def test_unsaved_new_document_switch_is_not_lost(self):
        self.window.new_layout()
        old = self.window.doc
        with (mock.patch.object(self.window, "_confirm_discard", return_value=True),
              mock.patch("ui_editor.ui.source_actions.QMessageBox.warning") as warn):
            self.choose("gbk")
        self.assertIs(self.window.doc, old)
        self.assertEqual(self.checked(), ["big5"])
        warn.assert_called_once()

    def test_loose_refresh_reloads_file_list_image_and_style(self):
        self.choose("gbk")
        self.window.open_layout_dir(str(self.root))
        self.window.open_layout_file(str(self.file))
        image = QImage(2, 2, QImage.Format_RGBA8888)
        image.fill(QColor("red"))
        image.save(str(self.root / "pic.png"))
        self.window.resolver.fetch_image("pic.png")
        self.window.resolver.fetch_bytes("new.bin")  # 缓存未命中也要失效
        image.fill(QColor("blue"))
        image.save(str(self.root / "pic.png"))
        (self.root / "new.bin").write_bytes(b"new")
        self.file.write_bytes(raw_text("刷新后的内容"))
        (self.root / "added.dlg").write_bytes(raw_text("新增"))
        (self.root / "ui.lst").write_bytes(b"[Font]\nArial 17 400 0\n")
        self.window.refresh_sources()
        self.assertEqual(self.text(), "刷新后的内容")
        self.assertEqual(self.window.resolver.fetch_image("pic.png")[0]
                         .pixelColor(0, 0), QColor("blue"))
        self.assertEqual(self.window.resolver.fetch_bytes("new.bin"), b"new")
        self.assertEqual(self.window.styles.fonts[0].size, 17)
        root = self.window.resource_panel._roots[("dir", str(self.root))]
        self.assertEqual(root.childCount(), 2)
        (self.root / "added.dlg").unlink()
        self.window.refresh_sources()
        root = self.window.resource_panel._roots[("dir", str(self.root))]
        self.assertEqual(root.childCount(), 1)

    def test_refresh_reopens_pack_index_not_only_cached_payload(self):
        self.choose("gbk")
        self.open_pack()
        self.window.resolver.fetch_bytes("new.bin")
        self.window.resolver.stage_image("staged.png", b"keep")
        package(self.pack, {self.name: raw_text("包已更新"), "new.bin": b"fresh"})
        self.window.refresh_sources()
        self.assertEqual(self.text(), "包已更新")
        self.assertEqual(self.window.resolver.fetch_bytes("new.bin"), b"fresh")
        self.assertEqual(self.window.resolver.staged_images(), {"staged.png": b"keep"})

    def test_refresh_resource_directory_discovers_new_pack(self):
        self.window.open_resource_dir(str(self.root))
        package(self.pack, {self.name: self.data})
        self.window.refresh_sources()
        self.assertIsNotNone(self.window.resolver.pack_for(str(self.pack)))
        self.assertIn(("pack", str(self.pack)), self.window.resource_panel._roots)

    def test_refresh_cancel_and_read_failure_keep_old_state(self):
        self.window.open_layout_file(str(self.file))
        old, resolver = self.window.doc, self.window.resolver
        old.dirty = True
        with mock.patch.object(self.window, "_confirm_discard", return_value=False):
            self.window.refresh_sources()
        self.assertIs(self.window.doc, old)
        self.assertIs(self.window.resolver, resolver)
        self.file.write_bytes(b"not a layout")
        with (mock.patch.object(self.window, "_confirm_discard", return_value=True),
              mock.patch("ui_editor.ui.source_actions.QMessageBox.warning") as warn):
            self.window.refresh_sources()
        self.assertIs(self.window.doc, old)
        self.assertIs(self.window.resolver, resolver)
        warn.assert_called_once()

    def test_save_uses_selected_codec_and_updates_raw_snapshot(self):
        self.choose("gbk")
        self.window.open_layout_file(str(self.file))
        self.window.doc.roots[0].props["sText"] = "已经编辑保存"
        out = self.root / "saved.dlg"
        with mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog.exec",
                return_value=1):
            self.assertTrue(self.window.save_as(str(out)))
        self.assertEqual(dlg_codec.parse_bytes(out.read_bytes(), text_encoding="gbk")
                         [0][0]["sText"], "已经编辑保存")
        self.choose("big5")
        self.choose("gbk")
        self.assertEqual(self.text(), "已经编辑保存")
        self.assertEqual(self.file.read_bytes(), self.data)

    def test_loose_save_failure_keeps_existing_target(self):
        self.choose("gbk")
        self.window.open_layout_file(str(self.file))
        out = self.root / "existing.dlg"
        old = b"old target bytes"
        out.write_bytes(old)
        with mock.patch(
                "ui_editor.ui.save_workflows.SaveReviewDialog.exec",
                return_value=1,
        ):
            with mock.patch(
                    "ui_editor.ui.save_workflows.os.replace",
                    side_effect=OSError("publish failed"),
            ):
                with mock.patch(
                        "ui_editor.ui.workflows.QMessageBox.warning",
                ):
                    self.assertFalse(self.window.save_as(str(out)))
        self.assertEqual(out.read_bytes(), old)

    def test_pack_save_roundtrip_with_gbk_and_utf8(self):
        for codec, text in (("gbk", "设置简体中文"), ("utf-8", "简体繁體🙂")):
            with self.subTest(codec=codec):
                self.window.doc = None
                self.choose(codec)
                self.data = raw_text(text, codec)
                self.open_pack()
                # open_pack_file 已挂载同名包时不重开；明确刷新后再验。
                self.window.refresh_sources()
                out = self.root / (codec + ".fls")
                report = self.window.write_pack_copy(str(out))
                self.assertTrue(report["ok"], report)
                self.assertEqual(self.text(), text)
                self.assertEqual(self.window.doc.source_bytes,
                                 self.window.resolver.fetch_pack_dlg_bytes(
                                     str(out), self.name))

    def test_import_precheck_uses_selected_encoding(self):
        package(self.pack, {self.name: self.data})
        with FlsPack(self.pack) as pack:
            doc, replacing = prepare_layout_import(
                pack, self.name, raw_text("简体导入"), text_encoding="gbk")
        self.assertTrue(replacing)
        self.assertEqual(doc.text_encoding, "gbk")
        self.assertEqual(doc.to_dicts()[0]["sText"], "简体导入")

    def test_export_loose_and_pack_verbatim_without_opening(self):
        self.open_pack()
        old = self.window.doc
        for source in (("file", str(self.file)), ("pack", str(self.pack), self.name)):
            with self.subTest(source=source):
                out = self.root / "export.dlg"
                with mock.patch(
                        "ui_editor.ui.source_actions.QFileDialog.getSaveFileName",
                        return_value=(str(out), "")):
                    self.window.export_layout(source)
                self.assertEqual(out.read_bytes(), self.data)
                self.assertIs(self.window.doc, old)

    def test_export_uses_clicked_pack_not_other_same_named_layout(self):
        self.open_pack()
        other = self.root / "other.fls"
        package(other, {self.name: raw_text("另一个包")})
        self.window.open_pack_file(str(other))
        out = self.root / "export.dlg"
        with mock.patch("ui_editor.ui.source_actions.QFileDialog.getSaveFileName",
                        return_value=(str(out), "")):
            self.window.export_layout(("pack", str(other), self.name))
        self.assertEqual(out.read_bytes(), raw_text("另一个包"))

    def test_export_cancel_and_source_alias_protected(self):
        self.window.open_layout_dir(str(self.root))
        before = self.file.read_bytes()
        alias = self.root / "alias.dlg"
        os.link(self.file, alias)
        for target in ("", str(self.file), str(alias)):
            with (mock.patch("ui_editor.ui.source_actions.QFileDialog.getSaveFileName",
                             return_value=(target, "")),
                  mock.patch(
                      "ui_editor.ui.source_actions.QMessageBox.warning") as warn):
                self.window.export_layout(("file", str(self.file)))
                self.assertEqual(warn.call_count, int(bool(target)))
        self.assertEqual(self.file.read_bytes(), before)

    def test_leaf_context_menu_emits_export_and_missing_is_disabled(self):
        self.open_pack()
        panel = self.window.resource_panel
        leaf = panel._roots[("pack", str(self.pack))].child(0)
        seen = []
        panel.export_layout_requested.disconnect(self.window.export_layout)
        panel.export_layout_requested.connect(seen.append)
        with (mock.patch.object(panel._tree, "itemAt", return_value=leaf),
              mock.patch("ui_editor.ui.resource_menu.QMenu") as menu):
            export, replace = mock.Mock(), mock.Mock()
            menu.return_value.addAction.side_effect = [export, replace]
            panel._show_context_menu(QPoint())
            self.assertEqual(
                [call.args[0]
                 for call in menu.return_value.addAction.call_args_list],
                ["导出布局…", "替换布局…"])
            export.triggered.connect.call_args.args[0]()
        self.assertEqual(seen, [("pack", str(self.pack), self.name)])
        font = leaf.font(0)
        font.setItalic(True)
        leaf.setFont(0, font)
        with (mock.patch.object(panel._tree, "itemAt", return_value=leaf),
              mock.patch("ui_editor.ui.resource_menu.QMenu") as menu):
            export, replace = mock.Mock(), mock.Mock()
            menu.return_value.addAction.side_effect = [export, replace]
            panel._show_context_menu(QPoint())
            # 包内缺失的布局：导出与替换都置灰（替换也无从谈起）
            export.setEnabled.assert_called_with(False)
            replace.setEnabled.assert_called_with(False)

    def test_confirmed_switch_discards_edits_but_uses_source_snapshot(self):
        self.window.open_layout_file(str(self.file))
        self.window.doc.roots[0].props["sText"] = "未保存编辑"
        self.window.doc.dirty = True
        with mock.patch.object(self.window, "_confirm_discard", return_value=True):
            self.choose("gbk")
        self.assertEqual(self.text(), "设置简体中文")
        self.assertFalse(self.window.doc.dirty)
        self.assertEqual(self.file.read_bytes(), self.data)

    def test_switch_parse_failure_rolls_back_choice_and_state(self):
        self.window.open_layout_file(str(self.file))
        old = self.window.doc
        old.source_bytes = b"invalid layout"
        with mock.patch("ui_editor.ui.source_actions.QMessageBox.warning") as warn:
            self.choose("gbk")
        self.assertIs(self.window.doc, old)
        self.assertEqual(self.checked(), ["big5"])
        self.assertEqual(self.window.resolver.text_encoding, "big5")
        warn.assert_called_once()

    def test_export_ignores_unsaved_edits_and_keeps_dirty_state(self):
        self.choose("gbk")
        self.window.open_layout_file(str(self.file))
        old = self.window.doc
        old.roots[0].props["sText"] = "未保存的内容"
        old.dirty = True
        out = self.root / "export.dlg"
        with mock.patch("ui_editor.ui.source_actions.QFileDialog.getSaveFileName",
                        return_value=(str(out), "")):
            self.window.export_layout(("file", str(self.file)))
        self.assertEqual(out.read_bytes(), self.data)
        self.assertTrue(old.dirty)
        self.assertIs(self.window.doc, old)
        self.assertEqual(self.text(), "未保存的内容")

    def test_pending_import_switch_keeps_original_import_bytes_and_pending_flag(self):
        package(self.pack, {"unrelated.bin": b"keep"})
        self.window.open_pack_file(str(self.pack))
        self.window.resolver.text_encoding = "gbk"
        self.window._restore_encoding_choice()
        with FlsPack(self.pack) as pack:
            doc, _ = prepare_layout_import(
                pack, self.name, self.data, text_encoding="gbk")
        doc.source_pack = (str(self.pack), self.name)
        self.window._set_document(doc)
        with mock.patch.object(self.window, "_confirm_discard", return_value=True):
            self.choose("big5")
            self.choose("gbk")
        self.assertEqual(self.text(), "设置简体中文")
        self.assertTrue(self.window.doc.pending_pack_import)
        self.assertIsNotNone(self.window.resource_panel._pending_item)

    def test_corrupt_pack_refresh_does_not_publish_half_reloaded_state(self):
        self.open_pack()
        old, resolver = self.window.doc, self.window.resolver
        self.pack.write_bytes(b"corrupt pack")
        with mock.patch("ui_editor.ui.source_actions.QMessageBox.warning") as warn:
            self.window.refresh_sources()
        self.assertIs(self.window.doc, old)
        self.assertIs(self.window.resolver, resolver)
        self.assertTrue(resolver.pack_for(str(self.pack)).contains(self.name))
        warn.assert_called_once()

    def test_export_protects_image_hardlink_even_outside_source_directory(self):
        self.window.open_layout_file(str(self.file))
        image = self.root / "asset.png"
        image.write_bytes(b"source image")
        with tempfile.TemporaryDirectory() as outside:
            alias = Path(outside) / "export.dlg"
            os.link(image, alias)
            with (mock.patch("ui_editor.ui.source_actions.QFileDialog.getSaveFileName",
                             return_value=(str(alias), "")),
                  mock.patch(
                      "ui_editor.ui.source_actions.QMessageBox.warning") as warn):
                self.window.export_layout(("file", str(self.file)))
            warn.assert_called_once()
            self.assertEqual(image.read_bytes(), b"source image")
