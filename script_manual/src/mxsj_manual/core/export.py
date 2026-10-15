from __future__ import annotations

import base64
import hashlib
import json
from importlib.resources import files
from pathlib import Path

from mxsj_manual import __version__

from .io import ManualError, digest


def _sha_policy(content):
    value = base64.b64encode(hashlib.sha256(content.encode("utf-8")).digest()).decode()
    return f"'sha256-{value}'"


def render_site(catalog):
    assets = files("mxsj_manual").joinpath("assets")
    css = assets.joinpath("style.css").read_text(encoding="utf-8")
    javascript = assets.joinpath("manual.js").read_text(encoding="utf-8")
    data = json.dumps(catalog.payload(), ensure_ascii=False, separators=(",", ":"))
    for value in "<>&\u2028\u2029":
        data = data.replace(value, f"\\u{ord(value):04x}")
    policy = (
        f"default-src 'none'; script-src {_sha_policy(javascript)}; "
        f"style-src {_sha_policy(css)}; base-uri 'none'; form-action 'none'"
    )
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="{policy}">
<title>MXSJ 客户端脚本开发手册 · 阶段样板</title>
<style>{css}</style></head><body>
<header><h1>MXSJ / 客户端脚本手册 <span class="badge">阶段样板 · 非全量</span></h1>
<p id="version"></p><div id="stats"></div></header>
<div class="workspace"><aside><label for="query">搜索路径 / 中文功能 / 函数名</label>
<input id="query" type="search"
placeholder="例如：公告、login/mainpage、refreshbulletin">
<select id="domain" aria-label="领域"><option value="">全部领域</option></select>
<select id="review" aria-label="审核"><option value="">全部审核状态</option></select>
<p id="count"></p><div id="results"></div><div id="paging">
<button id="previous">上一页</button><span id="page"></span>
<button id="next">下一页</button>
</div><p class="notice">仅供只读静态分析；不执行游戏脚本。
完整恢复不等于原始源码，作者静态核对不等于实机验证；审核者及授权单独记录。</p>
<p id="warnings"></p></aside><main id="detail"></main></div>
<script id="manual-data" type="application/json">{data}</script>
<script>{javascript}</script></body></html>'''


def export_site(catalog, destination: Path, *, content_root: Path):
    destination = destination.resolve()
    protected = [content_root.resolve()]
    for parent in content_root.resolve().parents:
        if (parent / ".git").exists():
            protected.append(parent)
            break
    if any(destination.is_relative_to(root) for root in protected):
        raise ManualError("生成物必须放在手册输入和Git仓库外，禁止覆盖输入")
    html = render_site(catalog).encode("utf-8")
    if len(html) > 64 * 1024 * 1024:
        raise ManualError("离线站点超过64MiB，请分批构建")
    destination.mkdir(parents=True, exist_ok=False)
    marker = destination / "INCOMPLETE.txt"
    marker.write_text("导出未完成；请勿分发。\n", encoding="utf-8")
    with (destination / "index.html").open("xb") as stream:
        stream.write(html)
    receipt = {
        "tool_version": __version__,
        "analysis_id": catalog.baseline["analysis_id"],
        "coverage": catalog.coverage(),
        "html_sha256": digest(html),
        "input_sha256": catalog.file_hashes,
        "evidence_verified": bool(catalog.coverage()["annotated"])
        and all(
            r["evidence_status"] == "verified_bytes_and_lines"
            for r in catalog.modules
            if r["annotation"]
        ),
        "scope": "只校验输入结构及可选字节/行号；不验证解释正确，不运行游戏。",
    }
    with (destination / "BUILD.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    marker.unlink()
    return destination / "index.html"
