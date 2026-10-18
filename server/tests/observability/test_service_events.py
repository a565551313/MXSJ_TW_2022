"""Business/transaction event ordering against real SQLite, including failures."""

from __future__ import annotations

import asyncio
import io
import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from _paths import ROOT  # noqa: F401  # Configure shared source imports.
from mxsj_server.bootstrap.local import compose
from mxsj_server.contracts.common import DomainError
from mxsj_server.modules.account.contracts import LoginRequest
from mxsj_server.modules.character.contracts import CreateCharacter
from mxsj_server.modules.character.domain.creation import CreationPolicy
from mxsj_server.observability.events import EventLogger
from mxsj_server.persistence.sqlite.repositories import OperationRepository
from mxsj_server.persistence.sqlite.store import SQLiteStore

SECRET = b"FAKE-password-must-not-be-logged"


class ServiceEventTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.console = io.StringIO()
        self.events = EventLogger.open(self.root / "logs", level="DEBUG")
        self.events.console = self.console
        self.addCleanup(self.events.close)
        self.store = SQLiteStore(self.root / "test.sqlite3", events=self.events)
        self.store.initialize()
        self.now = 1700000000000
        self.services = self.compose()
        await self.services.accounts.provision("fake_account", SECRET)
        self.login = await self.services.accounts.authenticate(self.login_request())
        self.console.seek(0)
        self.console.truncate()

    def compose(self, store=None):
        return compose(
            store or self.store,
            realm_id=1,
            policy=CreationPolicy(frozenset({(111, 1)}), 10),
            session_ttl_ms=60000,
            clock=lambda: self.now,
            events=self.events,
        )

    def login_request(self, secret=SECRET, name="fake_account"):
        return LoginRequest(
            account_name=name, credential=secret, protocol_version="operator-utf8-v1"
        )

    async def context(self, op="op-1"):
        return await self.services.sessions.context(self.login.session_ticket, op)

    def rows(self):
        return [json.loads(line) for line in self.console.getvalue().splitlines()]

    def request(self, name="HeroOne"):
        return CreateCharacter(name=name, appearance_template_id=111, school_id=1)

    async def test_committed_success_and_trace_correlation(self):
        ctx = await self.context()
        view = await self.services.characters.create(ctx, self.request())
        rows = [row for row in self.rows() if row.get("trace_id") == ctx.trace_id]
        self.assertEqual(rows[-1]["event"], "character.create")
        self.assertEqual(rows[-1]["outcome"], "succeeded")
        self.assertEqual(rows[-1]["character_id"], view.character_id)
        self.assertEqual(rows[-2]["event"], "database.transaction")
        self.assertEqual(rows[-2]["outcome"], "succeeded")
        self.assertEqual(
            rows[-1]["operation_id_sha256"], rows[-2]["operation_id_sha256"]
        )
        self.assertEqual(rows[0]["event"], "database.transaction")
        self.assertTrue(any(row["event"] == "session.context" for row in rows))

    async def test_replay_is_not_logged_as_new_create(self):
        ctx = await self.context()
        await self.services.characters.create(ctx, self.request())
        await self.services.characters.create(ctx, self.request())
        with self.assertRaises(DomainError):
            await self.services.characters.create(ctx, self.request("HeroTwo"))
        rows = [r for r in self.rows() if r["event"] == "character.create"]
        self.assertEqual(
            [r["outcome"] for r in rows], ["succeeded", "replayed", "failed"]
        )
        self.assertEqual(rows[-1]["error_code"], "IDEMPOTENCY_CONFLICT")

    async def test_failed_commit_has_no_business_success(self):
        ctx = await self.context()
        reader = sqlite3.connect(self.store.path, isolation_level=None)
        self.addCleanup(reader.close)
        reader.execute("BEGIN")
        reader.execute("SELECT * FROM characters").fetchall()
        locked = SQLiteStore(self.store.path, timeout=0.01, events=self.events)
        with self.assertRaises(DomainError):
            await self.compose(locked).characters.create(ctx, self.request())
        reader.rollback()
        rows = self.rows()
        created = [r for r in rows if r["event"] == "character.create"]
        self.assertEqual([r["outcome"] for r in created], ["failed"])
        self.assertEqual(created[0]["error_code"], "TEMPORARILY_UNAVAILABLE")
        self.assertTrue(any(r["event"] == "database.busy" for r in rows))
        self.assertEqual(await self.services.characters.list_characters(ctx), ())

    async def test_receipt_write_failure_no_success_and_no_exception_secret(self):
        ctx = await self.context()
        with patch.object(
            OperationRepository,
            "put",
            side_effect=sqlite3.OperationalError(SECRET.decode()),
        ):
            with self.assertRaises(DomainError):
                await self.services.characters.create(ctx, self.request())
        rows = [r for r in self.rows() if r["event"] == "character.create"]
        self.assertEqual([r["outcome"] for r in rows], ["failed"])
        self.assertNotIn(SECRET.decode(), self.console.getvalue())
        self.assertEqual(await self.services.characters.list_characters(ctx), ())

    async def test_runtime_log_failure_does_not_undo_or_report_failed_commit(self):
        ctx = await self.context()
        with patch.object(
            self.events.handler, "emit", side_effect=OSError("disk full")
        ):
            with patch("mxsj_server.observability.events.emergency") as fallback:
                view = await self.services.characters.create(ctx, self.request())
                fallback.assert_called_once()
        self.assertTrue(self.events.health()["degraded"])
        self.assertEqual((await self.services.characters.list_characters(ctx))[0], view)

    async def test_password_hash_ticket_account_name_and_reason_not_logged(self):
        await self.services.accounts.authenticate(self.login_request())
        with self.assertRaises(DomainError):
            await self.services.accounts.authenticate(
                self.login_request(secret=b"fake-wrong-long-password")
            )
        other_login = await self.services.accounts.authenticate(self.login_request())
        ctx = await self.services.sessions.context(
            other_login.session_ticket, "op-logout"
        )
        await self.services.accounts.revoke_sessions(
            ctx, account_id=ctx.account_id, reason=SECRET.decode()
        )
        with self.store.transaction() as uow:
            encoded = uow.accounts.by_name("fake_account").password_hash
        text = self.console.getvalue() + (self.root / "logs/server.jsonl").read_text()
        for secret in [
            SECRET.decode(),
            self.login.session_ticket,
            other_login.session_ticket,
            encoded,
            "fake_account",
            "fake-wrong-long-password",
        ]:
            self.assertNotIn(secret, text)
        self.assertTrue(
            any(
                r["event"] == "account.authenticate" and r["outcome"] == "failed"
                for r in self.rows()
            )
        )

    async def test_takeover_stale_expired_and_revocation_events(self):
        old_ctx = await self.context()
        self.login = await self.services.accounts.authenticate(self.login_request())
        with self.assertRaises(DomainError):
            await self.services.characters.create(old_ctx, self.request())
        ctx = await self.context()
        self.now += 60000
        with self.assertRaises(DomainError):
            await self.services.characters.create(ctx, self.request())
        self.login = await self.services.accounts.authenticate(self.login_request())
        ctx = await self.context("logout")
        await self.services.accounts.revoke_sessions(
            ctx, account_id=ctx.account_id, reason="test"
        )
        await self.services.accounts.revoke_sessions(
            ctx, account_id=ctx.account_id, reason="test"
        )
        events = {r["event"] for r in self.rows()}
        self.assertTrue(
            {"session.takeover", "session.stale", "session.expired"} <= events
        )
        self.assertEqual(
            [r["outcome"] for r in self.rows() if r["event"] == "account.revoke"],
            ["succeeded", "replayed"],
        )

    async def test_parallel_operations_have_isolated_worker_contexts(self):
        async def work(n):
            ctx = await self.context(f"create-{n}")
            view = await self.services.characters.create(ctx, self.request(f"Hero{n}"))
            return ctx.trace_id, view.character_id

        results = await asyncio.gather(*(work(n) for n in range(6)))
        self.assertEqual(len({trace for trace, _ in results}), 6)
        for trace, character in results:
            rows = [r for r in self.rows() if r.get("trace_id") == trace]
            created = [r for r in rows if r["event"] == "character.create"]
            self.assertEqual(len(created), 1)
            self.assertEqual(created[0]["character_id"], character)
            self.assertTrue(any(r["event"] == "database.transaction" for r in rows))

    async def test_cancelled_waiter_reports_unknown_not_rollback(self):
        ctx = await self.context()
        committed, release, finished = (
            threading.Event(),
            threading.Event(),
            threading.Event(),
        )
        base = self.store

        class PausedStore:
            @contextmanager
            def transaction(self):
                try:
                    with base.transaction() as uow:
                        yield uow
                    committed.set()
                    release.wait(5)
                finally:
                    finished.set()

        task = asyncio.create_task(
            self.compose(PausedStore()).characters.create(ctx, self.request())
        )
        try:
            self.assertTrue(await asyncio.to_thread(committed.wait, 5))
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        finally:
            release.set()
            await asyncio.to_thread(finished.wait, 5)
        rows = [r for r in self.rows() if r["event"] == "character.create"]
        self.assertEqual([r["outcome"] for r in rows], ["unknown"])
        self.assertEqual(rows[0]["error_code"], "CANCELLED_UNKNOWN")
        self.assertEqual(len(await self.services.characters.list_characters(ctx)), 1)
        await self.services.characters.create(ctx, self.request())
        self.assertEqual(
            [r for r in self.rows() if r["event"] == "character.create"][-1]["outcome"],
            "replayed",
        )
