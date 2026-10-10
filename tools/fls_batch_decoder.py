#!/usr/bin/env python3
"""Batch decoder for data/script.fls (Task B).

Decodes ALL 5002 entries: FLS directory -> zlib -> 5-segment single-byte XOR
-> Python 2.7 marshal. Each entry uses its OWN 5 XOR keys and boundaries
(discovered by Task B; entry 516's B1/44/30/41/20 are just one instance).

Algorithm (v2, per entry):
  * seg keys: seg0 key is EXACT (exp[0]^0x63='c'); others = mode byte of
    segment middle (top-5 kept as fallback).
  * boundaries: forward greedy. For boundary i, dense-scan candidates,
    score = marshal parse progress (prefix-limited, resumable-equivalent via
    limit); ties broken by region-local plausibility (zeros + printables in
    the differing window). Early-stop once progress runs past scan region.
  * validate: full marshal parse must consume ALL bytes (same criterion as
    decode_entry516.py for entry 516).

Read-only w.r.t. original game files. Outputs go to --output dir.

Examples:
  python3 tools/fls_batch_decoder.py --catalog out/script-catalog.csv --jobs 2
  python3 tools/fls_batch_decoder.py --index 516 --output out/entry516/
  python3 tools/fls_batch_decoder.py --all --output out/all/ --jobs 2
"""
from __future__ import annotations
import argparse, csv, json, os, struct, sys, time, zlib
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------- FLS basics
# (decode_directory vendored from notes/decoder-artifacts/decode_entry516.py)
MASK32 = 0xFFFFFFFF
EXPECTED_COUNT = 5002
EXPECTED_INDEX_OFFSET = 0x173EB22
NSEGS = 5
RADII = [200, 280, 340, 400]  # per-boundary scan radius around len*i//5

def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]

def decode_directory(index, raw):
    entry_id, r1, r2, r3 = raw
    f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
    f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
    f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
    return f1, f2, f3

def extract_entry(archive: bytes, entry_index: int):
    if archive[:4] != b"0SLF":
        raise ValueError("bad FLS magic")
    count = u32(archive, 4); index_offset = u32(archive, 8)
    raw_offset = index_offset + entry_index * 16
    raw = struct.unpack_from("<IIII", archive, raw_offset)
    f1, clen, doff = decode_directory(entry_index, raw)
    comp = archive[doff:doff+clen]
    exp = zlib.decompress(comp)
    return {"index": entry_index, "id": raw[0], "f1": f1,
            "clen": clen, "doff": doff, "comp": comp, "exp": exp}

# ------------------------------------------------------- marshal reader (2.7)
class _LimitReached(Exception):
    pass

# Hang-circuit-breaker (entry 251: pathological wrong-key decodes nest huge
# containers -> 60K-budget probe still ~3s; scans/combo call marshal_* 1000s
# of times). hits: read-budget aborts this retry (abort scan past 8);
# deadline: wall clock per entry (set in decode_entry_auto).
_SAFETY = {"hits": 0, "deadline": float("inf")}
def _expired() -> bool:
    return (_SAFETY["hits"] > 8 or time.time() > _SAFETY["deadline"])

class MarshalReader:
    """Extended copy of decode_entry516.MarshalReader (+ellipsis/complex/long/
    frozenset, +parse `limit` support for prefix-limited progress scoring)."""
    def __init__(self, data: bytes, limit: int = -1, budget: int = 60000):
        self.data = data; self.pos = 0
        self.limit = limit if limit >= 0 else len(data) + 1
        self.interned_strings = []
        self.code_objects = []
        self.strings = []
        # read budget: corrupt decodes can nest huge containers (tuple 1M x
        # tuple 1M ...) -> exponential reads without pos advancing (entry 251
        # hung 6+ min). Legit max = 32.5K reads (entry 1227, 393KB); 60K
        # budget = ~2x headroom, aborts pathological probes in ~3s.
        self.budget = budget
        self.budget_hit = False

    def take(self, size: int) -> bytes:
        pos = self.pos
        end = pos + size
        if end > len(self.data):
            raise ValueError(f"marshal truncated at 0x{pos:x}, need {size}")
        self.pos = end
        if end > self.limit:
            raise _LimitReached()
        return self.data[pos:end]

    def read(self):
        if self.pos >= self.limit:
            raise _LimitReached()
        self.budget -= 1
        if self.budget <= 0:
            self.budget_hit = True
            raise _LimitReached()
        d = self.data; pos = self.pos
        t = d[pos]; self.pos = pos + 1
        if t == 0x30 or t == 0x4E:      # '0' 'N'
            return None
        elif t == 0x46:                 # 'F'
            return False
        elif t == 0x54:                 # 'T'
            return True
        elif t == 0x53:                 # 'S'
            return StopIteration
        elif t == 0x2E:                 # '.'
            return Ellipsis
        elif t == 0x69:                 # 'i'
            return struct.unpack("<i", self.take(4))[0]
        elif t == 0x49:                 # 'I'
            return struct.unpack("<q", self.take(8))[0]
        elif t == 0x6C:                 # 'l' long
            n = struct.unpack("<i", self.take(4))[0]
            neg = n < 0
            n = -n if neg else n
            v = 0
            for i in range(n):
                v |= struct.unpack("<H", self.take(2))[0] << (15 * i)
            return -v if neg else v
        elif t == 0x66:                 # 'f'
            ln = struct.unpack("<I", self.take(4))[0]
            return float(self.take(ln).decode("ascii"))
        elif t == 0x67:                 # 'g'
            return struct.unpack("<d", self.take(8))[0]
        elif t == 0x78:                 # 'x'
            ln = struct.unpack("<I", self.take(4))[0]
            return complex(self.take(ln).decode("ascii"))
        elif t == 0x79:                 # 'y'
            re = struct.unpack("<d", self.take(8))[0]
            im = struct.unpack("<d", self.take(8))[0]
            return complex(re, im)
        elif t in (0x73, 0x74, 0x61, 0x41):  # 's' 't' 'a' 'A'
            ln = struct.unpack("<I", self.take(4))[0]
            v = self.take(ln)
            self.strings.append(v)
            if t == 0x74 or t == 0x41:
                self.interned_strings.append(v)
            return v
        elif t == 0x75:                 # 'u'
            ln = struct.unpack("<I", self.take(4))[0]
            return self.take(ln).decode("utf-8", "replace")
        elif t == 0x52:                 # 'R'
            idx = struct.unpack("<I", self.take(4))[0]
            try:
                return self.interned_strings[idx]
            except IndexError as exc:
                raise ValueError(f"bad marshal string ref {idx}") from exc
        elif t in (0x28, 0x5B, 0x3C, 0x3E):  # '(' '[' '<' '>'
            ln = struct.unpack("<I", self.take(4))[0]
            items = [self.read() for _ in range(ln)]
            if t == 0x28:
                return tuple(items)
            if t == 0x3E:
                try:
                    return frozenset(items)
                except TypeError:
                    return items
            return items
        elif t == 0x7B:                 # '{'
            v = {}
            while True:
                k = self.read()
                if k is None:
                    break
                v[k] = self.read()
            return v
        elif t == 0x63:                 # 'c'
            return self.read_code_object()
        else:
            raise ValueError(f"unsupported marshal type 0x{t:02x} at 0x{pos:x}")

    def read_code_object(self):
        start = self.pos - 1
        d = self.data
        # fast path: 4xi32 + replicate generic reads
        argcount = struct.unpack("<i", self.take(4))[0]
        nlocals = struct.unpack("<i", self.take(4))[0]
        stacksize = struct.unpack("<i", self.take(4))[0]
        flags = struct.unpack("<i", self.take(4))[0]
        code = self.read(); consts = self.read(); names = self.read()
        varnames = self.read(); freevars = self.read(); cellvars = self.read()
        filename = self.read(); name = self.read()
        firstlineno = struct.unpack("<i", self.take(4))[0]
        lnotab = self.read()
        rec = {"offset": start, "argcount": argcount, "nlocals": nlocals,
               "stacksize": stacksize, "flags": flags,
               "code": code, "consts": consts, "names": names,
               "varnames": varnames, "freevars": freevars, "cellvars": cellvars,
               "filename": filename, "name": name, "firstlineno": firstlineno,
               "lnotab": lnotab}
        self.code_objects.append(rec)
        return rec

def marshal_progress(data: bytes, limit: int) -> int:
    """Parse prefix; return bytes consumed (limit if reached past limit)."""
    r = MarshalReader(data, limit)
    try:
        r.read()
    except _LimitReached:
        # budget-hit = pathological nesting (score actual consumed, not limit)
        if r.budget_hit:
            _SAFETY["hits"] += 1
            return r.pos
        return limit
    except Exception:
        return r.pos
    return r.pos  # == len(data) if fully consumed (when limit >= len)

def marshal_try(data: bytes):
    """Return (ok, pos, root, reader). ok=True iff full consume + code root."""
    r = MarshalReader(data)
    try:
        root = r.read()
    except Exception:
        if r.budget_hit:
            _SAFETY["hits"] += 1
        return False, r.pos, None, r
    if r.pos != len(data):
        return False, r.pos, root, r
    if not isinstance(root, dict) or "filename" not in root:
        return False, r.pos, root, r
    return True, r.pos, root, r

# ------------------------------------------------------------- XOR auto-crack
def mode_byte(buf: bytes, lo: int, hi: int, topn=5):
    lo = max(0, lo); hi = min(len(buf), hi)
    if hi <= lo:
        return [(buf[lo] if lo < len(buf) else 0, 0)]
    return [(b, n) for b, n in Counter(buf[lo:hi]).most_common(topn)]

def estimate_keys(exp: bytes):
    n = len(exp)
    out = []
    for s in range(NSEGS):
        lo = (n * s) // NSEGS; hi = (n * (s + 1)) // NSEGS
        mid = (lo + hi) // 2; half = max(8, (hi - lo) // 4)
        out.append(mode_byte(exp, mid - half, mid + half))
    exact0 = exp[0] ^ 0x63
    rest = [c for c in out[0] if c[0] != exact0]
    out[0] = [(exact0, -1)] + rest
    return out

_XTAB_CACHE: dict[int, bytes] = {}
def _xtab(key: int) -> bytes:
    t = _XTAB_CACHE.get(key)
    if t is None:
        t = bytes(b ^ key for b in range(256))
        _XTAB_CACHE[key] = t
    return t

_PRINT = set(range(0x20, 0x7F)) | {9, 10, 13}
import re as _re
_MASS_RE = _re.compile(rb'[\x09\x0a\x0d\x20-\x7e]{8,}')
_IDENT_RE = _re.compile(rb'[A-Za-z0-9_]{4,}')
_LEN_RE = _re.compile(rb'[\x01-\x40]\x00\x00\x00')
def content_score(dec_prefix: bytes) -> tuple:
    """Combined evidence: printable-run mass + 3x zeros + 2x identifier mass.

    Long printable runs (>=8) = real strings; zeros = marshal structure;
    identifier runs ([A-Za-z0-9_]{4,}) = semantic check: XOR with small keys
    preserves printability for upper-case strings (e.g. TRUE "PR_C2R_..."
    vs garbage "NLA],LAU..." both printable) but garbage mixes punctuation
    that breaks identifier runs. Weights mass+4z+ident: zeros are the
    hardest evidence to fake (small-key letter-soup forges mass+ident but
    has ~0 zeros; entry 3300 soup beat TRUE 239-231 at 3/2 weights).
    Returns (mass, zeros, score).
    """
    mass = sum(len(m) for m in _MASS_RE.findall(dec_prefix))
    ident = sum(len(m) for m in _IDENT_RE.findall(dec_prefix))
    z = dec_prefix.count(0)
    return mass, z, mass + 4 * z + ident

def region_plausibility(dec_region: bytes) -> tuple:
    """Within-key boundary tiebreak. Returns (score, zeros, printables)."""
    mass, z, score = content_score(dec_region)
    return score, z, mass

def _clamp_rest(rest: list[int], b: int, n: int) -> list[int]:
    """Clamp rest bounds to [b, n), monotonic (handles b beyond estimates)."""
    out = []
    prev = b
    for r in rest:
        r = max(r, prev)
        r = min(r, n)
        out.append(r)
        prev = r
    return out


def _scan_boundary(exp: bytes, n: int, bounds: list[int], i: int,
                   lo: int, hi: int, rest_base: list[int],
                   keys: list[int], kR: int, xtabs: list, est_i: int,
                   limit: int):
    """Coarse step-4 scan + dense refine. Returns (refined, plo, phi, pn).

    refined: list of (prog, dens, mass, z, -|b-est|, b); dens = content
    density in a FIXED window [lo-64, hi+64) (same bytes compared across b;
    b-anchored windows compare different content = position artifact).
    If kL == kR the boundary is unobservable (identical decodes) -> pin at
    est with full-range plateau (low confidence).
    """
    tabR = _xtab(kR)
    kL = keys[i]
    fwlo = max(0, lo - 64); fwhi = min(n, hi + 64)
    # NOTE: kL == kR uses the normal scan (no pinning): decodes for
    # b <= rest0 are identical (plateau -> nearest-est wins via -dist),
    # while b > rest0 shifts rest-alignment and competes normally.
    # Pinning at est forced a suboptimal alignment when rest0 < TRUE-next.
    if hi - lo <= 400:
        # Small range: dense stride-1 (coarse stride-4 can skip a TRUE b
        # whose neighbors structurally fail while a hiding fluke wins).
        # Gated to <=400 (cheap); bigger ranges use coarse+refine (fast).
        dense = set(range(lo, hi + 1))
    else:
        coarse = []  # (prog, z, b)
        for b in range(lo, hi + 1, 4):
            if _expired():
                return [], -1, -1, 0
            dec = _build_decode(exp, n, bounds, b, rest_base, keys, kR,
                                xtabs, tabR, i)
            prog = marshal_progress(dec, limit)
            z = dec.count(0, max(0, lo - 32), min(n, hi + 32))
            coarse.append((prog, z, b))
        if not coarse:
            return []
        pmax = max(p for p, _, _ in coarse)
        # refine around ALL pmax achievers + zero-top-5 insurance
        targets = {b for p, _, b in coarse if p == pmax}
        by_z = sorted(coarse, key=lambda t: t[1], reverse=True)[:5]
        for _, _, b in by_z:
            targets.add(b)
        dense = set()
        for b in targets:
            for bb in range(max(lo, b - 4), min(hi, b + 4) + 1):
                dense.add(bb)
    out = []
    for bb in dense:
        if _expired():
            break
        dec = _build_decode(exp, n, bounds, bb, rest_base, keys, kR,
                            xtabs, tabR, i)
        prog = marshal_progress(dec, limit)
        mass, z, score = content_score(dec[fwlo:fwhi])
        dens = score / max(1, fwhi - fwlo)
        out.append((prog, dens, mass, z, -abs(bb - est_i), bb))
    out.sort(reverse=True)
    dpmax = out[0][0] if out else -1
    ach = [b for (p, _, _, _, _, b) in out if p == dpmax]
    plo, phi = (min(ach), max(ach)) if ach else (-1, -1)
    return out, plo, phi, len(ach)


def _key_candidates_for(exp: bytes, lo_ext: int, hi_ext: int,
                        seed: int | None = None):
    """Ranked key candidates for a segment spanning ~[lo_ext, hi_ext].

    256-key zero-probe on 3 wide windows (25/50/75%) + middle-mode votes.
    Wide extents deliberately span neighboring segments: the true key wins
    votes wherever its territory overlaps the extent, so even badly
    mis-estimated segments (small entries, dev > seg length) include the
    true key. Returns <=10 keys, best first.
    """
    n = len(exp)
    lo_ext = max(0, lo_ext); hi_ext = min(n, hi_ext)
    span = max(8, hi_ext - lo_ext)
    probes = []
    for frac in (0.25, 0.5, 0.75):
        c = lo_ext + int(span * frac)
        w = max(24, span // 5)
        a, b = max(0, c - w), min(n, c + w)
        if b - a >= 8:
            probes.append((a, b))
    if hi_ext >= n - 1 and n >= 96:
        # Tail probe: tiny-seg4 keys are diluted in wide probes (entry 24).
        probes.append((n - 96, n))
    votes: Counter = Counter()
    struct_probes = []
    for (a, b) in probes:
        seg = exp[a:b]
        scored = []
        for k in range(256):
            z = seg.translate(_xtab(k)).count(0)
            scored.append((z, k))
        scored.sort(reverse=True)
        for z, k in scored[:3]:
            votes[k] += z + 1
        # Per-probe ambiguity: global votes are dominated by strong
        # neighbors (entry 34's seg3-4e hid the tail 48/40 tie + 0x41).
        t1, t2 = scored[0][0], scored[1][0]
        if t1 < 8 or (t1 - t2) < 0.25 * max(1, t1):
            struct_probes.append((a, b))
    # Struct probe: len-field validity (small-lo + 000 + printable
    # content). Catches zero-weak keys (lnotab-alternating tails like
    # entry 34's 0x41, ~0 zeros). Only on ambiguous/weak probes.
    for (a, b) in struct_probes:
        seg = exp[a:b]
        if len(seg) < 12:
            continue
        for k in range(256):
            d = seg.translate(_xtab(k))
            hits = 0
            for m in _LEN_RE.finditer(d):
                p = m.start()
                lo_len = d[p]
                if 1 <= lo_len <= 64 and p + 4 + lo_len <= len(d):
                    frag = d[p+4:p+4+lo_len]
                    if frag and all(c in _PRINT or 0x80 <= c <= 0xFF
                                    for c in frag):
                        hits += 1
                        if hits >= 3:
                            break
            if hits:
                votes[k] += 50 * hits
    # middle-mode votes (classic estimator, robust for clean segments)
    mid = (lo_ext + hi_ext) // 2
    half = max(8, span // 4)
    for b, cnt in mode_byte(exp, mid - half, mid + half, topn=3):
        votes[b] += cnt
    ranked = sorted(votes.items(), key=lambda kv: kv[1], reverse=True)
    out = [k for k, _ in ranked[:10]]
    if seed is not None and seed not in out:
        out = [seed] + out[:9]
    return out


def _sane_filename(fn: str) -> bool:
    if not (3 <= len(fn) <= 260):
        return False
    if not fn.endswith(".py"):
        return False
    if "\\" not in fn and "/" not in fn:
        return False
    for ch in fn:
        o = ord(ch)
        if o in _PRINT or 0x80 <= o <= 0xFF or o > 0xFF:
            continue
        return False
    return True


def _solve_one(exp: bytes, n: int, bounds: list[int], i: int,
               lo: int, hi: int, rest_base: list[int],
               keys: list[int], kcand: list[int], xtabs: list, est_i: int,
               limit: int, force_expand: bool):
    """Solve boundary i (+key i+1). Returns (best, top3) or (None, []).

    best tuple: (scoreF, prog, massF, zF, dens, negdist, b, kR, plo, phi, pn).
    top3: up to 3 distinct-b (b, kR, prog, dens) for combo repair.
    Keys compared by content score on fixed window (progress is
    lucky-inflated across keys); boundaries by (prog, local density).
    """
    fast_keys = kcand[:2] if not force_expand else list(kcand)
    slo = max(0, lo - 64)
    scored = []
    alltops = []  # (prog, dens, b, kR) across keys for top3

    def _scan_range(klist, lor, hir):
        slor = max(0, lor - 64)
        for kR in klist:
            res = _scan_boundary(exp, n, bounds, i, lor, hir, rest_base,
                                 keys, kR, xtabs, est_i, limit)
            if not res:
                continue
            refined, plo, phi, pn = res
            if not refined:
                continue
            for top in refined[:3]:
                alltops.append((top[0], top[1], top[5], kR, plo, phi, pn))
            top = refined[0]
            dec = _build_decode(exp, n, bounds, top[5], rest_base, keys,
                                kR, xtabs, _xtab(kR), i)
            massF, zF, scoreF = content_score(dec[slor:limit])
            scored.append((scoreF, top[0], massF, zF, top[1], top[4],
                           top[5], kR, plo, phi, pn))

    _scan_range(fast_keys, lo, hi)
    if scored and not force_expand:
        scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
        top0 = scored[0]
        zdens = top0[3] / max(1, limit - slo)
        margin = top0[0] - scored[1][0] if len(scored) > 1 else 999
        if top0[1] < hi or zdens < 0.015 or margin < 8:
            _scan_range(kcand[2:], lo, hi)
            scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    if not scored:
        return None, []
    # Repeat tie-break: key repeats (kR == kL) are common; prefer them when
    # (scoreF, prog) tie (1-byte differences are otherwise arbitrary).
    kL0 = keys[i]
    scored.sort(key=lambda t: (t[0], t[1], t[7] == kL0, t[2], t[3], t[4],
                               t[5]),
                reverse=True)
    # Edge-expand: winner clamped at hi/lo -> TRUE boundary beyond radius
    # (the #1 fail cause). Rescan extension with all keys (<=2 rounds).
    prevb = bounds[-1] + 1 if bounds else 1
    _key = lambda t: (t[0], t[1], t[7] == kL0, t[2], t[3], t[4], t[5])
    for _ in range(8):
        cur = sorted(scored, key=_key, reverse=True)[0]
        bb = cur[6]
        plo, phi = cur[8], cur[9]
        grown = False
        # Winner OR plateau touches hi/lo edge -> TRUE boundary beyond.
        # (Plateau-touch matters: winner is est-nearest among prog-ties,
        # but the tied run reaching the edge signals more room (entry 84).)
        # No early stop: local flukes beat current-best before TRUE-far is
        # reached; expand to limits and let global-best win (entry 84 needs
        # 4+ rounds to prevb).
        if (bb >= hi - 8 or phi >= hi - 8) and hi < n - 1:
            hi2 = min(n - 1, hi + RADII[i])
            if hi2 > hi:
                _scan_range(list(kcand), hi + 1, hi2)
                hi = hi2
                grown = True
        if (bb <= lo + 8 or plo <= lo + 8) and lo > prevb:
            lo2 = max(prevb, lo - RADII[i])
            if lo2 < lo:
                _scan_range(list(kcand), lo2, lo - 1)
                lo = lo2
                grown = True
        if not grown:
            break
    qual = [t for t in scored if t[1] >= lo] or scored
    best = sorted(qual, key=_key, reverse=True)[0]
    # tops for combo: key-diverse (per-key best, top-3 keys) + b-diverse
    # (top-2 prog overall). Hiding flukes crowd out TRUE keys under pure
    # prog ranking (entry 24); off-by-N needs b-diversity (entry 400).
    # <=5 per boundary -> <=625 combos (fails/suspects only).
    alltops.sort(reverse=True)
    perkey: dict[int, tuple] = {}
    for (prog, dens, b, kR, plo, phi, pn) in alltops:
        if kR not in perkey:
            perkey[kR] = (b, kR, prog, dens)
    bykey = sorted(perkey.values(), key=lambda t: (t[2], t[3]),
                   reverse=True)[:3]
    tops = list(bykey)
    seenb = {t[0] for t in tops}
    for (prog, dens, b, kR, plo, phi, pn) in alltops:
        if b not in seenb:
            seenb.add(b)
            tops.append((b, kR, prog, dens))
        if len(tops) >= 5:
            break
    return best, tops


def _eval_current(exp: bytes, n: int, bounds: list[int], i: int,
                  rest_base: list[int], keys: list[int], xtabs: list,
                  limit: int, fwlo: int, fwhi: int):
    """Score the CURRENT (b, kR) under given rest. Returns (prog, dens)."""
    b = bounds[i]
    kR = keys[i+1]
    dec = _build_decode(exp, n, bounds[:i], b, rest_base, keys, kR,
                        xtabs, xtabs[i+1], i)
    prog = marshal_progress(dec, limit)
    mass, z, score = content_score(dec[fwlo:fwhi])
    return prog, score / max(1, fwhi - fwlo)


def _combo_repair(exp: bytes, n: int, tops: dict[int, list],
                  keys: list[int], bounds: list[int]):
    """Try tops (b, kR) combos per boundary (<=625 full parses).

    Fixes joint-commitment failures (greedy's per-boundary argmax can combine
    into a non-parsing whole). Returns (keys, bounds, confs) or None.
    """
    import itertools
    per: list[list] = []
    for i in range(NSEGS - 1):
        t3 = tops.get(i) or [(bounds[i], keys[i+1], 0, 0.0)]
        per.append(t3[:5])
    best = None  # (garbage, -mass, keys, bounds)
    for combo in itertools.product(*per):
        if _expired():
            break
        bb = [c[0] for c in combo]
        if any(bb[j+1] <= bb[j] for j in range(len(bb) - 1)):
            continue
        kk = [keys[0]] + [c[1] for c in combo]
        dec = _build_full(exp, n, bb, kk, [_xtab(k) for k in kk])
        ok, pos, root, r = marshal_try(dec)
        if not ok:
            continue
        fn = b2s(root.get("filename", ""))
        mn = b2s(root.get("name", ""))
        if not _sane_filename(fn) or mn != "<module>":
            continue
        blob_blobs = set()
        for co in r.code_objects:
            for fld in ("code", "lnotab"):
                c = co.get(fld)
                if isinstance(c, bytes):
                    blob_blobs.add(c)
        garbage = 0
        for s in r.strings:
            if s in blob_blobs:
                continue
            garbage += sum(1 for b in s
                           if b not in _PRINT and not (0x80 <= b <= 0xFF))
        mass, _, _ = content_score(dec)
        edges = [0] + bb + [n]
        minseg = min(edges[j+1] - edges[j] for j in range(NSEGS))
        if minseg < max(8, n // 25):
            continue
        cand = (garbage, -mass, kk, bb)
        if best is None or cand < best:
            best = cand
    if best is None:
        return None
    _, _, kk, bb = best
    confs = [f"{b}-{b}:combo" for b in bb]
    return kk, bb, confs


def _decode_greedy(exp: bytes, force_expand: bool = False,
                  fix_keys: list | None = None,
                  fix_bounds: list | None = None):
    n = len(exp)
    _SAFETY["hits"] = 0  # fresh abort-budget per greedy attempt
    key_cands = estimate_keys(exp)
    keys = [c[0][0] for c in key_cands]
    if fix_keys:
        for j, fk in enumerate(fix_keys):
            if fk is not None:
                keys[j] = fk
    est = [(n * i) // NSEGS for i in range(1, NSEGS)]
    xtabs = [_xtab(k) for k in keys]
    bounds: list[int] = []
    confs: list[str] = []
    tops: dict[int, list] = {}
    manual = ((fix_keys and any(f is not None for f in fix_keys))
              or (fix_bounds and any(f is not None for f in fix_bounds)))
    # Round 1: forward greedy with len/5 rest.
    for i in range(NSEGS - 1):
        if _expired():
            return {"status": "fail", "method": "timeout-s%d" % i,
                    "keys": bytes(keys).hex(), "bounds": bounds + est[i:],
                    "progress": 0, "explen": n}
        lo = max((bounds[-1] + 1) if bounds else 1, est[i] - RADII[i])
        hi = min(n - 1, est[i] + RADII[i])
        if fix_bounds and fix_bounds[i] is not None:
            lo = hi = fix_bounds[i]
        if lo > hi:
            return {"status": "fail", "method": f"empty-scan-s{i}",
                    "keys": bytes(keys).hex(), "bounds": bounds + est[i:],
                    "progress": 0, "explen": n}
        limit = min(n, hi + 256)
        prefix_end = bounds[-1] if bounds else 0
        ext_hi = (est[i+1] + RADII[i+1]) if i + 1 < NSEGS - 1 else n
        if fix_keys and fix_keys[i+1] is not None:
            kcand = [fix_keys[i+1]]
        else:
            kcand = _key_candidates_for(exp, prefix_end, min(n, ext_hi),
                                        seed=keys[i+1])
        best, top3 = _solve_one(exp, n, bounds, i, lo, hi, est[i+1:],
                                keys, kcand, xtabs, est[i], limit,
                                force_expand)
        if best is None:
            return {"status": "fail", "method": f"no-candidate-s{i}",
                    "keys": bytes(keys).hex(), "bounds": bounds + est[i:],
                    "progress": 0, "explen": n}
        scoreF, prog, massF, zF, dens, _, bsel, ksel, plo, phi, pn = best
        bounds.append(bsel)
        confs.append(f"{plo}-{phi}:{pn}")
        tops[i] = top3
        if ksel != keys[i+1] and not (fix_keys and
                                     fix_keys[i+1] is not None):
            keys[i+1] = ksel
            xtabs[i+1] = _xtab(ksel)
    # Skip refinement if round 1 is already clean (tight + parses + sane).
    _final1 = _build_full(exp, n, bounds, keys, xtabs)
    _ok1, _, _root1, _ = marshal_try(_final1)
    _tight = True
    for _c in confs:
        try:
            _rng, _ = _c.split(":")
            _a, _b = _rng.split("-")
            if int(_b) - int(_a) > 12:
                _tight = False
        except ValueError:
            _tight = False
    _sane1 = (_ok1 and _root1 is not None
              and _sane_filename(b2s(_root1.get("filename", "")))
              and b2s(_root1.get("name", "")) == "<module>")
    # Rounds 2-3: Gauss-Seidel refine with live rest (strict improvement).
    for rnd in range(0 if (_ok1 and _tight and _sane1) else 2):
        changed = False
        for i in range(NSEGS - 1):
            if _expired():
                break
            prevb = bounds[i-1] + 1 if i > 0 else 1
            lo = max(prevb, est[i] - RADII[i])
            hi = min(n - 1, est[i] + RADII[i])
            if fix_bounds and fix_bounds[i] is not None:
                lo = hi = fix_bounds[i]
            if lo > hi:
                continue
            limit = min(n, hi + 256)
            rest_base = bounds[i+1:]
            cur = _eval_current(exp, n, bounds, i, rest_base, keys,
                                xtabs, limit, max(0, lo - 64),
                                min(n, hi + 64))
            ext_lo = bounds[i-1] if i > 0 else 0
            ext_hi = ((bounds[i+1] + RADII[i+1]) if i + 1 < NSEGS - 1
                      else n)
            if fix_keys and fix_keys[i+1] is not None:
                kcand = [fix_keys[i+1]]
            else:
                kcand = _key_candidates_for(exp, ext_lo, min(n, ext_hi),
                                            seed=keys[i+1])
            best, top3 = _solve_one(exp, n, bounds[:i], i, lo, hi, rest_base,
                                    keys, kcand, xtabs, est[i], limit,
                                    force_expand)
            if best is None:
                continue
            tops[i] = top3
            scoreF, prog, massF, zF, dens, _, bsel, ksel, plo, phi, pn = best
            if (prog, dens) > (cur[0], cur[1]):
                if not (fix_bounds and fix_bounds[i] is not None):
                    bounds[i] = bsel
                confs[i] = f"{plo}-{phi}:{pn}"
                if ksel != keys[i+1] and not (fix_keys and
                                             fix_keys[i+1] is not None):
                    keys[i+1] = ksel
                    xtabs[i+1] = _xtab(ksel)
                changed = True
        if _expired() or not changed:
            break
    bounds = sorted(bounds)
    final = _build_full(exp, n, bounds, keys, xtabs)
    ok, pos, root, r = marshal_try(final)
    combo_used = False
    if not ok:
        # Combo repair: top-3 per boundary (joint re-commit).
        combo = _combo_repair(exp, n, tops, keys, bounds)
        if combo is not None:
            keys, bounds, confs = combo
            combo_used = True
            final = _build_full(exp, n, bounds, keys,
                                [_xtab(k) for k in keys])
            ok, pos, root, r = marshal_try(final)
    if ok:
        blob_blobs = set()
        for co in r.code_objects:
            for fld in ("code", "lnotab"):
                c = co.get(fld)
                if isinstance(c, bytes):
                    blob_blobs.add(c)
        garbage = 0; total = 0
        for s in r.strings:
            if s in blob_blobs:
                continue
            total += len(s)
            garbage += sum(1 for b in s if b not in _PRINT and not (0x80 <= b <= 0xFF))
        fn = b2s(root.get("filename", ""))
        mn = b2s(root.get("name", ""))
        ratio = garbage / max(1, total)
        edges = [0] + bounds + [n]
        minseg = min(edges[j+1] - edges[j] for j in range(NSEGS))
        tiny = minseg < max(8, n // 25)
        sane = _sane_filename(fn) and mn == "<module>" and ratio < 0.5 and not tiny
        if not sane and not combo_used:
            combo2 = _combo_repair(exp, n, tops, keys, bounds)
            if combo2 is not None:
                keys, bounds, confs = combo2
                combo_used = True
                final = _build_full(exp, n, bounds, keys,
                                    [_xtab(k) for k in keys])
                ok, pos, root, r = marshal_try(final)
                if ok:
                    blob_blobs = set()
                    for co in r.code_objects:
                        for fld in ("code", "lnotab"):
                            c = co.get(fld)
                            if isinstance(c, bytes):
                                blob_blobs.add(c)
                    garbage = 0; total = 0
                    for s in r.strings:
                        if s in blob_blobs:
                            continue
                        total += len(s)
                        garbage += sum(1 for b in s
                                       if b not in _PRINT
                                       and not (0x80 <= b <= 0xFF))
                    fn = b2s(root.get("filename", ""))
                    mn = b2s(root.get("name", ""))
                    ratio = garbage / max(1, total)
                    edges = [0] + bounds + [n]
                    minseg = min(edges[j+1] - edges[j]
                                 for j in range(NSEGS))
                    tiny = minseg < max(8, n // 25)
                    sane = (_sane_filename(fn) and mn == "<module>"
                            and ratio < 0.5 and not tiny)
        flag = "+tinyseg" if tiny else ""
        return {"status": "ok" if sane else "suspect",
                "method": ("greedy-v7" + ("+X" if force_expand else "")
                           + ("+combo" if combo_used else "")
                           + ("+M" if manual else "") + flag),
                "keys": bytes(keys).hex(),
                "bounds": bounds, "bconf": ";".join(confs),
                "decoded": final, "root": root, "reader": r,
                "garbage": garbage, "strbytes": total,
                "filename_check": fn, "modname_check": mn}
    return {"status": "fail", "method": "greedy-v7-final",
            "keys": bytes(keys).hex(), "bounds": bounds,
            "bconf": ";".join(confs),
            "progress": pos, "explen": n}


def decode_entry_auto(exp: bytes, fix_keys=None, fix_bounds=None):
    _SAFETY["deadline"] = time.time() + 150  # per-entry wall budget
    _SAFETY["hits"] = 0
    res = _decode_greedy(exp, force_expand=False, fix_keys=fix_keys,
                         fix_bounds=fix_bounds)
    if res["status"] in ("ok",):
        return res
    # one retry with forced key expansion
    res2 = _decode_greedy(exp, force_expand=True, fix_keys=fix_keys,
                          fix_bounds=fix_bounds)
    if res2["status"] == "ok":
        return res2
    # prefer suspect-with-decode over fail for manual review? keep first fail info
    if res["status"] == "suspect" and res2["status"] == "fail":
        return res
    return res2

def _build_decode(exp, n, bounds, b, rest_base, keys, kR, xtabs, tabR, i):
    # decode: [0..bounds..) fixed keys; [prev,b) key i; [b,...) kR + clamped rest
    out = bytearray(n)
    edges = [0] + list(bounds) + [b]
    for s in range(i + 1):
        s_lo = edges[s]; s_hi = edges[s + 1]
        if s_hi > s_lo:
            out[s_lo:s_hi] = exp[s_lo:s_hi].translate(xtabs[s])
    rest_edges = [b] + _clamp_rest(rest_base, b, n) + [n]
    rk = [tabR] + [xtabs[j] for j in range(i + 2, NSEGS)]
    for s in range(len(rest_edges) - 1):
        s_lo = rest_edges[s]; s_hi = rest_edges[s + 1]
        if s_hi > s_lo:
            out[s_lo:s_hi] = exp[s_lo:s_hi].translate(rk[s])
    return bytes(out)

def _build_full(exp, n, bounds, keys, xtabs):
    out = bytearray(n)
    edges = [0] + list(bounds) + [n]
    for s in range(NSEGS):
        if edges[s + 1] > edges[s]:
            out[edges[s]:edges[s+1]] = exp[edges[s]:edges[s+1]].translate(xtabs[s])
    return bytes(out)

# ---------------------------------------------------------- info extraction
def b2s(v):
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8")
        except UnicodeDecodeError:
            return v.decode("latin-1")
    return v if isinstance(v, str) else str(v)

def collect_texts(value, out: list, limit=20000):
    if len(out) >= limit:
        return
    if isinstance(value, bytes):
        try:
            t = value.decode("utf-8")
        except UnicodeDecodeError:
            t = value.decode("latin-1")
        if t and all((ch.isprintable() or ch in "\r\n\t") for ch in t):
            out.append(t)
    elif isinstance(value, str):
        if value:
            out.append(value)
    elif isinstance(value, dict):
        if "code" in value and "filename" in value:
            # code object: skip descending into code blob here (handled via strings)
            for k in ("consts", "names", "varnames", "filename", "name"):
                collect_texts(value.get(k), out, limit)
            return
        for k, v in value.items():
            collect_texts(k, out, limit)
            collect_texts(v, out, limit)
    elif isinstance(value, (tuple, list)):
        for v in value:
            collect_texts(v, out, limit)

def entry_info(reader: MarshalReader, root) -> dict:
    names = [b2s(co.get("name")) for co in reader.code_objects]
    texts: list = []
    collect_texts(root, texts)
    return {"filename": b2s(root.get("filename", "")),
            "modname": b2s(root.get("name", "")),
            "code_count": len(reader.code_objects),
            "func_names": names,
            "strings": sorted(set(texts))}

# ------------------------------------------------------------------ workers
_ARCHIVE = None
def _init_worker(path):
    global _ARCHIVE
    with open(path, "rb") as f:
        _ARCHIVE = f.read()

def _decode_one(idx: int):
    t0 = time.time()
    try:
        e = extract_entry(_ARCHIVE, idx)
        res = decode_entry_auto(e["exp"])
        base = {"index": idx, "id": f"0x{e['id']:08x}", "f1": e["f1"],
                "clen": e["clen"], "explen": len(e["exp"]), "dt": round(time.time()-t0, 2),
                "status": res["status"], "method": res.get("method", ""),
                "keys": res.get("keys", ""),
                "bounds": ",".join(map(str, res.get("bounds", []))),
                "bconf": res.get("bconf", "")}
        if res["status"] in ("ok", "suspect"):
            info = entry_info(res["reader"], res["root"])
            base.update({"filename": info["filename"], "modname": info["modname"],
                         "code_count": info["code_count"],
                         "garbage": res.get("garbage", -1),
                         "strbytes": res.get("strbytes", -1)})
            return base, info, res
        base.update({"filename": "", "modname": "", "code_count": 0,
                     "progress": res.get("progress", 0)})
        return base, None, res
    except Exception as ex:
        import traceback
        return ({"index": idx, "status": f"error: {ex}", "filename": "",
                 "modname": "", "code_count": 0,
                 "trace": traceback.format_exc()[-500:]}, None, None)

# ---------------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description="FLS batch decoder (Task B)")
    ap.add_argument("--archive", default="data/script.fls")
    ap.add_argument("--catalog", default=None, help="write catalog CSV for all entries")
    ap.add_argument("--index", type=int, default=None, help="decode single entry")
    ap.add_argument("--all", action="store_true", help="decode all entries to --output")
    ap.add_argument("--output", default="out-fls", help="output dir for decoded data")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0, help="limit #entries (debug)")
    ap.add_argument("--resume", action="store_true", help="skip indexes already in output jsonl")
    ap.add_argument("--fix-keys", default=None,
                    help="lock keys, e.g. 'eb,,85,,' (5 comma-sep hex or empty)")
    ap.add_argument("--fix-bounds", default=None,
                    help="lock bounds, e.g. '1453,,,' (4 comma-sep ints or empty)")
    ap.add_argument("--indices", default=None,
                    help="comma-separated index list for batch retry")
    args = ap.parse_args()

    def _parse_fixes():
        fk = fb = None
        if args.fix_keys:
            fk = [int(x, 16) if x.strip() else None
                  for x in args.fix_keys.split(",")]
            fk += [None] * (NSEGS - len(fk))
        if args.fix_bounds:
            fb = [int(x) if x.strip() else None
                  for x in args.fix_bounds.split(",")]
            fb += [None] * (NSEGS - 1 - len(fb))
        return fk, fb

    if args.index is not None:
        with open(args.archive, "rb") as f:
            arch = f.read()
        e = extract_entry(arch, args.index)
        t0 = time.time()
        fk, fb = _parse_fixes()
        res = decode_entry_auto(e["exp"], fix_keys=fk, fix_bounds=fb)
        dt = time.time() - t0
        print(json.dumps({k: (v if k not in ("decoded", "root", "reader") else f"<len {len(v) if isinstance(v,(bytes,bytearray)) else '?'}>")
                          for k, v in res.items()}, indent=2))
        print(f"decode time: {dt:.2f}s")
        if res["status"] == "ok":
            info = entry_info(res["reader"], res["root"])
            print("filename:", info["filename"], "| code objects:", info["code_count"])
            print("funcs:", ", ".join(info["func_names"][:40]))
        outdir = Path(args.output); outdir.mkdir(parents=True, exist_ok=True)
        if res["status"] in ("ok", "suspect"):
            (outdir / f"entry{args.index}.marshal.bin").write_bytes(res["decoded"])
            info = entry_info(res["reader"], res["root"])
            (outdir / f"entry{args.index}.info.json").write_text(
                json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            (outdir / f"entry{args.index}.EXPANDED.bin").write_bytes(e["exp"])
            (outdir / f"entry{args.index}.fail.json").write_text(
                json.dumps({k: v for k, v in res.items()
                            if k not in ("decoded", "root", "reader")},
                           ensure_ascii=False, indent=2), encoding="utf-8")
        return 0

    indices = list(range(EXPECTED_COUNT))
    if args.indices:
        indices = [int(x) for x in args.indices.split(",") if x.strip()]
    if args.limit:
        indices = indices[:args.limit]
    outdir = Path(args.output); outdir.mkdir(parents=True, exist_ok=True)
    jl_path = outdir / "decode-results.jsonl"
    done = set()
    if args.resume and jl_path.exists():
        with open(jl_path, encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(int(json.loads(line)["index"]))
                except Exception:
                    pass
        print(f"resume: {len(done)} already done")
    indices = [i for i in indices if i not in done]

    import multiprocessing as mp
    ctx = mp.get_context("fork")
    pool = ctx.Pool(args.jobs, initializer=_init_worker, initargs=(args.archive,))
    results = []
    try:
        N = len(indices)
        for n, (base, info, res) in enumerate(pool.imap_unordered(_decode_one, indices, chunksize=4)):
            results.append((base, info, res))
            if (n + 1) % 25 == 0 or (n + 1) == N:
                ok = sum(1 for b, _, _ in results if b.get("status") == "ok")
                print(f"[{n+1}/{N}] ok={ok} fail={n+1-ok}", flush=True)
            with open(jl_path, "a", encoding="utf-8") as f:
                slim = dict(base)
                if info and args.all:
                    slim["func_names"] = info["func_names"][:200]
                f.write(json.dumps(slim, ensure_ascii=False) + "\n")
            if args.all and base.get("status") in ("ok", "suspect"):
                idx = base["index"]
                (outdir / f"entry{idx}.marshal.bin").write_bytes(res["decoded"])
                (outdir / f"entry{idx}.info.json").write_text(
                    json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        pool.close(); pool.join()

    if args.catalog:
        rows = []
        with open(jl_path, encoding="utf-8") as jf:
            for line in jf:
                rows.append(json.loads(line))
        rows.sort(key=lambda r: r["index"])
        with open(args.catalog, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["index", "id", "f1", "clen", "explen",
                                              "status", "method", "keys", "bounds",
                                              "bconf", "filename", "modname",
                                              "code_count", "garbage", "dt"])
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in
                            ["index", "id", "f1", "clen", "explen", "status",
                             "method", "keys", "bounds", "bconf", "filename",
                             "modname", "code_count", "garbage", "dt"]})
        print(f"catalog written: {args.catalog}")
    ok = sum(1 for b, _, _ in results if b.get("status") == "ok")
    print(f"DONE ok={ok}/{len(results)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
