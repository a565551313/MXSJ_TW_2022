# 复核工具独立验收报告（Agent J）

- **验收对象：** Agent H 的 Python 加载层/API（`server/docs/review_browser/API_CONTRACT.md` +
  `server/apps/review_api/` + `server/src/mxsj_catalog/`）与 Agent I 的复核网页
  （`server/apps/review_web/`）。
- **本次结论：实际集成验收已执行（不再是"未交付"），但未通过。**
  15 项 API 检查中 2 项失败（`API-03`、`API-05`），12 项页面运行时检查中 4 项失败
  （页面打开后**白屏**），新增验收套件 67 项中 15 项失败（12 项为加载层接口缺陷）。
  因此账本中 `integration_acceptance_complete = false`，**本报告不声称全套通过**。
  未执行项只剩 1 项（真实浏览器渲染，沙箱无浏览器可执行文件），已逐项写明原因。
- **验收方分支：** `arena/d5a478f8-mxsj-tw-2022`（只在本分支工作，未切换、未推送他人分支，未合并任何 PR）。
- **报告生成时间：** 2026-10-12（UTC）。

---

## 1. 实际测试的 H/I 提交号与集成方式

| 交付物 | PR | 实测提交号（完整） | 内容 |
|---|---|---|---|
| H：契约 + API + 加载层 | #22 `arena/...` | `9f6ab439a2ecdee37b59b99ddf95e77691490a0f` | `API_CONTRACT.md`（355 行，前缀 `/api/v1/review`）、`server/apps/review_api/`（`create_app` 工厂、10 条 GET 路由）、`server/src/mxsj_catalog/`（`loader.py`/`catalog.py`） |
| I：复核网页 | #24 `arena/...` | `97d317e3acba1809c52a6b25a5cfda2cc66f866b` | `server/apps/review_web/`（Vite 7 + React 19，dev/build/test/typecheck 脚本，`vite.config.ts` 代理 `/api → http://127.0.0.1:8000`） |
| J：验收方分支 | #23 | 本轮提交（见 PR #23 页面） | 验收套件、契约驱动探针、页面运行时探针、账本 |

集成方式（**不改动 H/I 任何文件**）：

```bash
git clone --shared /home/user/MXSJ_TW_2022 /tmp/integ     # 一次性集成克隆
cd /tmp/integ && git checkout -b integration
git fetch origin pr-22 pr-24                              # 9f6ab439 / 97d317e3
git merge origin/pr-22 origin/pr-24                       # 无冲突
```

所有联调命令都在 `/tmp/integ` 中执行（合并了 H+I 的代码），验收方的交付物改动仍只落在
`arena/d5a478f8-mxsj-tw-2022`；`batch_001/`、`batch_001_profiles.json`、导出器、客户端、
FLS/密钥库、`server/game_data/` 全程零改动（见 §9 校验）。

---

## 2. 测试环境与启动命令

| 项 | 值 |
|---|---|
| 系统 | Linux 容器，仓库根 `/tmp/integ`（集成克隆）/ `/home/user/MXSJ_TW_2022`（验收方分支） |
| Python | 3.11.2；H 的 API 需要 fastapi/uvicorn/pydantic → 使用 venv `/tmp/reviewvenv`（fastapi 0.143.0、uvicorn 0.54.0、pydantic 2.14.1、httpx 0.28.1） |
| Node / npm | v22.22.3 / npm 12.2.0（`npm install` 成功，`node_modules` 已安装） |
| 浏览器 | **无** chromium / chrome / firefox 可执行文件；只能访问 npm/pypi/GitHub，无法下载浏览器构建 |
| 沙箱内网 | 服务一律绑定 `0.0.0.0`/`127.0.0.1`，页面发出的请求全部是相对 `/api/...` 路径 |

**实际启动命令（本轮真实执行）：**

```bash
# 1) API：调用 H 的官方工厂 create_app(ReviewCatalog.load(batch_dir))，不改产品源码
/tmp/reviewvenv/bin/python server/tools/review_browser_checks/review_api_launch.py \
    --batch-dir <临时 batch 副本> --host 0.0.0.0 --port 8000
#    （探针默认按 ops_review_api.json 的 startup_command 启动，等价于文档命令）

# 2) 页面：I 的 dev server，代理指向上面的 API
cd server/apps/review_web
VITE_API_PROXY_TARGET=http://127.0.0.1:8000 PORT=5173 npm run dev     # 实测 VITE v7.3.7

# 3) 页面运行时探针（按 I 自己声明的端点逐条请求 + 用 I 自己的 vite build 产物做渲染）
node --experimental-strip-types server/tools/review_browser_checks/web_origin_probe.mjs \
    --app-dir server/apps/review_web --origin http://127.0.0.1:5173
node --experimental-strip-types server/tools/review_browser_checks/web_ui_smoke.mjs \
    --app-dir server/apps/review_web --origin http://127.0.0.1:5173

# 4) 一键账本（自动完成 1–3 与会话回收）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py \
    --api-sha 9f6ab439 --web-sha 97d317e3
```

### 2.1 本轮实跑结果汇总（全部为真实执行）

| 项目 | 命令 | 结果 |
|---|---|---|
| 原有架构测试 | `unittest discover -s server/tests/architecture -q` | **Ran 161 tests … OK**（31.5s） |
| 导出器逐字节检查 | `export_review_csv.py --check` | **exit 0**（22 个文件逐字节一致） |
| 第一阶段独立复算 | `verify_data_baseline.py` | **30/30 pass** |
| 第二阶段 API（20 项） | `probe_live_api.py --start --map ops_review_api.json`（+ 以真实页面 origin 重跑以执行 API-15） | **18 pass / 2 fail**（`API-03`、`API-05`） |
| 第三阶段静态页面（8 项） | `scan_review_web.py` | **8 pass**（含代理配置/注释/测试的误报修复） |
| 第三阶段页面运行时（12 项） | `acceptance_runner.py` 的 `phase3_web_runtime` 会话 | **5 pass / 4 fail / 1 not_executed**（W-12/13/14、U-02/04 失败；U-05 无浏览器） |
| 新增验收测试套件 | `unittest discover -s server/tests/review_browser_acceptance` | **Ran 67 tests，15 failures，0 skipped**（12 项加载层接口 + 3 项交付门） |
| 汇总账本 | `acceptance_runner.py` | `phase1=pass`、`phase2_live_api=fail`、`phase3_static_page=pass`、`phase3_web_runtime=fail`、`new_acceptance_suite=fail`、`integration_acceptance_complete=false`；证据 `server/tools/review_browser_checks/evidence/acceptance_report.json` |

> 新增的 67 项测试**不计入**原有 161 项，两条命令分别陈述。

---

## 3. 第一阶段：固定数据验收基线（已完成，结论不变）

复算方式：`server/tools/review_browser_checks/batch_fixture.py` 自带读取器，
按 `manifest.json` 的列类型重新解析 CSV/JSONL，**不导入** `export_review_csv.py`。
`verify_data_baseline.py` 的 30 项检查在本轮（合并 H+I 之后）仍 **30/30 pass**。

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

同时确认：**1335/1344 是"记录数"而非唯一 NPC 数**，不能相加当作 NPC 总数。
（H 的 `/health` 自报 `total_records_count=12202` 是 17 个数据集行数之和；
契约文字里的 12085 与之相差 117，属于契约文字口径问题，不影响上述复算。）

### 3.3 来源分离 / 零 ID / 重复记录 / 原顺序

- **来源分离：** 每行 `source_entry`+`source_table` 与 manifest 声明的来源一致；
  2601 与 2804 保持独立文件，只有 `npc_2601_vs_2804_agreement.csv` 是显式对照表，
  没有合并为"统一 NPC 表"；8 个 `maps_npcs/*.csv` 与 `server/docs/csv_checks/staging/` 逐字节一致。
- **零 ID：** npcid=0 的记录保留（632/631），按 `(scene_id, record_index)` 各自成行；
  缺失资质记录没有用 0 号/零值填充。
- **重复记录：** 按 `(scene_id, npcid)` 统计，两份来源分别存在 **12** 组、**11** 组重复
  （单组最多 6 行），证明数据没有按该二元组错误去重。
- **字符集/格式：** 核心 CSV = UTF-8 无 BOM + 全字段引号 + LF（重新编码后逐字节一致）；
  `maps_npcs` = UTF-8 无 BOM + 最小引号 + CRLF。
- **繁体保真：** `終級命中/高級命中/時空石/天魔返生術/地魔返生術/裝備店` 全部存在；
  简体改写串 0 命中。

### 3.4 隔离与未批准参数（关键语义）

- 2800：隔离记录中的 `法力資質=2130`、`法力資質最大值=1989` 原样保留；
  `pet_aptitudes.csv` 中不存在 2800；entry 2954 的 `applied_bounds` **等于** `saved_bounds`，
  **没有**采用未经批准的 `7979`（1700）候选。
- 72548：原始非法 CP950 字节 `c2f9a448a7a4c34dc5e9c5e784` 完整保留。
- 719/4406：整行隔离，未进入 `pet_skills.csv`。
- 全部 profile `automatic_bytecode_solver_enabled=false`；`1945/2027/2954/3205` 的
  `applied_bounds` 与 `batch_001_profiles.json` 完全一致；manifest `native_verified=false`。
- 制品完整性：22 个文件的 `bytes`/`sha256` 与 manifest 一致；固定输入
  `data/script.fls`、`tools/decompiler/script_fls_keys.json` 哈希一致。

---

## 4. 第二阶段：API 与数据语义验收 —— **已执行，18/20 通过**

探针：`server/tools/review_browser_checks/probe_live_api.py`，操作映射
`server/tools/review_browser_checks/ops_review_api.json`（绑定 H 文档化的端点/参数/响应信封，
不另设 API）。期望值来自第一阶段 CSV 独立复算，而非 API 自报。

| 需求（任务书） | 检查 ID | 结果 | 说明 |
|---|---|---|---|
| 1. 分页无遗漏、无意外重复、排序稳定 | `API-01`（6 个数据集子项） | ✅ pass | items 6851 行 / 28 页 @250 全部走完且不重不漏；其余 5 个数据集同样完整 |
| 2. 搜索与精确过滤符合契约 | `API-02` | ✅ pass | `時空石` → [41052]；精确过滤与 CSV 行集一致 |
| 3. 非法参数有明确错误，不悄悄替换 | `API-03` | ❌ **fail** | 见 §6.2 |
| 4. `"false"`、空文本、缺失值不被错误转换 | `API-04` | ✅ pass | bool false / 空串 / null / int 逐条与 CSV 交叉核对 |
| 5. 哈希/类型校验失败不得继续提供伪正常目录 | `API-05` | ❌ **fail** | 见 §6.1（CSV 字节/类型损坏确实会拒启动；缺的是证据文件与 manifest 覆盖） |
| 6. 隔离记录不进入正常列表 | `API-06` | ✅ pass | 72548/2800/719/4406 均不在正常列表，4 条隔离记录完整 |
| 7. 2800 不被改成未经批准的 1700 | `API-07` | ✅ pass | 正常批次下 2800 详情 404，列表无 2800 |
| 8. 3010/4021/4022 缺失资质不补零 | `API-08` | ✅ pass | 独立端点返回 3 条且不含 `法力資質` 键 |
| 9. `高級命中` 保留 229/255 | `API-09` | ✅ pass | 返回 229、255 两条（`_pk` 为 `高級命中:229` 形式） |
| 10. `終級命中` 保留 329/355 | `API-10` | ✅ pass | 返回 329、355 两条 |
| 11. NPC 不按 `(scene_id, npcid)` 误去重 | `API-11` | ✅ pass | npcposdata 保留 632 条零 ID、131 组重复；minimap 631/130 |
| 12. 非法数据集、路径穿越、任意文件读取被拒绝 | `API-12` | ✅ pass | 全部 404/400，无文件内容泄漏 |
| 13. 调用方不能修改底层目录数据 | `API-13` | ✅ pass | 请求前后副本全量 sha256 一致 |
| 14. 不存在编辑/保存/上传/发布接口 | `API-14` | ✅ pass | 运行中服务的 `/openapi.json` 恰好 10 条 GET、无变更方法；16 个可疑路径 POST 全部非 2xx；源码无变更类路由 |
| 15.（附加）预览代理安全、页面不指向 localhost | `API-15` | ✅ pass | 入口 HTML 相对资源、Host/Origin 转发 200、`/api` 代理 200（前端契约不符的问题记在 `W-12/13/14`，不重复计为 API 缺陷） |

**通过的语义要点（真实后端，非替身）：** 列表信封 `{dataset,total,offset,limit,count,records[]}`、
每条记录带 `_pk`、`offset/limit`（默认 50，1..500，越界 400）、未知过滤列 400（但见 §6.2）、
未知数据集 404、`POST/PUT/PATCH/DELETE` 405。

**验收方自身修正（不属于产品缺陷，已修，全部在套件自检里有回归）：** 首轮探针把
`search_expect_ids` 写成裸 `229`，而真实 `_pk` 是 `高級命中:229`；`API-12` 曾把 `path`/`file`
当参数名传入（H 正确地 400）；`API-14` 的源码扫描曾把 `node_modules` 里的同名目录当文件读而报错；
`API-05` 的"读取探针"曾用错分页参数名（`page/page_size` 打到 offset/limit 的 API），
使 400 看起来像"已拒绝损坏数据"——现改为按映射声明的分页风格请求，并增加完好副本对照，
只有对照成功时"损坏副本被拒"才算通过。以上都是验收侧问题，不作为 H/I 的缺陷计入。

---

## 5. 第三阶段：网页与实际联调 —— **已执行；页面可打开但白屏**

### 5.1 静态策略扫描（`scan_review_web.py`，8/8 pass）

| 检查 | 结果 | 说明 |
|---|---|---|
| `W-00` 页面交付 | ✅ | 47 个前端文件，按 产品代码/测试/夹具/构建配置 分类 |
| `W-01` 浏览器不请求沙箱 localhost | ✅ | 产品代码无绝对 localhost 请求；`vite.config.ts` 的 `127.0.0.1:8000` 代理是**必要的服务端配置**，不判为违规 |
| `W-02` API 不可用时不自动切换假数据 | ✅ | fixture 模式需显式 `VITE_REVIEW_DATA_MODE=fixture`（opt-in），无自动回落 |
| `W-03` 前端不写死固定计数 | ✅ | 产品代码未出现 6851/1335 等冻结计数 |
| `W-04` 特殊文本只展示不执行（静态半边） | ✅ | 产品代码无 `dangerouslySetInnerHTML`/`innerHTML=`/`eval` 等 sink；测试里的负向断言不再误报 |
| `W-05` 加载/空/错误状态（源码半边） | ✅ | 有关键字；DOM 级结论见 5.2 |
| `W-06` 网络调用使用相对 URL | ✅ | 全部 `/api/v1/review/...` 相对路径 |
| `H-01` API 源码不含变更类路由 | ✅ | 仅 CORS `allow_methods`，非路由声明 |

> 误报修复：扫描器现在区分 产品运行时代码 / 测试 / 夹具 / 构建配置 / 注释与字符串；
> 只对**产品代码**判违规，只能给提示的一律标 `review`（待人工确认），不再当作已确认缺陷。
> 正反例都有回归测试（`test_harness_self_check.PageScannerSelfCheck`，3 项全绿）。

### 5.2 运行时检查（`web_origin_probe.mjs` + `web_ui_smoke.mjs`，12 项：5 pass / 4 fail / 1 未执行）

真正的做法：先按 `ops_review_api.json` 启动 H 的 API（临时 batch 副本），再用
I 自己的 dev server 起页面（`VITE_API_PROXY_TARGET` 指向该 API），然后
① 导入 I 自己的 `src/api/contract.ts`，把**它将要请求的每一个端点**逐条打到真实 web origin；
② 用 I 自己的 `vite build` 产物在 jsdom 中真实挂载应用，采集 console/未捕获异常/请求/渲染结果。

| 检查 | 结果 | 证据 |
|---|---|---|
| `W-10` 入口页面由 web origin 提供且资源相对 | ✅ | `GET /` 200，`<script src="/@vite/client">`、`/src/main.tsx`，无绝对沙箱 URL |
| `W-11` 入口模块可加载且不含沙箱主机 | ✅ | 应用模块 200；`/@vite/*`、`/node_modules/*` 属 dev-server 工具，不计入 |
| `W-12` 列表页拿到自己解析的信封 | ❌ **fail** | `GET /api/v1/review/items?page=1&page_size=25` → **404** `{"error":…}`；前端 `Page<T>={items,total,page,page_size}` 永远拿不到 |
| `W-13` 概览/异常/NPC/地图端点存在 | ❌ **fail** | `/anomalies`、`/maps/datasets`、`/npcs`、`/npcs/agreement` 全部 404 |
| `W-14` 详情页能取到单条记录 | ❌ **fail** | `/items/11`、`/pets/1010`、`/skills/101` 全部 404（真实端点形如 `/datasets/items/records/11`，返回带 `_pk`） |
| `W-15` web origin 能把 `/api` 代理到 API | ✅ | 代理 `GET /api/v1/review/datasets/items/records?offset=0&limit=1` → 200 |
| `W-16` web origin 接受转发后的 Host/Origin | ✅ | 带 `Host: review-preview.e2b.app` 等头请求 `/` → 200（`allowedHosts: true` 生效） |
| `U-01` 交付前端可用自身工具链构建 | ✅ | `vite build`（IIFE 供 jsdom 执行）成功产出 bundle |
| `U-02` 挂载后的应用渲染出可见内容 | ❌ **fail** | `#root` 的 `innerHTML=""`、`textContent=""` —— **白屏** |
| `U-03` 应用发出的每个请求都成功 | ✅ | 应用只发出 1 个请求 `GET /api/v1/review/batch` → 200（**注意：HTTP 200 ≠ 页面正常**） |
| `U-04` 加载期间无 console 错误 | ❌ **fail** | `uncaught TypeError: Cannot read properties of undefined (reading 'length')  at OverviewPage`（见 §6.3） |
| `U-05` 仅真实浏览器可做的检查 | ⏸ **not_executed** | 沙箱无浏览器可执行文件，也无法下载：布局/截图/真实浏览器 console 无法验证 |

**白屏根因链（可复现）：** 应用启动 → 只请求 `/batch`（返回 200，信封是
`{batch, native_loader_confirmed, manifest_files_count, csv_format, tables_summary{…}, validation_summary}`）
→ `OverviewPage` 读取 `resource.data.tables.length`，而 H 的信封里没有 `tables` 数组
（只有 `tables_summary` **对象**）→ `undefined.length` 抛错 → React 整棵树卸载 → `#root` 为空。
这与协调者复现的现象一致（`/batch` 200、结构不符、白屏）。

---

## 6. 失败项：复现步骤与证据

### 6.1 `API-05` ／ 加载层：证据文件缺失或被篡改仍报 `ready`（严重：**P1**）

复现（任意一条，均在临时副本上做，不改 `batch_001/`）：

```bash
cp -r server/docs/csv_checks/batch_001 /tmp/b1 && rm /tmp/b1/quarantine.jsonl
/tmp/reviewvenv/bin/python server/tools/review_browser_checks/review_api_launch.py \
    --batch-dir /tmp/b1 --port 8211
curl -s http://127.0.0.1:8211/api/v1/review/health
# => {"status":"ready","batch":"batch_001","loaded_files_count":22,"datasets_count":17,
#     "total_records_count":12202}            <-- 少了一个证据文件，仍自称 ready
curl -s http://127.0.0.1:8211/api/v1/review/quarantine
# => {"total":0,"records":[]}                 <-- 4 条隔离证据被静默清零
```

| 场景（自动探针/接口测试） | 期望 | 实测 |
|---|---|---|
| 删除 `quarantine.jsonl` | 拒启动或明确报错 | `ready`，`quarantine=0` |
| 删除 `validation.json` | 拒启动或明确报错 | `ready`（校验结论缺失却照常提供目录） |
| 删除 `overwrite_evidence.jsonl` | 拒启动或明确报错 | `ready` |
| 删除 `maps_npcs/provenance.json` | 拒启动或明确报错 | `ready` |
| 篡改 `quarantine.jsonl`（`2800→1700`，sha256 与字节数都与 manifest 不符） | 拒启动或报错 | `ready`，且 `/quarantine` 直接返回被篡改的 `record_key: 1700`（**把未经批准的值当证据提供**） |
| 缩短 `quarantine.jsonl` 并同步更新 manifest 的 sha256/bytes（1 行 vs manifest `rows=4`） | 行数校验失败 | `ready` |
| 从 `manifest.json` 删掉 `items.csv`（数据集 17 → 16） | 拒绝缩小后的 manifest | `ready`，静默少一个数据集 |

对照：**CSV 的字节/类型损坏会正确拒启动**（`csv_hash_corruption`、`csv_type_corruption`
两种情况进程退出并报 sha256/size/type 错误）——缺的是**辅助证据文件与 manifest 覆盖**这两类校验。
其中"截短并同步更新哈希"一行由加载层接口测试直接验证（`rows=1` vs manifest `rows=4`），
其余 6 行同时由运行中的 API 与加载层接口测试验证；对应测试：
`test_catalog_loader_acceptance.EvidenceFileTests`、`ManifestCoverageTests`。

> 判据说明：探针先在**完好副本**上做一次同样的读取作为对照（control），只有对照成功（200）时，
> "损坏副本上的 4xx/5xx"才被认定为"拒绝提供损坏数据"；否则记为验收工具自身不可信并直接判失败。
> 本轮 control 为 200，上述 6 项均为"直接 served → 记为产品缺陷"，不是"读取被拒"。

### 6.2 `API-03` ／ 加载层：非法或拼错的参数被静默忽略（严重：**P2**）

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  'http://127.0.0.1:8210/api/v1/review/datasets/items/records?sort_by=client_shape_id&order=sideways'
# => 200（按 asc 处理，正文没有任何提示）
curl -s 'http://127.0.0.1:8210/api/v1/review/quarantine?entry_indexx=2954'      # => 200 total=4（拼错被忽略，返回全量）
curl -s 'http://127.0.0.1:8210/api/v1/review/overwrites?keyy=4573'               # => 200 total=9
curl -s 'http://127.0.0.1:8210/api/v1/review/batch?batch=wrong'                  # => 200
curl -s 'http://127.0.0.1:8210/api/v1/review/missing-aptitudes?limit=1'          # => 200（固定形状端点忽略 limit/offset）
```

契约只声明 `order ∈ {asc, desc}`，且"未知 query 参数=精确过滤"。当前实现里
**只有列表端点的未知过滤列会 400**，固定形状端点（quarantine/overwrites/batch/missing-aptitudes/
ambiguous-skills）与 `order` 完全没有白名单校验 —— 拼错参数会得到"看起来正常"的结果，
比报错更危险（复核者会以为过滤生效了）。接口级对应测试：`test_invalid_order_is_rejected`。

### 6.3 页面：交付的网页打开后白屏（严重：**P0**）

```bash
# 1) 起 API 与页面（见 §2）
# 2) 前端声明的端点（取自 I 自己的 src/api/contract.ts）
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:5173/api/v1/review/items?page=1&page_size=25'   # => 404
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:5173/api/v1/review/anomalies'                    # => 404
curl -s -o /dev/null -w '%{http_code}\n' 'http://127.0.0.1:5173/api/v1/review/maps/datasets'                # => 404
# 3) 用 I 自己的构建产物在 jsdom 中执行应用
node --experimental-strip-types server/tools/review_browser_checks/web_ui_smoke.mjs \
    --app-dir server/apps/review_web --origin http://127.0.0.1:5173 --out /tmp/ui.json
# => U-02 fail: #root 渲染结果为空；U-04 fail:
#    TypeError: Cannot read properties of undefined (reading 'length')  at OverviewPage
```

- 端点契约不符：`src/api/contract.ts` 声明
  `/items`、`/pets`、`/skills`、`/maps/datasets`、`/npcs`、`/npcs/agreement`、`/anomalies`
  与 `page`/`page_size` 分页；H 的契约是
  `/datasets/{id}/records`（`offset`/`limit`）+ `/datasets`、`/quarantine`、`/overwrites`、
  `/missing-aptitudes`、`/ambiguous-skills`。两者没有一个共同的数据端点。
- 白屏直接原因：`OverviewPage.tsx:217` 用 `resource.data.tables.length`，而 `/batch`
  返回的是 `tables_summary` 对象且没有 `tables` 字段；应用没有错误边界，
  一个页面抛错就整棵树卸载 → 空 `#root`。
- 附带：(I) `src/api/types.ts` 头部注释仍写"契约尚未落地、各类型待与 `API_CONTRACT.md` 对齐"，
  与已交付的 H 契约脱节。

### 6.4 加载层：CSV 引号内换行被破坏（严重：**P2**）

`loader.py` 用 `data.decode().splitlines()` 切行后再交给 CSV 解析，导致**引号字段内的换行被拆开**。

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance \
    -p test_catalog_loader_acceptance.py -k CsvFidelity
# => 3 个 subTest 全 fail：LF / CRLF / CR 三种换行在引号字段里都无法保持原样
#    （正确做法是 decode 后以 newline='' 交给 csv.reader）
```

当前 `batch_001` 的行内分隔用的是 `#r` 风格标记而非真实换行，所以**真实数据暂未触发**；
但只要复核源 CSV 里出现带换行的说明文本（CSV 允许），字段内容就会被破坏。
`QuotationTests.test_qa_on_real_batch_records_round_trip` 证明真实批次当前是读得对的。

### 6.5 加载层：`DatasetSchema.source_entry` 仍是可变 list（严重：**P3**）

```bash
# 实测：ReviewCatalog.get_dataset('npc_2601_vs_2804_agreement').schema.source_entry == [2601, 2804]
# 调用方 list.append(...) 会改到目录内部结构（get_batch_info() 现在返回副本，此类问题仅剩这里）
```

---

## 7. 未执行项与原因（全部列明，不转写为通过）

| # | 未执行项 | 原因 | 影响 |
|---|---|---|---|
| 1 | `U-05`：真实浏览器中的渲染、布局/白屏视觉判定、截图证据、真实浏览器 console | 沙箱内没有 chromium/chrome/firefox 可执行文件，且只允许访问 npm/pypi/GitHub，无法下载浏览器构建（Playwright/Puppeteer 的下载域名不可达） | 白屏已由"执行 I 自己的构建产物 + 捕获未捕获异常 + 空 `#root`"给出可复现证据；但**没有**真实浏览器的截图/视觉回归结论 |
| 2 | 平台预览 URL（`https://{port}-{sandboxId}.e2b.app`）的直连访问 | 验收在沙箱内进行，无法从外部浏览器访问该域名 | 已用转发头（`Host`/`Origin`/`X-Forwarded-Proto`）模拟并通过（`W-16`）；公网预览的可见性属平台侧，需人工确认 |

其余原"未执行"项本轮全部已执行（第二阶段 15 项 + 静态 7 项 + 运行时 12 项，仅上表 1 项除外）。

---

## 8. 问题清单（按严重程度排序）

| 级别 | 归属 | 问题 | 影响 | 复现 / 证据 |
|---|---|---|---|---|
| **P0（阻塞）** | I | 交付的网页打开后**白屏**；`OverviewPage` 对 `/batch` 的 `tables` 字段做 `.length` 而后端返回 `tables_summary`，且无错误边界 | 复核工具无法使用：页面能打开但没有任何内容 | §6.3；`web_ui_smoke.json` 的 `U-02`/`U-04`；`OverviewPage.tsx:217` |
| **P0（阻塞）** | I | 前端端点契约与 H 的契约完全不匹配（`/items`、`/pets`、`/skills`、`/maps/datasets`、`/npcs`、`/anomalies` + `page/page_size` vs `/datasets/{id}/records` + `offset/limit`） | 即使修好渲染，也拿不到任何数据（6 类 404） | §6.3；`W-12/13/14`；`src/api/contract.ts` |
| **P1** | H | 辅助证据文件缺失/被篡改/被截短不报错：删除 `quarantine.jsonl`（`/quarantine` 变 0 条）、`validation.json`、`overwrite_evidence.jsonl`、`maps_npcs/provenance.json`；`2800→1700` 篡改后 `/quarantine` 直接返回未经批准的值 | 复核报告的依据（隔离/校验/覆盖/来源证据）可被静默删除或改写，工具仍宣称 `ready`，**会误导复核结论** | §6.1；`API-05`；`EvidenceFileTests`/`ManifestCoverageTests` |
| **P1** | H | manifest 覆盖校验缺失：删掉 `items.csv` 后 17 → 16 个数据集仍 `ready`；缩短 `quarantine.jsonl` 并更新哈希后行数（1 vs 4）不校验 | 数据集可以整块消失而不被发现 | §6.1 |
| **P2** | H | 非法/拼错参数被静默忽略：`order=sideways` 按 asc 处理；`entry_indexx`、`key=`、`keyy`、`batch=`、`missing-aptitudes?limit/offset` 全部 200 | 复核者以为过滤生效，实际拿到全量数据；契约声明的参数白名单没有实现 | §6.2；`API-03`；`test_invalid_order_is_rejected` |
| **P2** | H | CSV 引号内换行被 `splitlines()` 破坏（LF/CRLF/CR 三种都错） | CSV 语义级缺陷：带换行的字段内容会被改写 | §6.4；`CsvFidelityTests` |
| **P3** | H | `DatasetSchema.source_entry` 返回可变 list（`[2601, 2804]`） | 调用方可原地修改目录内部结构 | §6.5；`ImmutabilityTests` |
| **P3** | I | 无错误边界 / 未定义字段防御，任何页面抛错都会整树卸载成白屏；`types.ts` 头部注释仍称契约未落地 | 让 P0 从"一个字段不符"升级为"整页白屏"，且误导后续维护者 | §6.3 |

**已确认不是缺陷（避免误报）：** `vite.config.ts` 的 `0.0.0.0` 绑定与
`127.0.0.1:8000` 代理（Arena 预览必需的服务端配置）；测试文件中的
`dangerouslySetInnerHTML` 负向断言；注释里"不使用 innerHTML/不回落假数据"的说明；
`/openapi.json` 无变更方法；`allow_methods` 属 CORS 配置而非路由。

---

## 9. 本轮改动与边界

只改动 Agent J 责任范围内的三个位置：

- `server/tests/review_browser_acceptance/`：新增
  `test_catalog_loader_acceptance.py`（22 项加载层接口验收，覆盖 §6.1/6.4/6.5），
  重写 `test_harness_self_check.py` 的扫描器正反例并升级探针对照，
  重写交付门的页面测试（真启动 + 真代理 + 真前端契约 + 真渲染）。
  套件：**67 项**（原 44 项）。
- `server/tools/review_browser_checks/`：新增 `review_api_launch.py`（调用 H 官方工厂）、
  `ops_review_api.json`（契约绑定映射）、`web_origin_probe.mjs`（按前端自己的契约请求）、
  `web_ui_smoke.mjs`（构建并在 jsdom 中执行真实前端）；扩展 `probe_live_api.py`、
  `scan_review_web.py`（分类感知，消除误报）、`acceptance_runner.py`（新增页面运行时阶段、
  原始 161 项与导出器检查）、故障注入替身新增 `/health`；更新 `README.md`、`evidence/`。
- `server/docs/review_browser/ACCEPTANCE.md`：本文件。

**未修改**：H/I 的任何文件（契约、`server/apps/review_api`、`server/src/mxsj_catalog`、
`server/apps/review_web` 均逐字未动）；`batch_001/` 与 `manifest.json`（所有动态检查都在
`write_temp_batch()` 生成的临时副本上进行）；`batch_001_profiles.json`、`export_review_csv.py`、
客户端、FLS/历史密钥库、`server/game_data/`。

边界校验（本轮结束时）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check   # exit 0
git status --porcelain -- server/docs/csv_checks server/tools/export_review_csv.py \
                        server/tools/review_csv_export.py server/game_data        # 无输出
```

---

## 10. 复现步骤（本轮全部结论）

```bash
# ---- 原有基线（未改动）----
cd /home/user/MXSJ_TW_2022
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q   # Ran 161 tests OK
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check              # exit 0

# ---- 第一阶段：独立数据基线 ----
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/verify_data_baseline.py  # 30/30 pass

# ---- 集成环境（合并 H/I，不改产品源码）----
git clone --shared /home/user/MXSJ_TW_2022 /tmp/integ && cd /tmp/integ
git checkout -b integration && git fetch origin pr-22 pr-24
git merge origin/pr-22 origin/pr-24          # 9f6ab439 / 97d317e3

# ---- 第二阶段：API 与数据语义（真实进程 + 真实 HTTP）----
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/probe_live_api.py \
    --start --map server/tools/review_browser_checks/ops_review_api.json \
    --out server/tools/review_browser_checks/evidence/live_api_report.json     # 18 pass / 2 fail

# ---- 第三阶段：静态 + 运行时（真启动页面、真代理、真前端契约、真渲染）----
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/scan_review_web.py        # 8/8 pass
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/review_browser_checks/acceptance_runner.py \
    --api-sha 9f6ab439 --web-sha 97d317e3                                     # 账本 + 页面运行时会话

# ---- 新增验收套件（不计入原有 161 项）----
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_browser_acceptance
# => Ran 67 tests，15 failures（12 加载层接口 + 3 交付门），0 skipped
```

---

## 11. 结论

1. **第一阶段（固定数据验收基线）已完成并通过**，本轮在集成环境下复算仍 30/30 一致。
2. **实际集成验收已经真正执行**（不再是"未交付"）：H 的 `9f6ab439` 与 I 的 `97d317e3`
   被合并进集成克隆，用真实进程、真实 HTTP、真实 dev server、真实构建产物逐项验证。
3. **未通过，`integration_acceptance_complete = false`：**
   - 页面：**白屏（P0）** + 6 类数据端点 404（P0）；
   - API/加载层：证据文件缺失、被篡改、被截短、数据集被删除后仍报 `ready`（P1）；
     非法/拼错参数被静默忽略（P2）；CSV 引号内换行被破坏（P2）；`source_entry` 可变（P3）。
4. **未执行项只剩 1 项**（真实浏览器渲染/截图：沙箱无浏览器且无法下载），已按环境限制写明原因；
   其余 34 项检查全部真实执行，**没有任何未执行项被写成通过**。
5. 验收工具本身可信：故障注入替身的负向/正向对照、扫描器正反例、交付门与套件自检在本轮
   全部为绿（7/7），且页面测试现在真的会启动服务、真的经过代理、真的检查前端结构；
   `API-05` 还会先用完好副本做对照，避免"请求写错"被误判为"产品正确拒绝"。
