#!/usr/bin/env python3
"""Run every review-tool acceptance stage and emit one ledger.

Stages
------
1. Phase 1  independent data baseline (``verify_data_baseline.py``)
2. Phase 2  live loader/API semantics (``probe_live_api.py``) - only when Agent H's
   contract, application and the acceptor's operation map exist
3. Phase 3  static page policy (``scan_review_web.py``) - only when Agent I's page exists
4. Phase 3  web runtime: the real API behind the real dev server, driven by the
   front end's own endpoint contract (``web_origin_probe.mjs``) and by executing
   the built application in a jsdom document (``web_ui_smoke.mjs``)
5. the acceptance unittest suite (``server/tests/review_browser_acceptance``)

Nothing is ever reported as passed unless it actually ran; missing deliverables
produce ``not_executed`` entries with the reason and are listed in the summary.

Usage:
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py \
        [--out server/tools/review_browser_checks/evidence/acceptance_report.json] \
        [--api-sha <sha>] [--web-sha <sha>]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_data_baseline  # noqa: E402
from batch_fixture import default_batch_dir, repo_root, write_temp_batch  # noqa: E402
from scan_review_web import scan as scan_web  # noqa: E402

TOOLS = Path(__file__).resolve().parent
PROBE = TOOLS / 'probe_live_api.py'
LAUNCHER = TOOLS / 'review_api_launch.py'
WEB_PROBE = TOOLS / 'web_origin_probe.mjs'
UI_SMOKE = TOOLS / 'web_ui_smoke.mjs'
CONTRACT = repo_root() / 'server/docs/review_browser/API_CONTRACT.md'
WEB_APP = repo_root() / 'server/apps/review_web'
PYTHON = '/tmp/reviewvenv/bin/python' if Path('/tmp/reviewvenv/bin/python').exists() else sys.executable


REQUIRED_API_CHECKS = {
    'API-01': '分页无遗漏、无意外重复、排序稳定',
    'API-02': '搜索与精确过滤符合契约',
    'API-03': '非法参数有明确错误，不悄悄替换',
    'API-04': '"false"/空文本/缺失值不被错误转换',
    'API-05': '哈希或类型校验失败不得继续提供伪正常目录',
    'API-06': '隔离记录不进入正常列表',
    'API-07': '2800 不被改成未经批准的 1700',
    'API-08': '3010/4021/4022 缺失资质不补零',
    'API-09': '高級命中保留 229/255',
    'API-10': '終級命中保留 329/355',
    'API-11': 'NPC 不按 (scene_id, npcid) 误去重',
    'API-12': '非法数据集/路径穿越/任意文件读取被拒绝',
    'API-13': '调用方不能修改底层目录数据',
    'API-14': '不存在编辑/保存/上传/发布接口',
    'API-15': '预览代理安全、页面不指向沙箱 localhost',
}

REQUIRED_WEB_CHECKS = {
    'W-01': '浏览器不请求沙箱 localhost/127.0.0.1',
    'W-02': 'API 不可用时不自动切换假数据',
    'W-03': '前端不得写死固定计数',
    'W-04': '特殊文本只展示不执行（静态半边）',
    'W-05': '加载中/空结果/断连/错误状态（源码半边）',
    'W-06': '网络调用使用相对 URL',
    'H-01': 'API 源码不含变更类路由',
}
REQUIRED_WEB_RUNTIME_CHECKS = {
    'W-10': '入口页面由 web origin 提供且资源为相对路径',
    'W-11': '入口模块可加载且不含沙箱主机',
    'W-12': '列表页拿到自己解析的 {items,total,page,page_size} 信封',
    'W-13': '概览/异常/NPC/地图页面的端点存在',
    'W-14': '详情页能取到单条记录',
    'W-15': 'web origin 能把 /api 代理到复核 API',
    'W-16': 'web origin 接受转发后的 Host/Origin 头',
    'U-01': '交付的前端可用自身工具链成功构建',
    'U-02': '挂载后的应用渲染出可见内容（不是白屏）',
    'U-03': '应用发出的每个请求都成功',
    'U-04': '应用加载期间没有 console 错误',
    'U-05': '仅真实浏览器可做的检查（如实标注未执行）',
}


def outstanding(prefix_map: dict, stage: dict, reason: str) -> list[dict]:
    """Required checks that the stage did not execute, with the reason."""
    executed = {item['check'].split('.')[0] for item in (stage.get('checks') or [])
                if item['status'] in ('pass', 'fail')}
    return [{'check': check_id, 'requirement': text, 'status': 'not_executed', 'reason': reason}
            for check_id, text in sorted(prefix_map.items()) if check_id not in executed]


def git(*args: str) -> str:
    try:
        return subprocess.run(['git', *args], cwd=repo_root(), capture_output=True, text=True,
                              timeout=30).stdout.strip()
    except Exception:  # noqa: BLE001
        return ''


def deliverable_commits(api_sha: str | None, web_sha: str | None) -> dict:
    """Record what H/I revision was actually exercised (empty when nothing landed)."""
    recorded = {}
    paths = {
        'api_contract': 'server/docs/review_browser/API_CONTRACT.md',
        'api_application': 'server/apps/review_api',
        'loader_source': 'server/src/mxsj_catalog',
        'web_page': 'server/apps/review_web',
    }
    for label, path in paths.items():
        entry = {'path': path, 'last_commit': git('log', '-1', '--format=%H', '--', path) or None}
        entry['present'] = (repo_root() / path).exists()
        recorded[label] = entry
    recorded['api_contract']['reviewed_remote_ref'] = git('rev-parse', 'origin/pr-22') or None
    recorded['web_page']['reviewed_remote_ref'] = git('rev-parse', 'origin/pr-24') or None
    if api_sha:
        recorded['api_application']['tested_sha'] = api_sha
    if web_sha:
        recorded['web_page']['tested_sha'] = web_sha
    return recorded


def run_probe(mapping: Path, *, base_url: str | None = None, web_url: str | None = None,
              out_name: str = 'live_api_report.json') -> dict:
    out = TOOLS / 'evidence' / out_name
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(mapping.read_text(encoding='utf-8'))
    command = data.get('startup_command')
    args = [sys.executable, str(PROBE), '--map', str(mapping), '--out', str(out)]
    if web_url:
        args += ['--web-url', web_url]
    if base_url:
        args += ['--base-url', base_url]
    elif command:
        args += ['--start', '--command', command]
    else:
        return {'status': 'not_executed', 'checks': [], 'summary': {},
                'reason': f'{mapping.name} does not record startup_command'}
    completed = subprocess.run(args, cwd=repo_root(), capture_output=True, text=True, timeout=1800)
    if not out.exists():
        return {'status': 'not_executed', 'checks': [], 'summary': {},
                'reason': f'probe produced no report (exit {completed.returncode}): '
                          f'{(completed.stdout + completed.stderr)[-2000:]}'}
    return json.loads(out.read_text())


# --------------------------------------------------------------------------
# web runtime session: real API + real dev server + real front end
# --------------------------------------------------------------------------
def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def wait_for_port(port: int, process: subprocess.Popen, timeout: float = 90.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if process.poll() is not None:
            return False
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def start_process(command: list[str], cwd: Path | None, log_path: Path, env: dict | None = None):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handle = log_path.open('w', encoding='utf-8')
    process = subprocess.Popen(command, cwd=str(cwd) if cwd else None, env=env, stdout=handle,
                               stderr=subprocess.STDOUT, text=True, start_new_session=True)
    process.log_handle = handle
    return process


def stop_process(process) -> None:
    if process is None:
        return
    handle = getattr(process, 'log_handle', None)
    if handle is not None and not handle.closed:
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


def http_get(url: str, timeout: float = 30.0) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': '*/*'}),
                                    timeout=timeout) as response:
            return response.status, response.read(512).decode('utf-8', 'replace')
    except urllib.error.HTTPError as error:
        return error.code, error.read(512).decode('utf-8', 'replace')
    except OSError as error:
        return 0, str(error)


def node_available() -> tuple[bool, str]:
    try:
        version = subprocess.run(['node', '--version'], capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return False, 'node is not installed in this environment'
    match = re.match(r'v(\d+)\.(\d+)', version)
    if not match or (int(match.group(1)), int(match.group(2))) < (22, 6):
        return False, f'node {version} cannot run the probes (needs >= 22.6 for --experimental-strip-types)'
    return True, version


def run_web_runtime() -> dict:
    """Start the real dev server against a real API and drive the real front end."""
    stage = {'stage': 'phase3_web_runtime', 'checks': [], 'commands': [], 'session': {}}
    if not WEB_APP.is_dir():
        stage['status'] = 'not_executed'
        stage['reason'] = 'server/apps/review_web not delivered'
        return stage
    node_ok, node_note = node_available()
    if not node_ok:
        stage['status'] = 'not_executed'
        stage['reason'] = node_note
        return stage
    if not (WEB_APP / 'node_modules').is_dir():
        stage['status'] = 'not_executed'
        stage['reason'] = ('server/apps/review_web/node_modules is not installed (offline sandbox): the '
                           'dev server cannot be started here')
        return stage
    if not (repo_root() / 'server/apps/review_api').is_dir():
        stage['status'] = 'not_executed'
        stage['reason'] = 'server/apps/review_api not delivered, so the page has no backend to proxy to'
        return stage

    mapping = next(iter(sorted(TOOLS.glob('ops_*.json'))), None)
    workdir = Path(tempfile.mkdtemp(prefix='mxsj-web-runtime-'))
    batch = write_temp_batch(workdir / 'batch', default_batch_dir())
    api_port, web_port = free_port(), free_port()
    api_log, web_log = workdir / 'api.log', workdir / 'web.log'
    stage['session'] = {'workdir': str(workdir), 'batch_dir': str(batch), 'api_port': api_port,
                        'web_port': web_port, 'node': node_note}
    api = start_process([PYTHON, str(LAUNCHER), '--batch-dir', str(batch), '--host', '0.0.0.0',
                         '--port', str(api_port)], None, api_log)
    web = None
    try:
        if not wait_for_port(api_port, api):
            stage['status'] = 'not_executed'
            stage['reason'] = ('the review API did not start for the page session: '
                               + '\n'.join(str(api_log.read_text(errors="replace").splitlines()[-5:])))
            return stage
        env = dict(os.environ)
        env['VITE_API_PROXY_TARGET'] = f'http://127.0.0.1:{api_port}'
        env['PORT'] = str(web_port)
        command = ['node', str(WEB_APP / 'node_modules/vite/bin/vite.js'), '--port', str(web_port),
                   '--strictPort']
        stage['commands'].append({'page_start': f'cd server/apps/review_web && VITE_API_PROXY_TARGET='
                                                f'http://127.0.0.1:{api_port} PORT={web_port} npm run dev',
                                  'api_start': f'{PYTHON} server/tools/review_browser_checks/'
                                               f'review_api_launch.py --batch-dir <tmp copy> '
                                               f'--host 0.0.0.0 --port {api_port}'})
        web = start_process(command, WEB_APP, web_log, env)
        if not wait_for_port(web_port, web, 120):
            stage['status'] = 'not_executed'
            stage['reason'] = ('the dev server did not start: '
                               + '\n'.join(web_log.read_text(errors='replace').splitlines()[-5:]))
            return stage
        origin = f'http://127.0.0.1:{web_port}'
        stage['session']['origin'] = origin
        for _ in range(20):
            status, _body = http_get(f'{origin}/api/v1/review/health')
            if status == 200:
                break
            time.sleep(1.0)

        # 1. the endpoints the front end itself declares
        origin_out = workdir / 'web_origin_probe.json'
        subprocess.run(['node', '--experimental-strip-types', str(WEB_PROBE), '--app-dir',
                        str(WEB_APP), '--origin', origin, '--out', str(origin_out)],
                       capture_output=True, text=True, timeout=600)
        stage['commands'].append({'page_contract': f'node --experimental-strip-types '
                                                   f'server/tools/review_browser_checks/web_origin_probe.mjs '
                                                   f'--app-dir server/apps/review_web --origin {origin}'})
        if origin_out.exists():
            payload = json.loads(origin_out.read_text(encoding='utf-8'))
            stage['checks'].extend(payload['checks'])
            stage['session']['frontend_contract'] = payload.get('frontend_contract')
        else:
            for check_id in ('W-10', 'W-11', 'W-12', 'W-13', 'W-14', 'W-15', 'W-16'):
                stage['checks'].append({'check': check_id, 'status': 'not_executed',
                                        'title': REQUIRED_WEB_CHECKS[check_id],
                                        'detail': 'web_origin_probe.mjs produced no report'})

        # 2. the built application, executed against the real API
        ui_out = workdir / 'web_ui_smoke.json'
        subprocess.run(['node', '--experimental-strip-types', str(UI_SMOKE), '--app-dir', str(WEB_APP),
                        '--origin', origin, '--out', str(ui_out)], capture_output=True, text=True,
                       timeout=900)
        stage['commands'].append({'page_render': f'node --experimental-strip-types '
                                                 f'server/tools/review_browser_checks/web_ui_smoke.mjs '
                                                 f'--app-dir server/apps/review_web --origin {origin}'})
        if ui_out.exists():
            payload = json.loads(ui_out.read_text(encoding='utf-8'))
            stage['checks'].extend(payload['checks'])
            stage['session']['rendered'] = payload.get('rendered')
            stage['session']['console'] = payload.get('console', [])[:20]
            stage['session']['requests'] = payload.get('requests', [])[:20]
        else:
            for check_id in ('U-01', 'U-02', 'U-03', 'U-04', 'U-05'):
                stage['checks'].append({'check': check_id, 'status': 'not_executed',
                                        'title': REQUIRED_WEB_CHECKS[check_id],
                                        'detail': 'web_ui_smoke.mjs produced no report'})

        # 3. API-15 against this real page origin (the probe needs a web origin to run it)
        if mapping:
            api15 = run_probe(mapping, base_url=f'http://127.0.0.1:{api_port}', web_url=origin,
                              out_name='live_api_with_web_origin.json')
            stage['api15'] = next((c for c in (api15.get('checks') or []) if c['check'] == 'API-15'), None)
            stage['session']['reprobe_status'] = api15.get('status')
            stage['session']['reprobe_summary'] = api15.get('summary')
    except Exception as error:  # noqa: BLE001 - ledger must survive
        stage['status'] = 'not_executed'
        stage['reason'] = f'{type(error).__name__}: {error}'
        return stage
    finally:
        stop_process(web)
        stop_process(api)

    checks = stage['checks']
    if not checks:
        stage['status'] = 'not_executed'
        stage['reason'] = 'no page check was executed'
    elif any(c['status'] == 'fail' for c in checks) or (
            stage.get('api15') or {}).get('status') == 'fail':
        stage['status'] = 'fail'
    elif any(c['status'] == 'fail' for c in [stage.get('api15')] if c):
        stage['status'] = 'fail'
    else:
        stage['status'] = 'pass'
    return stage


def run_unit_suite() -> dict:
    completed = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'server/tests/review_browser_acceptance',
         '-v'],
        cwd=repo_root(), capture_output=True, text=True, timeout=1800,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    output = completed.stdout + completed.stderr
    lines = output.strip().splitlines()
    ran = next((line for line in reversed(lines) if line.startswith('Ran ')), '')
    skipped = [line for line in lines if 'NOT EXECUTED' in line]
    failures = [line for line in lines if re.match(r'^(FAIL|ERROR): ', line)]
    return {'exit_code': completed.returncode, 'tail': lines[-8:], 'ran': ran,
            'skipped_count': len(skipped), 'skipped_reasons': sorted(set(skipped))[:10],
            'failure_count': len(failures), 'failures': failures[:20],
            'status': 'pass' if completed.returncode == 0 else 'fail'}


def run_command(command: list[str], *, timeout: float = 1800.0) -> dict:
    """Run a command whose only verdict is its exit code and its summary line."""
    completed = subprocess.run(command, cwd=repo_root(), capture_output=True, text=True,
                               timeout=timeout, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    output = (completed.stdout + completed.stderr).strip()
    lines = output.splitlines()
    summary = next((line for line in reversed(lines) if line.startswith('Ran ')), '')
    if not summary:
        summary = next((line for line in reversed(lines)
                        if line.startswith(('OK', 'FAILED', 'checked '))), '')
    return {'command': ' '.join(command), 'exit_code': completed.returncode,
            'summary': summary, 'tail': lines[-5:],
            'status': 'pass' if completed.returncode == 0 else 'fail'}


def counts(stage: dict) -> dict:
    checks = stage.get('checks') or []
    return {'pass': sum(1 for c in checks if c['status'] == 'pass'),
            'fail': sum(1 for c in checks if c['status'] == 'fail'),
            'not_executed': sum(1 for c in checks if c['status'] == 'not_executed'),
            'review': sum(1 for c in checks if c['status'] == 'review')}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path,
                        default=TOOLS / 'evidence' / 'acceptance_report.json')
    parser.add_argument('--api-sha', default=None,
                        help='exact Agent H commit exercised (the integration merge revision)')
    parser.add_argument('--web-sha', default=None, help='exact Agent I commit exercised')
    parser.add_argument('--skip-web-runtime', action='store_true',
                        help='skip starting the dev server (static + API stages only)')
    args = parser.parse_args(argv)

    baseline = verify_data_baseline.run()
    contract_state = {
        'api_contract_present': CONTRACT.is_file(),
        'web_app_present': WEB_APP.is_dir(),
        'operations_map': None,
    }
    mapping = next(iter(sorted(TOOLS.glob('ops_*.json'))), None)
    contract_state['operations_map'] = str(mapping.relative_to(repo_root())) if mapping else None

    if contract_state['api_contract_present'] and mapping:
        api = run_probe(mapping)
    else:
        reason = ('server/docs/review_browser/API_CONTRACT.md not delivered'
                  if not contract_state['api_contract_present'] else
                  'no operations map (server/tools/review_browser_checks/ops_*.json) binding the contract')
        api = {'status': 'not_executed', 'checks': [], 'summary': {'total': 0, 'pass': 0, 'fail': 0,
                                                                   'not_executed': 0, 'executed': 0},
               'reason': reason}
    web = scan_web()
    runtime = ({'status': 'not_executed', 'checks': [], 'reason': 'skipped by --skip-web-runtime'}
               if args.skip_web_runtime else run_web_runtime())
    units = run_unit_suite()
    architecture = run_command([sys.executable, '-m', 'unittest', 'discover', '-s',
                                'server/tests/architecture', '-q'])
    csv_check = run_command([sys.executable, 'server/tools/export_review_csv.py', '--check'])

    # The page session also re-runs the API probe with a real web origin so that
    # API-15 (proxy safety) is executed rather than skipped.
    api15 = runtime.get('api15')
    if api15 and api15.get('status') in ('pass', 'fail') and (api.get('checks') or None):
        api['checks'] = [c for c in api['checks'] if c['check'] != 'API-15'] + [api15]
    api_checks = api.get('checks') or []
    if api_checks:
        if any(c['status'] == 'fail' for c in api_checks):
            api['status'] = 'fail'
        elif any(c['status'] == 'not_executed' for c in api_checks):
            api['status'] = 'incomplete'
        else:
            api['status'] = 'pass'

    report = {
        'stage': 'review_tool_acceptance_ledger',
        'generated_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'repository': {'branch': git('rev-parse', '--abbrev-ref', 'HEAD'), 'head': git('rev-parse', 'HEAD'),
                       'status_short': git('status', '--porcelain')},
        'environment': {'python': sys.version.split()[0], 'interpreter_used': PYTHON,
                        'node': subprocess.run(['node', '--version'], capture_output=True,
                                               text=True).stdout.strip() or None,
                        'browser_engine': 'none available (only npm/pypi/GitHub are reachable, so no '
                                          'browser build can be installed)'},
        'tested_deliverables': deliverable_commits(args.api_sha, args.web_sha),
        'stages': {
            'phase1_data_baseline': {'status': baseline['status'], **counts(baseline),
                                     'checks': baseline['checks']},
            'phase2_live_api': {'status': api['status'], **counts(api), 'reason': api.get('reason'),
                                'checks': api.get('checks', [])},
            'phase3_static_page': {'status': web['status'], **counts(web), 'checks': web['checks'],
                                   'result_meaning': web.get('status_meaning')},
            'phase3_web_runtime': {'status': runtime.get('status'), **counts(runtime),
                                   'reason': runtime.get('reason'),
                                   'session': runtime.get('session', {}),
                                   'commands': runtime.get('commands', []),
                                   'api15': runtime.get('api15'),
                                   'checks': runtime.get('checks', [])},
            'unittest_suite': units,
            'original_architecture_suite': architecture,
            'csv_exporter_check': csv_check,
        },
    }
    required_missing = [c['check'] for c in (api.get('checks') or []) if c['status'] == 'not_executed']
    api_reason = api.get('reason') or 'live loader/API acceptance not executed'
    web_reason = ('server/apps/review_web not delivered'
                  if not contract_state['web_app_present'] else 'static page scan not executed')
    runtime_reason = runtime.get('reason') or 'the web runtime session was not executed'
    runtime_checks = list(runtime.get('checks') or [])
    if api15:
        runtime_checks.append(api15)
    report['required_check_inventory'] = {
        'api': [{'check': check_id, 'requirement': text} for check_id, text in sorted(REQUIRED_API_CHECKS.items())],
        'web_static': [{'check': check_id, 'requirement': text}
                       for check_id, text in sorted(REQUIRED_WEB_CHECKS.items())],
        'web_runtime': [{'check': check_id, 'requirement': text}
                        for check_id, text in sorted(REQUIRED_WEB_RUNTIME_CHECKS.items())],
    }
    report['outstanding_not_executed'] = {
        'api': outstanding(REQUIRED_API_CHECKS, api, api_reason),
        'web_static': outstanding(REQUIRED_WEB_CHECKS, web, web_reason),
        'web_runtime': [c for c in runtime_checks if c['status'] == 'not_executed'] or
                       outstanding(REQUIRED_WEB_RUNTIME_CHECKS, {'checks': runtime_checks}, runtime_reason),
    }
    report['summary'] = {
        'phase1': baseline['status'],
        'phase2_live_api': api['status'],
        'phase3_static_page': web['status'],
        'phase3_web_runtime': runtime.get('status'),
        'new_acceptance_suite': units['status'],
        'original_architecture_suite': architecture['status'],
        'csv_exporter_check': csv_check['status'],
        'test_counts': {'original_architecture_tests': architecture.get('summary'),
                        'new_acceptance_suite': units.get('ran'),
                        'note': 'the new acceptance suite is deliberately counted separately from the '
                                'original architecture tests'},
        'integration_acceptance_complete': bool(
            baseline['status'] == 'pass' and api['status'] == 'pass' and web['status'] == 'pass'
            and runtime.get('status') == 'pass' and units['status'] == 'pass'
            and architecture['status'] == 'pass' and csv_check['status'] == 'pass'),
        'not_executed_required_checks': required_missing,
        'outstanding_api_checks': len(report['outstanding_not_executed']['api']),
        'outstanding_web_static_checks': len(report['outstanding_not_executed']['web_static']),
        'outstanding_web_runtime_checks': len(report['outstanding_not_executed']['web_runtime']),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                        encoding='utf-8')
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))
    try:
        shown = args.out.resolve().relative_to(repo_root())
    except ValueError:
        shown = args.out
    print(f'report: {shown}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
