"""Build the evidenced subset of legacy text resources, never update manifests."""

from __future__ import annotations

import ipaddress
import json
import shutil
from pathlib import Path

from mxsj_web_server.core.constants import LEGACY_ENCODING, MAX_TEXT_BYTES


def text_bytes(text: str) -> bytes:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Expected nonempty text")
    if any(ord(ch) < 32 and ch not in "\r\n\t" for ch in text):
        raise ValueError("Control characters are forbidden")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    result = (
        (normalized.rstrip("\n") + "\n").replace("\n", "\r\n").encode(LEGACY_ENCODING)
    )
    if len(result) > MAX_TEXT_BYTES:
        raise ValueError("Text is too large")
    return result


def token(value):
    if (
        not isinstance(value, str)
        or not value
        or any(ch.isspace() or ord(ch) < 32 or ch in "=#" for ch in value)
    ):
        raise ValueError("Invalid server-list token")
    value.encode(LEGACY_ENCODING)  # Strict; no silent substitution of names.
    return value


def render(raw: dict) -> dict[str, bytes]:
    if not isinstance(raw, dict) or set(raw) != {"news", "service", "groups"}:
        raise ValueError("Invalid content keys")
    groups = raw["groups"]
    if not isinstance(groups, list) or not 1 <= len(groups) <= 32:
        raise ValueError("Expected 1..32 server groups")
    lines, group_names = [], set()
    for group in groups:
        if not isinstance(group, dict) or set(group) != {"name", "servers"}:
            raise ValueError("Invalid group keys")
        name = token(group["name"])
        if name in group_names:
            raise ValueError("Duplicate group")
        group_names.add(name)
        lines.append(name)
        servers = group["servers"]
        if not isinstance(servers, list) or not 1 <= len(servers) <= 128:
            raise ValueError("Expected 1..128 servers per group")
        names = set()
        for server in servers:
            if not isinstance(server, dict) or set(server) != {
                "name",
                "ip",
                "port",
                "reserve",
                "type",
            }:
                raise ValueError("Only the five-field server-row subset is supported")
            name = token(server["name"])
            if name in names:
                raise ValueError("Duplicate server name in group")
            names.add(name)
            ip = token(server["ip"])
            ipaddress.IPv4Address(ip)  # Domains/IPv6 need independent client evidence.
            port = server["port"]
            if type(port) is not int or not 1 <= port <= 65535:
                raise ValueError("Invalid port")
            # Preserve observed opaque fields; do not interpret them as flags.
            reserve, kind = token(server["reserve"]), token(server["type"])
            lines.append(f"{name} {ip} {port} {reserve} {kind}")
    return {
        "news.txt": text_bytes(raw["news"]),
        "service.txt": text_bytes(raw["service"]),
        "server.txt": text_bytes("\n".join(lines)),
    }


def build(source: Path, destination: Path):
    # Validate all content before creating anything; publish to a NEW directory.
    source = source.absolute()
    with source.open("rb") as stream:
        data = stream.read(4 * MAX_TEXT_BYTES + 1)
    if len(data) > 4 * MAX_TEXT_BYTES:
        raise ValueError("Source is too large")
    resources = render(json.loads(data.decode("utf-8-sig")))
    destination = destination.absolute()
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError("Symlink output directory is forbidden")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination.mkdir(mode=0o700)  # Never overwrite an existing release or client root.
    try:
        for name, body in resources.items():
            with (destination / name).open("xb") as stream:
                stream.write(body)
        config = {
            "content_root": ".",
            "resources": [
                {
                    "url": "/" + name,
                    "file": name,
                    "content_type": "text/plain",
                    "max_age": 0,
                }
                for name in resources
            ],
        }
        with (destination / "config.json").open("x", encoding="utf-8") as stream:
            json.dump(config, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
    except Exception:
        shutil.rmtree(destination)
        raise
