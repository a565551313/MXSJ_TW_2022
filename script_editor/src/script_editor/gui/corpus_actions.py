"""语料导出：把一个包的全部条目倒成一个目录。

Nothing is executed and nothing is written back into a package; the two menu
entries differ only in whether the stored bytes are decrypted first.

The older import/verify entry points are kept as internal APIs (the corpus
import path is still used by recovery), but they are no longer exposed in the
menu — the visible 语料 menu is two exports.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from threading import Event

from PySide6.QtWidgets import QFileDialog, QMessageBox

from ..core.project.storage import CatalogRef
from ..core.services.corpus_manifest import load_corpus
from ..core.services.corpus_recovery import corpus_report, verified_parameters
from ..core.services.files import publish_new


class CorpusActions:
    def assert_writable_target(self, path):
        if any(
            Path(path).resolve().is_relative_to(r.path.parent.parent.resolve())
            for r in self.corpus_refs
        ):
            raise ValueError("语料目录只读；请另存到工作目录")

    def export_corpus(self, *, encrypted):
        """导出全量（加密/解密）语料——整个包，逐条写文件 + manifest。"""
        if self.jobs:
            return
        archive = self.selected_archive()
        if archive is None:
            self.fail("先在左侧选一个包，再导出语料")
            return
        label = "加密" if encrypted else "解密"
        name = QFileDialog.getExistingDirectory(
            self, f"选择导出位置（会在其中新建 corpus-{label} 目录）"
        )
        if not name:
            return
        destination = Path(name) / f"corpus-{'encrypted' if encrypted else 'decrypted'}"
        try:
            self.assert_writable_target(destination)
            if destination.exists():
                raise ValueError(f"{destination.name} 已存在；请换个目录或先移走它")
        except (OSError, ValueError) as exc:
            self.fail(exc)
            return
        catalog = self.catalog_for(archive)
        cancel = Event()

        def work():
            from ..core.services.corpus_export import export_corpus

            return export_corpus(
                archive,
                destination,
                mode="encrypted" if encrypted else "decrypted",
                catalog=catalog,
                progress=self.progress.update,
                cancel=cancel,
            )

        def complete(manifest):
            failed = len(manifest["failures"])
            self.info.setPlainText(
                f"已导出{label}语料：{destination}\n"
                f"条目 {manifest['entries_written']} / {manifest['entries_total']} 条；"
                f"失败 {failed} 条\n"
                f"清单：{destination / 'manifest.json'}\n"
                f"原包 SHA256：{manifest['archive_sha256']}\n"
                "只读取原包；未执行任何模块，未改动包内字节。"
            )
            self.output_tabs.setCurrentWidget(self.info)
            self.statusBar().showMessage(
                f"{label}语料导出完成：{manifest['entries_written']} 条", 9000
            )

        self.task(work, complete, cancel=cancel)

    def import_corpus(self):
        archive = self.selected_archive()
        if not archive:
            self.fail("请先选择script.fls或data.fls；清单必须匹配当前包")
            return
        name, _ = QFileDialog.getOpenFileName(
            self,
            "选择可信语料的full/manifest.audited.jsonl（全部独立ZIP解压到同一目录）",
            "",
            "Audited corpus (manifest.audited.jsonl)",
        )
        if not name:
            return
        if (
            QMessageBox.question(
                self,
                "确认外部语料来源",
                "将只读检查清单并读取其entry目录内的产物；不执行驱动/源码。\n"
                "语料完整标记/历史编译结果不代表可安全回包。继续？",
                defaultButton=QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        cancel = Event()
        self.task(
            lambda: load_corpus(archive, Path(name), cancel=cancel),
            self.adopt_corpus,
            cancel=cancel,
        )

    def adopt_corpus(self, corpus):
        self.corpora[corpus.ref.archive] = corpus
        self.corpus_refs = [
            r for r in self.corpus_refs if r.archive != corpus.ref.archive
        ] + [corpus.ref]
        self.project_dirty = True
        self.info.setPlainText(
            f"语料清单已关联 {len(corpus.offsets)} 条；SHA256 {corpus.ref.sha256}\n"
            "双击未打开条目会读取语料候选；已有稿不覆盖。\n"
            + (
                "右键可另开语料候选；修复参数须单独核验并另存目录，未自动应用。"
                if corpus.ref.archive
                in {a.path for a in self.archives if a.vm == "py25"}
                else "data按VM2.7严格解码，不套用script五段参数；采用前仍须编译核验。"
            )
        )

    def corpus_for(self, archive):
        corpus = self.corpora.get(archive.path)
        if corpus is not None:
            return corpus
        ref = next((r for r in self.corpus_refs if r.archive == archive.path), None)
        if ref is None:
            raise ValueError("此包尚未关联语料清单")
        return load_corpus(archive, ref.path, expected_sha=ref.sha256)

    def open_corpus_module(self):
        selected = self.selected()
        if not selected or self.jobs:
            return
        archive, entry = selected
        catalog = self.catalog_for(archive)

        def prepare():
            return corpus_report(self.corpus_for(archive), archive, entry, catalog)

        def complete(report):
            if not report.source:
                self.info.setPlainText(
                    "此语料条目没有源码候选：\n" + "\n".join(report.diagnostics)
                )
                return
            self.open_recovery_candidate(report)
            self.project_dirty = True

        self.task(prepare, complete)

    def generate_data_corpus(self):
        archive = self.selected_archive()
        if not archive or archive.vm != "py27" or self.jobs:
            self.fail("请先选择data.fls；此入口只处理VM2.7，不重跑script语料")
            return
        name, _ = QFileDialog.getSaveFileName(
            self,
            "选择全新data候选目录（不得存在，不执行目标脚本）",
            "data-corpus",
            "All (*)",
        )
        if not name:
            return
        try:
            destination = Path(name)
            self.assert_writable_target(destination)
            if destination.exists() or destination.is_symlink():
                raise ValueError("请选择尚不存在的data候选目录")
        except (OSError, ValueError) as exc:
            self.fail(exc)
            return
        cancel = Event()
        compiler = self.compilers.get("py27")

        def prepare():
            from ..core.services.data_corpus import build_data_corpus
            from ..core.services.pycdc_engine import discover_pycdc

            return build_data_corpus(
                archive,
                destination,
                pycdc=discover_pycdc(),
                compiler=compiler,
                cancel=cancel,
            )

        def complete(result):
            corpus, summary = result
            if not summary["counts"].get("editable_candidates", 0):
                self.info.setPlainText(
                    "未生成可编辑候选，未自动关联缓存；请检查恢复引擎。\n"
                    + json.dumps(summary, ensure_ascii=False, indent=2)
                )
                return
            self.adopt_corpus(corpus)
            self.info.appendPlainText(
                "data候选生成结果（非语义/回包验收）：\n"
                + json.dumps(summary, ensure_ascii=False, indent=2)
            )

        self.task(prepare, complete, cancel=cancel)

    def export_verified_catalog(self):
        archive = self.selected_archive()
        if not archive or self.jobs:
            return
        if archive.vm != "py25":
            self.fail("data无需五段参数；可直接生成或导入VM2.7候选清单")
            return
        catalog = self.catalog_for(archive)
        if catalog is None:
            self.fail("先确认与此原包对应的原参数目录")
            return

        def prepare():
            return verified_parameters(self.corpus_for(archive), archive, catalog)

        def complete(result):
            raw, accepted, rejected = result
            self.info.setPlainText(
                "严格全字节复现通过："
                + repr(accepted)
                + "\n拒绝（仍可阅读候选）：\n"
                + json.dumps(rejected, ensure_ascii=False, indent=2)
            )
            if not accepted:
                return
            name, _ = QFileDialog.getSaveFileName(
                self,
                "另存核验参数目录（全新JSON；不修改原表）",
                "verified-decoding.json",
                "JSON (*.json)",
            )
            if not name:
                return
            target = Path(name if name.lower().endswith(".json") else name + ".json")
            protected = (
                [a.path for a in self.archives]
                + [r.path for r in self.catalogs]
                + [r.path for r in self.corpus_refs]
            )
            self.assert_writable_target(target)
            publish_new(target, raw, protected)
            ref = CatalogRef(
                archive.path,
                archive.fingerprint(),
                target.resolve(),
                hashlib.sha256(raw).hexdigest(),
            )
            self.catalogs = [r for r in self.catalogs if r.archive != archive.path] + [
                ref
            ]
            self.project_dirty = True
            self.info.appendPlainText(
                "已另存并关联核验目录；项目中保存其路径/SHA。现有编辑未改变。"
            )

        self.task(prepare, complete)
