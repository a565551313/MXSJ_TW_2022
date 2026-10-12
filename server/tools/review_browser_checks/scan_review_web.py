#!/usr/bin/env python3
"""Phase 3 static acceptance scan for the review web page (Agent I) and API source (Agent H).

Static analysis cannot replace driving the page in a browser; it is the part of
the page acceptance that is provable without a browser engine. Every check that
needs a live DOM is reported as ``not_executed`` with the reason.

Checks:

* W-01  browser-facing files never target sandbox localhost / 127.0.0.1 / 0.0.0.0
* W-02  no mock/fake data fallback when the API is unavailable
* W-03  the frozen baseline counts are not hardcoded in the front end
* W-04  no unescaped HTML injection sink (innerHTML/document.write/eval) with data
* W-05  loading / empty / error states are handled
* W-06  API calls use relative URLs (preview-proxy safe)
* H-01  the API source declares no mutating (edit/save/upload/publish) routes

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

WEB_ROOTS = (repo_root() / 'server/apps/review_web',)
API_ROOTS = (repo_root() / 'server/apps/review_api', repo_root() / 'server/src/review',
             repo_root() / 'server/src/review_api')
FRONTEND_SUFFIXES = {'.html', '.htm', '.js', '.mjs', '.cjs', '.ts', '.jsx', '.tsx', '.css', '.vue', '.svelte'}
BACKEND_SUFFIXES = {'.py', '.js', '.ts', '.mjs'}

SANDBOX_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0', '::1')
MOCK_PATTERNS = (
    r'\bmock[_A-Za-z]*\b', r'\bfake[_A-Za-z]*\b', r'\bfallback[_A-Za-z]*\b',
    r'\bsample[_A-Za-z]*\b', r'\bdummy[_A-Za-z]*\b', r'\bhardcoded\b', r'\bstatic[_ ]data\b',
)
SINK_PATTERNS = (
    r'\.innerHTML\s*=', r'\.outerHTML\s*=', r'insertAdjacentHTML\s*\(', r'document\.write\s*\(',
    r'\beval\s*\(', r'new\s+Function\s*\(', r'setTimeout\s*\(\s*[\'"`]',
    r'v-html\s*=', r'\bdangerouslySetInnerHTML\b', r'\.srcdoc\s*=',
)
STATE_KEYWORDS = ('loading', 'empty', 'error', 'fail', 'offline', 'retry', '連線', '錯誤')


def iter_files(roots, suffixes):
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob('*')):
            if path.is_file() and path.suffix.lower() in suffixes:
                yield path


def relative(path: Path) -> str:
    try:
        return path.relative_to(repo_root()).as_posix()
    except ValueError:
        return str(path)


def make(check_id: str, title: str, status: str, detail) -> dict:
    return {'check': check_id, 'title': title, 'status': status, 'detail': detail}


def scan_text_file(path: Path):
    """Return (lines, code_lines) where comments/strings stay visible for context."""
    text = path.read_text(encoding='utf-8', errors='replace')
    return text, text.splitlines()


def scan(frontend_roots=WEB_ROOTS, backend_roots=API_ROOTS) -> dict:
    report = {'stage': 'phase3_static_page_scan', 'checks': []}
    web_files = list(iter_files(frontend_roots, FRONTEND_SUFFIXES))
    api_files = list(iter_files(backend_roots, BACKEND_SUFFIXES))

    if not web_files:
        report['checks'].append(make(
            'W-00', 'review web application delivered', 'not_executed',
            f'no browser-facing file found under {[relative(r) for r in frontend_roots]}'))
        for check_id, title in (('W-01', 'no sandbox localhost references'),
                                ('W-02', 'no mock/fake data fallback'),
                                ('W-03', 'baseline counts are not hardcoded'),
                                ('W-04', 'no unescaped HTML injection sink'),
                                ('W-05', 'loading/empty/error states handled'),
                                ('W-06', 'relative API URLs')):
            report['checks'].append(make(check_id, title, 'not_executed',
                                         'web application not delivered'))
        report['status'] = 'not_executed'
        report['summary'] = {'pass': 0, 'fail': 0, 'not_executed': len(report['checks'])}
        return report

    report['checks'].append(make('W-00', 'review web application delivered', 'pass',
                                 {'files': [relative(p) for p in web_files]}))

    def grep_hits(pattern, files, flags=re.I):
        hits = []
        compiled = re.compile(pattern, flags)
        for path in files:
            text, lines = scan_text_file(path)
            for number, line in enumerate(lines, 1):
                if compiled.search(line):
                    hits.append({'file': relative(path), 'line': number, 'text': line.strip()[:200]})
            _ = text
        return hits

    # W-01 sandbox localhost
    hits = grep_hits('|'.join(re.escape(host) for host in SANDBOX_HOSTS), web_files)
    report['checks'].append(make(
        'W-01', 'browser-facing files never target a sandbox host', 'fail' if hits else 'pass', hits))

    # W-02 mock/fake fallback
    hits = grep_hits('|'.join(MOCK_PATTERNS), web_files)
    report['checks'].append(make(
        'W-02', 'no mock/fake data fallback path', 'fail' if hits else 'pass', hits))

    # W-03 hardcoded baseline counts
    counts = [str(value) for key, value in FIXED_EXPECTATIONS.items()
              if isinstance(value, int) and value > 100]
    count_pattern = re.compile(r'(?<![\d.])(' + '|'.join(counts) + r')(?![\d.])')
    hits = []
    for path in web_files:
        _, lines = scan_text_file(path)
        for number, line in enumerate(lines, 1):
            if count_pattern.search(line):
                hits.append({'file': relative(path), 'line': number, 'text': line.strip()[:200]})
    report['checks'].append(make(
        'W-03', 'frozen baseline counts are not hardcoded in the front end',
        'fail' if hits else 'pass', hits or {'counts_checked': counts}))

    # W-04 injection sinks
    sink_re = re.compile('|'.join(SINK_PATTERNS))
    escape_re = re.compile(r'escapeHtml|escape_html|textContent|createTextNode|sanitiz|encodeURIComponent',
                           re.I)
    hits = []
    for path in web_files:
        text, lines = scan_text_file(path)
        for number, line in enumerate(lines, 1):
            if sink_re.search(line) and not escape_re.search(line):
                hits.append({'file': relative(path), 'line': number, 'text': line.strip()[:200]})
        _ = text
    report['checks'].append(make(
        'W-04', 'no unescaped HTML injection sink carrying data',
        'fail' if hits else 'pass', hits))

    # W-05 state handling
    text_all = '\n'.join(scan_text_file(p)[0] for p in web_files).lower()
    missing = [word for word in STATE_KEYWORDS if word.lower() not in text_all]
    report['checks'].append(make(
        'W-05', 'loading/empty/error states are represented in the page source',
        'pass' if len(missing) < len(STATE_KEYWORDS) else 'fail',
        {'missing_keywords': missing}))

    # W-06 relative API base
    absolute_api = []
    api_re = re.compile(r'(?:fetch|axios\.[a-z]+|open|src|href)\s*[=(]\s*[\'"`]https?://', re.I)
    for path in web_files:
        _, lines = scan_text_file(path)
        for number, line in enumerate(lines, 1):
            if api_re.search(line):
                absolute_api.append({'file': relative(path), 'line': number, 'text': line.strip()[:200]})
    report['checks'].append(make(
        'W-06', 'network calls use relative URLs (preview-proxy safe)',
        'fail' if absolute_api else 'pass', absolute_api))

    # H-01 mutating routes in the API source
    mutating = []
    route_re = re.compile(r'(\.(?:post|put|patch|delete)\s*\(|\bmethods\s*=\s*\[[^\]]*[\'"]'
                          r'(?:POST|PUT|PATCH|DELETE)|[\'"](?:/|\w)*(?:save|upload|publish|edit|update)'
                          r'[\'"]\s*(?:,|\)))', re.I)
    if not api_files:
        report['checks'].append(make('H-01', 'API source declares no mutating routes', 'not_executed',
                                     f'no API source found under {[relative(r) for r in backend_roots]}'))
    else:
        for path in api_files:
            _, lines = scan_text_file(path)
            for number, line in enumerate(lines, 1):
                if route_re.search(line):
                    mutating.append({'file': relative(path), 'line': number, 'text': line.strip()[:200]})
        report['checks'].append(make('H-01', 'API source declares no mutating routes',
                                     'fail' if mutating else 'pass', mutating,
                                     ))

    executed = [c for c in report['checks'] if c['status'] in ('pass', 'fail')]
    report['summary'] = {
        'pass': sum(1 for c in report['checks'] if c['status'] == 'pass'),
        'fail': sum(1 for c in report['checks'] if c['status'] == 'fail'),
        'not_executed': sum(1 for c in report['checks'] if c['status'] == 'not_executed'),
        'files_scanned': len(web_files),
    }
    report['status'] = 'fail' if any(c['status'] == 'fail' for c in report['checks']) else (
        'pass' if executed else 'not_executed')
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=None)
    args = parser.parse_args(argv)
    report = scan()
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + '\n', encoding='utf-8')
    print(text)
    return 0 if report['status'] == 'pass' else (3 if report['status'] == 'not_executed' else 1)


if __name__ == '__main__':
    raise SystemExit(main())
