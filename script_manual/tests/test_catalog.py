from __future__ import annotations

from support import Fixture

from mxsj_manual.core.catalog import load_catalog
from mxsj_manual.core.io import ManualError


class CatalogTests(Fixture):
    def test_coverage_separates_inventory_annotations_approval(self):
        self.assertEqual(
            load_catalog(self.root).coverage(),
            {
                "expected_entries": 5135,
                "indexed": 20,
                "annotated": 1,
                "accepted": 0,
                "excluded": 0,
            },
        )

    def test_three_search_modes_and_backslash_normalization(self):
        catalog = load_catalog(self.root)
        for query in (
            "公告",
            "login/mainpage",
            "refreshbulletin",
            "LOGIN\\MAINPAGE",
            "公告 news.txt",
        ):
            with self.subTest(query=query):
                self.assertEqual(
                    [r["entry_index"] for r in catalog.search(query)], [337]
                )
        self.assertFalse(catalog.search("公告", domain="network"))
        self.assertFalse(catalog.search("公告", status="accepted"))
        self.assertEqual(len(catalog.search(status="unannotated")), 19)
        self.assertFalse(catalog.search("does-not-exist"))

    def test_duplicate_inventory_identity_rejected(self):
        rows = self.inventory()
        self.put_inventory(rows + [rows[0]])
        with self.assertRaisesRegex(ManualError, "重复"):
            load_catalog(self.root)

    def test_duplicate_path_preserves_two_identities(self):
        rows = self.inventory()
        duplicate = dict(rows[0], entry_index=90)
        self.put_inventory(rows + [duplicate])
        self.assertEqual(load_catalog(self.root).coverage()["indexed"], 21)

    def test_automatic_function_names_are_searchable_without_annotations(self):
        rows = self.inventory()
        rows[0]["functions"] = [
            {"name": "Synthetic.ExactName", "signature": None, "kind": "method"}
        ]
        self.put_inventory(rows)
        self.assertEqual(len(load_catalog(self.root).search("Synthetic.ExactName")), 1)

    def test_vm_must_match_archive(self):
        rows = self.inventory()
        rows[0]["vm"] = "py27"
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "VM"):
            load_catalog(self.root)

    def test_unknown_archive_rejected(self):
        rows = self.inventory()
        rows[0]["archive_sha256"] = "0" * 64
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "冻结包"):
            load_catalog(self.root)

    def test_out_of_range_entry_rejected(self):
        rows = self.inventory()
        rows[0]["entry_index"] = 5002
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "条目范围"):
            load_catalog(self.root)

    def test_unconfirmed_path_cannot_be_marked_read(self):
        rows = self.inventory()
        rows[0]["path"] = None
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "缺少路径"):
            load_catalog(self.root)

    def test_excluded_entry_metadata_only_is_allowed(self):
        rows = self.inventory()
        rows.append(
            dict(
                rows[0],
                entry_index=1288,
                path=None,
                path_status="excluded_by_policy",
                functions=[],
            )
        )
        self.put_inventory(rows)
        self.assertEqual(load_catalog(self.root).coverage()["excluded"], 1)

    def test_excluded_entry_path_and_functions_are_rejected(self):
        for change in (
            {"path": "forbidden"},
            {
                "functions": [
                    {"name": "forbidden", "kind": "function", "signature": None}
                ]
            },
        ):
            with self.subTest(change=change):
                rows = self.inventory()
                rows = [r for r in rows if r["entry_index"] != 1288]
                row = dict(
                    rows[0],
                    entry_index=1288,
                    path=None,
                    path_status="excluded_by_policy",
                    functions=[],
                )
                row.update(change)
                self.put_inventory(rows + [row])
                with self.assertRaisesRegex(ManualError, "排除条目不得"):
                    load_catalog(self.root)

    def test_excluded_entry_cannot_be_marked_unreadable(self):
        rows = self.inventory()
        rows.append(
            dict(rows[0], entry_index=1288, path=None, path_status="unreadable")
        )
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "政策元数据"):
            load_catalog(self.root)

    def test_exclusion_cannot_be_removed_from_baseline(self):
        path = self.root / "coordination/baseline.json"
        baseline = self.get(path)
        baseline["archives"][0]["excluded_indices"] = []
        self.put(path, baseline)
        with self.assertRaisesRegex(ManualError, "禁止解除"):
            load_catalog(self.root)

    def test_directory_cannot_have_annotation(self):
        rows = self.inventory()
        next(r for r in rows if r["entry_index"] == 337)["path_status"] = "directory"
        self.put_inventory(rows)
        with self.assertRaisesRegex(ManualError, "目录记录"):
            load_catalog(self.root)

    def test_full_inventory_gate_rejects_pilot(self):
        with self.assertRaisesRegex(ManualError, "全量目录未完成"):
            load_catalog(self.root, require_full=True)

    def test_full_inventory_gate_counts_both_vms_and_policy_metadata(self):
        catalog = load_catalog(self.root)
        present = {(r["archive_sha256"], r["entry_index"]): r for r in self.inventory()}
        rows = []
        for archive in catalog.baseline["archives"]:
            for index in range(archive["entries"]):
                rows.append(
                    present.get(
                        (archive["sha256"], index),
                        {
                            "archive_sha256": archive["sha256"],
                            "entry_index": index,
                            "path": None,
                            "vm": archive["vm"],
                            "functions": [],
                            "path_status": "excluded_by_policy"
                            if index in archive["excluded_indices"]
                            else "unreadable",
                        },
                    )
                )
        self.put_inventory(rows)
        result = load_catalog(self.root, require_full=True)
        self.assertEqual(result.coverage()["indexed"], 5135)
        self.assertEqual(result.coverage()["annotated"], 1)

    def test_task_identity_must_exist(self):
        path = self.root / "coordination/tasks.json"
        tasks = self.get(path)
        tasks["tasks"][0]["entry_index"] = 1
        self.put(path, tasks)
        with self.assertRaisesRegex(ManualError, "任务引用未登记"):
            load_catalog(self.root)

    def test_duplicate_task_rejected(self):
        path = self.root / "coordination/tasks.json"
        tasks = self.get(path)
        tasks["tasks"].append(tasks["tasks"][0])
        self.put(path, tasks)
        with self.assertRaisesRegex(ManualError, "任务重复"):
            load_catalog(self.root)

    def test_historical_corpus_cannot_be_falsely_marked_pinned(self):
        path = self.root / "coordination/baseline.json"
        baseline = self.get(path)
        baseline["corpus_reference"]["status"] = "pinned_manifest_available"
        self.put(path, baseline)
        with self.assertRaisesRegex(ManualError, "manifest摘要"):
            load_catalog(self.root)

    def test_same_index_in_two_archives_remains_distinct(self):
        rows = self.inventory()
        base = load_catalog(self.root).baseline
        rows.append(
            dict(
                rows[0],
                archive_sha256=base["archives"][1]["sha256"],
                entry_index=8,
                vm="py27",
            )
        )
        self.put_inventory(rows)
        self.assertEqual(load_catalog(self.root).coverage()["indexed"], 21)
