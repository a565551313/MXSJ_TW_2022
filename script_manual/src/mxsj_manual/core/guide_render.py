"""Safe Qt rich text presentation of task guides (no game/source execution)."""

from __future__ import annotations

from urllib.parse import urlencode

from .render import REVIEWS, text


def guide_html(guide):
    result = (
        f"<h1>{text(guide['title'])}</h1><p>{text(guide['summary'])}</p>"
        f"<p><b>专题草稿 · {text(guide['author'])}编排，未独立审核</b></p>"
        "<p>引用模块通过不等于专题通过；修改建议不是运行结果。</p>"
    )
    if guide["stale_dependencies"]:
        result += (
            "<p><b>正文已变化，旧步骤锚点已禁用：</b>"
            + text(" / ".join(guide["stale_dependencies"]))
            + "</p>"
        )
    result += (
        "<h2>开始前</h2><ul>"
        + "".join(f"<li>{text(x)}</li>" for x in guide["prerequisites"])
        + "</ul>"
    )
    result += (
        "<h2>本专题步骤</h2><ol>"
        + "".join(
            f'<li><a href="#guide-step-{i}">{text(step["title"])}</a></li>'
            for i, step in enumerate(guide["steps"], 1)
        )
        + "</ol>"
    )
    for index, step in enumerate(guide["steps"], 1):
        result += f'<h2 id="guide-step-{index}">{index}. {text(step["title"])}</h2>'
        for label, field in (
            ("候选中的流程/分支", "explanation"),
            ("修改入口与建议（待验证）", "change"),
            ("应如何检查（不是已执行）", "check"),
        ):
            result += f"<h3>{label}</h3><p>{text(step[field])}</p>"
        for ref in step["references"]:
            result += f"<h4>{text(ref['path'])} → {text(ref['function'])}</h4>"
            result += f"<p>引用模块：{text(REVIEWS[ref['review_status']])}"
            result += f" · {text(ref['reviewer'] or '无有效审核者')}</p>"
            result += f"<p>专题绑定正文SHA：{text(ref['annotation_sha256'])}</p>"
            if not ref["binding_current"]:
                result += "<p>引用已过期；请先更新专题，不按新正文猜接旧结论。</p>"
                continue
            link = urlencode(
                {
                    "module": ref["module_id"],
                    "section": "functions",
                    "function": ref["function"],
                }
            )
            result += f'<p><a href="#{text(link)}">打开函数、调用线索和分支</a></p>'
            for evidence in ref["evidence"]:
                link = urlencode(
                    {
                        "module": ref["module_id"],
                        "section": "evidence",
                        "evidence": evidence["id"],
                    }
                )
                result += f'<p><a href="#{text(link)}">证据 {text(evidence["id"])}</a>'
                result += (
                    f" · {text(evidence['path'])} 物理行"
                    f" {evidence['start_line']}–{evidence['end_line']}</p>"
                )
                result += f"<p>来源SHA：{text(evidence['sha256'])}</p>"
                if evidence["verified"]:
                    result += (
                        "<pre>"
                        + "\n".join(
                            f"{line['number']}: {text(line['text'])}"
                            for line in evidence["lines"]
                        )
                        + "</pre>"
                    )
                    if evidence.get("truncated"):
                        result += "<p>仅预览前60物理行，非完整来源。</p>"
                else:
                    result += (
                        "<p>本次未校验/加载原文；可用文件菜单核对仓库证据。"
                        "以上是引用文件物理行，摘录L/R编号是候选原行。</p>"
                    )
    result += (
        "<h2>尚未确认 / 不包含</h2><ul>"
        + "".join(f"<li>{text(x)}</li>" for x in guide["limitations"])
        + "</ul>"
    )
    return result
