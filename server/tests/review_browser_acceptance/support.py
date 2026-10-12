"""Shared helpers for Agent J's review-browser acceptance suites.

The suites live outside ``server/tests/architecture`` on purpose: they are
acceptance/regression tests for the review tool (loader/API + web page), not
architecture smoke tests, and they are run with their own command:

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance -q

No third-party dependency is required.
"""
from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'server/tools/review_browser_checks'
DOCS_REVIEW = ROOT / 'server/docs/review_browser'
API_CONTRACT = DOCS_REVIEW / 'API_CONTRACT.md'
WEB_APP = ROOT / 'server/apps/review_web'
API_APP_CANDIDATES = (ROOT / 'server/apps/review_api', ROOT / 'server/src/review',
                      ROOT / 'server/src/review_api')

sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(ROOT / 'server/tests/review_browser_acceptance'))

NOT_EXECUTED = 'not_executed'


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def wait_for_port(port: int, process: subprocess.Popen, timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def run_json(command: list[str], timeout: float = 600.0, cwd: Path | None = None) -> tuple[int, dict, str]:
    completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                               cwd=str(cwd or ROOT))
    payload = {}
    for line in reversed(completed.stdout.strip().splitlines()):
        candidate = line.strip()
        if candidate.startswith('{') and candidate.endswith('}'):
            try:
                payload = json.loads(candidate)
                break
            except json.JSONDecodeError:
                continue
    if not payload and completed.stdout.strip().startswith('{'):
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            payload = {}
    return completed.returncode, payload, completed.stdout + completed.stderr


def deliverable_state() -> dict:
    """What of the H/I deliverable is actually present in this checkout."""
    return {
        'api_contract': API_CONTRACT.is_file(),
        'api_contract_path': str(API_CONTRACT.relative_to(ROOT)),
        'web_app': WEB_APP.is_dir(),
        'web_app_path': str(WEB_APP.relative_to(ROOT)),
        'api_app': next((str(path.relative_to(ROOT)) for path in API_APP_CANDIDATES if path.is_dir()), None),
    }


def operation_map_path() -> Path | None:
    """Operation map written by the acceptor once the contract exists."""
    candidates = sorted(TOOLS.glob('ops_*.json'))
    return candidates[0] if candidates else None


def tempdir(prefix: str = 'mxsj-acceptance-') -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))
