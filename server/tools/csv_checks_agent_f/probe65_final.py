#!/usr/bin/env python3
"""Agent F probe 65 - entry 244 (newfurnituredata.py) FINAL verification.

Corrected segmentation candidate:
    bounds = [18282, 36511, 54797, 73114]
    keys   = [233,   11,   132,   105, 246]
(saved DB has bounds [18282, 34193, 54797, 73070], keys [233, 132, 132, 105, 246])

Checks, all read-only:
  1. marshal walk consumes the payload exactly
  2. review_client_data_boundaries.instructions() walks the module co_code
     with no EXTENDED_ARG / NOP error
  3. the literal evaluator (extended locally with LOAD_NAME for ``None`` only)
     rebuilds DATA, ORDER, TYPE2NAME, SITE, LAYER, DIDRANGE, SPE_HORSE_DATA
  4. every DATA name/desc string passes strict CP950
Nothing is written to server/game_data/ and no recovered code is executed.
"""
import sys, json, zlib, struct
from pathlib import Path
ROOT = Path('/home/user/MXSJ_TW_2022')
sys.path.insert(0, str(ROOT))
from tools.decompiler import batch_decompile as decoder
from tools.fls_batch_decoder import MarshalReader

keys = json.loads((ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes())
arch = (ROOT / 'data/script.fls').read_bytes()
idx_off = struct.unpack_from('<I', arch, 8)[0]


def payload(index):
    entry_id, a, b, c = struct.unpack_from('<IIII', arch, idx_off + 16 * index)
    size = ((a * entry_id + 0xDF25E) & 0xFFFFFFFF) ^ b
    pos = ((b * index * 0xF718FE + 0xD59D16C) & 0xFFFFFFFF) ^ c
    return zlib.decompress(arch[pos:pos + size])


ENTRY = 244
m = keys[str(ENTRY)]
exp = payload(ENTRY)
SAVED_B = list(m['bounds'])
SAVED_K = list(m['keys'])
CAND_B = [18282, 36511, 54797, 73114]
CAND_K = [233, 11, 132, 105, 246]


def build(B, K):
    edges = [0] + list(B) + [len(exp)]
    return b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))


def load(B, K):
    dec = build(B, K)
    tr = decoder.Py25MarshalTranspiler(dec, exp, K, list(B))
    tr.transpile_object()
    r = MarshalReader(bytes(tr.out)[8:])
    co = r.read()
    if r.pos != len(r.data):
        raise ValueError('marshal reader did not consume the full output')
    return co


sys.path.insert(0, str(ROOT / 'server/tools'))
from review_client_data_boundaries import instructions


def _eval(co, body):
    stack = []
    for at, op, arg in body:
        if op == 100:
            stack.append(co['consts'][arg])
        elif op == 101:
            nm = co['names'][arg]
            if nm == b'None':
                stack.append(None)
            else:
                raise ValueError('LOAD_NAME %r at %d' % (nm, at))
        elif op == 102:
            n = arg or 0
            items = stack[len(stack) - n:] if n else []
            if n:
                del stack[len(stack) - n:]
            stack.append(tuple(items))
        elif op == 103:
            n = arg or 0
            items = stack[len(stack) - n:] if n else []
            if n:
                del stack[len(stack) - n:]
            stack.append(items)
        elif op == 104:
            stack.append({})
        elif op == 4:
            stack.append(stack[-1])
        elif op == 2:
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif op == 60:
            key, tgt, val = stack.pop(), stack.pop(), stack.pop()
            tgt[key] = val
        elif op in (90, 97):
            pass
        else:
            raise ValueError('unsupported opcode %d at %d' % (op, at))
    return stack[-1]


def evaluate(co, ins, target):
    seg = []
    for at, op, arg in ins:
        seg.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == target.encode('ascii'):
                return _eval(co, seg[:-1] + [(at, 90, arg)])
            seg = []
    raise ValueError('no %s' % target)


def quality(key, a, b):
    reg = exp[a:b].translate(decoder.XTABS[key])
    i = 0; n = 0; um = 0; at = []
    while i < len(reg):
        op = reg[i]
        if op not in decoder.PY25_MAP:
            um += 1; at.append(a + i)
        i += 3 if op >= 0x5F else 1
        n += 1
    return n, um, at


print('=== saved vs candidate ===')
print('saved    bounds=%s keys=%s' % (SAVED_B, SAVED_K))
print('candidate bounds=%s keys=%s' % (CAND_B, CAND_K))
print()
print('=== unmapped-Duoyi-opcode audit of the module co_code [22, 47423) ===')
for label, B, K in (('saved', SAVED_B, SAVED_K), ('candidate', CAND_B, CAND_K)):
    tot = 0
    parts = []
    for i in range(5):
        lo = 0 if i == 0 else B[i - 1]
        hi = B[i] if i < 4 else 47423
        if hi <= lo:
            continue
        n, um, at = quality(K[i], lo, hi)
        tot += um
        parts.append('[%d,%d) k=%d: %d/%d unmapped %s' % (lo, hi, K[i], um, n, at[:4]))
    print('  %-9s total_unmapped=%d' % (label, tot))
    for p in parts:
        print('      %s' % p)
print()
print('=== end-to-end check ===')
for label, B, K in (('saved', SAVED_B, SAVED_K), ('candidate', CAND_B, CAND_K)):
    print('--- %s %s %s' % (label, B, K))
    try:
        co = load(B, K)
        ins = list(instructions(co))
        print('    instructions(): %d instructions, no error' % len(ins))
    except Exception as e:
        print('    instructions() FAILED: %s: %s' % (type(e).__name__, e))
        continue
    for name in ('DATA', 'ORDER', 'TYPE2NAME', 'SITE', 'LAYER', 'DIDRANGE', 'SPE_HORSE_DATA'):
        try:
            v = evaluate(co, ins, name)
            print('    %-15s -> %s len=%d' % (name, type(v).__name__, len(v)))
        except Exception as e:
            print('    %-15s -> FAIL %s: %s' % (name, type(e).__name__, e))
    try:
        v = evaluate(co, ins, 'DATA')
    except Exception:
        continue
    good = bad = 0
    for fid in sorted(v):
        rec = v[fid]
        for f in (b'name', b'desc'):
            s = rec.get(f)
            if isinstance(s, bytes) and s:
                try:
                    t = s.decode('cp950')
                    good += 1
                    if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t):
                        bad += 1
                except UnicodeDecodeError:
                    bad += 1
    print('    DATA name/desc strings: good=%d bad=%d' % (good, bad))
