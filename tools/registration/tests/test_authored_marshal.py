"""The new-source verifier must reject corruption, never guess a replacement."""

import importlib.util
import struct
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "registration_authored_marshal", HERE / "authored_marshal.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def string(value):
    return b"s" + struct.pack("<I", len(value)) + value


def code_object(code):
    empty = b"(" + struct.pack("<I", 0)
    return (b"c" + struct.pack("<IIII", 0, 0, 1, 0) + string(code)
            + empty * 5 + string(b"script\\login\\register.py")
            + string(b"<module>") + struct.pack("<I", 1) + string(b""))


class AuthoredMarshalTest(unittest.TestCase):
    def test_only_code_bytes_translate_all_other_bytes_preserved(self):
        source = code_object(b"\x01\x02")
        actual = module.restore_authored_pyc(
            source + b"\0" * 50, source, lambda code: bytes(x + 1 for x in code)
        )
        self.assertEqual(actual, module.MAGIC + code_object(b"\x02\x03"))

    def test_nonzero_padding_or_payload_difference_is_rejected(self):
        source = code_object(b"\x01\x02")
        for bad in (source + b"\x01", source[:-1], b"x" + source[1:]):
            with self.subTest(bad_length=len(bad)), self.assertRaises(ValueError):
                module.restore_authored_pyc(bad, source, lambda code: code)

    def test_unknown_tag_or_truncated_marshal_is_not_repaired(self):
        for data in (b"z", b"c", b"s\xff\xff\xff\xff", b"NN"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                module.restore_authored_pyc(data, data, lambda code: code)

    def test_translator_cannot_change_code_width(self):
        source = code_object(b"\x01\x02")
        with self.assertRaises(ValueError):
            module.restore_authored_pyc(source, source, lambda code: code[:-1])


if __name__ == "__main__":
    unittest.main()
