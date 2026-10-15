from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from support import Fixture

from mxsj_manual.app import main
from mxsj_manual.core.catalog import load_catalog
from mxsj_manual.core.export import export_site, render_site
from mxsj_manual.core.io import ManualError, digest
from mxsj_manual.core.render import detail_html


class ReviewTests(Fixture):
    def test_exact_annotation_approval(self):
        self.review()
        self.assertEqual(load_catalog(self.root).coverage()["accepted"], 1)

    def test_one_byte_edit_invalidates_approval(self):
        self.review()
        self.annotation.write_bytes(self.annotation.read_bytes() + b"\n")
        catalog = load_catalog(self.root)
        self.assertEqual(catalog.coverage()["accepted"], 0)
        self.assertEqual(catalog.search("公告")[0]["review_status"], "stale_review")
        self.assertTrue(catalog.warnings)

    def test_review_requires_H(self):
        self.review(reviewer="C")
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_review_cannot_reference_nonexistent_annotation(self):
        self.review(entry_index=4293)
        with self.assertRaisesRegex(ManualError, "尚不存在的说明"):
            load_catalog(self.root)

    def test_duplicate_reviews_are_not_silently_overwritten(self):
        self.review()
        path = self.root / "reviews/H_337.json"
        self.put(path.with_name("another.json"), self.get(path))
        with self.assertRaisesRegex(ManualError, "重复提交"):
            load_catalog(self.root)

    def test_author_cannot_embed_approval_in_annotation(self):
        self.record["review_status"] = "accepted"
        self.save()
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_rejection_is_distinct_from_missing_review(self):
        self.review(decision="changes_requested")
        self.assertEqual(
            load_catalog(self.root).search("公告")[0]["review_status"],
            "changes_requested",
        )


class ExportTests(Fixture):
    def test_self_contained_export_receipt_and_no_input_writes(self):
        catalog = load_catalog(self.root, repository=self.repo)
        before = dict(catalog.file_hashes)
        output = Path(self.temporary.name) / "offline site"
        html = export_site(catalog, output, content_root=self.root)
        receipt = json.loads((output / "BUILD.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["html_sha256"], digest(html.read_bytes()))
        self.assertEqual(receipt["input_sha256"], before)
        self.assertIn("schema/contract.schema.json", before)
        self.assertTrue(receipt["evidence_verified"])
        self.assertFalse((output / "INCOMPLETE.txt").exists())
        self.assertEqual(before, load_catalog(self.root).file_hashes)

    def test_without_source_verification_receipt_does_not_claim_it(self):
        output = Path(self.temporary.name) / "offline"
        export_site(load_catalog(self.root), output, content_root=self.root)
        self.assertFalse(self.get(output / "BUILD.json")["evidence_verified"])

    def test_existing_output_cannot_be_overwritten(self):
        output = Path(self.temporary.name) / "existing"
        output.mkdir()
        marker = output / "user-data.txt"
        marker.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            export_site(load_catalog(self.root), output, content_root=self.root)
        self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")

    def test_output_inside_content_or_git_is_rejected(self):
        catalog = load_catalog(self.root)
        with self.assertRaises(ManualError):
            export_site(catalog, self.root / "site", content_root=self.root)
        (self.repo / ".git").mkdir()
        with self.assertRaises(ManualError):
            export_site(catalog, self.repo / "site", content_root=self.root)

    def test_partial_export_is_marked_incomplete(self):
        original = Path.open
        output = Path(self.temporary.name) / "failed"

        def fail_receipt(path, *args, **kwargs):
            if path.name == "BUILD.json":
                raise OSError("fixture disk full")
            return original(path, *args, **kwargs)

        with patch.object(Path, "open", fail_receipt):
            with self.assertRaises(OSError):
                export_site(load_catalog(self.root), output, content_root=self.root)
        self.assertTrue((output / "INCOMPLETE.txt").exists())

    def test_untrusted_strings_cannot_break_script_or_native_html(self):
        payload = '</script><img src="https://evil.invalid" onerror="alert(1)">\u2028'
        self.record["purpose"]["text"] = payload
        self.save()
        catalog = load_catalog(self.root)
        html = render_site(catalog)
        self.assertNotIn(payload, html)
        self.assertIn("\\u003c/script\\u003e", html)
        detail = detail_html(catalog.search("公告")[0])
        self.assertNotIn('<img src="https://evil.invalid"', detail)
        self.assertIn("&lt;img", detail)
        self.assertIn("Content-Security-Policy", html)
        self.assertIn("script-src 'sha256-", html)
        self.assertNotIn("<script src=", html)

    def test_cli_validation_and_incomplete_gate_exit_codes(self):
        with patch("sys.stdout"):
            self.assertEqual(main(["--content", str(self.root), "validate"]), 0)
            self.assertEqual(
                main(
                    [
                        "--content",
                        str(self.root),
                        "validate",
                        "--require-full-inventory",
                    ]
                ),
                2,
            )
            self.assertEqual(
                main(["--content", str(self.root), "validate", "--verify-evidence"]), 2
            )

    def test_core_does_not_import_Qt_or_game_modules(self):
        import ast

        from support import TOOL

        for path in (TOOL / "src/mxsj_manual/core").glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    names = [n.name for n in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                else:
                    continue
                self.assertFalse(
                    any(
                        n.startswith(("PySide6", "script_editor", "C_sys"))
                        for n in names
                    )
                )
