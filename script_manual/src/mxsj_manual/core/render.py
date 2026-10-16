from __future__ import annotations

from html import escape
from urllib.parse import quote

CONFIDENCE = {
    "extracted": "自动提取",
    "inferred": "推测待核实",
    "static_reviewed": "作者静态核对",
    "runtime_verified": "作者实机记录",
}
REVIEWS = {
    "unannotated": "尚未编写",
    "pending": "待审核",
    "accepted": "审核通过",
    "changes_requested": "要求修改",
    "stale_review": "审核已过期",
}
SOURCE_STATUS = {
    "metadata_only": "仅元数据",
    "historical_unverified_origin": "历史稿·原包对应未验证",
    "recovered_partial": "部分恢复·存在缺失",
    "recovered_complete_not_original": "完整恢复候选·非原始源码",
    "native_origin_checked_not_semantics": "已核原生来源·非语义验收",
}


def text(value):
    return escape(str(value), quote=True)


def claim_html(claim):
    refs = " / ".join(claim["evidence"]) or "无证据，待补"
    return (
        f"<p><b>[{text(CONFIDENCE[claim['confidence']])}]</b> "
        f"{text(claim['text'])}<br><small>证据：{text(refs)}</small></p>"
    )


def review_label(row):
    label = REVIEWS[row["review_status"]]
    review = row.get("review")
    if review:
        label += "（A代审）" if review["reviewer"] == "A_delegate" else "（H）"
    return label


def detail_html(row, section="overview"):
    annotation = row["annotation"]
    head = (
        f"<h2>{text(row['path'] or '路径不可用')}</h2>"
        f"<p>{text(review_label(row))} · 负责人 {text(row['owner'])}"
        f" · {text(row['vm'])} · 条目 {row['entry_index']}</p>"
    )
    review = row.get("review")
    if review:
        head += (
            "<h3>审核记录（过期时不计通过）</h3><p>"
            + text(review["note"])
            + "</p><p>授权："
            + text(review.get("delegation", "H独立审核流程"))
            + "</p><p>审核绑定正文SHA256："
            + text(review["annotation_sha256"])
            + "</p>"
        )
    if annotation is None:
        return head + (
            "<p>这里只登记了目录元数据，尚未解释模块功能。</p>"
            "<p>未填写不等于没有函数、调用或资源依赖。</p>"
            + "".join(f"<p>{text(f['name'])}</p>" for f in row["functions"])
        )
    head += f"<p><b>{text(SOURCE_STATUS[annotation['source_status']])}</b></p>"
    if section == "overview":
        return (
            head
            + claim_html(annotation["purpose"])
            + "<h3>限制与风险</h3>"
            + "".join(f"<p>• {text(item)}</p>" for item in annotation["limitations"])
            + "<h3>关键词</h3><p>"
            + text(" · ".join(annotation["keywords"]))
            + "</p>"
        )
    if section == "functions":
        result = head + "<p>函数清单是已整理子集；空调用列表不证明没有调用。</p>"
        for index, function in enumerate(annotation["functions"]):
            result += (
                f'<h3 id="function-{index}">{text(function["name"])}</h3>'
                f"<pre>{text(function['signature'] or '签名未确认')}</pre>"
                + claim_html(function["summary"])
            )
            result += (
                "<p>静态调用线索："
                + text(" / ".join(function["calls"]) or "尚未整理")
                + "</p>"
            )
            for branch in function["branches"]:
                result += f"<h4>分支：{text(branch['condition'])}</h4>" + claim_html(
                    branch["effect"]
                )
        return result
    if section == "resources":
        result = head + "<h3>上下游关系（按证据标注，不自动推定）</h3>"
        for relation in annotation["relationships"]:
            direction = "上游" if relation["direction"] == "upstream" else "下游"
            result += f"<h4>{direction} · {text(relation['kind'])}</h4>"
            result += f"<p>{text(relation['symbol'] or '符号未确认')}</p>"
            target = relation["module"]
            if target:
                identity = f"{target['archive_sha256']}:{target['entry_index']}"
                result += f'<a href="#module={quote(identity)}">条目 '
                result += f"{target['entry_index']}</a>"
            result += claim_html(relation["summary"])
        result += "<h3>关联文件 / 配置 / 布局</h3>"
        for item in annotation["resources"]:
            result += f"<h4>{text(item['kind'])} · {text(item['target'])}</h4>"
            result += claim_html(item["summary"])
        result += "<h3>修改入口问答</h3>"
        for guide in annotation["modification_guides"]:
            result += f"<h4>{text(guide['question'])}</h4>" + claim_html(
                guide["answer"]
            )
        for related in annotation["related_modules"]:
            identity = f"{related['archive_sha256']}:{related['entry_index']}"
            result += f'<p><a href="#module={quote(identity)}">关联条目 '
            result += f"{related['entry_index']}</a>（点击跳转，非已确认调用）</p>"
        return result
    result = head + "<h3>证据来源（只读，不执行）</h3>"
    result += f"<p>本次加载校验：{text(row['evidence_status'])}</p>"
    for source in annotation["sources"]:
        result += (
            f"<h4>{text(source['id'])}</h4><p>{text(source['path'])}</p>"
            f"<pre>SHA256 {text(source['sha256'])}</pre><p>{text(source['note'])}</p>"
        )
    for evidence in annotation["evidence"]:
        result += f'<p id="evidence-{text(evidence["id"])}">{text(evidence["id"])} → '
        result += f'{text(evidence["source_id"])} '
        result += f"L{evidence['start_line']}–{evidence['end_line']}</p>"
    return result
