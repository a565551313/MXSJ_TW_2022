"""Loader/catalog acceptance for Agent H's `mxsj_catalog` package (interface level).

These are *not* HTTP tests. The defeated classes the coordinator found are loader
contract defects, so they are exercised through the loader's public entry points:

    mxsj_catalog.catalog.ReviewCatalog.load(base_dir)
    ReviewCatalog.get_batch_info() / list_datasets() / query_records() / get_record()

Every test works on a **scratch copy** of batch_001 built by the acceptance
fixture (`server/docs/csv_checks/batch_001/` is never written to), and the loader
is only reached through the modules Agent H owns — no monkey-patching, no edits
to the product source.

While the catalog package is absent the module reports NOT EXECUTED.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import support  # noqa: E402,F401

from batch_fixture import Batch, default_batch_dir, repo_root, write_temp_batch  # noqa: E402

CATALOG_SRC = repo_root() / 'server/src'
CATALOG_PACKAGE = CATALOG_SRC / 'mxsj_catalog'


def load_catalog_module():
    if not CATALOG_PACKAGE.is_dir():
        return None
    if str(CATALOG_SRC) not in sys.path:
        sys.path.insert(0, str(CATALOG_SRC))
    from mxsj_catalog.catalog import ReviewCatalog  # noqa: PLC0415
    return ReviewCatalog


ReviewCatalog = load_catalog_module()
DELIVERED = ReviewCatalog is not None


def require_delivery() -> None:
    if not DELIVERED:
        raise unittest.SkipTest(
            'NOT EXECUTED: server/src/mxsj_catalog is not present in this checkout '
            '(Agent H loader not delivered/merged)')


class ScratchBatch:
    """A throwaway batch copy that can be deliberately damaged."""

    def __init__(self, case: str):
        self.path = write_temp_batch(support.tempdir('mxsj-loader-') / case, default_batch_dir())
        self.manifest = json.loads((self.path / 'manifest.json').read_text(encoding='utf-8'))

    def refresh_manifest_entry(self, name: str, *, rows: int | None = None) -> None:
        spec = self.manifest['files'][name]
        data = (self.path / name).read_bytes()
        spec['bytes'] = len(data)
        spec['sha256'] = hashlib.sha256(data).hexdigest()
        if rows is not None:
            spec['rows'] = rows
        (self.path / 'manifest.json').write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')


class LoaderContractCase(unittest.TestCase):
    def setUp(self):
        require_delivery()

    @staticmethod
    def load(path: Path):
        return ReviewCatalog.load(path)


class ImmutabilityTests(LoaderContractCase):
    """Defect 4: callers must not be able to change the catalogue through return values."""

    def test_batch_info_returns_isolated_copies(self):
        catalog = self.load(default_batch_dir())
        before = catalog.get_batch_info()
        mutated = catalog.get_batch_info()
        mutated['tables_summary']['1945']['source_records'] = -1
        mutated['validation_summary']['missing_aptitude_count'] = -1
        mutated['csv_format']['delimiter'] = 'TAMPERED'
        again = catalog.get_batch_info()
        self.assertEqual(again['tables_summary']['1945']['source_records'],
                         before['tables_summary']['1945']['source_records'],
                         'mutating a returned batch summary changed the internal catalogue state')
        self.assertEqual(again['validation_summary']['missing_aptitude_count'], 3)
        self.assertEqual(again['csv_format']['delimiter'], ',')

    def test_dataset_schema_fields_are_immutable(self):
        catalog = self.load(default_batch_dir())
        schema = catalog.get_dataset('npc_2601_vs_2804_agreement').schema
        self.assertNotIsInstance(schema.source_entry, list,
                                 'nested list in DatasetSchema.source_entry can be mutated in place')
        self.assertIsInstance(schema.source_entry, tuple)
        self.assertIsInstance(schema.primary_key, tuple)

    def test_record_objects_are_copies(self):
        catalog = self.load(default_batch_dir())
        first = catalog.get_record('items', '11')
        first['name'] = 'TAMPERED'
        second = catalog.get_record('items', '11')
        self.assertEqual(second['name'], 'NPC呼叫器')
        listing, _ = catalog.query_records('items', offset=0, limit=1)
        listing[0]['name'] = 'TAMPERED'
        again, _ = catalog.query_records('items', offset=0, limit=1)
        self.assertEqual(again[0]['name'], 'NPC呼叫器')

    def test_quarantine_evidence_is_isolated(self):
        catalog = self.load(default_batch_dir())
        records, _ = catalog.query_quarantine()
        records[0]['reasons'].append('TAMPERED')
        again, _ = catalog.query_quarantine()
        self.assertNotIn('TAMPERED', again[0]['reasons'])


class CsvFidelityTests(LoaderContractCase):
    """Defect 5: quoted LF/CRLF/CR inside a field must survive loading."""

    def _synthetic_items(self, value: str) -> ScratchBatch:
        scratch = ScratchBatch('csv_fidelity')
        columns = [c['name'] for c in scratch.manifest['files']['items.csv']['columns']]
        sink = io.StringIO(newline='')
        writer = csv.writer(sink, quoting=csv.QUOTE_ALL, lineterminator='\n')
        writer.writerow(columns)
        row = ['1', 'x', value, '0', '1', 'false', '1945', 'DATA', 'review_candidate']
        writer.writerow(row)
        (scratch.path / 'items.csv').write_bytes(sink.getvalue().encode('utf-8'))
        scratch.refresh_manifest_entry('items.csv', rows=1)
        return scratch

    def test_embedded_newlines_are_preserved(self):
        for label, raw in (('LF', 'before\nafter'), ('CRLF', 'before\r\nafter'), ('CR', 'before\rafter')):
            with self.subTest(case=label):
                scratch = self._synthetic_items(raw)
                catalog = self.load(scratch.path)
                record = catalog.get_record('items', '1')
                self.assertIsNotNone(record, f'{label}: the synthetic row was not readable')
                self.assertEqual(record['description_raw'], raw,
                                 f'{label}: the loader does not read the CSV with newline="" '
                                 f'(splitlines() destroys quoted line breaks)')

    def test_qa_on_real_batch_records_round_trip(self):
        catalog = self.load(default_batch_dir())
        for dataset, pk, field in (('items', '11', 'description_raw'),
                                   ('pet_skills', '101', 'description_raw')):
            with self.subTest(dataset=dataset):
                record = catalog.get_record(dataset, pk)
                expected = next(row[field] for row in Batch(default_batch_dir()).rows(f'{dataset}.csv')
                                if row[{'items': 'client_shape_id', 'pet_skills': 'skill_id'}[dataset]] == pk)
                self.assertEqual(record[field], expected)


class ParameterValidationTests(LoaderContractCase):
    """Defect 6: misspelled/invalid parameters must not be silently ignored."""

    def setUp(self):
        super().setUp()
        self.catalog = self.load(default_batch_dir())

    def test_invalid_order_is_rejected(self):
        rows = self.catalog.query_records('items', offset=0, limit=5, sort_by='client_shape_id',
                                          order='ascending-wrong')
        with self.assertRaises(ValueError):
            # Documented values are exactly 'asc' and 'desc'.
            self.catalog.query_records('items', offset=0, limit=5, sort_by='client_shape_id',
                                       order='x')

    def test_unknown_filter_column_is_rejected(self):
        with self.assertRaises(ValueError):
            self.catalog.query_records('items', offset=0, limit=5,
                                       filters={'entry_indexx': '1945'})

    def test_misspelled_quarantine_filter_is_rejected(self):
        with self.assertRaises((ValueError, TypeError)):
            self.catalog.query_quarantine(entry_index_x=2954)  # type: ignore[call-arg]

    def test_valid_filters_still_work(self):
        records, total = self.catalog.query_quarantine(entry_index=2954)
        self.assertEqual(total, 1)
        self.assertEqual(records[0]['record_key'], 2800)

    def test_limit_bounds_are_enforced(self):
        for limit in (0, -1, 501):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                self.catalog.query_records('items', offset=0, limit=limit)


class EvidenceFileTests(LoaderContractCase):
    """Defect 1: missing evidence files must not produce a 'ready' catalogue."""

    REQUIRED = ('quarantine.jsonl', 'overwrite_evidence.jsonl', 'validation.json',
                'maps_npcs/provenance.json')

    def test_missing_evidence_file_is_refused(self):
        for name in self.REQUIRED:
            with self.subTest(file=name):
                scratch = ScratchBatch('missing_' + name.replace('/', '_'))
                (scratch.path / name).unlink()
                with self.assertRaises(Exception) as caught:
                    self.load(scratch.path)
                self.assertNotIsInstance(caught.exception, (AssertionError, unittest.SkipTest))
                message = str(caught.exception).lower()
                self.assertTrue(any(word in message for word in
                                    ('missing', 'integrity', 'required', 'quarantine', 'overwrite',
                                     'validation', 'provenance')),
                                f'{name}: refusal message is not explanatory: {caught.exception!r}')

    def test_tampered_evidence_without_hash_update_is_refused(self):
        """Defect 2: editing quarantine.jsonl (kept byte-count equal) must be detected."""
        scratch = ScratchBatch('tampered_quarantine')
        record = Batch(scratch.path).quarantine()
        for item in record:
            if item['record_key'] == 2800:
                for pair in item['value_under_applied_profile']['dict']:
                    if bytes.fromhex(pair[0]['bytes_hex']).decode('cp950') == '法力資質':
                        pair[1] = 1234  # same length, same file size, different content
        lines = '\n'.join(json.dumps(item, ensure_ascii=False, sort_keys=True) for item in record) + '\n'
        original = (scratch.path / 'quarantine.jsonl').read_bytes()
        assert len(lines.encode('utf-8')) == len(original), 'tamper must keep the byte length'
        (scratch.path / 'quarantine.jsonl').write_bytes(lines.encode('utf-8'))
        with self.assertRaises(Exception) as caught:
            self.load(scratch.path)
        self.assertTrue(any(word in str(caught.exception).lower()
                            for word in ('sha256', 'hash', 'integrity', 'mismatch', 'checksum')),
                        f'tampered evidence was accepted: {caught.exception!r}')

    def test_evidence_row_counts_are_checked(self):
        scratch = ScratchBatch('shrunken_quarantine')
        record = Batch(scratch.path).quarantine()
        kept = json.dumps(record[0], ensure_ascii=False, sort_keys=True) + '\n'
        (scratch.path / 'quarantine.jsonl').write_bytes(kept.encode('utf-8'))
        scratch.refresh_manifest_entry('quarantine.jsonl')
        with self.assertRaises(Exception) as caught:
            self.load(scratch.path)
        self.assertTrue(any(word in str(caught.exception).lower()
                            for word in ('count', 'row', 'expected', '4', 'quarantine')),
                        f'shrunken quarantine evidence was accepted: {caught.exception!r}')


class ManifestCoverageTests(LoaderContractCase):
    """Defect 3: dropping a dataset from the manifest must not silently shrink the catalogue."""

    EXPECTED_DATASETS = 17

    def test_manifest_shrink_is_refused(self):
        scratch = ScratchBatch('manifest_shrink')
        scratch.manifest['files'].pop('items.csv')
        (scratch.path / 'manifest.json').write_text(
            json.dumps(scratch.manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
        with self.assertRaises(Exception) as caught:
            self.load(scratch.path)
        self.assertTrue(any(word in str(caught.exception).lower()
                            for word in ('dataset', 'missing', 'items', 'count', 'expected')),
                        f'the shrunken manifest was accepted: {caught.exception!r}')

    def test_declared_file_must_exist(self):
        scratch = ScratchBatch('missing_csv')
        (scratch.path / 'items.csv').unlink()
        with self.assertRaises(Exception):
            self.load(scratch.path)

    def test_dataset_list_matches_manifest(self):
        catalog = self.load(default_batch_dir())
        datasets = catalog.list_datasets()
        self.assertEqual(len(datasets), self.EXPECTED_DATASETS)
        manifest = Batch(default_batch_dir()).manifest()
        declared = {name for name in manifest['files'] if name.endswith('.csv')}
        self.assertEqual({d['filename'] for d in datasets}, declared)
        for dataset in datasets:
            spec = manifest['files'][dataset['filename']]
            self.assertEqual(dataset['rows'], spec['rows'], dataset['filename'])
            self.assertEqual(tuple(dataset['primary_key']), tuple(spec['primary_key']), dataset['filename'])
            self.assertEqual([c['name'] for c in dataset['columns']],
                             [c['name'] for c in spec['columns']], dataset['filename'])


class SemanticsTests(LoaderContractCase):
    """Data semantics the review tool must not lose (independent of HTTP)."""

    def setUp(self):
        super().setUp()
        self.catalog = self.load(default_batch_dir())

    def test_quarantined_records_are_absent_from_normal_datasets(self):
        for dataset, key in (('items', '72548'), ('pet_aptitudes', '2800'), ('pet_skills', '719'),
                             ('pet_skills', '4406')):
            with self.subTest(dataset=dataset, key=key):
                self.assertIsNone(self.catalog.get_record(dataset, key))
        records, total = self.catalog.query_quarantine()
        self.assertEqual(total, 4)

    def test_missing_aptitudes_are_separate_and_not_zero_filled(self):
        missing = self.catalog.get_missing_aptitudes()
        self.assertEqual(sorted(int(r['client_shape_id']) for r in missing), [3010, 4021, 4022])
        for record in missing:
            self.assertNotIn('法力資質', record)

    def test_ambiguous_skill_names_keep_both_ids(self):
        ambiguous = self.catalog.get_ambiguous_skills()
        by_name: dict[str, list[int]] = {}
        for record in ambiguous:
            by_name.setdefault(record['skill_name_raw'], []).append(int(record['skill_id']))
        self.assertEqual({name: sorted(ids) for name, ids in by_name.items()},
                         {'高級命中': [229, 255], '終級命中': [329, 355]})

    def test_npc_records_keep_zero_ids_and_duplicates(self):
        records, total = self.catalog.query_records('npcposdata_records', offset=0, limit=1)
        self.assertEqual(total, 1335)
        zero, zero_total = self.catalog.query_records('npcposdata_records', offset=0, limit=1,
                                                      filters={'npcid': 0})
        self.assertEqual(zero_total, 632)
        first_page, _ = self.catalog.query_records('npcposdata_records', offset=0, limit=20)
        csv_order = [(int(r['scene_id']), int(r['record_index']))
                     for r in Batch(default_batch_dir()).rows('maps_npcs/npcposdata_records.csv')[:20]]
        self.assertEqual([(r['scene_id'], r['record_index']) for r in first_page], csv_order,
                         'source record order is not preserved')

    def test_pagination_is_complete_and_stable(self):
        seen: list[str] = []
        offset = 0
        while True:
            page, total = self.catalog.query_records('items', offset=offset, limit=500)
            if not page:
                break
            seen.extend(r['_pk'] for r in page)
            offset += len(page)
            if offset >= total:
                break
        self.assertEqual(len(seen), 6851)
        self.assertEqual(len(set(seen)), 6851)


if __name__ == '__main__':
    unittest.main()
