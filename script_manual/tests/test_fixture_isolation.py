from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from support import TOOL, Fixture

from mxsj_manual.core.catalog import load_catalog
from mxsj_manual.core.io import ManualError


class FixtureIsolationTests(unittest.TestCase):
    def test_units_do_not_need_production_annotations_inventory_or_reviews(self):
        with tempfile.TemporaryDirectory() as folder:
            tool = Path(folder)
            shutil.copytree(TOOL / "schema", tool / "schema")
            shutil.copytree(TOOL / "tests/fixtures", tool / "tests/fixtures")
            case = Fixture()
            try:
                with patch("support.TOOL", tool):
                    case.setUp()
                catalog = load_catalog(case.root, repository=case.repo)
                self.assertEqual(catalog.coverage()["indexed"], 20)
                self.assertEqual(catalog.coverage()["annotated"], 1)
            finally:
                case.doCleanups()

    def test_production_smoke_has_no_hardcoded_annotation_count(self):
        # Structural smoke only; independent source/semantic review is still required.
        catalog = load_catalog(TOOL)
        coverage = catalog.coverage()
        self.assertEqual(coverage["indexed"], len(catalog.modules))
        self.assertLessEqual(coverage["accepted"], coverage["annotated"])
        self.assertLessEqual(coverage["annotated"], coverage["indexed"])
        self.assertEqual(
            coverage["annotated"],
            sum(row["annotation"] is not None for row in catalog.modules),
        )

    def test_isolation_does_not_disable_invalid_production_data_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in (
                "schema",
                "coordination",
                "inventory",
                "annotations",
                "reviews",
            ):
                shutil.copytree(TOOL / name, root / name)
            (root / "inventory/modules.jsonl").write_text(
                "broken JSON\n", encoding="utf-8"
            )
            with self.assertRaises(ManualError):
                load_catalog(root)
