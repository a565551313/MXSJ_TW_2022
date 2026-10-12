# 只读数据复核网页 — 前端交接（Agent I）

- 日期：2026-10-12（UTC）
- 工作分支：`arena/5ac000bd-mxsj-tw-2022`（PR #24，未合并）
- 前端目录：[`server/apps/review_web/`](../../apps/review_web/)
- 已接入的后端：Agent H 的 `server/apps/review_api`，**PR #22 head `9f6ab439a2ecdee37b59b99ddf95e77691490a0f`**
- 后端契约：[`API_CONTRACT.md`](./API_CONTRACT.md)（v1.0.0，随 PR #22 合入；已按它改写前端，不再使用自拟契约）

> **结论先说：前端已完成与 H 真实接口的适配，并用 H 的真实响应（152 份在线捕获）验证过。**
> 上一版文档写的「H 后端不存在 / 待接口联调」已不成立，本轮已按真实端点改写并在文档中给出可复现命令。
> 尚未完成的只有浏览器自动化（本沙箱无法下载 Chromium，见 §6.3），其余项目均已执行并记录结果。

---

## 1. 真实接口适配（本轮核心工作）

上一版前端请求 `/api/v1/review/items?page=1&page_size=25` 这类**自拟**路径，而 H 实际提供的是
`/api/v1/review/datasets/{dataset_id}/records?offset=0&limit=25`，`/pets`、`/skills`、`/anomalies`
之类的端点并不存在 —— 首页因此抛出
`Cannot read properties of undefined (reading 'length')` 并白屏。本轮按 H 的真实契约重做了适配层：

| 前端需求 | 现在用的真实端点 | 说明 |
|---|---|---|
| 批次概览 | `GET /batch`、`GET /health`、`GET /datasets` | `batch` / `tables_summary` / `validation_summary`，不再假设 `batch_id`/`tables`/`counters` |
| 分页与搜索 | `GET /datasets/{id}/records?offset&limit&q&sort_by&order&<列>=<值>` | `page/page_size` → `offset/limit`（`pageToOffset`/`offsetToPage`，`limit` 上限 500） |
| 道具 | `items` 数据集 + `/datasets/items/records/{client_shape_id}` | 详情按 `_pk`（此处即 `client_shape_id`）取单条 |
| 宠物主表 | `pets` 数据集 | 资质状态列由三个接口汇总（见下） |
| 宠物资质状态 | `/quarantine?entry_index=2954`、`pet_aptitudes`、`/missing-aptitudes` | 先隔离、再存在、再缺失、否则未知；**不补零** |
| 宠物详情 | `pet_skill_candidates`（按 `sequence` 排序）、`pet_required_skills`、`pet_skill_name_matches` | 关联查询**取全部页**，不只第一页 |
| 技能 | `pet_skills` 数据集 + `/overwrites?key=` + `pet_skill_name_matches?skill_id=` | 覆盖证据的旧/新名称由**原始字节**严格 CP950 解码 |
| 地图/场景 | `mapdata_scene_dictionary`、`mapdata_parent_scene`、`sceneid2name_minimap_scenes`、`npcname2realnamedata_alias_to_realname`、`minimapnpcpos_wenzi_entries` | 每个数据集独立查询自己的 records 端点，各自保留列定义与来源条目，不合表 |
| NPC | `npcposdata_records`（2601）与 `minimapnpcpos_pos_records`（2804）分别查询 | 两个来源永不合并；零 ID 计数来自后端自己的 `npcid=0` 过滤 total |
| 来源对照 | `npc_2601_vs_2804_agreement` | 分类计数遍历**全表**（677 行，两页：500 + 177）后统计 |
| 异常与证据 | `/quarantine`、`/missing-aptitudes`、`/ambiguous-skills`、`/overwrites` | 四个来源分开呈现，互不替代；覆盖名称就地解码，不再逐行拉技能详情 |

### 1.1 运行时的结构校验（不靠 `as` 断言）

- `src/api/schema.ts`：`Validator` 逐字段记录问题（JSON 路径 + 期望 + 实际），`ResponseSchemaError` 汇总抛出。
- `src/api/parsers.ts`：每个端点的结构校验（列表信封的 `dataset/total/offset/limit/count/records`、
  每条记录的 `_pk`、`count === records.length`、`batch` 的必需字段、`/missing-aptitudes` 的裸数组等）。
- `src/api/client.ts`：`fetch` → HTTP 错误 → 非 JSON → 结构校验，四种失败分别对应
  `ApiError.kind = network | http | invalid_json | schema`；**没有**任何“失败就用默认值/夹具”的分支。
- **JSON 合法但结构不对**（例如 200 + `{batch_id, tables, counters}`）→ `kind='schema'`，
  错误面板显示「这是接口结构错误」并列出不匹配的 JSON 路径；页面级 `ErrorBoundary` 保证不会白屏。
- 缺失字段**不会**被补成 `[]` / `0`：字段没有就是 `null`，由 UI 显示「（API 未提供）」。

### 1.2 关联查询取全量

`fetchAllRecords()` 逐页拉取（`limit=500`，直到 `records.length >= total`），用于：
宠物候选技能、必带技能、宠物详情里的名称匹配、覆盖证据、对照表全表统计。
超过安全上限（10,000 行）时抛 `RESULT_SET_TOO_LARGE`，**不返回被截断的列表**。

### 1.3 空 / 缺失 / 隔离 / 请求失败 的区分

| 情形 | 页面表现 |
|---|---|
| 真的没有记录（后端 200 + `total=0`） | 该区块显示空态文案，并说明这是接口返回 0 条 |
| 资质在源表中缺失（`pet_aptitude_missing`） | 「资质缺失」标签 + 原因（如 `no_record_in_2954`）+「本页不会把它显示为 0」 |
| 整行被隔离（`/quarantine`） | 「资质隔离」+ 隔离原因 + 原始字节；**不显示**未批准的候选值 |
| 请求失败（断网 / 4xx / 非 JSON / 结构错） | 错误面板（含请求 URL、类型、HTTP 码、错误码、响应片段），**不回退**夹具数据 |

## 2. 运行方式

```bash
cd server/apps/review_web
npm ci                       # 安装依赖（首次）
npm run dev                  # 默认：只连真实 API（Vite 绑定 0.0.0.0:5173）
```

浏览器只请求同源相对路径 `/api/...`，由沙箱内的 Vite 开发服务器代理到 Python 复核后端
（默认 `http://127.0.0.1:8000`，用 `VITE_API_PROXY_TARGET` 覆盖）。用户浏览器**从不**访问沙箱地址。

启动 H 的后端（在自己的工作树里，非本分支文件）：

```bash
# 以已有 checkout 为例（本沙箱用的是 PR #22 head 9f6ab439）
uvicorn app.main:app --app-dir server/apps/review_api --host 0.0.0.0 --port 8000
```

| 命令 | 作用 |
|---|---|
| `npm run dev` | 开发服务器（0.0.0.0:5173，`/api` 代理到 Python 后端） |
| `npm test` | Vitest + Testing Library（103 项通过 + 9 项在线联调默认跳过） |
| `REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts` | **在线联调**：对真实后端发真实 HTTP（12 项） |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run build` / `npm run preview` | 生产构建 / 预览构建产物（同样代理 `/api`） |
| `npm run fixture:capture` | 重新捕获 H 的真实响应到 `fixtures/h_api/` |
| `npm run fixture:check` | 重放每一条捕获并与在线后端逐字节比对 |
| `npm run fixture:api` | **显式**启动捕获回放服务（仅回环 `127.0.0.1:8788`） |
| `npm run dev:fixture` | **显式**回放模式（页面显示红色“非真实数据”横幅） |

### 2.1 回放模式（非默认，也不是联调证据）

`fixtures/h_api/` 存放 152 份**从 H 运行中的服务捕获的真实响应**（`fixtures/capture_h_api.py`，
manifest 记录 method/path/query/status/sha256/字节数，`_capture.provenance` 写明后端提交号）。
`fixtures/h_api/replay.mjs` 同时被两处使用：测试的 fetch stub（`src/test/hApiReplay.ts`）与
`npm run dev:fixture` 的回放服务。回放规则：

- 只回答**同路径 + 同非分页参数**的已捕获请求，记录逐字节来自捕获；
- `offset/limit` 可在捕获窗口内自由移动（`total` 仍是后端返回的真实总数）；
- 请求超出捕获窗口、或出现未捕获的过滤组合 → 明确返回
  `FIXTURE_CAPTURE_MISSING` 错误，**不用其它页、空列表或编造数据顶替**；
- 生产代码不引用 `fixtures/` 或 `src/test/`（架构测试强制），默认模式也永远不会回退到它。

旧的 `batch001.sample.json` / `contractHandler.mjs` / `build_fixture_sample.py` 已随本轮删除：
它们编码的是**自拟契约**，与新前端不再对应，留着只会误导。

## 3. 功能与数据源

| 能力 | 状态 | 数据来源 |
|---|---|---|
| 批次概览（批次、各表数量、校验状态、隔离/缺失/歧义） | 已实现 | `/batch`、`/datasets`、`/health` |
| 道具搜索（ID/名称）、分页、详情 | 已实现 | `items` 数据集（`offset/limit/q`） |
| 图片资源预览 | **有意不做** | 无图片资源 API；页面明确不提供预览、不伪造缩略图，只显示 `image_id` 与显式映射标记 |
| 宠物主表 + 资质状态列 | 已实现 | `pets` + `/quarantine?entry_index=2954` + `pet_aptitudes` + `/missing-aptitudes`（3 次批量请求，非每行 3 次） |
| 宠物详情：资质 / 候选技能 / 必带技能 / 名称匹配 | 已实现 | 4 个关联数据集，全部**取全页** |
| 技能描述 / 资源公式 / 覆盖证据 / 名称匹配 | 已实现 | `pet_skills`、`/overwrites`、`pet_skill_name_matches` |
| 地图与场景数据集（按来源分开） | 已实现 | 5 个地图数据集，各自独立查询 |
| NPC 记录（2601 / 2804 分开）+ 来源对照 | 已实现 | 两个来源数据集 + `npc_2601_vs_2804_agreement` |
| 异常与证据（4 条隔离、3 条缺失、2 组歧义、9 次覆盖） | 已实现 | `/quarantine`、`/missing-aptitudes`、`/ambiguous-skills`、`/overwrites` |
| 本批不变量自检 | 已实现 | 规范写在 `src/lib/invariants.ts`，判定与实际值全部来自接口 |
| 编辑 / 删除 / 导入 / 发布 | **未实现（按要求禁止）** | 代码只有 `GET`；测试断言页面不存在此类按钮 |
| 与 Python 复核后端的真实联调 | **已接入并验证** | §1 的端点表；证据见 §6.2 |

## 4. 必须保留的语义在前端如何落地

| 要求 | 前端行为 | 覆盖测试 |
|---|---|---|
| 道具 72548 继续隔离 | `/datasets/items/records` 不含该行；异常页卡片显示隔离原因与**逐字节十六进制**原值（`c2 f9 a4 48 …`），不裁剪、不猜名 | `AnomaliesPage.test.tsx`、`invariants.test.ts` |
| 资质 2800 继续隔离、不显示未批准的 1700 | 资质区显示「资质记录处于隔离状态」+ 原因 `value_exceeds_named_maximum:法力資質`；**不渲染数值网格**，界面不出现 `1700` | `PetsPage.test.tsx`（`not.toContain('1700')`、无 `aptitude-table`） |
| 3010 / 4021 / 4022 资质缺失、不显示为 0 | 列表打「资质缺失」；详情显示 `no_record_in_2954` 与「本页不会把它显示为 0」；异常页列出三条并给出原因 | `PetsPage.test.tsx`、`AnomaliesPage.test.tsx`、`reviewApi.test.ts` |
| 高級命中保留 229/255；終級命中保留 329/355 | 同名技能的**全部候选 ID** 都渲染为可点击 chip，`match_count`/`ambiguous` 同屏；无默认选中 | `AnomaliesPage.test.tsx`、`PetsPage.test.tsx`、`reviewApi.test.ts`、`invariants.test.ts` |
| NPC ID 0 不隐藏、复合身份与重复不折叠 | 每行渲染 `scene_id / [场景名] / #record_index（_pk=…）`，`npcid=0` 加「ID 0」标记；同页 `(scene_id, npcid)` 重复只加「重复 ×N」，不合并、不去重 | `MapsNpcsPage.test.tsx`（场景 1005 的两条 0 记录） |
| 两个来源不合并 | 2601 段显示 `1335 / npcid=0: 632`，2804 段显示 `1344 / npcid=0: 631`，各自查询自己的端点 | `MapsNpcsPage.test.tsx`、`reviewApi.test.ts`、在线联调 |
| 数据仍是复核候选 | 全站常驻「复核候选，非正式规则」横幅；`native_loader_confirmed=false` 原样显示；全站无「原生已确认」字样 | `App.test.tsx`、`OverviewPage.test.tsx` |

## 5. 安全与预览环境

- **安全文本渲染**：`SafeText`/`SafeFormula` 只把源文本作为 React 文本子节点输出（React 转义）；
  源码中没有 `dangerouslySetInnerHTML`、`innerHTML=`、`eval`、`new Function`、`document.write`
  （`src/test/architectureGuards.test.ts` 强制，逐文件扫描）。
- **不执行公式/标记**：`fpneed_raw`/`mpneed_raw`/`hpneed_raw` 与描述原样展示，`#r` 等标记保留，不计算、不解释、不做简繁转换。
- **相对路径**：浏览器只发 `/api/v1/review/...`；架构测试禁止源码出现 `http(s)://localhost|127.0.0.1|0.0.0.0`。
- **Vite 代理 + 预览域**：开发服务器绑定 `0.0.0.0`、`allowedHosts: true`、`/api` 转发到后端；
  用 Arena 形式 `Host` 头请求 `/` 与 `/api/v1/review/health` 均返回 200（§6.2）。
- **状态覆盖**：加载中、空结果、请求失败（网络 / 4xx / 非 JSON / 结构不符）、分页、跳页、
  窄屏（≤760px 表格变带 `data-label` 的堆叠卡片）。
- **无写操作**：代码仅 GET；页面无编辑/删除/导入/发布入口（测试逐页断言按钮文本与无 file/textarea 控件）。

## 6. 执行结果

### 6.1 前端自身

```bash
cd server/apps/review_web
npm test          # 15 个文件：103 passed | 9 skipped（在线联调默认跳过）
npm run typecheck # 无输出
npm run build     # dist/index.html 0.64 kB，css 10.54 kB (gzip 2.83)，js 316.35 kB (gzip 95.92)
python3 fixtures/capture_h_api.py --base http://127.0.0.1:8000 --check
                  # OK: all 152 captures match the live backend
```

### 6.2 真实联调（本轮实际执行，证据可直接复现）

| 项目 | 命令 / 方式 | 结果 |
|---|---|---|
| 与 H 后端的真实 HTTP 联调 | `REVIEW_API_BASE=http://127.0.0.1:8000 npx vitest run src/api/liveBackend.test.ts` | **12 项全部通过**（批次计数、items 分页/搜索/详情、三种资质状态、宠物详情组合、覆盖字节解码、异常板、两来源零 ID 计数、对照全表统计、404/400/405 错误信封） |
| 200 + 结构错误（真实 HTTP） | 同上文件内的本地 stub HTTP 服务 | 通过：`kind='schema'`，问题路径含 `response.batch`/`response.tables_summary`/`response.validation_summary`；缺 `records` 的列表**不会**变成空列表 |
| 200 + 非 JSON | 同上 | 通过：`kind='invalid_json'`（HTTP 200 不算成功） |
| 捕获逐字节比对 | `python3 fixtures/capture_h_api.py --check` | `OK: all 152 captures match the live backend`（后端为 PR #22 head `9f6ab439…`） |
| 代理探针：`GET /` | `curl http://127.0.0.1:5173/` | 200 `text/html` |
| 代理探针：`GET /api/v1/review/batch` | 经 Vite 代理 | 200，`batch_001`，`1945 = {6852, 6851, 1}`，隔离 4 |
| 代理探针：`items?offset=0&limit=25` | 经 Vite 代理 | 200，`total=6851`，`count=25`，首行 `NPC呼叫器` / `鹿茸` |
| 代理探针：`items?q=鹿茸` | 经 Vite 代理 | 200，`total=2`，`[12, 21302]` |
| 代理探针：旧式 `?page=1&page_size=25` | 经 Vite 代理 | 404 `NOT_FOUND`（证明前端已不再请求该方言） |
| 代理探针：`items/records/999999` | 经 Vite 代理 | 404 `RECORD_NOT_FOUND`（真实错误信封） |
| 预览域可用性 | `curl -H "Host: <arena-preview-host>" http://127.0.0.1:5173/` 与 `/api/v1/review/health` | 200 / `{"status":"ready",…}` |
| 后端不可用时的行为（组件层） | `installNetworkFailure()` 用例 | 错误面板「无法连接复核 API」，表格不渲染，**不回退夹具** |
| 后端不可用时的行为（真实 HTTP） | 另起一个把 `/api` 代理指向死地址的 Vite（`VITE_API_PROXY_TARGET=http://127.0.0.1:9`，端口 5199） | `/api/v1/review/health` → **HTTP 500**（非 JSON），`/` 仍返回 200：应用外壳不受影响，只有数据区显示错误 |

### 6.3 明确「未执行」的项目

- **真实浏览器（Chromium/Playwright）端到端点击与截图：未执行**。本沙箱没有浏览器，且
  `cdn.playwright.dev` / `playwright.azureedge.net` / `storage.googleapis.com` 等下载域名不可达，
  无法安装。替代证据：jsdom 组件测试（103 项）、真实 HTTP 联调（12 项）、经 Vite 代理的 curl 探针，
  以及可直接交互的实时预览（Vite 已绑定 `0.0.0.0:5173`，预览域 `Host` 已验证 200）。
  **HTTP 200 本身不算通过**，因此上面的 12 项在线检查断言到字段级。
- **窄屏视觉回归截图：未执行**（仅 `data-label` 结构断言）。
- **屏幕阅读器 / 无障碍审计：未执行**。
- **原生加载器对照：未执行**（超出本页职责范围）。

## 7. 与其它目录的边界

- 只改动 `server/apps/review_web/` 与本文档；未改 H 的后端、J 的测试、batch-1 CSV/manifest、
  参数配置、导出器、客户端文件、`data/script.fls`、历史密钥库、`server/game_data/`。
- 未做简繁转换；所有繁体字段名与数值原样来自接口。
- 未启动 `mock_server.py`，未运行任何可能改动客户端的浏览工具。
- 生产构建产物不含夹具/捕获内容（架构测试 + `dist` 检查）。

## 8. 文件说明（供复核者核查）

| 文件 | 作用 |
|---|---|
| `src/api/contract.ts` | 唯一记录路径/数据集 id/分页参数的模块（`/datasets/{id}/records`、`offset/limit`、`_pk`） |
| `src/api/schema.ts` | 运行时结构校验与 `ResponseSchemaError`（JSON 路径级报错） |
| `src/api/parsers.ts` | 各端点响应的结构校验器 |
| `src/api/client.ts` | GET + JSON + 校验；`ApiError.kind = network/http/invalid_json/schema` |
| `src/api/reviewApi.ts` | 领域组合层：资质状态、宠物详情、技能详情、异常板、地图/NPC/对照、取全量分页 |
| `src/components/ErrorBoundary.tsx` | 页面级错误边界（渲染异常不白屏，打印消息/组件栈/结构问题路径） |
| `src/test/hApiReplay.ts` | 测试用 fetch stub：回放 H 的真实捕获（可注入结构变更以验证报错） |
| `fixtures/h_api/` | 152 份真实捕获 + `manifest.json`（含 sha256 与后端提交号） |
| `fixtures/capture_h_api.py` | 捕获脚本；`--check` 逐字节复核（可对任意在线后端重跑） |
| `fixtures/h_api/replay.mjs` | 捕获回放实现（测试与 `dev:fixture` 共用；未捕获即报错） |
| `fixtures/serve-fixture-api.mjs` | 显式启动的回放 HTTP 服务（仅回环） |
| `src/api/liveBackend.test.ts` | 在线联调测试（默认跳过；`REVIEW_API_BASE=…` 时执行真实 HTTP） |

## 9. 待办（未完成，明确记录）

1. **浏览器级端到端点击/截图**：本沙箱无法安装浏览器（§6.3）；需要有人在实际环境里跑一次
   Playwright/Cypress 走查，或直接使用本次启动的实时预览点击确认。
2. **宠物列表的资质状态来源**：目前每次列表请求固定拉 3 个批量端点（其中 `pet_aptitudes` 是全表 131 行）。
   数据量增长后建议 H 提供一个“按 id 集合查询”的批量端点；当前行为已在文档与测试中固定。
3. **场景筛选下拉**：页面用文本框输入 `scene_id`，没有“场景清单”端点可用于下拉枚举；
   如需下拉，需要一个场景列表接口（现在没有，也不在前端硬编码）。
4. **`dev:fixture` 的覆盖范围**：回放只覆盖已捕获的请求组合；未捕获的组合会显示
   `FIXTURE_CAPTURE_MISSING` 错误（这是有意为之，避免把回放当成数据源）。扩展方法是补捕获后重跑
   `fixtures/capture_h_api.py`。
5. **窄屏视觉回归与无障碍审计**：未执行（§6.3）。
6. **`/batch` 的 `input_hashes`、`limitations`**：H 的 `/batch` 当前不返回这两个字段（旧前端曾假设存在）。
   前端只在接口返回时显示，否则显示「（API 未提供）」；若 H 后续补充，页面无需改动。
