"""Integration tests for Review API error handling and input validation."""

import shutil
import sys
import tempfile
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


class TestErrorHandling(unittest.TestCase):
    """Test unified error formats, 404, 400, 405, and parameter boundaries."""

    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.client = TestClient(app)

    def test_unknown_dataset_returns_404(self):
        r = self.client.get("/api/v1/review/datasets/non_existent_dataset/records")
        self.assertEqual(r.status_code, 404)
        err = r.json()["error"]
        self.assertEqual(err["code"], "DATASET_NOT_FOUND")
        self.assertIn("non_existent_dataset", err["message"])

    def test_unknown_record_returns_404(self):
        r = self.client.get("/api/v1/review/datasets/items/records/9999999")
        self.assertEqual(r.status_code, 404)
        err = r.json()["error"]
        self.assertEqual(err["code"], "RECORD_NOT_FOUND")

    def test_pagination_bounds_validation(self):
        # limit < 1
        r1 = self.client.get("/api/v1/review/datasets/items/records?limit=0")
        self.assertEqual(r1.status_code, 400)
        self.assertEqual(r1.json()["error"]["code"], "INVALID_PARAMETER")

        # limit > 500
        r2 = self.client.get("/api/v1/review/datasets/items/records?limit=501")
        self.assertEqual(r2.status_code, 400)
        self.assertEqual(r2.json()["error"]["code"], "INVALID_PARAMETER")

        # offset < 0
        r3 = self.client.get("/api/v1/review/datasets/items/records?offset=-1")
        self.assertEqual(r3.status_code, 400)
        self.assertEqual(r3.json()["error"]["code"], "INVALID_PARAMETER")

    def test_invalid_order_parameter_returns_400(self):
        # Reproduce coordinator's test: ?order=wrong
        r = self.client.get("/api/v1/review/datasets/items/records?order=wrong")
        self.assertEqual(r.status_code, 400)
        err = r.json()["error"]
        self.assertEqual(err["code"], "INVALID_PARAMETER")
        self.assertIn("order", err["message"].lower())

    def test_typo_in_quarantine_parameter_returns_400(self):
        # Reproduce coordinator's test: ?record_kee=72548
        r = self.client.get("/api/v1/review/quarantine?record_kee=72548")
        self.assertEqual(r.status_code, 400)
        err = r.json()["error"]
        self.assertEqual(err["code"], "INVALID_PARAMETER")
        self.assertIn("record_kee", err["message"])

    def test_unknown_overwrites_parameter_returns_400(self):
        r = self.client.get("/api/v1/review/overwrites?invalid_param=1")
        self.assertEqual(r.status_code, 400)
        err = r.json()["error"]
        self.assertEqual(err["code"], "INVALID_PARAMETER")
        self.assertIn("invalid_param", err["message"])

    def test_unexpected_param_on_zero_arg_endpoints_returns_400(self):
        r1 = self.client.get("/api/v1/review/health?foo=bar")
        self.assertEqual(r1.status_code, 400)
        self.assertEqual(r1.json()["error"]["code"], "INVALID_PARAMETER")

        r2 = self.client.get("/api/v1/review/batch?foo=bar")
        self.assertEqual(r2.status_code, 400)
        self.assertEqual(r2.json()["error"]["code"], "INVALID_PARAMETER")

        r3 = self.client.get("/api/v1/review/datasets?foo=bar")
        self.assertEqual(r3.status_code, 400)
        self.assertEqual(r3.json()["error"]["code"], "INVALID_PARAMETER")

    def test_unknown_filter_column_returns_400(self):
        r = self.client.get("/api/v1/review/datasets/items/records?invalid_column=123")
        self.assertEqual(r.status_code, 400)
        err = r.json()["error"]
        self.assertEqual(err["code"], "INVALID_PARAMETER")
        self.assertIn("invalid_column", err["message"])

    def test_unknown_sort_column_returns_400(self):
        r = self.client.get("/api/v1/review/datasets/items/records?sort_by=invalid_column")
        self.assertEqual(r.status_code, 400)
        err = r.json()["error"]
        self.assertEqual(err["code"], "INVALID_PARAMETER")
        self.assertIn("invalid_column", err["message"])

    def test_post_method_returns_405_method_not_allowed(self):
        r = self.client.post("/api/v1/review/datasets/items/records")
        self.assertEqual(r.status_code, 405)
        err = r.json()["error"]
        self.assertEqual(err["code"], "METHOD_NOT_ALLOWED")

    def test_unhandled_route_returns_404_not_found(self):
        r = self.client.get("/api/v1/review/invalid_nonexistent_endpoint")
        self.assertEqual(r.status_code, 404)
        err = r.json()["error"]
        self.assertEqual(err["code"], "NOT_FOUND")

    def test_corrupted_batch_dir_returns_503_catalog_not_ready(self):
        # When creating app with a non-existent or corrupted batch_dir
        temp_empty_dir = tempfile.mkdtemp()
        try:
            broken_app = create_app(batch_dir=temp_empty_dir)
            broken_client = TestClient(broken_app)
            r = broken_client.get("/api/v1/review/health")
            self.assertEqual(r.status_code, 503)
            err = r.json()["error"]
            self.assertEqual(err["code"], "CATALOG_NOT_READY")
        finally:
            shutil.rmtree(temp_empty_dir)


if __name__ == "__main__":
    unittest.main()
