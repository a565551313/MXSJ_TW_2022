"""CLI Entrypoint for running Review Query API server."""

import argparse
import sys
from pathlib import Path

# Ensure repo root and server/src are on sys.path
APPS_DIR = Path(__file__).resolve().parent
REPO_ROOT = APPS_DIR.parent.parent.parent
SRC_DIR = REPO_ROOT / "server" / "src"

for p in (REPO_ROOT, SRC_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import uvicorn

try:
    from .app import create_app
    from .config import DEFAULT_HOST, DEFAULT_PORT
except ImportError:
    from server.apps.review_api.app import create_app
    from server.apps.review_api.config import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    parser = argparse.ArgumentParser(description="MXSJ Review Browser Query API Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    args = parser.parse_args()

    app = create_app()
    print(f"Starting MXSJ Review API on {args.host}:{args.port} (prefix /api/v1/review)...")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
