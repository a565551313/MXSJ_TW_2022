"""Native VM25 XOR arithmetic, from mxmain.dll C_sys.PkgImport.

0x45D403..0x45D485: module-name seed (back edge 0x45D415, NOT
0x45D413: EBX is cleared once, then accumulates every character).
0x45D48B..0x45D529: floor(size/5), seed/256, XOR, seed recurrence.
Research catalog boundaries can be wrong while marshal still parses. Small
modules may also have repeated/missing research keys. Never treat parse success
alone as evidence: name-side recovery must match both seed and directory hash.
"""

from __future__ import annotations

from functools import lru_cache

from ...mxhash import mx_hash
from ..marshal_tree import parse


def module_seed(name: bytes) -> int:
    if not isinstance(name, bytes) or not 1 <= len(name) <= 128 or b"\0" in name:
        raise ValueError("invalid native import name")
    result = 0
    for position, byte in enumerate(name):
        result ^= character_seed(position, byte)
    return result


@lru_cache(maxsize=4096)
def character_seed(position: int, value: int) -> int:
    n = position + 2
    count = (n + 5) * (n - 1) * n if position < 5 else (n + 5) * (n + 1)
    for _ in range(count):
        # Values stay below 32768; these products cannot overflow signed int32.
        value ^= (value * 0x7E79 + 0x029A139F) % 0x7879
    return value


def next_seed(seed: int) -> int:
    return seed ^ ((seed * 0x788B + 0x024543DF) % 0x7F63)


def sequence(seed: int) -> tuple[int, ...]:
    keys = []
    for _ in range(5):
        keys.append(seed & 255)
        seed = next_seed(seed)
    return tuple(keys)


@lru_cache(maxsize=1)
def _seed_by_sequence() -> dict[tuple[int, ...], int | None]:
    """Precompute every seed's key sequence once (32768 x 5 steps).

    The per-entry search used to retry the whole recurrence for each catalog
    row (about 640 arithmetic steps per module, ~2 s of a whole-package scan).
    The mapping is the same function of the same seeds; entries that collide
    are stored as None so an ambiguous sequence is still refused instead of
    silently resolved to the first candidate.
    """
    table: dict[tuple[int, ...], int | None] = {}
    for seed in range(32768):
        keys = sequence(seed)
        table[keys] = None if keys in table else seed
    return table


def seed_from_keys(keys: tuple[int, ...]) -> int:
    if len(keys) != 5 or any(type(k) is not int or not 0 <= k <= 255 for k in keys):
        raise ValueError("invalid five-segment XOR keys")
    seed = _seed_by_sequence().get(tuple(keys))
    if seed is None:
        raise ValueError("XOR keys do not identify a unique native cipher seed")
    return seed


def bounds_from_seed(seed: int, size: int) -> tuple[int, ...]:
    if type(seed) is not int or not 0 <= seed < 32768:
        raise ValueError("invalid native XOR seed")
    if type(size) is not int or not 0 < size <= 64 * 1024 * 1024:
        raise ValueError("invalid native XOR payload size")
    cursor, bounds = 0, []
    for _ in range(5):
        cursor += size // 5 + seed // 256
        bounds.append(min(cursor, size))
        seed = next_seed(seed)
    if cursor < size:
        raise ValueError("native cipher needs more than five segments")
    return tuple(bounds[:4])


def bounds_from_keys(keys: tuple[int, ...], size: int) -> tuple[int, ...]:
    return bounds_from_seed(seed_from_keys(keys), size)


def parameters_for_name(name: bytes, size: int):
    seed = module_seed(name)
    return sequence(seed), bounds_from_seed(seed, size)


@lru_cache(maxsize=256)
def _xor_table(key):
    return bytes(n ^ key for n in range(256))


def xor_segments(data: bytes, keys: tuple[int, ...], bounds: tuple[int, ...]):
    points = (0, *bounds, len(data))
    return b"".join(
        data[points[i] : points[i + 1]].translate(_xor_table(keys[i])) for i in range(5)
    )


def _import_name(native):
    filename = parse(native, zero_padding=True).fields[5].value
    if (
        not isinstance(filename, bytes)
        or not 1 <= len(filename) <= 8192
        or any(c < 32 or c == 127 for c in filename)
        or not filename.endswith((b".py", b".pyo"))
    ):
        raise ValueError("native module filename unavailable")
    return filename.replace(b"\\", b"/").rsplit(b"/", 1)[-1].rsplit(b".", 1)[0]


def resolve_parameters(data, keys, bounds, entry_id):
    """Resolve incomplete research rows, never fall back to their old cipher.

    A filename is only a candidate. Accept it only if the independent native
    name seed AND hash(name + '.s') bind it to this exact directory entry, then
    decrypt afresh using native parameters and check that same name again.
    Search is bounded to 128 seeds; large entries require a valid metadata hint.
    """

    def verified(seed, name):
        return (
            seed & 255 == keys[0]
            and module_seed(name) == seed
            and mx_hash(name + b".s") == entry_id
        )

    try:
        name = _import_name(xor_segments(data, keys, bounds))
        seed = module_seed(name)
        canonical = sequence(seed), bounds_from_seed(seed, len(data))
        if (
            verified(seed, name)
            and _import_name(xor_segments(data, *canonical)) == name
        ):
            return canonical
    except (ValueError, TypeError, AttributeError):
        pass
    if len(data) > 1024 * 1024:
        raise ValueError("native cipher identity unresolved; bounded search refused")
    matches = []
    for seed in range(keys[0], 32768, 256):
        canonical = sequence(seed), bounds_from_seed(seed, len(data))
        try:
            name = _import_name(xor_segments(data, *canonical))
            if verified(seed, name):
                matches.append(canonical)
        except (ValueError, TypeError, AttributeError):
            pass
    if len(matches) != 1:
        raise ValueError("native cipher identity is missing or ambiguous")
    return matches[0]
