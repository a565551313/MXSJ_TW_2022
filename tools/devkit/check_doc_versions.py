#!/usr/bin/env python3
"""check_doc_versions.py — 文档版本号与源码元数据一致性静态检查。

**为什么有这个工具**：本仓库的顶层文档（README / AGENTS / STATUS）历史上长期
手工维护各组件的版本号，导致 `ui_editor` 从 0.8.4 涨到 0.21.0 而 README 一次都
没跟上，读者据此会得出错误结论。本工具把「文档里写的版本」与「源码里真实的
版本」机械比对，让漂移在提交前就红。

**检查什么**

1. 每个有 `pyproject.toml` 的组件，从其 `[project].version` 读真实版本。
2. 在指定文档里找形如 `` `component`/ ``、`` `component`， ``、`` component/ ``、
   `` `component`，... ``、`` （`component`/ `` 的**版本上下文**，
   抽出被声明的版本号，与真实版本比对。
3. 只在**版本上下文**里比对——组件目录名后面紧跟版本号（0.x.y / x.y.z /
   0.x.y.devN）才算声明。文档里提到组件名但不带版本号的正常叙述不受影响。

**历史叙述的处理（重要）**

本仓库的 `docs/STATUS.md` 按设计保留了大量**历史轮次记录**——那些记录里
「UI 编辑器 0.19.0」是**当时那一版**的标题，属于正确的事实陈述，不是漂移。
工具用两种方式区分：

- `--exclude-history`（默认开）：跳过明确标注为历史轮次的行——行内出现
  「历史」「快照」「归档」「该轮」「当时」「2026-xx-xx：」等标记，或整行以
  `## 3.xx` 历史章节标题开头。
- 剩下仍会被标记的，是**当前态声明**（README 的能力表、AGENTS 的指南、
  STATUS §1–§2 的现状表）。

若你只想看「当前态」，用默认参数；若要连历史叙述一起严格比对，
加 `--no-exclude-history`（届时历史轮次标题会大量报 ERROR，属预期）。

**退出码**

- 0：全部一致（或只出现 INFO 级提示）
- 1：有 ERROR（文档版本与源码不一致）
- 2：参数错误 / 组件目录缺失

**边界**：这是**静态**一致性检查，只比对字符串，不验证功能、测试数或 Windows 实机
行为。文档里「某版本曾经是什么样」的**历史叙述**若不带组件名紧邻版本号的写法，
不会被判为漂移；需要人工判断时看 `--json` 输出里的上下文。

只依赖标准库，Python 3.10+。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 组件登记表：文档里用的名字 → 仓库内含 pyproject.toml 的目录
# ---------------------------------------------------------------------------
COMPONENTS: dict[str, str] = {
    "ui_editor": "ui_editor",
    "map_editor": "map_editor",
    "resource_editor": "resource_editor",
    "script_editor": "script_editor",
    "script_manual": "script_manual",
    "web_server": "web_server",
    "native_channel": "tools/native_channel",
}

# 文档里组件名可能出现的其它别名（→ 登记表里的键）
ALIASES: dict[str, str] = {
    "UI 编辑器": "ui_editor",
    "地图编辑器": "map_editor",
    "资源编辑器": "resource_editor",
    "脚本编辑器": "script_editor",
    "脚本手册": "script_manual",
    "原生信道": "native_channel",
}

# 文档里常见的**缩写**形式：``当前资源 0.4.3 / UI 0.8.4``。
# 这些是「UI」「资源」这类短名，靠上下文唯一确定组件。
SHORT_ALIASES: dict[str, str] = {
    "UI": "ui_editor",
    "资源": "resource_editor",
    "地图": "map_editor",
    "脚本": "script_editor",
}

# 版本号字面量：1.2.3 / 0.21.0 / 0.6.0.dev9
VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?\b")

# 组件名后面「紧邻」版本号的分隔符：空格、／、/,、）、"，"、全角括号等
# 允许 `` `ui_editor`/，0.21.0 `` 与 `` （`ui_editor/`，0.21.0）`` 两种写法
_SEP = r"[\s/／,，、:：）)】\]]*"

# 允许出现在「组件名」与「版本号」之间的有限连接词/标点。
# 注意：反引号、斜杠、全角逗号、冒号、连字符、括号都要能跨过去，
# 因为实际文档里写法很杂：`` `ui_editor/`，0.21.0 ``、`` `ui_editor`，**0.21.0** ``。
# 「组件名」与「版本号」之间的连接部分。
#
# ⚠️ 这里**不能**写成「分隔符可选 + \s*」的形式，例如
#    ``(?:[/／,，、:：—\-]?\s*)*``
# 那样的模式里，一段 n 个连续空白有指数多种等价切分（空白既可能归给前一次
# 重复的 ``\s*``、也可能归给后一次），匹配失败时正则引擎会把这些切分
# **全部回溯一遍**——实测 n=10 约 3 ms、n=20 约 3 s，**每多 2 个空格耗时 ×4**，
# 是教科书级的指数回溯（ReDoS）。gitar-bot 与 CodeRabbit 在 PR #92 上都指出了
# 这一点，**他们的结论是对的**。
#
# 现在的写法把「可省略的标点」和「空白」**合并进同一个字符类**：
# 每次重复至少消耗 1 个字符，空白**只能**被唯一的那一处吃掉，
# 不存在二义切分 ⇒ 回溯次数是线性的。
_CONNECT = r"[\s*/／`~（）()\[\]【】,，、:：—\-]*"

# 版本号前置词：直接、当前、版本、v
_PREFIX = r"(?:当前\s*)?(?:直接\s*)?(?:版本\s*)?(?:v|V)?"

# 表格单元格里的版本号：``**0.21.0**``、``v1.0.0``、``0.4.3``
_CELL_VERSION_RE = re.compile(
    r"(?<![A-Za-z0-9_.])"
    + _PREFIX
    + r"\*{0,2}\s*"
    + r"(?P<version>\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?)"
)

# 表格里**不是**组件版本声明的版本号——依赖／解释器要求：
#   ``Python 3.10+``、``SQLite >=3.24``、``CPython 2.5.6``、``PySide6 + Pillow``
# 这些是环境要求，不是组件版本，不能拿来判漂移。
_DEP_VERSION_RE = re.compile(
    r"(?:Python|SQLite|CPython|Cython|PySide\d*|PyQt\d*|Pillow|Numpy|"
    r"numpy|Qt\s*\d|Node|Node\.js)\s*[>=~^]*\s*\d"
    r"|[>=~^]\s*\d+\.\d+"
)

# 统一��「组件名 + 连接 + 版本号」模式
_DECL_RE_CACHE: dict[str, re.Pattern[str]] = {}

# 历史叙述标记：出现任一即认为该行是「历史轮次记录」，不判为漂移。
# 判据来自 STATUS 的实际写法：轮次条目以「> **2026-10-xx：...**」开头，
# 历史章节标题形如「## 3.43 目录寻址判定结案（2026-10-16，...）」。
_HISTORY_MARKERS = (
    "历史",
    "快照",
    "归档",
    "该轮",
    "当时",
    "旧会话",
    "上一轮",
    "上一版",
    "已作废",
    "已取代",
    "归档至",
)

# 历史章节标题：``## 3.12 <标题>（日期...）``
_HISTORY_HEADING_RE = re.compile(r"^#{2,6}\s*3\.\d+\b")

# 带日期前缀的轮次条目：``> **2026-10-26：UI 编辑器 0.20.0（...）**``
# 这类行记录的是**那一轮**的版本，属于正确的事实陈述。
_DATE_PREFIX_RE = re.compile(r"^\s*>?\s*\**\s*\d{4}-\d{2}-\d{2}\s*[：:]")

# 表格里的日期首列：``| 2026-10-14 | UI 编辑器 0.5.3 ... |``
_TABLE_DATE_RE = re.compile(r"^\s*\|[^|]*\d{4}-\d{2}-\d{2}[^|]*\|")

# 轮次条目里常出现的「起点＝X.Y.Z」「本分支 X.Y.Z」等版本回指，
# 同样属于历史叙述的一部分。
_HISTORY_INLINE_MARKERS = (
    "起点",
    "本分支",
    "该分支",
    "上一版",
    "再上一版",
    "已合并",
    "已开",
    "未合并",
)

# 版本迁移箭头：``0.8.4 → 0.21.0``、``0.6.0.dev7 改为 0.6.0.dev9``。
# 变更记录里记录「从哪个版本改到哪个版本」是**正确的事实陈述**，
# 不是漂移——两边都不该被判成「当前声明」。
# 注意版本号两边可能裹着 markdown 粗体：``0.8.4 → **0.21.0**``。
_VERSION_ARROW_RE = re.compile(
    r"\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?"
    r"\s*(?:→|->|=>|—>|改[为到]|升[到至]|更新[到至])\s*"
    r"\**\s*"
    r"\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?"
    r"\s*\**"
)


def _is_history_line(line: str) -> bool:
    stripped = line.strip()
    if _HISTORY_HEADING_RE.match(stripped):
        return True
    if _DATE_PREFIX_RE.match(line):
        return True
    if _TABLE_DATE_RE.match(line):
        return True
    if any(marker in line for marker in _HISTORY_MARKERS):
        return True
    if any(marker in line for marker in _HISTORY_INLINE_MARKERS):
        return True
    return False


def _version_in_arrow(line: str, version: str) -> bool:
    """判断某个版本号是否出现在「版本迁移箭头」里。

    变更记录常写成 ``0.8.4 → 0.21.0`` 或 ``0.6.0.dev7 改为 0.6.0.dev9``——
    两端都是**历史事实**（记录改了什么），都不是「当前声明的版本」，
    因此都不该被判成漂移。
    """
    for m in _VERSION_ARROW_RE.finditer(line):
        if version in m.group(0):
            return True
    return False


# 明确声明「以下内容已归档／不是当前」的横幅
_ARCHIVE_BANNER_MARKERS = (
    "以下保留历史内容",
    "以下为历史",
    "历史内容及原章节锚点",
    "不是本轮任务或授权",
)


def _history_sections(text: str) -> list[tuple[int, int]]:
    """找出文档里属于「历史叙述」的整段范围。

    返回 [(起始行号, 结束行号)]，行号从 1 开始，结束为闭区间。

    识别两类：
    1. ``### 3.12 <标题>`` 这类编号历史章节——从标题行到下一个同级或更高级
       标题之前，整段都算历史。
    2. 显式横幅段落——``> 以下保留历史内容……`` 之后到下一个 ``##`` 级标题
       之前，整段都算历史。
    """
    lines = text.splitlines()
    ranges: list[tuple[int, int]] = []

    heading_re = re.compile(r"^(#{2,6})\s*(.*)$")
    headings: list[tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        m = heading_re.match(line)
        if m:
            headings.append((idx + 1, len(m.group(1)), m.group(2).strip()))

    # 1) 编号历史章节
    for pos, (line_no, level, title) in enumerate(headings):
        if not re.match(r"^3\.\d+\b", title):
            continue
        end = len(lines)
        for next_no, next_level, _ in headings[pos + 1 :]:
            if next_level <= level:
                end = next_no - 1
                break
        ranges.append((line_no, end))

    # 2) 横幅段落
    for idx, line in enumerate(lines):
        if not any(marker in line for marker in _ARCHIVE_BANNER_MARKERS):
            continue
        start = idx + 1
        end = len(lines)
        for next_no, next_level, _ in headings:
            if next_no > start and next_level <= 2:
                end = next_no - 1
                break
        ranges.append((start, end))

    return ranges


def _in_ranges(line_no: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= line_no <= end for start, end in ranges)


def _decl_re(name: str) -> re.Pattern[str]:
    """构造「组件名 + 版本号」的声明模式。

    允许的写法（name 会被 re.escape）：
      - `` `ui_editor`，0.21.0 ``
      - `` `ui_editor`/，0.21.0 ``
      - `` （`ui_editor/`，0.21.0）``
      - `` `ui_editor/`，**0.21.0** ``
      - `` UI 编辑器 0.21.0 ``
    """
    if name in _DECL_RE_CACHE:
        return _DECL_RE_CACHE[name]
    escaped = re.escape(name)
    spaced = re.escape(name.replace("_", " "))
    # 目录名可能自带结尾斜杠：`` `ui_editor/` ``
    alt = "|".join([escaped, escaped + r"/", spaced, spaced + r"/"])
    pat = re.compile(
        r"(?P<name>" + alt + r")"
        + _CONNECT
        + _PREFIX
        + r"(?P<version>\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?)"
    )
    _DECL_RE_CACHE[name] = pat
    return pat


# 缩写形式的声明模式：``UI 0.8.4``、``资源 0.4.3``。
# 短名歧义大（"UI" 也可能指界面），所以要求：
#   ① 短名后**紧邻**版本号；
#   ② 同一行里出现「/」分隔的并列短名（``当前资源 0.4.3 / UI 0.8.4``）；
#   ③ 该短名不是更长别名的一部分（用 (?<![A-Za-z一-鿿]) 守卫）。
_SHORT_DECL_RE_CACHE: dict[str, re.Pattern[str]] = {}


def _short_decl_re(short: str) -> re.Pattern[str]:
    """构造缩写形式的声明模式。

    守卫只用 ASCII 词字符——**不能**把中文字符排除在外：
    ``当前资源 0.4.3`` 里的「资源」前面就是中文字符「前」，
    用中文字符做负向守卫会误杀合法写法。

    短名与版本号之间允许夹 **markdown 粗体标记**：仓库里实际写法是
    ``当前资源 **0.4.3** / UI **0.21.0**``（`README.md` 365 行），
    不认粗体就等于这一行**完全没人管**（kody-ai 在 PR #92 上指出）。
    """
    if short not in _SHORT_DECL_RE_CACHE:
        _SHORT_DECL_RE_CACHE[short] = re.compile(
            r"(?<![A-Za-z0-9_])"
            + re.escape(short)
            + r"[\s/／]*\*{0,2}\s*"
            + r"(?P<version>\d+\.\d+(?:\.\d+)?(?:\.dev\d+)?)"
        )
    return _SHORT_DECL_RE_CACHE[short]


def scan_short_alias(
    text: str,
    key: str,
    real_version: str,
    *,
    exclude_history: bool = True,
) -> list[dict[str, object]]:
    """扫描缩写形式的版本声明（``UI 0.8.4``）。

    缩写歧义大，只在**同一行存在并列短名**时才采信——例如
    ``当前资源 0.4.3 / UI 0.8.4``。孤立的 ``UI 0.8.4`` 不采信，
    避免把普通叙述误判成版本声明。
    """
    if not any(alias_key == key for alias_key in SHORT_ALIASES.values()):
        return []
    hits: list[dict[str, object]] = []
    lines = text.splitlines()
    history_ranges = _history_sections(text) if exclude_history else []
    for short, alias_key in SHORT_ALIASES.items():
        if alias_key != key:
            continue
        for line_idx, line in enumerate(lines):
            line_no = line_idx + 1
            # 要求同一行有并列的短名声明（至少两个不同短名）
            shorts_here = [
                s for s, k in SHORT_ALIASES.items() if _short_decl_re(s).search(line)
            ]
            if len(set(shorts_here)) < 2:
                continue
            if exclude_history and (
                _is_history_line(line) or _in_ranges(line_no, history_ranges)
            ):
                continue
            for m in _short_decl_re(short).finditer(line):
                found = m.group("version")
                if found == real_version:
                    continue
                hits.append(
                    {
                        "component": key,
                        "found_version": found,
                        "real_version": real_version,
                        "line": line_no,
                        "context": line.strip()[:200],
                    }
                )
    return hits


def read_version(pyproject: Path) -> str | None:
    """从 pyproject.toml 读 [project].version。

    只用标准库做**最小**解析：找 `[project]` 段里的 `version = "..."`。
    不引入 tomllib 是为了兼容 Python 3.10（3.11 才有 tomllib），尽管仓库
    统一跑 3.11+——保持工具「标准库且老版本可用」的既有风格。
    """
    try:
        text = pyproject.read_text(encoding="utf-8")
    except OSError:
        return None
    in_project = False
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("["):
            in_project = line == "[project]"
            continue
        if not in_project:
            continue
        m = re.match(r"""version\s*=\s*["']([^"']+)["']""", line)
        if m:
            return m.group(1)
    return None


def collect_real_versions(root: Path) -> dict[str, str]:
    """返回 {组件键: 真实版本}；目录或 pyproject 缺失的组件直接跳过。"""
    out: dict[str, str] = {}
    for key, rel in COMPONENTS.items():
        pyproject = root / rel / "pyproject.toml"
        if not pyproject.is_file():
            continue
        version = read_version(pyproject)
        if version:
            out[key] = version
    return out


def find_skipped_components(root: Path) -> list[str]:
    """返回**被跳过**的组件（目录或 pyproject.toml 缺失、或读不到版本号）。

    组件被改名／删除时，它会**静默**退出闸门——文档里残留的旧版本号就再也
    没人查了。所以 CLI 必须把跳过项打印出来，让这件事**可见**。
    """
    skipped: list[str] = []
    for key, rel in COMPONENTS.items():
        pyproject = root / rel / "pyproject.toml"
        if not pyproject.is_file():
            skipped.append(f"{key}（缺 {rel}/pyproject.toml）")
            continue
        if not read_version(pyproject):
            skipped.append(f"{key}（{rel}/pyproject.toml 读不到 [project].version）")
    return skipped


def _table_row_scan(
    line: str,
    key: str,
    real_version: str,
) -> list[dict[str, object]]:
    """扫描**表格行**里的版本声明。

    表格是本仓库声明组件版本的主要位置之一（``README.md`` / ``AGENTS.md``
    的组件能力表），但组件名和版本号通常**不在同一个单元格**——
    例如::

        | UI 编辑器 | `.dlg` 布局编解码…… | **0.21.0**；批量导入布局…… |

    名字在 cell[1]、版本在 cell[3]，中间隔着描述文字。正则 ``_CONNECT``
    只允许紧邻的连接符，跨不过单元格分隔（kody-ai 在 PR #92 上指出：
    这样一来「表格里写错版本号」完全能溜过闸门）。

    所以这里**按单元格**处理：把一行拆成单元格，组件名出现在某个单元格、
    版本号出现在**同一行**的后续单元格，即视为一次声明。
    限定在**同一行**内，就不会把下一行的版本号算到这一行头上。
    """
    if "|" not in line:
        return []
    cells = line.split("|")
    names = [key, key.replace("_", " ")]
    for alias, alias_key in ALIASES.items():
        if alias_key == key:
            names.append(alias)
    hits: list[dict[str, object]] = []
    for name in names:
        for i, cell in enumerate(cells):
            if name not in cell:
                continue
            # 版本号只能出现在**同一行**的后续单元格里
            for later in cells[i + 1 :]:
                for m in _CELL_VERSION_RE.finditer(later):
                    found = m.group("version")
                    if found == real_version:
                        continue
                    # 依赖／解释器版本要求（``Python 3.10+``）不是组件版本声明
                    ctx = later[max(0, m.start() - 24) : m.end() + 4]
                    if _DEP_VERSION_RE.search(ctx):
                        continue
                    # 章节号引用（``§3.15.9``）不是版本声明
                    if re.search(r"§\s*$", later[: m.start()]):
                        continue
                    hits.append(
                        {
                            "component": key,
                            "found_version": found,
                            "real_version": real_version,
                            "line": 0,  # 由调用方补上
                            "context": line.strip()[:200],
                        }
                    )
            break
    return hits


def scan_doc(
    text: str,
    key: str,
    real_version: str,
    *,
    exclude_history: bool = True,
) -> list[dict[str, object]]:
    """在一份文档里找 `key` 的版本声明，返回与真实版本不符的条目。

    `exclude_history=True` 时跳过标记为历史叙述的行（见 `_is_history_line`）。
    """
    hits: list[dict[str, object]] = []
    lines = text.splitlines()
    history_ranges = _history_sections(text) if exclude_history else []
    # 组件名 + 别名
    names = [key, key.replace("_", " ")]
    for alias, alias_key in ALIASES.items():
        if alias_key == key:
            names.append(alias)
    seen_spans: set[tuple[int, int]] = set()
    for name in names:
        for m in _decl_re(name).finditer(text):
            span = m.span("version")
            if span in seen_spans:
                continue
            seen_spans.add(span)
            found = m.group("version")
            if found == real_version:
                continue
            line_no = text.count("\n", 0, m.start("version")) + 1
            line_text = lines[line_no - 1] if 1 <= line_no <= len(lines) else ""
            if exclude_history and (
                _is_history_line(line_text) or _in_ranges(line_no, history_ranges)
            ):
                continue
            # 版本迁移箭头两端的版本号都不是「当前声明」
            if exclude_history and _version_in_arrow(line_text, found):
                continue
            hits.append(
                {
                    "component": key,
                    "found_version": found,
                    "real_version": real_version,
                    "line": line_no,
                    "context": line_text.strip()[:200],
                }
            )

    # 表格行：组件名与版本号**不在同一个单元格**的情况（README/AGENTS 组件能力表）。
    # 正文路径的 ``_CONNECT`` 跨不过单元格分隔，那些行等于完全没人管。
    seen_rows: set[tuple[int, str]] = set()
    for line_idx, line in enumerate(lines):
        if "|" not in line:
            continue
        line_no = line_idx + 1
        for hit in _table_row_scan(line, key, real_version):
            marker = (line_no, str(hit["found_version"]))
            if marker in seen_rows:
                continue
            seen_rows.add(marker)
            if exclude_history and (
                _is_history_line(line) or _in_ranges(line_no, history_ranges)
            ):
                continue
            if exclude_history and _version_in_arrow(line, str(hit["found_version"])):
                continue
            hit["line"] = line_no
            hits.append(hit)
    return hits


def line_text_safe(text: str, line_no: int) -> bool:
    lines = text.splitlines()
    return 1 <= line_no <= len(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="检查顶层文档里声明的组件版本号与源码 pyproject.toml 是否一致。"
    )
    parser.add_argument(
        "--root",
        default=".",
        help="仓库根目录（默认当前目录）",
    )
    parser.add_argument(
        "--doc",
        action="append",
        default=None,
        metavar="PATH",
        help="要检查的文档，可重复。默认 README.md / AGENTS.md / docs/STATUS.md",
    )
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="把结果写成 JSON 到该路径",
    )
    parser.add_argument(
        "--no-exclude-history",
        dest="exclude_history",
        action="store_false",
        help="连历史轮次叙述一起严格比对（默认跳过历史行）",
    )
    parser.set_defaults(exclude_history=True)
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"[docver] 根目录不存在：{root}", file=sys.stderr)
        return 2

    docs = args.doc or ["README.md", "AGENTS.md", "docs/STATUS.md"]
    doc_paths: list[Path] = []
    for d in docs:
        p = Path(d)
        if not p.is_absolute():
            p = root / p
        if not p.is_file():
            print(f"[docver] 文档不存在：{p}", file=sys.stderr)
            return 2
        doc_paths.append(p)

    real = collect_real_versions(root)
    if not real:
        print("[docver] 未能从任何 pyproject.toml 读到版本号", file=sys.stderr)
        return 2

    # 组件被改名／删除会**静默**退出闸门——把跳过项打印出来让这件事可见。
    skipped = find_skipped_components(root)

    # 按文档分组收集问题
    all_findings: list[dict[str, object]] = []
    scanned_versions: dict[str, str] = {}

    for doc_path in doc_paths:
        try:
            text = doc_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"[docver] 读取失败：{doc_path}（{exc}）", file=sys.stderr)
            return 2
        rel = (
            doc_path.relative_to(root).as_posix()
            if doc_path.is_relative_to(root)
            else doc_path.name
        )
        for key, version in real.items():
            found = scan_doc(
                text, key, version, exclude_history=args.exclude_history
            )
            found += scan_short_alias(
                text, key, version, exclude_history=args.exclude_history
            )
            for item in found:
                item["doc"] = rel
            all_findings.extend(found)
            scanned_versions[f"{key}@{version}"] = version

    # 输出
    print(f"[docver] 仓库根：{root}")
    version_list = ", ".join(f"{k} {v}" for k, v in sorted(real.items()))
    print(f"[docver] 真实版本：{version_list}")
    print(f"[docver] 已检查文档：{', '.join(p.name for p in doc_paths)}")
    if skipped:
        print(
            f"[docver] 警告：{len(skipped)} 个组件被跳过（未纳入检查）——"
            "若它们本该存在，请核对目录名："
        )
        for item in skipped:
            print(f"[docver]   - {item}")

    if all_findings:
        print("")
        print(f"[docver] ERROR 发现 {len(all_findings)} 处版本声明与源码不一致：")
        for item in all_findings:
            print(
                f"  {item['doc']}:{item['line']}  {item['component']}："
                f"文档写 {item['found_version']}，源码是 {item['real_version']}"
            )
            if item.get("context"):
                print(f"      {item['context']}")
        print("")
        print("[docver] 请改文档（或改源码后同步文档），不要放宽本检查。")
    else:
        print("[docver] OK：文档中的组件版本声明与源码元数据一致。")

    if args.json:
        payload = {
            "root": str(root),
            "real_versions": real,
            "skipped_components": skipped,
            "docs": [str(p) for p in doc_paths],
            "findings": all_findings,
        }
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"[docver] JSON 已写入 {out}")

    return 1 if all_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
