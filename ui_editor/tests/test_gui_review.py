"""修改前护栏、删除子树、静态定位与保存清单；仅合成布局/包。"""

from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
try:
    from PySide6.QtWidgets import QApplication, QDialogButtonBox, QMessageBox

    from ui_editor.ui.main_window import MainWindow
    from ui_editor.ui.save_review import SaveReviewDialog

    HAS_QT = True
except ImportError:
    HAS_QT = False

from ui_editor.core import dlg_codec, pack_build
from ui_editor.core.diagnostics import Diagnostic
from ui_editor.core.model import LayoutDocument
from ui_editor.core.mxhash import mx_hash
from ui_editor.core.script_index import LayoutLink, ObjectRef


@unittest.skipUnless(HAS_QT, "PySide6 / system graphics libraries unavailable")
class TestGuiReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.window = MainWindow()
        self.window._set_document(
            LayoutDocument.from_dicts(
                [
                    {
                        "sWidgetType": "CMainFrame",
                        "sName": "root",
                        "iWidth": 100,
                        "iHeight": 100,
                        "lChildren": [
                            {
                                "sWidgetType": "CTextFrame",
                                "sName": "kid",
                                "iWidth": 20,
                                "iHeight": 20,
                                "sText": "測試",
                            }
                        ],
                    }
                ],
                None,
            )
        )
        self.link = LayoutLink(
            "ui/test.dlg",
            objects={"kid": [ObjectRef("controller", 10, "Panel", "Init", True)]},
        )
        self.link_patch = mock.patch.object(
            self.window, "_script_link", return_value=self.link
        )
        self.link_patch.start()

    def tearDown(self):
        self.link_patch.stop()
        if self.window.doc:
            self.window.doc.dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.temp.cleanup()

    def kid(self):
        return self.window.doc.roots[0].children[0]

    def test_rename_cancel_happens_before_mutation_and_history(self):
        w = self.window
        kid = self.kid()
        w._select_widget(kid)
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question", return_value=QMessageBox.No
        ) as question:
            self.assertFalse(w.props_panel._commit("sName", "renamed"))
        self.assertEqual(kid.name, "kid")
        self.assertFalse(w.doc.dirty)
        self.assertFalse(w.doc.can_undo)
        self.assertEqual(w.doc.changes(), [])
        self.assertIn("entry 10", question.call_args.args[2])
        self.assertIn("位置锚点", question.call_args.args[2])
        self.assertEqual(question.call_args.args[-1], QMessageBox.No)

    def test_confirmed_rename_is_undoable_but_index_is_read_only(self):
        w = self.window
        kid = self.kid()
        w._select_widget(kid)
        index_before = copy.deepcopy(self.link)
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ):
            self.assertTrue(w.props_panel._commit("sName", "renamed"))
        self.assertEqual(kid.name, "renamed")
        self.assertEqual(self.link, index_before)
        self.assertTrue(w.doc.can_undo)
        w.undo()
        self.assertEqual(self.kid().name, "kid")
        self.assertFalse(w.doc.dirty)
        w.redo()
        self.assertEqual(self.kid().name, "renamed")

    def test_add_property_cannot_bypass_rename_guard(self):
        w = self.window
        w._select_widget(self.kid())
        panel = w.props_panel
        panel._new_key.setText("sName")
        panel._new_value.setText("renamed")
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question", return_value=QMessageBox.No
        ) as question:
            panel._add_property()
        self.assertEqual(self.kid().name, "kid")
        self.assertFalse(w.doc.can_undo)
        question.assert_called_once()
        panel._remove_property("sName")  # 核心字段不能删掉绕过护栏
        self.assertEqual(self.kid().name, "kid")

    def test_duplicate_or_nonstring_name_is_rejected(self):
        w = self.window
        w._select_widget(self.kid())
        with (
            mock.patch("ui_editor.ui.main_window.QMessageBox.warning") as warning,
            mock.patch("ui_editor.ui.main_window.QMessageBox.question") as question,
        ):
            self.assertFalse(w.props_panel._commit("sName", "root"))
            self.assertFalse(w.props_panel._commit("sName", 42))
        self.assertEqual(warning.call_count, 2)
        question.assert_not_called()
        self.assertEqual(self.kid().name, "kid")

    def test_delete_parent_warns_about_referenced_descendant_and_cancel_is_clean(self):
        w = self.window
        before = w.doc.to_dicts()
        w._select_widget(w.doc.roots[0])
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question", return_value=QMessageBox.No
        ) as question:
            w.delete_selected()
        self.assertIn("kid", question.call_args.args[2])
        self.assertIn("子树", question.call_args.args[2])
        self.assertEqual(w.doc.to_dicts(), before)
        self.assertFalse(w.doc.can_undo)
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question",
            return_value=QMessageBox.Yes,
        ):
            w.delete_selected()
        self.assertEqual(w.doc.roots, [])
        w.undo()
        self.assertEqual(w.doc.to_dicts(), before)
        self.assertFalse(w.doc.dirty)

    def test_referenced_leaf_delete_warns_without_children(self):
        w = self.window
        w._select_widget(self.kid())
        with mock.patch(
            "ui_editor.ui.main_window.QMessageBox.question", return_value=QMessageBox.No
        ) as question:
            w.delete_selected()
        question.assert_called_once()
        self.assertEqual(len(w.doc.all_widgets()), 2)

    def test_diagnostics_locate_by_path_and_stale_results_do_not_locate(self):
        w = self.window
        w.doc.roots[0].name = "kid"
        w.run_diagnostics()
        panel = w.diagnostics_panel
        row = next(
            panel.table.topLevelItem(i)
            for i in range(panel.table.topLevelItemCount())
            if panel.table.topLevelItem(i).text(1) == "DUPLICATE_NAME"
            and panel.table.topLevelItem(i).text(2).startswith("1/1")
        )
        panel._locate(row, 0)
        self.assertIs(w._selected, self.kid())
        panel.mark_stale()
        with mock.patch.object(w, "_select_widget") as select:
            panel._locate(row, 0)
        select.assert_not_called()

    def test_session_ignore_does_not_hide_encoding_or_save_review_risks(self):
        panel = self.window.diagnostics_panel
        panel.set_issues(
            [
                Diagnostic("警告", "OUTSIDE_PARENT", (0, 0), "iX", "intentional"),
                Diagnostic("错误", "ENCODING", (0, 0), "sText", "bad encoding"),
            ]
        )
        panel.table.topLevelItem(0).setSelected(True)
        panel._ignore_selected()
        self.assertEqual(panel.table.topLevelItemCount(), 1)
        panel.table.topLevelItem(0).setSelected(True)
        panel._ignore_selected()
        self.assertEqual(panel.table.topLevelItemCount(), 1)
        panel._restore()
        self.assertEqual(panel.table.topLevelItemCount(), 2)
        self.kid().props["sText"] = "😀"
        dialog = SaveReviewDialog(
            str(self.root / "layout.dlg"),
            [],
            self.window._layout_diagnostics(),
            [],
            to_pack=False,
            parent=self.window,
        )
        buttons = dialog.findChild(QDialogButtonBox)
        self.assertFalse(buttons.button(QDialogButtonBox.Save).isEnabled())
        self.assertTrue(buttons.button(QDialogButtonBox.Cancel).isEnabled())
        dialog.deleteLater()

    def test_cancel_save_as_keeps_source_baseline_history_and_staged(self):
        w = self.window
        w.doc.source_path = str(self.root / "old.dlg")
        self.kid().props["sText"] = "修改"
        w._on_property_changed(self.kid(), "sText")
        w.resolver.stage_image("images/unused.png", b"pending")
        changes = w.doc.changes()
        target = self.root / "new.dlg"
        with mock.patch(
            "ui_editor.ui.main_window.SaveReviewDialog.exec", return_value=0
        ):
            self.assertFalse(w.save_as(str(target)))
        self.assertFalse(target.exists())
        self.assertEqual(w.doc.source_path, str(self.root / "old.dlg"))
        self.assertTrue(w.doc.dirty)
        self.assertTrue(w.doc.can_undo)
        self.assertEqual(w.doc.changes(), changes)
        self.assertEqual(w.resolver.staged_images(), {"images/unused.png": b"pending"})

    def test_failed_loose_save_keeps_baseline_and_unknown_fields(self):
        w = self.window
        self.kid().props["iFuture"] = 42
        w._on_property_changed(self.kid(), "iFuture")
        changes = w.doc.changes()
        with (
            mock.patch(
                "ui_editor.ui.main_window.SaveReviewDialog.exec", return_value=1
            ),
            mock.patch("ui_editor.ui.main_window.QMessageBox.warning"),
        ):
            self.assertFalse(w.save_as(str(self.root / "missing" / "new.dlg")))
        self.assertEqual(w.doc.changes(), changes)
        self.assertTrue(w.doc.dirty)
        self.assertIsNone(w.doc.source_path)

    def test_successful_loose_save_establishes_review_baseline(self):
        w = self.window
        self.kid().props["iFuture"] = 42
        w._on_property_changed(self.kid(), "iFuture")
        target = self.root / "new.dlg"
        with mock.patch(
            "ui_editor.ui.main_window.SaveReviewDialog.exec", return_value=1
        ):
            self.assertTrue(w.save_as(str(target)))
        self.assertEqual(w.doc.changes(), [])
        self.assertFalse(w.doc.dirty)
        self.assertEqual(
            dlg_codec.parse_bytes(target.read_bytes())[0], w.doc.to_dicts()
        )
        w.undo()
        self.assertTrue(w.doc.dirty)
        self.assertTrue(w.doc.changes())

    def test_pack_review_previews_added_replaced_unused_before_writing(self):
        w = self.window
        src, target = self.root / "source.fls", self.root / "new.fls"
        layout_path = "ui/test.dlg"
        plain = dlg_codec.dump_bytes(w.doc.to_dicts())
        raw = pack_build.build_archive(
            [
                pack_build.RawEntry(mx_hash(layout_path.encode()), 7, plain),
                pack_build.RawEntry(mx_hash(b"images/old.png"), 7, b"old"),
            ]
        )
        src.write_bytes(raw)
        w.resolver.mount_pack(src)
        w.doc.source_pack = (str(src), layout_path)
        self.kid().props["sFileName"] = "images/new.png"
        self.kid().props["sBgFileName"] = "images/old.png"
        w.resolver.stage_image("images/new.png", b"new")
        w.resolver.stage_image("images/old.png", b"replace")
        w.resolver.stage_image("images/unused.png", b"unused")
        w._on_property_changed(self.kid(), "sFileName")
        changes = w.doc.changes()
        with mock.patch(
            "ui_editor.ui.main_window.SaveReviewDialog", autospec=True
        ) as dlg:
            dlg.return_value.exec.return_value = 0
            self.assertFalse(w._confirm_save_review(str(target), to_pack=True))
            image_plan = dlg.call_args.args[3]
        self.assertEqual(
            {kind for kind, _name, _size in image_plan},
            {"新增图片", "替换图片", "未引用，跳过并保留待入包"},
        )
        self.assertEqual(w.doc.changes(), changes)
        self.assertEqual(len(w.resolver.staged_images()), 3)
        self.assertEqual(src.read_bytes(), raw)
        self.assertFalse(target.exists())

    def test_pack_dialog_cancel_never_calls_writer(self):
        w = self.window
        src, target = self.root / "source.fls", self.root / "new.fls"
        plain = dlg_codec.dump_bytes(w.doc.to_dicts())
        src.write_bytes(
            pack_build.build_archive(
                [pack_build.RawEntry(mx_hash(b"ui/test.dlg"), 7, plain)]
            )
        )
        w.doc.source_pack = (str(src), "ui/test.dlg")
        with (
            mock.patch(
                "ui_editor.ui.main_window.QFileDialog.getSaveFileName",
                return_value=(str(target), ""),
            ),
            mock.patch(
                "ui_editor.ui.main_window.SaveReviewDialog.exec", return_value=0
            ),
            mock.patch.object(w, "write_pack_copy") as writer,
        ):
            w.save_to_pack_dialog()
        writer.assert_not_called()
        self.assertFalse(target.exists())

    def test_save_review_states_how_the_target_entry_is_written(self):
        """保存清单必须明说目标条目会被怎么写（P2-1：连没改也会重写）。"""
        w = self.window
        src, target = self.root / "source.fls", self.root / "new.fls"
        plain = dlg_codec.dump_bytes(w.doc.to_dicts())
        # 源包里是**明文**存储的同一份布局 → 本次保存应报「迁移」
        src.write_bytes(pack_build.build_archive(
            [pack_build.RawEntry(mx_hash(b"ui/test.dlg"), 7, plain)]))
        w.doc.source_pack = (str(src), "ui/test.dlg")
        with mock.patch("ui_editor.ui.main_window.SaveReviewDialog",
                        autospec=True) as dlg:
            dlg.return_value.exec.return_value = 0
            w._confirm_save_review(str(target), to_pack=True)
            notice = dlg.call_args.kwargs["layout_notice"]
        self.assertTrue(notice.startswith("目标条目："), notice)
        self.assertIn("迁移为原生路径密钥", notice)

    def test_save_review_reports_layout_rewrite_for_foreign_plain(self):
        """源包里的布局不是编辑器版式时，清单要写明「版式重写」。"""
        w = self.window
        src, target = self.root / "source2.fls", self.root / "new2.fls"
        foreign = (
            b"# -*- coding: gbk -*-\n\nUI_INFO = [\n"
            b'    {"sName": "root", "sWidgetType": "CMainFrame",'
            b' "iWidth": 100, "iHeight": 100, "lChildren": ['
            b'{"sName": "kid", "sWidgetType": "CTextFrame"}]},\n]\n')
        src.write_bytes(pack_build.build_archive(
            [pack_build.RawEntry(mx_hash(b"ui/test.dlg"), 7, foreign)]))
        w.doc.source_pack = (str(src), "ui/test.dlg")
        with mock.patch("ui_editor.ui.main_window.SaveReviewDialog",
                        autospec=True) as dlg:
            dlg.return_value.exec.return_value = 0
            w._confirm_save_review(str(target), to_pack=True)
            notice = dlg.call_args.kwargs["layout_notice"]
        self.assertIn("版式按编辑器序列化重写", notice)

    def test_programmatic_pack_write_rejects_encoding_before_publish(self):
        w = self.window
        src = self.root / "source.fls"
        plain = dlg_codec.dump_bytes(w.doc.to_dicts())
        original = pack_build.build_archive(
            [pack_build.RawEntry(mx_hash(b"ui/test.dlg"), 7, plain)]
        )
        src.write_bytes(original)
        w.doc.source_pack = (str(src), "ui/test.dlg")
        out_dir = self.root / "outputs"
        out_dir.mkdir()
        target = out_dir / "previous.fls"
        target.write_bytes(b"previous-output")
        self.kid().props["sText"] = "😀"
        w._on_property_changed(self.kid(), "sText")
        changes = w.doc.changes()
        with self.assertRaisesRegex(ValueError, "编码"):
            w.write_pack_copy(str(target))
        self.assertEqual(target.read_bytes(), b"previous-output")
        self.assertEqual(src.read_bytes(), original)
        self.assertEqual(w.doc.changes(), changes)
        self.assertTrue(w.doc.can_undo)
        self.assertEqual(w.doc.source_pack, (str(src), "ui/test.dlg"))

    def test_unknown_image_path_field_cannot_bypass_gbk_write_guard(self):
        w = self.window
        src = self.root / "source.fls"
        src.write_bytes(
            pack_build.build_archive(
                [
                    pack_build.RawEntry(
                        mx_hash(b"ui/test.dlg"),
                        7,
                        dlg_codec.dump_bytes(w.doc.to_dicts()),
                    )
                ]
            )
        )
        w.doc.source_pack = (str(src), "ui/test.dlg")
        name = "images/😀.png"
        self.kid().props["sUnknownPath"] = name
        w.resolver.stage_image(name, b"pending")
        target = self.root / "new.fls"
        with self.assertRaisesRegex(ValueError, "GBK"):
            w.write_pack_copy(str(target))
        self.assertFalse(target.exists())
        self.assertEqual(w.resolver.staged_images(), {name: b"pending"})
