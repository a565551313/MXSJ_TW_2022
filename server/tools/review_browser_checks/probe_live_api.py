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
import io
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
        for method, path in re.findall(r'\b(GET|POST|PUT|PATCH|DELETE)\s+`?(/[^\s`|,)]*)', self.text, re.I):
            self.endpoints.append((method.upper(), path))
        port = re.search(r'(?:--port[= ]|PORT=)(\d{2,5})', self.text)
        if port:
            self.port_hint = int(port.group(1))
        env = re.search(r'\b([A-Z][A-Z0-9_]*(?:ROOT|DIR|DATA|BATCH|CSV)[A-Z0-9_]*)\b', self.text)
        if env:
            self.dataset_root_env = env.group(1)

    NEGATION_MARKERS = ('无', '無', '没有', '不', 'not ', "n't", 'never', 'forbid', '禁止',
                        'no ', 'only', '只能是', 'read-only', 'readonly')

    def mutating_route_declarations(self) -> list[tuple[str, str]]:
        """Mutating endpoints the contract *declares* as available.

        A line that forbids writes ("无任何 POST / PUT / PATCH / DELETE 变更接口",
        "must not implement POST ...") documents the absence of write routes; it
        is not a declaration. Only a real path-shaped method + path pair on a
        non-negated line counts.
        """
        declarations = []
        for line in self.text.splitlines():
            stripped = line.strip()
            if any(marker in stripped.lower() for marker in self.NEGATION_MARKERS):
                continue
            for method, path in re.findall(r'\b(POST|PUT|PATCH|DELETE)\b\s*`?(/[A-Za-z0-9_{}/.\-]*)',
                                           stripped):
                declarations.append((method.upper(), path))
        return declarations

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
                 integrity_runner=None, out_dir: Path | None = None):
        self.client = client
        self.out_dir = Path(out_dir) if out_dir else Path(tempfile.gettempdir()) / 'mxsj-review-probe'
        self.mapping = mapping or {}
        self.fixture = Path(fixture)
        self.batch = Batch(self.fixture)
        self.contract = contract
        self.integrity_runner = integrity_runner
        self.integrity_skip_reason: str | None = None
        self.web_url: str | None = (mapping or {}).get('web_url')
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
        """Pagination parameter names as declared by the mapping.

        Offset-style (`offset`/`limit`, used by the delivered API) and
        page-style (`page`/`page_size`) are both supported; the mapping decides.
        """
        params = self.mapping.get('list_params') or {}
        if 'offset' in params or 'limit' in params:
            return {'style': 'offset', 'offset': params.get('offset', 'offset'),
                    'limit': params.get('limit', 'limit'), 'q': params.get('q', 'q')}
        return {'style': 'page', 'page': params.get('page', 'page'),
                'page_size': params.get('page_size', 'page_size'), 'q': params.get('q', 'q')}

    def limit_param(self) -> str:
        params = self.list_params()
        return params['limit'] if params['style'] == 'offset' else params['page_size']

    def page_query(self, index: int, size: int, extra: dict | None = None) -> dict:
        """Build the pagination query for page `index` (1-based) with `size` rows."""
        params = self.list_params()
        if params['style'] == 'offset':
            query = {params['offset']: (index - 1) * size, params['limit']: size}
        else:
            query = {params['page']: index, params['page_size']: size}
        query.update(extra or {})
        return query

    def response_keys(self) -> dict:
        spec = self.mapping.get('list_response') or {}
        return {'rows': spec.get('rows', 'records'), 'total': spec.get('total', 'total')}

    def rows_of(self, payload):
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict):
            preferred = self.response_keys()['rows']
            if isinstance(payload.get(preferred), list):
                return payload[preferred]
            for key in ('records', 'rows', 'items', 'data', 'results'):
                value = payload.get(key)
                if isinstance(value, list):
                    return value
        return None

    def total_of(self, payload):
        if isinstance(payload, dict):
            value = payload.get(self.response_keys()['total'])
            if isinstance(value, int):
                return value
        return None

    def page_size_for_walk(self) -> int:
        declared = (self.mapping.get('pagination') or {}).get('page_size')
        return int(declared) if declared else 200

    def fetch_all(self, name: str, page_size: int | None = None,
                  extra: dict | None = None) -> tuple[list, list]:
        """Walk the whole list endpoint; returns (row identifiers, per-page counts)."""
        url = self.list_url(name)
        if not url:
            raise LookupError(f'no list endpoint mapped for dataset {name!r}')
        page_size = page_size or self.page_size_for_walk()
        id_field = (self.dataset(name) or {}).get('id', 'id')
        rows: list = []
        counts: list[int] = []
        max_pages = 500
        for index in range(1, max_pages + 1):
            response = self.client.get(url, params=self.page_query(index, page_size, extra))
            if response.status != 200:
                raise LookupError(f'{url} page {index} returned HTTP {response.status}')
            payload = response.json()
            page_rows = self.rows_of(payload)
            if page_rows is None:
                raise LookupError(f'{url} page {index} did not return a row list')
            counts.append(len(page_rows))
            for row in page_rows:
                if id_field not in row:
                    raise LookupError(f'{url}: row is missing id field {id_field!r}')
                rows.append(norm(row[id_field]))
            total = self.total_of(payload)
            if len(page_rows) < page_size:
                break
            if total is not None and len(rows) >= total:
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
                        problems or {'rows': len(first), 'pages': len(counts),
                                     'page_size_used': self.page_size_for_walk()},
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
                                                    self.limit_param(): 50})
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
                                                 self.limit_param(): 50})
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
        max_size = int((self.mapping.get('pagination') or {}).get('limit_max', 500))
        if params['style'] == 'offset':
            pos, size = params['offset'], params['limit']
            cases = [
                {pos: '-1'},
                {pos: 'abc'},
                {size: '0'},
                {size: 'abc'},
                {size: str(max_size + 1)},
                {size: str(10 ** 7)},
            ]
        else:
            pos, size = params['page'], params['page_size']
            cases = [
                {pos: 'abc'},
                {pos: '-1'},
                {pos: '0'},
                {size: '0'},
                {size: 'abc'},
                {size: str(10 ** 7)},
            ]
        problems, details = [], {}
        for name in list(datasets)[:2]:
            url = self.list_url(name)
            baseline = self.client.get(url, params={size: 5})
            if baseline.status != 200:
                problems.append(f'{name}: baseline request HTTP {baseline.status}')
                continue
            extra_cases = []
            if self.mapping.get('reject_invalid_sort_order'):
                extra_cases.append({'sort_by': self.mapping.get('sort_field', 'client_shape_id'),
                                    'order': 'sideways'})
            for case in cases + extra_cases:
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
        # Fixed-shape endpoints: a misspelled parameter must not be silently ignored.
        for endpoint in self.mapping.get('fixed_shape_endpoints') or []:
            path = endpoint['path']
            for misspelled, _expected in (endpoint.get('must_reject') or {}).items():
                response = self.client.get(path, params={misspelled: endpoint.get('valid_value', '1')})
                details[f'{path}?{misspelled}'] = response.status
                if response.status < 400:
                    payload = response.json()
                    served = self.rows_of(payload)
                    problems.append(f'{path}?{misspelled}=... was accepted with HTTP {response.status} '
                                    f'({len(served) if served is not None else "?"} rows) — a misspelled '
                                    f'filter must not be ignored silently')
                elif response.status >= 500:
                    problems.append(f'{path}?{misspelled}=... produced HTTP {response.status}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def csv_row_by_pk(self, source: str, pk: str) -> dict | None:
        """The reviewed CSV row whose manifest primary key equals `pk`."""
        keys = self.batch.manifest()['files'][source].get('primary_key') or []
        for row in self.batch.rows(source):
            candidate = ':'.join(norm(row[key]) for key in keys)
            if candidate == norm(pk):
                return row
        return None

    def check_literal_values(self):
        check_id, title = 'API-04', '"false", empty text and missing values are not coerced'
        if not self.mapping.get('literal_probes'):
            return self.not_executed(
                check_id, title,
                'no literal_probes mapping (needs the contract to state which row/field carries '
                'a boolean false, an empty string and an absent field)')
        problems, details = [], {}
        for probe in self.mapping['literal_probes']:
            name = probe['dataset']
            spec = self.dataset(name) or {}
            label = f'{name}/{probe["key"]}.{probe["path"]}'
            url = self.detail_url(name, probe['key'])
            response = self.client.get(url)
            if response.status != 200:
                problems.append(f'{label}: HTTP {response.status}')
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
                problems.append(f'{label}: field is missing from the API payload')
                continue
            column_type = next((c['type'] for c in self.batch.columns(spec['source'])
                                if c['name'] == probe['path']), None) if spec.get('source') else None
            csv_row = self.csv_row_by_pk(spec['source'], probe['key']) if spec.get('source') else None
            if csv_row is None:
                problems.append(f'{label}: probe key does not exist in {spec.get("source")}')
                continue
            raw_csv = csv_row[probe['path']]
            expected = self.batch._convert(spec['source'], probe['path'], column_type, raw_csv) \
                if column_type else raw_csv
            details[label] = {'api': value, 'csv': expected, 'csv_raw': raw_csv, 'type': column_type}
            if raw_csv == 'false':
                if value is not False:
                    problems.append(f'{label}: CSV "false" is exposed as {value!r} ({type(value).__name__})')
            elif raw_csv == '':
                if value not in ('', None):
                    problems.append(f'{label}: empty CSV cell is exposed as {value!r}')
                if column_type == 'str' and value != '':
                    problems.append(f'{label}: empty string column must stay "" (got {value!r})')
                if column_type == 'int_or_empty' and value is not None:
                    problems.append(f'{label}: empty int_or_empty cell must be null (got {value!r})')
            elif column_type == 'int':
                if not isinstance(value, int) or isinstance(value, bool):
                    problems.append(f'{label}: int column exposed as {value!r} ({type(value).__name__})')
                elif value != expected:
                    problems.append(f'{label}: API {value!r} != CSV {expected!r}')
            elif column_type == 'str':
                if not isinstance(value, str):
                    problems.append(f'{label}: str column exposed as {type(value).__name__}')
                elif value != expected:
                    problems.append(f'{label}: API {value!r} != CSV {expected!r}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def check_integrity_failure(self):
        check_id, title = 'API-05', ('damaged or tampered batch copies never yield a pseudo-normal catalogue '
                                     '(hash, type, missing or tampered evidence files, manifest shrinkage)')
        datasets = self.mapping.get('integrity_datasets')
        if not datasets:
            return self.not_executed(check_id, title, 'no integrity_datasets mapping (contract not delivered)')
        if self.integrity_runner is None:
            return self.not_executed(check_id, title, self.integrity_skip_reason or (
                'launch-based check: needs --start with a startup command so the harness can restart the '
                'server on a damaged copy of the batch'))
        scenarios = self.mapping.get('integrity_scenarios')
        observations = self.integrity_runner(datasets, scenarios) if scenarios else \
            self.integrity_runner()
        problems, details = [], observations
        control = observations.get('_control_valid_copy') or {}
        control_ok = control.get('outcome') == 'served'
        if not control_ok:
            # Without a working control every "refusal" below would be meaningless.
            problems.append('control (undamaged copy) did not answer a normal read '
                            f'(outcome={control.get("outcome")}, health={control.get("health_status")}, '
                            f'data_status={control.get("data_status")}) — the harness cannot tell a '
                            'refusal of damaged data from a broken request, so no scenario may pass')
        for name, record in observations.items():
            if name.startswith('_control'):
                continue
            outcome = record.get('outcome')
            health_status = record.get('health_status')
            if outcome == 'refused_start':
                log = (record.get('log_tail') or '').lower()
                if not any(word in log for word in ('integrity', 'hash', 'sha256', 'size mismatch',
                                                    'mismatch', 'expects', 'missing', 'tamper')):
                    problems.append(f'{name}: refused to start but the reason is unclear: '
                                    f'{(record.get("log_tail") or "")[-160:]!r}')
            elif outcome == 'not_ready':
                pass
            elif outcome == 'refused_data' and name.startswith('manifest_drops'):
                # The shrunken manifest must be refused when it is loaded, not when a
                # missing dataset happens to be requested later.
                problems.append(f'{name}: service stayed ready with {record.get("datasets")} datasets '
                                f'(health={health_status}) instead of refusing the shrunken manifest')
            elif outcome in ('refused_data', 'served'):
                if name.startswith('manifest_drops'):
                    # A shrunken manifest must be refused while loading, not only when
                    # the now-missing dataset happens to be requested.
                    problems.append(f'{name}: service stayed ready with {record.get("datasets")} datasets '
                                    f'(health={health_status}) instead of refusing the shrunken manifest')
                elif outcome == 'refused_data' and control_ok:
                    pass  # readiness is green but reading the damaged table is refused: compliant
                elif outcome == 'served' and not control_ok:
                    continue  # the harness control already failed; not the product's fault
                elif name.startswith('missing_') or name.startswith('tampered_'):
                    problems.append(f'{name}: service reported ready (health={health_status}, '
                                    f'quarantine_entries={record.get("quarantine")}) — the missing or '
                                    f'tampered evidence file was silently accepted')
                elif record.get('quarantine_has_1700_for_2800'):
                    problems.append(f'{name}: the tampered 2800 value was served as normal data')
                else:
                    problems.append(f'{name}: service answered HTTP 200 with a normal catalogue '
                                    f'(health={health_status}) instead of refusing the damaged data')
            else:
                problems.append(f'{name}: scenario produced no usable observation')
        for name, record in observations.items():
            details[name] = {'outcome': record.get('outcome'), 'description': record.get('description'),
                             'health_status': record.get('health_status'),
                             'data_status': record.get('data_status'),
                             'datasets': record.get('datasets'), 'quarantine': record.get('quarantine')}
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
            response = self.client.get(url, params={search_param: name, self.limit_param(): 50})
            if response.status != 200:
                self.record(check_id, title, FAIL, f'HTTP {response.status} for search {name!r}')
                continue
            rows = self.rows_of(response.json()) or []
            value_field = spec.get('compare_id') or spec.get('id', 'id')
            got = sorted(norm(row.get(value_field)) for row in rows)
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
        # Paths and parameter names only: a synthetic *file-path* value on a
        # filtered endpoint is a different contract question (the documented
        # endpoints take exact-column filters, not file names) and would fail a
        # correct implementation with 400 instead of 404.
        probes = [
            ('../' * 6 + 'etc/passwd', {}),
            ('..%2f' * 6 + 'etc%2fpasswd', {}),
            ('../../data/script.fls', {}),
            ('%2e%2e%2f%2e%2e%2fdata%2fscript.fls', {}),
            (name, {'dataset': '../../data/script.fls'}),
            (name, {'dataset_path': '/etc/passwd'}),
        ]
        problems, details = [], {}
        for dataset, extra in probes:
            url = self.list_url(name).replace(
                (self.dataset(name) or {}).get('api_name', name), urllib.parse.quote(str(dataset), safe=''))
            response = self.client.get(url, params={self.limit_param(): 5, **extra})
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
        problems, details = [], {}
        # 1) Authoritative: the routes the server actually exposes (OpenAPI).
        routes = self.fetch_openapi_routes()
        details['openapi_routes'] = routes or 'unavailable'
        if routes:
            mutating = sorted(name for name, methods in routes.items()
                              if {m.upper() for m in methods} & {'POST', 'PUT', 'PATCH', 'DELETE'})
            if mutating:
                problems.append(f'the running server exposes mutating routes: {mutating}')
        # 2) Empirical: probe mutation-shaped paths with a real request.
        suspicious = ['save', 'edit', 'update', 'upload', 'publish', 'import', 'commit', 'write',
                      'delete', 'delete_row', 'create', 'reload', 'refresh', 'rebuild', 'export']
        for name in suspicious:
            for url in (f'{self.contract.base_path.rstrip("/")}/{name}',
                        f'{self.list_url(next(iter(self.mapping["datasets"])))}/{name}'):
                response = self.client.request('POST', url, body=b'{}',
                                               headers={'Content-Type': 'application/json'})
                details[f'POST {url}'] = response.status
                if response.status < 400:
                    problems.append(f'POST {url} accepted with HTTP {response.status}')
        # 3) Documented routes: only real path-shaped entries count. Prose that
        #    *forbids* writes ("无任何 POST / PUT / PATCH / DELETE 变更接口") is not
        #    a route declaration.
        documented = [entry for entry in self.contract.mutating_route_declarations()]
        details['contract_mutating_routes'] = documented
        if documented:
            problems.append(f'the contract declares mutating endpoints: {documented}')
        scanned = self.scan_source_for_mutating_routes()
        details['static_routes'] = scanned
        if scanned.get('mutating_routes'):
            problems.append(f'mutating routes found in the implementation source: {scanned["mutating_routes"]}')
        self.record(check_id, title, FAIL if problems else PASS, problems or details, requirement=self.REQUIRED)

    def fetch_openapi_routes(self) -> dict | None:
        """Real route table from the running service (FastAPI et al.), if any."""
        for path in self.mapping.get('openapi_paths', ['/openapi.json', 'openapi.json']):
            response = self.client.get(path)
            if response.status != 200:
                continue
            payload = response.json()
            if isinstance(payload, dict) and isinstance(payload.get('paths'), dict):
                return {name: sorted(methods) for name, methods in payload['paths'].items()}
        return None

    SKIP_DIRS = ('node_modules', '.git', 'dist', 'build', '__pycache__', '.venv')

    def scan_source_for_mutating_routes(self) -> dict:
        """Best-effort static scan of Agent H's implementation for mutating routes.

        Third-party and generated trees are skipped: a route declaration only
        counts inside the delivered product source.
        """
        roots = [path for path in (
            repo_root() / 'server/apps', repo_root() / 'server/src/review', repo_root() / 'server/src/review_api',
            repo_root() / 'server/src/mxsj_catalog',
        ) if path.exists()]
        pattern = re.compile(
            r'(\.(?:post|put|patch|delete)\s*\(|methods\s*=\s*\[[^\]]*[\'"](?:POST|PUT|PATCH|DELETE)|'
            r'[\'"](?:/|\w)*(?:save|upload|publish|edit|update|delete)[\'"])', re.I)
        hits = []
        files = 0
        for root in roots:
            for path in sorted(root.rglob('*.py')) + sorted(root.rglob('*.js')) + sorted(root.rglob('*.ts')):
                if not path.is_file() or any(part in self.SKIP_DIRS for part in path.parts):
                    continue
                files += 1
                for number, line in enumerate(path.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
                    if pattern.search(line):
                        hits.append({'file': path.relative_to(repo_root()).as_posix(),
                                     'line': number, 'text': line.strip()[:160]})
        return {'files': files, 'roots': [str(root.relative_to(repo_root())) for root in roots],
                'mutating_routes': hits}

    def check_proxy_safety(self):
        check_id, title = 'API-15', ('pages and API work through the preview proxy: relative URLs only, '
                                     'no sandbox host in the browser payload')
        web_url = self.mapping.get('web_url') or self.web_url
        if not web_url:
            return self.not_executed(
                check_id, title,
                'no --web-url supplied and the operation map declares none: the browser-side origin '
                '(Vite dev server / preview) was not exercised')
        web = Client(web_url, timeout=self.client.timeout)
        page = self.mapping.get('page_url') or '/'
        problems, details = [], {}
        response = web.get(page)
        details['page_status'] = response.status
        details['content_type'] = response.headers.get('Content-Type')
        if response.status != 200:
            problems.append(f'page {web_url}{page} returned HTTP {response.status}')
        body = response.text
        for needle in ('localhost', '127.0.0.1', '0.0.0.0'):
            if needle in body:
                problems.append(f'served page contains {needle!r} (browser must use relative URLs)')
        assets = re.findall(r'<script[^>]+src=["\']([^"\']+)', body) + \
                 re.findall(r'<link[^>]+href=["\']([^"\']+)', body)
        for asset in assets:
            if re.match(r'^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)', asset):
                problems.append(f'absolute sandbox URL in page asset: {asset}')
        details['assets'] = assets[:10]
        # The proxied API call the page itself makes must work through this origin.
        api_path = self.mapping.get('list_path', '').format(dataset='items')
        proxied = web.get(api_path, params={self.limit_param(): 1})
        details['proxied_api_status'] = proxied.status
        if proxied.status != 200:
            problems.append(f'the web origin does not proxy {api_path} (HTTP {proxied.status}); the page '
                            'would receive no data')
        else:
            payload = proxied.json()
            if not isinstance(payload, dict) or self.rows_of(payload) is None:
                problems.append(f'{api_path} through the web origin did not return the documented envelope')
            elif len(self.rows_of(payload)) != 1:
                problems.append(f'{api_path}?limit=1 through the proxy returned '
                                f'{len(self.rows_of(payload))} rows')
        # Preview proxies forward a foreign Host/Origin; the app must not reject it.
        if response.status == 200:
            host_override = web.get(page, headers={
                'Host': 'review-preview.e2b.app',
                'Origin': 'https://review-preview.e2b.app',
                'X-Forwarded-Proto': 'https',
            })
            details['host_override_status'] = host_override.status
            if host_override.status >= 400:
                problems.append(f'the web origin rejects a proxied Host/Origin with HTTP '
                                f'{host_override.status}')

        # HTTP 200 on the HTML is not "the page works". Ask the front end itself
        # which endpoints it requests (src/api/contract.ts) and call them through
        # the same origin. Findings here are *front-end* defects: they are reported
        # as W-12/W-13/W-14 in the web stage, and repeated only as evidence — the
        # verdict of API-15 stays about proxy safety and page reachability, so a
        # front-end contract mismatch is never filed as an API defect.
        # Real-app probing is opt-in; synthetic conformance controls must not
        # accidentally import whatever product frontend happens to be installed.
        app_dir = Path(self.mapping.get('web_app_dir', 'server/apps/review_web'))
        if not app_dir.is_absolute():
            app_dir = repo_root() / app_dir
        node_probe = Path(__file__).with_name('web_origin_probe.mjs')
        if self.mapping.get('web_app_dir') and app_dir.is_dir() and node_probe.is_file():
            command = ['node', '--experimental-strip-types', str(node_probe),
                       '--app-dir', str(app_dir), '--origin', web_url,
                       '--out', str(self.out_dir / 'web_origin_probe.json')]
            try:
                completed = subprocess.run(command, capture_output=True, text=True, timeout=300)
                details['frontend_probe_returncode'] = completed.returncode
                details['frontend_probe_report'] = str(self.out_dir / 'web_origin_probe.json')
                if completed.returncode != 0:
                    payload = json.loads((self.out_dir / 'web_origin_probe.json').read_text(encoding='utf-8'))
                    details['frontend_contract_problems'] = [
                        {'check': c['check'], 'detail': str(c['detail'])[:400]}
                        for c in payload['checks'] if c['status'] == 'fail']
                    details['frontend_problems_note'] = (
                        'these are front-end (Agent I) contract mismatches; they are reported as '
                        'W-12/W-13/W-14 in phase3_web_runtime, and are listed here as evidence only')
                else:
                    payload = json.loads((self.out_dir / 'web_origin_probe.json').read_text(encoding='utf-8'))
                    details['frontend_checks'] = {c['check']: c['status'] for c in payload['checks']}
            except Exception as exc:  # noqa: BLE001 - acceptance report
                problems.append(f'the front-end contract probe could not be run: {exc}')
        else:
            details['frontend_probe'] = 'not available (front end or node probe missing)'
        self.record(check_id, title, FAIL if problems else PASS, problems or details,
                    requirement=self.REQUIRED)

    # -- driver ----------------------------------------------------------
    CHECK_IDS = {
        'check_pagination': 'API-01',
        'check_search_and_exact_filter': 'API-02',
        'check_invalid_parameters': 'API-03',
        'check_literal_values': 'API-04',
        'check_integrity_failure': 'API-05',
        'check_quarantine_isolation': 'API-06',
        'check_2800_not_1700': 'API-07',
        'check_missing_aptitudes': 'API-08',
        'check_ambiguous_names': 'API-09/API-10',
        'check_npc_keys': 'API-11',
        'check_traversal': 'API-12',
        'check_read_only': 'API-13',
        'check_no_mutation_endpoints': 'API-14',
        'check_proxy_safety': 'API-15',
    }

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
                self.record(self.CHECK_IDS.get(check.__name__, check.__name__), check.__name__,
                            NOT_EXECUTED, f'server unreachable: {exc}')
            except Exception as exc:  # noqa: BLE001 - acceptance report
                self.record(self.CHECK_IDS.get(check.__name__, check.__name__), check.__name__,
                            FAIL, f'acceptance harness error: {type(exc).__name__}: {exc}')
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
class IntegrityScenario:
    """One corrupted/missing-file scenario to run against the delivered service."""

    def __init__(self, name: str, description: str, *, remove: str | None = None,
                 corrupt: str | None = None, target: str | None = None,
                 manifest_drop: str | None = None):
        self.name = name
        self.description = description
        self.remove = remove
        self.corrupt = corrupt
        self.target = target
        self.manifest_drop = manifest_drop

    def apply(self, batch_dir: Path) -> None:
        import csv as _csv
        if self.remove:
            (batch_dir / self.remove).unlink()
        if self.corrupt and self.target:
            path = batch_dir / self.target
            data = bytearray(path.read_bytes())
            if self.corrupt == 'flip_byte':
                index = data.find(b',') + 1
                while index < len(data) and data[index:index + 1] in (b'"', b' '):
                    index += 1
                data[index] = ord('X') if data[index] != ord('X') else ord('Y')
            elif self.corrupt == 'bad_int':
                text = data.decode('utf-8')
                lines = text.split('\n')
                fields = next(_csv.reader(io.StringIO(lines[1])))
                fields[0] = 'not-an-integer'
                lines[1] = '"' + '","'.join(fields) + '"'
                data = bytearray('\n'.join(lines).encode('utf-8'))
            elif self.corrupt == 'tamper_quarantine':
                lines = data.decode('utf-8').splitlines()
                tampered = []
                for line in lines:
                    item = json.loads(line)
                    if item.get('record_key') == 2800:
                        value = item['value_under_applied_profile']
                        pairs = value['dict']
                        for pair in pairs:
                            key = pair[0]
                            if 'bytes_hex' in key and bytes.fromhex(key['bytes_hex']).decode('cp950') == '法力資質':
                                pair[1] = 1700
                        item['reasons'] = ['tampered_by_acceptance_harness']
                    tampered.append(json.dumps(item, ensure_ascii=False, sort_keys=True))
                data = bytearray(('\n'.join(tampered) + '\n').encode('utf-8'))
            else:
                raise ValueError(f'unknown corruption {self.corrupt!r}')
            path.write_bytes(bytes(data))
        if self.manifest_drop:
            manifest_path = batch_dir / 'manifest.json'
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['files'].pop(self.manifest_drop, None)
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
                                     encoding='utf-8')


DEFAULT_INTEGRITY_SCENARIOS = (
    IntegrityScenario('csv_hash_corruption', 'one byte changed in items.csv (size and sha256 break)',
                      corrupt='flip_byte', target='items.csv'),
    IntegrityScenario('csv_type_corruption', 'a non-numeric value in the int column client_shape_id',
                      corrupt='bad_int', target='items.csv'),
    IntegrityScenario('missing_quarantine_file', 'quarantine.jsonl deleted',
                      remove='quarantine.jsonl'),
    IntegrityScenario('missing_validation_file', 'validation.json deleted', remove='validation.json'),
    IntegrityScenario('missing_overwrite_evidence', 'overwrite_evidence.jsonl deleted',
                      remove='overwrite_evidence.jsonl'),
    IntegrityScenario('missing_provenance_file', 'maps_npcs/provenance.json deleted',
                      remove='maps_npcs/provenance.json'),
    IntegrityScenario('tampered_quarantine_no_hash_update',
                      'quarantine.jsonl content changed without updating manifest hashes',
                      corrupt='tamper_quarantine', target='quarantine.jsonl'),
    IntegrityScenario('manifest_drops_items_dataset',
                      'manifest.json no longer declares items.csv (16 datasets left)',
                      manifest_drop='items.csv'),
)


class IntegrityRunner:
    """Restart the candidate service on scratch copies that are damaged.

    Every scenario works on a throwaway copy; the committed batch is never
    touched. Outcomes are classified as:

    * ``refused_start``  - the process exits with an integrity/type error
    * ``not_ready``      - the service answers, but readiness reports a failure
    * ``refused_data``   - readiness is green but the damaged table is refused with
      an explicit error status when it is actually read
    * ``served``         - the service answers HTTP 200 with a normal catalogue
    """

    def __init__(self, command: str, env: dict, dataset_root_env: str, base_path: str,
                 mapping: dict, scratch: Path, ready_path: str, source_dir: Path,
                 timeout: float = 45.0):
        self.command = command
        self.env = env
        self.dataset_root_env = dataset_root_env
        self.base_path = base_path.strip('/')
        self.mapping = mapping
        self.scratch = Path(scratch)
        self.ready_path = ready_path
        self.source_dir = Path(source_dir)
        self.timeout = timeout

    # -- helpers ---------------------------------------------------------
    def _query_params(self) -> dict:
        """One small page, using the pagination style this mapping declares.

        Getting this wrong would make every data request 400 and could be
        mistaken for "the damaged data was refused", so it reads the same
        `list_params` / `pagination` keys the rest of the probe uses.
        """
        spec = self.mapping.get('list_params') or {}
        if 'offset' in spec or 'limit' in spec:
            return {spec.get('offset', 'offset'): 0, spec.get('limit', 'limit'): 5}
        if 'page' in spec or 'page_size' in spec:
            return {spec.get('page', 'page'): 1, spec.get('page_size', 'page_size'): 5}
        pagination = self.mapping.get('pagination') or {}
        return {pagination.get('limit_param', 'limit'): 5}

    def _healthy_probe(self, port: int) -> dict:
        """Ask the running instance what it thinks its state is."""
        client = Client(f'http://127.0.0.1:{port}')
        result = {'health': None, 'health_status': None, 'datasets': None, 'quarantine': None}
        try:
            health = client.get(f'/{self.base_path}/health')
            result['health_status'] = health.status
            result['health'] = health.json()
        except ConnectionError as exc:
            return {'refused': True, 'reason': f'connection refused: {exc}'}
        try:
            listing = client.get(f'/{self.base_path}/datasets')
            payload = listing.json()
            if isinstance(payload, dict) and isinstance(payload.get('datasets'), list):
                result['datasets'] = len(payload['datasets'])
        except ConnectionError:
            pass
        datasets = self.mapping.get('datasets') or {}
        if datasets:
            name, spec = next(iter(datasets.items()))
            template = self.mapping.get('list_path') or ''
            if template:
                try:
                    data = client.get(template.format(dataset=spec.get('api_name', name)),
                                      params=self._query_params())
                    result['data_status'] = data.status
                    result['data_url'] = template.format(dataset=spec.get('api_name', name))
                except ConnectionError:
                    pass
        try:
            quarantine = client.get(f'/{self.base_path}/quarantine')
            payload = quarantine.json()
            if isinstance(payload, dict) and isinstance(payload.get('records'), list):
                result['quarantine'] = len(payload['records'])
                values = json.dumps(payload, ensure_ascii=False)
                result['quarantine_has_1700_for_2800'] = '"record_key": 2800' in values and '"1700"' in values
        except ConnectionError:
            pass
        ready = isinstance(result['health'], dict) and str(result['health'].get('status')) == 'ready'
        result['ready'] = ready
        return result

    def __call__(self, datasets: list[str] | None = None,
                 scenario_names: list[str] | None = None) -> dict:
        # `datasets` is informational (which datasets the caller cares about);
        # `scenario_names` selects the damage scenarios to run.
        _ = datasets
        scenarios = [sc for sc in DEFAULT_INTEGRITY_SCENARIOS
                     if not scenario_names or sc.name in scenario_names]
        observations: dict[str, dict] = {}
        # Control: the same data request against an *undamaged* copy. Without it a
        # wrongly-formed request (e.g. a wrong pagination parameter) would look
        # like "the damaged data was refused" and mask a real defect.
        observations['_control_valid_copy'] = self._observe('_control_valid_copy', None)
        for scenario in scenarios:
            batch_dir = self.scratch / f'scenario-{scenario.name}' / 'batch'
            write_temp_batch(batch_dir, self.source_dir)
            scenario.apply(batch_dir)
            observations[scenario.name] = self._observe(scenario.name, scenario, batch_dir)
        return observations

    def _observe(self, name: str, scenario, batch_dir: Path | None = None) -> dict:
        port = free_port()
        if batch_dir is None:
            batch_dir = self.scratch / 'control' / 'batch'
            write_temp_batch(batch_dir, self.source_dir)
        env = dict(self.env)
        env[self.dataset_root_env] = str(batch_dir)
        env['REVIEW_BATCH_DIR'] = str(batch_dir)
        env['PORT'] = str(port)
        command = [part.replace('{port}', str(port)).replace('{batch_dir}', str(batch_dir))
                   for part in self.command.split()]
        log_path = self.scratch / f'scenario-{name}.log'
        with StartedServer(command, port, env, log_path) as server:
            ready = server.wait(self.ready_path, timeout=self.timeout)
            record = {'description': getattr(scenario, 'description', 'undamaged copy (control)'),
                      'started': ready}
            if not ready:
                record['outcome'] = 'refused_start'
                record['log_tail'] = log_path.read_text(errors='replace')[-600:]
            else:
                probe = self._healthy_probe(port)
                record.update(probe)
                data_status = probe.get('data_status')
                if not probe.get('ready'):
                    record['outcome'] = 'not_ready'
                elif isinstance(data_status, int) and data_status >= 400:
                    record['outcome'] = 'refused_data'
                else:
                    record['outcome'] = 'served'
            return record


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
    parser.add_argument('--integrity-scenarios', default=None,
                        help='comma-separated subset of integrity scenarios to run (default: all)')
    parser.add_argument('--web-url', default=None,
                        help='browser-facing origin (Vite dev server / preview) for the page checks')
    parser.add_argument('--out', type=Path, default=None)
    args = parser.parse_args(argv)

    contract = Contract(args.contract)
    mapping = json.loads(args.map.read_text(encoding='utf-8')) if args.map else {}

    scratch = None
    keep_scratch = False
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
            # Priority: explicit CLI > operation map (acceptor-owned) > contract document.
            command = args.command or mapping.get('startup_command') or (
                contract.startup_commands[0] if contract.startup_commands else None)
            if not command:
                print(json.dumps({'status': NOT_EXECUTED,
                                  'reason': 'no startup command: pass --command, or declare startup_command '
                                            'in the operation map / API_CONTRACT.md'},
                                 ensure_ascii=False))
                return 3
            port = args.port or contract.port_hint or free_port()
            command_template = command  # keeps {port}/{batch_dir} for restart-based checks
            command = command.replace('{port}', str(port)).replace('{batch_dir}', str(fixture))
            env = dict(os.environ)
            env['PORT'] = str(port)
            env['REVIEW_BATCH_DIR'] = str(fixture)
            root_env = (args.dataset_root_env or mapping.get('dataset_root_env')
                        or contract.dataset_root_env or 'REVIEW_BATCH_DIR')
            if root_env:
                env[root_env] = str(fixture)
            started = StartedServer(command.split(), port, env, scratch / 'server.log')
            started.__enter__()
            health = args.health_path or (mapping.get('health_path') or 'health')
            ready_path = f'/{contract.base_path.strip("/")}/{str(health).strip("/")}'
            if not started.wait(ready_path):
                tail = ''
                try:
                    tail = Path(started.log_path).read_text(errors='replace')[-1500:]
                except OSError:
                    pass
                keep_scratch = True
                print(json.dumps({'status': NOT_EXECUTED,
                                  'reason': 'server did not become ready on a VALID batch copy; '
                                            'the delivered startup command is not usable as documented',
                                  'command': command,
                                  'batch_dir_used': str(fixture),
                                  'log_tail': tail}, ensure_ascii=False, indent=2))
                return 4
            base_url = f'http://127.0.0.1:{port}'
            if mapping.get('integrity_datasets'):
                if root_env or '{batch_dir}' in command_template:
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
            if args.integrity_scenarios:
                mapping = dict(mapping)
                mapping['integrity_scenarios'] = [name.strip() for name in
                                                  args.integrity_scenarios.split(',') if name.strip()]
            probe = Probe(Client(base_url), mapping, fixture, contract, integrity_runner=integrity_runner,
                          out_dir=args.out.parent if args.out else None)
            probe.integrity_skip_reason = integrity_skip_reason
            if args.web_url:
                probe.web_url = args.web_url
            report = probe.run()
    finally:
        if started:
            started.__exit__(None, None, None)
        if scratch and args.data_dir is None and not keep_scratch:
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
