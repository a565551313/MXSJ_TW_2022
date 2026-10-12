#!/usr/bin/env python3
"""Negative/positive control test double for the acceptance harness (NOT a product API).

This file exists so that Agent J's acceptance harness is itself tested: it is a
deliberately *injected-fault* HTTP server used only by
``server/tests/review_browser_acceptance/test_harness_self_check.py``.

* It is **not** an implementation of Agent H's API and **not** a proposal for the
  contract; it only serves CSV rows out of a batch directory with the operation
  map that ``--emit-map`` prints.
* With ``--defects none`` it behaves like a well-behaved read-only server so the
  harness has a positive control (proving the probe is not trivially failing).
* With defects enabled it violates individual acceptance requirements so the
  harness must report those checks as failures.

Standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_fixture import Batch, default_batch_dir, repo_root  # noqa: E402

DATASETS = {
    'items': ('items.csv', 'client_shape_id', {'72548'}),
    'pets': ('pets.csv', 'client_shape_id', set()),
    'pet_aptitudes': ('pet_aptitudes.csv', 'client_shape_id', {'2800'}),
    'pet_skills': ('pet_skills.csv', 'skill_id', {'719', '4406'}),
    'pet_skill_name_matches': ('pet_skill_name_matches.csv', 'skill_id', set()),
    'npcposdata': ('maps_npcs/npcposdata_records.csv', '_rowkey', set()),
    'minimapnpcpos': ('maps_npcs/minimapnpcpos_pos_records.csv', '_rowkey', set()),
}

ALL_DEFECTS = (
    'dedup_pairs', 'zero_fill_missing', 'rewrite_2800', 'leak_quarantine', 'coerce_literals',
    'silent_default_page', 'traversal_allowed', 'accept_mutations', 'hide_ambiguous',
    'localhost_in_page', 'mutation_route', 'ignore_integrity', 'serve_corrupt', 'unstable_order',
)


def load_rows(batch: Batch, source: str, id_field: str) -> list[dict]:
    rows = []
    keys = batch.manifest()['files'][source].get('primary_key') or []
    for row in batch.rows(source):
        row = dict(row)
        if id_field == '_rowkey':
            row['_rowkey'] = ':'.join(str(row[key]) for key in keys)
        rows.append(row)
    return rows


class State:
    def __init__(self, data_dir: Path, defects: set[str], require_hash: bool):
        self.batch = Batch(data_dir)
        self.defects = defects
        self.require_hash = require_hash
        self.tables = {}
        for name, (source, id_field, quarantined) in DATASETS.items():
            rows = load_rows(self.batch, source, id_field)
            rules = {'source': source, 'id_field': id_field, 'quarantined': quarantined, 'rows': rows}
            if 'dedup_pairs' in defects and source.startswith('maps_npcs'):
                seen, unique = set(), []
                for row in rows:
                    pair = (row['scene_id'], row['npcid'])
                    if pair in seen:
                        continue
                    seen.add(pair)
                    unique.append(row)
                rules['rows'] = unique
            if 'zero_fill_missing' in defects and source == 'pet_aptitudes.csv':
                for missing in ('3010', '4021', '4022'):
                    rules['rows'].append({'client_shape_id': missing,
                                          **{k: '0' for k in rules['rows'][0] if '資質' in k},
                                          'source_entry': '2954'})
            if 'rewrite_2800' in defects and source == 'pet_aptitudes.csv':
                row = dict(rules['rows'][0])
                row.update({'client_shape_id': '2800'})
                for key in row:
                    if '資質' in key:
                        row[key] = '1700' if '最大' not in key else '1989'
                rules['rows'].append(row)
            if 'leak_quarantine' in defects:
                for key in quarantined:
                    if source == 'items.csv':
                        rules['rows'].append({'client_shape_id': key, 'name': 'LEAKED',
                                              'description_raw': '', 'category_code_raw': '0', 'image_id': '0',
                                              'image_mapping_explicit': 'false', 'source_entry': '1945',
                                              'source_table': 'DATA', 'review_status': 'review_candidate'})
                    elif source == 'pet_skills.csv':
                        rules['rows'].append({'skill_id': key, 'type_code_raw': '1', 'name': 'LEAKED',
                                              'description_raw': '', 'fpneed_raw': '0', 'mpneed_raw': '0',
                                              'hpneed_raw': '0', 'source_entry': '3205', 'source_table': 'DATA',
                                              'review_status': 'review_candidate'})
            if 'hide_ambiguous' in defects and source == 'pet_skill_name_matches.csv':
                keep, seen = [], set()
                for row in rules['rows']:
                    if row['skill_name_raw'] in ('高級命中', '終級命中'):
                        if row['skill_name_raw'] in seen:
                            continue
                        seen.add(row['skill_name_raw'])
                        row = dict(row, match_count='1', ambiguous='false')
                    keep.append(row)
                rules['rows'] = keep
            self.tables[name] = rules

    def ready(self) -> bool:
        """The double reports ready unless a defect makes it serve damaged data.

        ``serve_corrupt`` deliberately stays ready: the point of that fault is a
        service that keeps answering HTTP 200 with a damaged catalogue.
        """
        return True

    def integrity_error(self, table: str) -> str | None:
        if not self.require_hash or {'ignore_integrity', 'serve_corrupt'} & self.defects:
            return None
        spec = self.batch.manifest()['files'][self.tables[table]['source']]
        actual = hashlib.sha256((self.batch.root / self.tables[table]['source']).read_bytes()).hexdigest()
        if actual != spec['sha256']:
            return f'integrity failure: {self.tables[table]["source"]} does not match the manifest hash'
        return None

    def serialize(self, table: str, rows: list[dict]) -> list[dict]:
        if 'coerce_literals' not in self.defects:
            # The compliant mode converts per the manifest column types, exactly
            # as a correct catalogue reader must ("false" -> false, "" stays "").
            types = {c['name']: c['type']
                     for c in self.batch.manifest()['files'][self.tables[table]['source']]['columns']}
            output = []
            for row in rows:
                converted = {}
                for key, value in row.items():
                    kind = types.get(key)
                    try:
                        if kind == 'int' and value != '':
                            converted[key] = int(value)
                        elif kind == 'bool':
                            converted[key] = value == 'true'
                        elif kind == 'int_or_empty':
                            converted[key] = None if value == '' else int(value)
                        else:
                            converted[key] = value
                    except ValueError:
                        # Only reachable while injecting the type-corruption defect.
                        converted[key] = value
                output.append(converted)
            return output
        output = []
        for row in rows:
            converted = {}
            for key, value in row.items():
                if value == 'false':
                    converted[key] = 'false'
                elif value == '':
                    converted[key] = 'None'
                else:
                    converted[key] = value
            output.append(converted)
        return output


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    state: State
    map_path: str

    def log_message(self, *args):  # silence
        pass

    def _send(self, status: int, payload, *, content_type='application/json'):
        if isinstance(payload, (dict, list)):
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        elif isinstance(payload, bytes):
            body = payload
        else:
            body = str(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: int, message: str):
        self._send(status, {'error': {'code': status, 'message': message}})

    def _table(self):
        parsed = urllib.parse.urlparse(self.path)
        parts = [p for p in parsed.path.split('/') if p]
        if len(parts) < 4 or parts[:3] != ['api', 'v1', 'review']:
            return None, None, parsed
        if parts[3] == 'save' and 'mutation_route' in self.state.defects:
            return 'save', None, parsed
        if parts[3] != 'datasets' or len(parts) < 5 or parts[4] not in DATASETS:
            return None, None, parsed
        return parts[4], (parts[6] if len(parts) > 6 else None), parsed

    def do_GET(self):
        table, key, parsed = self._table()
        if table == 'save':
            return self._send(200, {'saved': True})
        if table is None:
            if parsed.path.rstrip('/') in ('/api/v1/review/health', '/health'):
                return self._health()
            if parsed.path.rstrip('/') in ('/api/v1/review', ''):
                return self._page()
            if 'traversal_allowed' in self.state.defects and 'passwd' in urllib.parse.unquote(self.path):
                return self._send(200, b'root:x:0:0:root:/root:/bin/bash\n', content_type='text/plain')
            return self._error(404, 'unknown endpoint')
        if self.state.integrity_error(table) and 'ignore_integrity' not in self.state.defects:
            return self._error(500, self.state.integrity_error(table))
        query = urllib.parse.parse_qs(parsed.query)
        unknown = set(query) - {'page', 'page_size', 'q', 'skill_name_raw'}
        if unknown and 'traversal_allowed' not in self.state.defects:
            return self._error(400, f'unsupported parameter(s): {sorted(unknown)}')
        rules = self.state.tables[table]
        rows = rules['rows']
        if 'search' in self.path:
            pass
        if 'q' in query:
            term = query['q'][0]
            rows = [r for r in rows if any(term in str(v) for v in r.values())]
        if table == 'pet_skill_name_matches' and 'skill_name_raw' in query:
            term = query['skill_name_raw'][0]
            rows = [r for r in rows if r['skill_name_raw'] == term]
        if key is not None:
            match = next((r for r in rows if str(r.get(rules['id_field'])) == key), None)
            if match is None:
                return self._error(404, f'no such row: {key}')
            return self._send(200, self.state.serialize(table, [match])[0])
        try:
            page = int(query.get('page', ['1'])[0])
            page_size = int(query.get('page_size', ['50'])[0])
            if page < 1 or page_size < 1:
                raise ValueError
        except ValueError:
            if 'silent_default_page' in self.state.defects:
                page, page_size = 1, 50
            else:
                return self._error(400, 'invalid page/page_size')
        if page_size > 500 and 'silent_default_page' not in self.state.defects:
            return self._error(400, 'page_size exceeds the documented maximum of 500')
        if 'unstable_order' in self.state.defects:
            rows = list(rows)
            for i in range(0, max(0, len(rows) - 1)):
                rows[i], rows[i + 1] = rows[i + 1], rows[i]
        total = len(rows)
        window = rows[(page - 1) * page_size: (page - 1) * page_size + page_size]
        self._send(200, {'rows': self.state.serialize(table, window), 'total': total,
                         'page': page, 'page_size': page_size})

    def _health(self):
        """Readiness endpoint the emitted map declares (the harness needs it)."""
        healthy = self.state.ready()
        self._send(200 if healthy else 503, {
            'status': 'ready' if healthy else 'degraded',
            'batch': 'batch_001',
            'datasets_count': len(self.state.tables),
            'note': 'self-check double, NOT the product API',
        })

    def _page(self):
        script = '<script src="app.js"></script>'
        if 'localhost_in_page' in self.state.defects:
            script = '<script>fetch("http://127.0.0.1:8100/api/v1/review/datasets/items");</script>'
        html = ('<!doctype html><html><head><meta charset="utf-8"><title>review</title></head>'
                f'<body><div id="app"></div>{script}</body></html>')
        self._send(200, html, content_type='text/html; charset=utf-8')

    def _mutate(self):
        table, key, _ = self._table()
        length = int(self.headers.get('Content-Length') or 0)
        if length:
            self.rfile.read(length)
        if 'accept_mutations' in self.state.defects and table in DATASETS:
            return self._send(200, {'updated': key or 'all'})
        self._error(405, 'this API is read-only')

    do_POST = do_PUT = do_PATCH = do_DELETE = _mutate


def emit_map(path: Path | None):
    mapping = {
        'label': 'harness self-check double (NOT the product API)',
        'base_path': '/api/v1/review/',
        'health_path': 'health',
        'page_url': '/api/v1/review/',
        'list_path': '/api/v1/review/datasets/{dataset}/rows',
        'detail_path': '/api/v1/review/datasets/{dataset}/rows/{key}',
        'list_params': {'page': 'page', 'page_size': 'page_size', 'q': 'q'},
        'datasets': {
            'items': {'source': 'items.csv', 'id': 'client_shape_id', 'api_name': 'items',
                      'search_term': '時空石', 'search_param': 'q', 'search_miss': 'zzz-none',
                      'search_expect_ids': [41052]},
            'pets': {'source': 'pets.csv', 'id': 'client_shape_id', 'api_name': 'pets'},
            'pet_aptitudes': {'source': 'pet_aptitudes.csv', 'id': 'client_shape_id',
                              'api_name': 'pet_aptitudes'},
            'pet_skills': {'source': 'pet_skills.csv', 'id': 'skill_id', 'api_name': 'pet_skills'},
            'pet_skill_name_matches': {'source': 'pet_skill_name_matches.csv', 'id': 'skill_id',
                                       'api_name': 'pet_skill_name_matches',
                                       'search_param': 'skill_name_raw'},
            'npcposdata': {'source': 'maps_npcs/npcposdata_records.csv', 'id': '_rowkey',
                           'api_name': 'npcposdata'},
            'minimapnpcpos': {'source': 'maps_npcs/minimapnpcpos_pos_records.csv', 'id': '_rowkey',
                              'api_name': 'minimapnpcpos'},
        },
        'pagination_datasets': ['items', 'pet_aptitudes', 'pet_skills'],
        'literal_probes': [
            {'dataset': 'items', 'key': 11, 'path': 'image_mapping_explicit', 'expect': 'false_bool'},
            {'dataset': 'npcposdata', 'key': '1001:0', 'path': 'secondary_name', 'expect': 'empty_str'},
        ],
        'integrity_datasets': ['items'],
    }
    text = json.dumps(mapping, ensure_ascii=False, indent=2)
    if path:
        path.write_text(text + '\n', encoding='utf-8')
        print(path)
    else:
        print(text)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--data-dir', type=Path, default=None)
    parser.add_argument('--port', type=int, default=0)
    parser.add_argument('--defects', default='all',
                        help='comma separated defect names, "all" or "none"')
    parser.add_argument('--require-hash', action='store_true',
                        help='refuse to serve datasets whose sha256 no longer matches the manifest')
    parser.add_argument('--emit-map', type=Path, default=None)
    parser.add_argument('--print-port', action='store_true')
    args = parser.parse_args(argv)
    if args.emit_map is not None or (args.emit_map is None and '--emit-map' in (argv or sys.argv)):
        return emit_map(args.emit_map)
    if args.defects == 'all':
        defects = set(ALL_DEFECTS)
    elif args.defects == 'none':
        defects = set()
    else:
        defects = {d.strip() for d in args.defects.split(',') if d.strip()}
        unknown = defects - set(ALL_DEFECTS)
        if unknown:
            parser.error(f'unknown defect(s): {sorted(unknown)}')
    data_dir = args.data_dir or Path(os.environ.get('REVIEW_BATCH_DIR') or default_batch_dir())
    Handler.state = State(data_dir, defects, args.require_hash)
    Handler.map_path = str(args.emit_map or '')
    server = ThreadingHTTPServer(('0.0.0.0', args.port), Handler)
    port = server.server_address[1]
    if args.print_port:
        print(json.dumps({'port': port}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
