#!/usr/bin/env python3
"""Run read-only manual gates, including the independent metadata/tool suites.

Uses the active environment (requirements-dev.txt). Does not import game modules,
recover archives or build artifacts. Missing Qt may skip GUI tests; --require-gui
makes that a failure. Passing these gates is not game/runtime acceptance.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-gui", action="store_true")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(repo / "script_manual/src"), str(repo)]
        + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
    )
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    if args.require_gui:
        env["MXSJ_MANUAL_REQUIRE_GUI"] = "1"
    python = sys.executable
    gates = [
        ("strict evidence + full inventory", [python, "-m", "mxsj_manual",
         "validate", "--verify-evidence", "--require-full-inventory",
         "--repository", str(repo)]),
        ("manual suite (GUI skips are reported, not passes)", [python, "-m",
         "unittest", "discover", "-s", "script_manual/tests", "-v"]),
        ("N1 independent signature metadata suite", [python, "-m", "unittest",
         "discover", "-s", "script_manual/inventory",
         "-p", "test_signature_metadata.py", "-v"]),
        ("isolated recovery tool synthetic suite", [python, "-m", "unittest",
         "discover", "-s", "tools/decompiler",
         "-p", "test_recover_entries.py", "-v"]),
        ("ruff (manual including spec)", [python, "-m", "ruff", "check",
         "script_manual", "script_manual/script_manual.spec"]),
        ("Windows static compatibility (not Windows runtime)", [python,
         "tools/devkit/check_windows_compat.py", "script_manual", "--strict",
         "--no-git"]),
    ]
    failures = []
    for label, command in gates:
        print(f"\n=== {label} ===", flush=True)
        try:
            code = subprocess.run(command, cwd=repo, env=env, check=False).returncode
        except OSError as exc:
            print(f"Cannot start gate: {exc}", file=sys.stderr, flush=True)
            code = 1
        if code:
            failures.append((label, code))
    if failures:
        print(f"\nFAILED GATES: {failures}", file=sys.stderr, flush=True)
        return 1
    print("\nAll six structural/test gates passed. Check GUI skips above; "
          "this does not imply semantic completeness, Windows/EXE or game acceptance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
