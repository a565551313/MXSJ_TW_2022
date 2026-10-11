#!/usr/bin/env python3
"""Inventory all script.fls entries without executing game scripts.

Generated outputs are research indexes, NOT a claim of complete server logic.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import zlib

SERVER = Path(__file__).resolve().parents[1]
REPO = SERVER.parent
sys.path.insert(0, str(REPO))
from tools.decompiler.batch_decompile import Py25MarshalTranspiler, XTABS

CATALOG = REPO / 'work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl'
OUT = SERVER / 'docs/catalog'


def escaped(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)[1:-1].replace('|', '\\|')


def valid_path(value: str | None) -> bool:
    return bool(value and value.startswith('script/') and value.endswith('.py')
                and not any(ord(c) < 32 for c in value)
                and not any(p in ('', '.', '..') for p in value.split('/')))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    historical = [json.loads(line) for line in CATALOG.read_text(encoding='utf-8').splitlines()]
    lookup = {r['index']: r for r in historical}
    archive = (REPO / 'data/script.fls').read_bytes()
    if archive[:4] != b'0SLF':
        raise ValueError('not a script.fls 0SLF archive')
    count, index_offset = struct.unpack_from('<II', archive, 4)
    keys_db = json.loads((REPO / 'tools/decompiler/script_fls_keys.json').read_text(encoding='utf-8'))
    rows = []
    for idx in range(count):
        old = lookup.get(idx, {})
        old_name = old.get('filename', '').replace('\\', '/')
        row = {
            'entry_index': idx,
            'historical_filename': old_name,
            'historical_decode_status': old.get('status', 'missing'),
            'historical_function_names': old.get('func_names', []),
            'function_names_origin': 'historical decoder; not revalidated in this pass',
            'current_filename': None,
            'current_check': 'unverified',
            'semantic_review': 'not_reviewed_in_this_pass',
        }
        try:
            eid, a, b, c = struct.unpack_from('<IIII', archive, index_offset + idx * 16)
            size = ((a * eid + 0xDF25E) & 0xffffffff) ^ b
            offset = ((b * idx * 0xF718FE + 0xD59D16C) & 0xffffffff) ^ c
            if offset + size > len(archive):
                raise ValueError('archive payload out of bounds')
            exp = zlib.decompress(archive[offset:offset + size])
            info = keys_db[str(idx)]
            keys, bounds = info['keys'], info['bounds']
            pts = [0] + bounds + [len(exp)]
            dec = b''.join(exp[pts[i]:pts[i+1]].translate(XTABS[keys[i]]) for i in range(5))
            tr = Py25MarshalTranspiler(dec, exp, keys, bounds)
            tr.transpile_object()
            row['current_filename'] = tr.filename
            row['current_check'] = ('marshal_transpiled_filename_checked' if tr.filename else 'marshal_transpiled_no_filename')
        except Exception as exc:
            row['error'] = str(exc)[:400]
        name = row['current_filename'] or old_name
        row['index_filename'] = name
        row['path_origin'] = 'current_archive' if row['current_filename'] else 'historical_fallback'
        row['path_quality'] = 'structurally_valid' if valid_path(name) else 'needs_review'
        row['historical_filename_differs'] = bool(row['current_filename'] and row['current_filename'] != old_name)
        basename = name.rsplit('/', 1)[-1]
        if '/data/' in name:
            hint = 'data_candidate'
        elif '/lib/' in name or '/pub2/' in name:
            hint = 'library_or_framework_candidate'
        elif basename.startswith('net') or any(f.startswith(('C2S', 'C2GS', 'S2C', 'GS2C')) for f in row['historical_function_names']):
            hint = 'protocol_candidate'
        elif any(s in name for s in ('/view/', '/dialog/', '/delegate/', '/ui', '/render/')):
            hint = 'client_presentation_candidate'
        elif '/model/' in name:
            hint = 'client_model_candidate'
        else:
            hint = 'unclassified'
        row['heuristic_kind'] = hint
        rows.append(row)
        if (idx + 1) % 500 == 0:
            print(f'Checked {idx + 1}/{count}', flush=True)
    (OUT/'script_entries.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows), encoding='utf-8')
    summary = {
        'schema_version': 1,
        'archive': 'data/script.fls',
        'archive_sha256': hashlib.sha256(archive).hexdigest(),
        'entry_count': count,
        'current_checks': dict(collections.Counter(r['current_check'] for r in rows)),
        'path_quality': dict(collections.Counter(r['path_quality'] for r in rows)),
        'path_origin': dict(collections.Counter(r['path_origin'] for r in rows)),
        'historical_filename_changes': sum(r['historical_filename_differs'] for r in rows),
        'heuristic_kinds': dict(collections.Counter(r['heuristic_kind'] for r in rows)),
        'meaning': 'Full entry coverage only. No full-source decompilation or full gameplay verification.',
    }
    # Describe sibling archives but do not infer skill/effect server semantics from names.
    summary['other_archives'] = []
    for path in sorted((REPO/'data').glob('*.fls')):
        if path.name == 'script.fls':
            continue
        header = path.read_bytes()[:12]
        summary['other_archives'].append({
            'path': str(path.relative_to(REPO)), 'magic': repr(header[:4]),
            'entry_count': struct.unpack_from('<I', header, 4)[0] if header[:4] == b'0SLF' else None,
            'scope': 'header only; payload semantics not reviewed in this pass',
        })
    manifest = json.loads((REPO/'tools/decompiler/output/data_fls/manifest.json').read_text())
    summary['data_fls_manifest_entries'] = len(manifest['entries'])
    summary['data_fls_python_sources'] = len(list((REPO/'tools/decompiler/output/data_fls').rglob('*.py')))
    summary['script_fls_existing_python_sources'] = len(list((REPO/'tools/decompiler/output/script_fls').rglob('*.py')))
    (OUT/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    # Complete structural index: do not silently omit damaged paths or root files.
    lines = ['# 全量材料目录索引', '',
        '这是目录/函数名层面的材料导航，**不是完整服务端功能证明**。优先使用当前归档转译出的文件名；失败时保留历史目录并标注。', '',
        f"- 归档条目：{count}；当前文件名检查：{summary['current_checks']}。",
        f"- 历史文件名与当前不一致：{summary['historical_filename_changes']}；路径形态异常：{summary['path_quality'].get('needs_review', 0)}。",
        '- 每条记录与完整历史函数名列表见 `script_entries.jsonl`；函数名本轮未逐一重新验证。', '']
    for prefix in ['script/', 'script/mxgame/', 'script/mxgame/activity/', 'script/yard/', 'script/dialog/', 'script/data/']:
        groups = collections.defaultdict(list)
        for row in rows:
            path = row['index_filename']
            if not path.startswith(prefix):
                continue
            tail = path[len(prefix):]
            key = tail.split('/')[0] if '/' in tail else '(direct files)'
            groups[key].append(row)
        summary.setdefault('directory_groups', {})[prefix] = {
            'subdirectories': len([k for k in groups if k != '(direct files)']),
            'direct_files': len(groups.get('(direct files)', [])),
            'entries': sum(len(v) for v in groups.values()),
        }
        lines.extend([f'## `{prefix}`', '', '| 分支 | 条目数 | 代表条目 | 历史回退数 |', '|---|---:|---|---:|'])
        for name, values in sorted(groups.items()):
            ids = ', '.join(str(v['entry_index']) for v in values[:5])
            lines.append(f"| `{escaped(name)}` | {len(values)} | {ids} | {sum(v['path_origin']=='historical_fallback' for v in values)} |")
        lines.append('')
    for title, predicate in [
        ('根目录独立脚本', lambda r: r['index_filename'].startswith('script/') and r['index_filename'].count('/') == 1),
        ('静态数据目录直接文件', lambda r: r['index_filename'].startswith('script/data/') and r['index_filename'].count('/') == 2),
        ('待核实条目：转译失败或路径异常', lambda r: r['current_check']!='marshal_transpiled_filename_checked' or r['path_quality']=='needs_review'),
    ]:
        lines.extend([f'## {title}', '', '| 条目 | 文件 | 状态/来源 |', '|---:|---|---|'])
        for r in rows:
            if predicate(r):
                lines.append(f"| {r['entry_index']} | `{escaped(r['index_filename'])}` | {r['current_check']} / {r['path_origin']} |")
        lines.append('')
    (OUT/'DIRECTORIES.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    (OUT/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
