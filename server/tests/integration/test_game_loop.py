from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER / "src"))

from mxsj_server.application.game_loop import GameLoopService
from mxsj_server.contracts.common import DomainError


class GameLoopIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.service = GameLoopService(Path(self.tempdir.name) / "game.sqlite3")
        self.service.register("player_1", "correct-horse-battery")
        self.realm = self.service.select_realm(1)
        self.login = self.service.login("PLAYER_1", "correct-horse-battery", self.realm.realm_id)
        self.ticket = self.login["session_ticket"]

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_registration_realm_login_create_select_and_enter_map(self) -> None:
        self.assertEqual(self.realm.realm_id, 1)
        self.assertEqual(self.login["session_epoch"], 1)
        created = self.service.create_character(
            self.ticket, 1, "create-op-1", "小明", school_id=1, appearance_template_id=1
        )
        self.assertEqual(created.level, 1)
        self.assertEqual(self.service.list_characters(self.ticket, 1), (created,))
        selected = self.service.select_character(self.ticket, 1, created.character_id)
        self.assertEqual(selected.character_id, created.character_id)
        entered = self.service.enter_map(self.ticket, 1)
        self.assertEqual(entered.character_id, created.character_id)
        self.assertEqual(entered.map_template_id, 1)
        self.assertEqual((entered.x, entered.y), (10, 10))
        self.assertGreater(entered.map_instance_id, 0)

    def test_registration_is_case_insensitive_and_duplicate_rejected(self) -> None:
        with self.assertRaises(DomainError) as raised:
            self.service.register("PLAYER_1", "another-correct-password")
        self.assertEqual(raised.exception.code, "CONFLICT")

    def test_bad_password_does_not_create_session(self) -> None:
        with self.assertRaises(DomainError) as raised:
            self.service.login("player_1", "wrong-password", 1)
        self.assertEqual(raised.exception.code, "UNAUTHENTICATED")

    def test_realm_must_exist_and_be_online(self) -> None:
        with self.assertRaises(DomainError) as raised:
            self.service.select_realm(999)
        self.assertEqual(raised.exception.code, "NOT_FOUND")

    def test_enter_map_requires_character_selection(self) -> None:
        with self.assertRaises(DomainError) as raised:
            self.service.enter_map(self.ticket, 1)
        self.assertEqual(raised.exception.code, "INVALID_STATE")

    def test_character_creation_is_idempotent_for_same_operation_and_payload(self) -> None:
        first = self.service.create_character(self.ticket, 1, "same-op", "Alice")
        second = self.service.create_character(self.ticket, 1, "same-op", "Alice")
        self.assertEqual(first, second)
        self.assertEqual(len(self.service.list_characters(self.ticket, 1)), 1)

    def test_idempotency_key_cannot_be_reused_for_different_payload(self) -> None:
        self.service.create_character(self.ticket, 1, "same-op", "Alice")
        with self.assertRaises(DomainError) as raised:
            self.service.create_character(self.ticket, 1, "same-op", "Bob")
        self.assertEqual(raised.exception.code, "CONFLICT")

    def test_duplicate_character_name_returns_conflict(self) -> None:
        self.service.create_character(self.ticket, 1, "name-op-1", "Alice")
        with self.assertRaises(DomainError) as raised:
            self.service.create_character(self.ticket, 1, "name-op-2", "Alice")
        self.assertEqual(raised.exception.code, "CONFLICT")

    def test_reentering_map_preserves_character_position_and_instance(self) -> None:
        character = self.service.create_character(self.ticket, 1, "map-op", "Alice")
        self.service.select_character(self.ticket, 1, character.character_id)
        first = self.service.enter_map(self.ticket, 1)
        second = self.service.enter_map(self.ticket, 1)
        self.assertEqual(first.map_instance_id, second.map_instance_id)
        self.assertEqual((first.x, first.y), (second.x, second.y))

    def test_cannot_select_another_accounts_character(self) -> None:
        other = self.service.register("player_2", "another-correct-password")
        other_login = self.service.login(other["account_name"], "another-correct-password", 1)
        character = self.service.create_character(
            other_login["session_ticket"], 1, "other-op", "OtherHero"
        )
        with self.assertRaises(DomainError) as raised:
            self.service.select_character(self.ticket, 1, character.character_id)
        self.assertEqual(raised.exception.code, "FORBIDDEN")

    def test_new_login_fences_old_ticket_and_clears_selection(self) -> None:
        character = self.service.create_character(self.ticket, 1, "first-op", "Alice")
        self.service.select_character(self.ticket, 1, character.character_id)
        replacement = self.service.login("player_1", "correct-horse-battery", 1)
        self.assertEqual(replacement["session_epoch"], self.login["session_epoch"] + 1)
        with self.assertRaises(DomainError) as raised:
            self.service.list_characters(self.ticket, 1)
        self.assertEqual(raised.exception.code, "UNAUTHENTICATED")
        with self.assertRaises(DomainError) as raised:
            self.service.enter_map(replacement["session_ticket"], 1)
        self.assertEqual(raised.exception.code, "INVALID_STATE")

    def test_password_policy_and_input_bounds(self) -> None:
        with self.assertRaises(DomainError):
            self.service.register("ab", "short")
        with self.assertRaises(DomainError):
            self.service.register("bad\nname", "correct-horse-battery")

    def test_ticket_is_not_stored_in_plaintext(self) -> None:
        import sqlite3
        with sqlite3.connect(self.service.database_path) as connection:
            stored = connection.execute(
                "SELECT ticket_hash FROM account_sessions WHERE account_id = 1 AND realm_id = 1"
            ).fetchone()[0]
        self.assertNotEqual(stored, self.ticket.encode("ascii"))
        self.assertEqual(len(stored), 32)


if __name__ == "__main__":
    unittest.main()
