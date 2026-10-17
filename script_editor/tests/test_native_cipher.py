"""Native XOR regressions: never load/execute a game DLL or recovered module."""

from __future__ import annotations

import json
import os
import struct
import tempfile
import unittest
import zlib
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from native_fixtures import minimal_pyc, script_fixture

from script_editor.core.archives.document import ArchiveDocument
from script_editor.core.compiler.runner import compile_standard, inspect_compiler
from script_editor.core.vm.marshal_tree import Atom, Code, Group, parse
from script_editor.core.vm.py25 import codec
from script_editor.core.vm.py25.cipher import (
    bounds_from_keys,
    bounds_from_seed,
    module_seed,
    parameters_for_name,
    resolve_parameters,
    seed_from_keys,
    sequence,
)
from script_editor.core.vm.py25.keys import inflate_script, load_profile, sha

CATALOG_SHA = "43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb"


def engine_decrypt(name, payload):
    """Separate name-side translation of the pinned x86 loop, no product helpers.

    Do not use a research catalog or seed_from_keys to check a produced package.
    The real binary evidence test pins the constants and loop back-edge below.
    """
    state = 0
    for index, char in enumerate(name):
        counter = index + 2
        rounds = (counter + 5) * (counter + 1)
        if index < 5:
            rounds = (counter + 5) * (counter - 1) * counter
        for _ in range(rounds):
            char ^= (char * 32377 + 43651999) % 30841
        state ^= char
    decoded = bytearray(payload)
    start = 0
    while start < len(decoded):
        stop = min(start + len(decoded) // 5 + state // 256, len(decoded))
        for offset in range(start, stop):
            decoded[offset] ^= state & 255
        start = stop
        state ^= (state * 30859 + 38093791) % 32611
    return bytes(decoded)


def code_nodes(node):
    if isinstance(node, Code):
        yield node
        for field in node.fields:
            yield from code_nodes(field)
    elif isinstance(node, Group):
        for item in node.items:
            yield from code_nodes(item)


def code_semantics(node):
    """Ignore intern-reference renumbering and source-line metadata only."""
    if isinstance(node, Atom):
        return node.value if node.value is not None else node.raw
    if isinstance(node, Group):
        return node.tag, tuple(code_semantics(item) for item in node.items)
    if isinstance(node, Code):
        # Descendants are checked independently, so changing the intended method
        # does not falsely count all enclosing code objects as semantic edits.
        return b"nested-code", node.fields[6].value
    raise AssertionError("unexpected marshal node")


class NativeCipherTests(unittest.TestCase):
    def test_name_and_key_golden_vectors(self):
        # Manually pinned from native arithmetic, not generated from the fixture.
        keys = (253, 168, 139, 169, 142)
        self.assertEqual(module_seed(b"dgtuieditor"), 6141)
        self.assertEqual(seed_from_keys(keys), 6141)
        self.assertEqual(
            parameters_for_name(b"dgtuieditor", 22441),
            (keys, (4511, 9012, 13542, 18070)),
        )
        self.assertEqual(
            parameters_for_name(b"authored", 512),
            ((140, 89, 30, 116, 106), (176, 316, 512, 512)),
        )
        self.assertEqual(
            bounds_from_keys((226, 28, 112, 247, 187), 10335), (2163, 4281, 6390, 8474)
        )

    def test_all_states_are_bounded_but_keys_are_not_always_unique(self):
        # There are two collisions: never choose the first matching seed.
        seen, collisions = {}, []
        for seed in range(32768):
            keys = sequence(seed)
            if keys in seen:
                collisions.append(keys)
            seen[keys] = seed
            self.assertEqual(bounds_from_seed(seed, 1)[-1], 1)
        self.assertEqual(len(seen), 32766)
        for keys in collisions:
            with self.assertRaisesRegex(ValueError, "unique"):
                seed_from_keys(keys)

    def test_incomplete_research_keys_require_native_name_and_directory_hash(self):
        # Entry 0's historical row duplicated adjacent keys. Hand-author a new
        # harmless marshal tree with its name, not a copy of the game payload.
        native = codec.encode(minimal_pyc("py25", filename=b"pubvoiceutil.py"))
        payload = engine_decrypt(b"pubvoiceutil", native + bytes(323 - len(native)))
        keys, bounds = (18, 18, 225, 225, 84), (64, 166, 193, 295)
        expected = (18, 225, 84, 214, 181), (166, 295, 323, 323)
        self.assertEqual(
            resolve_parameters(payload, keys, bounds, 0x0008914C), expected
        )
        # No readable metadata hint: bounded native candidates still require
        # seed AND directory identity, not merely a parseable marshal tree.
        self.assertEqual(
            resolve_parameters(payload, keys, (1, 1, 1, 1), 0x0008914C), expected
        )
        with self.assertRaisesRegex(ValueError, "identity"):
            resolve_parameters(payload, keys, bounds, 0x0008914D)
        with self.assertRaisesRegex(ValueError, "identity"):
            resolve_parameters(payload, (19, *keys[1:]), bounds, 0x0008914C)

    def test_only_exact_accepted_package_entry_has_known_ten_zero_slot_padding(self):
        stored = zlib.compress(b"cipher-input") + bytes(10)
        digest = "4bf116d0a6e62848bc1724ddfc67877c5a9db95a52768e8fa1d6f6d520318678"
        archive = SimpleNamespace(
            fingerprint=lambda: digest, read_stored=lambda _: stored
        )
        self.assertEqual(inflate_script(archive, 918), b"cipher-input")
        with self.assertRaises(ValueError):
            inflate_script(archive, 917)
        archive.fingerprint = lambda: "0" * 64
        with self.assertRaises(ValueError):
            inflate_script(archive, 918)
        archive.fingerprint = lambda: digest
        for bad in (stored + b"x", stored + zlib.compress(b"other") + bytes(10)):
            archive.read_stored = lambda _, payload=bad: payload
            with self.assertRaises(ValueError):
                inflate_script(archive, 918)

    def test_invalid_keys_size_and_import_name_are_rejected(self):
        for keys in ((1, 11, 21, 31, 41), (True, 1, 2, 3, 4), (1,), (256,) * 5):
            with self.assertRaises(ValueError):
                seed_from_keys(keys)
        for size in (0, -1, True, 64 * 1024 * 1024 + 1):
            with self.assertRaises(ValueError):
                bounds_from_seed(6141, size)
        for name in (b"", b"a\0b", b"a" * 129, "authored"):
            with self.assertRaises(ValueError):
                module_seed(name)

    def test_catalog_is_immutable_and_uncalibrated_profiles_cannot_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw, rows = script_fixture(expanded_size=1024)
            package, catalog = root / "script.fls", root / "keys.json"
            package.write_bytes(raw)
            correct = tuple(rows["0"]["bounds"])
            rows["0"]["bounds"][0] -= 3
            before = json.dumps(rows).encode()
            catalog.write_bytes(before)
            with ArchiveDocument(package) as archive:
                profile = load_profile(
                    archive,
                    0,
                    catalog,
                    archive_sha256=archive.fingerprint(),
                    catalog_sha256=sha(before),
                )
                self.assertEqual(profile.bounds, correct)
                with self.assertRaisesRegex(ValueError, "native cipher"):
                    replace(profile, bounds=tuple(rows["0"]["bounds"])).validate(
                        archive, 0
                    )
            self.assertEqual(catalog.read_bytes(), before)
            self.assertEqual(package.read_bytes(), raw)


class NativeCipherMaterialTests(unittest.TestCase):
    def inputs(self):
        location = os.environ.get("MXSJ_M2_REPO")
        if not location:
            self.skipTest("opt-in read-only original package/DLL required")
        repo = Path(location)
        return repo, repo / "tools/decompiler/script_fls_keys.json"

    def test_binary_constants_and_character_back_edge_are_pinned(self):
        repo, _ = self.inputs()
        data = (repo / "mxmain.dll").read_bytes()
        self.assertEqual(
            sha(data),
            "637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d",
        )
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        count = struct.unpack_from("<H", data, pe + 6)[0]
        opt = struct.unpack_from("<H", data, pe + 20)[0]
        base = struct.unpack_from("<I", data, pe + 24 + 28)[0]

        def read(va, size):
            for index in range(count):
                vsize, rva, rawsize, raw = struct.unpack_from(
                    "<IIII", data, pe + 24 + opt + index * 40 + 8
                )
                if rva <= va - base and va - base + size <= rva + min(vsize, rawsize):
                    start = raw + va - base - rva
                    return data[start : start + size]
            raise AssertionError("native cipher VA outside file-backed section")

        for va, hex_bytes in (
            (0x45D413, "33db0fb63c30"),
            (0x45D440, "69c7797e0000059f139a02"),
            (0x45D477, "7c9c"),  # signed -100 -> 0x45D415, not EBX reset
            (0x45D4D5, "c1f808038560ffffff03f0"),
            (0x45D4F8, "301439"),
            (0x45D509, "69c18b78000005df434502"),
        ):
            expected = bytes.fromhex(hex_bytes)
            self.assertEqual(read(va, len(expected)), expected)

    def test_all_5002_original_modules_decode_without_seam_guesses(self):
        repo, catalog = self.inputs()
        before = catalog.read_bytes()
        self.assertEqual(sha(before), CATALOG_SHA)
        with ArchiveDocument(repo / "data/script.fls") as archive:
            digest = archive.fingerprint()
            self.assertEqual(
                digest,
                "8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72",
            )
            self.assertEqual(len(archive.entries), 5002)
            for entry in archive.entries:
                with self.subTest(index=entry.index):
                    profile = load_profile(
                        archive,
                        entry.index,
                        catalog,
                        archive_sha256=digest,
                        catalog_sha256=CATALOG_SHA,
                    )
                    native = profile.crypt(
                        zlib.decompress(archive.read_stored(entry.index))
                    )
                    standard = codec.decode(native, padding=True)
                    filename = parse(standard[8:]).fields[5].value
                    name = (
                        filename.replace(b"\\", b"/")
                        .rsplit(b"/", 1)[-1]
                        .rsplit(b".", 1)[0]
                    )
                    self.assertEqual(
                        engine_decrypt(
                            name, zlib.decompress(archive.read_stored(entry.index))
                        ),
                        native,
                    )
            self.assertEqual(archive.fingerprint(), digest)
        self.assertEqual(catalog.read_bytes(), before)

    def test_complete_recompile_matches_name_side_engine_decryption(self):
        repo, catalog = self.inputs()
        exe = os.environ.get("MXSJ_PY25")
        if not exe:
            self.skipTest("real standard CPython 2.5.6 compiler required")
        compiler = inspect_compiler(Path(exe), "py25")
        from script_editor.core.project.document import Binding
        from script_editor.core.project.storage import CatalogRef, ProjectState
        from script_editor.core.services.workflow import (
            Snapshot,
            prepare_build,
            publish_build,
        )

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "dgtuieditor.py"
            source.write_bytes(
                (
                    repo
                    / "tools/client_patches/native_uieditor_open_list_v3/dgtuieditor.py"
                ).read_bytes()
            )
            with ArchiveDocument(repo / "data/script.fls") as archive:
                binding = Binding.associate(archive, 918, source)
                ref = CatalogRef(
                    archive.path, archive.fingerprint(), catalog, CATALOG_SHA
                )
                profile = load_profile(
                    archive,
                    918,
                    catalog,
                    archive_sha256=archive.fingerprint(),
                    catalog_sha256=CATALOG_SHA,
                )
                original = parse(
                    codec.decode(
                        profile.crypt(zlib.decompress(archive.read_stored(918))),
                        padding=True,
                    )[8:]
                )
            plan = prepare_build(
                Snapshot(binding, source.read_text(encoding="utf-8"), "py25"),
                compiler,
                ref,
            )
            report, _ = publish_build(
                plan, root / "script-new.fls", ProjectState((binding,), (ref,))
            )
            self.assertEqual(report.unchanged_entries, 5001)
            with ArchiveDocument(report.output) as archive:
                expanded = zlib.decompress(archive.read_stored(918))
            native = engine_decrypt(b"dgtuieditor", expanded)
            standard = codec.decode(native, padding=True)
            pyc = root / "fresh.pyc"
            compile_standard(
                compiler,
                source.read_text(encoding="utf-8"),
                b"script\\uieditor\\dgtuieditor.py",
                pyc,
            )
            self.assertEqual(standard[8:], pyc.read_bytes()[8:])
            nodes = tuple(code_nodes(parse(standard[8:])))
            self.assertEqual(len(nodes), 60)
            changed = []
            for old, new in zip(tuple(code_nodes(original)), nodes, strict=True):
                self.assertEqual(old.fields[6].value, new.fields[6].value)
                before = (
                    old.header,
                    old.code,
                    tuple(code_semantics(v) for v in old.fields),
                )
                after = (
                    new.header,
                    new.code,
                    tuple(code_semantics(v) for v in new.fields),
                )
                if before != after:
                    changed.append(new.fields[6].value)
            self.assertEqual(changed, [b"GetFileInfo"])
            self.assertTrue(
                all(
                    node.fields[5].value == b"script\\uieditor\\dgtuieditor.py"
                    for node in nodes
                )
            )
            self.assertEqual(sha(catalog.read_bytes()), CATALOG_SHA)
