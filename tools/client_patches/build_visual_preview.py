#!/usr/bin/env python3
"""Build the v3.1 candidate (shipped v3 failed startup), without source execution.

Requires the small frozen CPython-2.5 overlay plus its source hash manifest.
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


def homepage_hook(co):
    """Bounded, logged exception guard around BOTH import and caption setup.

    The original try-block footprint is 426..570. Preserve its relative handler
    target 552 and return at 571, but consume/log every Python exception instead
    of only IOError. The returned fragment contains no recovered instructions.
    """
    body = base.assemble((100, co['consts'].index(-1)), (100, co['consts'].index(None)),
                         (107, co['names'].index(b'register')), (125, co['varnames'].index(b'register')),
                         (124, co['varnames'].index(b'register')), (105, co['names'].index(b'GetData')),
                         (124, co['varnames'].index(b'self')), (131, 1), (1, None))
    handler = base.assemble((1, None),  # exception type; leave value and traceback
                            (100, co['consts'].index(b'login/mainpage.dlg')),
                            (71, None), (71, None), (72, None),  # prefix, exception value, newline
                            (1, None), (110, 8))  # traceback; resume original return
    base.require(len(handler) == 11, 'unexpected guard handler width')
    fragment = (base.assemble((121, 123)) + body
                + base.assemble((9, None)) * (119-len(body))
                + base.assemble((87, None), (110, 19))
                + handler + base.assemble((9, None)) * 8)
    base.require(len(fragment) == 145, 'unexpected startup hook width')
    return fragment


def registration_transition(co):
    """Construct the registration UI before discarding the existing homepage."""
    old = co['code']
    base.require(old[215:225] == base.assemble((116, co['names'].index(b'Show')),
                 (116, co['names'].index(b'False')), (131, 1), (1, None)), 'home hide fingerprint changed')
    base.require(old[225:238] == base.assemble((124, co['varnames'].index(b'register')),
                 (105, co['names'].index(b'Show')), (116, co['names'].index(b'True')),
                 (131, 1), (1, None)), 'registration show fingerprint changed')
    return old[225:238] + old[215:225]


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
            # Replace ONLY the optional tg.id block. Preserve all earlier home UI,
            # news behavior, version display, and the final return instruction.
            co = dict(base.objects(original))['CMainPage/__init__']
            base.require(len(co['code']) == 575, 'homepage constructor size changed')
            base.require((426, 121, 123) in base.normalized(co['code']), 'homepage hook fingerprint changed')
            body = homepage_hook(co)
            start = co['offset'] + 22 + 426
            end = co['offset'] + 22 + 571
            base.require(not any(start <= b < end for b in metadata[str(index)]['bounds']), 'hook crosses XOR boundary')
            patched = plain[:start] + body + plain[end:]
            after = dict(base.objects(base.tree(patched)))['CMainPage/__init__']
            base.valid_code(after, after['code'])
            transition = dict(base.objects(original))['CMainPage/OnMessage']
            at = transition['offset'] + 22 + 215
            replacement = registration_transition(transition)
            base.require(not any(at <= b < at + len(replacement) for b in metadata[str(index)]['bounds']),
                         'registration transition crosses XOR boundary')
            patched = patched[:at] + replacement + patched[at + len(replacement):]
            after = dict(base.objects(base.tree(patched)))['CMainPage/OnMessage']
            base.valid_code(after, after['code'])
            details['homepage'] = 'guarded registration caption hook; create target before hiding home'
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
    report = {'kind': 'registration_visual_preview_v3_1_candidate', 'source_sha256': base.sha(archive),
              'output_sha256': base.sha(result), 'output_bytes': len(result), 'changed_entries': [337, 4007],
              'untouched_entries_byte_identical': 5000, 'native_windows_client_tested': False,
              'source_executed_during_build': False, 'details': details, 'asset_sha256': manifest['assets'],
              'startup_changes': ['EXEC globals/locals use the actual None constant, not -1.',
                                  'Homepage guard covers import and caption call, logging exceptions and returning.',
                                  'Caption image is loaded and checked before removing the old caption.',
                                  'Registration/reject transitions create the target page before hiding the current one.'],
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
                        help='explicit opt-in: v3.1 has no native Windows acceptance yet')
    args = parser.parse_args()
    base.require(args.allow_unverified_candidate,
                 'explicit opt-in required: v3.1 is an unverified candidate; shipped v3 must not be reused')
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
