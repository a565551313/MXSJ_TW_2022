from __future__ import annotations

from copy import deepcopy

from guide_fixture import install_guide
from support import Fixture

from mxsj_manual.core.catalog import load_catalog
from mxsj_manual.core.export import render_site
from mxsj_manual.core.guide_render import guide_html
from mxsj_manual.core.guides import load_guides
from mxsj_manual.core.io import ManualError, digest
from mxsj_manual.core.store import ContentStore


class GuideTests(Fixture):
    def setUp(self):
        super().setUp()
        self.path, self.guide = install_guide(self)

    def put_guide(self):
        self.put(self.path, self.guide)

    def test_backward_compatible_content_without_guides(self):
        self.path.unlink()
        self.path.parent.rmdir()
        self.assertEqual(load_catalog(self.root).guides, [])

    def test_bound_navigation_and_search_not_editorial_approval(self):
        self.review()
        catalog = load_catalog(self.root)
        self.assertEqual(catalog.coverage()["accepted"], 1)
        guide = catalog.search_guides("合成 公告")[0]
        self.assertEqual(guide["editorial_status"], "draft_unreviewed")
        self.assertEqual(guide["navigation_status"], "current")
        ref = guide["steps"][0]["references"][0]
        self.assertEqual(ref["review_status"], "accepted")
        self.assertTrue(ref["binding_current"])
        self.assertEqual(ref["function_index"], 0)
        self.assertIn('href="#guide-step-1"', guide_html(guide))
        self.assertEqual(len(catalog.search_guides("LOGIN\\MAINPAGE")), 1)
        self.assertFalse(catalog.search_guides("not-covered"))

    def test_source_verification_previews_text_but_never_executes_it(self):
        self.record["evidence"][0].update(start_line=1, end_line=100)
        self.save()
        self.path, self.guide = install_guide(self)
        catalog = load_catalog(self.root, repository=self.repo)
        evidence = catalog.guides[0]["steps"][0]["references"][0]["evidence"][0]
        self.assertTrue(evidence["verified"])
        self.assertEqual(len(evidence["lines"]), 60)
        self.assertEqual(evidence["lines"][0]["number"], 1)
        self.assertIn("MUST_NEVER_EXECUTE_GAME_CODE", evidence["lines"][0]["text"])
        self.assertTrue(evidence["truncated"])
        self.assertIn("guides/fixture.json", catalog.file_hashes)
        self.assertIn("仅预览前60物理行", guide_html(catalog.guides[0]))

    def test_without_repository_no_fake_verified_snippet(self):
        evidence = load_catalog(self.root).guides[0]["steps"][0]["references"][0][
            "evidence"
        ][0]
        self.assertFalse(evidence["verified"])
        self.assertEqual(evidence["lines"], [])

    def test_annotation_one_byte_change_disables_old_anchors(self):
        self.annotation.write_bytes(self.annotation.read_bytes() + b"\n")
        catalog = load_catalog(self.root)
        guide = catalog.guides[0]
        ref = guide["steps"][0]["references"][0]
        self.assertEqual(guide["navigation_status"], "stale")
        self.assertTrue(catalog.warnings)
        self.assertFalse(ref["binding_current"])
        self.assertNotIn("function_index", ref)
        self.assertEqual(ref["evidence"], [])
        html = guide_html(guide)
        self.assertIn("旧步骤锚点已禁用", html)
        self.assertNotIn('href="#module=', html)

    def test_shared_path_cannot_reuse_cache_under_a_conflicting_source_sha(self):
        catalog = load_catalog(self.root)
        row = next(r for r in catalog.modules if r["annotation"])
        other = deepcopy(row)
        other["id"] = row["archive_sha256"] + ":9999"
        other["annotation"]["sources"][0]["sha256"] = "0" * 64
        ref = deepcopy(self.guide["steps"][0]["references"][0])
        ref["entry_index"] = 9999
        self.guide["steps"][0]["references"].append(ref)
        self.put_guide()
        with self.assertRaisesRegex(ManualError, "来源SHA绑定冲突"):
            load_guides(ContentStore(self.root), [row, other], self.repo, [])

    def test_unknown_function_or_evidence_is_rejected(self):
        for field, value in [
            ("function", "nonexistent"),
            ("evidence_ids", ["nonexistent"]),
        ]:
            with self.subTest(field=field):
                self.path, self.guide = install_guide(self)
                self.guide["steps"][0]["references"][0][field] = value
                self.put_guide()
                with self.assertRaises(ManualError):
                    load_catalog(self.root)

    def test_unannotated_or_protected_module_cannot_get_guide_content(self):
        for index in (1288, 9999):
            with self.subTest(index=index):
                self.guide["steps"][0]["references"][0]["entry_index"] = index
                self.put_guide()
                with self.assertRaises(ManualError):
                    load_catalog(self.root)

    def test_duplicate_identity_is_rejected(self):
        self.put(self.path.parent / "duplicate.json", self.guide)
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_editorial_acceptance_and_unknown_fields_are_not_allowed(self):
        for change in ({"editorial_status": "accepted"}, {"approved": True}):
            with self.subTest(change=change):
                self.path, self.guide = install_guide(self)
                self.guide.update(change)
                self.put_guide()
                with self.assertRaises(ManualError):
                    load_catalog(self.root)

    def test_missing_fields_and_empty_evidence_are_rejected(self):
        self.guide["steps"][0]["references"][0]["evidence_ids"] = []
        self.put_guide()
        with self.assertRaises(ManualError):
            load_catalog(self.root)
        self.path, self.guide = install_guide(self)
        del self.guide["steps"][0]["check"]
        self.put_guide()
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_html_escapes_editorial_and_evidence_text(self):
        payload = '</script><img src="https://evil.invalid" onerror="alert(1)">'
        self.guide["steps"][0]["change"] = payload
        self.put_guide()
        self.source.write_text(payload + "\n" * 350, encoding="utf-8")
        self.record["sources"][0]["sha256"] = digest(self.source.read_bytes())
        self.save()
        self.guide["steps"][0]["references"][0]["annotation_sha256"] = digest(
            self.annotation.read_bytes()
        )
        self.put_guide()
        catalog = load_catalog(self.root, repository=self.repo)
        html = guide_html(catalog.guides[0])
        self.assertNotIn(payload, html)
        self.assertIn("&lt;/script&gt;", html)
        site = render_site(catalog)
        self.assertNotIn(payload, site)
        self.assertIn("\\u003c/script\\u003e", site)

    def test_subdirectories_are_rejected_not_silently_ignored(self):
        (self.path.parent / "hidden").mkdir()
        with self.assertRaises(ManualError):
            load_catalog(self.root)
