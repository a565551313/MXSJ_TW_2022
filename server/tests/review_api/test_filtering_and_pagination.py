"""Integration tests for dataset querying, pagination, search, and filtering."""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from server.apps.review_api.app import create_app


class TestFilteringAndPagination(unittest.TestCase):
    """Test pagination bounds, exact field filtering, substring search, and composite PKs."""

    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.client = TestClient(app)

    def test_pagination_defaults_and_limits(self):
        r = self.client.get("/api/v1/review/datasets/items/records")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["offset"], 0)
        self.assertEqual(data["limit"], 50)
        self.assertEqual(data["count"], 50)
        self.assertEqual(data["total"], 6851)

        # Page 2
        r2 = self.client.get("/api/v1/review/datasets/items/records?offset=50&limit=25")
        self.assertEqual(r2.status_code, 200)
        data2 = r2.json()
        self.assertEqual(data2["offset"], 50)
        self.assertEqual(data2["limit"], 25)
        self.assertEqual(data2["count"], 25)

    def test_exact_field_filtering_pet_skills(self):
        # Query pet skill candidates for pet 2010
        r = self.client.get("/api/v1/review/datasets/pet_skill_candidates/records?client_shape_id=2010")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["total"] > 0)
        for rec in data["records"]:
            self.assertEqual(rec["client_shape_id"], 2010)

    def test_exact_field_filtering_maps_npcs(self):
        # Filter npcposdata_records by scene_id=1001
        r = self.client.get("/api/v1/review/datasets/npcposdata_records/records?scene_id=1001")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["total"] > 0)
        for rec in data["records"]:
            self.assertEqual(rec["scene_id"], 1001)

    def test_text_search_q(self):
        r = self.client.get("/api/v1/review/datasets/items/records?q=鹿茸")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total"], 2)
        for rec in data["records"]:
            self.assertIn("鹿茸", rec["name"])

    def test_sorting(self):
        # Sort by client_shape_id desc
        r = self.client.get("/api/v1/review/datasets/pets/records?sort_by=client_shape_id&order=desc&limit=5")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        ids = [rec["client_shape_id"] for rec in data["records"]]
        self.assertEqual(ids, sorted(ids, reverse=True))

    def test_single_record_lookup_simple_pk(self):
        r = self.client.get("/api/v1/review/datasets/items/records/11")
        self.assertEqual(r.status_code, 200)
        rec = r.json()
        self.assertEqual(rec["client_shape_id"], 11)
        self.assertEqual(rec["_pk"], "11")

    def test_single_record_lookup_composite_pk(self):
        # Composite PK for pet_skill_candidates is client_shape_id:sequence
        r = self.client.get("/api/v1/review/datasets/pet_skill_candidates/records/2010:0")
        self.assertEqual(r.status_code, 200)
        rec = r.json()
        self.assertEqual(rec["client_shape_id"], 2010)
        self.assertEqual(rec["sequence"], 0)
        self.assertEqual(rec["_pk"], "2010:0")


if __name__ == "__main__":
    unittest.main()
