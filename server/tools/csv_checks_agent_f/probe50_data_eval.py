#!/usr/bin/env python3
"""Agent F probe 50 - entry 244 (newfurnituredata.py).

Local, read-only analysis.  Does NOT write any game data, does NOT import or
execute the recovered script.  It only re-implements, in this probe, the same
literal-evaluation algorithm that
``server/tools/review_client_data_boundaries.py::evaluate_literals`` uses, with
one extra opcode (LOAD_NAME) allowed *only* when the name is ``None``.

Purpose: prove that the module-level table ``DATA`` for entry 244 is a
dict-of-dicts built by ``BUILD_MAP`` + ``DUP_TOP`` + ``LOAD_NAME``/``LOAD_CONST``
+ ``ROT_TWO`` + ``STORE_SUBSCR``, and that the reader failure
``unsupported opcode 101 at 2831`` is caused by the evaluator's allow-list
missing LOAD_NAME, NOT by corrupt bytes.
"""
import sys, json, zlib, struct, traceback
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
ks = m['keys']


def run(BOUNDS, KEYLIST):
    edges = [0] + list(BOUNDS) + [len(exp)]
    dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[KEYLIST[i]])
                   for i in range(5))
    tr = decoder.Py25MarshalTranspiler(dec, exp, KEYLIST, list(BOUNDS))
    tr.transpile_object()
    r = MarshalReader(bytes(tr.out)[8:])
    co = r.read()
    if r.pos != len(r.data):
        raise ValueError('reader did not consume output')
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
            pass  # value stays on the stack; caller returns stack[-1]
        else:
            raise ValueError('unsupported opcode %d at %d' % (op, at))
    return stack[-1]


def evaluate(co, ins, target_name):
    seg = []
    for at, op, arg in ins:
        seg.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == target_name.encode('ascii'):
                return _eval(co, seg[:-1] + [(at, 90, arg)])
            seg = []
    raise ValueError('no %s' % target_name)


for label, B, K in [
    ('SAVED', [18282, 34193, 54797, 73070], [233, 132, 132, 105, 246]),
    ('FIXED key1=11', [18282, 36511, 54797, 73070], [233, 11, 132, 105, 246]),
    ('FIXED key1=73', [18282, 36511, 54797, 73070], [233, 73, 132, 105, 246]),
]:
    print('===', label, B, K)
    try:
        co = run(B, K)
        ins = list(instructions(co))
        v = evaluate(co, ins, 'DATA')
        print('   DATA type=%s records=%d' % (type(v).__name__, len(v)))
        if isinstance(v, dict):
            ids = list(v)
            fields = set()
            for rec in v.values():
                if isinstance(rec, dict):
                    fields |= set(rec)
            print('   field set: %s' % sorted(x.decode('ascii') for x in fields))
            print('   first 5 ids: %s' % ids[:5])
            print('   last 5 ids: %s' % ids[-5:])
            bad = good = 0
            for rec in v.values():
                d = rec.get(b'desc')
                if isinstance(d, bytes) and d:
                    try:
                        t = d.decode('cp950')
                        good += 1
                        if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t):
                            bad += 1
                    except UnicodeDecodeError:
                        bad += 1
            print('   desc strings: good=%d bad=%d' % (good, bad))
            r0 = v[ids[0]]
            print('   record[%d] keys=%s' % (ids[0], sorted(k.decode('ascii') for k in r0)))
            print('   record[%d] name=%r desc=%r' % (ids[0], r0.get(b'name'), r0.get(b'desc')))
    except Exception as e:
        print('   FAIL', type(e).__name__, e)
        traceback.print_exc()
