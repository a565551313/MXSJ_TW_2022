from __future__ import annotations

import sys
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER / "src"))

from mxsj_server.contracts.common import DomainError
from mxsj_server.modules.account.contracts import LoginRequest
from mxsj_server.modules.account.validation import validate_login_request


def request(**overrides: object) -> LoginRequest:
    values: dict[str, object] = {
        "account_name": "player-1",
        "credential": b"opaque-test-credential",
        "protocol_version": "legacy-v1",
    }
    values.update(overrides)
    return LoginRequest(**values)  # type: ignore[arg-type]


class LoginRequestValidationTests(unittest.TestCase):
    def test_accepts_well_shaped_request(self) -> None:
        validate_login_request(request())

    def test_rejects_wrong_request_type(self) -> None:
        with self.assertRaises(DomainError):
            validate_login_request(object())  # type: ignore[arg-type]

    def test_account_name_must_be_nonempty_bounded_and_control_free(self) -> None:
        for value in ("", "  ", "x" * 129, "player\n1", "player\x7f1", None, 123):
            with self.subTest(value=value), self.assertRaises(DomainError):
                validate_login_request(request(account_name=value))

    def test_credential_must_be_nonempty_bytes_and_bounded(self) -> None:
        for value in (b"", b"x" * 4097, "password", None, 123):
            with self.subTest(value=repr(value)), self.assertRaises(DomainError):
                validate_login_request(request(credential=value))

    def test_protocol_version_must_be_nonempty_bounded_and_control_free(self) -> None:
        for value in ("", " ", "v" * 65, "legacy\n-v1", None, 1):
            with self.subTest(value=value), self.assertRaises(DomainError):
                validate_login_request(request(protocol_version=value))

    def test_validation_error_does_not_echo_credentials(self) -> None:
        invalid = request(credential=b"")
        with self.assertRaises(DomainError) as raised:
            validate_login_request(invalid)
        self.assertNotIn("credential", str(raised.exception).lower())
        self.assertNotIn("opaque-test-credential", repr(invalid))


if __name__ == "__main__":
    unittest.main()
