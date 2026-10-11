#!/usr/bin/env python3
"""Agent F probe 51 - entry 244 (newfurnituredata.py) final verification.

Read-only.  Re-derives the module-level table DATA for entry 244 under a
corrected XOR segmentation and checks every recovered name/description string
against strict CP950.  Nothing is written to server/game_data/.
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
            pass
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


def quality(key, a, b):
    reg = exp[a:b].translate(decoder.XTABS[key])
    i = 0; n = 0; um = 0; um_at = []
    while i < len(reg):
        op = reg[i]
        step = 3 if op >= 0x5F else 1
        if op not in decoder.PY25_MAP:
            um += 1; um_at.append(a + i)
        i += step; n += 1
    return n, um, um_at


print('=== B1 candidate comparison (key1 fixed to 11, rest saved) ===')
for B1 in (34193, 36494, 36508, 36511, 36514, 36517):
    B = [18282, B1, 54797, 73070]
    K = [233, 11, 132, 105, 246]
    try:
        co = run(B, K)
        ins = list(instructions(co))
        v = evaluate(co, ins, 'DATA')
        o = evaluate(co, ins, 'ORDER')
        good = bad = 0; badrows = []
        for fid, rec in v.items():
            for f in (b'name', b'desc'):
                s = rec.get(f)
                if isinstance(s, bytes) and s:
                    try:
                        t = s.decode('cp950')
                        good += 1
                        if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in t):
                            bad += 1; badrows.append((fid, f, s))
                    except UnicodeDecodeError:
                        bad += 1; badrows.append((fid, f, s))
        print('  B1=%-6d DATA=%-4d ORDER=%-4d strings good=%d bad=%d' % (B1, len(v), len(o), good, bad))
        if bad:
            for fid, f, s in badrows:
                print('      BAD %s[%d][%r] hex=%s' % ('name' if f == b'name' else 'desc', fid, f, s.hex()))
    except Exception as e:
        print('  B1=%-6d FAIL %s: %s' % (B1, type(e).__name__, e))

print()
print('=== unmapped-opcode locations for the chosen split ===')
n, um, at = quality(11, 18282, 36511)
print('  [18282,36511) key 11 : %d instr, %d unmapped at dec offsets %s' % (n, um, at))
n, um, at = quality(132, 36511, 47423)
print('  [36511,47423) key 132: %d instr, %d unmapped at dec offsets %s' % (n, um, at))
n, um, at = quality(132, 34193, 47423)
print('  [34193,47423) key 132: %d instr, %d unmapped (saved-bound comparison)' % (n, um))
n, um, at = quality(132, 18282, 34193)
print('  [18282,34193) key 132: %d instr, %d unmapped (saved key1)' % (n, um))

print()
print('=== full dump of DATA under the corrected split ===')
co = run([18282, 36511, 54797, 73070], [233, 11, 132, 105, 246])
ins = list(instructions(co))
v = evaluate(co, ins, 'DATA')
for fid in sorted(v):
    rec = v[fid]
    def d(x):
        if isinstance(x, bytes):
            try:
                return x.decode('cp950')
            except UnicodeDecodeError:
                return '!!CP950-FAIL!! ' + x.hex()
        return x
    print('%d | name=%s | type=%s | lv=%s | cost=%s | base_cost=%s | desc=%s' % (
        fid, d(rec.get(b'name')), rec.get(b'type'), rec.get(b'lv'), rec.get(b'cost'),
        rec.get(b'base_cost'), d(rec.get(b'desc'))))
