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
                                  '--map', str(cls.map_path), '--web-url', f'http://127.0.0.1:{port}',
                                  '--out', str(out)], timeout=600)
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

    def _run(self, extra: list[str], scenarios: str) -> dict:
        out = self.scratch / ('report-' + '-'.join(extra).replace('--', '') + '.json')
        command = f'{sys.executable} {DOUBLE} --port {{port}} ' + ' '.join(extra)
        _, _, log = run_json([sys.executable, str(PROBE), '--start', '--map', str(self.map_path),
                              '--dataset-root-env', 'REVIEW_BATCH_DIR', '--command', command,
                              '--integrity-scenarios', scenarios, '--out', str(out)], timeout=600)
        self.assertTrue(out.exists(), log)
        report = json.loads(out.read_text())
        return {item['check']: item for item in report['checks']}

    # The double can only speak to the CSV/hash scenarios; the evidence-file and
    # manifest-coverage scenarios are properties of Agent H's loader (covered by
    # test_catalog_loader_acceptance.py against the real loader).
    SCENARIO = 'csv_hash_corruption,csv_type_corruption'

    def test_integrity_enforced_passes(self):
        checks = self._run(['--defects', 'none', '--require-hash'], self.SCENARIO)
        self.assertEqual(checks['API-05']['status'], 'pass', checks['API-05']['detail'])

    def test_integrity_ignored_fails(self):
        checks = self._run(['--defects', 'serve_corrupt'], self.SCENARIO)
        self.assertEqual(checks['API-05']['status'], 'fail', checks['API-05']['detail'])


class PageScannerSelfCheck(unittest.TestCase):
    """The static page scanner must flag real sinks and ignore documentation.

    Both directions matter: a scanner that fails a legitimate Vite proxy config,
    a guard comment or a negative test would force Agent I to delete safety
    documentation to satisfy the tool.
    """

    def test_generated_dependency_bundles_are_not_authored_product_source(self):
        root = tempdir('mxsj-generated-bundle-')
        (root / 'src').mkdir()
        (root / 'src/app.ts').write_text('fetch("/api/v1/review/health")')
        (root / 'dist/assets').mkdir(parents=True)
        (root / 'dist/assets/vendor.js').write_text(
            'element.innerHTML = html; fetch("http://localhost:9999/api"); const total = 6851;')
        checks = {c['check']: c for c in self._scan(root)['checks']}
        for key in ('W-03', 'W-04', 'W-06'):
            self.assertEqual(checks[key]['status'], 'pass', checks[key])

    def _scan(self, root: Path, *, api: bool = False) -> dict:
        script = (
            'import json,sys;from pathlib import Path;sys.path.insert(0, %r);'
            'from scan_review_web import scan;'
            'print(json.dumps(scan(app_root=Path(%r), api_roots=(Path(%r),) if %r else ())));'
            % (str(ROOT / 'server/tools/review_browser_checks'), str(root), str(root), api)
        )
        completed = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True,
                                   timeout=120, cwd=str(ROOT))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return json.loads(completed.stdout)

    @staticmethod
    def _status(report: dict) -> dict:
        return {item['check']: item['status'] for item in report['checks']}

    def test_legitimate_config_comments_tests_and_proxies_are_not_violations(self):
        root = tempdir('mxsj-webscan-positive-')
        (root / 'src').mkdir(parents=True)
        (root / 'fixtures').mkdir()
        (root / 'vite.config.ts').write_text(
            "import { defineConfig } from 'vite'\n"
            "export default defineConfig({\n"
            "  server: { host: '0.0.0.0', port: 5173, allowedHosts: true,\n"
            "    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } } },\n"
            "})\n")
        (root / 'fixtures/serve-fixture-api.mjs').write_text(
            "// local fixture server; NOT real data, NOT integration evidence\n"
            "server.listen(8788, '127.0.0.1')\n")
        (root / 'src/main.tsx').write_text(
            "/**\n"
            " * We never use dangerouslySetInnerHTML, and there is deliberately no\n"
            " * fixture/fallback branch here: if the request fails the UI shows an error.\n"
            " */\n"
            "export function View() {\n"
            "  const rows = useApiResource(() => fetch('/api/v1/review/datasets/items/records'))\n"
            "  if (rows.loading) return <p>loading</p>\n"
            "  if (!rows.data || rows.data.records.length === 0) return <p>empty</p>\n"
            "  if (rows.error) return <p>連線失敗，請重試</p>\n"
            "  return <div><span>{rows.data.total === 6851 ? 'all' : String(rows.data.total)}</span>\n"
            "    <pre className=\"raw-fallback\">{JSON.stringify(rows.data, null, 2)}</pre></div>\n"
            "}\n")
        (root / 'src/guards.test.ts').write_text(
            "import { expect, it } from 'vitest'\n"
            "it('never injects raw HTML', () => {\n"
            "  const text = read('src/main.tsx')\n"
            "  expect(text).not.toContain('dangerouslySetInnerHTML')\n"
            "  expect(text).not.toMatch(/\\.innerHTML\\s*=/)\n"
            "  expect(text).not.toMatch(/https?:\\/\\/(localhost|127\\.0\\.0\\.1)/)\n"
            "  expect(6851).toBe(6851)\n"
            "})\n")
        (root / 'src/test').mkdir()
        (root / 'src/test/fakeApi.ts').write_text(
            "export const FALLBACK_ROWS = [{ id: 1 }]\n")
        (root / 'index.html').write_text('<!doctype html><div id="root"></div>')
        report = self._scan(root)
        statuses = self._status(report)
        failures = {key: item for key, item in statuses.items() if item == 'fail'}
        self.assertEqual(failures, {},
                         f'legitimate files were flagged as violations: '
                         f'{[c for c in report["checks"] if c["status"] == "fail"]}')
        self.assertIn(statuses['W-01'], ('pass', 'review'))
        self.assertIn(statuses['W-02'], ('pass', 'review'))
        self.assertIn(statuses['W-04'], ('pass', 'review'))

    def test_real_data_fallback_and_hardcoded_count_are_violations(self):
        root = tempdir('mxsj-webscan-negative-')
        (root / 'src').mkdir(parents=True)
        (root / 'src/app.tsx').write_text(
            "import { SAMPLE_ROWS } from '../fixtures/sample'\n"
            "export function App() {\n"
            "  useApiResource(() => fetch('/api/v1/review/datasets/items/records'), [])\n"
            "  catch (error) { setRows(SAMPLE_ROWS) }\n"
            "  return <div>{rows}</div>\n"
            "}\n")
        (root / 'src/legacy.js').write_text(
            "const total = 6851\n"  # no fetch in this file -> written-in total
            "document.getElementById('out').innerHTML = name\n")
        (root / 'src/live.js').write_text(
            "const base = 'http://127.0.0.1:8000/api/v1/review'\n"
            "fetch(base + '/datasets/items/records')\n")
        (root / 'index.html').write_text('<!doctype html><div id="root"></div>')
        report = self._scan(root)
        statuses = self._status(report)
        self.assertEqual(statuses['W-01'], 'fail', 'absolute sandbox request in product code must fail')
        self.assertEqual(statuses['W-02'], 'fail', 'fixture import/fallback must fail')
        self.assertEqual(statuses['W-03'], 'fail', 'written-in total without a data path must fail')
        self.assertIn(statuses['W-04'], ('fail', 'review'), 'innerHTML assignment must be reported')

    def test_mutating_route_is_a_violation_but_cors_is_not(self):
        root = tempdir('mxsj-webscan-api-')
        (root / 'src').mkdir(parents=True)
        (root / 'src/api.py').write_text(
            "app.add_middleware(CORSMiddleware, allow_methods=['GET', 'OPTIONS', 'HEAD'])\n"
            "@app.get('/api/v1/review/health')\ndef health(): ...\n")
        report = self._scan(root, api=True)
        statuses = self._status(report)
        self.assertEqual(statuses['H-01'], 'pass', 'CORS allow_methods is not a route declaration')
        (root / 'src/api.py').write_text(
            "@app.post('/api/v1/review/save')\ndef save(): ...\n")
        report = self._scan(root, api=True)
        self.assertEqual(self._status(report)['H-01'], 'fail', 'a real POST route must fail')


if __name__ == '__main__':
    unittest.main()
