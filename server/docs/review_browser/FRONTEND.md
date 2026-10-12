# 只读数据复核网页 — 前端交接（Agent I）

- 日期：2026-10-12（UTC）
- 工作分支：`arena/5ac000bd-mxsj-tw-2022`
- 前端目录：[`server/apps/review_web/`](../../apps/review_web/)
- 本轮基线提交：`5f2369066c638297cce51f73adb961e011652c52`（协调分支 `arena/b53b33e6-mxsj-tw-2022` 当时的最新提交；比任务给出的 `31f6083` 多 3 个 `map/*.map` 文件，无其它差异）

> **结论先说：这是一个可运行、可测试、只读的前端，但真实接口联调尚未进行。**
> 截至本基线，仓库里**没有** `server/docs/review_browser/API_CONTRACT.md`，也**没有**任何
> `/api/v1/review/` 的 Python 实现，因此本轮**没有可记录的后端联调提交号**。
> 真实数据接入状态记为 **待接口联调**，不写“已接入”。

---

## 1. 运行方式

```bash
cd server/apps/review_web
npm ci                       # 安装依赖（首次）
npm run dev                  # 默认模式：只连真实 API（Vite 绑定 0.0.0.0:5173）
```

默认模式下浏览器只请求同源相对路径 `/api/...`，由 Vite 开发服务器（运行在沙箱内）代理到
Python 复核后端，默认目标 `http://127.0.0.1:8000`，可用 `VITE_API_PROXY_TARGET` 覆盖：

```bash
VITE_API_PROXY_TARGET=http://127.0.0.1:9000 npm run dev
```

其它命令：

| 命令 | 作用 |
|---|---|
| `npm test` | 运行全部前端测试（Vitest + Testing Library，79 项） |
| `npm run typecheck` | `tsc --noEmit` |
| `npm run build` | 生产构建到 `dist/` |
| `npm run preview` | 预览构建产物（同样把 `/api` 代理到后端） |
| `npm run fixtures:rebuild` | 从 batch_001 重新生成夹具样本，`--check` 可校验字节一致 |
| `npm run fixture:api` | **显式**启动夹具 API（`127.0.0.1:8788`，只监听回环） |
| `npm run dev:fixture` | **显式**夹具演示模式（需先启动 `fixture:api`） |

### 夹具演示模式（非默认）

`npm run dev:fixture` 会把代理指向 `fixtures/serve-fixture-api.mjs`，页面顶部出现**红色常驻横幅**
标记“FIXTURE 演示模式：非真实 API 数据”。夹具只包含 batch_001 的一小部分**真实行样本**
（`fixtures/batch001.sample.json`，由 `fixtures/build_fixture_sample.py` 从冻结 CSV 复制，
不生成任何新值）。

边界说明：

- 默认模式**不会**加载夹具；API 失败时只显示错误，不自动切换成夹具数据；
- 夹具服务只监听 `127.0.0.1`，用户浏览器不会直接访问它；
- 夹具模式**不是**联调结果，不能作为数据接入证据。

## 2. 接口契约状态：待接口联调

接口前缀按任务要求固定为 `/api/v1/review/`。**Agent H 负责的 `API_CONTRACT.md` 尚未出现**，
因此前端目前只能声明“我们请求什么”，不能声明“后端已经这样实现”。

所有路径与查询参数集中在**唯一一处**：[`src/api/contract.ts`](../../apps/review_web/src/api/contract.ts)。
契约落地后，只需要改这一个文件里的路径/参数，页面代码不用动。

### 2.1 前端期望的读取接口（需求，不是已确认契约）

| 方法 | 路径 | 查询/路径参数 | 期望响应 |
|---|---|---|---|
| GET | `/api/v1/review/batch` | — | 批次概览对象（见 2.2） |
| GET | `/api/v1/review/items` | `q`, `page`, `page_size` | 分页对象，`items` 为道具行 |
| GET | `/api/v1/review/items/{client_shape_id}` | — | `{ item }` |
| GET | `/api/v1/review/pets` | `q`, `page`, `page_size` | 分页对象，行内含 `aptitude_status` |
| GET | `/api/v1/review/pets/{client_shape_id}` | — | `{ pet, aptitude, aptitude_status, required_skills, candidate_skills }` |
| GET | `/api/v1/review/skills` | `q`, `page`, `page_size` | 分页对象，`items` 为技能行 |
| GET | `/api/v1/review/skills/{skill_id}` | — | `{ skill, overwrite, name_matches }` |
| GET | `/api/v1/review/maps/datasets` | — | `{ datasets: [...] }`（每个 CSV 一份元数据） |
| GET | `/api/v1/review/maps/datasets/{dataset_key}` | `q`, `scene_id`, `page`, `page_size` | 分页对象 + `dataset` |
| GET | `/api/v1/review/npcs` | `source`（必填）, `q`, `scene_id`, `page`, `page_size` | 分页对象 + `source_info` |
| GET | `/api/v1/review/npcs/agreement` | `scene_id`, `page`, `page_size` | 分页对象 + `agreement_counts` |
| GET | `/api/v1/review/anomalies` | — | 隔离/缺失/歧义/覆盖证据 |

约定：

- 分页信封：`{ "items": [...], "total": <int>, "page": <int>, "page_size": <int> }`；
- 错误信封：`{ "error": { "code": "...", "message": "..." } }`，并使用非 2xx 状态码；
- DTO 字段名**沿用 manifest 的列名**（`client_shape_id`、`description_raw`、`category_code_raw`、
  `image_mapping_explicit`、`fpneed_raw`、`scene_id`、`record_index`、`npcid` …），不引入第二套命名；
- 文本字段一律按字符串返回；缺值用 `null`/缺字段表示，**不要**用 `0` 或空串替代；
- 全部为只读 `GET`，前端不会发出任何写请求。

### 2.2 `/batch` 期望字段

```jsonc
{
  "batch_id": "batch_001",
  "status": "review_candidate_not_native_verified",
  "native_verified": false,
  "tables": [ { "table_key": "1945", "csv_file": "items.csv", "source_entry": 1945,
                "source_table": "...", "source_records": 6852, "review_csv_records": 6851,
                "quarantined_records": 1, "missing_records": null } ],
  "checks": { "csv_round_trip": "pass" },
  "counters": { "quarantined_record_count": 4, "skill_unique_count": 581 },
  "ambiguous_pet_skill_names": { "高級命中": [229, 255] },
  "limitations": ["..."],
  "input_hashes": { "data/script.fls": "..." }
}
```

`counters` 里出现未知键时，前端**直接显示键名**并注明“接口新增计数”，不会猜标签、也不会补数字。
接口没返回的计数就不显示。

### 2.3 前端容忍的两处形状差异

1. `ambiguous_skill_names` 可以是「一个候选 ID 一行」（batch_001 的 `pet_skill_name_matches.csv` 形状），
   也可以是「一行里用逗号给出多个 ID」——两种情况都会把同一名称的**全部候选 ID**渲染出来；
2. 地图/NPC 行的值可以是字符串或数字；`null`/缺字段显示为「（源字段为空）」，不会变成 `0`。

## 3. 已接入 / 未接入功能清单

| 能力 | 状态 | 说明 |
|---|---|---|
| 批次概览（批次、各表数量、校验状态、隔离/缺失） | 已实现（数据源=API） | 计数全部来自 `/batch`，页面无硬编码数字 |
| 道具搜索（ID/名称）、分页、详情 | 已实现（数据源=API） | 原始描述、类别代码、图片映射 ID 与是否显式映射 |
| 图片资源预览 | **未实现（有意不做）** | 本轮没有图片资源 API；页面明确写“不提供图片预览，也不探测资源是否存在”，不会伪造缩略图 |
| 宠物主表 / 资质 / 候选技能 / 必带技能 | 已实现（数据源=API） | 缺失与隔离分别标注；候选技能保留源顺序与重复 |
| 技能描述 / 资源公式 / 重复覆盖摘要 | 已实现（数据源=API） | 公式只展示不计算 |
| 地图与场景数据集（按来源分开） | 已实现（数据源=API） | 数据集清单来自接口，列定义来自 manifest 元数据 |
| NPC 记录（2601 / 2804 分开）+ 来源对照 | 已实现（数据源=API） | 保留零 ID、复合主键与重复记录 |
| 异常与证据（4 条隔离、缺失资质、技能歧义、9 次覆盖） | 已实现（数据源=API） | 隔离证据按带类型 JSON 渲染，字节以十六进制显示 |
| 本批不变量自检 | 已实现（判定=API） | 规范列表写在前端，判定与实际值全部来自接口 |
| 与 Python 复核后端的真实联调 | **未接入（待接口联调）** | 仓库内既无契约文档也无后端实现；无联调提交号可记录 |
| 编辑 / 删除 / 导入 / 发布 | **未实现（按要求禁止）** | 代码只有 `GET`；测试断言页面不存在此类按钮 |

## 4. 必须保留的语义在前端如何落地

| 要求 | 前端行为 | 覆盖测试 |
|---|---|---|
| 道具 72548 继续隔离 | 道具表不会出现该行（它不在 `/items` 结果里）；异常页以卡片展示隔离原因与**十六进制原字节**，不裁剪末字节、不猜名 | `AnomaliesPage.test.tsx`（`c2 f9 a4 48 …` 逐字节断言 + 无 `\uFFFD` + 无“時空石”） |
| 资质 2800 继续隔离、不显示未批准的 1700 | 宠物 2800 详情显示“资质记录处于隔离状态”，**不渲染资质数值网格**；界面文本不出现该未批准候选值 | `PetsPage.test.tsx`（`not.toContain('1700')`、无 `aptitude-table`） |
| 3010 / 4021 / 4022 资质缺失、不显示为 0 | 列表打「资质缺失」标签，详情显示缺失原因与“本页不会把它显示为 0” | `PetsPage.test.tsx`、`AnomaliesPage.test.tsx` |
| 高級命中保留 229/255；終級命中保留 329/355 | 两个 ID 都以可点击 chip 渲染，`match_count` 与 `ambiguous` 同屏显示，无默认选中 | `PetsPage.test.tsx`（`['/skills/229','/skills/255']`）、`AnomaliesPage.test.tsx` |
| NPC ID 为 0 不隐藏 | 每行照常渲染 `npcid`，并加「ID 0」标记；来源信息显示零 ID 记录数 | `MapsNpcsPage.test.tsx` |
| 同名/同 ID 多条记录不折叠 | NPC 表按复合记录身份渲染每一行；同页内 `(scene_id, npcid)` 重复只加「重复 ×N」提示 | `MapsNpcsPage.test.tsx` |
| 数据仍是复核候选 | 全站常驻「复核候选，非正式规则」横幅；每行显示 `review_status`；`native_verified=false` 显示为状态而非“已确认” | `App.test.tsx`、`OverviewPage.test.tsx` |

## 5. 安全与预览环境

- **安全文本渲染**：所有源文本经 `SafeText`/`SafeFormula` 作为 React 文本子节点输出，React 负责转义；
  全仓库前端源码**没有** `dangerouslySetInnerHTML`、`innerHTML` 赋值、`eval`、`new Function`、`document.write`
  （由 `src/test/architectureGuards.test.ts` 强制）。
- **不执行公式/标记**：`fpneed_raw`/`mpneed_raw`/`hpneed_raw` 与描述都按原文展示，`#r` 等标记原样保留，不做简繁转换。
- **相对路径**：浏览器只请求 `/api/v1/review/...`；不会向沙箱 `localhost`/`127.0.0.1` 发请求
  （架构测试禁止源码中出现此类绝对地址）。
- **Vite 代理**：`/api` 由开发服务器转发到 Python 后端；后端地址只存在于服务器侧配置。
- **预览可用**：开发服务器绑定 `0.0.0.0`，`allowedHosts: true`，允许 Arena 预览域名访问；
  SPA 路由在 `dev` 与 `preview` 下都能回落到 `index.html`。
- **状态覆盖**：加载中、空结果、失败（含网络失败、非 JSON 代理错误、404 契约不匹配）、分页、
  窄屏（≤760px 表格改为带 `data-label` 的堆叠卡片）。
- 页面明确没有编辑、删除、导入、发布入口。

## 6. 测试与执行结果

```bash
cd server/apps/review_web
npm test          # 79 passed (12 files)
npm run typecheck # 无错误
npm run build     # 构建成功
```

本轮实际执行结果（2026-10-12，本沙箱）：

| 项目 | 结果 |
|---|---|
| `npx vitest run` | **12 个测试文件、79 项测试全部通过** |
| `npx tsc --noEmit` | 通过（无输出） |
| `npx vite build` | 成功（`dist/`，JS 约 288 kB / gzip 88 kB） |
| `python3 fixtures/build_fixture_sample.py --check` | 夹具与冻结 CSV 一致（逐字节） |
| 默认模式代理探针：`GET /api/v1/review/batch` | **HTTP 500**（后端不存在）→ 页面显示错误态，未回退夹具 |
| 夹具模式代理探针：`GET /api/v1/review/batch` | HTTP 200（`batch_id=batch_001`，4 张表元数据） |
| 预览域探针：带 Arena 形式 `Host` 请求 `/`、`/items/12` | HTTP 200（`allowedHosts` 与 SPA 回落均生效） |

### 覆盖的测试主题

- 搜索（名称/ID）、分页（下一页 + 总数）、详情显示：`ItemsPage.test.tsx`；
- 空结果、API 错误（网络失败 / 404 / 非 JSON）、加载状态、重试：`ItemsPage.test.tsx`、`OverviewPage.test.tsx`、`client.test.ts`；
- 同名技能歧义与资质缺失：`PetsPage.test.tsx`、`AnomaliesPage.test.tsx`、`invariants.test.ts`；
- 危险文本只展示不执行（`<img onerror>`、`<script>`、公式字符串、`#r` 标记）：`SafeText.test.tsx`；
- 真实 API 接入方式（相对路径、GET-only、失败不回退夹具、契约待联调）：`client.test.ts`、`architectureGuards.test.ts`。

### 明确“未执行”的测试

- **与 Agent H 后端的真实联调测试：未执行**（`API_CONTRACT.md` 与后端实现均不存在）。
- **夹具模式以外的端到端浏览器测试（Playwright 等）：未执行**，本轮没有引入浏览器自动化依赖。
- **窄屏视觉回归截图：未执行**；仅以 `data-label` 结构断言 + 手工窄屏查看代替。
- **屏幕阅读器/无障碍审计：未执行**。
- **原生加载器对照：未执行**（本任务不涉及，也无法在静态数据复核页完成）。

## 7. 与其它目录的边界

- 只新增 `server/apps/review_web/` 下的文件与本文档；未修改 Python 后端、CSV、导出器、参数配置、
  客户端、FLS、历史密钥库、`server/game_data/` 或其它 Agent 的目录。
- 未做简繁转换；所有繁体字段名与数值都原样来自冻结 CSV / 接口。
- 未启动 `mock_server.py`，未运行任何可能改动客户端的浏览工具。

## 8. 夹具文件说明（供复核者核查）

| 文件 | 作用 |
|---|---|
| `fixtures/batch001.sample.json` | 从 batch_001 复制的真实行样本（69 道具 / 8 宠物 / 4 资质 / 17 候选技能 / 19 名称匹配 / 28 技能 / 20+ NPC 行 / 2 个含 232 处零 ID 的来源 / 4 条隔离 / 9 次覆盖）。文件内 `_fixture` 段写明它不是数据源 |
| `fixtures/build_fixture_sample.py` | 生成脚本，只读 batch_001；`--check` 校验逐字节一致 |
| `fixtures/contractHandler.mjs` | 夹具模式与测试**共用**的请求处理实现，避免两份行为漂移 |
| `fixtures/serve-fixture-api.mjs` | 显式启动的夹具 HTTP 服务（仅回环） |

生产代码不引用 `fixtures/` 或 `src/test/`（由架构测试强制）；`vite build` 产物中不含夹具样本
（已用 `grep` 核查 `dist` 无夹具内容）。

## 9. 需要协调者/Agent H 确认的事

1. 若 H 的 `API_CONTRACT.md` 与第 2.1 节的路径或字段不同，请以 H 的契约为准，前端只需改
   `src/api/contract.ts`（路径/参数）与 `src/api/types.ts`（字段名）。
2. 需要确认 `aptitude_status.status` 的取值集合是否就是
   `present` / `missing_in_source_table` / `quarantined`（未知值会显示为“资质状态未知”，不猜）。
3. 需要确认隔离证据 `value_under_applied_profile` 是否保持
   `quarantine.jsonl` 的带类型 JSON（`{bytes_hex}` / `{dict}` / `{tuple}`）——前端就是按它渲染的。
4. 后端就绪后请告知提交号，我会补一次真实联调并把「待接口联调」改为已接入。
