"""Local JSON-lines development gateway for the minimal game loop.

This is a new development protocol, not the original game client's wire protocol.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from mxsj_server.application.game_loop import GameLoopService
from mxsj_server.contracts.common import DomainError

_MAX_FRAME_BYTES = 16 * 1024


def _public(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {key: getattr(value, key) for key in value.__dataclass_fields__}
    if isinstance(value, tuple):
        return [_public(item) for item in value]
    if isinstance(value, list):
        return [_public(item) for item in value]
    if isinstance(value, dict):
        return {key: _public(item) for key, item in value.items()}
    return value


def dispatch(service: GameLoopService, request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        raise DomainError("INVALID_ARGUMENT", "request must be a JSON object")
    action = request.get("action")
    if not isinstance(action, str):
        raise DomainError("INVALID_ARGUMENT", "action is required")

    if action == "register":
        result = service.register(request.get("account_name"), request.get("password"))
    elif action == "list_realms":
        result = service.list_realms()
    elif action == "select_realm":
        result = service.select_realm(request.get("realm_id"))
    elif action == "login":
        result = service.login(
            request.get("account_name"), request.get("password"), request.get("realm_id")
        )
    elif action == "create_character":
        result = service.create_character(
            request.get("session_ticket"),
            request.get("realm_id"),
            request.get("operation_id"),
            request.get("name"),
            appearance_template_id=request.get("appearance_template_id", 1),
            school_id=request.get("school_id", 1),
        )
    elif action == "list_characters":
        result = service.list_characters(request.get("session_ticket"), request.get("realm_id"))
    elif action == "select_character":
        result = service.select_character(
            request.get("session_ticket"), request.get("realm_id"), request.get("character_id")
        )
    elif action == "enter_map":
        result = service.enter_map(request.get("session_ticket"), request.get("realm_id"))
    else:
        raise DomainError("INVALID_ARGUMENT", "unknown action")
    return {"ok": True, "result": _public(result)}


async def _serve_connection(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    service: GameLoopService,
) -> None:
    try:
        while True:
            try:
                line = await reader.readline()
            except (ValueError, asyncio.LimitOverrunError):
                break
            if not line:
                break
            if len(line) > _MAX_FRAME_BYTES or not line.endswith(b"\n"):
                response = {"ok": False, "error": {"code": "FRAME_TOO_LARGE", "message": "request frame too large"}}
            else:
                try:
                    request = json.loads(line.decode("utf-8"))
                    response = await asyncio.to_thread(dispatch, service, request)
                except UnicodeDecodeError:
                    response = {"ok": False, "error": {"code": "INVALID_ARGUMENT", "message": "request must be UTF-8"}}
                except json.JSONDecodeError:
                    response = {"ok": False, "error": {"code": "INVALID_ARGUMENT", "message": "malformed JSON"}}
                except DomainError as exc:
                    response = {"ok": False, "error": {"code": exc.code, "message": str(exc)}}
                except Exception:
                    # Never return exception text, SQL, credentials or stack traces to clients.
                    response = {"ok": False, "error": {"code": "INTERNAL_ERROR", "message": "internal server error"}}
            writer.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n")
            try:
                await writer.drain()
            except (ConnectionError, asyncio.CancelledError):
                break
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except ConnectionError:
            pass


async def run_server(host: str, port: int, database: str) -> None:
    service = GameLoopService(database)
    server = await asyncio.start_server(
        lambda reader, writer: _serve_connection(reader, writer, service),
        host,
        port,
        limit=_MAX_FRAME_BYTES + 1,
    )
    sockets = ", ".join(str(sock.getsockname()) for sock in (server.sockets or ()))
    print(f"development game-loop listening on {sockets}; database={database}")
    print("WARNING: JSON-lines protocol is for local development, not the original game client.")
    async with server:
        await server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the minimal game-loop development server")
    parser.add_argument("--host", default=os.environ.get("MXSJ_SERVER_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("MXSJ_SERVER_PORT", "8765")))
    parser.add_argument(
        "--database",
        default=os.environ.get("MXSJ_SERVER_DATABASE", "server/data/game-loop.sqlite3"),
    )
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    if args.host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("non-loopback bind is disabled for this development prototype")
    asyncio.run(run_server(args.host, args.port, args.database))


if __name__ == "__main__":
    main()
