"""Persistent fixed-11-bit LZW decoder (mxmain 0x4c5e40)."""

from __future__ import annotations

END = 0x7FF
LAST = END - 1
RESET_DELAY = 5000


class ProtocolError(ValueError):
    """Malformed or out-of-policy wire input; discard the connection state."""


def pack_codes(codes: list[int]) -> bytes:
    """MSB-first 11-bit words, zero padded to a byte boundary."""
    output = bytearray()
    bits = value = 0
    for code in codes:
        if not 0 <= code <= END:
            raise ValueError("invalid 11-bit code")
        value = (value << 11) | code
        bits += 11
        while bits >= 8:
            bits -= 8
            output.append((value >> bits) & 255)
        value &= (1 << bits) - 1
    if bits:
        output.append(value << (8 - bits))
    return bytes(output)


def encode_literals(data: bytes) -> bytes:
    """Valid but deliberately unoptimized sender; dictionary references omitted."""
    if not data:
        raise ValueError("native compressed body must contain a command")
    return pack_codes([*data, END])


class LZWDecoder:
    """Dictionary persists across frames; bit reservoir and previous code do not."""

    def __init__(self, max_output: int = 1 << 20):
        if max_output < 1:
            raise ValueError("max_output must be positive")
        self.max_output = max_output
        self.table: dict[int, bytes] = {}
        self.next_code = 256
        self.full_count = 0

    def decode(self, data: bytes) -> bytes:
        result = bytearray()
        previous = b""
        value = bits = 0
        for byte in data:
            value = (value << 8) | byte
            bits += 8
            while bits >= 11:
                bits -= 11
                code = (value >> bits) & END
                if code == END:
                    if not result:
                        raise ProtocolError("empty compressed body")
                    return bytes(result)
                if code < 256:
                    word = bytes([code])
                elif code in self.table:
                    word = self.table[code]
                elif code == self.next_code and previous:
                    word = previous + previous[:1]
                else:
                    raise ProtocolError("invalid LZW dictionary reference")
                if len(result) + len(word) > self.max_output:
                    raise ProtocolError("decompressed body exceeds limit")
                result.extend(word)
                if previous:
                    if self.next_code <= LAST:
                        self.table[self.next_code] = previous + word[:1]
                        self.next_code += 1
                    elif self.full_count > RESET_DELAY:
                        self.table.clear()
                        self.next_code = 256
                        self.full_count = 0
                    else:
                        self.full_count += 1
                previous = word
            value &= (1 << bits) - 1
        # Native treats exhaustion as END. Reject truncation deliberately here.
        raise ProtocolError("missing LZW terminator")
