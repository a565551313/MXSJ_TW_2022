"""Integration tests for Review API endpoints."""

import sys
import unittest
from pathlib import Path

# Add src and repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from server.apps.review_api.app import create_app


class TestReviewApiEndpoints(unittest.TestCase):
    """Test all top-level API endpoints defined in API contract."""

    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.client = TestClient(app)

    def test_health_endpoint(self):
        r = self.client.get("/api/v1/review/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["status"], "ready")
        self.assertEqual(data["batch"], "batch_001")
        self.assertEqual(data["loaded_files_count"], 22)
        self.assertEqual(data["datasets_count"], 17)
        self.assertEqual(data["total_records_count"], 12202)

    def test_batch_endpoint(self):
        r = self.client.get("/api/v1/review/batch")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["batch"], "batch_001")
        self.assertFalse(data["native_loader_confirmed"])
        self.assertEqual(data["manifest_files_count"], 21)
        self.assertIn("1945", data["tables_summary"])
        self.assertIn("checks", data["validation_summary"])

    def test_datasets_list_endpoint(self):
        r = self.client.get("/api/v1/review/datasets")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total"], 17)
        self.assertEqual(len(data["datasets"]), 17)

    def test_single_dataset_meta(self):
        r = self.client.get("/api/v1/review/datasets/pets")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["id"], "pets")
        self.assertEqual(data["rows"], 135)
        self.assertEqual(data["primary_key"], ["client_shape_id"])
        self.assertEqual(data["source_entry"], 2027)

    def test_quarantine_endpoint(self):
        r = self.client.get("/api/v1/review/quarantine")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total"], 4)
        self.assertEqual(len(data["records"]), 4)

        # Filter by entry_index
        r2 = self.client.get("/api/v1/review/quarantine?entry_index=1945")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["total"], 1)
        self.assertEqual(data2["records"][0]["record_key"], 72548)

    def test_overwrites_endpoint(self):
        r = self.client.get("/api/v1/review/overwrites")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total"], 9)

        # Filter by key
        r2 = self.client.get("/api/v1/review/overwrites?key=4573")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["total"], 1)
        self.assertEqual(data2["records"][0]["key"], 4573)

    def test_missing_aptitudes_endpoint(self):
        r = self.client.get("/api/v1/review/missing-aptitudes")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 3)
        ids = {rec["client_shape_id"] for rec in data}
        self.assertEqual(ids, {3010, 4021, 4022})

    def test_ambiguous_skills_endpoint(self):
        r = self.client.get("/api/v1/review/ambiguous-skills")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(len(data), 4)
        for rec in data:
            self.assertTrue(rec["ambiguous"])
            self.assertIn(rec["skill_id"], [229, 255, 329, 355])


if __name__ == "__main__":
    unittest.main()
