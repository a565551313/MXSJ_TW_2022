"""Configuration for Review Query API."""

import os
from pathlib import Path

API_PREFIX = "/api/v1/review"
DEFAULT_HOST = os.environ.get("REVIEW_API_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.environ.get("REVIEW_API_PORT", "8000"))

# Path to batch_001 directory
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_BATCH_DIR = REPO_ROOT / "docs" / "csv_checks" / "batch_001"
