from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from mxsj_manual.core.io import digest

TOOL = Path(__file__).resolve().parents[1]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "中文 space"
        self.root = self.repo / "手册"
        # Production annotations/inventory must never define unit-test expectations.
        shutil.copytree(TOOL / "schema", self.root / "schema")
        shutil.copytree(TOOL / "tests/fixtures", self.root, dirs_exist_ok=True)
        for domain in ("login", "ui_chat", "network", "battle", "gameplay"):
            (self.root / "annotations" / domain).mkdir(parents=True, exist_ok=True)
        (self.root / "reviews").mkdir(exist_ok=True)
        self.annotation = self.root / "annotations/login/mainpage.json"
        self.record = self.get(self.annotation)
        source = self.repo / self.record["sources"][0]["path"]
        source.parent.mkdir(parents=True)
        self.source = source
        raw = b"raise AssertionError('MUST_NEVER_EXECUTE_GAME_CODE')\n" * 350
        source.write_bytes(raw)
        self.record["sources"][0]["sha256"] = digest(raw)
        self.save()

    @staticmethod
    def get(path):
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def put(path, record):
        path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def save(self):
        self.put(self.annotation, self.record)

    def inventory(self):
        return [
            json.loads(line)
            for line in (self.root / "inventory/modules.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]

    def put_inventory(self, rows):
        (self.root / "inventory/modules.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )

    def review(self, **updates):
        record = {
            "schema_version": 1,
            "archive_sha256": self.record["archive_sha256"],
            "entry_index": self.record["entry_index"],
            "annotation_sha256": digest(self.annotation.read_bytes()),
            "reviewer": "H",
            "decision": "accepted",
            "note": "fixture only",
        }
        record.update(updates)
        self.put(self.root / "reviews/H_337.json", record)
