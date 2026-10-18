"""Local operator console. No network listener and no client file modifications."""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import shlex
import sys
import uuid
from dataclasses import asdict
from pathlib import Path

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server" / "src"))

from mxsj_server.bootstrap.local import open_local
from mxsj_server.contracts.common import DomainError
from mxsj_server.modules.account.contracts import LoginRequest
from mxsj_server.modules.character.contracts import CreateCharacter
from mxsj_server.modules.character.domain.creation import CreationPolicy
from mxsj_server.persistence.sqlite.store import SQLiteStore


def read_config(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if set(raw) != {"database", "realm_id", "session_ttl_ms", "creation"}:
        raise ValueError("Unknown or missing configuration keys")
    creation = raw["creation"]
    if set(creation) != {"max_characters", "allowed_pairs"}:
        raise ValueError("Unknown creation policy keys")
    if not isinstance(raw["database"], str) or not raw["database"]:
        raise ValueError("Invalid database path")
    if type(raw["realm_id"]) is not int or not 1 <= raw["realm_id"] <= 65535:
        raise ValueError("Invalid realm_id")
    if (
        type(raw["session_ttl_ms"]) is not int
        or not 60_000 <= raw["session_ttl_ms"] <= 86_400_000
    ):
        raise ValueError("Invalid session_ttl_ms")
    policy = CreationPolicy(
        frozenset(tuple(pair) for pair in creation["allowed_pairs"]),
        creation["max_characters"],
    )
    db = Path(raw["database"])
    if not db.is_absolute():
        db = path.absolute().parent / db
    return db, raw["realm_id"], raw["session_ttl_ms"], policy


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
            print(f"{exc.code}: {exc}")
        except ValueError:
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
            print(f"Exit revoke: {exc.code}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("command", choices=("init-db", "check", "provision", "console"))
    parser.add_argument("--account", help="Required for operator-only provision")
    args = parser.parse_args(argv)
    try:
        db, realm, ttl, policy = read_config(args.config)
        store = SQLiteStore(db)
        if args.command == "init-db":
            # Explicit operator action; creates only the selected database directory.
            db.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            store.initialize()
            print("Database schema initialized (or already current)")
        elif args.command == "check":
            store.check()
            print("Database/schema check passed; no game listener implemented yet")
        else:
            services = open_local(db, realm_id=realm, policy=policy, session_ttl_ms=ttl)
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
        return 0
    except DomainError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError, OSError):
        print(
            "Configuration/input error; check config and private data directory",
            file=sys.stderr,
        )
        return 2
    except KeyboardInterrupt:
        # No token is printed; an interrupted session expires or is replaced at login.
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
