"""Engineering limits, not recovered official protocol constants.

Legacy encoding/line-ending evidence is recorded in LEGACY_FORMATS.md.
HTTP sizes and allowlists are our bounded publication policy, not client limits.
"""

from __future__ import annotations

import re

LEGACY_ENCODING = "big5"
MAX_TEXT_BYTES = 1024 * 1024
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 32 * 1024 * 1024
ROUTE = re.compile(r"/[A-Za-z0-9_/-]+(?:\.[A-Za-z0-9_-]+)?\Z")
TYPES = frozenset(
    {"text/plain", "text/html", "application/json", "application/octet-stream"}
)
