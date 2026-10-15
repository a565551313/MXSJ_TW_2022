"""Independent inverse: both native jump coordinates must resolve identically."""

from __future__ import annotations

import struct

from ..tables import PY27_ABS_JUMPS, PY27_MAP, PY27_REL_JUMPS


def join(code: bytes, extra: int):
    if not 1 <= extra <= len(code) or code[extra - 1] != 23:
        raise ValueError("VM27 split-stream sentinel/extra invalid")
    opcodes, arguments = code[: extra - 1], code[extra:]
    offsets, arg_offsets = [0], [0]
    for op in opcodes:
        if op not in PY27_MAP or op in (66, 242):
            raise ValueError("unknown/ambiguous/EXTENDED_ARG native VM27 instruction")
        std = PY27_MAP[op]
        if (std >= 90) != (op >= 90):
            raise ValueError("native VM27 opcode width mismatch")
        offsets.append(offsets[-1] + (3 if op >= 90 else 1))
        arg_offsets.append(
            arg_offsets[-1]
            + ((4 if op in PY27_ABS_JUMPS | PY27_REL_JUMPS else 2) if op >= 90 else 0)
        )
    if arg_offsets[-1] != len(arguments):
        raise ValueError("native VM27 argument stream length mismatch")
    out = bytearray()
    for i, op in enumerate(opcodes):
        out.append(PY27_MAP[op])
        if op < 90:
            continue
        ap = arg_offsets[i]
        value = struct.unpack_from("<H", arguments, ap)[0]
        if op in PY27_ABS_JUMPS | PY27_REL_JUMPS:
            argument_coordinate = struct.unpack_from("<H", arguments, ap + 2)[0]
            target = value if op in PY27_ABS_JUMPS else i + 1 + value
            expected_arg = (
                argument_coordinate
                if op in PY27_ABS_JUMPS
                else ap + 4 + argument_coordinate
            )
            if not 0 <= target < len(offsets) or arg_offsets[target] != expected_arg:
                raise ValueError("VM27 jump instruction/argument coordinates disagree")
            value = (
                offsets[target]
                if op in PY27_ABS_JUMPS
                else offsets[target] - offsets[i + 1]
            )
        if not 0 <= value <= 65535:
            raise ValueError("standard VM27 jump exceeds uint16")
        out.extend(struct.pack("<H", value))
    return bytes(out), offsets


def lines(lnotab: bytes, offsets: list[int]) -> bytes:
    if len(lnotab) % 2:
        raise ValueError("odd native lnotab")
    result, index, previous_byte = bytearray(), 0, 0
    for i in range(0, len(lnotab), 2):
        index += lnotab[i]
        line = lnotab[i + 1]
        if index >= len(offsets):
            raise ValueError("native lnotab index out of range")
        if not line and lnotab[i] == 255 and i + 2 < len(lnotab):
            continue
        delta = offsets[index] - previous_byte
        while delta > 255:
            result.extend((255, 0))
            delta -= 255
        result.extend((delta, line))
        previous_byte = offsets[index]
    return bytes(result)
