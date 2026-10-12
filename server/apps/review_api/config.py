"""Configuration for Review Query API."""

import os
from pathlib import Path

API_PREFIX = "/api/v1/review"
DEFAULT_HOST = os.environ.get("REVIEW_API_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.environ.get("REVIEW_API_PORT", "8000"))

# Path to batch_001 directory (can be overridden by REVIEW_BATCH_DIR environment variable)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_env_batch_dir = os.environ.get("REVIEW_BATCH_DIR")
if _env_batch_dir:
    DEFAULT_BATCH_DIR = Path(_env_batch_dir).resolve()
else:
    DEFAULT_BATCH_DIR = REPO_ROOT / "docs" / "csv_checks" / "batch_001"
