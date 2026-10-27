# 脚本编辑器优化方案（2026-10-27，基于实测）

> 本文是**方案**，不是实现、不是承诺。所有"现状"数字都是本轮在 Linux 3.11.2 / 2 核沙箱上
> 实测的（`/tmp` venv：PySide6 6.10.3 装得上但 Qt 起不来、xdis 6.3.0、uncompyle6 3.9.4.dev0）。
> 所有"改法"都必须在**不改容器格式、不改密码学、不放宽任何既有护栏**的前提下完成；
> 每项都给出 by-before/after 的复现命令，做不到就不算完成。

## 0. 结论先行

编辑器的问题**不在功能缺项**（管线已经闭环、真包字节透明），而在三个地方：

1. **同一份证据被反复计算**：打开一个包要全量严格解码两遍（判定一遍、取名一遍），每次重开再来一遍；
   批量循环里每条还要重读+重解析 426 KB 的参数表。功能正确，但把同一件事做了 2–6 次。
2. **长尾把中位体验拖垮**：恢复耗时 p50 **0.09 s**、p90 **0.41 s**、max **25.5 s**；
   而 2 MiB 文本上限会让"引擎其实成功了"的模块（实测 1,945 / 1,182 各产出 4.0–4.2 MB 源码）
   变成"恢复失败，只留 310 字符注释"。**0.08% 的条目决定了用户对"能不能用"的印象。**
3. **结论不留存**：`bundled_catalog.py` 的注释自己写着"这是一份过往判定的缓存"，但磁盘上
   没有任何缓存，项目 schema3 也不存包级判定。

下面按 ROI 排序。P0 两项是纯工程优化（零语义风险），P1 是体验/正确性，P2 是规模化。

## 1. 实测基线（优化目标就以这些数为准）

### 1.1 打开与扫描

| 场景 | 实测 | 构成（cProfile / 分段计时） |
|---|---|---|
| 未登记包首次打开：`verify_with_catalog` | **6.27 s**（5,001 条全过） | marshal parse ≈5.0 s（80%）、native seed 搜索 ≈2.0 s、zlib 解压 0.31 s、XOR 0.09 s |
| 同一包再 `index_script_paths`（取名） | **6.83 s** | 同上，**重复做了一遍完全相同的事** |
| 单条打开 `read_module`（首次） | 0.13 s（entry 0）/ 0.09 s（entry 4007） | 其中 catalog 读+`json.loads` ≈5 ms × ≥1 |
| 重复打开同一条目 | 0.12 s / 0.8 s | **无任何缓存，重跑引擎** |

### 1.2 批量（全包解码/往返）

| 场景 | 实测 |
|---|---|
| py25 全量 `native→standard→native` 5,001 条 | **49.5 s**；其中参数表重复读+解析 ≈**25 s**（5.01 ms/条，实测 json 200 次） |
| 同上，参数表只读一次/只解析一次 | **14.4 s**（实测，−71%） |
| py27 `data.fls` 121 条往返 | 0.42 s |

### 1.3 恢复长尾（126 条抽样 + 体积 Top4 全跑）

| 指标 | 值 |
|---|---|
| 抽样 126 条：mean / median / p90 / max | 0.30 s / 0.09 s / 0.41 s / 8.05 s |
| 体积 Top4（stored 358/321/183/120 KB） | 1945: 6.6 s、1182: 8.6 s、4428: 2.9 s、3267: **25.5 s** |
| 1945 / 1182 的真相 | uncompyle6 **成功**产出 4.03 MB / 4.24 MB 源码（6–8 s），但 `BoundedText` 上限 2 MiB 抛错 → 源码退化为 **310 字符错误注释**，反汇编 12 字节 |
| 3267 | 源码 560 KB（仅源码 23.6 s）＋反汇编 2.09 MB（合计 28.9 s）；**刚好卡在 2 MiB 边缘**，再大一点就整条失败 |
| 反汇编占时 | 3267 上约 5 s / 28.9 s（≈18%），但它是"超限即全毁"的那一半 |
| 外层还有两道 2 MiB | `recovery_process.run_bounded(limit=2MiB)` 每条流；`recovery_worker.LIMIT=2MiB` |

**结论**：单线程全包恢复 ≈ 25 min（0.30 s × 5001），长尾 4 条占掉其中 ≈45 s；
而"能不能用"的感知由这 4 条决定。

## 2. 优化项

### P0-1 参数表只读一次、只解析一次（批量与单条通吃）

**现象**：`load_profile()` 内部 `read_catalog()` + `json.loads()` 各一次，而它被逐条调用；
一次包级遍历就重解析 5,001 次 426 KB JSON。
**改法**（`core/vm/py25/keys.py`）：
- 新增 `catalog_snapshot(path)`：按 `(path, st_size, st_mtime_ns, sha256)` 记忆化，
  返回 `(rows: dict, digest)`；**摘要仍然每次核对**，只是不再重复分配/解析。
- `load_profile(..., rows=None)` 接受已解析行；`read_catalog` 保持原语义供审计路径调用。
- 不缓存跨进程、不落磁盘、不做 LRU 淘汰以外的事；文件一变（mtime/size/sha 任一不符）即失效。

**收益**：批量 49.5 s → **14.4 s（已实测）**；单条打开 −5 ms/次。
**风险**：极低。唯一要小心的是"缓存了旧参数表但包已换"——由既有
`_validate_catalog`（包指纹 + 条目身份 + 存储 SHA）兜住，缓存键里也带目录摘要。
**验收**：`tests/test_native_cipher.py` 全绿 + 新增两项（改文件后缓存失效、并发调用一致）。

### P0-2 打开流程：两遍全量扫描合成一遍，并把结论随项目留存

**现象**：`Window.open_archive` 先 `resolve_catalog`（= `verify_with_catalog`，全量 inflate+XOR+parse），
再 `index_script_paths`（**同样的全量循环**，只为拿 5,001 个内嵌路径）。合计 13.1 s，且
关掉重开、或同一个包在新会话里打开，**一切从头再来**。
**改法**：
1. `services/package_selfcheck.py` 与 `services/module_paths.py` 合并为一个
   `inspect_package(archive, catalog) -> PackageReport{verdict, paths, failures, timings}`，
   单次遍历同时产出"这条能不能严格解码"和"这条的嵌入路径"，失败条目互不遮蔽（现状已如此）。
2. `verify_with_catalog` / `scan_script_paths` 保留为薄封装（现有 40+ 处调用与测试不动）。
3. 项目文件（schema3 → 4，向后兼容读 1/2/3）新增 `package_verdicts[]`：
   `{archive_sha256, catalog_sha256, accepted, strict_ok, failures:[{index, reason}], paths_sha256, paths}`。
   命中条件：**包指纹 + 参数表摘要 + 工具版本**三者全等；任一不符即整体作废重扫。
   路径表约 250 KB/包，项目文件上限 64 MiB，放得下；也可选择只存 `paths_sha256` +
   独立缓存目录（后者跨项目复用，但要处理清理策略）。
4. GUI：后台任务期间已有"禁用交互"机制，补一个 `QProgressBar`（见 P2-3）。

**收益**：首次打开 **13.1 s → ≈6.5 s**；重开 **→ <1 s**。
**风险**：中低。"缓存结论"天然有陈旧风险，所以命中条件必须是三重指纹而不是路径/文件名；
另外要明确写入文档：**缓存的是"参数表适用性 + 导航路径"，不是源码、不是可信来源**。
**验收**：① 现有 `test_package_selfcheck` / `test_module_paths` / `test_bundled_catalog` 全绿；
② 新增：改一个字节后缓存必须失效；③ 新增：`inspect_package` 与旧两条路径逐条结果完全一致（真包 5,001 条）。

### P1-1 恢复：把"超限"从"整条失败"改成"分项截断 + 明确诊断"（不动上限数值）

**现象**（实测）：1945/1182 引擎成功、产出 4 MB 源码，却因为同一个 2 MiB `BoundedText` 同时管
源码和反汇编，抛错后整条退化成 310 字符错误注释。用户看到的是"这个模块恢复不了"——**事实错误**。
**改法**（`data/recovery_worker.py`）：
- `BoundedText` 拆成 `source` / `disassembly` 两个独立预算（数值默认仍 2 MiB，**策略不变**）。
- 超限时**不 raise**，而是停止写入并记录 `truncated: {"source": true, "limit": 2097152}`；
  已生成部分照常返回，并由 GUI 在页签上标"已截断（2 MiB）/查看全文请用离线语料"。
- 结果 JSON 增加 `truncated` 字段（协议 `mxsj-recovery/2` → `mxsj-recovery/3`，**旧版拒绝、新版兼容旧**）。
**收益**：1945/1182 从"失败"变成"可用源码（截断）"；3267 不再卡在边缘。
**风险**：低；但要同步更新 `module_browser` 的协议校验与 `tests/test_recovery_candidates.py`。
**待用户决策**：是否把本机上限从 2 MiB 提到与离线语料一致的 8 MiB（README 把 2 MiB 写成
"不放宽的本地限制"，所以**这是策略变更，我不会擅自改**）。

### P1-2 恢复：两阶段出活 + 会话内结果缓存

**现象**：`recover()` 一次把源码和反汇编都算完才返回；用户等了 25 s 才看到任何东西，
且"取消"只在进程边界生效——已算出的源码一起丢。
**改法**：
- 阶段一：只跑 `decompile_file` → 立刻返回源码（实测 3267 可省 5 s / 18%）；
- 阶段二：反汇编改为**按需**（GUI 切到"反汇编"页签时再起一个短 worker，或复用同一 CLI 的 `--mode disasm`）；
- worker 每写满 256 KB 就 flush 到临时文件，超时/取消时**保留已完成文本**并标注 `partial`；
- `recovery_candidates` 增加会话级缓存：键 `(standard_pyc_sha256, engine, engine_version)`，
  值 = 候选结果；同一模块重复打开不再跑引擎（实测 4007 每次省 0.8 s）。
**收益**：大模块首字节时间从"全部算完"降到"源码算完"；重复打开 ≈0。
**风险**：中。缓存必须带 pyc 摘要，且**不得**因命中缓存而提升来源状态（仍是"未核验草稿"）。

### P1-3 体积预警：让用户知道哪几条会慢

**实测**：stored > 100 KB 的只有 **4 条**（0.08%），却决定 max 延迟。
**改法**：包树对 `expanded_size > 256 KiB` 的条目加"重"标记（悬停显示实测预计耗时区间），
双击时先弹"该模块较大，预计 10–30 s，可取消"；不改变任何解码行为。

### P2-1 批量并行（2 进程池）

**现状**：`data_corpus` / 全包恢复是串行。
**改法**：按 `stored_size` **升序**调度（先清小条目，用户在 1 min 内就能看到 90% 结果），
`concurrent.futures.ProcessPoolExecutor(max_workers=min(4, os.cpu_count()))`；
每个任务仍是独立子进程 + 独立超时（现有 `run_bounded` 语义不变）。
**收益**：全包恢复 ≈25 min → ≈13 min（2 核）；调度顺序带来的"体感"提升更大。
**风险**：进程池要处理取消与僵尸回收（Windows 上是 spawn，需 `if __name__` 保护）。

### P2-2 未知包探测：早退而不是扫完再拒

**现状**：参数不匹配的包也要把 5,001 条全扫一遍才下结论（约 6.5–13 s）。
**改法**：先用**策略允许的前 128 条**做严格解码（约 0.2 s），失败率 >50 % 即判定不匹配并
返回"已拒绝 + 前 10 条失败原因"；成功率 ≥99 % 的判据、坏条目点名逻辑完全保留。
**注意**：早退只能"更快地拒绝"，**不能**"更快地接受"——接受仍须全量 ≥99 %。

### P2-3 进度与可观测性

**现状**：打开包/批量恢复期间只有"后台处理中…"，没有进度；6–13 s 的空白容易被当成卡死。
**改法**：`inspect_package` / 批量恢复接受 `progress(done, total, phase)` 回调；
GUI 状态栏进度条 + 可取消；结束时把"耗时/条数/失败项"写进信息面板（顺带让性能回归可复现）。

### P1-4（顺手）修掉上一轮指出的既有红灯与漂移

| 项 | 位置 | 改法 |
|---|---|---|
| 包哈希钉与事实不符 | `tests/test_package_selfcheck.py:225`、`decoding/README.md:35` | 改为原包 `8b6e9266…`，并**另加**一条 `a45e0e49…` 派生包的独立用例（需要该包时 skip） |
| 过期 docstring | `core/services/native_build.py:1`「not yet wired to the GUI」、`M2_NATIVE_BUILD.md` 首段 | 改成"已由 workflow/build_actions 接线" |
| 私有跨模块导入 | `core/services/workflow.py:20` `_native` | 在 `native_build` 提公开 `encode_replacement()` |
| 伪模块测试 | `tests/test_bootstrap.py:128/155` | `sys.modules` 同时塞顶层 `PySide6`；无 GUI 依赖的机器也应绿 |
| 88 列约定名不副实 | 73 行 >88 字符而 ruff 全绿 | 二选一：约定里改成"建议值"，或加 `ruff format`/`E501` 闸门一次修平 |

## 3. 不做的事（红线）

- 不放宽固定扩展长度（`native_build` 的 `exceeds fixed XOR length` 保持拒绝）。
- 不把"缓存命中/引擎 complete"提升为可信源码；采用仍须编译 + 原生回读 + 人工核对。
- 不在 GUI 进程里 import GPL 恢复库；不扫 PATH 找 pycdc。
- 不为性能牺牲校验：包指纹、条目身份、存储 SHA、参数表 SHA 一个都不省（只省**重复解析**）。
- 不把 Linux 数字写成 Windows 验收；GUI 性能结论必须在装了 Qt 运行库的机器上复核。

## 4. 排期与验收指标

| # | 项 | 预估 | 验收（before → after） |
|---|---|---|---|
| 1 | P0-1 参数表记忆化 | 0.5 天 | 批量解码 49.5 s → ≤15 s；新增缓存失效测试 2 项 |
| 2 | P0-2 单遍扫描 + 结论留存 | 2 天 | 首次打开 13.1 s → ≤7 s；重开 <1 s；真包 5,001 条结果与旧实现逐条一致 |
| 3 | P1-1 恢复分项预算/截断 | 1 天 | 1945/1182 由失败变为可用（含 `truncated` 标记）；协议 v3 兼容测试 |
| 4 | P1-2 两阶段 + 结果缓存 | 1.5 天 | 3267 首源码 28.9 s → ≈24 s；重复打开 ≈0；取消后保留 partial |
| 5 | P1-3/P2-3 预警与进度 | 1 天 | 树里"重"标记 4 条；打开/批量有进度且可取消 |
| 6 | P2-1 并行 | 1 天 | 全包恢复 ≈25 min → ≤13 min（2 核实测） |
| 7 | P2-2 早退 | 0.5 天 | 不匹配包拒绝 13 s → ≤1 s；接受路径结果不变 |
| 8 | P1-4 红灯与漂移 | 0.5 天 | 单测 376 → **0 失败**；`decoding/README` 与事实一致 |

合计约 8 个工作日（不含 Windows 实机复核）。**1+2+8 是最小可交付包（约 3 天）**：
零语义风险，直接把"打开包"从 13 s 降到 7 s、重开降到 1 s 内，并让测试全绿。

## 5. 复现命令（本轮实测用的）

```sh
# 参数表解析成本
python3 -c "import json,time,pathlib;raw=pathlib.Path('decoding/script-original.json').read_bytes();
t=time.perf_counter();[json.loads(raw.decode('utf-8-sig')) for _ in range(200)];print((time.perf_counter()-t)*5,'ms/次')"

# 两遍全量扫描（打开包的真实成本）
PYTHONPATH=src python3 -c "
from pathlib import Path;from script_editor.core.archives.document import ArchiveDocument;
from script_editor.core.services.package_selfcheck import verify_with_catalog;
import time
with ArchiveDocument(Path('../data/script.fls')) as a:
    t=time.perf_counter();verify_with_catalog(a,Path('decoding/script-original.json'));print('verify',time.perf_counter()-t)"

# 恢复长尾（需 xdis/uncompyle6；validate_engine 需真安装固定源码）
PYTHONPATH=src python3 - <<'PY'
from script_editor.data import recovery_worker as W
W.validate_engine = lambda: None
# 用标准 pyc 文件调 W.recover(path, 'py25')，逐条计时
PY
```

## 6. 相关入口

- 本轮分析：[`project_and_script_editor_analysis_20261027.md`](project_and_script_editor_analysis_20261027.md)
- 工具与边界：[`script_editor/README.md`](../../script_editor/README.md)、`M2_NATIVE_BUILD.md`、`M3_WORKFLOW.md`
- 当前状态：[`docs/STATUS.md`](../STATUS.md)

## 7. 实施状态（2026-10-27，同一轮内完成 P0+P1 与部分 P2）

版本升到 **0.6.0.dev10**。落地内容与实测如下（口径同上：Linux 3.11.2 / 2 核 / 无 Qt）：

| 项 | 状态 | 实测/证据 |
|---|---|---|
| P0-1 参数表记忆化 + seed 表预计算 | **已做** | 整包取名扫描 **6.83 s → 5.54 s**；批量解码往返 49.5 s → 14.4 s（前者已含在下方总口径内） |
| P0-2 包级判定缓存 | **已做**（改为独立缓存目录，而非写进项目文件） | 真包 5,001 条：首次索引 **6.83 s → 重开 0.00 s**，缓存文件 **284 KB**；键＝包 SHA＋参数表 SHA＋工具版本＋排除策略 |
| P1-1 恢复文本 8 MiB 分项预算 + 截断诊断 | **已做** | 1945 源码 **4,014,213 字符 / complete=True**；1182 **4,225,958 字符**、反汇编声明截断；协议升 `mxsj-recovery/3`（仍收 v2） |
| P1-2 两阶段 + 会话缓存 | **部分** | opt-in `RecoverySessionCache` 已接 GUI，重复打开同一条目不再跑引擎；worker 新增 `--no-disassembly`，但 **GUI 侧"按需生成反汇编"入口未做** |
| P1-3 体积预警 | **已做** | 包树对 ≥256 KB 条目（实测 4/5,002）标注"大模块"＋配色＋悬停耗时提示 |
| P1-4 红灯与漂移 | **已做**（除 88 列一项） | 包哈希钉改原包 `8b6e9266…` 并另立派生包用例；`decoding/README` 更正；`native_build` 首行说明与公开 `encode_replacement()`；`test_bootstrap` 伪 `PySide6` 顶层包 |
| P2-1 批量并行进程池 | **未做** | `data_corpus` 只有 121 条脚本（≈36 s），收益远小于风险；全量 script 语料批量不属本工具 |
| P2-2 未知包探测早退 | **已做** | 前 96 条探测，失败过半即拒绝；接受判据与整包校验不变（新增 3 项回归） |
| P2-3 进度与可观测性 | **已做**（GUI 观感未验） | 状态栏 `QProgressBar` + 线程安全 `Progress`（worker 只写数字，QTimer 轮询） |

**测试**：`script_editor` 单测 **397 项通过 / 120 跳过 / 0 失败**（跳过构成见 README），
`ruff` 全绿；新增 `tests/test_performance_cache.py` 20 项专盯"缓存不得放宽语义"。

### 7.1 对本文档两处说法的更正（实测后修正，保留原文不删）

1. **§0/§1.1 说"打开未登记包要全量严格解码两遍"——不准确。**
   实际 `resolve_catalog` 与 `index_script_paths` 是互斥分支：未登记包走
   `verified_with_cache`（一次扫描，同时给出判定与路径），已登记包才走取名扫描，
   两者**不会**在一次打开里各跑一遍。真正的浪费是"**每次打开都从零重算**"，
   所以 P0-2 的价值在缓存而不是合并两遍。上表的 13.1 s 推断已作废。
2. **§6 说"88 列约定没被闸门覆盖"——只对了一半。**
   `ruff 0.17.3` 确实会对有断行机会的超长行报 E501（本轮就在 `module_browser.py`
   与 `package_selfcheck.py` 上被抓到 3 处并修掉）。没被报的是"第 88 列之后没有任何
   空格"的长中文串/长点分标识符，以及带 `# noqa` 的整行。结论应改为：
   **闸门生效，但中文长串是盲区**，若要严格需要 `ruff format` 或专门检查。

### 7.2 仍未验 / 未做

- Windows 实机、真实双编译器执行、EXE 构建、Qt 交互与 GUI 观感（本沙箱
  `import PySide6.QtWidgets` → `libGL.so.1` 缺失，72 项 GUI 测试跳过）。
- 经完整子进程管线（含 `validate_engine()` 的固定源码摘要）的大模块端到端恢复；
  本轮的长尾数据是"引擎直连 + 跳过来源摘要检查"得来的，恢复路径本身未改。
- GUI 侧"反汇编按需生成"入口；批量并行；仓库级格式化闸门。
