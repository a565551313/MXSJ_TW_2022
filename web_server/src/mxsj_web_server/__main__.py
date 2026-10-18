"""Package entry point; importing the package never starts a listener."""

from __future__ import annotations

from mxsj_web_server.app import entry_main

if __name__ == "__main__":
    raise SystemExit(entry_main())
