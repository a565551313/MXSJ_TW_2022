"""Explicit server-side creation policy, not inferred original gameplay rules."""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from mxsj_local_server.core.contracts.common import DomainError
from mxsj_local_server.core.modules.character.contracts import CreateCharacter


@dataclass(frozen=True)
class CreationPolicy:
    allowed_pairs: frozenset[tuple[int, int]]
    max_characters: int
    initial_level: int = 1

    def __post_init__(self):
        if (
            type(self.max_characters) is not int
            or not 1 <= self.max_characters <= 10
            or type(self.initial_level) is not int
            or not 1 <= self.initial_level <= 255
            or not self.allowed_pairs
            or any(
                type(x) is not int or x <= 0
                for pair in self.allowed_pairs
                for x in pair
            )
            or any(len(pair) != 2 for pair in self.allowed_pairs)
        ):
            raise ValueError("Invalid creation policy")

    def validate(self, request: CreateCharacter) -> tuple[str, str]:
        name = request.name
        if (
            not isinstance(name, str)
            or name != name.strip()
            or not 2 <= len(name) <= 12
        ):
            raise DomainError(
                "INVALID_ARGUMENT", "Character name must be 2-12 characters"
            )
        name = unicodedata.normalize("NFC", name)
        if any(unicodedata.category(c)[0] in "CZ" for c in name):
            raise DomainError(
                "INVALID_ARGUMENT", "Character name has hidden/space characters"
            )
        try:
            if len(name.encode("big5", errors="strict")) > 16:
                raise ValueError("too long")
        except (UnicodeEncodeError, ValueError) as exc:
            raise DomainError(
                "INVALID_ARGUMENT", "Name must fit 16 Big5 bytes"
            ) from exc
        if (
            type(request.appearance_template_id) is not int
            or type(request.school_id) is not int
            or (request.appearance_template_id, request.school_id)
            not in self.allowed_pairs
        ):
            raise DomainError("INVALID_ARGUMENT", "Unapproved appearance/school pair")
        return name, name.casefold()
