"""Local operator console. No network listener and no client file modifications."""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import shlex
import sys
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from mxsj_local_server.core.bootstrap.local import open_local
from mxsj_local_server.core.configuration.settings import read_config
from mxsj_local_server.core.contracts.common import DomainError
from mxsj_local_server.core.modules.account.contracts import LoginRequest
from mxsj_local_server.core.modules.character.contracts import CreateCharacter
from mxsj_local_server.core.observability.events import (
    EventLogger,
    emergency,
    safe_error,
)
from mxsj_local_server.core.observability.tracing import bind
from mxsj_local_server.core.persistence.sqlite.store import SQLiteStore


def password() -> bytes:
    if not sys.stdin.isatty():
        raise ValueError("Password input requires an interactive terminal")
    return getpass.getpass("Password (not logged): ").encode("utf-8")


async def console(services):
    print("Local operator console: no game listener, no client patches.")
    print("login ACCOUNT | list | create NAME APPEARANCE SCHOOL OP_ID | logout | quit")
    print(
        "Reuse OP_ID with identical data when retrying create; ticket stays in memory."
    )
    ticket = None
    while True:
        try:
            parts = shlex.split(input("local> "))
            if not parts:
                continue
            cmd, *args = parts
            if cmd == "quit" and not args:
                break
            if cmd == "login" and len(args) == 1:
                result = await services.accounts.authenticate(
                    LoginRequest(
                        account_name=args[0],
                        credential=password(),
                        protocol_version="operator-utf8-v1",
                    )
                )
                ticket = result.session_ticket
                print(f"Authenticated account_id={result.account_id}; ticket hidden")
                continue
            if ticket is None:
                raise DomainError("UNAUTHENTICATED")
            op_id = args[3] if cmd == "create" and len(args) == 4 else uuid.uuid4().hex
            ctx = await services.sessions.context(ticket, op_id)
            if cmd == "list" and not args:
                print(
                    json.dumps(
                        [
                            asdict(v)
                            for v in await services.characters.list_characters(ctx)
                        ],
                        ensure_ascii=False,
                    )
                )
            elif cmd == "create" and len(args) == 4:
                result = await services.characters.create(
                    ctx,
                    CreateCharacter(
                        name=args[0],
                        appearance_template_id=int(args[1]),
                        school_id=int(args[2]),
                    ),
                )
                print(json.dumps(asdict(result), ensure_ascii=False))
            elif cmd == "logout" and not args:
                await services.accounts.revoke_sessions(
                    ctx, account_id=ctx.account_id, reason="operator logout"
                )
                ticket = None
                print("Session revoked")
            else:
                print("Unknown command or arguments")
        except DomainError as exc:
            print(safe_error(exc))
        except ValueError:
            services.events.emit(
                "console.rejected", outcome="failed", error_code="INVALID_ARGUMENT"
            )
            print("INVALID_ARGUMENT")
        except EOFError:
            break
    if ticket is not None:
        try:
            ctx = await services.sessions.context(ticket, uuid.uuid4().hex)
            await services.accounts.revoke_sessions(
                ctx, account_id=ctx.account_id, reason="console exit"
            )
        except DomainError as exc:
            print(f"Exit revoke: {safe_error(exc)}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("command", choices=("init-db", "check", "provision", "console"))
    parser.add_argument("--account", help="Required for operator-only provision")
    args = parser.parse_args(argv)
    events = EventLogger()  # Safe console fallback if configuration is unreadable.
    lifecycle = {"trace_id": uuid.uuid4().hex}
    result_code = 1
    started = time.monotonic_ns()
    try:
        db, realm, ttl, policy, log_options = read_config(args.config)
        # Fail startup before DB writes if required log output cannot open/lock.
        events = EventLogger.open(**log_options)
        with bind(events, realm_id=realm) as lifecycle:
            events.emit("process.start", outcome="started", **lifecycle)
            events.emit("config.validated", **lifecycle)
            store = SQLiteStore(db, events=events)
            if args.command == "init-db":
                db.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                store.initialize()
                print("Database schema initialized (or already current)")
            elif args.command == "check":
                store.check()
                print("Database/schema check passed; no game listener implemented yet")
            else:
                services = open_local(
                    db,
                    realm_id=realm,
                    policy=policy,
                    session_ttl_ms=ttl,
                    events=events,
                )
                if args.command == "provision":
                    if not args.account:
                        raise ValueError("--account is required")
                    secret = password()
                    if secret != getpass.getpass("Confirm password: ").encode("utf-8"):
                        raise ValueError("Password confirmation differs")
                    account_id = asyncio.run(
                        services.accounts.provision(args.account, secret)
                    )
                    print(f"Provisioned account_id={account_id}")
                else:
                    asyncio.run(console(services))
        result_code = 0
    except DomainError as exc:
        events.emit(
            "process.failed",
            outcome="failed",
            error_code=safe_error(exc),
            exception=exc,
            **lifecycle,
        )
        print(safe_error(exc), file=sys.stderr)
        result_code = 1
    except (ValueError, TypeError, KeyError, OSError) as exc:
        events.emit(
            "process.failed",
            outcome="failed",
            error_code="CONFIGURATION_ERROR",
            exception=exc,
            **lifecycle,
        )
        print(
            "Configuration/log setup/input error; inspect sanitized diagnostics",
            file=sys.stderr,
        )
        result_code = 2
    except KeyboardInterrupt:
        events.emit(
            "process.failed", outcome="unknown", error_code="INTERRUPTED", **lifecycle
        )
        result_code = 130
    except Exception as exc:
        events.emit(
            "process.failed",
            outcome="failed",
            error_code="INTERNAL_ERROR",
            exception=exc,
            **lifecycle,
        )
        print("INTERNAL_ERROR; inspect sanitized diagnostics", file=sys.stderr)
        result_code = 1
    finally:
        events.emit(
            "process.stop",
            outcome="succeeded" if result_code == 0 else "failed",
            duration_ms=(time.monotonic_ns() - started) // 1_000_000,
            **lifecycle,
        )
        events.close()
        if events.health()["failures"]:
            emergency()  # Explicit exit warning, without changing committed results.
    return result_code


if __name__ == "__main__":
    raise SystemExit(main())
