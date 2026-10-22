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
from .errors import Cancelled
from .mxhash import path_hash
from .native_layout import HEADER, decode_native, encode_layout, plain_if_layout
from .pack import FlsPack

__all__ = [
    "ReadBack",
    "SavePlan",
    "TargetWrite",
    "classify_target_path",
    "classify_target_write",
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
                     info: Mapping,
                     layout_paths: Sequence[str] | None = None,
                     progress: Callable[[int, int, str], None] | None = None,
                     cancelled: Callable[[], bool] | None = None) -> dict:
    """结构检查（条目数/升序/集合/二分命中/未改条目保真）。

    ``layout_paths``：本次一共写了哪些布局条目（批量导入时不止一个）；
    不传就只看 ``res_path``。新增布局按 ``info["layouts_added"]`` 计数，
    旧调用方的 ``info["layout_added"]`` 仍然认。

    逐条保真是全包读取的重活：``progress(done, total, text)`` 回报进度；
    ``cancelled()`` 为真时抛 :class:`~ui_editor.core.errors.Cancelled`
    （结果作废，调用方清理未验证产物），不写入 ``report``。
    """
    report: dict = {}
    try:
        # 就地写回（src 与 out 是同一个文件）时，「写前」的句柄拿到的
        # 已经是写后的内容，逐条比对只会得出 0 条，别当成真在报告。
        same_file = Path(src_pack).resolve() == Path(out_path).resolve()
        paths = list(layout_paths) if layout_paths is not None else [res_path]
        with FlsPack(src_pack) as before, FlsPack(out_path) as after:
            before_ids = set(before.entry_ids)
            new_layouts = [path for path in paths
                           if path_hash(path) not in before_ids]
            claimed = info.get("layouts_added")
            if claimed is None:
                claimed = [res_path] if info.get("layout_added") else []
            expected = (before.count + len(info["images_added"])
                        + len(claimed))
            if after.count != expected:
                report["error"] = "条目数变化，写回结果不可信"
                return report
            # 写包方声明的「新增」还要和源包实际情况对得上：声称新增了
            # 一个本来就在包里的布局，意味着它可能把别的东西写丢了。
            if sorted(claimed) != sorted(new_layouts):
                report["error"] = (
                    "新增布局的声明与源包不符："
                    f"声称 {sorted(claimed)}，实为 {sorted(new_layouts)}")
                return report
            ids_after = after.entry_ids
            if not directory_is_sorted(ids_after):
                report["error"] = "新包目录未按条目号升序，引擎可能查不到条目"
                return report
            added_ids = {path_hash(name) for name in info["images_added"]}
            if set(ids_after) != (before_ids | added_ids
                                  | {path_hash(path) for path in paths}):
                report["error"] = "新包条目集合与预期不符，写回结果不可信"
                return report
            for name in [*paths, *extras]:
                if not engine_finds(ids_after, path_hash(name)):
                    report["error"] = f"新包中二分查找不到：{name}"
                    return report
            allowed = set(info["changed_ids"])
            changed = 0
            unexpected = 0
            total = len(before.entry_ids)
            for done, entry_id in enumerate(before.entry_ids, 1):
                if cancelled is not None and cancelled():
                    raise Cancelled("写回校验已取消")
                if progress is not None and (done == 1 or done == total
                                             or done % 32 == 0):
                    progress(done, total, f"逐条保真校验 {done}/{total}")
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
            report["changed_entries"] = None if same_file else changed
            report["entries_after"] = after.count
    except Cancelled:
        raise  # 用户取消原样上抛（结果作废），不当成校验失败
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
    extra_layouts: Mapping[str, list[dict]] | None = None,
    progress: Callable[[int, int, str], None] | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> dict:
    """结构 + 回读检查；返回报告片段（``ok`` 或 ``error``）。

    ``extra_layouts``：批量导入一并写进新包的其它布局（``{路径: 字典列表}``），
    每个都用同一套 ``read_back`` 独立回读比对。

    ``progress``/``cancelled`` 只作用于结构检查的逐条保真循环，
    取消时抛 :class:`~ui_editor.core.errors.Cancelled`。
    """
    extra_layouts = dict(extra_layouts or {})
    report = verify_structure(src_pack=src_pack, out_path=out_path,
                              res_path=res_path, extras=extras, info=info,
                              layout_paths=[res_path, *extra_layouts],
                              progress=progress, cancelled=cancelled)
    if "error" not in report:
        report.update(verify_readback(read_back=read_back, out_path=out_path,
                                      res_path=res_path, extras=extras,
                                      expected_dicts=expected_dicts))
        for path, dicts in extra_layouts.items():
            if "error" in report:
                break
            got, _extras = read_back(Path(out_path), path, [])
            if got is None:
                report["error"] = f"新包回读布局失败：{path}"
            elif got != dicts:
                report["error"] = f"新包回读内容与导入的布局不一致：{path}"
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
    #: 批量导入时一并写进新包的其它布局：(新增/替换, 包内路径, 明文字节数)
    layouts: list[tuple[str, str, int]] = field(default_factory=list)
    issues: list[Diagnostic] = field(default_factory=list)
    notice: str = ""
    target_write: TargetWrite | None = None


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
    new_plain: bytes | None = None,
    extra_layouts: Mapping[str, bytes] | None = None,
) -> SavePlan:
    """保存前改动清单里除「布局改动」之外的那几行（图片/编码/待入包提示）。

    ``pack_path`` 给出时用 :class:`FlsPack` 判断每张待写入图片是**新增**还是
    **替换**（与原实现一致：只按路径哈希判定，不读负载）；同时用
    :func:`classify_target_write` 说明**目标条目本身**会被怎么写
    （新增 / 旧存储迁移 / 版式重写 / 字节不变），这是分析报告 P2-1 的落地。
    """
    issues = list(issues)
    if to_pack:
        issues.extend(_extra_encoding_issues(extras))
    images: list[tuple[str, str, int]] = []
    layouts: list[tuple[str, str, int]] = []
    notice = ""
    target_write: TargetWrite | None = None
    if to_pack and pack_path is not None:
        with FlsPack(pack_path) as pack:
            for name, data in (extra_layouts or {}).items():
                kind = "替换布局" if pack.contains(name) else "新增布局"
                layouts.append((kind, name, len(data)))
            if res_path and new_plain is not None:
                target_write = classify_target_write(
                    pack.read_named(res_path), path_hash(res_path), new_plain)
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
    if target_write is not None:
        notice = (target_write.summary
                  + (("\n" + notice) if notice else ""))
    return SavePlan(target=target, to_pack=to_pack, images=images,
                    layouts=layouts, issues=issues, notice=notice,
                    target_write=target_write)


# -- 目标条目会被怎么写（分析报告 P2-1）---------------------------------


@dataclass(frozen=True)
class TargetWrite:
    """写回时目标条目会发生什么：存储层与版式层分开说清楚。

    `storage`：``absent``（源包没有，属新增）/ ``native``（原生路径密钥）/
    ``legacy``（旧密钥）/ ``plaintext``（明文）/ ``unreadable``（既不是原生
    密钥也不是可识别布局——写回会拒绝替换）。
    `layout_rewritten`：原明文与编辑器即将写入的明文不同（**哪怕用户没改
    任何属性**，序列化也会归一化字段顺序与写法，见分析报告 P2-1：
    8 个真实 .dlg 里只有 1 个逐字节往返一致）。
    `migrated`：旧存储（明文/旧密钥）本次改为原生路径密钥。
    `byte_identical`：只有原生密钥且明文相同时才有意义（XOR 同密钥同明文
    ⇒ 存储字节不变）。
    """

    storage: str
    layout_rewritten: bool
    migrated: bool
    byte_identical: bool | None
    summary: str


def _classify_summary(storage: str, rewritten: bool, migrated: bool,
                      byte_identical: bool | None) -> str:
    if storage == "absent":
        return "目标条目：源包里没有 → 本次新增（原生路径密钥）。"
    if storage == "unreadable":
        return ("目标条目：现有字节既不是原生密钥、也不是可识别布局；"
                "写回会拒绝替换（不是 .dlg 条目）。")
    if storage == "native":
        if rewritten:
            return ("目标条目：原生密钥写入；「版式按编辑器序列化重写」"
                    "（原明文与新明文不同）→ 该条目字节会变。")
        if byte_identical:
            return "目标条目：原生密钥，明文未变 → 该条目字节不变。"
        return "目标条目：原生密钥，明文未变，但重新编码后存储字节不同。"
    label = "明文存储" if storage == "plaintext" else "旧密钥存储"
    if rewritten:
        return (f"目标条目：{label} → 本次迁移为原生路径密钥，"
                "而且「版式按编辑器序列化重写」 → 该条目字节会变。")
    return (f"目标条目：{label} → 本次迁移为原生路径密钥"
            "（明文内容未变，仅存储层迁移）。")


def classify_target_write(stored: bytes | None, entry_id: int,
                          new_plain: bytes) -> TargetWrite:
    """判断写回时目标条目是新增/迁移/版式重写/拒绝（不抛异常）。"""
    if stored is None:
        return TargetWrite("absent", False, False, None,
                           _classify_summary("absent", False, False, None))
    plain0: bytes | None = None
    storage = "unreadable"
    try:
        plain0 = decode_native(stored, entry_id)
        storage = "native"
    except ValueError:
        try:
            plain0 = plain_if_layout(stored)
        except ValueError:
            plain0 = None
        if plain0 is not None:
            storage = "plaintext" if stored.startswith(HEADER) else "legacy"
    if storage == "unreadable":
        return TargetWrite(storage, False, False, None,
                           _classify_summary(storage, False, False, None))
    rewritten = plain0 != new_plain
    migrated = storage in ("plaintext", "legacy")
    identical: bool | None = None
    if storage == "native" and not rewritten:
        try:
            identical = encode_layout(new_plain, entry_id) == stored
        except ValueError:
            identical = None
    return TargetWrite(storage, rewritten, migrated, identical,
                       _classify_summary(storage, rewritten, migrated,
                                         identical))


def classify_target_path(pack_path, res_path: str,
                         new_plain: bytes) -> TargetWrite:
    """从源包读出目标条目再分类；读不到（或读失败）按 ``absent`` 处理。"""
    stored: bytes | None = None
    try:
        with FlsPack(pack_path) as pack:
            stored = pack.read_named(res_path)
    except Exception:
        stored = None
    return classify_target_write(stored, path_hash(res_path), new_plain)
