"""Read-only WSGI origin with an explicit, startup-snapshotted publication map."""

from __future__ import annotations

import hashlib
import json
import stat
from dataclasses import dataclass
from pathlib import Path

from mxsj_web_server.core.constants import (
    MAX_FILE_BYTES,
    MAX_TOTAL_BYTES,
    ROUTE,
    TYPES,
)


@dataclass(frozen=True)
class Asset:
    body: bytes
    content_type: str
    etag: str
    cache_control: str


def load_assets(config: Path) -> dict[str, Asset]:
    """Fail startup on invalid publication; no automatic client-file discovery."""
    config = config.absolute()
    raw = json.loads(config.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict) or set(raw) != {"content_root", "resources"}:
        raise ValueError("Invalid configuration keys")
    root_value = raw["content_root"]
    if not isinstance(root_value, str) or not root_value:
        raise ValueError("Invalid content root")
    root = Path(root_value)
    if not root.is_absolute():
        root = config.parent / root
    if any(p.is_symlink() for p in (root, *root.parents)):
        raise ValueError("Symlink root is not allowed")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Content root must be a directory")
    resources = raw["resources"]
    if not isinstance(resources, list) or len(resources) > 128:
        raise ValueError("Invalid resource list")
    result = {}
    total = 0
    for entry in resources:
        if not isinstance(entry, dict) or set(entry) != {
            "url",
            "file",
            "content_type",
            "max_age",
        }:
            raise ValueError("Invalid resource keys")
        url, filename = entry["url"], entry["file"]
        if (
            not isinstance(url, str)
            or not ROUTE.fullmatch(url)
            or "//" in url
            or url.endswith("/")
            or url == "/healthz"
            or url in result
        ):
            raise ValueError("Invalid or duplicate resource URL")
        if (
            not isinstance(filename, str)
            or not filename
            or "\\" in filename
            or ":" in filename
        ):
            raise ValueError("Invalid resource filename")
        relative = Path(filename)
        if relative.is_absolute() or any(p in {".", ".."} for p in filename.split("/")):
            raise ValueError("Resource must remain under content root")
        path = root / relative
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError("Symlink resource is not allowed")
        path = path.resolve(strict=True)
        if not path.is_relative_to(root):
            raise ValueError("Resource escapes content root")
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Resource must be a non-aliased regular file")
        if info.st_size > MAX_FILE_BYTES:
            raise ValueError("Resource too large; use a separate download origin")
        content_type = entry["content_type"]
        age = entry["max_age"]
        if not isinstance(content_type, str) or content_type not in TYPES:
            raise ValueError("Unsupported content type")
        if type(age) is not int or not 0 <= age <= 86400:
            raise ValueError("Invalid cache lifetime")
        # Operator-owned publication directory, not hostile concurrent writers.
        with path.open("rb") as stream:
            body = stream.read(MAX_FILE_BYTES + 1)
        total += len(body)
        if len(body) > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("Publication snapshot too large")
        etag = '"' + hashlib.sha256(body).hexdigest() + '"'
        result[url] = Asset(
            body, content_type, etag, f"public, max-age={age}, must-revalidate"
        )
    return result


class Application:
    """No database, upload, admin API, filesystem routing or runtime file writes."""

    def __init__(self, assets: dict[str, Asset]):
        self.assets = dict(assets)

    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "")
        headers = [("X-Content-Type-Options", "nosniff")]
        if method not in {"GET", "HEAD"}:
            status, body = "405 Method Not Allowed", b"Method not allowed\n"
            headers += [("Allow", "GET, HEAD"), ("Cache-Control", "no-store")]
        elif path == "/healthz":
            status, body = "200 OK", b'{"status":"ok","service":"web_server"}\n'
            headers += [
                ("Content-Type", "application/json"),
                ("Cache-Control", "no-store"),
            ]
        elif path not in self.assets:
            status, body = "404 Not Found", b"Not found\n"
            headers += [("Cache-Control", "no-store")]
        else:
            asset = self.assets[path]
            # A query is ignored, never reflected or used to choose a file.
            candidates = environ.get("HTTP_IF_NONE_MATCH", "").split(",")
            matches = any(
                v.strip().removeprefix("W/") in {asset.etag, "*"} for v in candidates
            )
            status, body = (
                ("304 Not Modified", b"") if matches else ("200 OK", asset.body)
            )
            headers += [
                ("Content-Type", asset.content_type),
                ("ETag", asset.etag),
                ("Cache-Control", asset.cache_control),
            ]
            if asset.content_type == "text/html":
                headers += [
                    (
                        "Content-Security-Policy",
                        "default-src 'none'; frame-ancestors 'none'",
                    )
                ]
        if not any(k == "Content-Type" for k, _ in headers):
            headers.append(("Content-Type", "text/plain"))
        if not status.startswith("304"):
            headers.append(("Content-Length", str(len(body))))
        if status.startswith("304"):
            headers = [(k, v) for k, v in headers if k != "Content-Type"]
        start_response(status, headers)
        return [] if method == "HEAD" or status.startswith("304") else [body]


def create_app(config_path: str | Path) -> Application:
    return Application(load_assets(Path(config_path)))
