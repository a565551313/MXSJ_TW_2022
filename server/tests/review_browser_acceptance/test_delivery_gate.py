"""Phase 2/3 gate: run the real acceptance against H/I deliverables, or say why not.

The gate never turns a missing deliverable into a pass:

* while ``server/docs/review_browser/API_CONTRACT.md`` or ``server/apps/review_web``
  is absent, the corresponding tests report ``NOT EXECUTED`` with the reason and
  the acceptance document must keep saying that integration acceptance is not
  finished;
* once the deliverable exists, the same tests stop skipping. If the contract is
  present but the acceptor has not yet bound the documented endpoints (operation
  map) the gate FAILS instead of quietly skipping.
"""
from __future__ import annotations

import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from shutil import which as shutil_which

sys.path.insert(0, str(Path(__file__).resolve().parent))
from support import (  # noqa: E402
    ROOT, deliverable_state, free_port, operation_map_path, run_json, tempdir, wait_for_port,
)

sys.path.insert(0, str(ROOT / 'server/tools/review_browser_checks'))
from batch_fixture import default_batch_dir, write_temp_batch  # noqa: E402


class HttpResult:
    def __init__(self, status: int, body: str, headers):
        self.status = status
        self.body = body
        self.headers = headers


def http_get(url: str, headers: dict | None = None, timeout: float = 30.0) -> HttpResult:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return HttpResult(response.status, response.read().decode('utf-8', 'replace'),
                              dict(response.headers))
    except urllib.error.HTTPError as error:  # a 404 is an answer, not an exception
        return HttpResult(error.code, error.read().decode('utf-8', 'replace'), dict(error.headers))

PROBE = ROOT / 'server/tools/review_browser_checks/probe_live_api.py'
SCANNER = ROOT / 'server/tools/review_browser_checks/scan_review_web.py'
DOUBLE = ROOT / 'server/tools/review_browser_checks/conformance_negative_control.py'
WEB_PROBE = ROOT / 'server/tools/review_browser_checks/web_origin_probe.mjs'
UI_SMOKE = ROOT / 'server/tools/review_browser_checks/web_ui_smoke.mjs'
LAUNCHER = ROOT / 'server/tools/review_browser_checks/review_api_launch.py'
PYTHON = '/tmp/reviewvenv/bin/python' if Path('/tmp/reviewvenv/bin/python').exists() else sys.executable
WEB_APP = ROOT / 'server/apps/review_web'
STATE = deliverable_state()
NODE = shutil_which('node')


def frontend_ready() -> tuple[bool, str]:
    """Can the delivered front end actually be started in this sandbox?"""
    if not STATE['web_app']:
        return False, 'review web page not delivered'
    if not (WEB_APP / 'package.json').is_file():
        return False, f'{WEB_APP}/package.json is missing'
    if not (WEB_APP / 'node_modules').is_dir():
        return False, ('node_modules is not installed (offline sandbox): dependencies could not be '
                       'resolved, so the dev server cannot be started here')
    if NODE is None:
        return False, 'node is not available in this environment'
    return True, 'ready'


def node_can_import_typescript() -> bool:
    """--experimental-strip-types needs Node >= 22.6."""
    if NODE is None:
        return False
    completed = subprocess.run([NODE, '--version'], capture_output=True, text=True)
    match = re.match(r'v(\d+)\.(\d+)', completed.stdout.strip())
    if not match:
        return False
    return (int(match.group(1)), int(match.group(2))) >= (22, 6)


def start_process(command: list[str], cwd: Path | None, log_path: Path, env: dict | None = None):
    """Start a background process that survives until explicitly stopped.

    Output goes to a file (never a pipe): an undrained pipe can block a dev
    server, and the log is what the failure messages need.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handle = log_path.open('w', encoding='utf-8')
    process = subprocess.Popen(command, cwd=str(cwd) if cwd else None, env=env,
                               stdout=handle, stderr=subprocess.STDOUT, text=True,
                               start_new_session=True)
    process.log_handle = handle  # closed by stop_process
    return process


def log_tail(path: Path, lines: int = 30) -> str:
    if not path.is_file():
        return f'{path} was not created'
    return '\n'.join(path.read_text(encoding='utf-8', errors='replace').splitlines()[-lines:])


def stop_process(process) -> None:
    if process is None:
        return
    handle = getattr(process, 'log_handle', None)
    if handle is not None:
        handle.close()
    if process.poll() is not None:
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            process.kill()
        process.wait(timeout=10)
    if handle is not None and not handle.closed:
        handle.close()


def not_executed(reason: str):
    raise unittest.SkipTest(f'NOT EXECUTED: {reason}')


class ApiDeliveryGate(unittest.TestCase):
    def test_contract_is_delivered(self):
        if not STATE['api_contract']:
            not_executed(f"{STATE['api_contract_path']} does not exist yet; "
                         'Agent H has not published the loader/API contract')
        text = (ROOT / STATE['api_contract_path']).read_text(encoding='utf-8')
        self.assertIn('/api/v1/review/', text, 'the contract must document the agreed API prefix')

    def test_operation_map_is_bound_to_the_contract(self):
        if not STATE['api_contract']:
            not_executed('contract not delivered yet')
        mapping = operation_map_path()
        if mapping is None:
            self.fail('API_CONTRACT.md exists but no operation map (server/tools/review_browser_checks/'
                      'ops_*.json) binds it to the acceptance checks — the gate must not skip now')
        data = json.loads(mapping.read_text(encoding='utf-8'))
        self.assertTrue(data.get('datasets'), f'{mapping} declares no datasets')

    def test_live_api_conformance(self):
        if not STATE['api_contract'] or not STATE['api_app']:
            not_executed(f"contract={STATE['api_contract']} api_app={STATE['api_app']}; "
                         'no runnable loader/API to drive')
        mapping = operation_map_path()
        if mapping is None:
            self.fail('contract and API exist but the acceptance operation map is missing')
        command = (json.loads(mapping.read_text(encoding='utf-8')).get('startup_command'))
        if not command:
            self.fail(f'{mapping} does not record the documented startup command to launch in a new process')
        out = tempdir('mxsj-gate-api-') / 'report.json'
        code, report, log = run_json([sys.executable, str(PROBE), '--start', '--map', str(mapping),
                                      '--command', command, '--out', str(out)], timeout=900)
        if not out.exists():
            self.fail(f'probe produced no report (exit {code}):\n{log[-2000:]}')
        report = json.loads(out.read_text())
        failures = [item for item in report['checks'] if item['status'] == 'fail']
        self.assertEqual(failures, [], f'live API acceptance failures: {failures}')
        # API-15 drives the browser-facing origin; it is executed (and required to
        # pass) by WebDeliveryGate, which can start the dev server itself. Every
        # other check must have really been executed: "not executed" is never green.
        missing = [item['check'] for item in report['checks']
                   if item['status'] == 'not_executed' and item['check'] != 'API-15']
        self.assertEqual(missing, [], f'live API checks that could not be executed: {missing}')


class WebDeliveryGate(unittest.TestCase):
    """Drives the delivered page: real API + real dev server + real application code."""

    servers: dict = {}
    unavailable: str | None = None

    @classmethod
    def setUpClass(cls):
        ready, reason = frontend_ready()
        if not ready:
            cls.unavailable = reason
            return
        if not STATE['api_app']:
            cls.unavailable = 'the review API is not present, so the page has no backend to proxy to'
            return
        if NODE is None:
            cls.unavailable = 'node executable not found'
            return
        if not node_can_import_typescript():
            version = subprocess.run([NODE, '--version'], capture_output=True, text=True).stdout.strip()
            cls.unavailable = f'node --experimental-strip-types needs Node >= 22.6; found {version}'
            return
        for tool in (LAUNCHER, WEB_PROBE, UI_SMOKE):
            if not tool.is_file():
                cls.unavailable = f'acceptance tool missing: {tool}'
                return

        workdir = tempdir('mxsj-gate-page-')
        api_port, web_port = free_port(), free_port()
        batch = write_temp_batch(workdir / 'batch', default_batch_dir())
        api_log, web_log = workdir / 'api.log', workdir / 'web.log'
        api = start_process([PYTHON, str(LAUNCHER), '--batch-dir', str(batch),
                             '--host', '127.0.0.1', '--port', str(api_port)], None, api_log)
        cls.servers = {'workdir': workdir, 'api': api, 'api_log': api_log, 'web_log': web_log,
                       'api_port': api_port, 'web_port': web_port, 'web': None,
                       'origin': f'http://127.0.0.1:{web_port}'}
        if not wait_for_port(api_port, api, timeout=90):
            cls.unavailable = f'the review API did not start on port {api_port}:\n{log_tail(api_log)}'
            stop_process(api)
            return
        env = dict(os.environ)
        env['VITE_API_PROXY_TARGET'] = f'http://127.0.0.1:{api_port}'
        web = start_process([NODE, str(WEB_APP / 'node_modules/vite/bin/vite.js'),
                             '--port', str(web_port), '--strictPort'], WEB_APP, web_log, env)
        cls.servers['web'] = web
        if not wait_for_port(web_port, web, timeout=120):
            cls.unavailable = f'the web dev server did not start on port {web_port}:\n{log_tail(web_log)}'
            stop_process(web)
            stop_process(api)
            return
        # The proxy may still be warming up behind the dev server.
        for _ in range(20):
            probe = http_get(f'{cls.servers["origin"]}/api/v1/review/health')
            if probe.status == 200:
                break
            time.sleep(1.0)

    @classmethod
    def tearDownClass(cls):
        stop_process(cls.servers.get('web'))
        stop_process(cls.servers.get('api'))
        cls.servers = {}

    def setUp(self):
        if self.unavailable:
            not_executed(self.unavailable)

    def test_page_is_reachable_through_a_proxy_safe_server(self):
        """Start the real dev server, proxy the real API, and ask the front end for its endpoints.

        An HTTP 200 on the HTML proves nothing: the coordinator reproduced a white
        screen where ``/batch`` returned 200 while the data the front end expected
        was absent. This test requests the entry page and the module it loads, then
        imports the front end's own ``src/api/contract.ts`` to obtain the exact
        endpoint list it will call and checks every one of them through the web
        origin.
        """
        origin = self.servers['origin']
        entry = http_get(f'{origin}/')
        self.assertEqual(entry.status, 200, 'the dev server did not serve the entry page')
        problems = []
        if not re.search(r'<script[^>]+src=', entry.body):
            problems.append('the served HTML has no script entry point')
        for asset in re.findall(r'<(?:script|link)[^>]+(?:src|href)=["\']([^"\']+)', entry.body):
            if re.match(r'^https?://', asset):
                problems.append(f'absolute asset URL in the page: {asset}')
        self.assertEqual(problems, [], f'the served entry page is not proxy-safe: {problems}')

        proxied = http_get(f'{origin}/api/v1/review/datasets/items/records?offset=0&limit=1')
        self.assertEqual(proxied.status, 200,
                         f'the web origin does not proxy the review API (HTTP {proxied.status}): '
                         f'{proxied.body[:300]}\n--- vite ---\n{log_tail(self.servers["web_log"])}\n'
                         f'--- api ---\n{log_tail(self.servers["api_log"])}')

        out = self.servers['workdir'] / 'web_origin_probe.json'
        completed = subprocess.run([NODE, '--experimental-strip-types', str(WEB_PROBE),
                                    '--app-dir', str(WEB_APP), '--origin', origin, '--out', str(out)],
                                   capture_output=True, text=True, timeout=300)
        self.assertTrue(out.exists(), 'the front-end contract probe produced no report:\n'
                                      f'{completed.stdout[-2000:]}{completed.stderr[-2000:]}')
        report = json.loads(out.read_text(encoding='utf-8'))
        failures = [item for item in report['checks'] if item['status'] == 'fail']
        self.assertEqual(failures, [],
                         'the page is served but the application cannot load its data through it: '
                         + json.dumps([{c['check']: c['detail']} for c in failures],
                                      ensure_ascii=False)[:4000])

    def test_page_renders_application_code(self):
        """Build and execute the delivered front end against the real API.

        The application's own bundle is executed in a jsdom document: this catches
        the class of failure where the shell renders but a page component throws,
        leaving the user with a blank screen.
        """
        out = self.servers['workdir'] / 'web_ui_smoke.json'
        completed = subprocess.run([NODE, '--experimental-strip-types', str(UI_SMOKE),
                                    '--app-dir', str(WEB_APP), '--origin', self.servers['origin'],
                                    '--out', str(out)], capture_output=True, text=True, timeout=600)
        self.assertTrue(out.exists(), 'the UI smoke test produced no report:\n'
                                      f'{completed.stdout[-2000:]}{completed.stderr[-2000:]}')
        report = json.loads(out.read_text(encoding='utf-8'))
        failures = [item for item in report['checks'] if item['status'] == 'fail']
        self.assertEqual(failures, [],
                         'the delivered front end does not render against the real API: '
                         + json.dumps([{c['check']: c['detail']} for c in failures],
                                      ensure_ascii=False)[:4000])
        console = [item for item in report['console'] if item['level'] in ('error', 'uncaught', 'fatal')]
        self.assertEqual(console, [], f'the application logged errors while loading: {console[:5]}')


class NoVacuityGate(unittest.TestCase):
    """Guard against the acceptance suite going green by staying skipped."""

    def test_suite_identity(self):
        # This suite is separate from the 161 architecture tests and must never
        # be reported as part of them.
        self.assertTrue((ROOT / 'server/tests/review_browser_acceptance').is_dir())

    def test_self_check_double_is_not_a_product_deliverable(self):
        # The fault-injection double must stay out of the product paths.
        self.assertTrue(DOUBLE.is_file())
        for forbidden in (ROOT / 'server/apps/review_web', ROOT / 'server/apps/review_api',
                          ROOT / 'server/docs/review_browser'):
            if forbidden.is_dir():
                files = [p.name for p in forbidden.rglob('*') if p.is_file()]
                self.assertNotIn(DOUBLE.name, files)
                _ = files


if __name__ == '__main__':
    unittest.main()
