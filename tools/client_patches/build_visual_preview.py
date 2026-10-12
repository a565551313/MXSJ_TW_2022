#!/usr/bin/env python3
"""Build the v3.3 candidate (shipped v3 failed startup), without source execution.

Requires frozen CPython-2.5 UI/entry fragments plus their source hash manifest.
Homepage and register entries are both reserialized; only a click loads register.
The register entry is semantically reserialized to make room for a new compiled
UI overlay; the unused 2980 class is removed. Payload length/keys/bounds stay
fixed. This is a new packaging path: native Windows acceptance is still needed.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_registration_preview as base

HERE = Path(__file__).resolve().parent


class Writer:
    def __init__(self):
        self.interned = {}

    def string(self, value, intern=True):
        if intern and len(value) <= 512:
            if value in self.interned:
                return b'R' + struct.pack('<I', self.interned[value])
            self.interned[value] = len(self.interned)
            marker = b't'
        else:
            marker = b's'
        return marker + struct.pack('<I', len(value)) + value

    def write(self, value):
        if value is None:
            return b'N'
        if value is True:
            return b'T'
        if value is False:
            return b'F'
        if isinstance(value, int):
            return b'i' + struct.pack('<i', value)
        if isinstance(value, float):
            return b'g' + struct.pack('<d', value)
        if isinstance(value, bytes):
            return self.string(value)
        if isinstance(value, str):
            data = value.encode('utf-8')
            return b'u' + struct.pack('<I', len(data)) + data
        if isinstance(value, tuple):
            return b'(' + struct.pack('<I', len(value)) + b''.join(self.write(x) for x in value)
        if isinstance(value, dict) and 'code' in value:
            return (b'c' + struct.pack('<iiii', *(value[k] for k in ('argcount', 'nlocals', 'stacksize', 'flags')))
                    + self.string(value['code'], False)
                    + b''.join(self.write(value[k]) for k in ('consts', 'names', 'varnames', 'freevars', 'cellvars', 'filename', 'name'))
                    + struct.pack('<i', value['firstlineno']) + self.string(value['lnotab'], False))
        raise ValueError('unsupported authored marshal value: ' + type(value).__name__)


def semantic(value):
    if isinstance(value, dict):
        return {k: semantic(v) for k, v in value.items() if k != 'offset'}
    if isinstance(value, tuple):
        return tuple(semantic(v) for v in value)
    return value


def prepare_overlay(raw):
    """Translate only fresh CPython-2.5 output, never heuristic recovered source."""
    co = base.tree(raw)
    def convert(value):
        if isinstance(value, str):
            # Only authored traditional-Chinese body text uses the TW font path.
            # Simplified captions are supplied as PNG glyphs instead.
            return value.encode('cp950')
        if isinstance(value, tuple):
            return tuple(convert(x) for x in value)
        if isinstance(value, dict):
            result = dict(value)
            source = value['code']
            code = bytearray()
            at = 0
            while at < len(source):
                op = source[at]
                size = 3 if op >= 90 else 1
                arg = int.from_bytes(source[at+1:at+3], 'little') if size == 3 else None
                code.extend(base.assemble((op, arg)))
                at += size
            result['code'] = bytes(code)
            result['consts'] = convert(value['consts'])
            base.valid_code(result, result['code'])
            return result
        return value
    co = convert(co)
    co['name'] = b'_registration_visual_overlay'
    return co


def load_overlay():
    raw = (HERE / 'visual_assets/overlay.py25').read_bytes()
    manifest = json.loads((HERE / 'visual_assets/manifest.json').read_text())
    base.require(base.sha((HERE / 'registration_visual_overlay.py').read_bytes()) == manifest['source_sha256'], 'overlay source is stale')
    base.require(base.sha(raw) == manifest['compiled_sha256'], 'compiled overlay mismatch')
    for name, digest in manifest['assets'].items():
        base.require(base.sha((HERE / 'visual_assets' / name).read_bytes()) == digest, 'asset mismatch: ' + name)
    return prepare_overlay(raw), manifest


def overlay_invocation(root, index=41):
    """Never assume module constant zero is None (it is -1 in this archive)."""
    none_indices = [i for i, value in enumerate(root['consts']) if value is None]
    base.require(len(none_indices) == 1, 'module needs exactly one None constant')
    none_index = none_indices[0]
    base.require(isinstance(root['consts'][index], dict), 'overlay slot is not code')
    return base.assemble((100, index), (100, none_index), (100, none_index), (85, None))


def load_home_entry():
    manifest = json.loads((HERE / 'visual_assets/manifest.json').read_text())
    raw = (HERE / 'visual_assets/home_entry.py25').read_bytes()
    base.require(base.sha((HERE / 'home_registration_entry.py').read_bytes()) == manifest['home_source_sha256'],
                 'home entry source is stale')
    base.require(base.sha(raw) == manifest['home_compiled_sha256'], 'compiled home entry mismatch')
    root = prepare_overlay(raw)
    return {co['name']: co for co in root['consts'] if isinstance(co, dict)}


# CPython 2.5 table operands and jump semantics (before native-opcode mapping).
NAME_OPS = {90, 91, 95, 96, 97, 98, 101, 105, 107, 108, 109, 116}
LOCAL_OPS = {124, 125, 126}
REL_JUMPS = {93, 110, 111, 112, 120, 121, 122}
ABS_JUMPS = {113, 119}


def inline_fragment(target, start, end, authored):
    """Replace a whole control-flow region, rebasing jumps and operand tables.

    No incoming jump may enter the removed region's interior. Only owned
    fragments are inserted; all surviving instructions retain their semantics.
    The owned RETURN_VALUE exits the containing method (both callers want None).
    """
    base.require(not authored['freevars'] and not authored['cellvars'], 'fragment has closures')
    base.require(not target['freevars'] and not target['cellvars'], 'target has closures')
    base.require(not (target['flags'] & 12), 'target has variable arguments')
    base.require(0 <= start < end <= len(target['code']), 'invalid replacement region')
    old = target['code']
    boundaries = {at for at, _, _ in base.normalized(old)} | {len(old)}
    base.require(start in boundaries and end in boundaries, 'split instruction')
    pools = {name: list(target[name]) for name in ('consts', 'names', 'varnames')}
    maps = {}
    for name, pool in pools.items():
        maps[name] = []
        for value in authored[name]:
            found = next((i for i, v in enumerate(pool) if type(v) is type(value) and v == value), None)
            if found is None:
                found = len(pool)
                pool.append(value)
            maps[name].append(found)
    fragment = []
    for at, op, arg in base.normalized(authored['code']):
        if op == 100:
            arg = maps['consts'][arg]
        elif op in NAME_OPS:
            arg = maps['names'][arg]
        elif op in LOCAL_OPS:
            arg = maps['varnames'][arg]
        elif op in ABS_JUMPS:
            arg += start
        fragment.append((op, arg))
    inserted = base.assemble(*fragment)
    delta = len(inserted) - (end-start)

    def location(at):
        base.require(not start < at < end, 'incoming jump enters replaced region')
        return at + delta if at >= end else at

    result = bytearray()
    for at, op, arg in base.normalized(old):
        if at == start:
            result.extend(inserted)
        if start <= at < end:
            continue
        if op in ABS_JUMPS:
            arg = location(arg)
        elif op in REL_JUMPS:
            arg = location(at + 3 + arg) - location(at) - 3
        result.extend(base.assemble((op, arg)))
    target.update({name: tuple(pool) for name, pool in pools.items()})
    target['code'] = bytes(result)
    target['stacksize'] = max(target['stacksize'], authored['stacksize'])
    target['nlocals'] = len(target['varnames'])
    target['lnotab'] = b''  # old byte offsets would be misleading after relocation
    # Drop only unreferenced const/name/local slots from these two methods.
    # Keep arguments in their original order even if unused by a fragment.
    for name, ops in (('consts', {100}), ('names', NAME_OPS), ('varnames', LOCAL_OPS)):
        seq = base.normalized(target['code'])
        used = {arg for _, op, arg in seq if op in ops}
        if name == 'varnames':
            used.update(range(target['argcount']))
        indices = sorted(used)
        mapping = {old: new for new, old in enumerate(indices)}
        target[name] = tuple(target[name][i] for i in indices)
        target['code'] = base.assemble(*[(op, mapping[arg] if op in ops else arg) for _, op, arg in seq])
    target['nlocals'] = len(target['varnames'])
    base.valid_code(target, target['code'])
    return start, start + len(inserted)


def padded_payload(root, size):
    """Keep original payload length/XOR boundaries with a real final constant."""
    consts = root['consts']
    root['consts'] = consts + (b'',)
    padding = size - len(Writer().write(root))
    base.require(padding >= 0, 'authored code exceeds original payload budget')
    root['consts'] = consts + (b' ' * padding,)
    raw = Writer().write(root)
    base.require(len(raw) == size, 'payload size changed')
    base.require(semantic(root) == semantic(base.tree(raw)), 'marshal semantic roundtrip mismatch')
    return raw, padding


def build(archive, keys):
    baseline, prior_report = base.build(archive, keys, stage='form-validate')
    metadata = json.loads(keys)
    _, rows = base.entries(baseline)
    overlay, manifest = load_overlay()
    replacements = {}
    details = {}
    for index in (337, 4007):
        plain = base.xor_payload(zlib.decompress(rows[index][1]), metadata[str(index)])
        original = base.tree(plain)
        if index == 337:
            root = copy.deepcopy(original)
            methods = dict(base.objects(root))
            owned = load_home_entry()
            constructor = methods['CMainPage/__init__']
            message = methods['CMainPage/OnMessage']
            base.require(len(constructor['code']) == 575, 'homepage constructor size changed')
            base.require((426, 121, 123) in base.normalized(constructor['code']), 'homepage hook fingerprint changed')
            base.require((209, 107, message['names'].index(b'register')) in base.normalized(message['code']),
                         'registration click import fingerprint changed')
            caption_span = inline_fragment(constructor, 426, 575, owned[b'install_caption'])
            click_span = inline_fragment(message, 90, 263, owned[b'open_registration'])
            patched, padding = padded_payload(root, len(plain))
            # Nothing outside these two methods changes semantically (parents
            # contain the methods and the root gains a harmless padding constant).
            after_objects = dict(base.objects(base.tree(patched)))
            for path, co in base.objects(original):
                if path not in ('', 'CMainPage', 'CMainPage/__init__', 'CMainPage/OnMessage'):
                    base.require(semantic(co) == semantic(after_objects[path]), 'unrelated home function changed: ' + path)
            details['homepage'] = {'startup_imports_registration': False,
                'caption': 'independent native caption, no imports; missing PNG retains old text',
                'entry': 'msgid 2 only: import register, construct new agreement, then hide home',
                'caption_span': caption_span, 'click_span': click_span,
                'payload_bytes': len(patched), 'padding_bytes': padding,
                'serialization': 'new intern table; same total length and original XOR keys/bounds'}
        else:
            root = copy.deepcopy(original)
            base.require(root['consts'][41]['name'] == b'CRegPanel2_2980', 'obsolete class slot changed')
            base.require(root['code'][488:513] == base.assemble(
                (100, 40), (101, root['names'].index(b'combdialog')),
                (105, root['names'].index(b'CCombPanel')), (102, 1), (100, 41),
                (132, 0), (131, 0), (89, None), (90, root['names'].index(b'CRegPanel2_2980'))),
                'obsolete class construction changed')
            consts = list(root['consts'])
            consts[41] = overlay
            # Execute already-compiled CODE in the current register namespace.
            # There is no execfile, eval, network code loading, or native compiler.
            invoke = overlay_invocation(root)
            root['code'] = root['code'][:488] + invoke + base.assemble((9, None)) * (25-len(invoke)) + root['code'][513:]
            root['consts'] = tuple(consts + [b''])
            size = len(Writer().write(root))
            padding = len(plain) - size
            base.require(padding >= 0, 'overlay exceeds original encrypted payload budget')
            # A real final constant makes the marshal parser consume all bytes;
            # no undocumented trailing-garbage tolerance is required.
            root['consts'] = tuple(consts + [b' ' * padding])
            patched = Writer().write(root)
            # Empty padding may intern while a large one does not; both have a
            # five-byte header, so the overall size remains exactly pinned.
            base.require(len(patched) == len(plain), 'register payload size changed')
            decoded = base.tree(patched)
            base.require(semantic(root) == semantic(decoded), 'marshal semantic roundtrip mismatch')
            before_objects = dict(base.objects(original))
            after_objects = dict(base.objects(decoded))
            for path, co in before_objects.items():
                if path and not path.startswith('CRegPanel2_2980'):
                    base.require(semantic(co) == semantic(after_objects[path]), 'unrelated function changed: ' + path)
            for path, co in base.objects(overlay):
                base.valid_code(co, co['code'])
            base.valid_code(decoded, decoded['code'])
            details['register'] = {'removed_class': 'CRegPanel2_2980', 'overlay_source_sha256': manifest['source_sha256'],
                                   'payload_bytes': len(patched), 'padding_bytes': padding,
                                   'serialization': 'new intern table; same total length and original XOR keys/bounds'}
        encrypted = base.xor_payload(patched, metadata[str(index)])
        base.require(base.xor_payload(encrypted, metadata[str(index)]) == patched, 'XOR roundtrip failed')
        replacements[index] = zlib.compress(encrypted, 9)
    # Repack against ORIGINAL, not the already appended v2.2 baseline.
    result = base.repack(archive, replacements)
    source_rows = base.entries(archive)[1]
    output_rows = base.entries(result)[1]
    base.require([i for i, (a,b) in enumerate(zip(source_rows, output_rows)) if a != b] == [337, 4007], 'archive scope changed')
    report = {'kind': 'registration_visual_preview_v3_3_candidate', 'source_sha256': base.sha(archive),
              'output_sha256': base.sha(result), 'output_bytes': len(result), 'changed_entries': [337, 4007],
              'untouched_entries_byte_identical': 5000, 'native_windows_client_tested': False,
              'source_executed_during_build': False, 'details': details, 'asset_sha256': manifest['assets'],
              'control_fixes': ['CClickBox uses color/alpha=0, SetPos sets coordinates.',
                                'Complete new gold actions replace and disable old terms/login/back controls.',
                                'Caption Z=1; edit Z=2 above card, explicit dark caret linecolor and Z=1.',
                                'Native CEdit focus/Flash/Tab logic retained; no custom blink timer.'],
              'startup_changes': ['EXEC globals/locals use the actual None constant, not -1.',
                                  'Homepage caption is independent: no registration import during homepage initialization.',
                                  'Caption image is loaded and checked before removing the old caption.',
                                  'Click-only registration import/construction is guarded; targets are created before hiding current pages.'],
              'limits': ['New compiled overlay and marshal reserialization require Windows native validation.',
                         'Original selected-realm service dialog and login controller are not modified or instantiated.',
                         'Preview only: inherited v2.2 validation, no registration request or saved credentials.',
                         'Caption lookup requires exactly one text button for its message ID; failures are logged.',
                         '800x600 only; original template art remains. Simplified PNG captions, traditional preview notice.',
                         'Not a full-client network block; agreement text is a preview notice, not production legal terms.']}
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--allow-unverified-candidate', action='store_true',
                        help='explicit opt-in: v3.3 has no native Windows acceptance yet')
    args = parser.parse_args()
    base.require(args.allow_unverified_candidate,
                 'explicit opt-in required: v3.3 is an unverified candidate; shipped v3 must not be reused')
    out = args.output_dir.resolve()
    base.require(not out.is_relative_to(base.ROOT), 'write outside repository')
    base.require(not (out / 'data/script.fls').exists(), 'refusing overwrite')
    source = (base.ROOT / 'data/script.fls').read_bytes()
    result, report = build(source, (base.ROOT / 'tools/decompiler/script_fls_keys.json').read_bytes())
    (out / 'data').mkdir(parents=True, exist_ok=True)
    (out / 'data/script.fls').write_bytes(result)
    assets = out / 'photo/registration_preview_v3'
    assets.mkdir(parents=True, exist_ok=True)
    for path in (HERE / 'visual_assets').glob('*.png'):
        (assets / path.name).write_bytes(path.read_bytes())
    (out / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    base.require((base.ROOT / 'data/script.fls').read_bytes() == source, 'source changed')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
