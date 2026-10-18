"""Check standard-library prerequisites; never initialize a DB or patch a client."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--config", type=Path)
    args = parser.parse_args(argv)
    if sys.version_info < (3, 11) or sqlite3.sqlite_version_info < (3, 24, 0):
        print("Python >=3.11 and SQLite >=3.24 required", file=sys.stderr)
        return 1
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from mxsj_local_server.core.bootstrap.local import open_local  # noqa: F401

    print(
        f"Python {sys.version.split()[0]}, SQLite {sqlite3.sqlite_version}; "
        "standard library only"
    )
    if args.check_only:
        return 0
    if args.config is None:
        print("Copy config.example.json to config.json; run init-db explicitly first.")
        return 2
    from mxsj_local_server.app import main as run

    return run(["--config", str(args.config), "console"])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # Bootstrap may fail before the local logger can even be imported.
        try:
            Path(__file__).with_name("启动日志.txt").write_text(
                "BOOTSTRAP_FAILED: check Python, dependencies and configuration.\n",
                encoding="utf-8",
            )
        except OSError:
            pass
        try:
            sys.stderr.write("BOOTSTRAP_FAILED; check local runtime prerequisites.\n")
        except OSError:
            pass
        raise SystemExit(1) from None
