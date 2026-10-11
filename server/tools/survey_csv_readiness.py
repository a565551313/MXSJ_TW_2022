#!/usr/bin/env python3
"""Selected-table CSV survey. Read-only; no game script execution or CSV release.

All 'screen passed' counts refer to this finite set of checks, not correctness
against the native loader. Existing heuristic boundaries are used unchanged.
"""
from __future__ import annotations
import collections
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_client_data_boundaries import Review, instructions, evaluate_literals, readable

TARGETS = {
    17: ['DATA'],
    1945: ['DATA', 'SHAPETABLE', 'ITEMDATABYTYPE', 'EQUIPCONDITION', 'MULTISHAPETABLE', 'FABAOEXPLAIN'],
    2027: ['DATA', 'SHAPE2ICON'], 1115: ['DATA'], 3205: ['DATA'],
    2242: ['SKILLIDLST'], 1698: ['DATA'], 960: ['DATA'],
    3791: ['DATA', 'CHILD_DATA'], 2954: ['DATA'], 1761: ['DATA'],
    400: ['DATA'], 1301: ['DATA', 'MAP_ASCRIPTION'],
    2601: ['DATA'], 2804: ['DATA'], 3724: ['DATA'], 1799: ['DATA'],
    2409: ['DATA'], 1381: ['DATA'], 2455: ['DATA'], 2338: ['DATA'],
    246: ['GEM2EQUIP'], 293: ['DATA'], 3075: ['DATA'], 2566: ['DATA'],
    1919: ['CHANGESHAPE_PREVIEWDATA'], 244: ['TYPE2NAME', 'ORDER', 'DATA'],
    3515: ['ROLEDCT', 'LUIPAIDCT', 'SEXLP2SHAPE'], 3526: ['DATA'],
    454: ['DATA'], 333: ['DATA', 'ICONTABLE'],
    1535: ['ZhaoshiData', 'BuffData', 'SealData'], 4924: ['DATA'],
}


def extract(co, name):
    """Also recognize literal STORE_GLOBAL assignments; never execute globals."""
    segment = []
    for at, op, arg in instructions(co):
        segment.append((at, op, arg))
        if op in (90, 97):
            if co['names'][arg] == name.encode('ascii'):
                return evaluate_literals(co, segment[:-1] + [(at, 90, arg)])
            segment = []
    raise ValueError('no supported literal assignment found for ' + name)


def inspect_text(value, path='row'):
    errors = []
    if isinstance(value, bytes):
        try:
            decoded = value.decode('cp950')
        except UnicodeDecodeError:
            return [{'kind': 'encoding', 'path': path, 'bytes_hex': value.hex()}]
        if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in decoded):
            errors.append({'kind': 'control_character', 'path': path, 'bytes_hex': value.hex()})
    elif isinstance(value, str):
        if any((ord(c) < 32 and c not in '\t\n\r') or ord(c) == 127 for c in value):
            errors.append({'kind': 'control_character', 'path': path, 'text': value})
    elif isinstance(value, (list, tuple)):
        for i, child in enumerate(value):
            errors += inspect_text(child, f'{path}[{i}]')
    elif isinstance(value, dict):
        for key, child in value.items():
            errors += inspect_text(key, f'{path}.key({key!r})')
            errors += inspect_text(child, f'{path}[{key!r}]')
    return errors


def schema_ok(entry, name, key, value):
    """Narrow observed shapes, not invented server-side schemas."""
    integer = lambda x: type(x) is int
    string = lambda x: type(x) is bytes
    fields = lambda spec: (type(value) is dict and set(value) == set(spec)
                           and all(check(value[k]) for k, check in spec.items()))
    ints = lambda x: type(x) is list and all(integer(v) for v in x)
    if entry in (17, 1945) and name == 'DATA':
        return integer(key) and type(value) is tuple and len(value) == (3 if entry == 17 else 2) and all(string(v) for v in value)
    if entry == 1115 or (entry in (3791, 1698) and name in ('DATA', 'CHILD_DATA')):
        return integer(key) and string(value)
    if entry == 1945 and name in ('SHAPETABLE', 'ITEMDATABYTYPE'):
        return integer(key) and integer(value)
    if entry == 1945 and name == 'EQUIPCONDITION':
        return integer(key) and type(value) is list and len(value) == 2 and all(string(v) for v in value)
    if entry == 2027 and name == 'DATA':
        required = {b'name', b'liupai', b'attack_type', b'carry_grade', b'maySkillLst', b'maxskillnum', b'address'}
        return (integer(key) and type(value) is dict and required <= set(value) <= required | {b'mustSkillName'}
                and all(string(value[k]) for k in (b'name', b'liupai', b'attack_type', b'address'))
                and all(integer(value[k]) for k in (b'carry_grade', b'maxskillnum'))
                and type(value[b'maySkillLst']) is tuple and all(string(v) for v in value[b'maySkillLst'])
                and (b'mustSkillName' not in value or string(value[b'mustSkillName'])))
    if entry == 3515 and name == 'ROLEDCT':
        return integer(key) and fields({b'name': string, b'sex': integer, b'lpList': ints})
    if entry == 3515 and name == 'SEXLP2SHAPE':
        return type(key) is tuple and len(key) == 2 and all(integer(v) for v in key) and integer(value)
    if entry == 1301 and name == 'DATA':
        return integer(key) and fields({b'name': string, b'w': lambda x: integer(x) and x > 0, b'h': lambda x: integer(x) and x > 0})
    if entry == 400:
        return integer(key) and type(value) is tuple and len(value) == 4 and string(value[0]) and all(integer(v) for v in value[1:])
    if entry == 3724:
        return integer(key) and type(value) is tuple and len(value) == 2 and integer(value[0]) and string(value[1])
    if entry == 2455:
        return integer(key) and fields({b'name': string, b'desc': string, b'lv': integer, b'cost': integer})
    if entry == 960:
        return integer(key) and fields({b'iNeedServerGrade': integer, b'iRelatedList': ints, b'iSort': integer})
    if entry == 2409:
        return integer(key) and fields({b'discount': lambda x: x is None or string(x), b'itemid': integer, b'name': string, b'num': integer, b'price': integer, b'type': integer})
    if entry == 2954:
        names = [n.encode('cp950') for s in ['法力', '防禦', '攻擊', '速度', '體力'] for n in [s+'資質', s+'資質最大值']]
        return integer(key) and fields({n: integer for n in names})
    if entry == 246:
        return integer(key) and fields({b'Desc': integer, b'EquipPos': ints, b'Name': string})
    return None  # No per-field schema supplied; don't claim it was validated.


def survey():
    review = Review()
    result = {'status': 'selected_literal_tables_only_not_production_approval',
              'source_sha256': hashlib.sha256(review.archive).hexdigest(),
              'keys_sha256': hashlib.sha256(review.key_bytes).hexdigest(),
              'entries_selected': len(TARGETS), 'tables': [], 'cross_checks': {},
              'limitations': [
                  'No candidate boundary fixes applied; uses existing heuristic transpiler.',
                  'No native loader comparison; valid text/numbers can still be wrong.',
                  'Only selected literal assignments, not final runtime values after mutations.',
                  'Schema validation exists only for explicitly implemented table shapes.',
                  'Cross-table conflicts require review; neither source is assumed authoritative.',
                  'No CSV data or production configuration is written.',
              ]}
    cache, summaries = {}, {}
    for entry, names in TARGETS.items():
        try:
            co = review.load(entry)
            load_error = None
        except Exception as exc:
            load_error = f'{type(exc).__name__}: {exc}'
        for name in names:
            row = {'entry_index': entry, 'table': name, 'issues': []}
            summaries[entry, name] = row
            result['tables'].append(row)
            try:
                if load_error:
                    raise ValueError(load_error)
                row['filename'] = readable(co['filename'])
                data = extract(co, name)
                if type(data) not in (dict, list, tuple):
                    raise ValueError('not a table')
                cache[entry, name] = data
                row.update(status='literal_assignment_recovered', count=len(data),
                           schema_checked=False, flagged_keys=[])
                pairs = list(data.items()) if isinstance(data, dict) else list(enumerate(data))
                row['value_types'] = dict(collections.Counter(type(v).__name__ for _, v in pairs))
                row['sample'] = [{'key': readable(k), 'value': readable(v)} for k, v in pairs[:1]]
                for k, v in pairs:
                    errors = inspect_text(k, 'key') + inspect_text(v)
                    valid = schema_ok(entry, name, k, v)
                    if valid is not None:
                        row['schema_checked'] = True
                    if valid is False:
                        errors.append({'kind': 'schema', 'path': 'row'})
                    for error in errors:
                        row['issues'].append({'key': readable(k), **error})
            except Exception as exc:
                row.update(status='not_recovered_by_this_reader', error=f'{type(exc).__name__}: {exc}')

    def note(entry, table, key, kind, **details):
        summaries[entry, table]['issues'].append({'key': readable(key), 'kind': kind, **details})
    items, pets = cache[1945, 'DATA'], cache[2027, 'DATA']
    aptitude = cache[2954, 'DATA']
    for key, data in aptitude.items():
        for field, value in data.items():
            maximum = field + '最大值'.encode('cp950')
            if maximum in data and type(value) is int and type(data[maximum]) is int and value > data[maximum]:
                note(2954, 'DATA', key, 'value_exceeds_named_maximum', field=readable(field), value=value, maximum=data[maximum])
    result['cross_checks']['aptitude_pet_ids'] = {
        'aptitude_without_pet': sorted(set(aptitude)-set(pets)),
        'pets_without_aptitude': sorted(set(pets)-set(aptitude))}
    for entry, table, field in [(17, 'DATA', 0), (2455, 'DATA', b'name'), (246, 'GEM2EQUIP', b'Name'), (3791, 'CHILD_DATA', None)]:
        for key, value in cache[entry, table].items():
            name = value if field is None else value[field]
            if key not in items:
                note(entry, table, key, 'not_in_item_catalog')
            elif name != items[key][0]:
                note(entry, table, key, 'name_difference', value=readable(name), item_name=readable(items[key][0]))
    for key, value in cache[2409, 'DATA'].items():
        if value[b'itemid'] not in items:
            note(2409, 'DATA', key, 'item_reference_not_in_catalog', value=readable(value[b'itemid']))
    scenes, maps = cache[400, 'DATA'], cache[1301, 'DATA']
    for key, value in scenes.items():
        if key not in maps:
            note(400, 'DATA', key, 'not_in_map_catalog')
        elif value[0] != maps[key][b'name']:
            note(400, 'DATA', key, 'map_name_difference')
    result['cross_checks']['item_images'] = {
        'image_mapping_without_item': len(set(cache[1945, 'SHAPETABLE'])-set(items)),
        'items_without_explicit_mapping': len(set(items)-set(cache[1945, 'SHAPETABLE'])),
        'note': 'Client Shape2Image falls back to shape; missing explicit mapping is not automatically an error.'}
    result['cross_checks']['item_type_keys_equal_item_keys'] = set(cache[1945, 'ITEMDATABYTYPE']) == set(items)
    roles = cache[3515, 'ROLEDCT']; schools = cache[3515, 'LUIPAIDCT']
    result['cross_checks']['children_unresolved_school_refs'] = [
        [key, skill] for key, value in roles.items() for skill in value[b'lpList'] if skill not in schools]
    result['cross_checks']['children_unresolved_shape_refs'] = [
        readable(key) for key, value in cache[3515, 'SEXLP2SHAPE'].items() if value not in roles or key[1] not in schools]
    note(2242, 'SKILLIDLST', 16, 'previously_flagged_boundary_candidate', value=cache[2242, 'SKILLIDLST'][16], candidate=416, approved=False)
    for row in result['tables']:
        if 'count' in row:
            keys = {json.dumps(issue['key'], ensure_ascii=False) for issue in row['issues']}
            row['flagged_keys'] = [json.loads(k) for k in sorted(keys)]
            row['flagged_row_count'] = len(keys)
            row['not_flagged_by_these_checks'] = row['count']-len(keys)
    result['tables_requested'] = len(result['tables'])
    result['tables_recovered'] = sum('count' in row for row in result['tables'])
    return result


if __name__ == '__main__':
    print(json.dumps(survey(), ensure_ascii=False, indent=2))
