from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from ..core.archives.document import ArchiveDocument
from ..core.compiler.profiles import PROFILES
from ..core.compiler.runner import bundled_compiler, compile_standard, inspect_compiler
from ..core.project.storage import ProjectState
from ..core.services.module_paths import index_script_paths
from ..core.services.package_selfcheck import verify_with_catalog
from ..core.services.workflow import Snapshot, prepare_build, publish_build
from .preview import BuildPreview


class BuildActions:
    def selected_archive(self):
        selected = self.selected()
        if selected:
            return selected[0]
        item = self.tree.currentItem()
        return item.data(0, Qt.ItemDataRole.UserRole + 1) if item else None

    def catalog_for(self, archive):
        return next((c for c in self.catalogs if c.archive == archive.path), None)

    def active_binding(self):
        selected, tab = self.selected(), self.tabs.currentWidget()
        if (
            not selected
            or not tab
            or tab.reference
            or tab.source_kind == "recovered-draft"
        ):
            return None
        archive, index = selected
        return next(
            (
                b
                for b in self.bindings
                if b.archive == archive.path
                and b.index == index
                and b.source == tab.path
                and b.vm == tab.vm.currentData()
            ),
            None,
        )

    def refresh_native_action(self, *_):
        if hasattr(self, "native_action"):
            binding = self.active_binding()
            self.native_action.setEnabled(
                bool(binding and binding.vm in self.compilers and not self.jobs)
            )

        if hasattr(self, "workspace_refresh"):
            self.workspace_refresh()

    def configure_catalog(self):
        archive = self.selected_archive()
        if not archive or archive.vm != "py25":
            self.fail("先选中script包或其条目；data包不需要五段XOR目录")
            return
        name, _ = QFileDialog.getOpenFileName(
            self, "选择与此原包匹配的XOR研究目录", "", "JSON (*.json)"
        )
        if not name:
            return
        path = Path(name).resolve()

        def prepare():
            # Decode before asking: the question used to be "do you trust this
            # file", which nobody can answer. Now the file is applied to every
            # allowed entry and the dialog reports what actually happened.
            return verify_with_catalog(archive, path)

        def complete(check):
            if not check.accepted:
                QMessageBox.warning(self, "这套参数解不开这个包", check.report())
                return
            ref = check.ref
            if (
                QMessageBox.question(
                    self,
                    "确认目录来源（自检结果见下，仍不等于源码可信）",
                    f"{check.report()}\n\n包：{ref.archive}\n目录：{ref.path}"
                    f"\nSHA256：{ref.sha256}\n确认以此参数继续？",
                    defaultButton=QMessageBox.StandardButton.No,
                )
                != QMessageBox.StandardButton.Yes
            ):
                return
            paths = check.paths
            self.catalogs = [c for c in self.catalogs if c.archive != ref.archive] + [
                ref
            ]
            check.apply(archive)
            self.module_names = {
                key: name
                for key, name in self.module_names.items()
                if key[0] != archive.path
            }
            self.module_names.update(
                ((archive.path, i), name) for i, name in paths.items()
            )
            self._navigation_revision = None
            self.workspace_refresh()
            self.project_dirty = True
            tab = self.tabs.currentWidget()
            if tab and tab.source_kind == "module-unavailable" and self.selected():
                self.open_package_module(reload=True)

        self.task(prepare, complete)

    def preview_native(self):
        try:
            tab = self.editable()
            binding = self.active_binding()
            if not binding:
                raise ValueError("选中条目必须与当前源码及VM明确关联")
            compiler = self.compilers.get(binding.vm)
            if not compiler:
                raise ValueError("请先检查/选择此VM的精确标准编译器")
            snapshot = Snapshot(
                binding,
                tab.editor.toPlainText(),
                tab.vm.currentData(),
                tab.reference,
                tab.editor.document().isModified(),
            )
            baseline = self.built_texts.get((binding.archive, binding.index))
            catalog = self.catalog_for(self.selected()[0])
            allow_resize = self.resize_entries()
            self.task(
                lambda: prepare_build(
                    snapshot,
                    compiler,
                    catalog,
                    baseline,
                    allow_resize=allow_resize,
                ),
                self.show_build_plan,
            )
        except Exception as exc:
            self.fail(exc)

    def show_build_plan(self, plan):
        if BuildPreview(plan, self).exec() != QDialog.DialogCode.Accepted:
            return
        name, _ = QFileDialog.getSaveFileName(
            self, "生成新包（必须是尚不存在的新名字）", "", "FLS (*.fls)"
        )
        if name:
            self.publish_plan(
                plan, Path(name if name.lower().endswith(".fls") else name + ".fls")
            )

    def publish_plan(self, plan, destination):
        try:
            tab = self.editable()
            if (
                self.active_binding() != plan.snapshot.binding
                or tab.editor.toPlainText() != plan.snapshot.text
                or tab.vm.currentData() != plan.snapshot.vm
            ):
                raise ValueError("清单已过期，请重新预编译确认")
            self.assert_writable_target(destination)
            state = ProjectState(tuple(self.bindings), tuple(self.catalogs))
            protected = tuple(a.path for a in self.archives) + tuple(
                self.tabs.widget(i).path for i in range(self.tabs.count())
            )
            self.task(
                lambda: self.publish_for_gui(plan, destination, state, protected),
                lambda result: self.adopt_build(plan, result),
            )
        except Exception as exc:
            self.fail(exc)

    @staticmethod
    def publish_for_gui(plan, destination, state, protected=()):
        report, state = publish_build(plan, destination, state, protected=protected)
        new = None
        try:
            new = ArchiveDocument(report.output)
            if new.fingerprint() != report.output_sha256:
                raise ValueError("新包发布后发生变化")
            index_script_paths(
                new, next((c for c in state.catalogs if c.archive == new.path), None)
            )
            return report, state, new, None
        except Exception as exc:
            if new is not None:
                new.close()
            return report, state, None, str(exc)

    def adopt_build(self, plan, result):
        report, state, new, error = result
        try:
            if error:
                raise ValueError(error)
            self.add_archive(new)
        except Exception as exc:
            if new is not None and new not in self.archives:
                new.close()
            self.info.setPlainText(
                f"新包已成功生成，但自动切换失败：{exc}\n"
                f"{report.output}\nSHA256 {report.output_sha256}\n"
                "旧项目与源码保留，可手动打开新包；不要重复覆盖输出。"
            )
            return
        old_path = plan.snapshot.binding.archive
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            origin = tab.recovery
            if origin is not None and origin.current_archive == old_path:
                tab.update_recovery_target(origin.continue_after_build(report, new))
        self.bindings, self.catalogs = list(state.bindings), list(state.catalogs)
        self.project_dirty = True
        self.built_texts = {
            (report.output.resolve() if path == old_path else path, index): text
            for (path, index), text in self.built_texts.items()
        }
        self.built_texts[(report.output.resolve(), plan.snapshot.binding.index)] = (
            plan.snapshot.text
        )
        # Remove old package tree/reader only AFTER new package is available.
        for i in range(self.tree.topLevelItemCount() - 1, -1, -1):
            root = self.tree.topLevelItem(i)
            archive = root.data(0, Qt.ItemDataRole.UserRole + 1)
            if archive and archive.path == old_path:
                self.tree.takeTopLevelItem(i)
                self.archives.remove(archive)
                archive.close()
        self.module_names = {
            key: name for key, name in self.module_names.items() if key[0] != old_path
        }
        root = next(
            self.tree.topLevelItem(i)
            for i in range(self.tree.topLevelItemCount())
            if self.tree.topLevelItem(i).data(0, Qt.ItemDataRole.UserRole + 1).path
            == report.output.resolve()
        )
        root.setExpanded(True)
        self.tree.setCurrentItem(root.child(plan.snapshot.binding.index))
        self.refresh_native_action()
        self.info.setPlainText(
            f"新包成功，已切换来源：{report.output}\nSHA256 {report.output_sha256}\n"
            f"替换 {report.modified_indexes}；"
            f"其余 {report.unchanged_entries} 条保持。\n"
            "源码编辑区/撤销不变，未自动保存.py；项目关联已更新，请保存项目。"
        )

    def select_compiler(self):
        try:
            vm = self.current().vm.currentData()
            name, _ = QFileDialog.getOpenFileName(
                self, f"选择标准CPython {PROFILES[vm].version}"
            )
            if name:
                self.task(
                    lambda: inspect_compiler(Path(name), vm), self.register_compiler
                )
        except Exception as exc:
            self.fail(exc)

    def register_compiler(self, compiler):
        audit = (
            f"整套文件审计：{len(compiler.bundle.files)} 文件；"
            f"清单SHA256 {compiler.bundle.manifest_sha256}"
            if compiler.bundle
            else "显式开发编译器：仅版本/魔数/EXE SHA，不是随包发行审计"
        )
        self.compilers[compiler.vm] = compiler
        self.refresh_native_action()
        self.info.setPlainText(
            f"{compiler.vm} / CPython {compiler.version} / "
            f"{compiler.bits}bit\n{compiler.executable}\n"
            f"SHA256 {compiler.sha256}\n{audit}\n仅编译，不执行目标模块。"
        )

    def initialize_compilers(self):
        """Check both pinned runtimes without requiring an open source tab.

        Failures stay in the diagnostic pane; reading/editing source remains
        available. Only successfully checked VMs become compile candidates.
        """
        root = self.runtime_root

        def check():
            ready, errors = [], {}
            for vm in PROFILES:
                try:
                    ready.append(bundled_compiler(vm, root))
                except (OSError, ValueError) as exc:
                    errors[vm] = str(exc)
            return ready, errors

        def complete(result):
            ready, errors = result
            self.compilers.clear()
            lines = ["双VM内置编译器启动自检（版本 / 魔数 / x86 / 整套SHA）"]
            for compiler in ready:
                self.compilers[compiler.vm] = compiler
                lines.append(
                    f"通过：{compiler.vm} / CPython {compiler.version} / "
                    f"{compiler.bits}bit\n{compiler.executable}"
                )
            for vm, error in errors.items():
                lines.append(f"不可用：{vm}：{error}")
            lines.append(
                "仅编译，不执行目标模块。完整编译/marshal验收："
                "运行bootstrap.py --check-only或检查内置编译器.bat。\n"
                "保存.py不等于写游戏包；原生写包仍需可信源码关联和清单确认。"
            )
            self.info.setPlainText("\n\n".join(lines))
            self.refresh_native_action()
            self.statusBar().showMessage(f"内置编译器自检：{len(ready)}/2可用")

        self.task(check, complete)

    def check_bundled(self):
        try:
            vm = self.current().vm.currentData()
            self.task(
                lambda: bundled_compiler(vm, self.runtime_root), self.register_compiler
            )
        except Exception as exc:
            self.fail(exc)

    def compile(self):
        try:
            tab = self.editable()
            compiler = self.compilers.get(tab.vm.currentData())
            if compiler is None:
                raise ValueError("当前VM没有已验证的编译器；请先检查内置或显式选择")
            name, _ = QFileDialog.getSaveFileName(
                self, "仅生成标准pyc；不能直接用于游戏", "", "Standard bytecode (*.pyc)"
            )
            if not name:
                return
            target = Path(name if name.lower().endswith(".pyc") else name + ".pyc")
            self.assert_writable_target(target)
            text = tab.editor.toPlainText()
            filename = str(tab.path)
            protected = tuple(
                [a.path for a in self.archives]
                + [self.tabs.widget(i).path for i in range(self.tabs.count())]
            )
            self.task(
                lambda: compile_standard(compiler, text, filename, target, protected),
                lambda digest: self.info.setPlainText(
                    f"标准.pyc编译成功（未写原生包）\nSHA256 {digest}"
                ),
            )
        except Exception as exc:
            self.fail(exc)
