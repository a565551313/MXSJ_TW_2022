#!/usr/bin/env python3
"""Agent F probe 53 - entry 244: full dump of DATA record 29760 + neighbours.

Read-only.
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
ks = m['keys']
BOUNDS = [18282, 36511, 54797, 73070]
KEYLIST = [233, 11, 132, 105, 246]
edges = [0] + BOUNDS + [len(exp)]
dec = b''.join(exp[edges[i]:edges[i + 1]].translate(decoder.XTABS[KEYLIST[i]]) for i in range(5))

needle = bytes.fromhex(
    '3a4a2732295f357e3ede5dfe5dfe5bf85bf83b38293e2ce525e32a445c672ef03bdf373c35252'
    'dd729312dd2b773b74ec4ad2372a169c3feabaca16aae78b07cb8cbb9a2a147b4bac65bb4d3aa'
    'ab2372a169aaabab7eb5a5afc5a16a312372a169bb73a740bbdda844a16a3730afc5a5a9a64ba4a7b34e')
P = dec.find(needle)
print('string at dec %d..%d (len %d), B3=%d' % (P, P + len(needle), len(needle), BOUNDS[2]))

print()
print('--- boundary experiment: decode [73070, X) with key 105, [X, 73189) with key 246 ---')
for X in range(P, P + len(needle) + 1, 1):
    a = dec[P:X].translate(decoder.XTABS[105])
    b = dec[X:P + len(needle)].translate(decoder.XTABS[246])
    try:
        t = (a + b).decode('cp950')
        print('   X=%d OK -> %r' % (X, t))
    except UnicodeDecodeError:
        pass

print()
print('--- same, key 105 for [X, end) and 246 for [P, X) ---')
for X in range(P, P + len(needle) + 1):
    a = dec[P:X].translate(decoder.XTABS[246])
    b = dec[X:P + len(needle)].translate(decoder.XTABS[105])
    try:
        t = (a + b).decode('cp950')
        print('   X=%d OK -> %r' % (X, t))
    except UnicodeDecodeError:
        pass

print()
print('--- all 256 keys on the whole string ---')
for k in range(256):
    t = dec[P:P + len(needle)].translate(decoder.XTABS[k])
    try:
        t.decode('cp950')
        print('   key %d decodes cleanly' % k)
    except UnicodeDecodeError:
        pass

print()
print('--- per-byte analysis: which byte offsets fail ---')
try:
    needle.decode('cp950')
except UnicodeDecodeError as e:
    print('first CP950 failure at string offset %d (byte 0x%02x)' % (e.start, needle[e.start]))

print()
print('--- record 29760 and neighbours (from the corrected decode) ---')
sys.path.insert(0, str(ROOT / 'server/tools'))
from review_client_data_boundaries import instructions
tr = decoder.Py25MarshalTranspiler(dec, exp, KEYLIST, BOUNDS)
tr.transpile_object()
r = MarshalReader(bytes(tr.out)[8:]); co = r.read()


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


seg = []
DATA = None
for at, op, arg in instructions(co):
    seg.append((at, op, arg))
    if op in (90, 97):
        if co['names'][arg] == b'DATA':
            DATA = _eval(seg[:-1] + [(at, 90, arg)])
            break
        seg = []

for fid in (29758, 29759, 29760, 29761, 29762):
    rec = DATA.get(fid)
    print('  %s -> %s' % (fid, 'MISSING' if rec is None else ''))
    if rec:
        for k in sorted(rec):
            v = rec[k]
            if isinstance(v, bytes):
                try:
                    print('     %-12s %r' % (k.decode(), v.decode('cp950')))
                except UnicodeDecodeError:
                    print('     %-12s !!CP950-FAIL!! %s' % (k.decode(), v.hex()))
            else:
                print('     %-12s %r' % (k.decode(), v))
