"""Corrupt scratch copies only; hash refresh must not bypass semantic checks."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

SERVER = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SERVER / 'src'))
from mxsj_catalog import ReviewCatalog
from mxsj_catalog.errors import CatalogIntegrityError


class EvidenceConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'batch'
        shutil.copytree(SERVER / 'docs/csv_checks/batch_001', self.root)

    def read_lines(self, name):
        return [json.loads(line) for line in (self.root / name).read_text().splitlines()]

    def write(self, name, value, lines=True):
        text = (''.join(json.dumps(v, ensure_ascii=False) + '\n' for v in value) if lines
                else json.dumps(value, ensure_ascii=False))
        data = text.encode()
        (self.root / name).write_bytes(data)
        manifest = json.loads((self.root / 'manifest.json').read_text())
        manifest['files'][name].update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
        (self.root / 'manifest.json').write_text(json.dumps(manifest))

    def test_valid_batch_is_accepted(self):
        catalog = ReviewCatalog.load(self.root)
        self.assertEqual(catalog.query_quarantine()[1], 4)
        self.assertEqual(catalog.query_overwrites()[1], 9)

    def test_shortened_quarantine_with_updated_hash_is_refused(self):
        self.write('quarantine.jsonl', self.read_lines('quarantine.jsonl')[:1])
        with self.assertRaisesRegex(CatalogIntegrityError, 'quarantine.*count'):
            ReviewCatalog.load(self.root)

    def test_shortened_overwrites_with_updated_hash_is_refused(self):
        self.write('overwrite_evidence.jsonl', self.read_lines('overwrite_evidence.jsonl')[:1])
        with self.assertRaisesRegex(CatalogIntegrityError, 'overwrites.*count'):
            ReviewCatalog.load(self.root)

    def test_duplicate_quarantine_identity_is_refused(self):
        rows = self.read_lines('quarantine.jsonl'); rows[-1] = rows[-2]
        self.write('quarantine.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'duplicate'):
            ReviewCatalog.load(self.root)

    def test_per_source_quarantine_mismatch_is_refused(self):
        rows = self.read_lines('quarantine.jsonl'); rows[-1]['entry_index'] = 1945
        self.write('quarantine.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'quarantine.*count'):
            ReviewCatalog.load(self.root)

    def test_empty_raw_evidence_is_refused(self):
        rows = self.read_lines('quarantine.jsonl'); rows[0]['value_under_applied_profile'] = {}
        self.write('quarantine.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'evidence envelope'):
            ReviewCatalog.load(self.root)

    def test_missing_overwrite_payload_is_refused(self):
        rows = self.read_lines('overwrite_evidence.jsonl'); del rows[0]['old_value']
        self.write('overwrite_evidence.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'required evidence'):
            ReviewCatalog.load(self.root)

    def test_overwrite_csv_offset_mismatch_is_refused(self):
        rows = self.read_lines('overwrite_evidence.jsonl'); rows[0]['code_offset'] += 1
        self.write('overwrite_evidence.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'CSV write summary'):
            ReviewCatalog.load(self.root)

    def test_invalid_summary_counter_is_refused(self):
        summary = json.loads((self.root / 'validation.json').read_text())
        summary['quarantined_record_count'] = '4'
        self.write('validation.json', summary, lines=False)
        with self.assertRaisesRegex(CatalogIntegrityError, 'expected count'):
            ReviewCatalog.load(self.root)

    def test_missing_summary_counter_is_refused(self):
        summary = json.loads((self.root / 'validation.json').read_text())
        del summary['skill_overwrite_count']
        self.write('validation.json', summary, lines=False)
        with self.assertRaisesRegex(CatalogIntegrityError, 'expected count'):
            ReviewCatalog.load(self.root)

    def test_absent_quarantine_reasons_are_refused(self):
        rows = self.read_lines('quarantine.jsonl'); rows[0]['reasons'] = []
        self.write('quarantine.jsonl', rows)
        with self.assertRaisesRegex(CatalogIntegrityError, 'reasons'):
            ReviewCatalog.load(self.root)


if __name__ == '__main__':
    unittest.main()
