# 复核工具独立验收报告（Agent J）

- **验收对象：** Agent H 的 Python 加载层/API（`server/docs/review_browser/API_CONTRACT.md`）与
  Agent I 的复核网页（`server/apps/review_web/`）。
- **本次结论：第一阶段（固定数据验收基线）已完成并通过；第二、三阶段的实际集成验收尚未完成。**
  H 与 I 在本轮检查时**均未交付任何提交**，因此没有可以驱动的加载层、API 或网页。
  本文件逐项写明"已执行 / 未执行"及原因，**不声称全套通过**。
- **验收方分支：** `arena/d5a478f8-mxsj-tw-2022`（只在本分支工作，未切换、未推送他人分支）。
- **验收方提交：** 见本 PR（分支提交号在 PR 页面显示）。
- **报告生成时间：** 2026-10-12（UTC）。

---

## 1. 实际测试的 H/I 提交号

| 交付物 | 负责人 | 是否交付 | 实测提交号 | 核对方式 |
|---|---|---|---|---|
| `server/docs/review_browser/API_CONTRACT.md` | H | **未交付** | **无** | 文件不存在；仓库全量 grep `review_browser|review_web|API_CONTRACT|api/v1/review` 为 0 命中 |
| 加载层/API 实现（`server/apps/review_api`、`server/src/review*` 等） | H | **未交付** | **无** | 上述候选目录均不存在 |
| `server/apps/review_web/` | I | **未交付** | **无** | 目录不存在，仓库内无任何前端文件引用 `/api/v1/review/` |

核对基线：

- 协调分支最新 tip = `5f2369066c638297cce51f73adb961e011652c52`，含本轮已知基线
  `31f608394e40087fad5ab3dc871a20767a0ac174`（`31f6083` 是 `5f23690` 的父提交；
  `5f23690` 仅比 `31f6083` 多 3 个二进制 `map/*.map` 文件）。本验收分支已同步到该 tip，
  未额外变更。
- `gh pr list --state all --limit 30`：共 21 个 PR，#21 已合并，#13/#14/#15/#17 已关闭，
  **当前没有 open PR**。
- `git ls-remote origin`：远端 15 个 arena 分支及其 PR ref，逐一检查后没有任何一个包含
  H/I 的复核工具产物（另有两个分支为 mxLauncher 重建与 map_editor 碰撞网格，与本任务无关）。

> 含义：任何"API 语义""网页行为"结论现在都无法成立。下面的第二阶段/第三阶段条目
> 全部以 `NOT EXECUTED` 记录，并在 §6 列出恢复联调所需的全部前置条件。

---

## 2. 测试环境与启动命令

| 项 | 值 |
|---|---|
| 系统 | Linux 容器，仓库根 `/home/user/MXSJ_TW_2022` |
| Python | 3.11.2（**无任何 pip 依赖**，仅标准库） |
| Node / npm | v22.22.3 / 10.9.8（可访问 registry.npmjs.org） |
| 浏览器 | **无** chromium / chrome / firefox 可执行文件；Playwright/Puppeteer 浏览器下载域名不在允许网络内 |

验收执行命令（全部在仓库根目录运行）：

```bash
# 原有基线（未改动）
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check

# 新增独立验收（不属于原有 161 项）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance -q

# 拿到 H/I 交付后（第二阶段：真实联调，新进程启动 + 契约驱动探针）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
    --start --command "<API_CONTRACT.md 的启动命令，可含 {port}>" \
    --dataset-root-env <契约声明的数据根环境变量> \
    --map server/tools/review_browser_checks/ops_<name>.json
```

工具与环境说明另见 `server/tools/review_browser_checks/README.md`。

### 本轮实跑结果汇总

| 项目 | 命令 | 结果 |
|---|---|---|
| 原有架构测试 | `unittest discover -s server/tests/architecture` | **Ran 161 tests … OK**（26.3s） |
| 导出器逐字节检查 | `export_review_csv.py --check` | **exit 0**，22 个文件逐字节一致，工作区无改动 |
| 第一阶段独立复算 | `verify_data_baseline.py` | **30/30 pass** |
| 新增验收测试套件 | `unittest discover -s server/tests/review_browser_acceptance` | **Ran 44 tests … OK (skipped=5)**，跳过项全部标注 `NOT EXECUTED:` 原因 |
| 汇总账本 | `acceptance_runner.py` | `phase1=pass`、`phase2_live_api=not_executed`、`phase3_static_page=not_executed`、`integration_acceptance_complete=false`、`outstanding_api_checks=15`、`outstanding_web_checks=7`（证据：`server/tools/review_browser_checks/evidence/acceptance_report.json`） |

> 新增测试**不计入**原有 161 项；两条命令的通过情况分别陈述，避免混淆。

---

## 3. 第一阶段：固定数据验收基线（已完成）

复算方式：`server/tools/review_browser_checks/batch_fixture.py` 自带读取器，
按 `manifest.json` 的列类型重新解析 CSV/JSONL，**不导入** `export_review_csv.py`。
逐项结果（`verify_data_baseline.py` 的 30 项检查全部 pass）：

### 3.1 固定预期数字（来自 manifest / CSV / validation.json）

| 项目 | 期望 | 独立复算 | 一致 |
|---|---:|---:|---|
| 道具（items.csv） | 6851 | 6851（主键唯一） | ✅ |
| 宠物（pets.csv） | 135 | 135 | ✅ |
| 资质（pet_aptitudes.csv） | 131 | 131 | ✅ |
| 技能（pet_skills.csv） | 579 | 579（主键唯一） | ✅ |
| 候选技能关系（pet_skill_candidates.csv） | 458 | 458 | ✅ |
| 必带技能关系（pet_required_skills.csv） | 26 | 26 | ✅ |
| 被宠物引用的去重技能名称 | 143 | 143（候选 ∪ 必带，原名精确、不做简繁/模糊匹配） | ✅ |
| 技能名称匹配行（pet_skill_name_matches.csv） | 145 | 145 = 141 个单 ID 名称 + 2 个双 ID 名称 | ✅ |
| 技能覆盖记录（pet_skill_overwrites.csv） | 9 | 9（write_order 352–360，仅 4573 值变化） | ✅ |
| 隔离记录（quarantine.jsonl） | 4 | 4（1945/72548、2954/2800、3205/719、3205/4406） | ✅ |
| 缺失资质记录（pet_aptitude_missing.csv） | 3 | 3（3010、4021、4022） | ✅ |

`validation.json` 与上述复算逐项一致：`skill_write_count=590`、`skill_unique_count=581`
（= 579 导出 + 2 隔离）、`pet_skill_names=143`、`missing_aptitude_count=3`、
`quarantined_record_count=4`，五类 check 全部 `pass`；
`1945/2027/2954/3205` 分别为 `6852→6851(+1 隔离)`、`135→135(0)`、`132→131(+1)`、`581→579(+2)`。

### 3.2 地图 / NPC（数量、列、复合主键以 manifest 为准）

| 文件 | manifest 行数 | 复算 | 主键（manifest 声明） | 备注 |
|---|---:|---:|---|---|
| `mapdata_scene_dictionary.csv` | 104 | 104 | `scene_id` | 源条目 1301 |
| `mapdata_parent_scene.csv` | 6 | 6 | `scene_id` | 源表 MAP_ASCRIPTION |
| `sceneid2name_minimap_scenes.csv` | 57 | 57 | `scene_id` | 源条目 400 |
| `npcname2realnamedata_alias_to_realname.csv` | 55 | 55 | `alias` | 源条目 1799 |
| `npcposdata_records.csv` | 1335 | 1335 | `(scene_id, record_index)` | 源条目 2601；npcid=0 共 **632** 条 |
| `minimapnpcpos_pos_records.csv` | 1344 | 1344 | `(scene_id, scene_display_name, record_index)` | 源条目 2804；npcid=0 共 **631** 条 |
| `minimapnpcpos_wenzi_entries.csv` | 287 | 287 | `(scene_id, x, y)` | 源表 DATA_WENZI |
| `npc_2601_vs_2804_agreement.csv` | 677 | 677 | `(scene_id, npcid)` | 全部为非零 NPC ID |

同时确认：**1335/1344 是"记录数"而非唯一 NPC 数**（`npcid` 去重后的数量明显更小），
不能相加当作 NPC 总数。

### 3.3 来源分离 / 零 ID / 重复记录 / 原顺序

- **来源分离：** 每行 `source_entry`+`source_table` 与 manifest 声明的来源一致；
  2601 与 2804 两种 NPC 来源保持独立文件，只有 `npc_2601_vs_2804_agreement.csv`
  是显式对照表（manifest `source_entry=[2601, 2804]`），没有合并为"统一 NPC 表"；
  8 个 `maps_npcs/*.csv` 与 `server/docs/csv_checks/staging/` 逐字节一致。
- **零 ID：** npcid=0 的记录保留（632/631），且按 `(scene_id, record_index)` 各自成行，
  未被折叠成单个"NPC 0"；缺失资质记录没有用 0 号/零值填充。
- **重复记录：** 按 `(scene_id, npcid)` 统计，两份来源分别存在 **12** 组、**11** 组重复
  （单组最多 6 行），证明数据没有按该二元组错误去重；子表 `sequence` 保留重复与顺序。
- **原顺序：** 2601/2804 每个 scene 的 `record_index` 均为文件内的 `0..n-1`；
  宠物技能候选每个宠物的 `sequence` 均为 `0..n-1`；主键组合唯一性全部成立。
- **字符集/格式：** 核心 CSV = UTF-8 无 BOM + 全字段引号 + LF，且"重新编码后逐字节一致"
  （9 个文件全部通过）；`maps_npcs` = UTF-8 无 BOM + 最小引号 + CRLF（8 个文件全部通过）。
- **繁体保真：** `終級命中/高級命中/時空石/天魔返生術/地魔返生術/裝備店` 全部存在；
  `宠物/资质/技能书/装备店/时空石` 等简体改写串 0 命中。

### 3.4 隔离与未批准参数（关键语义）

- 2800：隔离记录中的 `法力資質=2130`、`法力資質最大值=1989` 原样保留；
  `pet_aptitudes.csv` 中不存在 2800；entry 2954 的 `applied_bounds` **等于** `saved_bounds`
  `[3973,7978,11868,…]`，**没有**采用未经批准的 `7979`（1700）候选。
  （注意：1700 这个数值本身在其他宠物行里合法存在，检查针对的是 2800 这一行是否被改写。）
- 72548：原始非法 CP950 字节 `c2f9a448a7a4c34dc5e9c5e784` 完整保留，未裁末字节、未替换占位符，
  且未出现在 `items.csv`。
- 719/4406：整行隔离，未进入 `pet_skills.csv`，隔离记录保留 `type/name/desc/fpneed/mpneed/hpneed` 六字段。
- 全部 profile（核心 5 个 + 地图 5 个）`automatic_bytecode_solver_enabled=false`；
  3205 `applied_bounds[1]=36123`（saved 为 36122）、2027 `applied_bounds[2..3]=16264/21751`
  （saved 为 16277/21755）、1945 `applied_bounds[2]=778759`（saved 778764），
  与 `batch_001_profiles.json` 完全一致；manifest `native_verified=false`。
- 制品完整性：22 个文件的 `bytes`/`sha256` 与 manifest 一致；固定输入
  `data/script.fls`、`tools/decompiler/script_fls_keys.json` 哈希一致；
  manifest 记录的 10 个工具/证据文件哈希也仍然一致（说明"manifest 仍描述当前生产者"）。

---

## 4. 第二阶段：API 与数据语义验收 —— **未执行（H 未交付）**

验收项已全部实现为可执行检查（`probe_live_api.py`），并以故障注入替身做过自检（§5）。
之所以**没有真实结论**，是因为没有可运行的加载层/API 与契约。

| 需求（任务书） | 检查 ID | 当前状态 | 未执行原因 |
|---|---|---|---|
| 1. 分页无遗漏、无意外重复、排序稳定 | `API-01`（按数据集拆分子项） | `NOT EXECUTED` | 无 API、无契约端点 |
| 2. 搜索与精确过滤符合契约 | `API-02` | `NOT EXECUTED` | 同上 |
| 3. 非法参数有明确错误，不悄悄替换 | `API-03` | `NOT EXECUTED` | 同上 |
| 4. `"false"`、空文本、缺失值不被错误转换 | `API-04` | `NOT EXECUTED` | 同上 |
| 5. 哈希/类型校验失败不得继续提供伪正常目录 | `API-05` | `NOT EXECUTED` | 需契约声明的启动命令 + 数据根环境变量，才能用损坏副本重启比对 |
| 6. 隔离记录不进入正常列表 | `API-06` | `NOT EXECUTED` | 无 API |
| 7. 2800 不被改成未经批准的 1700 | `API-07` | `NOT EXECUTED` | 无 API |
| 8. 3010/4021/4022 缺失资质不补零 | `API-08` | `NOT EXECUTED` | 无 API |
| 9. `高級命中` 保留 229/255 | `API-09` | `NOT EXECUTED` | 无 API |
| 10. `終級命中` 保留 329/355 | `API-10` | `NOT EXECUTED` | 无 API |
| 11. NPC 不按 `(scene_id, npcid)` 误去重 | `API-11` | `NOT EXECUTED` | 无 API |
| 12. 非法数据集、路径穿越、任意文件读取被拒绝 | `API-12` | `NOT EXECUTED` | 无 API |
| 13. 调用方不能修改底层目录数据 | `API-13` | `NOT EXECUTED` | 无 API |
| 14. 不存在编辑/保存/上传/发布接口 | `API-14` | `NOT EXECUTED` | 无 API；静态半边（源码路由扫描）亦无源码可扫 |
| 15.（附加）预览代理安全、页面不指向 localhost | `API-15` | `NOT EXECUTED` | 无页面可请求 |

设计要点（拿到交付后即可直接跑）：

- 全部动态用例使用 `batch_fixture.write_temp_batch()` 生成的**临时副本**，
  从不修改真实 `batch_001/`；`API-13` 在尝试写操作前后对副本做全量 sha256 比对。
- `API-05` 会用同一条契约启动命令分别在"正常副本"和"损坏副本"（字节篡改 + 类型篡改）上
  各起一个进程，逐字段比对，避免把"HTTP 200"当成通过。
- 期望值来自 CSV 独立复算（§3），不是 API 自报，也不是前端写死的计数。

---

## 5. 第三阶段：网页与实际联调 —— **未执行（I 未交付）；且无浏览器引擎**

| 验收项 | 检查 ID | 状态 | 说明 |
|---|---|---|---|
| 文档启动命令在新进程启动服务 | `API-05`/启动门 | `NOT EXECUTED` | 无启动命令可验 |
| 网页通过预览代理访问真实 API | `API-15` + 交付门 | `NOT EXECUTED` | 无网页 |
| 浏览器不请求沙箱 localhost/127.0.0.1 | `W-01`/`API-15` | `NOT EXECUTED`（静态部分待页面存在） | 静态扫描已就绪，无文件可扫 |
| 实际操作搜索、分页、详情、异常查看 | `API-01/02/…` | `NOT EXECUTED` | 无页面、无 API |
| 加载中 / 空结果 / 断连 / 错误状态 | `W-05`（源码级）+ DOM 级 | `NOT EXECUTED` | 源码级待页面存在；**DOM 级无浏览器引擎，本轮无法执行** |
| API 不可用时不自动切换假数据 | `W-02`（静态）+ 动态 | `NOT EXECUTED` | 同上 |
| 专用测试文本（HTML/脚本/引号/换行/公式前缀）只展示不执行 | `W-04`（静态）+ DOM 级 | `NOT EXECUTED` | 同上；需要 jsdom/浏览器 |
| 同名技能、隔离记录、缺失资质、NPC 重复记录不被界面隐藏 | `API-06/08/09/10/11` + DOM 级 | `NOT EXECUTED` | 同上 |

**明确声明：本轮没有任何网页验收结论，更没有"HTTP 200 即通过"式的判断。**

无浏览器引擎的后果与替代方案：

- 已实现：页面交付后的静态策略扫描（`scan_review_web.py`，含"前端不得写死固定计数"）。
- 未能实现：真实 DOM 中"注入文本只显示不执行""加载/空/错误状态实际呈现""界面未隐藏记录"
  这三类只能由浏览器验证的断言 —— 记为 `NOT EXECUTED`，不转写为通过。
- 建议在网页交付后补做：在具备 Chromium/Playwright 的环境重跑，或准许访问浏览器下载域名；
  届时可用 jsdom（npm registry 可达）做"经典脚本"页面的替代性 DOM 检查，
  但 jsdom 无法覆盖真实浏览器行为，仍需标注为"替代验证"。

### 5.1 验收套件自身的可信度（负向/正向对照，已执行）

为证明"这些验收检查真的能发现问题"，用故意植入缺陷的测试替身
（`conformance_negative_control.py`，**不是** Agent H 的 API、也不是契约提案）做了对照：

- **负向对照：** 开启全部缺陷时，探针必须报出 `API-01/03/04/06/07/08/09/10/11/12/13/14/15` 失败；
  自检测试逐条断言这些检查确实变红。
- **正向对照：** 关闭缺陷时，同一探针 16 项全部通过（`API-05` 走单独的启动式对照：完整性校验开 → pass，
  完整性校验关 → fail）。
- 若某个检查以后不再能发现对应缺陷，`test_harness_self_check.py` 会失败 —— 防止验收空转。

自检本身的结果：`test_harness_self_check.py` 的 6 项测试全部通过
（探针负向/正向对照各 1 项、API-05 损坏副本双向各 1 项、页面扫描正反例各 1 项）。

---

## 6. 未执行项与前置条件（按恢复顺序）

| # | 未执行项 | 阻塞原因 | 恢复所需 |
|---|---|---|---|
| 1 | 第二阶段全部 `API-01…API-15` | H 未交付契约与实现 | H 提交 `server/docs/review_browser/API_CONTRACT.md`（含前缀、启动命令、数据根环境变量）+ 可运行实现 |
| 2 | 验收方操作映射 `ops_*.json` | 依赖真实契约 | 契约落地后由验收方按其端点填写（绑定文档化端点，不另设 API） |
| 3 | 第三阶段静态 `W-01…W-06`、`H-01` | I 未交付网页 | I 提交 `server/apps/review_web/` |
| 4 | DOM 级注入/状态/隐藏检查 | 沙箱无浏览器引擎 | 具备 Chromium 的环境，或允许浏览器下载域名 |
| 5 | 预览代理端到端（真实代理 URL） | 依赖可运行服务 | 服务启动后通过平台预览代理访问 |
| 6 | 文档启动命令的新进程验证 | 依赖文档 | 契约/网页 README 给出确切启动命令 |

---

## 7. 问题清单（按严重程度）

| 级别 | 问题 | 影响 | 复现 / 证据 |
|---|---|---|---|
| **P0（阻塞）** | H、I 均未交付（无契约、无加载层/API、无网页） | 整个复核工具的**实际集成验收无法进行**；第二阶段 15 项、第三阶段 8 项全部 `NOT EXECUTED` | §1 核对方式；`acceptance_runner.py` 输出 `integration_acceptance_complete=false` |
| **P1** | 沙箱无浏览器引擎 | DOM 级断言（注入只显示不执行、加载/空/错误状态、界面未隐藏）无法执行 | §2 环境；`which chromium/chrome/firefox` 无结果 |
| **P2（待契约确认，非缺陷）** | 验收探针对以下语义作了**显式假设**，需与 H 的契约对齐：① 未知 query 参数应 4xx（用于路径穿越判定）；② `page_size` 有文档上限并拒绝超限；③ 复合主键以 `scene_id:record_index[:…]` 形式暴露；④ 数据集命名与数据根环境变量名 | 若契约不同，需修改 `ops_*.json` 映射与探针参数，而**不是**放宽验收预期 | `probe_live_api.py` 中 `API-03/11/12` 的实现与 `DATASETS` 约定 |
| **P3（报告口径）** | 固定计数（6851/135/131/579/458/145/143）在**前端源码**中出现即判失败（`W-03`），用于落实"不得写死计数" | 与数据的合法展示无关，但在页面交付后会触发人工确认 | `scan_review_web.py` 的 `W-03` |

本轮**未发现产品缺陷**：原因是 H/I 没有交付任何代码，无从发现。
故障注入替身产生的 15 项失败是**预期证据**（用于证明探针有效），不是产品问题。

---

## 8. 本轮改动与边界

只新增 Agent J 责任目录内的文件，未修改任何他人目录或受保护资产：

- 新增 `server/tests/review_browser_acceptance/`（44 项验收测试：31 项第一阶段独立复算、
  6 项验收套件自检、7 项交付门）
- 新增 `server/tools/review_browser_checks/`（读取器、基线复算、契约驱动探针、页面静态扫描、
  故障注入替身、账本 runner、README、`evidence/` 报告）
- 新增本文件 `server/docs/review_browser/ACCEPTANCE.md`

**未修改**：第一批 CSV、`manifest.json`、`batch_001_profiles.json`、`export_review_csv.py`、
客户端与 FLS/历史密钥库、`server/game_data/`、H/I 的实现目录（尚不存在）。
未执行任何恢复脚本或 eval 公式；未做简繁转换；未启动 `mock_server.py`。
`export_review_csv.py --check` 与 161 项架构测试在改动后仍全部通过，工作区在检查后无差异。

---

## 9. 复现步骤（本轮全部结论）

```bash
cd /home/user/MXSJ_TW_2022
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q     # 161 OK
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check                # exit 0, 22 files
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py   # 30/30 pass
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance -q
# -> Ran 44 tests ... OK (skipped=5)，跳过项原因均以 "NOT EXECUTED:" 开头
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py   # 账本
```

若要在 H/I 交付后复现联调（**当前无法执行，缺少前置条件**）：

```bash
# 1) 先确认契约存在
ls server/docs/review_browser/API_CONTRACT.md
# 2) 按其声明的端点填写 ops_<name>.json（绑定而非新设计）
# 3) 新进程启动 + 契约驱动验收
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
    --start --command "<contract startup command>" --dataset-root-env <declared env var> \
    --map server/tools/review_browser_checks/ops_<name>.json \
    --out server/tools/review_browser_checks/evidence/live_api_report.json
# 4) 页面静态策略
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/scan_review_web.py
# 5) 重新生成账本
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py
```

---

## 10. 结论

1. **固定数据验收基线已经独立建立并通过**：任务书列出的 11 个数字，
   加上地图/NPC 的行数、列、复合主键、来源分离、零 ID、重复记录、原顺序、
   隔离记录、缺失资质、未批准参数、制品哈希与文本保真，全部由验收方自己的读取器复算一致。
2. **实际集成验收尚未完成**：H、I 在本轮检查时均未交付，第二阶段 15 项、
   第三阶段 8 项全部为 `NOT EXECUTED`，并在 §4/§5/§6 逐项写明原因与恢复条件。
3. 验收工具与测试已就位并**经过故障注入自检**（负向必须变红、正向必须全绿），
   拿到交付后只需填写 `ops_*.json` 即可直接进入联调，无需改写验收预期。
4. 未发现产品缺陷（无产品可测）；未修改任何他人目录或受保护数据。
