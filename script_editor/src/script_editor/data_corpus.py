"""CLI: cache all data.fls VM2.7 candidates without executing target modules."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core.archives.document import ArchiveDocument
from .core.compiler.runner import inspect_compiler
from .core.services.data_corpus import build_data_corpus
from .core.services.pycdc_engine import discover_pycdc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path, help="New directory; never overwritten")
    parser.add_argument("--pycdc-bundle", type=Path)
    parser.add_argument("--compiler", type=Path, help="Optional standard CPython2.7.13")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args(argv)
    compiler = inspect_compiler(args.compiler, "py27") if args.compiler else None
    engine = discover_pycdc(args.pycdc_bundle)
    with ArchiveDocument(args.archive) as archive:
        _, summary = build_data_corpus(
            archive, args.output, pycdc=engine, compiler=compiler, timeout=args.timeout
        )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
