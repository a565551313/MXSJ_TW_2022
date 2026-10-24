"""Self-check and offline demo; standard library only, no dependency install."""

from __future__ import annotations

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    if sys.version_info < (3, 10):  # noqa: UP036  # Bootstrap must diagnose old Python.
        print("Python >=3.10 required: https://www.python.org/downloads/")
        return 2
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    from mxsj_native_channel.app import main as run
    from mxsj_native_channel.core.cipher import derive

    # Use explicit check instead of assert so it runs under python -O
    if derive(0).rx_key != 1442715248:
        raise RuntimeError(
            "derivation fixture mismatch: derive(0).rx_key != 1442715248"
        )
    if "--check-only" in sys.argv[1:]:
        print("PASS: standard-library runtime and derivation fixture")
        return 0
    return run(sys.argv[1:])


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        Path(__file__).with_name("启动日志.txt").write_text(
            f"{datetime.now(timezone.utc).isoformat()}\n{sys.version}\n"
            + traceback.format_exc(),
            encoding="utf-8",
        )
        traceback.print_exc()
        if sys.stdin.isatty():
            input("Press Enter to exit...")
        raise SystemExit(2) from None
