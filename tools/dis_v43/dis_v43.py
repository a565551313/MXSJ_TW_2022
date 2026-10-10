#!/usr/bin/env python3
"""Alignment-fit disassembler for the game's custom S-box bytecode, driven by
mapping_table_v4.json version 4.3-taskB (notes/co_code_analysis/).

Method (see P3-result.md section 1):
  1. Opcode sizes/names come from the v4.3 table (table A + table B).
  2. Dual-variant bytes (0x37, 0x6C, 0x90) and unknown bytes are tried at
     BOTH 1-byte and 3-byte sizes; the parse must end exactly at co_code end
     (end-exact) -- alignment fitting.
  3. Solutions are ranked by jump-target alignment: A2 = absolute target,
     B7/E3/AF/D3/E5 = pos+3+arg (v4.3 settled; A2 absolute). Targets that
     land on instruction starts (or EOF) score; misaligned targets penalise.
  4. Arg plausibility for known 3-byte ops (name/const/varname index ranges;
     CALL_FUNCTION allows a kwarg count in the high byte).

Caveats (from the multi-variant S-box proof in v4.3, 0x6C/0x37):
  the same byte can have different size/meaning per code object. The
  annotations emitted here (DUP_TOP / ROT_TWO / BINARY_MODULO / SLICE / ...)
  for bytes the v4.3 table marks differently are CONTEXT findings from
  netserver.py function code -- they are printed with a '(ctx)' tag, they do
  NOT override the v4.3 table.

Usage:
  dis_v43.py <marshal.bin> --list
  dis_v43.py <marshal.bin> [path-filter ...]        # substring match
  dis_v43.py <marshal.bin.py /CRandomConnectMgr/Connect

Provenance: written for parallel task P3 (2026-10-10); reproduces the
disassembly in P3-result.md appendices. Read-only.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_marshal import load, walk, codename  # noqa: E402

# ---- mapping_table_v4.json (4.3-taskB), table A + table B -----------------
OPS = {
    # 1-byte
    0x05: ("BINARY_?", 1), 0x06: ("PUSHER_?", 1), 0x08: ("IMPORT_STAR", 1),
    0x09: ("BINARY_?", 1), 0x15: ("BINARY_?", 1), 0x23: ("BINARY_SUBTRACT?", 1),
    0x30: ("POP_TOP?", 1), 0x36: ("GET_ITER", 1), 0x38: ("LOAD_LOCALS", 1),
    0x3F: ("BINARY_?", 1), 0x41: ("POP_TOP", 1), 0x42: ("BUILD_CLASS", 1),
    0x43: ("BINARY_?|NOP_?", 1), 0x55: ("RETURN_VALUE", 1),
    0x58: ("BINARY_SUBSCR", 1), 0x5A: ("NOP_?", 1),
    # 3-byte
    0x71: ("STORE_FAST", 3), 0x72: ("LOAD_CONST?", 3), 0x85: ("LOAD_NAME", 3),
    0x8F: ("LOAD_CONST", 3), 0x95: ("COMPARE_OP", 3), 0x98: ("STORE_NAME", 3),
    0xA2: ("JUMP_ABSOLUTE", 3), 0xAA: ("LOAD_NAME", 3), 0xAD: ("IMPORT_FROM", 3),
    0xAF: ("FOR_ITER", 3), 0xB7: ("POP_JUMP_IF_FALSE", 3), 0xBB: ("LOAD_CONST", 3),
    0xC1: ("LOAD_FAST", 3), 0xC4: ("STORE_NAME", 3), 0xC5: ("STORE_ATTR", 3),
    0xCA: ("BUILD_LIST", 3), 0xD3: ("SETUP_LOOP", 3), 0xD9: ("LOAD_ATTR", 3),
    0xDA: ("CALL_FUNCTION", 3), 0xDE: ("BUILD_TUPLE", 3), 0xE0: ("IMPORT_NAME", 3),
    0xE3: ("JUMP_IF_TRUE?", 3), 0xE5: ("JUMP_FORWARD", 3), 0xEA: ("LOAD_?", 3),
    0xFB: ("MAKE_FUNCTION", 3), 0x91: ("LOAD_GLOBAL", 3), 0xBF: ("STORE_GLOBAL", 3),
}
DUAL = {0x37, 0x6C, 0x90}          # v4.3 proven dual-variant (try 3B and 1B)
# NOTE: 0x00 must NOT be treated as an instruction here: allowing it lets
# wrong 3B readings of dual/unknown bytes "escape" through 00-pads and crowd
# out the correct parse (verified on CRandomConnectMgr.Connect during P3).
UNKNOWN = {0x40, 0x0E, 0x0D, 0x3D, 0x0B, 0x1F, 0x31, 0xCF, 0x10,
           0xC0, 0x39, 0x9A, 0xFC, 0x20}
JMP_ABS = {0xA2}
JMP_REL3 = {0xAF, 0xD3, 0xE5, 0xB7}      # target = pos + 3 + arg
JMP_E3 = {0xE3}                          # +3 suspected (v4.3); see ranking
CMP = ["<", "<=", "==", "!=", ">", ">=", "in", "not in",
       "is", "is not", "exc-match", "BAD"]

# Context semantics proven inside netserver.py function code objects during
# P3 (stack-necessity). Display-only; does not override the v4.3 table.
CTX_1B = {
    0x30: "DUP_TOP(ctx)", 0x5A: "ROT_TWO(ctx)", 0x43: "INPLACE_ADD?(ctx)",
    0x37: "BINARY_MODULO?(ctx)", 0x3D: "BINARY_FLOORDIV?(ctx)",
    0x0E: "SLICE+2?(ctx)", 0x0D: "SLICE+1?(ctx)",
    0x0B: "PRINT_ITEM?(ctx)", 0x1F: "PRINT_NEWLINE?(ctx)",
    0x40: "POP_BLOCK?(ctx)",
}


def disasm(code, names, consts, varnames, max_solutions=8):
    """Return end-exact instruction lists, best-aligned first."""
    n = len(code)

    def cand(pos):
        b = code[pos]
        if b in OPS:
            yield OPS[b][1], OPS[b][0], b, False
        elif b in DUAL:
            yield 3, "UNPACK_SEQ?", b, True
            yield 1, "BINARY_/STORE_SUBSCR?", b, True
        elif b in UNKNOWN:
            yield 1, "UNK", b, True
            yield 3, "UNK", b, True

    solutions = []

    def bt(pos, insns):
        if len(solutions) >= max_solutions:
            return
        if pos == n:
            solutions.append(list(insns))
            return
        if pos > n:
            return
        for sz, name, b, amb in cand(pos):
            arg = None
            if sz == 3:
                if pos + 3 > n:
                    continue
                arg = code[pos + 1] | (code[pos + 2] << 8)
                if b in OPS and not amb:      # arg plausibility
                    if b == 0xDA:             # CALL: lo=pos-argc, hi=kwarg-argc
                        if (arg & 0xFF) > 12 or (arg >> 8) > 4:
                            continue
                    elif b == 0x95:           # COMPARE_OP
                        if arg > 11:
                            continue
                    elif b in (0x85, 0xAA, 0x98, 0xC4, 0xC5, 0xD9, 0xE0, 0xAD):
                        if arg >= len(names):
                            continue
                    elif b in (0x8F, 0xBB, 0x72):
                        if arg >= len(consts) + 2:
                            continue
                    elif b in (0x71, 0xC1):
                        if arg >= len(varnames) and arg >= 4:
                            continue
            insns.append((pos, sz, name, b, arg, amb))
            bt(pos + sz, insns)
            insns.pop()

    bt(0, [])

    def score(sol):
        starts = {p for p, _, _, _, _, _ in sol}
        good = bad = 0
        for p, sz, name, b, arg, amb in sol:
            if arg is None:
                continue
            if b in JMP_ABS:
                t = arg
            elif b in JMP_REL3 or b in JMP_E3:
                t = p + 3 + arg
            else:
                continue
            if t in starts or t == n:
                good += 1
            else:
                bad += 1
        unk3 = sum(1 for _, sz, nm, _, _, _ in sol if nm == "UNK" and sz == 3)
        unk1 = sum(1 for _, sz, nm, _, _, _ in sol if nm == "UNK" and sz == 1)
        return (-bad, good, -unk3, -unk1)

    solutions.sort(key=score)
    return solutions


# ---- display ---------------------------------------------------------------

def _s(x):
    return x.decode("utf-8", "replace") if isinstance(x, bytes) else str(x)


def _const_repr(c):
    if isinstance(c, dict) and "code" in c:
        return "<code %s len=%d>" % (codename(c), len(c["code"]))
    if isinstance(c, bytes):
        try:
            big5 = c.decode("big5")
            return "b'%s' (Big5:%r)" % (c.hex(), big5)
        except (UnicodeDecodeError, ValueError):
            return "b'%s'" % c.hex()
    return repr(c)


def show(label, code, names, varnames, consts, out=sys.stdout):
    code = code if isinstance(code, bytes) else bytes(code)
    sols = disasm(code, names, consts, varnames)
    print("=" * 110, file=out)
    print("%s  len=%d  pools: names=%d consts=%d varnames=%d  | end-exact solutions: %d"
          % (label, len(code), len(names), len(consts), len(varnames), len(sols)), file=out)
    if not sols:
        print("  !! NO END-EXACT SOLUTION", file=out)
        return None
    sol = sols[0]
    starts = {p for p, _, _, _, _, _ in sol} | {len(code)}
    for p, sz, name, b, arg, amb in sol:
        raw = code[p:p + sz].hex()
        if sz == 1 and b in CTX_1B:
            name = CTX_1B[b]
        note = ""
        if b in (0x8F, 0xBB, 0x72):
            if arg is not None and arg < len(consts):
                note = " ; const[%d]=%s" % (arg, _const_repr(consts[arg]))
            else:
                note = " ; const[%d]=<OUT OF RANGE pool=%d>" % (arg, len(consts))
        elif b in (0x85, 0xAA, 0x98, 0xC4, 0xC5, 0xD9, 0xE0, 0xAD):
            if arg is not None and arg < len(names):
                note = " ; names[%d]=%r" % (arg, _s(names[arg]))
            else:
                note = " ; names[%d]=<OOR %d>" % (arg, len(names))
        elif b in (0x71, 0xC1, 0x72):
            if arg is not None and arg < len(varnames):
                note = " ; varnames[%d]=%r" % (arg, _s(varnames[arg]))
            else:
                note = " ; varnames[%d]=<OOR %d>" % (arg, len(varnames))
        elif b == 0x95:
            note = " ; CMP %s" % (CMP[arg] if arg is not None and arg < len(CMP) else "?")
        elif b in JMP_ABS:
            t = arg
            note = " ; ->0x%X %s" % (t, "OK" if (t in starts or t == len(code))
                                     else "*** MISALIGNED ***")
        elif b in JMP_REL3 or b in JMP_E3:
            t = p + 3 + arg
            note = " ; pos+3+arg=0x%X %s" % (t, "OK" if (t in starts or t == len(code))
                                             else "*** MISALIGNED ***")
        elif b in (0xDA, 0xFB, 0xDE, 0xCA):
            if b == 0xDA:
                note = " ; %d pos + %d kw" % (arg & 0xFF, arg >> 8)
            else:
                note = " ; arg=%d" % arg
        if amb:
            note += "   [AMBIGUOUS-SIZE]"
        print("  0x%03X  %-8s %-24s%s" % (p, raw, name, note), file=out)
    return sols


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    path, filters = args[0], args[1:]
    list_only = "--list" in filters
    filters = [f for f in filters if not f.startswith("--")]
    root = load(path)
    if list_only:
        for p, c in walk(root):
            print("%-50s len=%-5d lineno=%s argcount=%d"
                  % (p or "<module>", len(c["code"]), c["firstlineno"], c["argcount"]))
        return
    for p, c in walk(root):
        if filters and not any(f in p for f in filters):
            continue
        names = [x.decode("utf-8", "replace") if isinstance(x, bytes) else x
                 for x in c["names"]]
        varnames = [x.decode("utf-8", "replace") if isinstance(x, bytes) else x
                    for x in c["varnames"]]
        consts = [x if (isinstance(x, dict) and "code" in x) else x
                  for x in c["consts"]]
        show(p or "<module>", c["code"], names, varnames, consts)


if __name__ == "__main__":
    main()
