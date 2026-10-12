#!/usr/bin/env python3
"""Phase 1 acceptance: independently recompute the fixed batch_001 baseline.

Agent J acceptance tool. It reads the committed artefacts through
``batch_fixture.py`` (its own reader, no producer code) and checks the frozen
numbers, source separation, zero IDs, duplicate records, original order,
quarantine handling and parameter approvals.

Usage (repository root, no third-party dependency):

    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py --out report.json

Exit code 0 only when every check passes. Read-only: this tool never writes to
the batch directory.
"""
from __future__ import annotations

import argparse
import collections
import csv
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from batch_fixture import (  # noqa: E402
    CORE_CSVS, FIXED_EXPECTATIONS, MAP_NPC_CSVS, Batch, BatchError,
    repo_root, sha256_file,
)

CHECKS: list[tuple[str, str, object]] = []


def check(check_id: str, title: str):
    def register(function):
        CHECKS.append((check_id, title, function))
        return function
    return register


class Failure(BatchError):
    pass


def expect(condition, message):
    if not condition:
        raise Failure(message)


def equal(actual, expected, label):
    if actual != expected:
        raise Failure(f'{label}: expected {expected!r}, actual {actual!r}')


# --------------------------------------------------------------------------
# inventory / integrity
# --------------------------------------------------------------------------
@check('data.files.inventory', 'manifest file set equals the committed file set')
def files_inventory(batch: Batch):
    manifest = batch.manifest()
    # manifest.json cannot hash itself; every other committed file must be listed.
    declared = set(manifest['files']) | {'manifest.json'}
    actual = batch.file_names()
    expect(declared == actual, f'missing={sorted(declared - actual)} extra={sorted(actual - declared)}')
    equal(len(actual), 22, 'batch_001 file count (17 CSV + 5 JSON/JSONL)')
    return {'files': len(actual)}


@check('data.files.integrity', 'bytes and sha256 of every artefact match the manifest')
def files_integrity(batch: Batch):
    digest = {}
    for name, spec in sorted(batch.manifest()['files'].items()):
        data = batch.read_bytes(name)
        equal(len(data), spec['bytes'], f'{name} byte length')
        equal(batch.read_bytes(name).hex() and __import__('hashlib').sha256(data).hexdigest(),
              spec['sha256'], f'{name} sha256')
        digest[name] = spec['sha256']
    return {'hashed': len(digest)}


@check('data.inputs.hashes', 'pinned archive and key database hashes still match')
def inputs_hashes(batch: Batch):
    seen = {}
    for rel, expected in sorted(batch.manifest()['inputs'].items()):
        actual = sha256_file(repo_root() / rel)
        equal(actual, expected, f'{rel} sha256')
        seen[rel] = actual
    return seen


@check('data.files.tool_hashes', 'tool/evidence hashes recorded by the manifest still match')
def tool_hashes(batch: Batch):
    changed = {}
    for rel, expected in sorted(batch.manifest()['tool_and_evidence_sha256'].items()):
        actual = sha256_file(repo_root() / rel)
        if actual != expected:
            changed[rel] = {'expected': expected, 'actual': actual}
    # A changed tool hash is not automatically a failure of the data, but it
    # invalidates "the manifest still describes the producer", so it is a finding.
    equal(changed, {}, 'tool/evidence hashes that no longer match the manifest')
    return {'verified': len(batch.manifest()['tool_and_evidence_sha256'])}


@check('data.csv_format.core', 'core CSVs are UTF-8/LF/all-quoted and re-encode byte-identically')
def core_csv_format(batch: Batch):
    for name in CORE_CSVS:
        data = batch.read_bytes(name)
        expect(not data.startswith(b'\xef\xbb\xbf'), f'{name}: BOM found')
        text = batch.csv_text(name)
        rows = list(csv.reader(io.StringIO(text, newline='')))
        sink = io.StringIO(newline='')
        writer = csv.writer(sink, quoting=csv.QUOTE_ALL, lineterminator='\n')
        writer.writerows(rows)
        expect(sink.getvalue().encode('utf-8') == data,
               f'{name}: not reproducible as UTF-8 + LF + QUOTE_ALL (format drift)')
        expect(rows[0] == [c['name'] for c in batch.columns(name)], f'{name}: header differs from manifest')
    return {'files': len(CORE_CSVS)}


@check('data.csv_format.maps_npc', 'maps_npcs CSVs keep E staging format (minimal quoting, CRLF)')
def maps_csv_format(batch: Batch):
    for name in MAP_NPC_CSVS:
        data = batch.read_bytes(name)
        expect(not data.startswith(b'\xef\xbb\xbf'), f'{name}: BOM found')
        rows = list(csv.reader(io.StringIO(batch.csv_text(name), newline='')))
        sink = io.StringIO(newline='')
        writer = csv.writer(sink, quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
        writer.writerows(rows)
        expect(sink.getvalue().encode('utf-8') == data,
               f'{name}: not reproducible as UTF-8 + CRLF + QUOTE_MINIMAL')
        expect(rows[0] == [c['name'] for c in batch.columns(name)], f'{name}: header differs from manifest')
    return {'files': len(MAP_NPC_CSVS)}


@check('data.declared_shape', 'declared rows/columns/primary keys match the actual files')
def declared_shape(batch: Batch):
    manifest = batch.manifest()
    summary = {}
    for name, spec in sorted(manifest['files'].items()):
        if 'columns' not in spec:
            continue
        rows = batch.rows(name)
        equal(len(rows), spec['rows'], f'{name} row count')
        equal([c['name'] for c in spec['columns']], batch.header(name), f'{name} column list')
        summary[name] = len(rows)
    equal(summary['items.csv'], FIXED_EXPECTATIONS['items_rows'], 'items rows')
    return {'csv_files': len(summary)}


@check('data.primary_keys.unique', 'manifest primary keys are unique in every file')
def primary_keys(batch: Batch):
    result = {}
    for name, spec in sorted(batch.manifest()['files'].items()):
        keys = spec.get('primary_key')
        if not keys:
            continue
        seen = collections.Counter(tuple(row[k] for k in keys) for row in batch.rows(name))
        duplicates = [k for k, n in seen.items() if n > 1]
        expect(not duplicates, f'{name}: duplicate primary keys {duplicates[:5]}')
        result[name] = len(seen)
    return result


# --------------------------------------------------------------------------
# fixed numbers
# --------------------------------------------------------------------------
@check('data.counts.fixed', 'frozen review counts (17 CSV / 22 files input)')
def counts_fixed(batch: Batch):
    actual = {
        'items_rows': len(batch.rows('items.csv')),
        'pets_rows': len(batch.rows('pets.csv')),
        'pet_aptitudes_rows': len(batch.rows('pet_aptitudes.csv')),
        'pet_skills_rows': len(batch.rows('pet_skills.csv')),
        'pet_skill_candidates_rows': len(batch.rows('pet_skill_candidates.csv')),
        'pet_required_skills_rows': len(batch.rows('pet_required_skills.csv')),
        'pet_skill_name_match_rows': len(batch.rows('pet_skill_name_matches.csv')),
        'skill_overwrite_rows': len(batch.rows('pet_skill_overwrites.csv')),
        'quarantined_records': len(batch.quarantine()),
        'missing_aptitude_rows': len(batch.rows('pet_aptitude_missing.csv')),
    }
    names = {r['skill_name_raw'] for r in batch.rows('pet_skill_candidates.csv')}
    names |= {r['skill_name_raw'] for r in batch.rows('pet_required_skills.csv')}
    actual['referenced_skill_names'] = len(names)
    matches = collections.Counter(r['skill_name_raw'] for r in batch.rows('pet_skill_name_matches.csv'))
    actual['single_id_skill_names'] = sum(1 for n in names if matches[n] == 1)
    for key, expected in FIXED_EXPECTATIONS.items():
        if key in actual:
            equal(actual[key], expected, f'baseline {key}')
    return actual


@check('data.rows.accounting', 'source = review + quarantined rows for every source entry')
def rows_accounting(batch: Batch):
    tables = batch.validation()['tables']
    equal({int(k) for k in tables}, {1945, 2027, 2954, 3205}, 'reviewed source entries')
    for index, spec in sorted(tables.items(), key=lambda kv: int(kv[0])):
        equal(spec['source_records'], spec['review_csv_records'] + spec['quarantined_records'],
              f'entry {index}: source = review + quarantine')
    recomputed = {
        '1945': len(batch.rows('items.csv')),
        '2027': len(batch.rows('pets.csv')),
        '2954': len(batch.rows('pet_aptitudes.csv')),
        '3205': len(batch.rows('pet_skills.csv')),
    }
    for index, count in recomputed.items():
        equal(count, tables[index]['review_csv_records'], f'entry {index} review rows')
    quarantined = collections.Counter(r['entry_index'] for r in batch.quarantine())
    for index, spec in tables.items():
        equal(quarantined[int(index)], spec['quarantined_records'], f'entry {index} quarantine count')
    validation = batch.validation()
    equal(validation['skill_unique_count'],
          tables['3205']['review_csv_records'] + tables['3205']['quarantined_records'],
          'unique skill ids = exported + quarantined')
    equal(validation['skill_overwrite_count'], len(batch.rows('pet_skill_overwrites.csv')), 'overwrite rows')
    return {'tables': {k: v['source_records'] for k, v in tables.items()}}


@check('data.validation.json', 'validation.json agrees with the recomputed values')
def validation_consistency(batch: Batch):
    validation = batch.validation()
    equal(validation['quarantined_record_count'], len(batch.quarantine()), 'quarantined_record_count')
    equal(validation['missing_aptitude_count'], len(batch.rows('pet_aptitude_missing.csv')), 'missing_aptitude_count')
    equal(validation['skill_overwrite_count'], len(batch.rows('pet_skill_overwrites.csv')), 'skill_overwrite_count')
    names = {r['skill_name_raw'] for r in batch.rows('pet_skill_candidates.csv')}
    names |= {r['skill_name_raw'] for r in batch.rows('pet_required_skills.csv')}
    equal(validation['pet_skill_names'], len(names), 'pet_skill_names')
    for name, ids in sorted(FIXED_EXPECTATIONS['ambiguous_skill_name_matches'].items()):
        equal(validation['ambiguous_pet_skill_names'][name], ids, f'validation.json ambiguity for {name}')
    equal(sorted(validation['ambiguous_pet_skill_names']),
          sorted(FIXED_EXPECTATIONS['ambiguous_skill_name_matches']), 'only the two approved ambiguous names')
    expect(all(status == 'pass' for status in validation['checks'].values()),
           f'validation.json checks are not all "pass": {validation["checks"]}')
    return validation['checks']


# --------------------------------------------------------------------------
# pet / skill graph
# --------------------------------------------------------------------------
@check('data.pets_skills.foreign_keys', 'reviewed child tables only reference reviewed parents')
def pet_graph(batch: Batch):
    pets = {r['client_shape_id'] for r in batch.rows('pets.csv')}
    skills = {r['skill_id'] for r in batch.rows('pet_skills.csv')}
    aptitudes = {r['client_shape_id'] for r in batch.rows('pet_aptitudes.csv')}
    missing = {r['client_shape_id'] for r in batch.rows('pet_aptitude_missing.csv')}
    quarantined = {(r['entry_index'], r['record_key']) for r in batch.quarantine()}
    for row in batch.rows('pet_skill_candidates.csv'):
        expect(row['client_shape_id'] in pets, f'candidate references unknown pet {row["client_shape_id"]}')
    for row in batch.rows('pet_required_skills.csv'):
        expect(row['client_shape_id'] in pets, f'required skill references unknown pet {row["client_shape_id"]}')
    for row in batch.rows('pet_skill_name_matches.csv'):
        expect(row['skill_id'] in skills, f'name match references unreviewed skill {row["skill_id"]}')
    expect(aptitudes <= pets, 'aptitude table references pets outside the pet table')
    equal(len(aptitudes) + len(missing) + sum(1 for k in quarantined if k[0] == 2954), len(pets),
          'pets = aptitudes + missing aptitudes + quarantined aptitude rows')
    return {'pets': len(pets), 'aptitudes': len(aptitudes), 'missing': len(missing)}


@check('data.pet_skill_candidates.order', 'candidate sub-tables keep source order, duplicates and sequence 0..n-1')
def candidates_order(batch: Batch):
    per_pet = collections.defaultdict(list)
    for row in batch.rows('pet_skill_candidates.csv'):
        per_pet[row['client_shape_id']].append(int(row['sequence']))
    for pet, sequences in per_pet.items():
        equal(sequences, list(range(len(sequences))), f'pet {pet}: sequence is not 0..n-1 in file order')
    total = sum(len(v) for v in per_pet.values())
    equal(total, FIXED_EXPECTATIONS['pet_skill_candidates_rows'], 'candidate row total')
    duplicated = sum(1 for pet, rows in
                     ((p, [r['skill_name_raw'] for r in batch.rows('pet_skill_candidates.csv')
                           if r['client_shape_id'] == p]) for p in per_pet)
                     if len(rows) != len(set(rows)))
    return {'pets_with_candidates': len(per_pet), 'pets_with_repeated_names': duplicated}


@check('data.pet_required_skills.presence_only', 'required skills only list fields the source actually has')
def required_skills(batch: Batch):
    rows = batch.rows('pet_required_skills.csv')
    for row in rows:
        expect(row['skill_name_raw'] != '', f'pet {row["client_shape_id"]}: empty required skill name')
        expect(row['skill_name_raw'].strip() != '0', f'pet {row["client_shape_id"]}: fabricated skill id 0')
    equal(len({r['client_shape_id'] for r in rows}), len(rows), 'required-skill rows are unique per pet')
    return {'pets_with_required_skills': len(rows)}


@check('data.pet_skill_name_matches.ambiguity', 'same-name skill matches keep every candidate ID')
def name_matches(batch: Batch):
    matches = batch.rows('pet_skill_name_matches.csv')
    equal(len(matches), FIXED_EXPECTATIONS['pet_skill_name_match_rows'], 'match row count')
    by_name = collections.defaultdict(list)
    for row in matches:
        by_name[row['skill_name_raw']].append(row)
    equal(len(by_name), FIXED_EXPECTATIONS['referenced_skill_names'], 'distinct matched names')
    for name, rows in by_name.items():
        counts = {int(r['match_count']) for r in rows}
        equal(counts, {len(rows)}, f'{name}: match_count does not equal the number of rows')
        flags = {r['ambiguous'] for r in rows}
        equal(flags, {'true' if len(rows) > 1 else 'false'}, f'{name}: ambiguous flag wrong')
    ambiguous = {name: sorted(int(r['skill_id']) for r in rows)
                 for name, rows in by_name.items() if len(rows) > 1}
    equal(ambiguous, FIXED_EXPECTATIONS['ambiguous_skill_name_matches'], 'ambiguous skill name map')
    for name, ids in FIXED_EXPECTATIONS['ambiguous_skill_name_matches'].items():
        expect(len(ids) == 2 and ids[0] != ids[1], f'{name}: both candidate IDs must be retained')
    return {'names': len(by_name), 'ambiguous': ambiguous}


@check('data.pet_skills.quarantine_excluded', 'quarantined skill rows are not in the normal skill table')
def skills_quarantine(batch: Batch):
    ids = {r['skill_id'] for r in batch.rows('pet_skills.csv')}
    for quarantined in (719, 4406):
        expect(str(quarantined) not in ids, f'quarantined skill {quarantined} leaked into pet_skills.csv')
    equal(len(ids), FIXED_EXPECTATIONS['pet_skills_rows'], 'unique skill ids in the review CSV')
    return {'skill_ids': len(ids)}


@check('data.skill_overwrites.order', 'dictionary overwrites keep both values and the write order')
def overwrites(batch: Batch):
    rows = batch.rows('pet_skill_overwrites.csv')
    equal([int(r['write_order']) for r in rows], list(range(352, 361)), 'write order 352..360')
    changed = [r for r in rows if r['identical_values'] == 'false']
    equal(len(changed), 1, 'exactly one overwrite changes the value')
    row = changed[0]
    equal((row['skill_id'], row['old_name'], row['new_name']), ('4573', '天魔返生術', '地魔返生術'),
          'the changed overwrite must be 4573 天魔返生術 -> 地魔返生術')
    evidence = batch.overwrite_evidence()
    equal(len(evidence), len(rows), 'overwrite evidence rows')
    equal(sorted(int(e['order']) for e in evidence), list(range(352, 361)), 'evidence write order')
    # Decode the evidence with this suite's own typed-JSON decoder.
    from batch_fixture import TypedJson
    changed_evidence = next(e for e in evidence if e['key'] == 4573)
    old = TypedJson.decode(changed_evidence['old_value'])
    new = TypedJson.decode(changed_evidence['new_value'])
    equal(TypedJson.text(old[b'name']), '天魔返生術', 'overwrite evidence old name')
    equal(TypedJson.text(new[b'name']), '地魔返生術', 'overwrite evidence new name')
    identical = [e for e in evidence if e['key'] != 4573]
    for item in identical:
        equal(item['old_value'], item['new_value'], f"overwrite {item['key']}: claimed identical but differs")
    return {'overwrites': len(rows), 'value_changing': 1}


@check('data.review_status.labels', 'source entry, source table and review status are explicit on every row')
def review_labels(batch: Batch):
    checked = 0
    for name, expected_entries in FIXED_EXPECTATIONS['source_entries'].items():
        rows = batch.rows(name)
        if 'source_entry' in rows[0]:
            seen = collections.Counter(int(r['source_entry']) for r in rows)
            equal(dict(seen), {entry: seen[entry] for entry in expected_entries}, f'{name} source_entry mix')
        for row in rows:
            if 'source_table' in row:
                expect(row['source_table'].strip() != '', f'{name}: empty source_table')
            if 'review_status' in row:
                equal(row['review_status'], 'review_candidate_not_native_verified', f'{name} review_status')
        checked += 1
    # Source separation: the derived cross-source table must declare both parents
    # in the manifest instead of merging the two NPC sources into one table.
    spec = batch.manifest()['files']['maps_npcs/npc_2601_vs_2804_agreement.csv']
    equal(spec['source_entry'], [2601, 2804], 'cross-source agreement provenance')
    return {'files_checked': checked}


# --------------------------------------------------------------------------
# quarantine / missing data
# --------------------------------------------------------------------------
@check('data.quarantine.records', 'the four quarantined records are preserved with reasons')
def quarantine_records(batch: Batch):
    records = batch.quarantine()
    keys = [(r['entry_index'], r['record_key']) for r in records]
    expected = [(r['entry_index'], r['record_key']) for r in FIXED_EXPECTATIONS['quarantined_keys']]
    equal(sorted(keys), sorted(expected), 'quarantined (entry_index, record_key) set')
    for item in records:
        expect(item['reasons'], f'{item["record_key"]}: quarantine without a reason')
        equal(item['native_verified'], False, f'{item["record_key"]}: quarantine claims native verification')
        equal(item['table'], 'DATA', f'{item["record_key"]}: unexpected source table')
        expect(item['value_under_applied_profile'], f'{item["record_key"]}: quarantine lost the record value')
    profiles = json.loads((repo_root() / 'server/docs/csv_checks/batch_001_profiles.json').read_text('utf-8'))
    policy = {(p['entry_index'], p['record_id']) for p in profiles['quarantine_policy']}
    equal(sorted(policy), sorted(expected), 'batch_001_profiles.json quarantine policy keys')
    return {'records': len(records)}


@check('data.quarantine.2800_not_1700', 'aptitude 2800 keeps the saved 2130/1989 and is not rewritten to 1700')
def quarantine_2800(batch: Batch):
    from batch_fixture import TypedJson
    record = next(r for r in batch.quarantine() if r['record_key'] == 2800 and r['entry_index'] == 2954)
    value = TypedJson.decode(record['value_under_applied_profile'])
    decoded = {TypedJson.text(k): v for k, v in value.items()}
    equal(decoded['法力資質'], 2130, '法力資質 under the applied profile')
    equal(decoded['法力資質最大值'], 1989, '法力資質最大值 under the applied profile')
    expect(any('exceeds_named_maximum' in reason for reason in record['reasons']),
           '2800 quarantine must still record the unresolved value/maximum conflict')
    # 1700 is a legitimate value for other pets, so the check is that row 2800
    # itself was neither substituted nor re-added under the 7979 hypothesis.
    expect(all(int(r['client_shape_id']) != 2800 for r in batch.rows('pet_aptitudes.csv')),
           '2800 must not appear in the normal aptitude table')
    profile = batch.manifest()['profiles']['2954']
    equal(profile['applied_bounds'], profile['saved_bounds'],
          'entry 2954 must run with the saved parameters, not the unapproved 7979 candidate')
    expect(7979 not in profile['applied_bounds'], 'unapproved 7979 bound is in use')
    return {'法力資質': 2130, '法力資質最大值': 1989, 'applied_bounds': profile['applied_bounds']}


@check('data.quarantine.item_72548', 'item 72548 keeps the original invalid CP950 bytes and stays out of items.csv')
def quarantine_item(batch: Batch):
    from batch_fixture import TypedJson
    record = next(r for r in batch.quarantine() if r['record_key'] == 72548 and r['entry_index'] == 1945)
    value = TypedJson.decode(record['value_under_applied_profile'])
    equal(value[0].hex(), 'c2f9a448a7a4c34dc5e9c5e784', 'raw item name bytes')
    expect(all(int(r['client_shape_id']) != 72548 for r in batch.rows('items.csv')),
           '72548 leaked into items.csv')
    return {'bytes_hex': value[0].hex()}


@check('data.quarantine.skill_rows', 'quarantined skill rows keep the six source fields')
def quarantine_skills(batch: Batch):
    from batch_fixture import TypedJson
    for key in (719, 4406):
        record = next(r for r in batch.quarantine() if r['record_key'] == key and r['entry_index'] == 3205)
        value = TypedJson.decode(record['value_under_applied_profile'])
        fields = sorted(TypedJson.text(k) for k in value)
        equal(fields, ['desc', 'fpneed', 'hpneed', 'mpneed', 'name', 'type'], f'{key} field set')
        expect(TypedJson.text(value[b'name']) != '', f'{key}: name lost')
    return {'rows': [719, 4406]}


@check('data.missing_aptitudes.not_zero_filled', 'missing aptitude rows are declared missing, never zero-filled')
def missing_aptitudes(batch: Batch):
    rows = batch.rows('pet_aptitude_missing.csv')
    ids = sorted(int(r['client_shape_id']) for r in rows)
    equal(ids, FIXED_EXPECTATIONS['missing_aptitude_ids'], 'missing aptitude ids')
    for row in rows:
        expect(row['reason'].strip() != '', f'{row["client_shape_id"]}: missing row without a reason')
    have = {int(r['client_shape_id']) for r in batch.rows('pet_aptitudes.csv')}
    expect(have.isdisjoint(ids), 'missing aptitude ids also exist in pet_aptitudes.csv')
    expect(2800 not in have, 'quarantined 2800 must not be used as a missing-aptitude placeholder')
    for row in batch.typed('pet_aptitudes.csv'):
        values = [v for k, v in row.items() if '資質' in k]
        expect(any(v != 0 for v in values), f'{row["client_shape_id"]}: synthesised all-zero aptitude row')
    return {'missing': ids}


# --------------------------------------------------------------------------
# maps / NPC
# --------------------------------------------------------------------------
@check('data.maps.rows_and_zero_ids', 'map/NPC record counts and NPC ID 0 records are preserved')
def maps_zero(batch: Batch):
    a = batch.rows('maps_npcs/npcposdata_records.csv')
    b = batch.rows('maps_npcs/minimapnpcpos_pos_records.csv')
    equal(len(a), FIXED_EXPECTATIONS['map_npc_rows']['maps_npcs/npcposdata_records.csv'], '2601 record rows')
    equal(len(b), FIXED_EXPECTATIONS['map_npc_rows']['maps_npcs/minimapnpcpos_pos_records.csv'], '2804 POS rows')
    equal(sum(1 for r in a if r['npcid'] == '0'), FIXED_EXPECTATIONS['zero_npcid_records']['npcposdata'],
          'zero npcid rows in 2601')
    equal(sum(1 for r in b if r['npcid'] == '0'), FIXED_EXPECTATIONS['zero_npcid_records']['minimapnpcpos_pos'],
          'zero npcid rows in 2804')
    # Zero-ID rows belong to many scenes and must stay as individual records,
    # not be collapsed into one "NPC 0" or dropped.
    for name, rows in (('2601', a), ('2804', b)):
        zero_rows = [r for r in rows if r['npcid'] == '0']
        scenes = {r['scene_id'] for r in zero_rows}
        expect(len(scenes) > 1, f'{name}: zero-ID rows collapsed to a single scene')
        expect(len({(r['scene_id'], r['record_index']) for r in zero_rows}) == len(zero_rows),
               f'{name}: zero-ID rows were merged')
    return {'2601': len(a), '2804': len(b),
            'zero_ids': dict(FIXED_EXPECTATIONS['zero_npcid_records'])}


@check('data.maps.no_pair_dedup', '(scene_id, npcid) is not a unique key and duplicates are retained')
def maps_duplicates(batch: Batch):
    result = {}
    for name, label in (('maps_npcs/npcposdata_records.csv', '2601'),
                        ('maps_npcs/minimapnpcpos_pos_records.csv', '2804')):
        rows = batch.rows(name)
        seen = collections.Counter((r['scene_id'], r['npcid']) for r in rows if r['npcid'] != '0')
        repeated = {k: n for k, n in seen.items() if n > 1}
        expect(repeated, f'{label}: no repeated (scene_id, npcid) pairs — data may have been deduplicated')
        equal(max(repeated.values()) >= 2, True, f'{label}: duplicate groups collapsed')
        result[label] = {'duplicate_groups': len(repeated), 'max_group': max(repeated.values())}
    return result


@check('data.maps.order_preserved', 'record_index keeps original order per scene for both NPC sources')
def maps_order(batch: Batch):
    checks = 0
    for name in ('maps_npcs/npcposdata_records.csv', 'maps_npcs/minimapnpcpos_pos_records.csv'):
        per_scene = collections.defaultdict(list)
        for row in batch.rows(name):
            per_scene[row['scene_id']].append(int(row['record_index']))
        for scene, indexes in per_scene.items():
            equal(indexes, list(range(len(indexes))), f'{name} scene {scene}: record_index order')
        checks += len(per_scene)
    return {'scenes_checked': checks}


@check('data.maps.source_separation', 'E staging sources stay separate and byte-identical to the batch copies')
def maps_separation(batch: Batch):
    staging = repo_root() / 'server/docs/csv_checks/staging'
    equal(sorted(p.name for p in staging.glob('*.csv')),
          sorted(Path(name).name for name in MAP_NPC_CSVS if (staging / Path(name).name).exists()),
          'staging file list')
    for name in MAP_NPC_CSVS:
        staged = staging / Path(name).name
        if staged.exists():
            equal(batch.read_bytes(name), staged.read_bytes(), f'{name} differs from E staging')
    provenance = json.loads(batch.read_bytes('maps_npcs/provenance.json').decode('utf-8'))
    equal(provenance['status'], 'candidate_framing_not_confirmed_by_the_native_loader', 'provenance status')
    expect('no table merging' in provenance['rules'], 'provenance must forbid table merging')
    expect('zero-npcid records kept' in provenance['rules'], 'provenance must keep zero npcid records')
    expect('duplicate records kept' in provenance['rules'], 'provenance must keep duplicates')
    agreement = batch.rows('maps_npcs/npc_2601_vs_2804_agreement.csv')
    expect(all(r['npcid'] != '0' for r in agreement), 'agreement table must only compare non-zero NPC IDs')
    expect(len({(r['scene_id'], r['npcid']) for r in agreement}) == len(agreement), 'agreement table not unique')
    return {'staging_files': len(list(staging.glob('*.csv')))}


@check('data.profiles.parameters_approved', 'no automatic solver and no unapproved parameter substitution')
def profile_parameters(batch: Batch):
    manifest = batch.manifest()
    result = {}
    for group in ('profiles', 'map_npc_profiles'):
        for index, profile in sorted(manifest[group].items()):
            equal(profile['automatic_bytecode_solver_enabled'], False,
                  f'{group}[{index}]: automatic bytecode solver must stay disabled')
            result[f'{group}.{index}'] = profile['applied_bounds']
    profiles = json.loads((repo_root() / 'server/docs/csv_checks/batch_001_profiles.json').read_text('utf-8'))
    equal(profiles['status'], 'review_only_not_native_verified', 'parameter file status')
    equal(profiles['bytecode_boundary_solver_enabled'], False, 'parameter file solver flag')
    equal(profiles['merged_prs'], [19, 18, 20], 'parameter file merge provenance')
    for index, entry in sorted(profiles['entries'].items()):
        entry_profile = manifest['profiles'][index]
        equal(entry_profile['applied_bounds'], entry['bounds'], f'entry {index} bounds vs batch_001_profiles.json')
        # Applied keys may be shorter than the file's list; compare the used prefix.
        equal(entry_profile['applied_keys'], entry['keys'][:len(entry_profile['applied_keys'])],
              f'entry {index} keys vs batch_001_profiles.json')
    saved = manifest['profiles']['2954']['saved_bounds']
    applied = manifest['profiles']['2954']['applied_bounds']
    expect(7979 not in applied, 'entry 2954 must not use the unapproved 7979 candidate bound')
    equal(applied, saved, 'entry 2954 applied bounds')
    equal(manifest['profiles']['3205']['applied_bounds'][1], 36123, 'entry 3205 approved second bound')
    equal(manifest['profiles']['3205']['saved_bounds'][1], 36122, 'entry 3205 saved second bound')
    equal(manifest['profiles']['2027']['applied_bounds'][2], 16264, 'entry 2027 approved third bound')
    equal(manifest['profiles']['2027']['applied_bounds'][3], 21751, 'entry 2027 approved fourth bound')
    equal(manifest['profiles']['1945']['applied_bounds'][2], 778759, 'entry 1945 candidate third bound')
    equal(manifest['native_verified'], False, 'manifest native_verified flag')
    equal(manifest['status'], 'review_candidate_not_native_verified', 'manifest status')
    return {'profiles': len(result)}


@check('data.text.no_simplified_conversion', 'traditional text is preserved and no simplified rewrite leaked in')
def text_fidelity(batch: Batch):
    text = ''.join(batch.csv_text(name) for name in CORE_CSVS + MAP_NPC_CSVS)
    for needle in FIXED_EXPECTATIONS['required_traditional_strings']:
        expect(needle in text, f'expected traditional string missing: {needle}')
    for needle in FIXED_EXPECTATIONS['forbidden_simplified_strings']:
        expect(needle not in text, f'simplified rewrite detected: {needle}')
    return {'required': len(FIXED_EXPECTATIONS['required_traditional_strings']),
            'forbidden': len(FIXED_EXPECTATIONS['forbidden_simplified_strings'])}


@check('data.text.opaque_formulas', 'resource formulas and rich-text markers stay opaque source text')
def opaque_formulas(batch: Batch):
    items = batch.rows('items.csv')
    with_marker = sum(1 for r in items if '#' in r['description_raw'])
    expect(with_marker > 0, 'no rich-text markers found — item text may have been rewritten')
    formular = [r for r in items if '=' in r['description_raw'] or '$' in r['description_raw']]
    skills = batch.rows('pet_skills.csv')
    equal(sum(1 for r in skills if r['description_raw'] == ''), 0, 'skill rows with an empty description')
    equal(sum(1 for r in skills if r['fpneed_raw'] == ''), 0, 'skill rows with an empty fpneed')
    # Numeric resource fields must stay raw text, never evaluated numbers.
    for row in skills[:50]:
        for field in ('fpneed_raw', 'mpneed_raw', 'hpneed_raw'):
            expect(isinstance(row[field], str), f'{field} is not raw text')
    return {'items_with_rich_text': with_marker, 'items_with_equals_or_dollar': len(formular)}


# --------------------------------------------------------------------------
def run(batch_root: Path | None = None) -> dict:
    batch = Batch(batch_root)
    results = []
    for check_id, title, function in CHECKS:
        try:
            detail = function(batch)
            results.append({'check': check_id, 'title': title, 'status': 'pass', 'detail': detail})
        except Exception as exc:  # noqa: BLE001 - acceptance report, not control flow
            results.append({'check': check_id, 'title': title, 'status': 'fail',
                            'detail': f'{type(exc).__name__}: {exc}'})
    failed = [r for r in results if r['status'] == 'fail']
    return {
        'stage': 'phase1_independent_data_baseline',
        'batch_root': str(batch_root or batch.root),
        'tool': 'server/tools/review_browser_checks/verify_data_baseline.py',
        'checks': results,
        'summary': {'total': len(results), 'pass': len(results) - len(failed), 'fail': len(failed)},
        'status': 'fail' if failed else 'pass',
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--batch', type=Path, default=None, help='batch directory (default: batch_001)')
    parser.add_argument('--out', type=Path, default=None, help='write the JSON report to this path')
    parser.add_argument('--quiet', action='store_true', help='only print the summary line')
    args = parser.parse_args(argv)
    report = run(args.batch)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                            encoding='utf-8')
    if not args.quiet:
        for item in report['checks']:
            marker = 'ok  ' if item['status'] == 'pass' else 'FAIL'
            print(f'[{marker}] {item["check"]}: {item["title"]}')
            if item['status'] == 'fail':
                print(f'         {item["detail"]}')
    print(json.dumps({'status': report['status'], **report['summary']}, ensure_ascii=False))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
