#!/usr/bin/env python3
"""Launch the delivered review API against an arbitrary batch directory.

Agent J acceptance helper — **not a product file**. It only calls the public
factory that Agent H ships:

    server/apps/review_api/app.py::create_app(catalog)
    mxsj_catalog.catalog.ReviewCatalog.load(base_dir)

Using the official factory with an injected catalog is how the acceptance suite
points the service at a scratch copy (normal / corrupted) without editing any
product source or bypassing the product configuration. No product module is
monkey-patched, and nothing in H's directory is written.

Usage (run with an interpreter that has the API requirements installed):

    python3 server/tools/review_browser_checks/review_api_launch.py \
        --batch-dir /tmp/scratch/batch --host 0.0.0.0 --port 8100
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--batch-dir', required=True)
    parser.add_argument('--host', default=os.environ.get('REVIEW_API_HOST', '0.0.0.0'))
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '8000')))
    args = parser.parse_args(argv)

    batch_dir = Path(args.batch_dir).resolve()
    if not batch_dir.is_dir():
        print(f'batch directory does not exist: {batch_dir}', file=sys.stderr)
        return 2

    src = REPO_ROOT / 'server/src'
    for path in (REPO_ROOT, src):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    import uvicorn  # noqa: PLC0415 - only needed when actually serving

    from mxsj_catalog.catalog import ReviewCatalog  # noqa: PLC0415
    from server.apps.review_api.app import create_app  # noqa: PLC0415

    # A failing load must be visible: the process exits non-zero instead of
    # serving an empty or partially valid catalogue.
    catalog = ReviewCatalog.load(batch_dir)
    app = create_app(catalog)
    print(f'acceptance launch: batch={batch_dir} host={args.host} port={args.port}', flush=True)
    uvicorn.run(app, host=args.host, port=args.port, log_level='warning')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
