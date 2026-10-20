"""Socket-independent candidate TCP codec. No listeners or account logic."""

from __future__ import annotations

import struct
from dataclasses import dataclass

from .cipher import StreamCipher, derive, uint32
from .compression import LZWDecoder, ProtocolError, encode_literals


@dataclass(frozen=True)
class Packet:
    command: int
    payload: bytes


def hello(seed: int, server_number: int = 1, certificate: int = 0) -> bytes:
    """Plain S2C HELLO: length=8, command=1, seed:u32, server:u16, cert:u8."""
    return b"\x08\x01" + struct.pack("<IHB", uint32(seed), server_number, certificate)


def hello_reply(seed: int) -> bytes:
    """script.fls entry 4082 S2CHello; raw bytes, never ciphered."""
    seed = uint32(seed)
    # UnpackInt uses Py_BuildValue("i"), so high-bit seeds arrive signed.
    signed_seed = seed if seed < 0x80000000 else seed - (1 << 32)
    value = (((1 << 32) + signed_seed) % 3227993 + 2562088) ^ 6636321
    return value.to_bytes(4, "little")[:3] + bytes(22)


def encode_c2s(command: int, payload: bytes) -> bytes:
    """Command, payload length + trailing zero, payload, zero; max total 250."""
    if len(payload) > 247:
        raise ValueError("C2S payload exceeds conservative native 250-byte limit")
    return bytes([command, len(payload) + 1]) + payload + b"\0"


def encode_s2c(body: bytes, length_bytes: int = 3) -> bytes:
    if length_bytes not in (2, 3):
        raise ValueError("length_bytes must be 2 or 3")
    size = len(body)
    if not 0 < size < (1 << (8 * length_bytes)):
        raise ValueError("invalid S2C body size")
    prefix = (
        bytes([size]) if size < 255 else b"\xff" + size.to_bytes(length_bytes, "little")
    )
    return prefix + body


class Channel:
    """Established stream. Construct a fresh instance on every connection.

    role='client': send C2S, receive S2C. role='server': the inverse.
    Use only after the raw HELLO/reply exchange. After any receive error this
    object is permanently failed; reconnect with a new one. Not thread safe.
    """

    def __init__(
        self,
        seed: int,
        role: str,
        *,
        length_bytes: int = 3,
        max_frame: int | None = None,
        max_output: int = 1 << 20,
    ):
        if role not in ("client", "server") or length_bytes not in (2, 3):
            raise ValueError("invalid role or extended length width")
        if max_frame is None:
            max_frame = min(1 << 20, (1 << (8 * length_bytes)) - 1)
        if not 1 <= max_frame < (1 << (8 * length_bytes)):
            raise ValueError("invalid frame limit")
        keys = derive(seed)
        rx = StreamCipher(keys.rx_key, keys.rx_skip)
        tx = StreamCipher(keys.tx_key, keys.tx_skip)
        self.rx, self.tx = (rx, tx) if role == "client" else (tx, rx)
        self.role = role
        self.length_bytes = length_bytes
        self.max_frame = max_frame
        self.decoder = LZWDecoder(max_output)
        self.buffer = bytearray()
        self.failed = False

    def send(self, command: int, payload: bytes = b"") -> bytes:
        if self.failed:
            raise ProtocolError("channel failed; reconnect")
        if self.role == "client":
            frame = encode_c2s(command, payload)
        else:
            if len(payload) + 1 > self.decoder.max_output:
                raise ValueError("body exceeds output limit")
            body = encode_literals(bytes([command]) + payload)
            if len(body) > self.max_frame:
                raise ValueError("compressed body exceeds frame limit")
            frame = encode_s2c(body, self.length_bytes)
        return self.tx.crypt(frame)

    def _pop(self) -> Packet | None:
        data = self.buffer
        if self.role == "server":
            if len(data) < 2:
                return None
            size, offset = data[1], 2
            if not 1 <= size <= 248:
                raise ProtocolError("invalid C2S length")
        else:
            if not data:
                return None
            size, offset = data[0], 1
            if size == 255:
                offset += self.length_bytes
                if len(data) < offset:
                    return None
                size = int.from_bytes(data[1:offset], "little")
            if not 1 <= size <= self.max_frame:
                raise ProtocolError("invalid S2C length")
        if len(data) < offset + size:
            return None
        body = bytes(data[offset : offset + size])
        if self.role == "server":
            if body[-1] != 0:
                raise ProtocolError("missing C2S trailing zero")
            packet = Packet(data[0], body[:-1])
        else:
            decoded = self.decoder.decode(body)
            packet = Packet(decoded[0], decoded[1:])
        del data[: offset + size]
        return packet

    def feed(self, data: bytes) -> list[Packet]:
        """Accept arbitrary TCP chunks; decrypt headers too, exactly once."""
        if self.failed:
            raise ProtocolError("channel failed; reconnect")
        packets = []
        try:
            # Bound internal buffering even if a caller passes a huge recv chunk.
            for start in range(0, len(data), 4096):
                self.buffer.extend(self.rx.crypt(data[start : start + 4096]))
                while (packet := self._pop()) is not None:
                    packets.append(packet)
        except ProtocolError:
            self.failed = True
            self.buffer.clear()
            raise
        return packets

    def finish(self) -> None:
        """Signal EOF; partial frames are errors."""
        if self.failed or self.buffer:
            self.failed = True
            raise ProtocolError("failed channel or truncated frame at EOF")


class ClientHandshake:
    """Incremental HELLO receiver; feed returns packets following HELLO.

    take_reply() returns the raw reply once. Queue it before any Channel.send()
    output. Incoming bytes coalesced with HELLO use the newly initialized cipher.
    """

    def __init__(self):
        self.buffer = bytearray()
        self.channel: Channel | None = None
        self.reply = b""
        self.server_number: int | None = None
        self.certificate: int | None = None
        self.failed = False

    def feed(self, data: bytes) -> list[Packet]:
        if self.failed:
            raise ProtocolError("handshake failed; reconnect")
        if self.channel is not None:
            return self.channel.feed(data)
        needed = 9 - len(self.buffer)
        self.buffer.extend(data[:needed])
        if self.buffer and self.buffer[0] != 8:
            self.failed = True
            raise ProtocolError("unexpected HELLO length")
        if len(self.buffer) >= 2 and self.buffer[1] != 1:
            self.failed = True
            raise ProtocolError("unexpected HELLO command")
        if len(self.buffer) < 9:
            return []
        seed, self.server_number, self.certificate = struct.unpack(
            "<IHB", self.buffer[2:]
        )
        self.reply = hello_reply(seed)
        self.channel = Channel(seed, "client")
        self.buffer.clear()
        return self.channel.feed(data[needed:])

    def take_reply(self) -> bytes:
        result, self.reply = self.reply, b""
        return result

    def finish(self) -> None:
        if self.channel is None:
            self.failed = True
            raise ProtocolError("EOF before HELLO")
        self.channel.finish()
