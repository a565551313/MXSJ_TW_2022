from __future__ import annotations

import json
import shutil
from unittest.mock import patch

from support import Fixture

from mxsj_manual.core.catalog import load_catalog
from mxsj_manual.core.io import ManualError, digest, parse_json, read_bytes


class ValidationTests(Fixture):
    def test_unknown_and_missing_fields_rejected(self):
        for update in ({"bogus": 1}, {"purpose": "not a claim"}):
            with self.subTest(update=update):
                original = self.get(self.annotation)
                self.put(self.annotation, {**original, **update})
                with self.assertRaises(ManualError):
                    load_catalog(self.root)
                self.put(self.annotation, original)
        del self.record["source_status"]
        self.save()
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_annotation_identity_and_path_are_frozen(self):
        for field, value in (
            ("entry_index", 900),
            ("path", "wrong/path.py"),
            ("archive_sha256", "0" * 64),
        ):
            with self.subTest(field=field):
                original = self.get(self.annotation)
                self.put(self.annotation, {**original, field: value})
                with self.assertRaises(ManualError):
                    load_catalog(self.root)
                self.put(self.annotation, original)

    def test_duplicate_annotation_rejected(self):
        shutil.copy(self.annotation, self.annotation.with_name("copy.json"))
        with self.assertRaisesRegex(ManualError, "重复提交"):
            load_catalog(self.root)

    def test_domain_directory_is_enforced(self):
        self.annotation.rename(self.root / "annotations/network/mainpage.json")
        with self.assertRaisesRegex(ManualError, "所属领域目录"):
            load_catalog(self.root)

    def test_owner_cannot_be_changed_unilaterally(self):
        self.record.update(owner="E", domain="network")
        self.save()
        with self.assertRaisesRegex(ManualError, "跨域抢占"):
            load_catalog(self.root)

    def test_source_hash_and_lines_verified_without_executing_source(self):
        catalog = load_catalog(self.root, repository=self.repo)
        row = catalog.search("公告")[0]
        self.assertEqual(row["evidence_status"], "verified_bytes_and_lines")
        self.assertEqual(row["review_status"], "pending")

    def test_source_hash_drift_rejected(self):
        self.source.write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(ManualError, "摘要变化"):
            load_catalog(self.root, repository=self.repo)

    def test_evidence_beyond_end_rejected(self):
        self.record["evidence"][0]["end_line"] = 351
        self.save()
        with self.assertRaisesRegex(ManualError, "超过来源文件"):
            load_catalog(self.root, repository=self.repo)

    def test_evidence_reverse_range_rejected_without_repository(self):
        self.record["evidence"][0]["start_line"] = 99
        self.save()
        with self.assertRaisesRegex(ManualError, "倒置"):
            load_catalog(self.root)

    def test_non_utf8_source_cannot_be_silently_decoded(self):
        self.source.write_bytes(b"\xff\xfe\x00")
        self.record["sources"][0]["sha256"] = digest(self.source.read_bytes())
        self.save()
        with self.assertRaisesRegex(ManualError, "UTF8"):
            load_catalog(self.root, repository=self.repo)

    def test_duplicate_sources_and_evidence_rejected(self):
        for field in ("sources", "evidence"):
            with self.subTest(field=field):
                original = self.get(self.annotation)
                changed = json.loads(json.dumps(original))
                changed[field].append(changed[field][0])
                self.put(self.annotation, changed)
                with self.assertRaisesRegex(ManualError, "重复"):
                    load_catalog(self.root)
                self.put(self.annotation, original)

    def test_unknown_evidence_rejected(self):
        self.record["purpose"]["evidence"] = ["missing"]
        self.save()
        with self.assertRaisesRegex(ManualError, "未知证据"):
            load_catalog(self.root)

    def test_static_claim_requires_evidence(self):
        self.record["purpose"].update(confidence="static_reviewed", evidence=[])
        self.save()
        with self.assertRaisesRegex(ManualError, "必须引用证据"):
            load_catalog(self.root)

    def test_runtime_claim_cannot_be_proven_by_static_source(self):
        self.record["purpose"]["confidence"] = "runtime_verified"
        self.save()
        with self.assertRaisesRegex(ManualError, "不能证明实机"):
            load_catalog(self.root)

    def test_runtime_report_reference_is_required_not_automatically_approved(self):
        report = self.repo / "runtime.md"
        report.write_text("fixture report, not a real game test\n", encoding="utf-8")
        self.record["sources"].append(
            {
                "id": "run",
                "path": "runtime.md",
                "sha256": digest(report.read_bytes()),
                "kind": "runtime_report",
                "note": "fixture only",
            }
        )
        self.record["evidence"].append(
            {"id": "run", "source_id": "run", "start_line": 1, "end_line": 1}
        )
        self.record["purpose"].update(confidence="runtime_verified", evidence=["run"])
        self.save()
        result = load_catalog(self.root, repository=self.repo)
        self.assertEqual(result.coverage()["accepted"], 0)

    def test_source_paths_reject_escape_and_windows_drive(self):
        for name in (
            "../escape",
            "/absolute",
            "C:/secret",
            "a\\b",
            "./a",
            "a//b",
            "a\nb",
        ):
            with self.subTest(name=name):
                self.record["sources"][0]["path"] = name
                self.save()
                with self.assertRaises(ManualError):
                    load_catalog(self.root)

    def test_duplicate_function_qualified_name_rejected(self):
        self.record["functions"].append(self.record["functions"][0])
        self.save()
        with self.assertRaisesRegex(ManualError, "限定名重复"):
            load_catalog(self.root)

    def test_remote_schema_reference_never_uses_network(self):
        schema = self.root / "schema/contract.schema.json"
        value = self.get(schema)
        value["$defs"]["claim"] = {"$ref": "https://example.invalid/schema"}
        self.put(schema, value)
        with patch("socket.socket", side_effect=AssertionError("network forbidden")):
            with self.assertRaisesRegex(ManualError, "本地"):
                load_catalog(self.root)

    def test_symlink_source_and_content_directory_rejected(self):
        link = self.repo / "linked.py"
        try:
            link.symlink_to(self.source)
        except OSError:
            self.skipTest("此平台/账号无创建符号链接许可")
        self.record["sources"][0]["path"] = "linked.py"
        self.save()
        with self.assertRaisesRegex(ManualError, "符号链接"):
            load_catalog(self.root, repository=self.repo)
        link.unlink()
        folder = self.root / "reviews"
        renamed = self.root / "old-reviews"
        folder.rename(renamed)
        folder.symlink_to(renamed, target_is_directory=True)
        with self.assertRaisesRegex(ManualError, "符号链接"):
            load_catalog(self.root)

    def test_duplicate_json_key_nan_and_boolean_index_rejected(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}'):
            with self.subTest(raw=raw):
                with self.assertRaises(ManualError):
                    parse_json(raw)
        self.record["entry_index"] = True
        self.save()
        with self.assertRaises(ManualError):
            load_catalog(self.root)

    def test_file_and_aggregate_size_limits(self):
        with self.assertRaisesRegex(ManualError, "安全上限"):
            read_bytes(self.annotation, limit=10)
        with patch("mxsj_manual.core.store.MAX_ANNOTATIONS", 10):
            with self.assertRaisesRegex(ManualError, "总量"):
                load_catalog(self.root)

    def test_relationship_target_must_use_frozen_archive(self):
        self.record["relationships"][0]["module"]["archive_sha256"] = "0" * 64
        self.save()
        with self.assertRaisesRegex(ManualError, "冻结包"):
            load_catalog(self.root)

    def test_unresolved_relationship_is_explicit_not_guessed(self):
        self.record["relationships"][0]["module"] = None
        self.save()
        catalog = load_catalog(self.root)
        self.assertIsNone(
            catalog.search("公告")[0]["annotation"]["relationships"][0]["module"]
        )

    def test_relationship_claim_also_needs_runtime_evidence(self):
        self.record["relationships"][0]["summary"]["confidence"] = "runtime_verified"
        self.save()
        with self.assertRaisesRegex(ManualError, "不能证明实机"):
            load_catalog(self.root)
