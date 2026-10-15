"""Lexical Python2 outline. Never import, eval or execute the edited source."""

from __future__ import annotations

import io
import tokenize
from dataclasses import dataclass


@dataclass(frozen=True)
class Symbol:
    kind: str
    name: str
    line: int
    column: int


def outline(text: str) -> tuple[Symbol, ...]:
    result = []
    pending = None
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if pending is not None:
                if token.type == tokenize.NAME:
                    result.append(
                        Symbol(
                            pending.string,
                            token.string,
                            pending.start[0],
                            pending.start[1],
                        )
                    )
                pending = None
            if token.type == tokenize.NAME and token.string in {"def", "class"}:
                pending = token
    except (tokenize.TokenError, IndentationError):
        pass  # Incomplete editing buffers still have useful lexical symbols.
    return tuple(result)
