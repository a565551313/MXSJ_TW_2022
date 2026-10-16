"""One-command verifier for the local development game-loop prototype."""
from __future__ import annotations

import argparse
import json
import os
import secrets
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SERVER_SRC = ROOT / "server" / "src"
PYTHON = sys.executable


def request(sock: socket.socket, file, **payload: Any) -> dict[str, Any]:
    file.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    file.flush()
    line = file.readline()
    if not line:
        raise RuntimeError("server closed the connection without a response")
    response = json.loads(line)
    if not response.get("ok"):
        error = response.get("error", {})
        raise RuntimeError(f"{payload.get('action')} failed: {error.get('code')}: {error.get('message')}")
    return response["result"]


def run_flow(host: str, port: int) -> None:
    suffix = secrets.token_hex(5)
    account = f"check_{suffix}"
    password = "LoopCheck-" + secrets.token_urlsafe(12)
    character_name = "Check" + suffix[:8]
    operation_id = "verify-" + secrets.token_hex(12)

    with socket.create_connection((host, port), timeout=5) as sock:
        sock.settimeout(5)
        with sock.makefile("rw", encoding="utf-8", newline="\n") as stream:
            registered = request(sock, stream, action="register", account_name=account, password=password)
            print(f"[PASS] Register account: {registered['account_name']}")

            realms = request(sock, stream, action="list_realms")
            if not any(item.get("realm_id") == 1 for item in realms):
                raise RuntimeError("expected development realm id=1 was not returned")
            print("[PASS] List realms")

            realm = request(sock, stream, action="select_realm", realm_id=1)
            print(f"[PASS] Select realm: {realm['name']}")

            login = request(sock, stream, action="login", account_name=account, password=password, realm_id=1)
            ticket = login["session_ticket"]
            print("[PASS] Login and receive session ticket")

            created = request(sock, stream, action="create_character", session_ticket=ticket,
                              realm_id=1, operation_id=operation_id, name=character_name)
            character_id = created["character_id"]
            print(f"[PASS] Create character: {created['name']} (id={character_id})")

            repeated = request(sock, stream, action="create_character", session_ticket=ticket,
                               realm_id=1, operation_id=operation_id, name=character_name)
            if repeated["character_id"] != character_id:
                raise RuntimeError("idempotent character creation returned a different character")
            print("[PASS] Character creation retry is idempotent")

            characters = request(sock, stream, action="list_characters", session_ticket=ticket, realm_id=1)
            if not any(item.get("character_id") == character_id for item in characters):
                raise RuntimeError("new character is missing from character list")
            print("[PASS] List characters")

            selected = request(sock, stream, action="select_character", session_ticket=ticket,
                               realm_id=1, character_id=character_id)
            if selected["character_id"] != character_id:
                raise RuntimeError("selected character id does not match")
            print("[PASS] Select character")

            entered = request(sock, stream, action="enter_map", session_ticket=ticket, realm_id=1)
            if entered["character_id"] != character_id or entered["map_template_id"] != 1:
                raise RuntimeError("map entry returned unexpected character or map")
            print(f"[PASS] Enter map: template={entered['map_template_id']} spawn=({entered['x']},{entered['y']})")


def run_unit_tests() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SERVER_SRC) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    suites = [
        ("Architecture tests", ["-m", "unittest", "discover", "-s", "server/tests/architecture", "-v"]),
        ("Account validation tests", ["-m", "unittest", "discover", "-s", "server/tests/modules/account", "-v"]),
        ("Game-loop integration tests", ["-m", "unittest", "discover", "-s", "server/tests/integration", "-v"]),
        ("TCP protocol tests", ["-m", "unittest", "discover", "-s", "server/tests/protocol", "-v"]),
    ]
    for label, args in suites:
        print(f"\n=== {label} ===", flush=True)
        completed = subprocess.run([PYTHON, *args], cwd=ROOT, env=env)
        if completed.returncode:
            raise RuntimeError(f"{label} failed (exit code {completed.returncode})")
        print(f"[PASS] {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify registration-to-map loop without third-party packages")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--database", default=str(ROOT / "server" / "data" / "verify-game-loop.sqlite3"))
    parser.add_argument("--skip-unit-tests", action="store_true")
    args = parser.parse_args()

    if args.host not in ("127.0.0.1", "::1", "localhost"):
        parser.error("only loopback addresses are supported")
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(SERVER_SRC) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    Path(args.database).parent.mkdir(parents=True, exist_ok=True)
    command = [PYTHON, "-m", "mxsj_server.bootstrap.game_server",
               "--host", args.host, "--port", str(args.port), "--database", args.database]
    server = None
    try:
        print("Starting an isolated local development server...", flush=True)
        server = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True)
        deadline = time.monotonic() + 20
        last_error = None
        while time.monotonic() < deadline:
            if server.poll() is not None:
                output = server.stdout.read() if server.stdout else ""
                raise RuntimeError(f"server exited during startup (code {server.returncode}):\n{output}")
            try:
                with socket.create_connection((args.host, args.port), timeout=0.5):
                    break
            except OSError as exc:
                last_error = exc
                time.sleep(0.25)
        else:
            raise RuntimeError(f"server did not start within 20 seconds: {last_error}")

        run_flow(args.host, args.port)
        if not args.skip_unit_tests:
            run_unit_tests()
        print("\nSUCCESS: registration -> realm -> login -> character -> map loop verified.", flush=True)
        return 0
    except Exception as exc:
        print(f"\nFAILED: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)
        if server is not None and server.stdout:
            server.stdout.close()


if __name__ == "__main__":
    raise SystemExit(main())
