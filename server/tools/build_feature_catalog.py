#!/usr/bin/env python3
"""Build reviewable work-package cards from explicit specs and full material index."""
from __future__ import annotations
import collections
import json
import os
from pathlib import Path
import re

SERVER = Path(__file__).resolve().parents[1]
DOCS = SERVER / 'docs'


def display(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)[1:-1].replace('|', '\\|')


def main() -> int:
    rows = [json.loads(line) for line in (DOCS/'catalog/script_entries.jsonl').read_text(encoding='utf-8').splitlines()]
    lookup = {r['entry_index']: r for r in rows}
    specs = json.loads((DOCS/'feature_specs.json').read_text(encoding='utf-8'))['features']
    summary = json.loads((DOCS/'catalog/summary.json').read_text(encoding='utf-8'))
    owners = {m['module'] for m in json.loads((DOCS/'source_map.json').read_text())['modules']}
    links = collections.defaultdict(list)
    feature_maps = []
    seen_ids = set()
    cards = DOCS/'features'
    cards.mkdir(exist_ok=True)
    lines = ['# 二级/三级子系统与接口缺口清单', '',
        '**上一版21项是一级责任区，不是完整玩法清单。这里展开工作包，不把目录数当玩法数。**', '',
        f"- 全量索引覆盖 {summary['entry_count']} 个 script.fls 条目；见[原始索引与异常清单](catalog/DIRECTORIES.md)。",
        f"- 当前已细分 {len(specs)} 个跨目录工作包；包含客户端材料线索和服务端新增工程要求，并不代表{len(specs)}套原版逻辑已还原。",
        '- `contracts.py` 仍只有上一版起步用例。本页新增接口为**文字级设计建议，未生成可执行方法、未冻结字段**。',
        '- 后续代码目录/迁移/跨域事务需按这些工作包进一步细分；本次不盲目制造未核实的业务实现。', '',
        '| 工作包 | 当前责任区 | 客户端材料命中 | 接口起点（新设计） |', '|---|---|---:|---|']
    for spec in specs:
        key = spec['feature_id']
        if key in seen_ids or not re.fullmatch(r'[a-z_]+\.[a-z_]+', key):
            raise ValueError(f'invalid or duplicate feature id {key}')
        seen_ids.add(key)
        if spec['owner_module'] not in owners:
            raise ValueError(f'unknown owner {spec["owner_module"]}')
        for idx in spec['primary_entries']:
            if idx not in lookup:
                raise ValueError(f'unknown entry {idx}')
        matches = {idx: lookup[idx] for idx in spec['primary_entries']}
        for row in rows:
            if any(row['index_filename'].startswith(p) for p in spec['source_prefixes']):
                matches[row['entry_index']] = row
        if not matches:
            raise ValueError(f'no source references: {key}')
        entry_ids = sorted(matches)
        for idx in entry_ids:
            links[idx].append(key)
        feature_maps.append({'feature_id':key,'owner_module':spec['owner_module'],'entry_indices':entry_ids,
                             'basis':'explicit entry references and current/fallback filename prefixes; NOT semantic ownership proof',
                             'proposed_independent_module':spec['proposed_independent_module']})
        lines.append(f"| [{spec['title']}](features/{key}.md) | `{spec['owner_module']}` | {len(matches)} | `{spec['proposed_api']}` |")
        text=[f"# {spec['title']}", '', f"工作包：`{key}`；当前归口：`{spec['owner_module']}`。负责人待分配。", '',
              '**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**', '', '本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。', '', '## 职责与边界', '',
              spec['notes'] or '具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。', '',
              '## 接口设计起点', '', f"`{spec['proposed_api']}`", '',
              '这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。',
              '业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。',
              '不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。', '']
        if spec['proposed_independent_module']:
            text+=['## 一级目录拆分建议', '',
                   f"建议评审独立模块 `{spec['proposed_independent_module']}`。当前仍在原责任区研究，尚未创建该独立实现，也没有默认批准跨域写入。", '']
        text+=['## 客户端材料清单', '',
               '命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。', '',
               '| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |', '|---:|---|---|---|']
        for idx in entry_ids:
            row=matches[idx]
            funcs=[f for f in row['historical_function_names'] if f.startswith(('C2S','C2GS','S2C','GS2C'))][:6]
            text.append(f"| {idx} | `{display(row['index_filename'])}` | {row['current_check']} / {row['path_origin']} / {row['path_quality']} | {display(', '.join(funcs))} |")
        text+=['', '## 独立交付要求', '',
               '- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。',
               '- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。',
               '- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。',
               '- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。',
               '- 回填代码和测试路径、完成状态及原客户端验证样本。', '']
        (cards/f'{key}.md').write_text('\n'.join(text),encoding='utf-8')
    lines += ['', '## 不要遗漏活动的独立分支', '',
              '下面展开当前索引里全部活动分支，包括公共框架、测试和历史活动；不能把每个目录都算成一个独立线上玩法。', '',
              '| 分支 | 材料条目数 | 代表条目 |', '|---|---:|---|']
    activity_groups=collections.defaultdict(list)
    prefix='script/mxgame/activity/'
    for r in rows:
        if r['index_filename'].startswith(prefix):
            rest=r['index_filename'][len(prefix):]
            activity_groups[rest.split('/')[0]].append(r['entry_index'])
    for name, ids in sorted(activity_groups.items()):
        lines.append(f"| `{display(name)}` | {len(ids)} | {', '.join(map(str,ids[:6]))} |")
    lines += ['', '## 覆盖与剩余项', '',
              f"{len(specs)}个工作包引用了 {len(links)} 个不同条目；剩余 {len(rows)-len(links)} 个尚未映射到这些工作包。",
              '未映射不等于缺失玩法：其中可能是界面、通用库、渲染、原生模块绑定、异常条目，也可能确实是尚漏的玩法。完整ID清单见 `catalog/entry_feature_map.jsonl`。',
              '每个条目均有记录，未匹配项保留空工作包列表，不用“其他”掩盖未分析内容。', '']
    (DOCS/'SUBSYSTEMS.md').write_text('\n'.join(lines),encoding='utf-8')
    (DOCS/'catalog/feature_material_map.json').write_text(json.dumps(feature_maps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (DOCS/'catalog/entry_feature_map.jsonl').write_text(''.join(json.dumps({'entry_index':r['entry_index'],'feature_ids':links.get(r['entry_index'], [])},ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
    for owner in sorted(owners):
        base=SERVER/'src/mxsj_server/modules'/owner
        title=['# 子系统工作包', '', '起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。', '', '| 工作包 | 接口草案 |', '|---|---|']
        for spec in specs:
            if spec['owner_module']==owner:
                relative=os.path.relpath(cards/f"{spec['feature_id']}.md",base)
                title.append(f"| [{spec['title']}]({relative}) | `{spec['proposed_api']}` |")
        (base/'FEATURES.md').write_text('\n'.join(title)+'\n',encoding='utf-8')
    print(f'Feature cards: {len(specs)}; mapped entries: {len(links)}; unmapped entries: {len(rows)-len(links)}; activity branches: {len(activity_groups)}')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
