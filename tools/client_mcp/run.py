"""Run the source-tree MCP server."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from mxsj_client_mcp.run import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
