from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mxsj_native_channel import (  # noqa: E402
    Channel,
    ClientHandshake,
    Packet,
    ProtocolError,
    StreamCipher,
    derive,
    hello,
    hello_reply,
)
from mxsj_native_channel.core.channel import encode_c2s, encode_s2c  # noqa: E402
from mxsj_native_channel.core.cipher import generate_block  # noqa: E402
from mxsj_native_channel.core.compression import (  # noqa: E402
    LZWDecoder,
    encode_literals,
    pack_codes,
)

VECTORS = json.loads(
    (Path(__file__).resolve().parents[1] / "evidence" / "vectors.json").read_text(
        encoding="utf-8"
    )
)


class NativeVectors(unittest.TestCase):
    def test_derive_and_cipher(self):
        for row in VECTORS["cipher"]:
            with self.subTest(seed=row["seed"]):
                k = derive(row["seed"])
                self.assertEqual(list(vars(k).values()), row["keys"])
                for (key, skip), vector in zip(
                    [(k.rx_key, k.rx_skip), (k.tx_key, k.tx_skip)],
                    row["directions"],
                    strict=True,
                ):
                    data = bytes(i % 251 for i in range(9000))
                    cipher = StreamCipher(key, skip)
                    out = cipher.crypt(data[:1]) + cipher.crypt(data[1:4095])
                    out += cipher.crypt(b"") + cipher.crypt(data[4095:])
                    self.assertEqual(out[:64].hex(), vector["prefix_hex"])
                    self.assertEqual(
                        hashlib.sha256(out).hexdigest(), vector["sha256_9000"]
                    )
                    self.assertEqual(StreamCipher(key, skip).crypt(out), data)

    def test_native_blocks(self):
        for vector in VECTORS["blocks"]:
            state, block = generate_block(vector["state"])
            self.assertEqual(state, vector["final"])
            self.assertEqual(hashlib.sha256(block).hexdigest(), vector["sha256"])

    def test_persistent_native_lzw(self):
        decoder = LZWDecoder()
        for row in VECTORS["lzw"]:
            wire = pack_codes(row["codes"])
            self.assertEqual(hashlib.sha256(wire).hexdigest(), row["wire_sha256"])
            self.assertEqual(decoder.decode(wire).hex(), row["output_hex"])
            self.assertEqual(decoder.next_code, row["next_code"])
            self.assertEqual(decoder.full_count, row["full_count"])

    def test_discard(self):
        a, b = StreamCipher(123, 0), StreamCipher(123, 0)
        a.discard(8193)
        self.assertEqual(a.crypt(bytes(41)), b.crypt(bytes(8234))[8193:])
        with self.assertRaises(ValueError):
            a.discard(-1)


class Framing(unittest.TestCase):
    def test_hello_bytes(self):
        self.assertEqual(hello(0x12345678, 0x4321, 5).hex(), "080178563412214305")
        # Arithmetic independently calculated from script constants.
        self.assertEqual(
            hello_reply(0x12345678).hex(),
            "16ed4b00000000000000000000000000000000000000000000",
        )
        self.assertEqual(len(hello_reply(0)), 25)

    def test_signed_seed_reply(self):
        self.assertEqual(hello_reply(0xFFFFFFFF)[:3].hex(), "e4d424")
        self.assertNotEqual(hello_reply(0), hello_reply(0x80000000))

    def test_two_byte_profile(self):
        a = Channel(1, "server", length_bytes=2)
        b = Channel(1, "client", length_bytes=2)
        self.assertEqual(b.feed(a.send(2, bytes(300))), [Packet(2, bytes(300))])

    def test_directional_layout(self):
        self.assertEqual(encode_c2s(7, b"ab"), b"\x07\x03ab\0")
        self.assertEqual(encode_s2c(b"ab"), b"\x02ab")
        self.assertEqual(encode_s2c(bytes(255))[:4], b"\xff\xff\0\0")
        with self.assertRaises(ValueError):
            encode_c2s(1, bytes(248))

    def test_all_handshake_splits(self):
        for split in range(10):
            server = Channel(1, "server")
            wire = hello(1) + server.send(42, b"fake")
            client = ClientHandshake()
            packets = client.feed(wire[:split]) + client.feed(wire[split:])
            self.assertEqual(packets, [Packet(42, b"fake")])
            self.assertEqual(client.take_reply(), hello_reply(1))
            self.assertEqual(client.take_reply(), b"")
            self.assertEqual(
                server.feed(client.channel.send(7, b"x")), [Packet(7, b"x")]
            )

    def test_extended_fragmentation_and_coalescing(self):
        server, client = Channel(1, "server"), Channel(1, "client")
        wire = server.send(2, bytes(range(256)) * 25) + server.send(3)
        packets = []
        for start in range(0, len(wire), 7):
            packets.extend(client.feed(wire[start : start + 7]))
        self.assertEqual(packets, [Packet(2, bytes(range(256)) * 25), Packet(3, b"")])
        client.finish()

    def test_c2s_fragments(self):
        server, client = Channel(1, "server"), Channel(1, "client")
        wire = client.send(2, bytes(247)) + client.send(3)
        packets = []
        for byte in wire:
            packets.extend(server.feed(bytes([byte])))
        self.assertEqual(packets, [Packet(2, bytes(247)), Packet(3, b"")])

    def test_reconnect(self):
        a, b = Channel(1, "client"), Channel(1, "client")
        self.assertEqual(a.send(1), b.send(1))
        a.send(2)
        self.assertNotEqual(a.send(1), Channel(1, "client").send(1))

    def test_limits_and_fail_closed(self):
        server = Channel(1, "server")
        client = Channel(1, "client", max_frame=10)
        with self.assertRaises(ProtocolError):
            client.feed(server.send(1, bytes(20)))
        with self.assertRaises(ProtocolError):
            client.feed(b"")
        with self.assertRaises(ProtocolError):
            client.send(1)

    def test_bad_c2s_terminator(self):
        client, server = Channel(1, "client"), Channel(1, "server")
        with self.assertRaises(ProtocolError):
            server.feed(client.tx.crypt(b"\x01\x01x"))

    def test_bad_c2s_length(self):
        client, server = Channel(1, "client"), Channel(1, "server")
        with self.assertRaises(ProtocolError):
            server.feed(client.tx.crypt(b"\x01\0"))

    def test_bad_hello_and_eof(self):
        for data in [b"\x09", b"\x08\x02"]:
            client = ClientHandshake()
            with self.assertRaises(ProtocolError):
                client.feed(data)
            with self.assertRaises(ProtocolError):
                client.feed(b"")
        with self.assertRaises(ProtocolError):
            ClientHandshake().finish()
        server, client = Channel(1, "server"), Channel(1, "client")
        client.feed(server.send(1)[:-1])
        with self.assertRaises(ProtocolError):
            client.finish()

    def test_invalid_config(self):
        for args in [(1, "other"), (-1, "client"), (1 << 32, "client")]:
            with self.assertRaises(ValueError):
                Channel(*args)

    def test_lzw_rejections(self):
        for codes in [[2047], [300, 2047], [1, 300, 2047], [1]]:
            with self.assertRaises(ProtocolError):
                LZWDecoder().decode(pack_codes(codes))
        with self.assertRaises(ProtocolError):
            LZWDecoder(2).decode(encode_literals(b"abc"))


if __name__ == "__main__":
    unittest.main()
