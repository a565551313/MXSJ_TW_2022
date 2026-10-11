#!/usr/bin/env python3
"""Agent F probe 66 - entry 244: co_code-only unmapped-opcode statistics and a
full dump of the recovered module-level tables.  Read-only; output goes to
stdout only."""
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


exp = payload(244)
SAVED_B = [18282, 34193, 54797, 73070]
SAVED_K = [233, 132, 132, 105, 246]
CAND_B = [18282, 36511, 54797, 73114]
CAND_K = [233, 11, 132, 105, 246]


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


print('=== module co_code only: decoded payload [22, 47423) ===')
for label, B, K in (('saved', SAVED_B, SAVED_K), ('candidate', CAND_B, CAND_K)):
    cuts = [22, 18282] + [b for b in B if 22 < b < 47423] + [47423]
    tot = 0
    print('  %s' % label)
    for i in range(len(cuts) - 1):
        lo, hi = cuts[i], cuts[i + 1]
        ki = 0
        for b in B:
            if lo >= b:
                ki += 1
        n, um, at = quality(K[ki], lo, hi)
        tot += um
        print('     [%6d,%6d) key=%3d : %4d unmapped / %5d instructions  %s'
              % (lo, hi, K[ki], um, n, at[:5]))
    print('     TOTAL unmapped = %d' % tot)

print()
print('=== full dump under the candidate segmentation ===')


def build(B, K):
    edges = [0] + list(B) + [len(exp)]
    return b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[K[i]]) for i in range(5))


dec = build(CAND_B, CAND_K)
tr = decoder.Py25MarshalTranspiler(dec, exp, CAND_K, CAND_B)
tr.transpile_object()
r = MarshalReader(bytes(tr.out)[8:]); co = r.read()
sys.path.insert(0, str(ROOT / 'server/tools'))
from review_client_data_boundaries import instructions


def _eval(body):
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
            n = arg or 0; items = stack[len(stack)-n:] if n else []
            if n: del stack[len(stack)-n:]
            stack.append(tuple(items))
        elif op == 103:
            n = arg or 0; items = stack[len(stack)-n:] if n else []
            if n: del stack[len(stack)-n:]
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


ins = list(instructions(co))
stores = [(at, op, arg, co['names'][arg]) for at, op, arg in ins if op in (90, 97)]
print('module-level stores (co_code offset, name):')
for at, op, arg, nm in stores:
    if at > 1000:
        print('   %7d  %s' % (at, nm.decode()))


def ev(name):
    seg = []
    for at, op, arg in ins:
        seg.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == name.encode('ascii'):
                return _eval(seg[:-1] + [(at, 90, arg)])
            seg = []
    raise ValueError(name)


def d(x):
    if isinstance(x, bytes):
        try:
            return x.decode('cp950')
        except UnicodeDecodeError:
            return '!!CP950-FAIL!!' + x.hex()
    return x


print()
print('TYPE2NAME:')
for k in sorted(ev('TYPE2NAME')):
    print('   %r -> %r' % (d(k), d(ev('TYPE2NAME')[k])))
print()
print('DIDRANGE:')
for k in sorted(ev('DIDRANGE')):
    print('   %r -> %r' % (d(k), d(ev('DIDRANGE')[k])))
print()
print('LAYER:')
for k in sorted(ev('LAYER')):
    print('   %r' % (ev('LAYER')[k],))
print()
print('SITE:')
for k in sorted(ev('SITE')):
    print('   %r' % (ev('SITE')[k],))
print()
print('ORDER (first 20 of %d): %s' % (len(ev('ORDER')), ev('ORDER')[:20]))
print()
print('SPE_HORSE_DATA (first 5 of %d): %s' % (len(ev('SPE_HORSE_DATA')),
                                              sorted(ev('SPE_HORSE_DATA').items())[:5]))
print()
DATA = ev('DATA')
print('DATA: %d records' % len(DATA))
for fid in sorted(DATA):
    rec = DATA[fid]
    print('%d | %s | type=%s subtype=%s lv=%s cost=%s base_cost=%s | %s'
          % (fid, d(rec.get(b'name')), rec.get(b'type'), rec.get(b'subtype'),
             rec.get(b'lv'), rec.get(b'cost'), rec.get(b'base_cost'), d(rec.get(b'desc'))))
