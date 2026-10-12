#!/usr/bin/env python3
"""Deterministic batch-001 review export; never a production config loader.

No recovered scripts or formula strings are executed. Candidate parameters live
in a separate profile, not the historical key database. Build everything and
validate before writing. UTF-8, quoted CSV; type contracts are in manifest.json.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_client_data_boundaries import Archive
from review_client_data_boundaries import extract_table_report
from survey_csv_readiness import extract, inspect_text, schema_ok
import map_npc_reproduction as maps

PROFILE = ROOT / 'server/docs/csv_checks/batch_001_profiles.json'
DEFAULT_OUT = ROOT / 'server/docs/csv_checks/batch_001'
STATUS = 'review_candidate_not_native_verified'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                       allow_nan=False) + '\n').encode('utf-8')


def lossless(value):
    """Typed JSON for evidence: preserve byte strings, tuple/list and dictionary keys."""
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, tuple):
        return {'tuple': [lossless(v) for v in value]}
    if isinstance(value, list):
        return {'list': [lossless(v) for v in value]}
    if isinstance(value, dict):
        return {'dict': [[lossless(k), lossless(v)] for k, v in value.items()]}
    if value is None or type(value) in (int, bool, str):
        return value
    raise ValueError(f'unsupported evidence type: {type(value).__name__}')


def restore(value):
    if not isinstance(value, dict):
        return value
    if set(value) == {'bytes_hex'}:
        return bytes.fromhex(value['bytes_hex'])
    if set(value) == {'tuple'}:
        return tuple(restore(v) for v in value['tuple'])
    if set(value) == {'list'}:
        return [restore(v) for v in value['list']]
    if set(value) == {'dict'}:
        pairs = [(restore(k), restore(v)) for k, v in value['dict']]
        result = dict(pairs)
        require(len(result) == len(pairs), 'duplicate key in evidence encoding')
        return result
    raise ValueError('invalid evidence envelope')


def text(value):
    require(type(value) is bytes, 'text field is not source bytes')
    require(not inspect_text(value), 'invalid encoding/control character in export text')
    return value.decode('cp950')


def encode_csv(columns, rows):
    """Validate every cell and round-trip through the standard CSV reader."""
    output = io.StringIO(newline='')
    writer = csv.writer(output, quoting=csv.QUOTE_ALL, lineterminator='\n')
    writer.writerow([name for name, _kind in columns])
    rendered = []
    for row in rows:
        require(len(row) == len(columns), 'CSV row width mismatch')
        cells = []
        for (name, kind), value in zip(columns, row):
            require(type(value) is {'int': int, 'str': str, 'bool': bool}[kind],
                    f'{name}: expected {kind}, got {type(value).__name__}')
            if kind == 'str':
                require(not inspect_text(value), f'{name}: text contains control characters')
            cells.append(('true' if value else 'false') if kind == 'bool' else str(value))
        writer.writerow(cells)
        rendered.append(cells)
    data = output.getvalue().encode('utf-8')
    require(list(csv.reader(io.StringIO(data.decode('utf-8')))) ==
            [[name for name, _kind in columns]] + rendered, 'CSV round-trip mismatch')
    return data


def classify_record(entry, key, value, explicit):
    reasons = []
    if (entry, key) in explicit:
        reasons.append(explicit[entry, key])
    if inspect_text(key) or inspect_text(value):
        reasons.append('encoding_or_control_character')
    if entry == 3205:
        fields = {b'type', b'name', b'desc', b'fpneed', b'mpneed', b'hpneed'}
        ok = (type(key) is int and type(value) is dict and set(value) == fields
              and type(value[b'type']) is int
              and all(type(value[f]) is bytes for f in fields - {b'type'}))
    else:
        ok = schema_ok(entry, 'DATA', key, value)
    if ok is not True:
        reasons.append('schema_mismatch')
    if entry == 2954 and ok:
        for f, v in value.items():
            maximum = f + '最大值'.encode('cp950')
            if maximum in value and v > value[maximum]:
                reasons.append('value_exceeds_named_maximum:' + f.decode('cp950'))
    return reasons


def build_batch():
    profile = json.loads(PROFILE.read_text(encoding='utf-8'))
    arc = Archive()
    require(arc.archive_sha256 == profile['expected_archive_sha256'], 'archive hash mismatch')
    require(arc.keydb_sha256 == profile['expected_key_database_sha256'], 'key database hash mismatch')
    require(profile['bytecode_boundary_solver_enabled'] is False, 'automatic solver forbidden')
    modules, tables, all_tables = {}, {}, {}
    source_manifest = {}
    for index_text, parameters in profile['entries'].items():
        index = int(index_text)
        co = arc.transpile(index, parameters['bounds'], parameters['keys'], use_solver=False)
        require(co['filename'].endswith(b'.py'), 'unexpected source filename')
        modules[index] = co
        tables[index] = (extract_table_report(co)['value'] if index == 3205 else extract(co, 'DATA'))
        all_tables[index] = tables[index]
        source_manifest[index_text] = {
            'filename': co['filename'].decode('ascii'),
            'saved_keys': arc.keys[index_text]['keys'], 'saved_bounds': arc.keys[index_text]['bounds'],
            'applied_keys': parameters['keys'], 'applied_bounds': parameters['bounds'],
            'payload_sha256': sha(arc.payload(index)), 'evidence': parameters['evidence'],
            'note': parameters['note'], 'automatic_bytecode_solver_enabled': False,
        }
    explicit = {(p['entry_index'], p['record_id']): p['reason'] for p in profile['quarantine_policy']}
    quarantine = []
    table_counts = {}
    for index, table in list(tables.items()):
        accepted = {}
        for key, value in table.items():
            reasons = classify_record(index, key, value, explicit)
            if reasons:
                envelope = lossless(value)
                require(restore(envelope) == value, 'evidence round-trip mismatch')
                quarantine.append({'entry_index': index, 'table': 'DATA', 'record_key': lossless(key),
                                   'reasons': reasons, 'value_under_applied_profile': envelope,
                                   'native_verified': False})
            else:
                accepted[key] = value
        tables[index] = accepted
        table_counts[str(index)] = {'source_records': len(table), 'review_csv_records': len(accepted),
                                    'quarantined_records': len(table)-len(accepted)}

    files, file_info = {}, {}
    def emit(name, columns, rows, entry, table, notes, primary_key):
        columns = columns + [('source_entry', 'int'), ('source_table', 'str'), ('review_status', 'str')]
        full_rows = [list(row) + [entry, table, STATUS] for row in rows]
        keys = [tuple(row[[n for n, _ in columns].index(k)] for k in primary_key) for row in full_rows]
        require(len(keys) == len(set(keys)), f'{name}: duplicate exported primary key')
        files[name] = encode_csv(columns, full_rows)
        file_info[name] = {'rows': len(rows), 'columns': [{'name': n, 'type': t} for n, t in columns],
                           'primary_key': primary_key, 'source_entry': entry, 'source_table': table,
                           'notes': notes}

    items = tables[1945]
    categories = extract(modules[1945], 'ITEMDATABYTYPE')
    images = extract(modules[1945], 'SHAPETABLE')
    require(set(categories) == set(all_tables[1945]), 'item category keys differ from full item table')
    require(all(type(k) is int and type(v) is int for k, v in images.items()), 'invalid image mapping')
    emit('items.csv', [('client_shape_id', 'int'), ('name', 'str'), ('description_raw', 'str'),
                       ('category_code_raw', 'int'), ('image_id', 'int'), ('image_mapping_explicit', 'bool')],
         [[k, text(v[0]), text(v[1]), categories[k], images.get(k, k), k in images] for k, v in sorted(items.items())],
         1945, 'DATA+ITEMDATABYTYPE+SHAPETABLE',
         'Display catalog, includes test/history entries. Category meanings not normalized. Image fallback mirrors Shape2Image; assets not checked.', ['client_shape_id'])

    pets = tables[2027]
    emit('pets.csv', [('client_shape_id', 'int'), ('name', 'str'), ('liupai_raw', 'str'),
                     ('attack_type_raw', 'str'), ('carry_grade', 'int'), ('maxskillnum_raw', 'int'), ('address_raw', 'str')],
         [[k, text(v[b'name']), text(v[b'liupai']), text(v[b'attack_type']), v[b'carry_grade'],
           v[b'maxskillnum'], text(v[b'address'])] for k, v in sorted(pets.items())], 2027, 'DATA',
         'Original classifications and maxskillnum semantics retained; not a server progression rule.', ['client_shape_id'])
    candidate_rows = [[k, i, text(name)] for k, v in sorted(pets.items()) for i, name in enumerate(v[b'maySkillLst'])]
    required_rows = [[k, text(v[b'mustSkillName'])] for k, v in sorted(pets.items()) if b'mustSkillName' in v]
    emit('pet_skill_candidates.csv', [('client_shape_id', 'int'), ('sequence', 'int'), ('skill_name_raw', 'str')],
         candidate_rows, 2027, 'DATA.maySkillLst', 'Zero-based source order; not probabilities or guaranteed skills.', ['client_shape_id', 'sequence'])
    emit('pet_required_skills.csv', [('client_shape_id', 'int'), ('skill_name_raw', 'str')],
         required_rows, 2027, 'DATA.mustSkillName', 'Only explicitly present source values; absence is not filled.', ['client_shape_id'])

    aptitudes = tables[2954]
    require(set(all_tables[2954]) <= set(pets), 'aptitude has unknown pet reference')
    aptitude_fields = [s+suffix for s in ['法力', '防禦', '攻擊', '速度', '體力'] for suffix in ['資質', '資質最大值']]
    emit('pet_aptitudes.csv', [('client_shape_id', 'int')] + [(f, 'int') for f in aptitude_fields],
         [[k]+[v[f.encode('cp950')] for f in aptitude_fields] for k, v in sorted(aptitudes.items())],
         2954, 'DATA', 'Original field labels; 2800 withheld. No 1700 substitution or missing-row zero fill.', ['client_shape_id'])
    gaps = [[k, text(pets[k][b'name']), 'no_record_in_2954'] for k in sorted(set(pets)-set(all_tables[2954]))]
    emit('pet_aptitude_missing.csv', [('client_shape_id', 'int'), ('pet_name', 'str'), ('reason', 'str')],
         gaps, 2954, 'DATA (absence checked against 2027.DATA)', 'Missing records, not zero-valued aptitude records.', ['client_shape_id'])

    skills = tables[3205]
    emit('pet_skills.csv', [('skill_id', 'int'), ('type_code_raw', 'int'), ('name', 'str'), ('description_raw', 'str'),
                           ('fpneed_raw', 'str'), ('mpneed_raw', 'str'), ('hpneed_raw', 'str')],
         [[k, v[b'type'], text(v[b'name']), text(v[b'desc']), text(v[b'fpneed']), text(v[b'mpneed']), text(v[b'hpneed'])]
          for k, v in sorted(skills.items())], 3205, 'DATA',
         '581 recovered, weak description rows 719/4406 withheld. Resource formulas are opaque strings: never eval.', ['skill_id'])
    skill_report = extract_table_report(modules[3205])
    duplicate_rows, duplicate_evidence = [], []
    for w in skill_report['overwrites']:
        duplicate_rows.append([w.order, w.at, w.key, text(w.old[b'name']), text(w.new[b'name']), w.old == w.new])
        duplicate_evidence.append({'entry_index': 3205, 'table': 'DATA', 'order': w.order, 'code_offset': w.at,
                                   'key': lossless(w.key), 'old_value': lossless(w.old), 'new_value': lossless(w.new)})
    emit('pet_skill_overwrites.csv', [('write_order', 'int'), ('code_offset', 'int'), ('skill_id', 'int'),
                                     ('old_name', 'str'), ('new_name', 'str'), ('identical_values', 'bool')],
         duplicate_rows, 3205, 'DATA write history', 'Write order is zero-based per DATA dict. Full byte values in overwrite_evidence.jsonl.', ['write_order'])

    name_index = collections.defaultdict(list)
    for key, row in skills.items():
        name_index[text(row[b'name'])].append(key)
    referenced_names = sorted({row[2] for row in candidate_rows} | {row[1] for row in required_rows})
    matches = []
    for name in referenced_names:
        ids = sorted(name_index[name])
        require(ids, f'pet skill name missing from non-quarantined skill catalog: {name}')
        matches += [[name, key, len(ids), len(ids)>1] for key in ids]
    emit('pet_skill_name_matches.csv', [('skill_name_raw', 'str'), ('skill_id', 'int'), ('match_count', 'int'), ('ambiguous', 'bool')],
         matches, 3205, 'DATA.name (references from 2027)',
         'All exact-name candidates retained. Do NOT choose first ID for duplicated names; this is evidence, not authoritative mapping.', ['skill_name_raw', 'skill_id'])

    def json_lines(rows):
        return ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False)+'\n' for row in rows).encode('utf-8')
    files['quarantine.jsonl'] = json_lines(quarantine)
    files['overwrite_evidence.jsonl'] = json_lines(duplicate_evidence)

    # Consume E's checked-in staging bundle only after regenerating evidence and
    # verifying it against the original archive. Never silently copy stale CSVs.
    map_archive = maps.Archive()
    map_evidence = maps.build_evidence(map_archive, with_scan=True)
    committed_evidence = ROOT/'server/docs/csv_checks/agent_e_reproduction.json'
    require(map_evidence == json.loads(committed_evidence.read_text(encoding='utf-8')), 'E evidence changed; review required')
    for index in (1301, 1799, 2601, 2804, 4897):
        require(map_evidence['verifications'][str(index)]['candidate']['pass'], f'E candidate failed: {index}')
    map_schemas = {
        'mapdata_scene_dictionary.csv': (1301, 'DATA', ['scene_id'], {'name'}),
        'mapdata_parent_scene.csv': (1301, 'MAP_ASCRIPTION', ['scene_id'], set()),
        'sceneid2name_minimap_scenes.csv': (400, 'DATA', ['scene_id'], {'name'}),
        'npcname2realnamedata_alias_to_realname.csv': (1799, 'DATA', ['alias'], {'alias', 'real_name'}),
        'npcposdata_records.csv': (2601, 'DATA', ['scene_id', 'record_index'],
                                {'display_name', 'secondary_name', 'real_name', 'field6', 'shape'}),
        'minimapnpcpos_pos_records.csv': (2804, 'DATA_POS', ['scene_id', 'scene_display_name', 'record_index'],
                                       {'scene_display_name', 'display_name', 'secondary_name', 'real_name', 'field6', 'shape'}),
        'minimapnpcpos_wenzi_entries.csv': (2804, 'DATA_WENZI', ['scene_id', 'x', 'y'],
                                         {'name', 'desc', 'npcName'}),
        'npc_2601_vs_2804_agreement.csv': ([2601, 2804], 'DATA vs DATA_POS', ['scene_id', 'npcid'], {'agreement'}),
    }
    with tempfile.TemporaryDirectory(prefix='mx-review-maps-') as temp:
        analyses = {k: maps.EntryAnalysis(map_archive, k, maps.CANDIDATE_BOUNDS.get(k) or
                                         map_archive.keydb[str(k)]['bounds'])
                    for k in (400, 1301, 1799, 2601, 2804, 4897)}
        maps.write_staging_csvs(analyses, temp, archive=map_archive)
        for p in sorted(Path(temp).iterdir()):
            saved = ROOT/'server/docs/csv_checks/staging'/p.name
            require(p.read_bytes() == saved.read_bytes(), f'E staging differs: {p.name}')
            name = 'maps_npcs/'+p.name
            files[name] = p.read_bytes()
            if p.suffix == '.csv':
                rows = list(csv.reader(io.StringIO(p.read_text(encoding='utf-8'))))
                require(all(len(r)==len(rows[0]) for r in rows), f'E CSV width mismatch: {p.name}')
                entry, table, primary_key, string_fields = map_schemas[p.name]
                dict_rows = [dict(zip(rows[0], row)) for row in rows[1:]]
                primary_values = [tuple(row[k] for k in primary_key) for row in dict_rows]
                require(len(set(primary_values)) == len(primary_values), f'E duplicate record key: {p.name}')
                for row in dict_rows:
                    for field, cell in row.items():
                        require(not inspect_text(cell), f'E control character: {p.name}/{field}')
                        if field not in string_fields and cell:
                            require(str(int(cell)) == cell, f'E integer representation: {p.name}/{field}')
                file_info[name] = {'rows': len(rows)-1,
                                   'columns': [{'name': c, 'type': 'str' if c in string_fields else 'int_or_empty'} for c in rows[0]],
                                   'primary_key': primary_key, 'source_entry': entry, 'source_table': table,
                                   'csv_format': 'UTF-8 without BOM; minimal quoting; CRLF; E legacy blank/null convention',
                                   'schema_document': '../AGENT_E_HANDOVER.md',
                                   'notes': 'E staging copied byte-for-byte after revalidation. Preserve record_index and zero IDs. Blank cells use E legacy convention (None/empty text not distinguished); not a lossless typed round-trip format.'}

    counts = {'tables': table_counts, 'skill_write_count': len(skill_report['writes']),
              'skill_unique_count': len(all_tables[3205]), 'skill_overwrite_count': len(duplicate_rows),
              'quarantined_record_count': len(quarantine), 'missing_aptitude_count': len(gaps),
              'pet_skill_names': len(referenced_names),
              'ambiguous_pet_skill_names': {n: sorted(name_index[n]) for n in referenced_names if len(name_index[n])>1},
              'checks': {'item_category_key_set': 'pass', 'pet_aptitude_foreign_keys': 'pass',
                         'pet_skill_names_have_candidates': 'pass', 'csv_round_trip': 'pass',
                         'map_npc_evidence_and_staging_match': 'pass'}}
    files['validation.json'] = json_bytes(counts)
    source_files = ['server/tools/export_review_csv.py', 'server/tools/script_literal_reader.py',
                    'server/tools/review_client_data_boundaries.py', 'server/tools/verify_client_data_boundaries.py',
                    'server/tools/survey_csv_readiness.py', 'server/tools/map_npc_reproduction.py',
                    'tools/decompiler/batch_decompile.py', 'tools/fls_batch_decoder.py',
                    'server/docs/csv_checks/batch_001_profiles.json',
                    'server/docs/csv_checks/agent_e_reproduction.json']
    map_profiles = {
        str(k): {'filename': analysis.co['filename'].decode('ascii'),
                 'applied_keys': map_archive.keydb[str(k)]['keys'],
                 'applied_bounds': maps.CANDIDATE_BOUNDS.get(k) or map_archive.keydb[str(k)]['bounds'],
                 'saved_bounds': map_archive.keydb[str(k)]['bounds'],
                 'payload_sha256': sha(map_archive.payload(k)),
                 'automatic_bytecode_solver_enabled': False,
                 'role': 'supporting_cross_check_only' if k == 4897 else 'csv_source',
                 'evidence': 'server/docs/csv_checks/agent_e_reproduction.json'}
        for k, analysis in analyses.items()
    }
    manifest = {'schema_version': 1, 'batch': 'batch_001', 'status': STATUS, 'native_verified': False,
                'map_npc_profiles': map_profiles,
                'inputs': {'data/script.fls': arc.archive_sha256, 'tools/decompiler/script_fls_keys.json': arc.keydb_sha256},
                'tool_and_evidence_sha256': {p: sha((ROOT/p).read_bytes()) for p in source_files},
                'profiles': source_manifest, 'source_profile': 'server/docs/csv_checks/batch_001_profiles.json',
                'csv_format': {'scope': 'Core CSVs only; maps_npcs overrides retained from E staging',
                               'encoding': 'UTF-8 without BOM', 'delimiter': ',', 'quoting': 'all fields',
                               'newline': 'LF', 'nulls': 'No nulls in core CSVs; missing relations are separate rows/files.',
                               'formula_policy': 'Opaque text. Spreadsheet users must import text; do not evaluate formulas.'},
                'limitations': ['Candidate extraction, not native-loader proof or server-authoritative rules.',
                                'Literal assignments only; later client mutations not applied.',
                                'No Simplified/Traditional conversion; rich-text and formulas preserved.',
                                'Maps/NPC retain E column/blank-cell conventions and unresolved coordinate semantics.',
                                'Only selected tables; unmerged B/C/D/F findings are not globally applied.'],
                'files': {name: {'sha256': sha(data), 'bytes': len(data), **file_info.get(name, {})}
                          for name, data in sorted(files.items())}}
    files['manifest.json'] = json_bytes(manifest)
    return files, counts


def write_batch(out, files):
    out = Path(out).resolve()
    for protected in [ROOT/'data', ROOT/'tools', ROOT/'server/game_data', ROOT/'server/src', ROOT/'.git']:
        require(not out.is_relative_to(protected.resolve()), f'protected output path: {out}')
    require(out != ROOT, 'repository root cannot be output directory')
    if out.exists():
        require(not any(out.rglob('*')), 'output directory must be empty; use --check or a new directory')
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = out/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    parser.add_argument('--check', action='store_true', help='compare fresh output with existing batch, do not write')
    args = parser.parse_args()
    files, counts = build_batch()
    if args.check:
        for name, data in files.items():
            require((args.out/name).read_bytes() == data, f'generated output differs: {name}')
        actual = {p.relative_to(args.out).as_posix() for p in args.out.rglob('*') if p.is_file()}
        require(actual == set(files), 'unexpected/missing files in batch')
    else:
        write_batch(args.out, files)
    print(json.dumps({'mode': 'check' if args.check else 'write', 'output': str(args.out),
                      'file_count': len(files), **counts}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
