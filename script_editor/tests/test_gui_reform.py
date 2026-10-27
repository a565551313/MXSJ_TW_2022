"""The reformed UI: three menus' worth of real behaviour, no hidden steps.

These tests pin the promise the reform makes:

* the menu tree is exactly the small one (and the retired entries are gone);
* **写入原包** writes the package in one call, keeps a ``.bak`` and repoints the
  window;
* **生成新包** writes a new file and leaves the original untouched;
* a recovery draft is verified and bound **automatically** — no button, no
  "检查并采用" step;
* the two 语料 exports dump every entry.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from native_fixtures import minimal_pyc, script_fixture
from test_gui import QT_ERROR

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import Compiler
from script_editor.core.project.document import Binding
from script_editor.core.project.storage import CatalogRef
from script_editor.core.services.corpus_export import export_corpus

if not QT_ERROR:
    from PySide6.QtWidgets import QApplication, QFileDialog

    from script_editor.gui.window import Window


def sync_task(work, done, *, cancel=None, on_error=None, **_options):
    """Run a Window job inline, including its error path."""
    try:
        result = work()
    except Exception as exc:  # noqa: BLE001 - mirrors Window.task
        if on_error is not None:
            on_error(exc)
        return
    done(result)


COMPILE = "script_editor.core.services.workflow.compile_standard"


def fake_compile(seed=5):
    """Compile stub: the exact pyc a pinned CPython would have produced."""

    def compile_standard(_compiler, _source, _filename, destination, protected=()):
        pyc = minimal_pyc("py25", seed)
        destination.write_bytes(pyc)
        return hashlib.sha256(pyc).hexdigest()

    return compile_standard


class Package:
    """A synthetic script package plus the catalog that decodes it."""

    def __init__(self, root: Path, *, two_modules=True):
        raw, catalog = script_fixture(two_modules=two_modules)
        self.path = root / "script.fls"
        self.path.write_bytes(raw)
        self.before = raw
        self.digest = hashlib.sha256(raw).hexdigest()
        catalog_file = root / "catalog.json"
        catalog_file.write_text(json.dumps(catalog), encoding="utf-8")
        self.catalog = CatalogRef(
            self.path,
            self.digest,
            catalog_file,
            hashlib.sha256(catalog_file.read_bytes()).hexdigest(),
        )

    def bindings(self, source_root: Path, indexes=(0,)):
        result = []
        with ArchiveDocument(self.path) as archive:
            for index in indexes:
                source = source_root / f"module{index}.py"
                source.write_text(f"VALUE = {index}\n", encoding="utf-8")
                result.append(
                    Binding.associate(archive, index, source).__class__(
                        self.path,
                        self.digest,
                        "py25",
                        index,
                        archive.entries[index].identity,
                        source.resolve(),
                        "",
                        "",
                        "authored",
                        "",
                    )
                )
        return result


class CorpusExportTests(unittest.TestCase):
    """Core-level: the two exports work without any Qt."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mxscript-corpus-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)

    def test_decrypted_export_writes_pyc_and_a_manifest(self):
        with ArchiveDocument(self.package.path) as archive:
            manifest = export_corpus(
                archive, self.root / "dec", catalog=self.package.catalog
            )
        self.assertEqual(manifest["mode"], "decrypted")
        self.assertEqual(manifest["archive_sha256"], self.package.digest)
        self.assertEqual(manifest["entries_written"], 2)  # two decodable modules
        for entry in manifest["entries"]:
            path = self.root / "dec" / entry["file"]
            self.assertTrue(path.is_file())
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"]
            )
        written = json.loads(
            (self.root / "dec" / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(written["entries_total"], 3)

    def test_encrypted_export_keeps_the_stored_bytes(self):
        with ArchiveDocument(self.package.path) as archive:
            expected = archive.read_stored(0)
            manifest = export_corpus(
                archive, self.root / "enc", mode="encrypted", catalog=None
            )
        self.assertEqual(manifest["mode"], "encrypted")
        first = next(e for e in manifest["entries"] if e["index"] == 0)
        self.assertEqual((self.root / "enc" / first["file"]).read_bytes(), expected)

    def test_destination_must_not_exist(self):
        (self.root / "dec").mkdir()
        with ArchiveDocument(self.package.path) as archive:
            with self.assertRaisesRegex(ValueError, "尚不存在"):
                export_corpus(archive, self.root / "dec", catalog=None)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class MenuShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="mxscript-menu-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.window = Window(self.root)
        self.addCleanup(self._close)

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def menus(self):
        return {
            menu.title(): [action.text() for action in menu.actions()]
            for menu in self.window.menuBar().findChildren(type(self.window.menuBar()))
            if menu.title()
        }

    def test_menu_tree_is_the_small_one(self):
        titles = [
            action.text() for action in self.window.menuBar().actions()
        ]
        self.assertEqual(
            titles, ["文件", "语料", "编辑", "编码", "编译", "视图"]
        )

    def test_file_menu_order(self):
        file_menu = next(
            action.menu()
            for action in self.window.menuBar().actions()
            if action.text() == "文件"
        )
        texts = [a.text() for a in file_menu.actions() if a.text()]
        self.assertEqual(
            texts,
            [
                "新建 .py 文件…",
                "打开 .py 文件…",
                "打开 .py 目录…",
                "保存",
                "另存为…",
                "打开脚本文件…",
                "打开脚本目录…",
                "退出",
            ],
        )

    def test_corpus_edit_and_build_menus(self):
        menus = {
            action.text(): action.menu()
            for action in self.window.menuBar().actions()
        }
        self.assertEqual(
            [a.text() for a in menus["语料"].actions()],
            ["导出全量解密语料…", "导出全量加密语料…"],
        )
        self.assertEqual(
            [a.text() for a in menus["编译"].actions()],
            ["写入原包", "生成新包"],
        )
        edit = [a.text() for a in menus["编辑"].actions() if a.text()]
        self.assertEqual(
            edit,
            [
                "撤销",
                "恢复",
                "剪切",
                "复制",
                "粘贴",
                "查找…",
                "替换…",
                "在文件中查找…",
                "在文件中替换…",
            ],
        )
        self.assertEqual(
            [a.text() for a in menus["编码"].actions() if a.text()],
            [
                "选中文案 → Big5 字节…",
                "选中路径 → GBK 字节…",
                "字节字面量 → 可读对照（只读）…",
            ],
        )

    def test_toolbar_is_the_short_one(self):
        from PySide6.QtWidgets import QToolBar

        toolbar = self.window.findChild(QToolBar, "mainToolbar")
        texts = [
            action.iconText() or action.text() for action in toolbar.actions()
            if action.text()
        ]
        self.assertEqual(
            texts,
            [
                "打开",
                "目录",
                "保存",
                "撤销",
                "恢复",
                "查找",
                "写入原包",
                "生成新包",
                "检查编译器",
            ],
        )
        # The strict/loose switch is gone; the two verbs replaced it.
        self.assertFalse(
            [a for a in toolbar.actions() if "模式" in (a.text() or "")]
        )


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class OneClickWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mxscript-write-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = Package(self.root)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.errors = []
        patch.object(self.window, "fail", self.errors.append).start()
        self.addCleanup(patch.stopall)
        self.window.add_archive(ArchiveDocument(self.package.path))
        self.window.catalogs = [self.package.catalog]
        self.window.bindings = self.package.bindings(self.root)
        self.window.compilers["py25"] = Compiler(
            Path(sys.executable), "py25", "unit-test", 64, "t"
        )

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def run_sync(self):
        return patch.object(self.window, "task", side_effect=sync_task)

    def test_f5_writes_the_package_in_one_call(self):
        with (
            patch(COMPILE, fake_compile()),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch("script_editor.core.services.native_build.audit_standard"),
            self.run_sync(),
        ):
            self.window.write_in_place()
        self.assertEqual(self.errors, [])
        self.assertNotEqual(self.package.path.read_bytes(), self.package.before)
        backup = self.package.path.with_name(self.package.path.name + ".bak")
        self.assertEqual(backup.read_bytes(), self.package.before)
        self.assertIn("已写入原包", self.window.info.toPlainText())
        self.assertEqual(self.window.bindings[0].fingerprint, hashlib.sha256(
            self.package.path.read_bytes()
        ).hexdigest())

    def test_f6_writes_a_new_file_and_leaves_the_original_alone(self):
        new_file = self.root / "copy.fls"
        with (
            patch(COMPILE, fake_compile()),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch("script_editor.core.services.native_build.audit_standard"),
            patch.object(
                QFileDialog, "getSaveFileName", return_value=(str(new_file), "")
            ),
            self.run_sync(),
        ):
            self.window.generate_new_package()
        self.assertEqual(self.errors, [])
        self.assertEqual(self.package.path.read_bytes(), self.package.before)
        self.assertTrue(new_file.is_file())
        self.assertIn("已生成新包", self.window.info.toPlainText())

    def test_write_refuses_a_package_without_bound_source(self):
        self.window.bindings = []
        with self.run_sync():
            self.window.write_in_place()
        self.assertTrue(self.errors)
        self.assertIn("双击包内条目", str(self.errors[0]))
        self.assertEqual(self.package.path.read_bytes(), self.package.before)


@unittest.skipIf(bool(QT_ERROR), "GUI未执行：" + QT_ERROR)
class AutoAdoptTests(unittest.TestCase):
    """Opening a module verifies and binds it — the button is gone."""

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="mxscript-adopt-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        patcher = patch.dict(os.environ, {"MXSCRIPT_HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.package = Package(self.root, two_modules=False)
        self.window = Window(self.root)
        self.addCleanup(self._close)
        self.window.add_archive(ArchiveDocument(self.package.path))
        self.window.catalogs = [self.package.catalog]
        self.window.compilers["py25"] = Compiler(
            Path(sys.executable), "py25", "unit-test", 64, "t"
        )

    def _close(self):
        for i in range(self.window.tabs.count()):
            self.window.tabs.widget(i).editor.document().setModified(False)
        self.window.project_dirty = False
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def draft(self, text="# coding: utf-8\nVALUE = 1\n"):
        """A recovery-draft tab, exactly what opening an entry produces."""
        tab = self.window.add_source(
            self.root / ".script.fls.0.recovered.py",
            text=text,
            source_kind="recovered-draft",
            vm="py25",
        )
        tab.draft_saved = False
        report = SimpleNamespace(
            source=text,
            complete=True,
            archive=self.package.path,
            index=0,
            filename_hex=b"authored.py".hex(),
        )
        return tab, report

    def test_opened_module_is_verified_bound_and_writable(self):
        tab, report = self.draft()
        with (
            patch(COMPILE, fake_compile()),
            patch("script_editor.core.services.workflow.audit_standard"),
            patch.object(self.window, "task", side_effect=sync_task),
        ):
            with ArchiveDocument(self.package.path) as archive:
                self.window.auto_adopt(tab, archive, 0, report)
        self.assertEqual(len(self.window.bindings), 1)
        binding = self.window.bindings[0]
        self.assertTrue(binding.source.is_file())
        self.assertTrue(str(binding.source).startswith(str(self.home)), binding.source)
        self.assertEqual(tab.path, binding.source)
        self.assertEqual(tab.source_kind, "recovered-reviewed")
        self.assertIn("已自动校验并绑定", tab.mode_label.text())

    def test_verification_failure_leaves_an_editable_unbound_draft(self):
        tab, report = self.draft()
        with (
            patch(
                "script_editor.core.services.workflow.compile_standard",
                side_effect=ValueError("compiler exploded"),
            ),
            patch.object(self.window, "task", side_effect=sync_task),
        ):
            with ArchiveDocument(self.package.path) as archive:
                self.window.auto_adopt(tab, archive, 0, report)
        self.assertEqual(self.window.bindings, [])
        self.assertEqual(tab.source_kind, "recovered-draft")
        self.assertIn("未通过", tab.mode_label.text())

    def test_missing_compiler_says_so_instead_of_binding(self):
        tab, report = self.draft()
        self.window.compilers.clear()
        with ArchiveDocument(self.package.path) as archive:
            self.window.auto_adopt(tab, archive, 0, report)
        self.assertEqual(self.window.bindings, [])
        self.assertIn("检查编译器", tab.mode_label.text())
