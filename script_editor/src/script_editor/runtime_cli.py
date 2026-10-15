"""Explicit release tooling. Static audit never claims Windows execution."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core.compiler.distribution import audit_runtimes, stage_runtimes


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit/stage standard Windows runtimes"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "stage"):
        command = sub.add_parser(name)
        command.add_argument(
            "--root",
            type=Path,
            required=True,
            help="Application root containing runtimes/manifest.json",
        )
        command.add_argument(
            "--static",
            action="store_true",
            help="Hash/PE/provenance only; NEVER execution acceptance",
        )
        if name == "stage":
            command.add_argument(
                "--destination",
                type=Path,
                required=True,
                help="Existing application folder; runtimes must not exist",
            )
    args = parser.parse_args(argv)
    try:
        if args.command == "audit":
            report = audit_runtimes(args.root.absolute(), execute=not args.static)
        else:
            report = stage_runtimes(
                args.root.absolute(),
                args.destination.absolute(),
                execute=not args.static,
            )
    except (OSError, ValueError) as exc:
        # No remote downloading or automatic compiler fallback on failure.
        print(
            json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=True),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
