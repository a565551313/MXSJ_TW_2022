#!/usr/bin/env python3
"""Read-only Python 2.7 marshal reader for decoded .fls script blobs.

Parses a marshal object tree (as produced by decoder-artifacts/
decode_entry516.py, e.g. entry516-five-xor-marshal.bin) and exposes the
code-object tree with FULL const pools (ints included).

Why this exists: notes/co_code_analysis/code_objects.json only keeps
string constants (its generator drops ints/floats), which is not enough
to decode expressions like `chr(port % 256)` that reference integer
constants. This module re-parses the marshal blob directly.

Provenance: written for parallel task P3 (2026-10-10), see
work/dream-world-connect-login-map/notes/parallel-20261010/P3-result.md.
Read-only: never writes to the client sample.
"""

from __future__ import annotations

import struct


class MarshalReader:
    """Small Python 2.7 marshal reader with interned-string support."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.interned = []

    # -- primitives ------------------------------------------------------
    def take(self, size: int) -> bytes:
        if self.pos + size > len(self.data):
            raise ValueError("marshal truncated at 0x%x, need %d" % (self.pos, size))
        r = self.data[self.pos:self.pos + size]
        self.pos += size
        return r

    def byte(self) -> int:
        return self.take(1)[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.take(4))[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    # -- object tree -----------------------------------------------------
    def read(self):
        t = self.byte()
        if t in (ord("0"), ord("N")):
            return None
        if t == ord("F"):
            return False
        if t == ord("T"):
            return True
        if t == ord("S"):
            return StopIteration
        if t == ord("i"):
            return self.i32()
        if t == ord("I"):
            return struct.unpack("<q", self.take(8))[0]
        if t == ord("f"):
            return float(self.take(self.u32()).decode("ascii"))
        if t == ord("g"):
            return struct.unpack("<d", self.take(8))[0]
        if t in (ord("s"), ord("t"), ord("a"), ord("A")):
            v = self.take(self.u32())
            if t == ord("t"):
                self.interned.append(v)
            return v
        if t == ord("u"):
            return self.take(self.u32()).decode("utf-8", "replace")
        if t == ord("R"):
            return self.interned[self.u32()]
        if t in (ord("("), ord("["), ord("<")):
            n = self.u32()
            items = [self.read() for _ in range(n)]
            return tuple(items) if t == ord("(") else items
        if t == ord("{"):
            d = {}
            while True:
                k = self.read()
                if k is None:
                    break
                d[k] = self.read()
            return d
        if t == ord("c"):
            return self.read_code_object()
        raise ValueError("unsupported marshal type 0x%02x at 0x%x" % (t, self.pos - 1))

    def read_code_object(self) -> dict:
        argcount = self.i32()
        nlocals = self.i32()
        stacksize = self.i32()
        flags = self.i32()
        code = self.read()
        consts = self.read()
        names = self.read()
        varnames = self.read()
        freevars = self.read()
        cellvars = self.read()
        filename = self.read()
        name = self.read()
        firstlineno = self.i32()
        lnotab = self.read()
        if isinstance(code, str):
            code = code.encode("latin-1")
        return dict(argcount=argcount, nlocals=nlocals, stacksize=stacksize,
                    flags=flags, code=bytes(code), consts=consts, names=names,
                    varnames=varnames, freevars=freevars, cellvars=cellvars,
                    filename=filename, name=name, firstlineno=firstlineno,
                    lnotab=lnotab)


def load(path: str) -> dict:
    """Parse a marshal blob and return the root code object (dict)."""
    with open(path, "rb") as f:
        data = f.read()
    r = MarshalReader(data)
    root = r.read()
    if r.pos != len(data):
        raise ValueError("trailing bytes: stopped at 0x%x of 0x%x" % (r.pos, len(data)))
    return root


def codename(c: dict) -> str:
    n = c.get("name")
    return n.decode("utf-8", "replace") if isinstance(n, bytes) else str(n)


def walk(code: dict, path: str = ""):
    """Yield (path, code_object) over the whole tree, depth-first.

    Paths look like '/CRandomConnectMgr/Connect' (root is '').
    """
    yield path, code
    for c in code.get("consts", ()):
        if isinstance(c, dict) and "code" in c:
            for item in walk(c, path + "/" + codename(c)):
                yield item


if __name__ == "__main__":
    import sys
    root = load(sys.argv[1])
    print("root: %s  code_len=%d  %d top-level consts"
          % (codename(root), len(root["code"]), len(root["consts"])))
    for p, c in walk(root):
        print("%-50s len=%-5d lineno=%s argcount=%d"
              % (p or "<module>", len(c["code"]), c["firstlineno"], c["argcount"]))
