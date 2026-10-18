"""Local smoke-test runner; not a production HTTP server."""

from __future__ import annotations

import argparse
import json
import sys
from wsgiref.simple_server import WSGIRequestHandler, make_server

from app import create_app


class SafeHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        # Never log URLs, query strings, headers or arbitrary exception messages.
        pass

    def log_request(self, code="-", size="-"):
        try:
            status = int(code)
        except (TypeError, ValueError):
            status = 0
        print(json.dumps({"event": "http.response", "status": status}), file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        app = create_app(args.config)
        if args.check_only:
            print("Publication configuration validated; no server started")
            return 0
        with make_server(
            args.host, args.port, app, handler_class=SafeHandler
        ) as server:
            print(
                "web_server development runner started; not a production HTTP server",
                flush=True,
            )
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except Exception:
        print(
            "WEB_SERVER_START_FAILED: inspect configuration, files and port",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
