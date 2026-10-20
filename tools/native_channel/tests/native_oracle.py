"""Bounded offline x86 oracle. No DLL loader, imports, network or game scripts.

Run directly with --write to regenerate synthetic fixtures, otherwise compare.
Requires pefile and Unicorn; ordinary unit tests require neither nor game files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

import pefile
from unicorn import UC_ARCH_X86, UC_HOOK_CODE, UC_MODE_32, Uc
from unicorn.x86_const import (
    UC_X86_REG_EAX,
    UC_X86_REG_ECX,
    UC_X86_REG_EIP,
    UC_X86_REG_ESP,
)

CONTEXT = 0x4100000
INPUT = 0x4200000
OUTPUT = 0x4300000
RETURN = 0x4000000
SAMPLES = {
    "mxmain.dll": "637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d",
    "exe/render.dll": "7c1563df5e86c7950d2a21d5240c94c7"
    "9586e287b7fc3ebff877197ae747365f",
}


class Oracle:
    def __init__(self, root: Path, name: str):
        path = root / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != SAMPLES[name]:
            raise ValueError(f"sample hash mismatch: {name}")
        pe = pefile.PE(str(path))
        image = pe.get_memory_mapped_image()
        self.u = Uc(UC_ARCH_X86, UC_MODE_32)
        self.u.mem_map(0x400000, (len(image) + 4095) // 4096 * 4096)
        self.u.mem_write(0x400000, image)
        self.u.mem_map(RETURN, 0x400000)
        # Only /GS cookie helper is stubbed for the decompressor. No cipher
        # instruction is intercepted. Native input files are never modified.
        if name == "mxmain.dll":
            self.u.hook_add(UC_HOOK_CODE, self._cookie, begin=0x5C10A4, end=0x5C10A4)

    @staticmethod
    def _cookie(u: Uc, address: int, size: int, user: object) -> None:
        stack = u.reg_read(UC_X86_REG_ESP)
        target = struct.unpack("<I", u.mem_read(stack, 4))[0]
        u.reg_write(UC_X86_REG_ESP, stack + 4)
        u.reg_write(UC_X86_REG_EIP, target)

    def call(
        self, address: int, args: tuple[int, ...] = (), context: int = CONTEXT
    ) -> int:
        self.u.reg_write(UC_X86_REG_ESP, 0x40F0000)
        self.u.reg_write(UC_X86_REG_ECX, context)
        self.u.mem_write(
            0x40F0000, struct.pack("<" + "I" * (len(args) + 1), RETURN, *args)
        )
        self.u.emu_start(address, RETURN, timeout=10_000_000, count=20_000_000)
        if self.u.reg_read(UC_X86_REG_EIP) != RETURN:
            raise RuntimeError("native function exceeded execution budget")
        return self.u.reg_read(UC_X86_REG_EAX)

    def derive(self, address: int, seed: int) -> tuple[int, ...]:
        self.call(address, (seed, CONTEXT, CONTEXT + 4, CONTEXT + 8, CONTEXT + 12))
        return struct.unpack("<4I", self.u.mem_read(CONTEXT, 16))

    def crypt(self, data: bytes) -> bytes:
        self.u.mem_write(INPUT, data)
        self.call(0x92C3B0, (INPUT, len(data)))
        return bytes(self.u.mem_read(INPUT, len(data)))

    def cipher_init(self, key: int, skip: int) -> None:
        self.u.mem_write(CONTEXT + 0x1008, struct.pack("<2I", key, skip))
        self.call(0x92C380, (key,))
        self.call(0x92C3B0, (0, skip))

    def decode(self, data: bytes) -> bytes:
        self.u.mem_write(INPUT, data)
        size = self.call(0x4C5E40, (INPUT, len(data), OUTPUT, 65536))
        if size > 65536:
            raise RuntimeError("unexpected native decode result")
        return bytes(self.u.mem_read(OUTPUT, size))


def native_codes(codes: list[int]) -> bytes:
    # Independent test fixture construction, not the production packer.
    bits = "".join(f"{code:011b}" for code in codes)
    bits += "0" * (-len(bits) % 8)
    return int(bits, 2).to_bytes(len(bits) // 8, "big")


def generate(root: Path) -> dict:
    target = Oracle(root, "mxmain.dll")
    render = Oracle(root, "exe/render.dll")
    result = {"samples": SAMPLES, "cipher": [], "blocks": [], "lzw": []}
    for seed in (0, 1, 0x12345678, 0x80000000, 0xFFFFFFFF):
        keys = target.derive(0x4ABB20, seed)
        if keys != render.derive(0x817360, seed):
            raise AssertionError("native derivation differs")
        row = {"seed": seed, "keys": list(keys), "directions": []}
        for key, skip in ((keys[0], keys[2]), (keys[1], keys[3])):
            render.cipher_init(key, skip)
            plaintext = bytes(i % 251 for i in range(9000))
            ciphertext = render.crypt(plaintext)
            render.cipher_init(key, skip)
            split = b"".join(
                render.crypt(plaintext[a:b])
                for a, b in (
                    (0, 1),
                    (1, 4095),
                    (4095, 4096),
                    (4096, 8193),
                    (8193, 9000),
                )
            )
            if split != ciphertext:
                raise AssertionError("native stream is not chunk invariant")
            row["directions"].append(
                {
                    "prefix_hex": ciphertext[:64].hex(),
                    "sha256_9000": hashlib.sha256(ciphertext).hexdigest(),
                }
            )
        result["cipher"].append(row)
    for state in (0, 1, 0x12345678, 0xFFFFFFFF):
        target.u.mem_write(CONTEXT, struct.pack("<I", state))
        final = target.call(0x4C5D00, (CONTEXT,))
        block = bytes(target.u.mem_read(CONTEXT + 8, 4096))
        render.u.mem_write(CONTEXT, struct.pack("<I", state))
        other = render.call(0x92C610, (CONTEXT,))
        if final != other or block != bytes(render.u.mem_read(CONTEXT + 8, 4096)):
            raise AssertionError("native generators differ")
        result["blocks"].append(
            {
                "state": state,
                "final": final,
                "sha256": hashlib.sha256(block).hexdigest(),
            }
        )
    # Consecutive packets exercise persistent dictionary, KwKwK, full table,
    # delayed reset and literal zero. The native constructor runs only once.
    target.call(0x4C5D50)
    sequences = [
        [65, 66, 256, 258, 2047],
        [256, 0, 2047],
        [i % 251 for i in range(7000)] + [2047],
        [1, 2, 2047],
    ]
    for codes in sequences:
        wire = native_codes(codes)
        decoded = target.decode(wire)
        result["lzw"].append(
            {
                "codes": codes,
                "output_hex": decoded.hex(),
                "wire_sha256": hashlib.sha256(wire).hexdigest(),
                "next_code": struct.unpack(
                    "<I", target.u.mem_read(CONTEXT + 0x4854, 4)
                )[0],
                "full_count": struct.unpack(
                    "<I", target.u.mem_read(CONTEXT + 0x486C, 4)
                )[0],
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path(__file__).resolve().parents[3]
    )
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = generate(args.repo)
    path = Path(__file__).resolve().parents[1] / "evidence" / "vectors.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    elif result != json.loads(path.read_text(encoding="utf-8")):
        raise AssertionError("native vectors changed")
    print("PASS: native derivation, cipher chunks, blocks and persistent LZW")


if __name__ == "__main__":
    main()
