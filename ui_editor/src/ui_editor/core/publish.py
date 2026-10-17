"""写回新包后的独立校验（零 Qt）——保存链最危险那一段的可测化。

为什么单独成模块：`ui/main_window.py` 里的 verifier 决定「新包算不算写成功」，
却挤在 1,700 行的窗口类里、只能被 GUI 测试间接覆盖
（`docs/analysis/ui_editor_analysis_20261016.md` P1-3 / 建议④）。抽出来之后
它可以**脱离窗口**直接测：结构检查只依赖 `FlsPack` 与 `path_hash`，
「用全新解析器回读」由调用方注入 :data:`ReadBack`（GUI 注入 AssetResolver
版，测试注入只读 FlsPack 版），所以本模块既不 import Qt、也不 import
`core.assets`。

检查项与抽取前逐条一致，任一不过 → ``report["error"]`` 填字符串、**不抛异常**：

1. 条目数 = 原条目数 + 新增图片数 + （新增布局 ? 1 : 0）；
2. 目录没有逆序（引擎按有序目录二分寻址，见
   `notes/native_dlg_path_cipher.md` §2.1）；
3. 条目集合 = 原集合 ∪ 新增图片 ∪ 目标布局；
4. 目标布局与每张新图都能被二分查找命中（模拟引擎寻址）；
5. 除 ``info["changed_ids"]`` 外没有条目字节被改（逐条比 ``read_id``，
   不以 span 相同当作保真证据）；
6. 回读：新包解码出的目标布局与当前文档逐字段一致、新图逐字节一致。

成功时报告带 ``ok=True``、``entries_after``（新包条目数）与
``changed_entries``（允许被改且确实变了的条目数）。
"""

from __future__ import annotations

from bisect import bisect_left
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .diagnostics import Diagnostic, diagnose
from .mxhash import path_hash
from .pack import FlsPack

__all__ = [
    "ReadBack",
    "SavePlan",
    "directory_is_sorted",
    "engine_finds",
    "require_save_encoding",
    "save_encoding_issues",
    "save_review_plan",
    "verify_readback",
    "verify_structure",
    "verify_written_pack",
]

#: ``read_back(pack_path, res_path, names) -> (布局字典 | None, {名称: 字节})``
ReadBack = Callable[[Path, str, Iterable[str]],
                    tuple[list[dict] | None, dict[str, bytes]]]


def engine_finds(entry_ids: Sequence[int], entry_id: int) -> bool:
    """模拟引擎寻址：在有序目录上 lower_bound 后判相等。

    对应 ``mxmain.dll:0x60E690`` 的 ``std::lower_bound`` 与调用点的
    「等于 end / 不等于 key」两次判定（`notes/native_dlg_path_cipher.md` §2.1）。
    """
    index = bisect_left(entry_ids, entry_id)
    return index < len(entry_ids) and entry_ids[index] == entry_id


def directory_is_sorted(entry_ids: Sequence[int]) -> bool:
    """目录是否无逆序（与抽取前的判定一致：相等不算错，真实包无重复条目）。"""
    return not any(a > b for a, b in
                   zip(entry_ids, entry_ids[1:], strict=False))


def verify_structure(*, src_pack, out_path, res_path: str, extras: Mapping,
                     info: Mapping) -> dict:
    """结构检查（条目数/升序/集合/二分命中/未改条目保真）。"""
    report: dict = {}
    try:
        with FlsPack(src_pack) as before, FlsPack(out_path) as after:
            expected = (before.count + len(info["images_added"])
                        + int(info.get("layout_added", False)))
            if after.count != expected:
                report["error"] = "条目数变化，写回结果不可信"
                return report
            ids_after = after.entry_ids
            if not directory_is_sorted(ids_after):
                report["error"] = "新包目录未按条目号升序，引擎可能查不到条目"
                return report
            added_ids = {path_hash(name) for name in info["images_added"]}
            if set(ids_after) != (set(before.entry_ids) | added_ids
                                  | {path_hash(res_path)}):
                report["error"] = "新包条目集合与预期不符，写回结果不可信"
                return report
            for name in [res_path, *extras]:
                if not engine_finds(ids_after, path_hash(name)):
                    report["error"] = f"新包中二分查找不到：{name}"
                    return report
            allowed = set(info["changed_ids"])
            changed = 0
            unexpected = 0
            for entry_id in before.entry_ids:
                if (entry_id not in allowed
                        and before.span_of(entry_id) == after.span_of(entry_id)):
                    continue
                if before.read_id(entry_id) != after.read_id(entry_id):
                    if entry_id in allowed:
                        changed += 1
                    else:
                        unexpected += 1
            if unexpected:
                report["error"] = f"有 {unexpected} 条条目被意外改变"
                return report
            report["changed_entries"] = changed
            report["entries_after"] = after.count
    except Exception as exc:  # 结构检查自身失败同样只记报告
        report["error"] = f"写回校验失败：{exc}"
    return report


def verify_readback(*, read_back: ReadBack, out_path, res_path: str,
                    extras: Mapping[str, bytes],
                    expected_dicts: list[dict]) -> dict:
    """回读检查：目标布局逐字段一致、新图逐字节一致（用全新解析器）。"""
    report: dict = {}
    try:
        got, read_extras = read_back(Path(out_path), res_path, extras)
        for name, data in extras.items():
            if read_extras.get(name) != data:
                report["error"] = f"新图 {name} 回读不一致"
                return report
        if got is None:
            report["error"] = "新包回读目标布局失败"
            return report
        if got != expected_dicts:
            report["error"] = "新包回读内容与当前文档不一致"
    except Exception as exc:
        report["error"] = f"写回校验失败：{exc}"
    return report


def verify_written_pack(
    *,
    src_pack,
    out_path,
    res_path: str,
    extras: Mapping[str, bytes],
    expected_dicts: list[dict],
    info: Mapping,
    read_back: ReadBack,
) -> dict:
    """结构 + 回读检查；返回报告片段（``ok`` 或 ``error``）。"""
    report = verify_structure(src_pack=src_pack, out_path=out_path,
                              res_path=res_path, extras=extras, info=info)
    if "error" not in report:
        report.update(verify_readback(read_back=read_back, out_path=out_path,
                                      res_path=res_path, extras=extras,
                                      expected_dicts=expected_dicts))
    report["ok"] = "error" not in report
    return report


# -- 保存前检查（同样是零 Qt 的保存链逻辑）------------------------------


def save_encoding_issues(doc, extras: Mapping[str, bytes]) -> list[Diagnostic]:
    """原生字段编码检查：布局自身的 ENCODING 问题 + 待写入图片路径。

    程序化写回也不能绕过原生字段编码检查；codec 的 GBK 回退仍仅作兼容
    （见 `core/diagnostics.py` 的 ENCODING 判定）。
    """
    issues = [issue for issue in diagnose(doc) if issue.code == "ENCODING"]
    issues.extend(_extra_encoding_issues(extras))
    return issues


def _extra_encoding_issues(extras: Mapping[str, bytes]) -> list[Diagnostic]:
    issues: list[Diagnostic] = []
    for name in extras:
        try:
            name.encode("gbk")
        except UnicodeEncodeError:
            issues.append(Diagnostic(
                "错误", "ENCODING", None, "图片资源路径",
                f"图片资源路径无法按 GBK 编码：{name!r}"))
    return issues


def require_save_encoding(doc, extras: Mapping[str, bytes]) -> None:
    """有编码问题就抛 :class:`ValueError`（写入前拒绝，而不是静默回退）。"""
    issues = save_encoding_issues(doc, extras)
    if issues:
        raise ValueError("原生字段编码检查未通过："
                         + "；".join(issue.message for issue in issues))


@dataclass
class SavePlan:
    """保存前清单的数据部分：对话框只负责画，不负责算。"""

    target: str
    to_pack: bool
    images: list[tuple[str, str, int]] = field(default_factory=list)
    issues: list[Diagnostic] = field(default_factory=list)
    notice: str = ""


def save_review_plan(
    *,
    target: str,
    to_pack: bool,
    issues: Iterable[Diagnostic],
    staged: Mapping[str, bytes],
    extras: Mapping[str, bytes],
    pack_path=None,
    res_path: str | None = None,
    pending_pack_import: bool = False,
) -> SavePlan:
    """保存前改动清单里除「布局改动」之外的那几行（图片/编码/待入包提示）。

    ``pack_path`` 给出时用 :class:`FlsPack` 判断每张待写入图片是**新增**还是
    **替换**（与原实现一致：只按路径哈希判定，不读负载）。
    """
    issues = list(issues)
    if to_pack:
        issues.extend(_extra_encoding_issues(extras))
    images: list[tuple[str, str, int]] = []
    notice = ""
    if to_pack and pack_path is not None:
        with FlsPack(pack_path) as pack:
            for name, data in extras.items():
                kind = "替换图片" if pack.contains(name) else "新增图片"
                images.append((kind, name, len(data)))
            images.extend(("未引用，跳过并保留待入包", name, len(data))
                          for name, data in staged.items()
                          if name not in extras)
            if pending_pack_import and res_path:
                kind = "替换" if pack.contains(res_path) else "新增"
                notice = (f"导入布局待入包：{kind} {res_path}；"
                          "不自动接脚本。新增布局明文存储，客户端加载待实机验证。")
    else:
        images.extend(("散装保存不嵌入，保留待入包", name, len(data))
                      for name, data in staged.items())
    return SavePlan(target=target, to_pack=to_pack, images=images,
                    issues=issues, notice=notice)
