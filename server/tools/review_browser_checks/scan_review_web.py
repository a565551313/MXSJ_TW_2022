#!/usr/bin/env python3
"""Phase 3 static acceptance scan for the review web page (Agent I) and API source (Agent H).

The scanner is deliberately *classification-aware*, because a keyword grep over a
whole app directory produces false positives:

* **product runtime code** - files that end up in the browser bundle
  (``src/**`` minus tests and test helpers, ``index.html``).
* **test code** - ``*.test.ts(x)``, ``src/test/**``, ``tests/**``: may legitimately
  contain negative expectations ("must not contain localhost"), fixtures and
  hardcoded expected counts. Never a product violation.
* **fixtures / local dev servers** - ``fixtures/**``, ``*.mjs`` fixture servers:
  opt-in local tooling, not shipped to the browser.
* **server / build configuration** - ``vite.config.*``, ``*.config.js/ts``:
  binding ``0.0.0.0`` and proxying to ``127.0.0.1`` is *required* for the Arena
  preview, and is not a browser request to localhost.
* **comments** - stripped before scanning, so documentation such as
  "we never use dangerouslySetInnerHTML" or "no fixture/fallback branch here"
  cannot trip a guard.

Findings carry a severity:

* ``violation`` - proven from the code itself (e.g. a product file importing a
  fixture module, an unguarded ``innerHTML`` assignment, a browser fetch to an
  absolute sandbox URL). Only violations fail the gate.
* ``lead`` - suspicious but not decidable statically (e.g. a frozen row count
  appearing in product code). Reported for manual confirmation and never
  described as a proven product defect.

Usage:
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/scan_review_web.py [--out report.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batch_fixture import FIXED_EXPECTATIONS, repo_root  # noqa: E402

APP_ROOT = repo_root() / 'server/apps/review_web'
API_ROOTS = (repo_root() / 'server/apps/review_api', repo_root() / 'server/src/mxsj_catalog',
             repo_root() / 'server/src/review', repo_root() / 'server/src/review_api')

BROWSER_SUFFIXES = {'.html', '.htm', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.svelte'}
BACKEND_SUFFIXES = {'.py', '.js', '.ts', '.mjs'}

TEST_PATH = re.compile(r'(\.test\.[cm]?[jt]sx?$|\.spec\.[cm]?[jt]sx?$|/__tests__/|/src/test/|/tests?/)', re.I)
FIXTURE_PATH = re.compile(r'(/fixtures?/|serve-fixture|fixture-api)', re.I)
CONFIG_NAME = re.compile(r'(vite\.config\.|vitest\.config\.|eslint\.config\.|tsconfig|[a-z0-9_.\-]*\.config\.[cm]?[jt]s$)', re.I)
STYLE_SUFFIX = {'.css', '.scss', '.less'}

SANDBOX_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
STATE_KEYWORDS = ('loading', 'empty', 'error', 'fail', 'offline', 'retry', '連線', '錯誤')
SCRIPT_EXT = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.vue', '.svelte', '.html', '.htm'}


# --------------------------------------------------------------------------
# source utilities
# --------------------------------------------------------------------------
def strip_comments(text: str, suffix: str) -> str:
    """Remove comments so that documenting a rule cannot violate it."""
    if suffix in {'.py'}:
        return re.sub(r'(?m)^\s*#.*$', '', text)
    without_block = re.sub(r'/\*[\s\S]*?\*/', '', text)
    without_line = re.sub(r'(?m)(^|[^:])//.*$', r'\1', without_block)
    if suffix in {'.html', '.htm'}:
        return re.sub(r'<!--[\s\S]*?-->', '', without_line)
    return without_line


def code_only(line: str) -> str:
    """Remove quoted strings and JSX text nodes.

    A fixture word inside a banner string, a CSS class name or a `<code>` snippet
    is documentation, not a data path.
    """
    without_strings = re.sub(r"'[^'\n]*'|\"[^\"\n]*\"|`[^`]*`", "''", line)
    return re.sub(r'>[^<>]*<', '><', without_strings)


def classify(path: Path, root: Path) -> str:
    """product | test | fixture | config | style"""
    rel = '/' + path.relative_to(root).as_posix()
    if TEST_PATH.search(rel):
        return 'test'
    if FIXTURE_PATH.search(rel) or path.name.startswith('serve-fixture'):
        return 'fixture'
    if CONFIG_NAME.search(path.name):
        return 'config'
    if path.suffix.lower() in STYLE_SUFFIX:
        return 'style'
    return 'product'


def iter_files(roots, suffixes):
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*')):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if 'node_modules' in path.parts or path.name.startswith('.'):
                continue
            yield path


def relative(path: Path) -> str:
    try:
        return path.relative_to(repo_root()).as_posix()
    except ValueError:
        return str(path)


def finding(severity: str, kind: str, path: Path, line: int, text: str, note: str) -> dict:
    return {'severity': severity, 'kind': kind, 'file': relative(path), 'line': line,
            'text': text.strip()[:200], 'note': note}


def make(check_id: str, title: str, status: str, detail) -> dict:
    return {'check': check_id, 'title': title, 'status': status, 'detail': detail}


def status_for(violations, leads, executed=True) -> str:
    if violations:
        return 'fail'
    if not executed:
        return 'not_executed'
    if leads:
        return 'review'  # needs manual confirmation; not a proven defect
    return 'pass'


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------
def scan_runtime_hosts(files) -> tuple[list, list, list]:
    violations, leads, details = [], [], {}
    url_re = re.compile(r'(fetch|axios\.[a-z]+|new\s+WebSocket|EventSource|import\s*\(|[a-z]+\.src\s*=)'
                        r'\s*[(`\'"]{1,2}\s*https?://', re.I)
    # An absolute URL *bound as a value* (const base = 'http://127.0.0.1:8000/api') is a
    # request target even when the fetch( call is on a later line.
    bound_url_re = re.compile(r'''(=|\?\?|\(|,|return)\s*['"`]https?://(localhost|127\.0\.0\.1|0\.0\.0\.0)''')
    for path, kind in files:
        if kind not in ('product',):
            continue
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            if not any(host in line for host in SANDBOX_HOSTS):
                continue
            if url_re.search(line) or bound_url_re.search(line):
                violations.append(finding('violation', 'browser_request_to_sandbox_host', path, number,
                                          line, 'product code performs a request to an absolute sandbox URL'))
            else:
                leads.append(finding('lead', 'sandbox_host_mention', path, number, line,
                                     'sandbox host appears in product code; needs manual confirmation '
                                     'that it is not a request'))
        details[relative(path)] = 'scanned'
    return violations, leads, details


def read_code(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding='utf-8', errors='replace')
    return text, strip_comments(text, path.suffix.lower())


def scan_fixture_fallback(files) -> tuple[list, list, list]:
    """Opt-in fixture mode is fine; an automatic fallback on API failure is not."""
    violations, leads, details = [], [], {}
    import_re = re.compile(r"""from\s+['"][^'"]*(fixtures?/|/src/test/|__fixtures__)[^'"]*['"]""")
    data_symbol = r'(FALLBACK|FIXTURE|SAMPLE|MOCK|FAKE|fixture|mock|fake)[A-Za-z_]*'
    # A fixture symbol *used as data* - assignment, default, return value or call argument.
    data_use = re.compile(r'(=\s*|\?\?\s*|\|\|\s*|return\s+|,\s*|\breturn\s+\w{0,20}\(\s*)'
                          + data_symbol)
    for path, kind in files:
        if kind != 'product' or path.suffix.lower() not in SCRIPT_EXT:
            continue
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            if import_re.search(line):
                violations.append(finding('violation', 'product_imports_fixture', path, number, line,
                                          'production code imports fixtures/test helpers'))
                continue
            bare = code_only(line)
            if data_use.search(bare):
                violations.append(finding('violation', 'fixture_data_fallback', path, number, line,
                                          'production code uses a fixture/sample symbol as data'))
            elif re.search(r'\b(fixture|mock|fake|fallback)\b', bare, re.I):
                leads.append(finding('lead', 'fixture_identifier_in_product', path, number, line,
                                     'fixture-related identifier in product code; confirm it is not a '
                                     'data fallback'))
    details['product_files'] = sum(1 for _, kind in files if kind == 'product')
    details['opt_in_fixture_mode'] = any(
        'VITE_' in read_code(path)[1] for path, kind in files
        if kind == 'product' and path.suffix.lower() in SCRIPT_EXT)
    details['note'] = ('fixture mode gated by an explicit build-time flag is allowed; a data fallback '
                       'after a failed request is a violation')
    return violations, leads, details


def scan_hardcoded_counts(files) -> tuple[list, list, list]:
    counts = sorted(str(value) for value in FIXED_EXPECTATIONS.values() if isinstance(value, int) and value > 100)
    pattern = re.compile(r'(?<![\d.\w])(' + '|'.join(counts) + r')(?![\d.\w])')
    violations, leads, details = [], [], {}
    for path, kind in files:
        if kind != 'product' or path.suffix.lower() not in SCRIPT_EXT:
            continue
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            match = pattern.search(line)
            if not match:
                continue
            # Rendering a number that came from the API is not a hardcoded count;
            # statically we cannot always tell, so this is a lead.
            fetches = re.search(r'fetch\(|useApi|apiClient|/api/v1/review', code)
            if not fetches:
                violations.append(finding('violation', 'frozen_count_without_data_path', path, number, line,
                                          f'literal {match.group(1)} equals a frozen baseline count in a '
                                          'product file that performs no API request'))
            else:
                leads.append(finding('lead', 'frozen_count_literal', path, number, line,
                                     f'literal {match.group(1)} equals a frozen baseline count; confirm it is '
                                     'not used as an expected value or a written-in total'))
    details['counts_watched'] = counts
    details['product_files'] = sum(1 for _, kind in files if kind == 'product')
    return violations, leads, details


def scan_injection_sinks(files) -> tuple[list, list, list]:
    sinks = (
        (re.compile(r'dangerouslySetInnerHTML'), 'react_raw_html'),
        (re.compile(r'\.innerHTML\s*='), 'inner_html_assignment'),
        (re.compile(r'\.outerHTML\s*='), 'outer_html_assignment'),
        (re.compile(r'insertAdjacentHTML\s*\('), 'insert_adjacent_html'),
        (re.compile(r'document\.write\s*\('), 'document_write'),
        (re.compile(r'\beval\s*\('), 'eval'),
        (re.compile(r'new\s+Function\s*\('), 'function_constructor'),
        (re.compile(r'\bsetTimeout\s*\(\s*[\'"`]'), 'string_timeout'),
        (re.compile(r'\bv-html\s*='), 'vue_v_html'),
    )
    violations, leads, details = [], [], {}
    for path, kind in files:
        if path.suffix.lower() not in SCRIPT_EXT:
            continue
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            for pattern, label in sinks:
                if not pattern.search(line):
                    continue
                if kind == 'product':
                    violations.append(finding('violation', f'injection_sink:{label}', path, number, line,
                                              'unsafe HTML/script sink in production code'))
                elif re.search(r'\.not\.(toContain|toMatch|toBe)|assertNot|must not|禁止|不得', line):
                    # A guard asserting the sink never appears is the opposite of a violation.
                    continue
                else:
                    leads.append(finding('lead', f'injection_sink_in_{kind}:{label}', path, number, line,
                                         f'{label} appears in {kind} code; confirm it is a guard rather '
                                         'than a real sink'))
    details['sinks_watched'] = [label for _, label in sinks]
    return violations, leads, details


def scan_states(files) -> tuple[list, list, list]:
    product_text = '\n'.join(read_code(path)[1] for path, kind in files
                             if kind == 'product' and path.suffix.lower() in SCRIPT_EXT)
    missing = [word for word in STATE_KEYWORDS if word.lower() not in product_text.lower()]
    details = {'missing_keywords': missing,
               'product_files': sum(1 for _, kind in files if kind == 'product')}
    if not product_text.strip():
        return [], [], details
    leads = []
    if len(missing) == len(STATE_KEYWORDS):
        leads.append(finding('lead', 'no_state_keywords', APP_ROOT, 0, '',
                             'no loading/empty/error keywords found in product code; confirm the states exist'))
    return [], leads, details


def scan_relative_urls(files) -> tuple[list, list, list]:
    absolute_re = re.compile(r'''['"`]https?://[^'"`\s]+''')
    violations, leads, details = [], [], {}
    for path, kind in files:
        if kind != 'product' or path.suffix.lower() not in SCRIPT_EXT:
            continue
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            if absolute_re.search(line):
                violations.append(finding('violation', 'absolute_url_in_product', path, number, line,
                                          'absolute URL in browser-facing code; must be a relative path'))
    details['product_files'] = sum(1 for _, kind in files if kind == 'product')
    return violations, leads, details


def scan_mutating_routes(api_files) -> tuple[list, list, list]:
    violations, leads, details = [], [], {}
    route_re = re.compile(r'(@\w+\.(?:post|put|patch|delete)\s*\(|'
                          r'(?:app|router|api|bp|blueprint)\.(?:post|put|patch|delete)\s*\(|'
                          r'add_api_route\s*\(|add_url_rule\s*\()')
    cors_re = re.compile(r'allow_methods|allow_origins|CORSMiddleware|Access-Control')
    for path in api_files:
        _, code = read_code(path)
        for number, line in enumerate(code.splitlines(), 1):
            if cors_re.search(line):
                continue
            if route_re.search(line):
                violations.append(finding('violation', 'mutating_route', path, number, line,
                                          'mutating HTTP route declared in the API implementation'))
    details['api_files'] = len(api_files)
    details['routes_checked_live'] = 'API-14 probes the running service via OpenAPI and real requests'
    return violations, leads, details


# --------------------------------------------------------------------------
def scan(app_root: Path = APP_ROOT, api_roots=API_ROOTS) -> dict:
    report = {'stage': 'phase3_static_page_scan', 'checks': []}
    web_files = [(path, classify(path, app_root)) for path in iter_files((app_root,), BROWSER_SUFFIXES)]
    api_files = list(iter_files(api_roots, BACKEND_SUFFIXES))

    if not web_files:
        report['checks'].append(make('W-00', 'review web application delivered', 'not_executed',
                                     f'no browser-facing file found under {relative(app_root)}'))
        for check_id, title in (('W-01', 'no browser request to a sandbox host'),
                                ('W-02', 'no fixture/fallback data path in product code'),
                                ('W-03', 'frozen baseline counts are not hardcoded'),
                                ('W-04', 'no unescaped HTML/script sink'),
                                ('W-05', 'loading/empty/error states represented'),
                                ('W-06', 'relative API URLs only')):
            report['checks'].append(make(check_id, title, 'not_executed', 'web application not delivered'))
        report['checks'].append(make('H-01', 'API source declares no mutating routes',
                                     'fail' if api_files and any(
                                         scan_mutating_routes(api_files)[0]) else 'pass',
                                     'checked against delivered API source'))
        return finalize(report, web_files)

    kinds = {}
    for _, kind in web_files:
        kinds[kind] = kinds.get(kind, 0) + 1
    report['checks'].append(make('W-00', 'review web application delivered', 'pass',
                                 {'files': len(web_files), 'by_kind': kinds,
                                  'classified': {relative(p): k for p, k in web_files[:40]}}))

    specs = (
        ('W-01', 'no browser request to a sandbox host (server proxy config is not a violation)',
         scan_runtime_hosts),
        ('W-02', 'no fixture/fallback data path in product code (tests and opt-in fixture mode excluded)',
         scan_fixture_fallback),
        ('W-03', 'frozen baseline counts are not hardcoded in product code (tests excluded)',
         scan_hardcoded_counts),
        ('W-04', 'no unsafe HTML/script sink in product code (guard comments and negative tests excluded)',
         scan_injection_sinks),
        ('W-05', 'loading/empty/error states represented in product code', scan_states),
        ('W-06', 'relative API URLs only in browser-facing code', scan_relative_urls),
    )
    for check_id, title, function in specs:
        violations, leads, details = function(web_files)
        report['checks'].append(make(check_id, title, status_for(violations, leads), {
            'violations': violations, 'leads': leads, **details}))

    if not api_files:
        report['checks'].append(make('H-01', 'API source declares no mutating routes', 'not_executed',
                                     f'no API source found under {[relative(r) for r in api_roots]}'))
    else:
        violations, leads, details = scan_mutating_routes(api_files)
        report['checks'].append(make('H-01', 'API source declares no mutating routes',
                                     status_for(violations, leads),
                                     {'violations': violations, 'leads': leads, **details}))
    return finalize(report, web_files)


def finalize(report: dict, web_files) -> dict:
    statuses = [c['status'] for c in report['checks']]
    report['summary'] = {
        'pass': statuses.count('pass'),
        'fail': statuses.count('fail'),
        'review': statuses.count('review'),
        'not_executed': statuses.count('not_executed'),
        'files_scanned': len(web_files),
        'leads_needing_manual_confirmation': sum(
            len(c['detail'].get('leads', [])) for c in report['checks']
            if isinstance(c['detail'], dict)),
    }
    if 'fail' in statuses:
        report['status'] = 'fail'
    elif statuses.count('not_executed') == len(statuses):
        report['status'] = 'not_executed'
    elif 'review' in statuses:
        report['status'] = 'review'
    else:
        report['status'] = 'pass'
    report['status_meaning'] = {
        'pass': 'no violation and no lead',
        'review': 'no violation, but leads need manual confirmation (not proven defects)',
        'fail': 'at least one proven violation in product code',
        'not_executed': 'nothing to scan',
    }[report['status']]
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=None)
    parser.add_argument('--app-root', type=Path, default=APP_ROOT)
    args = parser.parse_args(argv)
    report = scan(args.app_root)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
    print(text)
    return {'pass': 0, 'review': 0, 'fail': 1, 'not_executed': 3}[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
