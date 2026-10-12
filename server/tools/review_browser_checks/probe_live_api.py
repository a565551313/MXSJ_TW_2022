#!/usr/bin/env python3
"""Phase 2/3 acceptance probe for the review API (Agent H) and review web page (Agent I).

This is Agent J's independent acceptance harness. It does **not** implement or
propose the product API: it drives an already running (or freshly started)
instance of whatever Agent H/I deliver, using

* ``server/docs/review_browser/API_CONTRACT.md`` for discovery (base path,
  startup command, documented endpoints), and
* an explicit *operation map* (``--map``) that binds the documented endpoints to
  the required acceptance behaviours.

Until a mapping is supplied, every dynamic check reports ``not_executed`` with a
precise reason. Nothing is guessed and nothing is silently treated as passed.

Checks are the twelve API semantics plus the page-delivery rules required by the
acceptance brief (search/pagination/detail, parameter validation, literal types,
integrity failure handling, quarantine isolation, 2800/1700, missing aptitudes,
229/255, 329/355, NPC key semantics, traversal refusal, read-only catalogue,
absence of edit/save/upload/publish endpoints, proxy safety).

Usage:

    # against a running instance
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
        --base-url http://127.0.0.1:8100 --map ops.json --data-dir /tmp/batch-copy

    # start the documented command yourself with --start
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
        --start --command "python3 -m review_api --port {port}" --map ops.json

Standard library only.
"""
from __future__ import annotations

import argparse
import collections
import copy
import hashlib
import json
import os
import random
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from batch_fixture import (  # noqa: E402
    FIXED_EXPECTATIONS, Batch, default_batch_dir, repo_root, sha256_bytes, write_temp_batch,
)

CONTRACT_PATH = repo_root() / 'server/docs/review_browser/API_CONTRACT.md'
DEFAULT_BASE_PATH = '/api/v1/review/'

NOT_EXECUTED = 'not_executed'
PASS = 'pass'
FAIL = 'fail'


# --------------------------------------------------------------------------
# contract discovery
# --------------------------------------------------------------------------
class Contract:
    """Everything the harness learns from Agent H's contract document."""

    def __init__(self, path: Path = CONTRACT_PATH):
        self.path = Path(path)
        self.available = self.path.is_file()
        self.text = self.path.read_text(encoding='utf-8') if self.available else ''
        self.base_path = DEFAULT_BASE_PATH
        self.startup_commands: list[str] = []
        self.endpoints: list[tuple[str, str]] = []
        self.port_hint: int | None = None
        self.dataset_root_env: str | None = None
        if not self.available:
            return
        match = re.search(r'/api/v\d+/review/?', self.text)
        if match:
            self.base_path = match.group(0)
        for block in re.findall(r'```[a-zA-Z0-9_-]*\n(.*?)```', self.text, re.S):
            for line in block.splitlines():
                stripped = line.strip().lstrip('$ ').strip()
                if re.match(r'^(python3?|uvicorn|flask|gunicorn|node|npm)\b', stripped):
                    self.startup_commands.append(stripped)
        for method, path in re.findall(r'\b(GET|POST|PUT|PATCH|DELETE)\s+`?([^\s`|]+)', self.text, re.I):
            self.endpoints.append((method.upper(), path))
        port = re.search(r'(?:--port[= ]|PORT=)(\d{2,5})', self.text)
        if port:
            self.port_hint = int(port.group(1))
        env = re.search(r'\b([A-Z][A-Z0-9_]*(?:ROOT|DIR|DATA|BATCH|CSV)[A-Z0-9_]*)\b', self.text)
        if env:
            self.dataset_root_env = env.group(1)

    def summary(self) -> dict:
        return {
            'path': str(self.path.relative_to(repo_root())) if self.available else None,
            'available': self.available,
            'base_path': self.base_path,
            'startup_commands': self.startup_commands,
            'documented_endpoints': self.endpoints,
            'port_hint': self.port_hint,
            'dataset_root_env_hint': self.dataset_root_env,
        }


# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------
class Response:
    def __init__(self, status: int, headers, body: bytes):
        self.status = status
        self.headers = headers
        self.body = body

    @property
    def text(self) -> str:
        return self.body.decode('utf-8', 'replace')

    def json(self):
        try:
            return json.loads(self.body.decode('utf-8'))
        except Exception:  # noqa: BLE001
            return None


class Client:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def request(self, method: str, path: str, *, params: dict | None = None,
                headers: dict | None = None, body: bytes | None = None) -> Response:
        url = path if path.startswith('http') else f'{self.base_url}/{path.lstrip("/")}'
        if params:
            url = url + ('&' if '?' in url else '?') + urllib.parse.urlencode(params, doseq=True)
        request = urllib.request.Request(url, method=method, data=body)
        request.add_header('Accept', 'application/json, text/html;q=0.9, */*;q=0.1')
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as handle:
                return Response(handle.status, dict(handle.headers), handle.read())
        except urllib.error.HTTPError as error:
            return Response(error.code, dict(error.headers or {}), error.read())
        except urllib.error.URLError as error:
            raise ConnectionError(f'{method} {url}: {error}') from error

    def get(self, path: str, **kwargs) -> Response:
        return self.request('GET', path, **kwargs)


def norm(value) -> str:
    """Acceptance comparisons are string-based: JSON ints and CSV text compare equal."""
    return str(value)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


# --------------------------------------------------------------------------
# probe
# --------------------------------------------------------------------------
class Probe:
    """Runs the acceptance checks against one running instance."""

    def __init__(self, client: Client, mapping: dict, fixture: Path, contract: Contract,
                 integrity_runner=None):
        self.client = client
        self.mapping = mapping or {}
        self.fixture = Path(fixture)
        self.batch = Batch(self.fixture)
        self.contract = contract
        self.integrity_runner = integrity_runner
        self.integrity_skip_reason: str | None = None
        self.results: list[dict] = []

    # -- helpers ---------------------------------------------------------
    def record(self, check_id: str, title: str, status: str, detail, *, requirement: str = ''):
        self.results.append({'check': check_id, 'title': title, 'status': status,
                             'requirement': requirement, 'detail': detail})

    def not_executed(self, check_id: str, title: str, reason: str, requirement: str = ''):
        self.record(check_id, title, NOT_EXECUTED, reason, requirement=requirement)

    def dataset(self, name: str) -> dict | None:
        return (self.mapping.get('datasets') or {}).get(name)

    def list_url(self, name: str) -> str | None:
        spec = self.dataset(name)
        if not spec:
            return None
        template = spec.get('list_path') or self.mapping.get('list_path')
        return template.format(dataset=spec.get('api_name', name)) if template else None

    def detail_url(self, name: str, key) -> str | None:
        spec = self.dataset(name) or {}
        template = spec.get('detail_path') or self.mapping.get('detail_path')
        if not template:
            return None
        return template.format(dataset=spec.get('api_name', name), key=key)

    def list_params(self) -> dict:
        return self.mapping.get('list_params') or {'page': 'page', 'page_size': 'page_size', 'q': 'q'}

    def response_keys(self) -> dict:
        spec = self.mapping.get('list_response') or {}
        return {'rows': spec.get('rows', 'rows'), 'total': spec.get('total', 'total')}

    @staticmethod
    def rows_of(payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            for key in ('rows', 'items', 'records', 'data', 'results'):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        return None

    def fetch_all(self, name: str, page_size: int = 200, extra: dict | None = None) -> tuple[list, list]:
        """Walk every page of a list endpoint; returns (rows, per_page_counts)."""
        url = self.list_url(name)
        if not url:
            raise LookupError(f'no list endpoint mapped for dataset {name!r}')
        params = self.list_params()
        id_field = (self.dataset(name) or {}).get('id', 'id')
        rows: list = []
        counts: list[int] = []
        for page in range(1, 200):
            query = {params['page']: page, params['page_size']: page_size, **(extra or {})}
            response = self.client.get(url, params=query)
            if response.status != 200:
                raise LookupError(f'{url} page {page} returned HTTP {response.status}')
            payload = response.json()
            page_rows = self.rows_of(payload)
            if page_rows is None:
                # Some servers return the plain list without the documented envelope.
                if isinstance(payload, list):
                    page_rows = payload
                else:
                    raise LookupError(f'{url} page {page} did not return a row list')
            counts.append(len(page_rows))
            for row in page_rows:
                if id_field not in row:
                    raise LookupError(f'{url}: row is missing id field {id_field!r}')
                rows.append(norm(row[id_field]))
            if len(page_rows) < page_size:
                break
        return rows, counts

    def expected_ids(self, source: str, id_field: str) -> list:
        """Row identifiers as the API must expose them.

        ``_rowkey`` is the harness convention for a composite key: it is built
        from the manifest primary key of the CSV in declaration order.
        """
        rows = self.batch.rows(source)
        if id_field.startswith('_'):
            keys = self.batch.manifest()['files'][source]['primary_key']
            return [':'.join(norm(row[key]) for key in keys) for row in rows]
        return [norm(row[id_field]) for row in rows]

    # -- checks ----------------------------------------------------------
    REQUIRED = 'required'

    def check_pagination(self):
        check_id, title = 'API-01', 'pagination is complete, duplicate-free and stably ordered'
        if not self.mapping.get('datasets'):
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        for name in self.mapping.get('pagination_datasets') or list(self.mapping['datasets']):
            spec = self.dataset(name) or {}
            if not spec.get('source'):
                self.not_executed(f'{check_id}.{name}', title, f'dataset {name!r} has no CSV source mapping')
                continue
            try:
                first, counts = self.fetch_all(name)
                second, _ = self.fetch_all(name)
            except LookupError as exc:
                self.record(f'{check_id}.{name}', title, FAIL, str(exc))
                continue
            expected = self.expected_ids(spec['source'], spec.get('id', 'id'))
            if len(counts) > 1:
                if counts[-1] != 0 and len(counts[-1:]) and counts[-1] == counts[0]:
                    pass  # full final page is allowed
            problems = []
            if len(first) != len(expected):
                problems.append(f'paged rows {len(first)} != CSV rows {len(expected)}')
            if collections.Counter(first) != collections.Counter(expected):
                missing = collections.Counter(expected) - collections.Counter(first)
                extra = collections.Counter(first) - collections.Counter(expected)
                problems.append(f'row multiset differs (missing={sum(missing.values())}, extra={sum(extra.values())})')
            if first != second:
                problems.append('order is not stable between two identical walks')
            self.record(f'{check_id}.{name}', title, FAIL if problems else PASS,
                        problems or {'rows': len(first), 'pages': len(counts), 'page_size_used': 200},
                        requirement=self.REQUIRED)

    def check_search_and_exact_filter(self):
        check_id, title = 'API-02', 'search and exact filters follow the contract'
        datasets = self.mapping.get('datasets') or {}
        if not datasets:
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        problems, details = [], {}
        for name, spec in datasets.items():
            term = spec.get('search_term')
            if not term or not spec.get('search_param'):
                continue
            url = self.list_url(name)
            response = self.client.get(url, params={spec['search_param']: term,
                                                    self.list_params()['page_size']: 50})
            if response.status != 200:
                problems.append(f'{name}: search HTTP {response.status}')
                continue
            rows = self.rows_of(response.json()) or []
            wanted = spec.get('search_expect_ids')
            got = sorted(norm(row.get(spec.get('id', 'id'))) for row in rows)
            details[name] = {'term': term, 'ids': got}
            if wanted is not None and got != sorted(norm(item) for item in wanted):
                problems.append(f'{name}: search {term!r} returned {got}, expected {sorted(wanted)}')
            empty = self.client.get(url, params={spec['search_param']: spec.get('search_miss', 'zzz-no-such-name'),
                                                 self.list_params()['page_size']: 50})
            if empty.status == 200:
                rows = self.rows_of(empty.json()) or []
                if rows:
                    problems.append(f'{name}: a guaranteed-miss search returned {len(rows)} rows')
            elif empty.status >= 500:
                problems.append(f'{name}: guaranteed-miss search raised HTTP {empty.status}')
        if not details:
            return self.not_executed(check_id, title, 'no dataset declares search_term/search_param')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_invalid_parameters(self):
        check_id, title = 'API-03', 'invalid parameters produce explicit errors, never silent substitution'
        datasets = self.mapping.get('datasets') or {}
        if not datasets:
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        params = self.list_params()
        cases = [
            {params['page']: 'abc'},
            {params['page']: '-1'},
            {params['page']: '0'},
            {params['page_size']: '0'},
            {params['page_size']: 'abc'},
            {params['page_size']: str(10 ** 7)},
        ]
        problems, details = [], {}
        for name in list(datasets)[:2]:
            url = self.list_url(name)
            baseline = self.client.get(url, params={params['page_size']: 5})
            if baseline.status != 200:
                problems.append(f'{name}: baseline request HTTP {baseline.status}')
                continue
            for case in cases:
                response = self.client.get(url, params=case)
                key = f'{name}:{case}'
                details[key] = response.status
                if response.status < 400:
                    payload = response.json()
                    rows = self.rows_of(payload) or []
                    if not isinstance(payload, dict) or not any(
                            word in json.dumps(payload, ensure_ascii=False).lower()
                            for word in ('error', 'invalid', 'clamp', 'adjusted', 'ignored')):
                        problems.append(f'{name}: {case} accepted silently with HTTP {response.status} '
                                        f'({len(rows)} rows, no explanation in the body)')
                elif response.status >= 500:
                    problems.append(f'{name}: {case} produced a server error HTTP {response.status}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_literal_values(self):
        check_id, title = 'API-04', '"false", empty text and missing values are not coerced'
        if not self.mapping.get('literal_probes'):
            return self.not_executed(
                check_id, title,
                'no literal_probes mapping (needs the contract to state which row/field carries '
                'a boolean false, an empty string and an absent field)')
        problems, details = [], {}
        for probe in self.mapping['literal_probes']:
            url = self.detail_url(probe['dataset'], probe['key'])
            response = self.client.get(url)
            details[f'{probe["dataset"]}/{probe["key"]}'] = response.status
            if response.status != 200:
                problems.append(f'{probe["dataset"]}/{probe["key"]}: HTTP {response.status}')
                continue
            payload = response.json()
            value = payload
            for part in probe['path'].split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    value = '<absent>'
                    break
            if value == '<absent>':
                problems.append(f'{probe["dataset"]}/{probe["key"]}: field {probe["path"]} is missing')
                continue
            if probe.get('expect') == 'false_bool' and value is not False:
                problems.append(f'{probe["dataset"]}/{probe["key"]}: {probe["path"]}={value!r} is not JSON false')
            if probe.get('expect') == 'empty_str' and value != '':
                problems.append(f'{probe["dataset"]}/{probe["key"]}: {probe["path"]}={value!r} is not an empty string')
            if probe.get('expect') == 'null' and value is not None:
                problems.append(f'{probe["dataset"]}/{probe["key"]}: {probe["path"]}={value!r} is not null/absent')
            details[probe['path']] = value
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_integrity_failure(self):
        check_id, title = 'API-05', 'hash/type validation failure does not keep serving a normal catalogue'
        datasets = self.mapping.get('integrity_datasets')
        if not datasets:
            return self.not_executed(check_id, title, 'no integrity_datasets mapping (contract not delivered)')
        if self.integrity_runner is None:
            return self.not_executed(check_id, title, self.integrity_skip_reason or (
                'launch-based check: needs --start with a startup command so the harness can restart the '
                'server on a corrupted copy of the batch (an external --base-url cannot be corrupted safely)'))
        observations = self.integrity_runner(datasets)
        problems, details = [], observations
        for name, variants in observations.items():
            spec = self.dataset(name) or {}
            expected = len(self.batch.rows(spec['source'])) if spec.get('source') else None
            for kind, result in variants.items():
                status = result.get('status')
                rows = result.get('rows')
                message = json.dumps(result.get('payload'), ensure_ascii=False)[:200]
                if status is None and not result.get('refused'):
                    problems.append(f'{name}/{kind}: server did not become reachable on the corrupted copy')
                elif status < 400:
                    if rows == expected:
                        problems.append(f'{name}/{kind}: corrupted {spec.get("source")} still served all '
                                        f'{rows} rows with HTTP {status} (pseudo-normal catalogue)')
                    elif not re.search(r'error|invalid|integrity|hash|mismatch|refus', message, re.I):
                        problems.append(f'{name}/{kind}: HTTP {status} without an explicit error message '
                                        f'({message})')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_quarantine_isolation(self):
        check_id, title = 'API-06', 'quarantined records never enter the normal lists'
        datasets = self.mapping.get('datasets') or {}
        if not datasets:
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        wanted = {'items': {'72548'}, 'pet_aptitudes': {'2800'}, 'pet_skills': {'719', '4406'}}
        problems, details = [], {}
        for name, spec in datasets.items():
            source = spec.get('source')
            if not source:
                continue
            id_field = spec.get('id', 'id')
            try:
                rows, _ = self.fetch_all(name)
            except LookupError as exc:
                problems.append(str(exc))
                continue
            delivered = set(rows)
            csv_ids = set(self.expected_ids(source, id_field))
            quarantined_here = wanted.get(name, set())
            leaked = delivered & quarantined_here
            if leaked:
                problems.append(f'{name}: quarantined ids {sorted(leaked)} are served in the normal list')
            if not delivered >= csv_ids:
                problems.append(f'{name}: {len(csv_ids - delivered)} reviewed rows are missing from the API')
            unexpected = delivered - (csv_ids | quarantined_here)
            if unexpected:
                problems.append(f'{name}: {len(unexpected)} rows are not in the reviewed CSV: '
                                f'{sorted(unexpected)[:5]}')
            details[name] = {'rows': len(delivered)}
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_2800_not_1700(self):
        check_id, title = 'API-07', 'aptitude 2800 is never rewritten to the unapproved 1700'
        if not self.mapping.get('datasets'):
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        problems, details = [], {}
        for name, spec in (self.mapping.get('datasets') or {}).items():
            if spec.get('source') != 'pet_aptitudes.csv':
                continue
            url = self.detail_url(name, 2800)
            response = self.client.get(url)
            details['detail_2800'] = response.status
            if response.status < 300:
                problems.append('aptitude 2800 is served as a normal row although it is quarantined')
            try:
                rows, _ = self.fetch_all(name)
            except LookupError as exc:
                problems.append(str(exc))
                continue
            if '2800' in set(rows):
                problems.append('aptitude 2800 appears in the normal list')
        if 'detail_2800' not in details:
            return self.not_executed(check_id, title, 'no dataset mapped to pet_aptitudes.csv')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_missing_aptitudes(self):
        check_id, title = 'API-08', 'missing aptitudes (3010/4021/4022) are not zero-filled'
        datasets = self.mapping.get('datasets') or {}
        if not datasets:
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        problems, details = [], {}
        for name, spec in datasets.items():
            if spec.get('source') != 'pet_aptitudes.csv':
                continue
            try:
                rows, _ = self.fetch_all(name)
            except LookupError as exc:
                problems.append(str(exc))
                continue
            for missing in FIXED_EXPECTATIONS['missing_aptitude_ids']:
                if norm(missing) in set(rows):
                    detail = self.client.get(self.detail_url(name, missing))
                    if detail.status < 300:
                        payload = detail.json() or {}
                        zeroed = all(str(value) in ('0', '0.0') for key, value in payload.items()
                                     if isinstance(value, int) and key.endswith('資質'))
                        problems.append(f'missing aptitude {missing} is served as a normal row'
                                        + (' (all-zero values)' if zeroed else ''))
            details[name] = {'rows': len(rows)}
        if not details:
            return self.not_executed(check_id, title, 'no dataset mapped to pet_aptitudes.csv')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_ambiguous_names(self):
        for check_id, name, ids in (('API-09', '高級命中', [229, 255]), ('API-10', '終級命中', [329, 355])):
            title = f'same-name skill {name} keeps every candidate id {ids}'
            matches = [key for key, spec in (self.mapping.get('datasets') or {}).items()
                       if spec.get('source') == 'pet_skill_name_matches.csv']
            if not matches:
                self.not_executed(check_id, title, 'no dataset mapped to pet_skill_name_matches.csv')
                continue
            dataset = matches[0]
            spec = self.dataset(dataset)
            search_param = spec.get('search_param') or self.list_params().get('q')
            url = self.list_url(dataset)
            response = self.client.get(url, params={search_param: name, self.list_params()['page_size']: 50})
            if response.status != 200:
                self.record(check_id, title, FAIL, f'HTTP {response.status} for search {name!r}')
                continue
            rows = self.rows_of(response.json()) or []
            got = sorted(norm(row.get(spec.get('id'))) for row in rows)
            expected = sorted(norm(item) for item in ids)
            problems = []
            if got != expected:
                problems.append(f'{dataset}: search {name!r} returned ids {got}, expected {expected}')
            for row in rows:
                if str(row.get('match_count')) not in (None, '2', 2):
                    problems.append(f'{dataset}: match_count {row.get("match_count")!r} for {name!r}')
                if 'ambiguous' in row and row['ambiguous'] not in (True, 'true'):
                    problems.append(f'{dataset}: ambiguous flag {row.get("ambiguous")!r} for {name!r}')
            self.record(check_id, title, FAIL if problems else PASS, problems or {'ids': got},
                        requirement=self.REQUIRED)

    def check_npc_keys(self):
        check_id, title = 'API-11', 'NPC records are not deduplicated by (scene_id, npcid)'
        npc_datasets = [(name, spec) for name, spec in (self.mapping.get('datasets') or {}).items()
                        if spec.get('source') in ('maps_npcs/npcposdata_records.csv',
                                                  'maps_npcs/minimapnpcpos_pos_records.csv')]
        if not npc_datasets:
            return self.not_executed(check_id, title, 'no dataset mapped to the two NPC sources')
        problems, details = [], {}
        for name, spec in npc_datasets:
            source = spec['source']
            id_field = spec.get('id', '_rowkey')
            try:
                rows, counts = self.fetch_all(name)
            except LookupError as exc:
                problems.append(str(exc))
                continue
            expected = self.expected_ids(source, id_field)
            csv_rows = self.batch.rows(source)
            primary_key = self.batch.manifest()['files'][source]['primary_key']
            zero_keys = [':'.join(norm(row[key]) for key in primary_key)
                         for row in csv_rows if row['npcid'] == '0']
            missing = collections.Counter(expected) - collections.Counter(rows)
            extra = collections.Counter(rows) - collections.Counter(expected)
            if missing or extra:
                problems.append(f'{source}: delivered row keys differ from the CSV '
                                f'(missing={sum(missing.values())}, extra={sum(extra.values())}) — '
                                'records may have been collapsed by (scene_id, npcid)')
            if not set(zero_keys) <= set(rows):
                problems.append(f'{source}: NPC ID 0 rows are missing from the API '
                                f'({len(set(zero_keys) - set(rows))} dropped)')
            # Duplicate (scene_id, npcid) groups must still be visible as separate rows.
            repeated = {pair for pair, count in collections.Counter(
                (r['scene_id'], r['npcid']) for r in csv_rows).items() if count > 1}
            if not repeated:
                problems.append(f'{source}: the CSV no longer contains duplicate (scene_id, npcid) groups')
            if rows != expected:
                problems.append(f'{source}: page order differs from the CSV order')
            details[source] = {'rows': len(rows), 'csv_rows': len(csv_rows), 'pages': len(counts),
                               'zero_id_rows': len(zero_keys), 'duplicate_groups': len(repeated)}
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_traversal(self):
        check_id, title = 'API-12', 'illegal datasets, path traversal and arbitrary file reads are refused'
        if not self.mapping.get('datasets'):
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        name = next(iter(self.mapping['datasets']))
        probes = [
            ('../' * 6 + 'etc/passwd', {}),
            ('..%2f' * 6 + 'etc%2fpasswd', {}),
            ('../../data/script.fls', {}),
            ('%2e%2e%2f%2e%2e%2fdata%2fscript.fls', {}),
            (name, {'file': '/etc/passwd'}),
            (name, {'path': '../../data/script.fls'}),
            (name, {'dataset': '../../data/script.fls'}),
        ]
        problems, details = [], {}
        for dataset, extra in probes:
            url = self.list_url(name).replace(
                (self.dataset(name) or {}).get('api_name', name), urllib.parse.quote(str(dataset), safe=''))
            response = self.client.get(url, params={self.list_params()['page_size']: 5, **extra})
            details[str(dataset) + str(extra)] = response.status
            body = response.body
            if response.status < 400:
                problems.append(f'{dataset} {extra}: accepted with HTTP {response.status}')
            if b'root:' in body or b'FLS' in body or b'PK\x03\x04' in body:
                problems.append(f'{dataset} {extra}: response body leaked file content')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_read_only(self):
        check_id, title = 'API-13', 'callers cannot modify the underlying catalogue'
        if not self.mapping.get('datasets'):
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        before = {path.relative_to(self.fixture).as_posix(): sha256_bytes(path.read_bytes())
                  for path in self.fixture.rglob('*') if path.is_file()}
        name = next(iter(self.mapping['datasets']))
        urls = [self.list_url(name), self.detail_url(name, 11) or self.list_url(name)]
        problems, details = [], {}
        for url in urls:
            for method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                payload = json.dumps({'name': 'tampered', 'description_raw': 'tampered'}).encode()
                response = self.client.request(method, url, body=payload,
                                               headers={'Content-Type': 'application/json'})
                details[f'{method} {url}'] = response.status
                if response.status < 400:
                    problems.append(f'{method} {url} was accepted with HTTP {response.status}')
        after = {path.relative_to(self.fixture).as_posix(): sha256_bytes(path.read_bytes())
                 for path in self.fixture.rglob('*') if path.is_file()}
        changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
        if changed:
            problems.append(f'fixture files changed during the attempt: {changed}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_no_mutation_endpoints(self):
        check_id, title = 'API-14', 'no edit/save/upload/publish endpoints exist'
        if not self.mapping.get('datasets'):
            return self.not_executed(check_id, title, 'no dataset mapping supplied (contract not delivered)')
        suspicious = ['save', 'edit', 'update', 'upload', 'publish', 'import', 'commit', 'write',
                      'delete', 'delete_row', 'create', 'reload', 'refresh', 'rebuild', 'export']
        problems, details = [], {}
        for name in suspicious:
            for url in (f'{self.contract.base_path.rstrip("/")}/{name}',
                        f'{self.list_url(next(iter(self.mapping["datasets"])))}/{name}'):
                response = self.client.request('POST', url, body=b'{}',
                                               headers={'Content-Type': 'application/json'})
                details[f'POST {url}'] = response.status
                if response.status < 400:
                    problems.append(f'POST {url} accepted with HTTP {response.status}')
        documented = [entry for entry in self.contract.endpoints
                      if entry[0] in ('POST', 'PUT', 'PATCH', 'DELETE')]
        if documented:
            problems.append(f'the contract itself documents mutating endpoints: {documented}')
        scanned = self.scan_source_for_mutating_routes()
        details['static_routes'] = scanned
        if scanned.get('mutating_routes'):
            problems.append(f'mutating routes found in the implementation source: {scanned["mutating_routes"]}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def scan_source_for_mutating_routes(self) -> dict:
        """Best-effort static scan of Agent H's implementation for mutating routes."""
        roots = [path for path in (
            repo_root() / 'server/apps', repo_root() / 'server/src/review', repo_root() / 'server/src/review_api',
        ) if path.exists()]
        pattern = re.compile(
            r'(\.(?:post|put|patch|delete)\s*\(|methods\s*=\s*\[[^\]]*[\'"](?:POST|PUT|PATCH|DELETE)|'
            r'[\'"](?:/|\w)*(?:save|upload|publish|edit|update|delete)[\'"])', re.I)
        hits = []
        files = 0
        for root in roots:
            for path in sorted(root.rglob('*.py')) + sorted(root.rglob('*.js')) + sorted(root.rglob('*.ts')):
                files += 1
                for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
                    if pattern.search(line):
                        hits.append({'file': path.relative_to(repo_root()).as_posix(),
                                     'line': number, 'text': line.strip()[:160]})
        return {'files': files, 'roots': [str(root.relative_to(repo_root())) for root in roots],
                'mutating_routes': hits}

    def check_proxy_safety(self):
        check_id, title = 'API-15', 'page works behind the preview proxy and never targets sandbox localhost'
        page = self.mapping.get('page_url') or self.contract.base_path
        problems, details = [], {}
        response = self.client.get(page)
        details['page_status'] = response.status
        if response.status != 200:
            problems.append(f'page {page} returned HTTP {response.status}')
        body = response.text
        for needle in ('localhost', '127.0.0.1', '0.0.0.0'):
            if needle in body:
                problems.append(f'served page contains {needle!r} (browser must use relative URLs)')
        assets = re.findall(r'<script[^>]+src=["\']([^"\']+)', body) + \
                 re.findall(r'<link[^>]+href=["\']([^"\']+)', body)
        for asset in assets:
            if re.match(r'^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)', asset):
                problems.append(f'absolute sandbox URL in page asset: {asset}')
        if response.status == 200:
            proxied = self.client.get(page, headers={
                'Host': 'review-preview.example.invalid',
                'Origin': 'https://review-preview.e2b.app',
                'X-Forwarded-Proto': 'https',
            })
            details['host_override_status'] = proxied.status
            if proxied.status >= 400:
                problems.append(f'the app rejects a proxied Host/Origin with HTTP {proxied.status}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    # -- driver ----------------------------------------------------------
    def run(self) -> dict:
        for check in (self.check_pagination,
                      self.check_search_and_exact_filter,
                      self.check_invalid_parameters,
                      self.check_literal_values,
                      self.check_integrity_failure,
                      self.check_quarantine_isolation,
                      self.check_2800_not_1700,
                      self.check_missing_aptitudes,
                      self.check_ambiguous_names,
                      self.check_npc_keys,
                      self.check_traversal,
                      self.check_read_only,
                      self.check_no_mutation_endpoints,
                      self.check_proxy_safety):
            try:
                check()
            except ConnectionError as exc:
                self.record(check.__name__, check.__name__, NOT_EXECUTED, f'server unreachable: {exc}')
            except Exception as exc:  # noqa: BLE001 - acceptance report
                self.record(check.__name__, check.__name__, FAIL, f'{type(exc).__name__}: {exc}')
        failed = [r for r in self.results if r['status'] == FAIL]
        executed = [r for r in self.results if r['status'] in (PASS, FAIL)]
        missing = [r for r in self.results if r['status'] == NOT_EXECUTED]
        if failed:
            status = 'fail'
        elif missing:
            # A required check that could not be executed must never look green.
            status = 'incomplete'
        elif executed:
            status = 'pass'
        else:
            status = NOT_EXECUTED
        return {
            'stage': 'phase2_phase3_api_and_page',
            'contract': self.contract.summary(),
            'checks': self.results,
            'summary': {
                'total': len(self.results),
                'pass': sum(1 for r in self.results if r['status'] == PASS),
                'fail': len(failed),
                'not_executed': sum(1 for r in self.results if r['status'] == NOT_EXECUTED),
                'executed': len(executed),
            },
            'status': status,
            'status_meaning': {
                'pass': 'every required check executed and passed',
                'fail': 'at least one required check failed',
                'incomplete': 'no failure, but some required checks could not be executed',
                'not_executed': 'nothing could be executed',
            }[status],
        }


# --------------------------------------------------------------------------
# process management
# --------------------------------------------------------------------------
class StartedServer:
    def __init__(self, command: list[str], port: int, env: dict, log_path: Path):
        self.command = command
        self.port = port
        self.env = env
        self.log_path = log_path
        self.process: subprocess.Popen | None = None

    def __enter__(self):
        log = self.log_path.open('wb')
        self.process = subprocess.Popen(self.command, stdout=log, stderr=subprocess.STDOUT,
                                        env=self.env, start_new_session=True)
        return self

    def wait(self, path: str, timeout: float = 30.0) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.process.poll() is not None:
                return False
            try:
                with socket.create_connection(('127.0.0.1', self.port), timeout=0.5):
                    pass
            except OSError:
                time.sleep(0.2)
                continue
            try:
                client = Client(f'http://127.0.0.1:{self.port}')
                if client.get(path).status < 500:
                    return True
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.2)
        return False

    def __exit__(self, *exc):
        if self.process and self.process.poll() is None:
            try:
                os.killpg(self.process.pid, signal.SIGTERM)
                self.process.wait(timeout=10)
            except Exception:  # noqa: BLE001
                try:
                    os.killpg(self.process.pid, signal.SIGKILL)
                except Exception:  # noqa: BLE001
                    pass
        return False


# --------------------------------------------------------------------------
class IntegrityRunner:
    """Restart the candidate server on deliberately corrupted copies of the batch.

    Variants: a single byte flip inside the CSV (hash mismatch) and a type
    corruption in the id column (type/contract mismatch). Both copies are
    scratch copies; the committed batch is never touched.
    """

    def __init__(self, command: str, env: dict, dataset_root_env: str, base_path: str,
                 mapping: dict, scratch: Path, ready_path: str, source_dir: Path,
                 timeout: float = 30.0):
        self.command = command
        self.env = env
        self.dataset_root_env = dataset_root_env
        self.base_path = base_path.strip('/')
        self.mapping = mapping
        self.scratch = Path(scratch)
        self.ready_path = ready_path
        self.source_dir = Path(source_dir)
        self.timeout = timeout

    def _corrupt(self, target: Path, source: str, kind: str) -> Path:
        destination = target / kind
        copy = write_temp_batch(destination, self.source_dir)
        path = copy / source
        data = bytearray(path.read_bytes())
        if kind == 'hash':
            index = data.find(b',') + 1
            while index < len(data) and data[index:index + 1] in (b'"', b' '):
                index += 1
            data[index] = ord('X') if data[index] != ord('X') else ord('Y')
        else:
            text = data.decode('utf-8')
            lines = text.split('\n')
            fields = next(_csv_split(lines[1])) if len(lines) > 1 else []
            if fields:
                fields[0] = 'not-an-integer'
                lines[1] = '"' + '","'.join(fields) + '"'
            data = bytearray('\n'.join(lines).encode('utf-8'))
        path.write_bytes(bytes(data))
        return copy

    def __call__(self, datasets: list[str]) -> dict:
        observations: dict[str, dict] = {}
        for name in datasets:
            spec = self.mapping['datasets'].get(name) or {}
            observations[name] = {}
            if not spec.get('source'):
                continue
            for kind in ('hash', 'type'):
                copy = self._corrupt(self.scratch / f'{name}-{kind}', spec['source'], kind)
                env = dict(self.env)
                env[self.dataset_root_env] = str(copy)
                port = free_port()
                command = [part.replace('{port}', str(port)) for part in self.command.split()]
                env['PORT'] = str(port)
                with StartedServer(command, port, env, self.scratch / f'corrupt-{kind}.log') as server:
                    ready = server.wait(self.ready_path, timeout=self.timeout)
                    result = {'status': None, 'rows': None, 'payload': None}
                    if ready:
                        client = Client(f'http://127.0.0.1:{port}')
                        url = (spec.get('list_path') or self.mapping.get('list_path')).format(
                            dataset=spec.get('api_name', name))
                        try:
                            response = client.get(url, params={'page_size': 5})
                        except ConnectionError as exc:
                            # Refusing to answer also prevents a pseudo-normal catalogue.
                            observations[name][kind] = {'status': None, 'rows': 0, 'payload': str(exc),
                                                        'refused': True}
                            continue
                        payload = response.json()
                        rows = None
                        if isinstance(payload, dict) and isinstance(payload.get('rows'), list):
                            rows = len(payload['rows'])
                        result = {'status': response.status, 'rows': rows, 'payload': payload}
                    observations[name][kind] = result
        return observations


def _csv_split(line: str):
    import csv as _csv
    import io as _io
    return _csv.reader(_io.StringIO(line))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base-url', help='already running instance, e.g. http://127.0.0.1:8100')
    parser.add_argument('--start', action='store_true', help='start the server from --command/contract')
    parser.add_argument('--command', help='startup command ({port} placeholder supported)')
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--dataset-root-env', default=None,
                        help='environment variable that points the server at the batch directory')
    parser.add_argument('--data-dir', type=Path, default=None,
                        help='batch directory to serve (default: a scratch copy of batch_001)')
    parser.add_argument('--map', type=Path, default=None, help='operation map JSON')
    parser.add_argument('--contract', type=Path, default=CONTRACT_PATH)
    parser.add_argument('--health-path', default=None, help='readiness probe path')
    parser.add_argument('--out', type=Path, default=None)
    args = parser.parse_args(argv)

    contract = Contract(args.contract)
    mapping = json.loads(args.map.read_text(encoding='utf-8')) if args.map else {}

    scratch = None
    if args.start:
        scratch = Path(tempfile.mkdtemp(prefix='mxsj-review-fixture-'))
        fixture = write_temp_batch(scratch / 'batch', args.data_dir or default_batch_dir())
    else:
        fixture = args.data_dir or default_batch_dir()

    started = None
    base_url = args.base_url
    integrity_runner = None
    integrity_skip_reason = None
    try:
        if args.start:
            command = args.command or (contract.startup_commands[0] if contract.startup_commands else None)
            if not command:
                print(json.dumps({'status': NOT_EXECUTED,
                                  'reason': 'no startup command: pass --command or deliver API_CONTRACT.md'},
                                 ensure_ascii=False))
                return 3
            port = args.port or contract.port_hint or free_port()
            command_template = command  # keeps the {port} placeholder for restart-based checks
            command = command.replace('{port}', str(port))
            env = dict(os.environ)
            env['PORT'] = str(port)
            root_env = args.dataset_root_env or contract.dataset_root_env
            if root_env:
                env[root_env] = str(fixture)
            started = StartedServer(command.split(), port, env, scratch / 'server.log')
            started.__enter__()
            health = args.health_path or (mapping.get('health_path') or 'health')
            ready_path = f'/{contract.base_path.strip("/")}/{str(health).strip("/")}'
            if not started.wait(ready_path):
                print(json.dumps({'status': NOT_EXECUTED,
                                  'reason': f'server did not become ready; see {started.log_path}',
                                  'command': command}, ensure_ascii=False))
                return 4
            base_url = f'http://127.0.0.1:{port}'
            if mapping.get('integrity_datasets'):
                if root_env:
                    integrity_runner = IntegrityRunner(command_template, dict(env), root_env,
                                                       contract.base_path, mapping, scratch, ready_path,
                                                       fixture)
                else:
                    integrity_skip_reason = (
                        'the startup command is known but no dataset-root environment variable is declared '
                        'in API_CONTRACT.md (pass --dataset-root-env), so the harness cannot point the '
                        'server at a corrupted copy')

        if not base_url:
            report = {'stage': 'phase2_phase3_api_and_page', 'contract': contract.summary(),
                      'checks': [], 'status': NOT_EXECUTED,
                      'summary': {'total': 0, 'pass': 0, 'fail': 0, 'not_executed': 0, 'executed': 0},
                      'reason': 'no --base-url and no --start: nothing was executed'}
        else:
            probe = Probe(Client(base_url), mapping, fixture, contract, integrity_runner=integrity_runner)
            probe.integrity_skip_reason = integrity_skip_reason
            report = probe.run()
    finally:
        if started:
            started.__exit__(None, None, None)
        if scratch and args.data_dir is None:
            shutil.rmtree(scratch, ignore_errors=True)

    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
    print(text)
    if report['status'] in (NOT_EXECUTED, 'incomplete'):
        return 3
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
