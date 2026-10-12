#!/usr/bin/env python3
"""Read-only structural reader for module-level literal assignments in `script.fls`.

Why this module exists
----------------------
The earlier reader (`server/tools/review_client_data_boundaries.py`) had two
limitations that changed a research conclusion about entry 3205
(`script/data/petskill.py`):

1. It only recognized `STORE_NAME` (opcode 90) as the statement that publishes a
   module-level table, so a `STORE_GLOBAL` (opcode 97) table was reported as
   "missing".  Entry 3205 publishes `DATA` and `ICON_MAPPING` with
   `STORE_GLOBAL`.
2. It refused to evaluate a literal that stores the same dictionary key twice
   (`ValueError: duplicate dictionary key ...`).  Refusing is the right default
   -- silently keeping only the last write would hide evidence -- but it must not
   be the only behaviour: `petskill.py` really writes 9 skill IDs twice in its
   source, the second write wins at runtime, and the evidence of the first write
   has to survive.

This module therefore:

* recognizes both `STORE_NAME` and `STORE_GLOBAL`;
* keeps every dictionary write as an ordered `WriteEvent` (position, old value,
  new value, insert/overwrite), per dictionary, so duplicates are neither
  dropped nor silently resolved;
* evaluates the module-level literal code with a strict stack machine, which
  checks constant/name indices, stack shape (underflow, container type before
  `STORE_SUBSCR`, empty stack at module end) and the literal grammar, and reports
  the exact offset and opcode of every shape it cannot accept.

It never executes recovered code: values are rebuilt from `co_consts` with plain
Python containers.  Nothing in this module writes to disk.

The opcode numbers below are this repository's labels produced by
`tools/decompiler/batch_decompile.py`, and the operand convention of
`STORE_SUBSCR` (TOS = key, SECOND = container, THIRD = value) is the one the
existing reader already uses; the machine additionally *validates* it by
requiring the container to be a dictionary.
"""
from __future__ import annotations

import collections
import dataclasses
from typing import Any, Iterator

STORE_NAME = 90
STORE_GLOBAL = 97
LOAD_CONST = 100
BUILD_TUPLE = 102
BUILD_LIST = 103
BUILD_MAP = 104
DUP_TOP = 4
ROT_TWO = 2
ROT_THREE = 3
STORE_SUBSCR = 60
POP_TOP = 1
NOP = 9
IMPORT_STAR = 84
IMPORT_NAME = 107
IMPORT_FROM = 108
MAKE_FUNCTION = 132
RETURN_VALUE = 83
EXTENDED_ARG = 143
HAVE_ARGUMENT = 90

STORE_OPS = (STORE_NAME, STORE_GLOBAL)
VALUE_OPS = (LOAD_CONST, BUILD_MAP, BUILD_TUPLE, BUILD_LIST)

# Opcodes a module body may contain while it only builds literal tables, declares
# functions and returns.  Anything else (control flow, calls, attributes, ...)
# is recorded as a violation by the strict machine.
ALLOWED_OPS = frozenset({
    LOAD_CONST, BUILD_MAP, BUILD_LIST, BUILD_TUPLE, DUP_TOP, ROT_TWO, ROT_THREE,
    STORE_SUBSCR, STORE_NAME, STORE_GLOBAL, POP_TOP, MAKE_FUNCTION, RETURN_VALUE,
    IMPORT_NAME, IMPORT_FROM, IMPORT_STAR,
})

OPCODE_NAMES = {
    1: 'POP_TOP', 2: 'ROT_TWO', 3: 'ROT_THREE', 4: 'DUP_TOP', 9: 'NOP',
    60: 'STORE_SUBSCR', 80: 'BREAK_LOOP', 83: 'RETURN_VALUE', 84: 'IMPORT_STAR',
    89: 'BUILD_CLASS', 90: 'STORE_NAME', 97: 'STORE_GLOBAL', 100: 'LOAD_CONST',
    102: 'BUILD_TUPLE', 103: 'BUILD_LIST', 104: 'BUILD_MAP',
    107: 'IMPORT_NAME', 108: 'IMPORT_FROM', 119: 'CONTINUE_LOOP',
    132: 'MAKE_FUNCTION', 136: 'LOAD_LOCALS', 143: 'EXTENDED_ARG',
}


class _Stop(Exception):
    """Internal: stop the strict machine at the first violation."""


class _Opaque:
    """A value the reader cannot rebuild literally (e.g. a function object)."""

    def __init__(self, kind: str):
        self.kind = kind

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f'<{self.kind}>'


class LiteralSyntaxError(ValueError):
    """A bytecode shape that is not a well-formed module-level literal statement."""

    def __init__(self, at: int, op: int | None, reason: str, expected: str | None = None):
        self.at = at
        self.op = op
        self.reason = reason
        self.expected = expected
        name = OPCODE_NAMES.get(op, '?')
        detail = f'opcode {op} ({name})' if op is not None else 'end of code'
        if expected:
            detail += f', expected {expected}'
        super().__init__(f'{reason} at {at}: {detail}')

    def as_dict(self) -> dict:
        return {'at': self.at, 'op': self.op, 'op_name': OPCODE_NAMES.get(self.op, '?'),
                'reason': self.reason, 'expected': self.expected, 'message': str(self)}


@dataclasses.dataclass(frozen=True)
class WriteEvent:
    """One `STORE_SUBSCR` into a literal dictionary, in execution order."""

    order: int
    at: int
    kind: str            # 'insert' | 'overwrite'
    key: Any
    old: Any             # None when the write inserted the key
    new: Any

    @property
    def overwrote(self) -> bool:
        return self.kind == 'overwrite'


@dataclasses.dataclass(frozen=True)
class Assignment:
    """A module-level literal assignment published by STORE_NAME or STORE_GLOBAL."""

    name: bytes
    store_op: int
    store_at: int
    value: Any
    writes: tuple
    #: False when the module scan could not read the whole body, i.e. this value was
    #: published before a shape the reader does not accept.  A partial value must
    #: never be presented as fully verified.
    verified: bool = True
    #: The violations of the scan that produced this assignment (empty when complete).
    violations: tuple = ()

    @property
    def store_kind(self) -> str:
        return 'STORE_NAME' if self.store_op == STORE_NAME else 'STORE_GLOBAL'

    @property
    def overwrites(self) -> tuple:
        return tuple(w for w in self.writes if w.overwrote)

    @property
    def duplicate_keys(self) -> tuple:
        return tuple(dict.fromkeys(w.key for w in self.overwrites))

    @property
    def partial(self) -> bool:
        return not self.verified


@dataclasses.dataclass(frozen=True)
class Statement:
    """A top-level statement that is not a literal table assignment."""

    at: int
    op: int
    arg: int | None
    kind: str            # 'function_definition' | 'opaque_assignment' | 'return'

    @property
    def name(self):
        return None


@dataclasses.dataclass
class ScanResult:
    assignments: list
    statements: list
    violations: list
    stack_depth_max: int = 0

    def by_name(self, name: bytes) -> Assignment | None:
        for assignment in self.assignments:
            if assignment.name == name:
                return assignment
        return None

    @property
    def violation_histogram(self) -> dict:
        return dict(collections.Counter(
            f'opcode {v.op} ({OPCODE_NAMES.get(v.op, "?")})' if v.op is not None
            else v.reason for v in self.violations))

    @property
    def first_violation(self) -> LiteralSyntaxError | None:
        return self.violations[0] if self.violations else None

    @property
    def complete(self) -> bool:
        """True only when the whole module body was read without a violation."""
        return not self.violations


def instructions(co) -> Iterator[tuple]:
    """Walk normalised Python 2.5 bytecode. Yields (offset, opcode, arg|None)."""
    code = co['code']
    at = 0
    extension = 0
    while at < len(code):
        start = at
        op = code[at]
        at += 1
        if op >= HAVE_ARGUMENT:
            if at + 2 > len(code):
                raise LiteralSyntaxError(start, op, 'truncated instruction')
            arg = int.from_bytes(code[at:at + 2], 'little') | extension
            at += 2
            if op == EXTENDED_ARG:
                extension = arg << 16
                continue
            extension = 0
        else:
            if extension:
                raise LiteralSyntaxError(start, op,
                                         'EXTENDED_ARG before argument-free instruction')
            arg = None
        yield start, op, arg
    if extension:
        raise LiteralSyntaxError(len(code), None, 'dangling EXTENDED_ARG')


def scan_module(co) -> ScanResult:
    """Evaluate a transpiled module body with a strict literal stack machine.

    Reading stops at the *first* shape the machine cannot accept: values the body
    publishes after that offset are not read, because the instruction stream no
    longer describes literal tables.  A violation is a statement about the
    decoded bytes only; it is not by itself a claim about the client's source.
    """
    try:
        stream = list(instructions(co))
    except LiteralSyntaxError as exc:
        return ScanResult([], [], [exc])

    consts, names = co['consts'], co['names']
    stack: list = []
    live: list = []                       # keeps dictionary ids stable
    writes_of: dict = {}                  # id(dict) -> [WriteEvent]
    assignments: list = []
    statements: list = []
    violations: list = []
    depth_max = 0

    class _MachineStop(Exception):
        pass

    def violation(at, op, reason, expected=None):
        violations.append(LiteralSyntaxError(at, op, reason, expected))
        raise _MachineStop

    def pop(at, op):
        if not stack:
            violation(at, op, 'stack underflow', 'one value on the stack')
        return stack.pop()

    try:
        for at, op, arg in stream:
            if op not in ALLOWED_OPS:
                reason = ('opcode is not allowed in module-level literal code (this '
                          'reader follows literal tables only; a module that computes '
                          'its tables at import time is reported here)')
                if op == NOP:
                    reason = ('NOP in module-level literal code (a real NOP or the '
                              'transpiler fallback for an unmapped Duoyi opcode)')
                violation(at, op, reason)
            elif op == LOAD_CONST:
                if arg is None or arg >= len(consts):
                    violation(at, op, f'LOAD_CONST index {arg} out of range '
                                      f'(co_consts has {len(consts)} entries)')
                stack.append(consts[arg])
            elif op == BUILD_MAP:
                if arg:
                    violation(at, op, f'BUILD_MAP with {arg} pre-built items is unsupported')
                value: dict = {}
                live.append(value)
                writes_of[id(value)] = []
                stack.append(value)
            elif op in (BUILD_LIST, BUILD_TUPLE):
                if arg is None or arg > len(stack):
                    violation(at, op, f'BUILD_* needs {arg} values, stack has {len(stack)}')
                items = stack[-arg:] if arg else []
                if arg:
                    del stack[-arg:]
                stack.append(list(items) if op == BUILD_LIST else tuple(items))
            elif op == DUP_TOP:
                if not stack:
                    violation(at, op, 'stack underflow', 'one value to duplicate')
                stack.append(stack[-1])
            elif op == ROT_TWO:
                if len(stack) < 2:
                    violation(at, op, 'stack underflow', 'two values to rotate')
                stack[-2], stack[-1] = stack[-1], stack[-2]
            elif op == ROT_THREE:
                if len(stack) < 3:
                    violation(at, op, 'stack underflow', 'three values to rotate')
                stack[-3], stack[-2], stack[-1] = stack[-1], stack[-3], stack[-2]
            elif op == STORE_SUBSCR:
                key = pop(at, op)
                target = pop(at, op)
                value = pop(at, op)
                if id(target) not in writes_of:
                    violation(at, op, 'STORE_SUBSCR target is not a literal dictionary '
                                      f'({type(target).__name__})')
                events = writes_of[id(target)]
                if key in target:
                    events.append(WriteEvent(len(events), at, 'overwrite',
                                             key, target[key], value))
                else:
                    events.append(WriteEvent(len(events), at, 'insert', key, None, value))
                target[key] = value
            elif op in STORE_OPS:
                if arg is None or arg >= len(names):
                    violation(at, op, f'name index {arg} out of range '
                                      f'(co_names has {len(names)} entries)')
                value = pop(at, op)
                if isinstance(value, _Opaque):
                    statements.append(Statement(at, op, arg, 'opaque_assignment'))
                else:
                    assignments.append(Assignment(names[arg], op, at, value,
                                                  tuple(writes_of.get(id(value), ()))))
            elif op == IMPORT_NAME:
                # `import a.b` at module scope: level/fromlist are opaque here.
                if len(stack) < 2:
                    violation(at, op, 'stack underflow', 'two import operands')
                del stack[-2:]
                stack.append(_Opaque('module'))
            elif op == IMPORT_FROM:
                stack.append(_Opaque('attribute'))
            elif op == IMPORT_STAR:
                pop(at, op)
            elif op == MAKE_FUNCTION:
                if arg:
                    violation(at, op, f'MAKE_FUNCTION with {arg} default values is unsupported')
                if stack:
                    stack.pop()
                stack.append(_Opaque('function'))
            elif op == POP_TOP:
                pop(at, op)
            elif op == RETURN_VALUE:
                pop(at, op)
                statements.append(Statement(at, op, arg, 'return'))
                break
            depth_max = max(depth_max, len(stack))
    except _MachineStop:
        pass

    if not violations and stack:
        violation(stream[-1][0] if stream else 0, None,
                  f'module ends with {len(stack)} value(s) left on the stack')
    if violations:
        # Every assignment here was published before the first violation, so it is
        # a partial read: keep the values, but say so on the value itself.
        assignments = [dataclasses.replace(a, verified=False,
                                           violations=tuple(violations))
                       for a in assignments]
    return ScanResult(assignments, statements, violations, depth_max)


def disallowed_opcode_histogram(co) -> dict:
    """Count opcodes outside the module-level literal allowlist, over the whole body.

    This is a structural density metric like the 'unmapped opcode' count, but
    with an allowlist that reflects what module-level literal code may contain.
    """
    try:
        stream = list(instructions(co))
    except LiteralSyntaxError as exc:
        return {f'reader error: {exc.reason}': 1}
    counts = collections.Counter(
        f'opcode {op} ({OPCODE_NAMES.get(op, "?")})'
        for _, op, _ in stream if op not in ALLOWED_OPS)
    return dict(counts)


def read_assignment(co, name: bytes, duplicate_policy: str = 'record',
                    allow_partial: bool = False) -> Assignment | None:
    """Return the module-level literal assignment `name`, or None when absent.

    Contract (same as `review_client_data_boundaries.extract_table_report`):

    * `allow_partial=False` (default) is strict: if the module body contains a
      shape this reader cannot accept, the call raises `ValueError` even when
      `name` was already published, because the value is then unverified.
    * `allow_partial=True` returns the (possibly partial) assignment; the returned
      object carries `verified=False` and the full `violations` tuple.
    * `None` is returned only when the body was read completely and `name` is
      genuinely absent.  A table that was never published while the body could not
      be read raises in both modes: there is no partial value to inspect.

    `duplicate_policy` is 'record' (keep every write, default) or 'error'
    (raise on the first repeated dictionary key, the historical behaviour).
    """
    if duplicate_policy not in ('record', 'error'):
        raise ValueError(f'unknown duplicate_policy {duplicate_policy!r}')
    scan = scan_module(co)
    assignment = scan.by_name(name)
    if assignment is None:
        if scan.violations:
            # Nothing was published for `name`, so `allow_partial` has nothing to
            # hand back; `None` stays reserved for "read completely, really absent".
            raise ValueError(f'module body could not be read completely, table '
                             f'{name!r} not found; first rejected shape: '
                             f'{scan.violations[0]}')
        return None
    if scan.violations and not allow_partial:
        raise ValueError(f'module body could not be read completely, table {name!r} '
                         f'is unverified; pass allow_partial=True to inspect the '
                         f'partial value. First rejected shape: {scan.violations[0]}')
    if duplicate_policy == 'error' and assignment.overwrites:
        first = assignment.overwrites[0]
        raise ValueError(f'duplicate dictionary key {first.key!r} at {first.at}')
    return assignment


def scan_index_bounds(co) -> list:
    """Report constant/name indices outside co_consts/co_names."""
    limit = {'consts': len(co['consts']), 'names': len(co['names'])}
    table_of = {LOAD_CONST: 'consts', 105: 'names', 106: 'names', 107: 'names',
                108: 'names', 116: 'names', STORE_NAME: 'names', STORE_GLOBAL: 'names'}
    try:
        stream = list(instructions(co))
    except LiteralSyntaxError as exc:
        return [exc.as_dict()]
    problems = []
    for at, op, arg in stream:
        table = table_of.get(op)
        if table and arg is not None and arg >= limit[table]:
            problems.append({'at': at, 'op': op, 'arg': arg,
                             'table': table, 'size': limit[table]})
    return problems


def dump(value) -> Any:
    """JSON-friendly rendering of decoded bytes/containers (no text guessing)."""
    if isinstance(value, _Opaque):
        return {'opaque': value.kind}
    if isinstance(value, bytes):
        try:
            return value.decode('cp950')
        except UnicodeDecodeError:
            return {'invalid_cp950_hex': value.hex()}
    if isinstance(value, (list, tuple)):
        return [dump(v) for v in value]
    if isinstance(value, dict):
        return {str(dump(k)): dump(v) for k, v in value.items()}
    return value
