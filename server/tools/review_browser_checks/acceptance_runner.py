#!/usr/bin/env python3
"""Run every review-tool acceptance stage and emit one ledger.

Stages
------
1. Phase 1  independent data baseline (``verify_data_baseline.py``)
2. Phase 2  live loader/API semantics (``probe_live_api.py``) - only when Agent H's
   contract, application and the acceptor's operation map exist
3. Phase 3  static page policy (``scan_review_web.py``) - only when Agent I's page exists
4. the acceptance unittest suite (``server/tests/review_browser_acceptance``)

Nothing is ever reported as passed unless it actually ran; missing deliverables
produce ``not_executed`` entries with the reason and are listed in the summary.

Usage:
    PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py \
        [--out server/tools/review_browser_checks/evidence/acceptance_report.json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify_data_baseline  # noqa: E402
from batch_fixture import repo_root  # noqa: E402
from scan_review_web import scan as scan_web  # noqa: E402

TOOLS = Path(__file__).resolve().parent
PROBE = TOOLS / 'probe_live_api.py'
CONTRACT = repo_root() / 'server/docs/review_browser/API_CONTRACT.md'
WEB_APP = repo_root() / 'server/apps/review_web'


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


def deliverable_commits() -> dict:
    """Record what H/I revision was actually exercised (empty when nothing landed)."""
    recorded = {}
    for label, path in (('api_contract', 'server/docs/review_browser/API_CONTRACT.md'),
                        ('api_application', 'server/apps/review_api'),
                        ('api_source', 'server/src/review'),
                        ('web_page', 'server/apps/review_web')):
        if (repo_root() / path).exists():
            recorded[label] = {'path': path, 'last_commit': git('log', '-1', '--format=%H', '--', path)}
        else:
            recorded[label] = {'path': path, 'last_commit': None, 'present': False}
    return recorded


def run_probe(mapping: Path) -> dict:
    out = TOOLS / 'evidence' / 'live_api_report.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(mapping.read_text(encoding='utf-8'))
    command = data.get('startup_command')
    args = [sys.executable, str(PROBE), '--map', str(mapping), '--out', str(out)]
    if command:
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


def run_unit_suite() -> dict:
    completed = subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'server/tests/review_browser_acceptance', '-q'],
        cwd=repo_root(), capture_output=True, text=True, timeout=1800,
        env={**__import__('os').environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    tail = (completed.stdout + completed.stderr).strip().splitlines()
    return {'exit_code': completed.returncode, 'tail': tail[-6:],
            'status': 'pass' if completed.returncode == 0 else 'fail'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path,
                        default=TOOLS / 'evidence' / 'acceptance_report.json')
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
    units = run_unit_suite()

    def counts(stage: dict) -> dict:
        checks = stage.get('checks') or []
        return {'pass': sum(1 for c in checks if c['status'] == 'pass'),
                'fail': sum(1 for c in checks if c['status'] == 'fail'),
                'not_executed': sum(1 for c in checks if c['status'] == 'not_executed')}

    report = {
        'stage': 'review_tool_acceptance_ledger',
        'generated_utc': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'repository': {'branch': git('rev-parse', '--abbrev-ref', 'HEAD'), 'head': git('rev-parse', 'HEAD'),
                       'status_short': git('status', '--porcelain')},
        'tested_deliverables': deliverable_commits(),
        'stages': {
            'phase1_data_baseline': {'status': baseline['status'], **counts(baseline),
                                     'checks': baseline['checks']},
            'phase2_live_api': {'status': api['status'], **counts(api), 'reason': api.get('reason'),
                                'checks': api.get('checks', [])},
            'phase3_static_page': {'status': web['status'], **counts(web), 'checks': web['checks']},
            'unittest_suite': units,
        },
    }
    required_missing = [c['check'] for c in (api.get('checks') or [])
                        if c['status'] == 'not_executed']
    api_reason = api.get('reason') or 'live loader/API acceptance not executed'
    web_reason = ('server/apps/review_web not delivered'
                  if not contract_state['web_app_present'] else 'static page scan not executed')
    report['required_check_inventory'] = {
        'api': [{'check': check_id, 'requirement': text} for check_id, text in sorted(REQUIRED_API_CHECKS.items())],
        'web': [{'check': check_id, 'requirement': text} for check_id, text in sorted(REQUIRED_WEB_CHECKS.items())],
    }
    report['outstanding_not_executed'] = {
        'api': outstanding(REQUIRED_API_CHECKS, api, api_reason),
        'web': outstanding(REQUIRED_WEB_CHECKS, web, web_reason),
    }
    report['summary'] = {
        'phase1': baseline['status'],
        'phase2_live_api': api['status'],
        'phase3_static_page': web['status'],
        'unittest_suite': units['status'],
        'integration_acceptance_complete': bool(
            api['status'] == 'pass' and web['status'] == 'pass' and units['status'] == 'pass'),
        'not_executed_required_checks': required_missing,
        'outstanding_api_checks': len(report['outstanding_not_executed']['api']),
        'outstanding_web_checks': len(report['outstanding_not_executed']['web']),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                        encoding='utf-8')
    print(json.dumps({k: v for k, v in report['summary'].items()}, ensure_ascii=False, indent=2))
    print(f'report: {args.out.relative_to(repo_root())}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
