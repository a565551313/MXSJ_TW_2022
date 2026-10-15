"use strict";
(() => {
  const data = JSON.parse(document.getElementById("manual-data").textContent);
  const $ = (id) => document.getElementById(id);
  const reviews = {
    unannotated: "尚未编写",
    pending: "待H审核",
    accepted: "H审核通过",
    changes_requested: "H要求修改",
    stale_review: "审核过期",
  };
  const confidence = {
    extracted: "自动提取",
    inferred: "推测待核实",
    static_reviewed: "作者静态核对",
    runtime_verified: "作者实机记录",
  };
  const provenance = {
    metadata_only: "仅元数据",
    historical_unverified_origin: "历史稿 · 原包对应未验证",
    recovered_partial: "部分恢复 · 存在缺失",
    recovered_complete_not_original: "完整恢复候选 · 非原始源码",
    native_origin_checked_not_semantics: "已核原生来源 · 非语义验收",
  };
  let page = 0,
    selected = null,
    tab = "overview",
    matches = [];
  const pageSize = 60;
  const element = (tag, text, cls) => {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  };
  const append = (parent, tag, text, cls) => {
    const e = element(tag, text, cls);
    parent.appendChild(e);
    return e;
  };
  const info = data.coverage;
  $("stats").textContent =
    `目录 ${info.indexed}/${info.expected_entries} · 已写说明 ${info.annotated} · H通过 ${info.accepted} · 已登记排除 ${info.excluded}`;
  $("version").textContent =
    `${data.baseline.analysis_id} · 固定源码提交 ${data.baseline.repository_commit.slice(0, 12)}`;
  $("warnings").textContent = data.warnings.join("\n");
  for (const domain of [...new Set(data.modules.map((m) => m.domain))].sort())
    $("domain").appendChild(new Option(domain, domain));
  for (const [value, title] of Object.entries(reviews))
    $("review").appendChild(new Option(title, value));
  function claim(parent, item) {
    append(parent, "p", `[${confidence[item.confidence]}] ${item.text}`);
    append(
      parent,
      "small",
      `证据：${item.evidence.join(" / ") || "无证据，待补"}`,
    );
  }
  function changeModule(row) {
    selected = row;
    const hash = "#module=" + encodeURIComponent(row.id);
    if (location.hash !== hash) location.hash = hash;
    render();
    drawResults();
  }
  function drawResults() {
    $("results").replaceChildren();
    for (const row of matches.slice(page * pageSize, (page + 1) * pageSize)) {
      const button = append(
        $("results"),
        "button",
        row.path || `路径不可读 · #${row.entry_index}`,
      );
      if (selected && row.id === selected.id) button.className = "selected";
      append(
        button,
        "small",
        `${row.vm} · ${row.domain} · ${reviews[row.review_status]}`,
      );
      button.onclick = () => changeModule(row);
    }
    $("count").textContent = `${matches.length} 个匹配模块`;
    $("page").textContent =
      `${page + 1}/${Math.max(1, Math.ceil(matches.length / pageSize))}`;
    $("previous").disabled = page === 0;
    $("next").disabled = (page + 1) * pageSize >= matches.length;
    if (!matches.length)
      append(
        $("results"),
        "p",
        "未找到匹配项；本阶段目录不完整，“搜不到”不等于功能不存在。",
      );
  }
  function search() {
    const tokens = $("query")
      .value.replaceAll("\\", "/")
      .toLowerCase()
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    matches = data.modules.filter(
      (m) =>
        (!$("domain").value || m.domain === $("domain").value) &&
        (!$("review").value || m.review_status === $("review").value) &&
        tokens.every((t) => m.search_text.includes(t)),
    );
    page = 0;
    drawResults();
  }
  function render() {
    const panel = $("detail");
    panel.replaceChildren();
    if (!selected) {
      append(panel, "h2", "从功能、路径或函数名开始");
      append(
        panel,
        "p",
        "左侧搜索支持中文关键词、路径片段、函数名；多个词按“同时包含”匹配。只有实际编写的说明才可搜中文职责。",
      );
      return;
    }
    const row = selected,
      a = row.annotation;
    append(panel, "h2", row.path || `路径不可读 · #${row.entry_index}`);
    append(
      panel,
      "p",
      `${reviews[row.review_status]} · 负责人 ${row.owner} · ${row.vm} · 条目 ${row.entry_index}`,
      "status",
    );
    append(panel, "small", `archive SHA256: ${row.archive_sha256}`);
    if (!a) {
      append(
        panel,
        "p",
        "这里只登记目录元数据，尚未解释职责。未填写不等于没有函数、调用或资源。",
        "notice",
      );
      for (const f of row.functions)
        append(panel, "pre", `${f.name} ${f.signature || "签名未确认"}`);
      return;
    }
    append(panel, "p", provenance[a.source_status], "notice");
    if (row.review_status !== "accepted")
      append(
        panel,
        "small",
        "以下证据级别由作者标注，尚未通过有效H复核；字节/行号校验不验证解释正确。",
      );
    const tabs = append(panel, "nav", undefined, "tabs");
    for (const [id, label] of [
      ["overview", "模块职责"],
      ["functions", "类与函数"],
      ["resources", "关联与修改"],
      ["evidence", "证据与来源"],
    ]) {
      const b = append(tabs, "button", label, id === tab ? "active" : "");
      b.onclick = () => {
        tab = id;
        render();
      };
    }
    const body = append(panel, "section");
    if (tab === "overview") {
      claim(body, a.purpose);
      append(body, "h3", "关键词");
      append(body, "p", a.keywords.join(" · "));
      append(body, "h3", "限制与风险");
      for (const risk of a.limitations) append(body, "p", `• ${risk}`);
    } else if (tab === "functions") {
      append(
        body,
        "p",
        "这里是已整理子集；空调用列表不证明不存在调用。",
        "notice",
      );
      for (const f of a.functions) {
        append(body, "h3", f.name);
        append(body, "pre", f.signature || "签名未确认");
        claim(body, f.summary);
        append(body, "p", `静态调用线索：${f.calls.join(" / ") || "尚未整理"}`);
        for (const branch of f.branches) {
          append(body, "h4", `分支：${branch.condition}`);
          claim(body, branch.effect);
        }
      }
    } else if (tab === "resources") {
      append(body, "h3", "上下游关系（按证据标注，不自动推定）");
      for (const relation of a.relationships) {
        append(
          body,
          "h4",
          `${relation.direction === "upstream" ? "上游" : "下游"} · ${relation.kind}`,
        );
        append(body, "p", relation.symbol || "符号未确认");
        claim(body, relation.summary);
        if (relation.module) {
          const target = data.modules.find(
            (m) =>
              m.archive_sha256 === relation.module.archive_sha256 &&
              m.entry_index === relation.module.entry_index,
          );
          if (target) {
            const b = append(
              body,
              "button",
              `跳转：${target.path || target.entry_index}`,
            );
            b.onclick = () => {
              tab = "overview";
              changeModule(target);
            };
          } else
            append(
              body,
              "p",
              `条目 ${relation.module.entry_index} 尚未编入目录`,
            );
        }
      }
      append(body, "h3", "关联文件 / 配置 / 布局");
      for (const r of a.resources) {
        append(body, "h4", `${r.kind} · ${r.target}`);
        claim(body, r.summary);
      }
      append(body, "h3", "修改入口问答");
      for (const g of a.modification_guides) {
        append(body, "h4", g.question);
        claim(body, g.answer);
      }
      append(body, "h3", "跨模块线索（不自动认定调用关系）");
      for (const r of a.related_modules) {
        const target = data.modules.find(
          (m) =>
            m.archive_sha256 === r.archive_sha256 &&
            m.entry_index === r.entry_index,
        );
        if (target) {
          const b = append(
            body,
            "button",
            target.path || `条目 ${r.entry_index}`,
          );
          b.onclick = () => {
            tab = "overview";
            changeModule(target);
          };
        } else append(body, "p", `条目 ${r.entry_index} 尚未编入本阶段目录`);
      }
    } else {
      append(
        body,
        "p",
        `本次加载校验：${row.evidence_status}。SHA及行号有效 ≠ 源语义正确。`,
      );
      append(body, "pre", `本说明SHA256: ${row.annotation_sha256}`);
      for (const s of a.sources) {
        append(body, "h3", s.id);
        append(body, "p", s.path);
        append(body, "pre", s.sha256);
        append(body, "p", s.note);
      }
      for (const e of a.evidence)
        append(
          body,
          "p",
          `${e.id} → ${e.source_id} L${e.start_line}–${e.end_line}`,
        );
    }
  }
  $("query").oninput = search;
  $("domain").onchange = search;
  $("review").onchange = search;
  $("previous").onclick = () => {
    page--;
    drawResults();
  };
  $("next").onclick = () => {
    page++;
    drawResults();
  };
  function fromHash() {
    const id = new URLSearchParams(location.hash.slice(1)).get("module");
    const row = data.modules.find((m) => m.id === id);
    if (row) {
      selected = row;
      render();
      drawResults();
    }
  }
  window.onhashchange = fromHash;
  search();
  render();
  fromHash();
})();
