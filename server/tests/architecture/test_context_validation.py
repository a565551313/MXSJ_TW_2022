from __future__ import annotations

import sys
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER / "src"))

from mxsj_server.contracts.common import CommandSource, DomainError, RequestContext
from mxsj_server.contracts.validation import validate_request_context


def context(**overrides: object) -> RequestContext:
    values: dict[str, object] = {
        "operation_id": "op-1",
        "trace_id": "trace-1",
        "realm_id": 1,
        "account_id": 10,
        "character_id": 20,
        "session_epoch": 3,
        "source": CommandSource.CLIENT,
    }
    values.update(overrides)
    return RequestContext(**values)  # type: ignore[arg-type]


class RequestContextValidationTests(unittest.TestCase):
    def test_accepts_authenticated_client_context(self) -> None:
        validate_request_context(context())

    def test_character_is_optional_for_character_selection_stage(self) -> None:
        validate_request_context(context(character_id=None), require_character=False)

    def test_character_command_requires_character(self) -> None:
        with self.assertRaisesRegex(DomainError, "character context required"):
            validate_request_context(context(character_id=None), require_character=True)

    def test_client_context_requires_account_and_session_epoch(self) -> None:
        for override in (
            {"account_id": None, "character_id": None, "session_epoch": None},
            {"session_epoch": None},
        ):
            with self.subTest(override=override), self.assertRaises(DomainError) as raised:
                validate_request_context(context(**override))
            self.assertEqual(raised.exception.code, "UNAUTHENTICATED")

    def test_character_and_session_epoch_require_account(self) -> None:
        for override in (
            {"account_id": None, "character_id": 20, "source": CommandSource.INTERNAL},
            {"account_id": None, "session_epoch": 3, "source": CommandSource.INTERNAL},
        ):
            with self.subTest(override=override), self.assertRaises(DomainError):
                validate_request_context(context(**override))

    def test_identifiers_must_be_nonempty_and_bounded(self) -> None:
        for field, value in (
            ("operation_id", ""),
            ("operation_id", "  "),
            ("trace_id", ""),
            ("trace_id", "x" * 129),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(DomainError):
                validate_request_context(context(**{field: value}))

    def test_numeric_identity_fields_must_be_positive_integers_not_booleans(self) -> None:
        for field, value in (
            ("realm_id", 0),
            ("realm_id", True),
            ("account_id", -1),
            ("character_id", 0),
            ("session_epoch", False),
        ):
            with self.subTest(field=field, value=value), self.assertRaises(DomainError):
                validate_request_context(context(**{field: value}))

    def test_source_must_be_enum_member(self) -> None:
        with self.assertRaises(DomainError):
            validate_request_context(context(source="client"))  # type: ignore[arg-type]

    def test_internal_context_can_omit_account_and_session(self) -> None:
        validate_request_context(
            context(
                account_id=None,
                character_id=None,
                session_epoch=None,
                source=CommandSource.INTERNAL,
            )
        )

    def test_does_not_claim_to_authorize_character_ownership(self) -> None:
        # The helper validates context shape only; ownership must be checked by the use case.
        validate_request_context(context())


if __name__ == "__main__":
    unittest.main()
