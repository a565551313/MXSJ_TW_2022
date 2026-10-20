"""Candidate game stream cipher; evidence and scope in README.md."""

from __future__ import annotations

from dataclasses import dataclass

MASK = 0xFFFFFFFF
INITIAL_XOR = 0x05027919
POLYNOMIAL = 0xDA3A2A9C
BLOCK_SIZE = 4096


def uint32(value: int) -> int:
    if not isinstance(value, int) or not 0 <= value <= MASK:
        raise ValueError("expected uint32")
    return value


def mix(value: int, high: int, low: int) -> int:
    value |= 0x80000000
    return ((value % high) << 16) | (value % low)


@dataclass(frozen=True)
class Keys:
    rx_key: int
    tx_key: int
    rx_skip: int
    tx_skip: int


def derive(seed: int) -> Keys:
    """Client RX/TX ordering: mxmain 0x4abb20, render 0x817360."""
    a = b = uint32(seed)
    for _ in range(5):
        a = mix(a, 0x6FFD, 0x53EF)
        b = mix(b, 0x7159, 0x6FFD)
        a = mix(a, 0x758B, 0x7159)
        b = mix(b, 0x53EF, 0x758B)
    total = (a >> 1) + (b >> 1)
    return Keys(a, b, total % 0xFFD, total % 0xFFB)


def generate_block(state: int) -> tuple[int, bytes]:
    """Target plaintext generator 0x4c5d00; 1024 little endian words."""
    output = bytearray()
    for _ in range(BLOCK_SIZE // 4):
        for _ in range(32):
            state = ((state << 1) & MASK) | ((state & POLYNOMIAL).bit_count() & 1)
        output.extend(state.to_bytes(4, "little"))
    return state, bytes(output)


class StreamCipher:
    """Mutable one-direction stream. Never reuse across connections or directions.

    Refill/init/process reconstructed from render.dll; protected mxmain wrappers
    remain unvalidated. No integrity protection is provided by this legacy cipher.
    """

    def __init__(self, key: int, skip: int):
        self.key = uint32(key)
        self.skip = uint32(skip)
        self.state = key ^ INITIAL_XOR
        self.cursor = BLOCK_SIZE
        self.block = b""
        self.discard(skip)

    def _refill(self) -> None:
        state = self.state
        if self.key and self.skip:
            state = (mix(state, 0x758B, 0x7159) + self.key) & MASK
            state = (mix(state, 0x6FFD, 0x53EF) + self.skip) & MASK
        self.state, self.block = generate_block(state)
        self.state = self.state or INITIAL_XOR
        self.cursor = 0

    def discard(self, count: int) -> None:
        if count < 0:
            raise ValueError("negative discard")
        while count:
            if self.cursor == BLOCK_SIZE:
                self._refill()
            size = min(count, BLOCK_SIZE - self.cursor)
            self.cursor += size
            count -= size

    def crypt(self, data: bytes) -> bytes:
        """Encrypt/decrypt once, preserving cursor over arbitrary TCP chunks."""
        output = bytearray()
        offset = 0
        while offset < len(data):
            if self.cursor == BLOCK_SIZE:
                self._refill()
            size = min(len(data) - offset, BLOCK_SIZE - self.cursor)
            output.extend(
                a ^ b
                for a, b in zip(
                    data[offset : offset + size],
                    self.block[self.cursor : self.cursor + size],
                    strict=True,
                )
            )
            self.cursor += size
            offset += size
        return bytes(output)
