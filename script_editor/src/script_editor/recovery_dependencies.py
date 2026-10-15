"""Metadata and source pins only; never import GPL recovery libraries in GUI."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
from pathlib import Path

SOURCE_COMMIT = "91298ba80e322cfb8736ab8a697509527297a7a9"
SOURCE_FILENAME = f"uncompyle6-{SOURCE_COMMIT}.tar.gz"
SOURCE_SHA256 = "9e60958d4b0386e3976331ba6236ef2a1a986b2a162f3ddb9a8db424ae2e4d87"
SOURCE_URL = (
    "https://codeload.github.com/rocky/python-uncompyle6/tar.gz/" + SOURCE_COMMIT
)
RECOVERY_REQUIREMENTS = [
    ("uncompyle6", "uncompyle6 @ " + SOURCE_URL),
    ("xdis", "xdis==6.3.0"),
    ("spark_parser", "spark-parser==1.9.0"),
    ("six", "six==1.17.0"),
    ("click", "click==8.5.0"),
]
RECOVERY_VERSIONS = {
    "uncompyle6": "3.9.4.dev0",
    "xdis": "6.3.0",
    "spark_parser": "1.9.0",
    "six": "1.17.0",
    "click": "8.5.0",
}


def checked_recovery_source(root: Path) -> Path:
    path = root / "third_party" / SOURCE_FILENAME
    with path.open("rb") as stream:
        raw = stream.read(8 * 1024 * 1024 + 1)
    if len(raw) > 8 * 1024 * 1024 or hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError("恢复引擎上游源码摘要不符，拒绝安装；请完整解压新版工具")
    return path.resolve()


def installed_recovery_source_matches() -> bool:
    """A same-version dev build from some other commit is not our tested pin."""
    try:
        info = importlib.metadata.distribution("uncompyle6").read_text(
            "direct_url.json"
        )
        data = json.loads(info or "{}")
        return (
            data.get("archive_info", {}).get("hashes", {}).get("sha256")
            == SOURCE_SHA256
        )
    except (
        OSError,
        ValueError,
        TypeError,
        AttributeError,
        importlib.metadata.PackageNotFoundError,
    ):
        return False
