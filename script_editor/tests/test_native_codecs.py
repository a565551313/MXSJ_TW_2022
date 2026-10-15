from __future__ import annotations

import struct
import unittest
from unittest.mock import patch

from native_fixtures import minimal_pyc, raw_string

from script_editor.core.vm import compression
from script_editor.core.vm.marshal_tree import Reader, parse
from script_editor.core.vm.py25 import codec as py25
from script_editor.core.vm.py27 import codec as py27
from script_editor.core.vm.py27 import forward, inverse


class CodecTests(unittest.TestCase):
    def test_minimal_both_vms_exact_marshal(self):
        for vm, codec in [("py25", py25), ("py27", py27)]:
            std = minimal_pyc(vm)
            self.assertEqual(codec.decode(codec.encode(std)), std)

    def test_py25_dispatch_golden_bytes(self):
        self.assertEqual(
            py25.map_code(bytes.fromhex("6400005309")), bytes.fromhex("8f00005500")
        )
        self.assertEqual(
            py25.map_code(bytes.fromhex("c10000980000"), inverse=True),
            bytes.fromhex("7c00005a0000"),
        )

    def test_py27_relative_jump_has_two_golden_coordinates(self):
        std = bytes.fromhex("6e030064000053")
        native, extra, _ = forward.split(std)
        self.assertEqual(native, bytes.fromhex("935b5417010002000000"))
        self.assertEqual(extra, 4)
        self.assertEqual(inverse.join(native, extra)[0], std)
        broken = bytearray(native)
        broken[6] = 1
        with self.assertRaisesRegex(ValueError, "coordinates"):
            inverse.join(bytes(broken), extra)

    def test_py27_absolute_jump_coordinates(self):
        native, extra, _ = forward.split(bytes.fromhex("71060064000053"))
        self.assertEqual(native, bytes.fromhex("e25b5417020006000000"))
        self.assertEqual(
            inverse.join(native, extra)[0], bytes.fromhex("71060064000053")
        )

    def test_real_nops_are_not_stripped_as_sentinels(self):
        native, extra, _ = forward.split(b"\x09\x09")
        self.assertEqual(native, b"\x17\x17\x17")
        self.assertEqual(inverse.join(native, extra)[0], b"\x09\x09")

    def test_line_overflow_inside_instruction_is_aggregated(self):
        code = b"d\0\0" * 86 + b"S"
        native, extra, mapping = forward.split(code)
        original = b"\xff\x00\x03\x01"
        lines = forward.lines(original, mapping)
        self.assertEqual(lines, b"\x56\x01")
        _, offsets = inverse.join(native, extra)
        self.assertEqual(inverse.lines(lines, offsets), original)
        std = minimal_pyc("py27", code=code, lnotab=original)
        self.assertEqual(py27.decode(py27.encode(std)), std)

    def test_semicolon_zero_line_events_are_not_overflow_padding(self):
        code = bytes.fromhex("6400005a0000") * 201 + b"S"
        original = b"\x06\x00" * 200 + b"\x06\x01"
        native, extra, mapping = forward.split(code)
        converted = forward.lines(original, mapping)
        self.assertEqual(converted, b"\x02\x00" * 200 + b"\x02\x01")
        self.assertEqual(
            inverse.lines(converted, inverse.join(native, extra)[1]), original
        )

    def test_invalid_line_tables_not_clamped(self):
        _, _, mapping = forward.split(b"d\0\0S")
        for lines in (b"\x01", b"\x01\x01", b"\xff\x01"):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                forward.lines(lines, mapping)
        with self.assertRaises(ValueError):
            inverse.lines(b"\xff\x01", [0, 3, 4])

    def test_ext_arg_and_address_overflow_explicitly_rejected(self):
        for code in (b"\x91\0\0", b"d\0\0" * 33000, b"\x09" * 66000):
            with self.assertRaises(ValueError):
                forward.split(code)

    def test_invalid_opcode_or_truncated_instruction(self):
        for codec in (py25, py27):
            vm = "py25" if codec is py25 else "py27"
            for code in (b"\xff", b"d\0"):
                with self.assertRaises(ValueError):
                    codec.encode(minimal_pyc(vm, code=code))
        with self.assertRaises(ValueError):
            forward.split(bytes.fromhex("6e010064000053"))

    def test_py27_semantic_opcode_golden_not_py25_numbering(self):
        # CPython2.7 opcode.py + actual DLL dispatch, NOT old research comments:
        # BUILD_SET / BUILD_MAP / LOAD_ATTR / COMPARE_OP / IMPORT_NAME / IMPORT_FROM.
        source = b"".join(bytes((op, 0, 0)) for op in (104, 105, 106, 107, 108, 109))
        native, extra, _ = forward.split(source)
        self.assertEqual(native[:extra], bytes((183, 137, 230, 124, 135, 155, 23)))
        self.assertEqual(inverse.join(native, extra)[0], source)
        # Old numeric alias 66 actually lands on the unknown-opcode handler.
        with self.assertRaises(ValueError):
            inverse.join(b"\x42\x17", 2)

    def test_bad_sentinel_extra_args(self):
        for code, extra in [(b"S", 1), (b"\x17", 0), (b"\x17", 2), (b"\x17\0", 1)]:
            with self.assertRaises(ValueError):
                inverse.join(code, extra)

    def test_marshal_requires_code_root_and_eof(self):
        for data in (b"N", b"?", b"", minimal_pyc("py25")[8:] + b"X"):
            with self.assertRaises(ValueError):
                parse(data)
        native = py25.encode(minimal_pyc("py25"))
        self.assertEqual(
            py25.decode(native + bytes(10), padding=True), minimal_pyc("py25")
        )
        with self.assertRaises(ValueError):
            py25.decode(native + b"\0X", padding=True)

    def test_marshal_all_scalar_shapes_intern_references(self):
        # Exercise both components of textual complex (legacy writer missed one).
        scalars = [
            b"N",
            b"F",
            b"T",
            b"S",
            b".",
            b"i" + bytes(4),
            b"I" + bytes(8),
            b"g" + bytes(8),
            b"y" + bytes(16),
            b"l" + struct.pack("<iH", -1, 7),
            raw_string(b"x"),
            b"t\1\0\0\0a",
            b"R" + bytes(4),
            b"u\3\0\0\0" + "測".encode(),
            b"f\3" + b"1.0",
            b"x\3" + b"1.0\3" + b"2.0",
            b"(\0\0\0\0",
            b"[\0\0\0\0",
            b"<\0\0\0\0",
            b">\0\0\0\0",
            b"{0",
        ]
        reader = Reader(b"".join(scalars))
        for _ in scalars:
            reader.walk()
        self.assertEqual(reader.pos, len(reader.data))
        with self.assertRaises(ValueError):
            Reader(b"R" + bytes(4)).walk()
        for raw in (b"s\xff\xff\xff\x7f", b"(\xff\xff\xff\x7f", b"l\1\0\0\0\xff\xff"):
            with self.assertRaises(ValueError):
                Reader(raw).walk()

    def test_depth_limit(self):
        with self.assertRaises(ValueError):
            Reader((b"(\1\0\0\0" * 102) + b"N").walk()

    def test_zlib_limits_trailing_truncation(self):
        import zlib

        stored = zlib.compress(b"A" * 1000)
        with patch.object(compression, "MAX_MARSHAL", 100):
            with self.assertRaises(ValueError):
                compression.inflate(stored)
        for raw in (stored[:-1], stored + b"x", stored + stored):
            with self.assertRaises(ValueError):
                compression.inflate(raw)
