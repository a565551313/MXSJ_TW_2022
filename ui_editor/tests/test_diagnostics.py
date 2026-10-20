"""无 Qt 的诊断、引用影响与保存基线回归；不依赖真实 .dlg 语料库。"""

from __future__ import annotations

import copy
import unittest

from ui_editor.core.diagnostics import (
    diagnose,
    reference_impacts,
    walk_paths,
    widget_at_path,
)
from ui_editor.core.model import LayoutDocument
from ui_editor.core.review import layout_changes, referenced_staged_images
from ui_editor.core.script_index import LayoutLink, ObjectRef, SkinRef


def make_doc():
    return LayoutDocument.from_dicts(
        [
            {
                "sWidgetType": "CMainFrame",
                "sName": "root",
                "iWidth": 100,
                "iHeight": 100,
                "lChildren": [
                    {
                        "sWidgetType": "CButton",
                        "sName": "button",
                        "iX": 10,
                        "iY": 10,
                        "iWidth": 20,
                        "iHeight": 20,
                        "sFileName": "images/a.png",
                    },
                    {"sWidgetType": "CTextFrame", "sName": "text", "sText": "測試"},
                ],
            }
        ],
        None,
    )


def codes(doc, **kwargs):
    return {issue.code for issue in diagnose(doc, **kwargs)}


def link():
    return LayoutLink(
        "ui/test.dlg",
        objects={
            "button": [ObjectRef("controller", 10, "Panel", "Init", True)],
            "dynamic": [ObjectRef("factory", 11, "Panel", "Build", False)],
        },
        skins={
            "button": [
                SkinRef(
                    "controller",
                    10,
                    "Panel",
                    "Init",
                    "MakeButton",
                    "images/skin.png",
                    "",
                    12,
                )
            ]
        },
    )


class TestDiagnostics(unittest.TestCase):
    def test_diagnostics_are_read_only(self):
        doc = make_doc()
        doc.reset_history()
        before = copy.deepcopy(doc.to_dicts())
        diagnose(doc, link=link(), resource_exists=lambda _name: False)
        self.assertEqual(doc.to_dicts(), before)
        self.assertFalse(doc.dirty)
        self.assertFalse(doc.can_undo)
        self.assertEqual(doc.changes(), [])

    def test_paths_disambiguate_duplicates_and_invalid_path(self):
        doc = make_doc()
        doc.roots[0].children[1].name = "button"
        issues = [i for i in diagnose(doc) if i.code == "DUPLICATE_NAME"]
        self.assertEqual([i.path for i in issues], [(0, 0), (0, 1)])
        self.assertIs(widget_at_path(doc, (0, 1)), doc.roots[0].children[1])
        self.assertIsNone(widget_at_path(doc, (0, 9)))
        self.assertIsNone(widget_at_path(doc, (-1,)))
        self.assertIsNone(widget_at_path(doc, ()))
        self.assertEqual([p for p, _ in walk_paths(doc.roots)], [(0,), (0, 0), (0, 1)])

    def test_negative_geometry_zero_is_info_not_engine_failure(self):
        doc = make_doc()
        widget = doc.roots[0].children[0]
        widget.props["iWidth"] = -1
        widget.props["iHeight"] = 0
        issues = diagnose(doc)
        self.assertTrue(any(i.code == "NEGATIVE_SIZE" for i in issues))
        self.assertEqual(
            [i.severity for i in issues if i.code == "AUTO_SIZE"], ["提示"]
        )
        self.assertNotIn("OUTSIDE_PARENT", {i.code for i in issues})

    def test_geometry_type_and_bounds(self):
        doc = make_doc()
        widget = doc.roots[0].children[0]
        widget.props["iX"] = 90
        self.assertIn("OUTSIDE_PARENT", codes(doc))
        widget.props["iWidth"] = "twenty"
        self.assertIn("GEOMETRY_TYPE", codes(doc))
        self.assertNotIn("OUTSIDE_PARENT", codes(doc))
        widget.props["iWidth"] = True
        self.assertIn("GEOMETRY_TYPE", codes(doc))

    def test_unknown_parent_dimensions_not_guessed(self):
        doc = make_doc()
        doc.roots[0].props["iWidth"] = 0
        doc.roots[0].children[0].props["iX"] = 999
        self.assertNotIn("OUTSIDE_PARENT", codes(doc))

    def test_encoding_checks_native_codecs_and_nested_fields(self):
        doc = make_doc()
        widget = doc.roots[0].children[1]
        widget.props["sText"] = "😀"
        widget.props["lFuture"] = [{"sTitles": ("測試", "😀")}]
        widget.props["sSoundPath"] = "music/😀.ogg"
        errors = [i for i in diagnose(doc) if i.code == "ENCODING"]
        self.assertEqual({i.field for i in errors}, {"sText", "lFuture", "sSoundPath"})
        self.assertTrue(all(i.severity == "错误" for i in errors))

    def test_big5_text_vs_gbk_path_and_original_surrogate_bytes(self):
        doc = make_doc()
        widget = doc.roots[0].children[1]
        widget.props["sText"] = "对"  # GBK 有、Big5 没有，不能静默简繁转换
        widget.props["sFileName"] = "images/对.png"
        errors = [i for i in diagnose(doc) if i.code == "ENCODING"]
        self.assertEqual([i.field for i in errors], ["sText"])
        widget.props["sText"] = "\udc80"  # 原始损坏/扩展字节应原样保留
        self.assertNotIn("ENCODING", codes(doc))

    def test_missing_resource_staged_normalization_and_unmounted(self):
        doc = make_doc()
        self.assertIn("RESOURCES_NOT_CHECKED", codes(doc))
        self.assertNotIn("RESOURCE_MISSING", codes(doc))
        self.assertIn("RESOURCE_MISSING", codes(doc, resource_exists=lambda _p: False))
        found = []

        def exists(path):
            found.append(path)
            return True

        self.assertNotIn("RESOURCE_MISSING", codes(doc, resource_exists=exists))
        self.assertEqual(found, ["images/a.png"])
        result = codes(
            doc, resource_exists=lambda _p: False, staged_paths=["IMAGES\\A.PNG"]
        )
        self.assertIn("STAGED_RESOURCE", result)
        self.assertNotIn("RESOURCE_MISSING", result)

    def test_dir_base_paths_not_reported_missing(self):
        """以斜杠结尾的目录型基路径（探针 v7 的伪引用）不再误报缺图。"""
        doc = make_doc()
        widget = doc.roots[0].children[0]
        widget.props["sFileName"] = (
            "combdialog4\\新登陆界面\\三态按钮\\声音按钮\\关闭\\"
        )
        issues = diagnose(doc, resource_exists=lambda _p: False)
        found = {i.code for i in issues}
        self.assertNotIn("RESOURCE_MISSING", found)
        self.assertIn("RESOURCE_DIR_BASE", found)
        issue = next(i for i in issues if i.code == "RESOURCE_DIR_BASE")
        self.assertEqual(issue.severity, "提示")
        self.assertEqual(issue.field, "sFileName")
        self.assertEqual(issue.path, (0, 0))
        self.assertIn("不按缺图处理", issue.message)

    def test_dir_base_probe_reports_matched_family(self):
        """诊断报出「命中了哪一族」，与画布同一套拼名规则；缺席也不判缺。"""
        doc = make_doc()
        widget = doc.roots[0].children[0]
        widget.props["sFileName"] = "combdialog4/新登陆界面/上文字底/"
        probed = []

        def exists(name):
            probed.append(name)
            return name.endswith(("0l.png", "0c.png", "0r.png"))

        issues = diagnose(doc, resource_exists=exists)
        self.assertIn("combdialog4/新登陆界面/上文字底/0l.png", probed)
        issue = next(i for i in issues if i.code == "RESOURCE_DIR_BASE")
        self.assertIn("三态横片", issue.message)
        self.assertNotIn("RESOURCE_MISSING", {i.code for i in issues})
        probed.clear()

        def absent(name):
            probed.append(name)
            return False

        issues = diagnose(doc, resource_exists=absent)
        self.assertIn("combdialog4/新登陆界面/上文字底/0.png", probed)
        issue = next(i for i in issues if i.code == "RESOURCE_DIR_BASE")
        self.assertIn("没拼出任何已知族", issue.message)
        self.assertIn("不代表缺图", issue.message)
        self.assertNotIn("RESOURCE_MISSING", {i.code for i in issues})

    def test_dir_base_classified_without_resolver(self):
        """没挂载来源也要归类目录型基路径，且不与 RESOURCES_NOT_CHECKED 冲突。"""
        doc = make_doc()
        doc.roots[0].children[0].props["sFileName"] = "dir\\sub\\"
        found = codes(doc)
        self.assertIn("RESOURCE_DIR_BASE", found)
        self.assertIn("RESOURCES_NOT_CHECKED", found)
        self.assertNotIn("RESOURCE_MISSING", found)

    def test_static_missing_name_is_warning_not_proof(self):
        doc = make_doc()
        issues = diagnose(doc, link=link())
        missing = [i for i in issues if i.code == "SCRIPT_REFERENCE_MISSING"]
        self.assertEqual(len(missing), 1)
        self.assertIn("dynamic", missing[0].message)
        self.assertIn("动态创建", missing[0].message)
        self.assertIsNone(missing[0].path)
        self.assertIn("STATIC_ONLY", {i.code for i in issues})
        self.assertIn("STATIC_ONLY", codes(LayoutDocument()))

    def test_reference_impacts_cover_anchor_skin_and_dedupe(self):
        index_link = link()
        impacts = reference_impacts(["button", "button", "no-hit"], index_link)
        self.assertEqual(len(impacts), 1)
        self.assertEqual(impacts[0].name, "button")
        self.assertEqual(len(impacts[0].details), 2)
        self.assertTrue(
            any("entry 10" in d and "位置锚点" in d for d in impacts[0].details)
        )
        self.assertTrue(any("代码皮肤" in d for d in impacts[0].details))
        self.assertEqual(reference_impacts(["button"], None), [])


class TestLayoutReview(unittest.TestCase):
    def test_change_list_tracks_unknown_fields_and_rename(self):
        doc = make_doc()
        widget = doc.roots[0].children[0]
        widget.name = "renamed"
        widget.props["lFuture"] = [1, True]
        changes = doc.changes()
        self.assertEqual({c.field for c in changes}, {"sName", "lFuture"})
        self.assertTrue(all(c.path == (0, 0) for c in changes))
        name = next(c for c in changes if c.field == "sName")
        self.assertEqual(name.before, "'button'")
        self.assertEqual(name.after, "'renamed'")

    def test_add_and_delete_subtrees_are_included(self):
        before = make_doc().to_dicts()
        self.assertEqual(len(layout_changes(before, [])), 3)
        self.assertTrue(
            all(c.operation == "删除控件" for c in layout_changes(before, []))
        )
        self.assertEqual(len(layout_changes([], before)), 3)
        self.assertEqual(layout_changes(before, copy.deepcopy(before)), [])

    def test_field_value_type_changes_not_lost(self):
        left = [{"sName": "b", "iFuture": 1}]
        right = [{"sName": "b", "iFuture": True}]
        change = layout_changes(left, right)[0]
        self.assertEqual((change.before, change.after), ("1", "True"))

    def test_undo_redo_review_uses_actual_state_not_operation_log(self):
        doc = make_doc()
        doc.reset_history()
        doc.roots[0].props["iWidth"] = 120
        doc.dirty = True
        doc.checkpoint()
        self.assertEqual(len(doc.changes()), 1)
        doc.undo()
        self.assertEqual(doc.changes(), [])
        self.assertFalse(doc.dirty)
        doc.redo()
        self.assertEqual(len(doc.changes()), 1)
        self.assertTrue(doc.dirty)

    def test_mark_saved_keeps_undo_but_refreshes_baseline_and_merge(self):
        doc = make_doc()
        doc.reset_history()
        doc.roots[0].props["iWidth"] = 120
        doc.checkpoint("width")
        doc.mark_saved()
        self.assertFalse(doc.dirty)
        self.assertEqual(doc.changes(), [])
        doc.roots[0].props["iWidth"] = 130
        doc.dirty = True
        doc.checkpoint("width")
        doc.undo()
        self.assertEqual(doc.roots[0].width, 120)
        self.assertFalse(doc.dirty)
        doc.undo()
        self.assertTrue(doc.dirty)
        self.assertEqual(doc.changes()[0].before, "120")
        doc.redo()
        self.assertFalse(doc.dirty)
        self.assertEqual(doc.changes(), [])

    def test_baseline_is_detached_from_mutable_unknown_values(self):
        doc = LayoutDocument.from_dicts([{"lFuture": [1]}], None)
        doc.roots[0].props["lFuture"].append(2)
        self.assertEqual(doc.changes()[0].before, "[1]")

    def test_staged_image_filter_matches_unknown_fields_too(self):
        roots = [{"sFileName": "Images\\A.PNG", "lFuture": ["images/b.png"]}]
        staged = {"images/a.png": b"A", "images/b.png": b"B", "unused.png": b"U"}
        self.assertEqual(
            referenced_staged_images(roots, staged),
            {"images/a.png": b"A", "images/b.png": b"B"},
        )
        self.assertEqual(len(staged), 3)  # 筛选本身不销账

    def test_redo_type_change_is_dirty_even_if_python_values_compare_equal(self):
        doc = LayoutDocument.from_dicts([{"iFuture": 1}], None)
        doc.reset_history()
        doc.roots[0].props["iFuture"] = True
        doc.dirty = True
        doc.checkpoint()
        doc.undo()
        self.assertFalse(doc.dirty)
        doc.redo()
        self.assertTrue(doc.changes())
        self.assertTrue(doc.dirty)
