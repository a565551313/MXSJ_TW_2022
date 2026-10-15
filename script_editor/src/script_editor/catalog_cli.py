"""Audit/stage only the explicitly authorized package-specific decode data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.services.bundled_catalog import audit_catalogs, stage_catalogs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "stage"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "stage":
            if args.destination is None:
                parser.error("stage requires --destination")
            report = stage_catalogs(args.root, args.destination)
        else:
            report = audit_catalogs(args.root)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}))
        return 2
    print(json.dumps({"status": "catalog-hashes-passed", "catalogs": report}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
