"""Acceptance-harness self-check (negative and positive control).

An acceptance suite that has never failed is worthless, so this module runs the
live-API probe and the page scanner against a deliberately fault-injected test
double (``server/tools/review_browser_checks/conformance_negative_control.py``).

* Negative control: with defects enabled the probe must FAIL the corresponding
  checks. Asserting the exact check ids keeps the harness honest — if a check
  stops detecting its fault, this test fails.
* Positive control: with defects disabled the same probe must PASS every check,
  proving the probe does not simply fail everything.

The double is **not** Agent H's API and **not** a proposal for the contract; it
only exists so the harness itself can be verified before the real deliverable
exists.
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from support import ROOT, free_port, run_json, tempdir, wait_for_port  # noqa: E402

DOUBLE = ROOT / 'server/tools/review_browser_checks/conformance_negative_control.py'
PROBE = ROOT / 'server/tools/review_browser_checks/probe_live_api.py'
SCANNER = ROOT / 'server/tools/review_browser_checks/scan_review_web.py'

NEGATIVE_EXPECTED_FAILURES = {
    'API-01.items': 'pagination without duplicates/completeness',
    'API-03': 'invalid parameters silently replaced',
    'API-04': 'literal false/empty coerced',
    'API-06': 'quarantined records leaking into normal lists',
    'API-07': 'quarantined aptitude 2800 served as a normal row',
    'API-08': 'missing aptitudes zero-filled',
    'API-09': 'ambiguous skill name collapsed to one id',
    'API-10': 'ambiguous skill name collapsed to one id',
    'API-11': 'NPC records deduplicated by (scene_id, npcid)',
    'API-12': 'path traversal accepted / file content leaked',
    'API-13': 'catalogue mutated through the API',
    'API-14': 'save/edit endpoints reachable',
    'API-15': 'page targets sandbox localhost',
}


class ProbeAgainstInjectedFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempdir('mxsj-selfcheck-')
        cls.map_path = cls.scratch / 'ops.json'
        subprocess.run([sys.executable, str(DOUBLE), '--emit-map', str(cls.map_path)],
                       check=True, capture_output=True)
        cls.mapping = json.loads(cls.map_path.read_text())
        cls.negative = cls._probe('all')
        cls.positive = cls._probe('none')

    @classmethod
    def _probe(cls, defects: str) -> dict:
        port = free_port()
        server = subprocess.Popen(
            [sys.executable, str(DOUBLE), '--port', str(port), '--defects', defects],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
            env={**__import__('os').environ, 'REVIEW_BATCH_DIR': str(ROOT / 'server/docs/csv_checks/batch_001')})
        try:
            if not wait_for_port(port, server):
                raise AssertionError(f'the self-check double did not start (defects={defects})')
            out = cls.scratch / f'report-{defects}.json'
            _, _, log = run_json([sys.executable, str(PROBE), '--base-url', f'http://127.0.0.1:{port}',
                                  '--map', str(cls.map_path), '--out', str(out)], timeout=600)
            if not out.exists():
                raise AssertionError(f'probe produced no report (defects={defects}):\n{log}')
            return json.loads(out.read_text())
        finally:
            server.terminate()
            server.wait(timeout=15)

    def test_negative_control_reports_failures(self):
        self.assertEqual(self.negative['status'], 'fail')
        statuses = {item['check']: item['status'] for item in self.negative['checks']}
        for check_id, meaning in NEGATIVE_EXPECTED_FAILURES.items():
            with self.subTest(check=check_id, meaning=meaning):
                self.assertEqual(statuses.get(check_id), 'fail',
                                 f'{check_id} no longer detects: {meaning}')

    def test_positive_control_passes_every_executed_check(self):
        failures = [item for item in self.positive['checks'] if item['status'] == 'fail']
        self.assertEqual(failures, [], f'the probe fails a compliant server: {failures}')
        executed = [item for item in self.positive['checks'] if item['status'] != 'not_executed']
        self.assertGreaterEqual(len(executed), 16)
        # API-05 (corrupt copy must not be served as a normal catalogue) is a
        # launch-based check and is exercised separately below, so a probe run
        # against an externally started instance reports "incomplete".
        self.assertEqual(self.positive['status'], 'incomplete',
                         'a run with a required-but-unexecuted check must not look green')
        statuses = {item['check']: item['status'] for item in self.positive['checks']}
        self.assertEqual(statuses['API-05'], 'not_executed')


class IntegrityCheckAgainstCorruptedCopies(unittest.TestCase):
    """API-05: a corrupted batch copy must not be served as a normal catalogue."""

    @classmethod
    def setUpClass(cls):
        cls.scratch = tempdir('mxsj-selfcheck-integrity-')
        cls.map_path = cls.scratch / 'ops.json'
        subprocess.run([sys.executable, str(DOUBLE), '--emit-map', str(cls.map_path)],
                       check=True, capture_output=True)

    def _run(self, extra: list[str]) -> dict:
        out = self.scratch / ('report-' + '-'.join(extra).replace('--', '') + '.json')
        command = f'{sys.executable} {DOUBLE} --port {{port}} ' + ' '.join(extra)
        _, _, log = run_json([sys.executable, str(PROBE), '--start', '--map', str(self.map_path),
                              '--dataset-root-env', 'REVIEW_BATCH_DIR', '--command', command,
                              '--out', str(out)], timeout=600)
        self.assertTrue(out.exists(), log)
        report = json.loads(out.read_text())
        return {item['check']: item for item in report['checks']}

    def test_integrity_enforced_passes(self):
        checks = self._run(['--defects', 'none', '--require-hash'])
        self.assertEqual(checks['API-05']['status'], 'pass', checks['API-05']['detail'])

    def test_integrity_ignored_fails(self):
        checks = self._run(['--defects', 'serve_corrupt'])
        self.assertEqual(checks['API-05']['status'], 'fail', checks['API-05']['detail'])


class PageScannerSelfCheck(unittest.TestCase):
    """The static page scanner must flag the faults it claims to detect."""

    def _scan(self, root: Path) -> dict:
        script = (
            'import json,sys;from pathlib import Path;sys.path.insert(0, %r);'
            'from scan_review_web import scan;'
            'print(json.dumps(scan(frontend_roots=(Path(%r),), backend_roots=(Path(%r),))))'
            % (str(ROOT / 'server/tools/review_browser_checks'), str(root), str(root))
        )
        completed = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True,
                                   timeout=120, cwd=str(ROOT))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    def test_noncompliant_page_is_rejected(self):
        root = tempdir('mxsj-webscan-bad-')
        (root / 'index.html').write_text(
            '<!doctype html><script>fetch("http://127.0.0.1:8100/api/v1/review/datasets/items");</script>')
        (root / 'app.js').write_text(
            'const FALLBACK = [{id: 1}];\nconst total = 6851;\nif (err) { render(FALLBACK); }\n'
            'el.innerHTML = row.name;\n')
        report = self._scan(root)
        statuses = {item['check']: item['status'] for item in report['checks']}
        for check_id in ('W-01', 'W-02', 'W-03', 'W-04', 'W-05', 'W-06'):
            with self.subTest(check=check_id):
                self.assertEqual(statuses[check_id], 'fail')

    def test_compliant_page_passes(self):
        root = tempdir('mxsj-webscan-good-')
        (root / 'index.html').write_text('<!doctype html><div id="app"></div>')
        (root / 'app.js').write_text(
            'fetch("/api/v1/review/datasets/items").then(r => r.json()).then(rows => {\n'
            '  if (!rows.length) { app.textContent = "無資料"; return; }\n'
            '  app.textContent = rows.map(row => row.name).join("");\n'
            '}).catch(() => { app.textContent = "連線失敗，請重試"; });\n')
        report = self._scan(root)
        statuses = {item['check']: item['status'] for item in report['checks']}
        self.assertEqual([c for c in ('W-01', 'W-02', 'W-03', 'W-04', 'W-05', 'W-06')
                          if statuses[c] != 'pass'], [])


if __name__ == '__main__':
    unittest.main()
