"""Frozen GUI entry point: no dependency installation."""

from __future__ import annotations

from script_editor.app import main

if __name__ == "__main__":
    raise SystemExit(main())
