"""Native storage repair: static binding proof and synthetic packs."""

from __future__ import annotations

import hashlib
import importlib.util
import os
import random
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


repair = load("repair_native_layouts", HERE / "repair_interface_layouts.py")
hash_ref = load("old_hash_reference", ROOT / "tools/data-parser/mx_path_hash.py")


def synthetic_pack(stored, noise=b"unrelated opaque stored payload"):
    items = [(1, noise)] + [
        (repair.native_path_hash(path), blob) for path, blob in stored.items()
    ]
    items.sort()
    out = bytearray(b"0SLF" + struct.pack("<II", len(items), 0))
    directory = []
    for index, (entry_id, blob) in enumerate(items):
        r1 = 0xA1B2C3D4  # Arbitrary existing r1, deliberately not interpreted as a key.
        r2 = ((r1 * entry_id + 0x0DF25E) & repair.MASK) ^ len(blob)
        r3 = ((r2 * index * 0x00F718FE + 0x0D59D16C) & repair.MASK) ^ len(out)
        directory.append(struct.pack("<IIII", entry_id, r1, r2, r3))
        out.extend(blob)
    struct.pack_into("<I", out, 8, len(out))
    out.extend(b"".join(directory))
    return bytes(out)


class NativePathCipherTest(unittest.TestCase):
    def test_actual_loadfile_method_and_native_call_chain(self):
        dll = ROOT / "mxmain.dll"
        if not dll.is_file():
            self.skipTest("native read-only image not present")
        data = dll.read_bytes()
        self.assertEqual(
            hashlib.sha256(data).hexdigest(),
            "637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d",
        )
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
        count = struct.unpack_from("<H", data, pe + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        sections = []
        for i in range(count):
            at = pe + 24 + optional_size + i * 40
            _, rva, raw_size, offset = struct.unpack_from("<IIII", data, at + 8)
            sections.append((base + rva, raw_size, offset))

        def read(va, length):
            for start, size, offset in sections:
                if start <= va and va + length <= start + size:
                    return data[offset + va - start : offset + va - start + length]
            raise AssertionError("static address outside file-backed sections")

        self.assertEqual(read(0x6B4038, 9), b"LoadFile\0")
        self.assertEqual(
            struct.unpack("<III", read(0x7DB2F0, 12)),
            (0x6B4038, 0x45D580, 3),
        )
        for site, target in (
            (0x45D5EA, 0x609760),
            (0x609771, 0x6097F0),
            (0x609AA2, 0x60DD00),
            (0x60DD11, 0x60E080),
            (0x60E105, 0x454860),
            (0x6097B9, 0x609C80),
        ):
            instruction = read(site, 5)
            self.assertEqual(instruction[0], 0xE8)
            self.assertEqual(site + 5 + struct.unpack("<i", instruction[1:])[0], target)
        self.assertEqual(
            read(0x60E153, 13), bytes.fromhex("8d82ab3492003512497f938907")
        )
        # Read loop XORs with the nonzero key field; no header recovery.
        self.assertEqual(read(0x609CE0, 4), bytes.fromhex("8b013106"))

    def test_literal_arithmetic_matches_independent_existing_hash(self):
        vectors = {
            b"login/regterms.dlg": (0x25EDC010, "a9bd00b5"),
            b"login/regform.dlg": (0xF2AECE40, "f94b3e60"),
            b"login/service.dlg": (0x14595D67, "00db9487"),
            b"dialog/recommendfriend.dlg": (0x04964CA7, "40c85796"),
        }
        for path, (entry_id, key) in vectors.items():
            self.assertEqual(repair.native_path_hash(path), entry_id)
            self.assertEqual(repair.native_layout_key(path).hex(), key)
            self.assertEqual(repair.native_path_hash(path), hash_ref.mx_hash(path))
            self.assertEqual(
                repair.native_layout_key(path),
                repair.native_layout_key(path.upper().replace(b"/", b"\\")),
            )
        randomizer = random.Random(147)
        alphabet = b"0123456789abcdefghijklmnopqrstuvwxyz/\\._-"
        for length in range(1, 256):
            path = bytes(randomizer.choice(alphabet) for _ in range(length))
            self.assertEqual(repair.native_path_hash(path), hash_ref.mx_hash(path))

    def test_old_plaintext_write_fails_native_decrypt_but_ciphertext_recovers(self):
        for path in repair.TARGETS:
            plain = (HERE / path.decode("ascii").split("/")[-1]).read_bytes()
            decoded_old = repair.xor4(plain, repair.native_layout_key(path))
            self.assertFalse(decoded_old.startswith(repair.HEADER))
            with self.assertRaises((SyntaxError, ValueError)):
                repair.validate_layout(decoded_old)
            stored = repair.xor4(plain, repair.native_layout_key(path))
            self.assertEqual(repair.xor4(stored, repair.native_layout_key(path)), plain)
            repair.validate_layout(plain)


class InterfaceRepairTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.source = self.folder / "interface.fls"
        self.output = self.folder / "interface_native_fixed.fls"
        self.plain = {
            path: (HERE / path.decode("ascii").split("/")[-1]).read_bytes()
            for path in repair.TARGETS
        }

    def prepare(self, stored=None, noise=b"opaque unrelated payload"):
        raw = synthetic_pack(self.plain if stored is None else stored, noise)
        self.source.write_bytes(raw)
        return raw

    def test_preserve_user_edits_and_all_other_bytes_across_chunk_boundary(self):
        path = repair.TARGETS[0]
        # Different whitespace/MD5/comment bytes must remain exactly the USER'S bytes.
        self.plain[path] += b"\n# user layout revision, not repository default\n"
        original = self.prepare(noise=b"Z" * (repair.CHUNK - 24))
        result = repair.repair_pack(self.source, self.output)
        self.assertTrue(result["output_created"])
        self.assertEqual(result["changed_layout_count"], 2)
        self.assertEqual(self.source.read_bytes(), original)
        final = self.output.read_bytes()
        self.assertEqual(len(final), len(original))
        expected = bytearray(original)
        with self.source.open("rb") as fh:
            rows = {
                entry: (offset, length)
                for entry, offset, length in repair.read_index(fh, len(original))
            }
        for path, plain in self.plain.items():
            offset, length = rows[repair.native_path_hash(path)]
            stored = repair.xor4(plain, repair.native_layout_key(path))
            expected[offset : offset + length] = stored
            self.assertEqual(
                repair.xor4(
                    final[offset : offset + length], repair.native_layout_key(path)
                ),
                plain,
            )
        self.assertEqual(
            final, expected
        )  # Header/directory and all unrelated bytes equal.
        self.assertEqual(result["output_sha256"], hashlib.sha256(final).hexdigest())
        self.assertFalse(list(self.folder.glob(".reg-native-*")))

    def test_already_native_no_output_and_mixed_storage(self):
        stored = {
            path: repair.xor4(plain, repair.native_layout_key(path))
            for path, plain in self.plain.items()
        }
        original = self.prepare(stored)
        result = repair.repair_pack(self.source, self.output)
        self.assertFalse(result["output_created"])
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), original)
        stored[repair.TARGETS[1]] = self.plain[repair.TARGETS[1]]
        original = self.prepare(stored)
        result = repair.repair_pack(self.source, self.output)
        self.assertEqual(result["changed_layout_count"], 1)
        self.assertEqual(self.source.read_bytes(), original)

    def test_arbitrary_old_key_can_be_corrected_without_changing_plaintext(self):
        stored = {
            path: repair.xor4(plain, b"\x12\x34\x56\x78")
            for path, plain in self.plain.items()
        }
        self.prepare(stored)
        result = repair.repair_pack(self.source, self.output)
        self.assertTrue(
            all(
                item["storage_before"] == "different_key_needs_native_xor"
                for item in result["layouts"]
            )
        )

    def test_refuse_inputs_existing_outputs_and_link_aliases(self):
        original = self.prepare()
        hardlink, symlink = self.folder / "hard.fls", self.folder / "sym.fls"
        os.link(self.source, hardlink)
        symlink.symlink_to(self.source)
        self.output.write_bytes(b"existing output must remain")
        for output in (self.source, hardlink, symlink, self.output):
            with self.assertRaisesRegex(ValueError, "NEW path"):
                repair.repair_pack(self.source, output)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(self.output.read_bytes(), b"existing output must remain")

    def test_missing_bad_or_executable_layout_fails_without_output(self):
        for stored in (
            {repair.TARGETS[0]: self.plain[repair.TARGETS[0]]},
            dict.fromkeys(repair.TARGETS, b"not a layout"),
            dict.fromkeys(repair.TARGETS, repair.HEADER + b"\nUI_INFO = dangerous()\n"),
        ):
            original = self.prepare(stored)
            with self.assertRaises((ValueError, SyntaxError)):
                repair.repair_pack(self.source, self.output)
            self.assertEqual(self.source.read_bytes(), original)
            self.assertFalse(self.output.exists())
            self.assertFalse(list(self.folder.glob(".reg-native-*")))

    def test_verification_and_racing_publication_fail_closed(self):
        original = self.prepare()
        with patch.object(
            repair, "verify_copy", side_effect=ValueError("test failure")
        ):
            with self.assertRaisesRegex(ValueError, "test failure"):
                repair.repair_pack(self.source, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(self.source.read_bytes(), original)
        verify = repair.verify_copy

        def racing_output(*args):
            digest = verify(*args)
            self.output.write_bytes(b"another writer's file")
            return digest

        with patch.object(repair, "verify_copy", side_effect=racing_output):
            with self.assertRaises(FileExistsError):
                repair.repair_pack(self.source, self.output)
        self.assertEqual(self.output.read_bytes(), b"another writer's file")
        self.assertEqual(self.source.read_bytes(), original)
        self.assertFalse(list(self.folder.glob(".reg-native-*")))


if __name__ == "__main__":
    unittest.main()
