"""Shared services exercised against real temporary SQLite, not a fake database."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from _paths import ROOT
from mxsj_server.bootstrap.local import compose
from mxsj_server.contracts.common import CommandSource, DomainError
from mxsj_server.modules.account.contracts import LoginRequest
from mxsj_server.modules.character.contracts import CreateCharacter
from mxsj_server.modules.character.domain.creation import CreationPolicy
from mxsj_server.persistence.sqlite.repositories import OperationRepository
from mxsj_server.persistence.sqlite.store import SQLiteStore

SECRET = b"fake-local-password-123"


def request(name="HeroOne", appearance=111, school=1):
    return CreateCharacter(
        name=name, appearance_template_id=appearance, school_id=school
    )


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "local.sqlite3"
        self.store = SQLiteStore(self.db)
        self.store.initialize()
        self.now = 1_700_000_000_000
        self.policy = CreationPolicy(frozenset({(111, 1)}), 2)
        self.services = self.build()
        self.account_id = await self.services.accounts.provision("player_one", SECRET)
        self.login = await self.authenticate()

    def build(self, *, realm=1, store=None):
        return compose(
            store or self.store,
            realm_id=realm,
            policy=self.policy,
            session_ttl_ms=60_000,
            clock=lambda: self.now,
        )

    async def authenticate(
        self, *, name="player_one", credential=SECRET, services=None
    ):
        return await (services or self.services).accounts.authenticate(
            LoginRequest(
                account_name=name,
                credential=credential,
                protocol_version="operator-utf8-v1",
            )
        )

    async def ctx(self, op="create-1", *, ticket=None, character=None):
        return await self.services.sessions.context(
            ticket or self.login.session_ticket,
            op,
            character_id=character,
        )

    def assert_code(self, code):
        test = self

        class ErrorContext:
            def __enter__(self):
                return self

            def __exit__(self, typ, value, traceback):
                if value is None:
                    test.fail(f"Expected {code}")
                test.assertIsInstance(value, DomainError)
                test.assertEqual(value.code, code)
                return True

        return ErrorContext()

    async def test_unknown_account_is_not_registered(self):
        with self.assert_code("UNAUTHENTICATED"):
            await self.authenticate(name="missing_user")
        with self.store.transaction() as uow:
            self.assertIsNone(uow.accounts.by_name("missing_user"))

    async def test_wrong_password_rejected(self):
        with self.assert_code("UNAUTHENTICATED"):
            await self.authenticate(credential=b"wrong-but-valid-length")

    async def test_account_case_collision_and_policy(self):
        with self.assert_code("ALREADY_EXISTS"):
            await self.services.accounts.provision("PLAYER_ONE", SECRET)
        for value in (b"short", b"x" * 129, b"x" * 12 + b"\x00", b"\xff" * 12):
            with self.assert_code("INVALID_ARGUMENT"):
                await self.services.accounts.provision("second_one", value)

    async def test_legacy_credential_not_silently_treated_as_password(self):
        with self.assert_code("UNSUPPORTED_PROTOCOL"):
            await self.services.accounts.authenticate(
                LoginRequest(
                    account_name="player_one",
                    credential=SECRET,
                    protocol_version="legacy",
                )
            )

    async def test_database_has_neither_password_nor_raw_ticket(self):
        data = self.db.read_bytes()
        self.assertNotIn(SECRET, data)
        self.assertNotIn(self.login.session_ticket.encode(), data)
        self.assertNotIn(self.login.session_ticket, repr(self.login))
        with self.store.transaction() as uow:
            stored = uow.accounts.by_name("player_one")
            self.assertTrue(stored.password_hash.startswith("scrypt-v1$"))
            self.assertNotIn(stored.password_hash, repr(stored))

    async def test_login_replaces_old_ticket_and_fences_queued_context(self):
        old_ctx = await self.ctx()
        newer = await self.authenticate()
        self.assertNotEqual(newer.session_ticket, self.login.session_ticket)
        with self.assert_code("UNAUTHENTICATED"):
            await self.ctx()
        with self.assert_code("UNAUTHENTICATED"):
            await self.services.characters.create(old_ctx, request())

    async def test_expiry_checked_again_inside_mutation(self):
        ctx = await self.ctx()
        self.now += 60_000
        with self.assert_code("UNAUTHENTICATED"):
            await self.services.characters.create(ctx, request())
        with self.assert_code("UNAUTHENTICATED"):
            await self.ctx()

    async def test_revoke_survives_restart(self):
        ctx = await self.ctx("logout")
        receipt = await self.services.accounts.revoke_sessions(
            ctx,
            account_id=self.account_id,
            reason="test",
        )
        self.assertGreater(receipt.revision, ctx.session_epoch)
        self.services = self.build()
        with self.assert_code("UNAUTHENTICATED"):
            await self.ctx()
        fresh = await self.authenticate()
        latest = await self.ctx(ticket=fresh.session_ticket)
        self.assertGreater(latest.session_epoch, receipt.revision)

    async def test_revoke_retry_returns_receipt_without_revoking_new_login(self):
        ctx = await self.ctx("logout-1")
        first = await self.services.accounts.revoke_sessions(
            ctx,
            account_id=self.account_id,
            reason="test",
        )
        self.login = await self.authenticate()
        replay = await self.services.accounts.revoke_sessions(
            ctx,
            account_id=self.account_id,
            reason="test",
        )
        self.assertEqual(first, replay)
        await self.ctx()  # A retry of old logout must not revoke the new epoch.
        with self.assert_code("IDEMPOTENCY_CONFLICT"):
            await self.services.accounts.revoke_sessions(
                ctx,
                account_id=self.account_id,
                reason="different",
            )

    async def test_cannot_revoke_someone_else(self):
        with self.assert_code("FORBIDDEN"):
            await self.services.accounts.revoke_sessions(
                await self.ctx(),
                account_id=self.account_id + 1,
                reason="test",
            )

    async def test_create_is_persistent_after_new_service_and_connection(self):
        view = await self.services.characters.create(await self.ctx(), request())
        fresh = self.build(store=SQLiteStore(self.db))
        ctx = await fresh.sessions.context(self.login.session_ticket, "list")
        self.assertEqual(await fresh.characters.list_characters(ctx), (view,))

    async def test_session_and_character_survive_a_fresh_python_process(self):
        view = await self.services.characters.create(await self.ctx(), request())
        script = """
import asyncio, sys
from pathlib import Path
from mxsj_server.bootstrap.local import open_local
from mxsj_server.modules.character.domain.creation import CreationPolicy
from mxsj_server.bootstrap.local import compose
from mxsj_server.persistence.sqlite.store import SQLiteStore
async def main():
    store = SQLiteStore(Path(sys.argv[1]))
    store.check()
    services = compose(store, realm_id=1,
        policy=CreationPolicy(frozenset({(111,1)}),2),
        session_ttl_ms=60000, clock=lambda: 1700000000000)
    ctx = await services.sessions.context(sys.stdin.read(), "restart-list")
    print((await services.characters.list_characters(ctx))[0].character_id)
asyncio.run(main())
"""
        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "-c", script, str(self.db)],
            input=self.login.session_ticket,
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PYTHONPATH": str(ROOT / "server/src")},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), str(view.character_id))
        self.assertNotIn(self.login.session_ticket, result.stdout + result.stderr)

    async def test_same_key_same_payload_returns_original_receipt_after_relogin(self):
        ctx = await self.ctx()
        view = await self.services.characters.create(ctx, request())
        self.login = await self.authenticate()
        replay = await self.services.characters.create(await self.ctx(), request())
        self.assertEqual(view, replay)
        self.assertEqual(
            len(await self.services.characters.list_characters(await self.ctx())), 1
        )

    async def test_same_key_different_payload_rejected(self):
        ctx = await self.ctx()
        await self.services.characters.create(ctx, request())
        with self.assert_code("IDEMPOTENCY_CONFLICT"):
            await self.services.characters.create(ctx, request("HeroTwo"))

    async def test_parallel_duplicate_is_one_character(self):
        ctx = await self.ctx()
        result = await asyncio.gather(
            *[self.services.characters.create(ctx, request()) for _ in range(8)]
        )
        self.assertTrue(all(v == result[0] for v in result))
        self.assertEqual(len(await self.services.characters.list_characters(ctx)), 1)

    async def test_parallel_same_name_different_keys_has_one_winner(self):
        contexts = [await self.ctx(f"create-{n}") for n in range(5)]
        results = await asyncio.gather(
            *[self.services.characters.create(ctx, request()) for ctx in contexts],
            return_exceptions=True,
        )
        self.assertEqual(sum(not isinstance(x, Exception) for x in results), 1)
        self.assertTrue(
            all(
                not isinstance(x, Exception)
                or isinstance(x, DomainError)
                and x.code == "NAME_TAKEN"
                for x in results
            )
        )

    async def test_name_uniqueness_and_character_limit(self):
        await self.services.characters.create(await self.ctx("one"), request("HeroOne"))
        with self.assert_code("NAME_TAKEN"):
            await self.services.characters.create(
                await self.ctx("two"), request("heroone")
            )
        await self.services.characters.create(await self.ctx("two"), request("HeroTwo"))
        with self.assert_code("CHARACTER_LIMIT"):
            await self.services.characters.create(
                await self.ctx("three"), request("HeroThree")
            )
        # Retry still succeeds at capacity because receipt is checked before limit.
        await self.services.characters.create(await self.ctx("one"), request("HeroOne"))

    async def test_invalid_character_inputs(self):
        for req in (
            request("x"),
            request(" space"),
            request("A\x00B"),
            request("夢" * 9),
            request("hello😀"),
            request(appearance=999),
            request(school=True),
            request(school=2),
        ):
            with self.assert_code("INVALID_ARGUMENT"):
                await self.services.characters.create(await self.ctx(), req)

    async def test_other_account_cannot_select_or_enter_role(self):
        view = await self.services.characters.create(await self.ctx(), request())
        await self.services.accounts.provision("player_two", SECRET)
        other = await self.authenticate(name="player_two")
        with self.assert_code("FORBIDDEN"):
            await self.ctx(ticket=other.session_ticket, character=view.character_id)
        ctx = await self.ctx(ticket=other.session_ticket)
        self.assertEqual(await self.services.characters.list_characters(ctx), ())
        with self.assert_code("FORBIDDEN"):
            await self.services.characters.enter_world(
                ctx, character_id=view.character_id
            )

    async def test_enter_world_does_not_fake_success(self):
        view = await self.services.characters.create(await self.ctx(), request())
        with self.assert_code("NOT_IMPLEMENTED"):
            await self.services.characters.enter_world(
                await self.ctx(), character_id=view.character_id
            )

    async def test_wrong_realm_or_admin_source_cannot_bypass_fence(self):
        ctx = await self.ctx()
        for forged in (
            replace(ctx, realm_id=2),
            replace(ctx, source=CommandSource.ADMIN),
            replace(ctx, session_epoch=99),
            replace(ctx, account_id=None),
        ):
            with self.assert_code("UNAUTHENTICATED"):
                await self.services.characters.create(forged, request())
        other_realm = self.build(realm=2)
        with self.assert_code("UNAUTHENTICATED"):
            await other_realm.sessions.context(self.login.session_ticket, "x")
        second = await self.authenticate(services=other_realm)
        await self.ctx()  # Realm 2 login must not revoke realm 1.
        ctx2 = await other_realm.sessions.context(second.session_ticket, "create-1")
        self.assertEqual(await other_realm.characters.list_characters(ctx2), ())

    async def test_invalid_ticket_and_operation_id(self):
        for ticket in ("", "x" * 42, "x" * 44, "?" * 43, "A" * 43):
            with self.assert_code("UNAUTHENTICATED"):
                await self.services.sessions.context(ticket, "test")
        with self.assert_code("INVALID_ARGUMENT"):
            await self.ctx("bad\nkey")

    async def test_receipt_write_failure_rolls_back_character(self):
        with patch.object(
            OperationRepository,
            "put",
            side_effect=sqlite3.OperationalError("disk failure"),
        ):
            with self.assert_code("STORAGE_ERROR"):
                await self.services.characters.create(await self.ctx(), request())
        self.assertEqual(
            await self.services.characters.list_characters(await self.ctx()), ()
        )
        # Same operation can now complete; failed transaction left no receipt.
        await self.services.characters.create(await self.ctx(), request())

    async def test_exception_after_yield_rolls_back_and_never_returns_success(self):
        base = self.store

        class FailingStore:
            @contextmanager
            def transaction(self):
                with base.transaction() as uow:
                    yield uow
                    raise DomainError("STORAGE_ERROR", "before commit")

        services = self.build(store=FailingStore())
        ctx = await self.ctx()
        with self.assert_code("STORAGE_ERROR"):
            await services.characters.create(ctx, request())
        self.assertEqual(await self.services.characters.list_characters(ctx), ())

    async def test_busy_database_is_bounded_and_retryable(self):
        ctx = await self.ctx()
        locked = sqlite3.connect(self.db, isolation_level=None)
        self.addCleanup(locked.close)
        locked.execute("BEGIN IMMEDIATE")
        services = self.build(store=SQLiteStore(self.db, timeout=0.01))
        with self.assert_code("TEMPORARILY_UNAVAILABLE"):
            await services.characters.create(ctx, request())
        locked.rollback()
        await services.characters.create(ctx, request())

    async def test_actual_commit_failure_does_not_acknowledge(self):
        # DELETE journal: a reader lets BEGIN IMMEDIATE run, but blocks COMMIT.
        ctx = await self.ctx()
        reader = sqlite3.connect(self.db, isolation_level=None)
        self.addCleanup(reader.close)
        reader.execute("BEGIN")
        reader.execute("SELECT * FROM characters").fetchall()
        services = self.build(store=SQLiteStore(self.db, timeout=0.01))
        with self.assert_code("TEMPORARILY_UNAVAILABLE"):
            await services.characters.create(ctx, request())
        reader.rollback()
        self.assertEqual(await self.services.characters.list_characters(ctx), ())
        await services.characters.create(ctx, request())


class StoreAndCLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "local.sqlite3"
        self.store = SQLiteStore(self.db)

    def test_missing_db_is_not_created_by_check(self):
        with self.assertRaises(DomainError):
            self.store.check()
        self.assertFalse(self.db.exists())

    def test_initialization_is_idempotent(self):
        self.store.initialize()
        self.store.initialize()
        self.store.check()
        with self.store.transaction() as uow:
            self.assertIsNone(uow.accounts.by_name("anything"))

    def test_foreign_database_is_not_replaced(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute("CREATE TABLE unrelated (x)")
            conn.execute("INSERT INTO unrelated VALUES (42)")
        before = hashlib.sha256(self.db.read_bytes()).digest()
        with self.assertRaises(DomainError):
            self.store.initialize()
        self.assertEqual(hashlib.sha256(self.db.read_bytes()).digest(), before)

    def test_corrupt_database_is_not_replaced(self):
        self.db.write_bytes(b"not a sqlite file")
        with self.assertRaises(DomainError):
            self.store.initialize()
        self.assertEqual(self.db.read_bytes(), b"not a sqlite file")

    def test_future_schema_and_checksum_are_rejected(self):
        self.store.initialize()
        with sqlite3.connect(self.db) as conn:
            conn.execute("PRAGMA user_version=999")
        with self.assertRaises(DomainError):
            self.store.check()
        with self.assertRaises(DomainError):
            self.store.initialize()
        with sqlite3.connect(self.db) as conn:
            conn.execute("PRAGMA user_version=1")
            conn.execute("UPDATE schema_migrations SET checksum='bad'")
        with self.assertRaises(DomainError):
            self.store.check()

    def test_foreign_keys_enforced_and_rollback(self):
        self.store.initialize()
        with self.assertRaises(DomainError):
            with self.store.transaction() as uow:
                uow.characters.insert(999, 1, "Hero", "hero", 111, 1, 1)
        with self.store.transaction() as uow:
            self.assertEqual(uow.characters.list_owned(999, 1), ())

    def test_bad_suffix_and_aliases_rejected(self):
        with self.assertRaises(ValueError):
            SQLiteStore(self.root / "script.fls")
        self.store.initialize()
        alias = self.root / "alias.sqlite3"
        os.link(self.db, alias)
        with self.assertRaises(ValueError):
            SQLiteStore(alias)
        alias.unlink()
        try:
            alias.symlink_to(self.db)
        except OSError:
            self.skipTest("Host does not allow symbolic links")
        with self.assertRaises(ValueError):
            SQLiteStore(alias)

    def test_cli_subprocess_init_check_and_noninteractive_provision(self):
        config = self.root / "config.json"
        raw = json.loads(
            (ROOT / "local_server/config.example.json").read_text(encoding="utf-8")
        )
        raw["database"] = "local.sqlite3"
        config.write_text(json.dumps(raw), encoding="utf-8")
        cmd = [
            sys.executable,
            str(ROOT / "local_server/run.py"),
            "--config",
            str(config),
        ]
        result = subprocess.run(cmd + ["check"], capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.db.exists())
        for command in ("init-db", "check"):
            result = subprocess.run(cmd + [command], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(
            cmd + ["provision", "--account", "player_one"],
            input=b"fake-password",
            capture_output=True,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(b"fake-password", result.stdout + result.stderr)
        raw["realm_id"] = True
        config.write_text(json.dumps(raw), encoding="utf-8")
        result = subprocess.run(cmd + ["check"], capture_output=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_bootstrap_check_only_has_no_database_side_effect(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "local_server/bootstrap.py"), "--check-only"],
            cwd=self.root,
            capture_output=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(self.root.iterdir()), [])
