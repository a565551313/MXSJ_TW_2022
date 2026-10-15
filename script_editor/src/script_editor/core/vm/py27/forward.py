"""Checked standard-bytecode -> native instruction/argument split streams."""

from __future__ import annotations

import struct

from ..tables import PY27_ABS_JUMPS, PY27_MAP, PY27_REL_JUMPS

FORWARD = {s: n for n, s in PY27_MAP.items() if n != 66}
FORWARD.update({106: 230, 107: 124, 108: 135, 133: 93, 134: 121})


def split(code: bytes):
    rows, byte_to_op, byte_to_arg = [], {}, {}
    pos, arg_offset = 0, 0
    while pos < len(code):
        op = code[pos]
        if op == 145:
            raise ValueError("VM27 EXTENDED_ARG not supported; no truncation")
        if op not in FORWARD:
            raise ValueError(f"unmapped standard VM27 opcode {op}")
        width = 3 if op >= 90 else 1
        if pos + width > len(code):
            raise ValueError("truncated standard VM27 instruction")
        native = FORWARD[op]
        if (native >= 90) != (width == 3):
            raise ValueError("VM27 opcode width mismatch")
        byte_to_op[pos], byte_to_arg[pos] = len(rows), arg_offset
        argument = (
            int.from_bytes(code[pos + 1 : pos + 3], "little") if width == 3 else 0
        )
        rows.append((pos, native, argument, arg_offset))
        arg_offset += (
            (4 if native in PY27_ABS_JUMPS | PY27_REL_JUMPS else 2) if width == 3 else 0
        )
        pos += width
    byte_to_op[pos], byte_to_arg[pos] = len(rows), arg_offset
    if len(rows) > 65535 or arg_offset > 65535:
        raise ValueError("VM27 instruction/argument addressing exceeds uint16")
    ops, args = bytearray(), bytearray()
    for index, (offset, native, argument, ap) in enumerate(rows):
        ops.append(native)
        if native in PY27_ABS_JUMPS | PY27_REL_JUMPS:
            target = argument if native in PY27_ABS_JUMPS else offset + 3 + argument
            if target not in byte_to_op:
                raise ValueError("VM27 jump does not target an instruction boundary")
            oi, ai = byte_to_op[target], byte_to_arg[target]
            if native in PY27_REL_JUMPS:
                oi, ai = oi - index - 1, ai - ap - 4
            if not (0 <= oi <= 65535 and 0 <= ai <= 65535):
                raise ValueError("VM27 jump overflow")
            args.extend(struct.pack("<HH", oi, ai))
        elif native >= 90:
            args.extend(struct.pack("<H", argument))
    ops.append(23)  # Exactly ONE terminal sentinel, not arbitrary NOP stripping.
    return bytes(ops + args), len(ops), byte_to_op


def lines(lnotab: bytes, boundaries: dict[int, int]) -> bytes:
    if len(lnotab) % 2:
        raise ValueError("odd standard lnotab")
    out, address, prior = bytearray(), 0, 0
    for i in range(0, len(lnotab), 2):
        address += lnotab[i]
        line = lnotab[i + 1]
        # Zero-line overflow chunks may temporarily point inside instructions.
        if not line and lnotab[i] == 255 and i + 2 < len(lnotab):
            continue
        if address not in boundaries:
            raise ValueError("lnotab does not resolve to an instruction boundary")
        target = boundaries[address]
        delta = target - prior
        while delta > 255:
            out.extend((255, 0))
            delta -= 255
        out.extend((delta, line))
        prior = target
    return bytes(out)
