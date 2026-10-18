"""Explicit path services shared by source and frozen entry points."""

from __future__ import annotations

import json
from pathlib import Path


def user_directory(appdata: str | None, home: Path) -> Path:
    return (Path(appdata) if appdata else home) / "MXSJWebServer"


def initialize_example(resources: Path, destination: Path) -> Path:
    """Create a NEW editable profile from bundled fake data; never overwrite."""
    # Check inputs before creating output. Caller controls trusted local directory.
    config = json.loads(
        (resources / "config.example.json").read_text(encoding="utf-8-sig")
    )
    files = {
        "config.json": (json.dumps(config, indent=2) + "\n").encode("utf-8"),
        "content.json": (resources / "content.example.json").read_bytes(),
    }
    for entry in config["resources"]:
        files["public/" + entry["file"]] = (
            resources / "public" / entry["file"]
        ).read_bytes()
    destination = destination.absolute()
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError("Unsafe profile path")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    destination.mkdir(mode=0o700)
    for name, body in files.items():
        path = destination / name
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(body)
    return destination / "config.json"
