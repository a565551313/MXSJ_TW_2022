# MXSJ 客户端数据复核后端与查询 API 说明文档 (BACKEND.md)

- **作者：** Agent H
- **分支：** `arena/e5907ab5-mxsj-tw-2022`
- **目标 PR 基线：** `arena/b53b33e6-mxsj-tw-2022`
- **版本：** 1.1.0 (2026-10-12)

---

## 1. 模块定位与职责边界

本模块为 **MXSJ 客户端复核数据专用只读加载层与查询 API**。
- **定位**：仅供数据复核网页（Agent I 开发）与自动化验收（Agent J）使用。
- **职责边界**：
  - 严格只读，不提供任何数据写入、修改、上传或发布接口。
  - 不实现游戏业务逻辑（不接入正式战斗、背包、账号等玩法系统）。
  - 不修改全仓通用依赖方案，API 专用依赖集中于 `server/apps/review_api/requirements.txt`。
  - 加载层 `mxsj_catalog` 完全基于 Python 3.11+ 标准库开发，独立于任何 HTTP 框架。

---

## 2. 目录结构与责任分配

```
server/
├── src/
│   └── mxsj_catalog/               # 只读数据加载核心层（纯标准库，无 HTTP 依赖）
│       ├── __init__.py             # 包导出接口与类型
│       ├── errors.py               # 强类型目录异常层次
│       ├── models.py               # 不可变 Schema、Dataset、Quarantine 与 Overwrite 数据结构
│       ├── loader.py               # manifest 完整性校验、SHA-256/大小核验、文本流保真与类型转换器
│       └── catalog.py              # ReviewCatalog 管理器、内存索引、不可变查询/过滤/排序
├── apps/
│   └── review_api/                 # FastAPI + Uvicorn 查询 API
│       ├── __init__.py
│       ├── config.py               # 路径配置与服务绑定（0.0.0.0:8000，支持 REVIEW_BATCH_DIR）
│       ├── schemas.py              # Pydantic 响应结构模型
│       ├── routes.py               # /api/v1/review 严格参数校验与路由实现
│       ├── app.py                  # FastAPI 应用工厂与统一异常处理
│       ├── main.py                 # CLI 启动入口（支持 --batch-dir 参数）
│       └── requirements.txt        # 独立依赖清单
├── tests/
│   ├── catalog/                    # 加载层单元测试
│   │   ├── test_loader_and_types.py
│   │   ├── test_catalog_immutability.py
│   │   ├── test_corruptions_and_errors.py
│   │   └── test_semantics.py
│   └── review_api/                 # API 集成测试
│       ├── test_api_endpoints.py
│       ├── test_filtering_and_pagination.py
│       └── test_error_handling.py
└── docs/
    └── review_browser/
        ├── API_CONTRACT.md         # 统一接口契约（前缀 /api/v1/review/）
        └── BACKEND.md              # 本说明文档
```

---

## 3. 只读加载层核心设计 (`mxsj_catalog`)

### 3.1 启动全量校验与一次性加载
- 启动时读取 `manifest.json`，强制检查必须包含第一批全部 **21 个声明文件**（17 个核心 CSV + 4 个证据文件）。
- 严格校验全部 21 个声明文件的存在性、字节长度以及 SHA-256 哈希值；若存在缺少文件、字节不符或哈希不符（包括篡改 `quarantine.jsonl`），直接抛出 `CatalogIntegrityError` 终止启动，绝不返回残缺的就绪目录。
- **目录隔离安全**：对 manifest 中声明的文件相对路径强制执行路径穿越防护校验，禁止引用批次根目录以外的任何文件。
- CSV 表头列名与顺序必须与 manifest `columns` 声明完全一致，否则抛出 `CatalogSchemaError`。
- 实际记录行数必须与 manifest `rows` 完全一致，否则抛出 `CatalogIntegrityError`。
- 一次性加载入内存，避免运行期每个 HTTP 请求重复解码或解析。

### 3.2 CSV 文本流保真与严格类型转换
- **文本流换行保真**：采用 `io.StringIO` 保留原始文本流交由 `csv.reader` 读取，支持带有嵌入 `\n`、`\r\n`、`\r`、引号、逗号及公式前缀（`=`、`@` 等）的单元格，严禁在读取前简单使用 `splitlines()` 切割导致换行丢失。
- `int`：严格整数转换 `int(val.strip())`，拒绝空串、浮点数或非数字字符。
- `int_or_empty`：遵循地图/NPC 旧有约定，空串映射为 Python `None`（JSON 中为 `null`），非空值严格转换为整数。
- `bool`：严格比对 `"true"` -> `True`、`"false"` -> `False`，绝不把字符串 `"false"` 误判为真值；其它输入抛出 `CatalogValueError`。
- `str`：保留原始文本，空字符串保持 `""`，公式和格式控制符保持原始字面量，严禁 `eval`。
- 明确支持的列类型集合 `{"int", "int_or_empty", "bool", "str"}`，出现任何未知类型直接拒绝并抛出 `CatalogSchemaError`，绝不静默降级为 `str`。

### 3.3 深度数据不可变性保证
- 内部所有记录与 Schema 元数据均使用 `MappingProxyType`、`tuple` 等不可变结构固化，`schema.source_entry` 固化为 `tuple`，防止调用方通过 `.append()` 修改。
- 对外公开的所有查询与信息接口（`get_batch_info`、`get_validation_summary`、`list_datasets`、`get_record`、`query_records`、`query_quarantine`、`query_overwrites` 等）均返回深度独立拷贝（`copy.deepcopy`），调用方对返回的嵌套字典/列表进行任何篡改，绝对不会影响加载层内部真实状态。

### 3.4 核心业务语义固化
1. **隔离记录（4 条）**：
   - 道具 72548：保留非法 CP950 原字节十六进制 `c2f9a448a7a4c34dc5e9c5e784`。
   - 资质 2800：保留 `法力資質=2130` 与 `法力資質最大值=1989`，不篡改不补零。
   - 技能 719、4406：描述边界未确认，继续隔离。
2. **缺失资质（3 条）**：
   - 宠物 3010（未定）、4021（年獸）、4022（爆竹）在资质表不存在，作为缺失记录单独提供，不合成零值。
3. **同名技能歧义保留**：
   - `高級命中` 同时保留候选 229 与 255；
   - `終級命中` 同时保留候选 329 与 355；
   - 均标注 `ambiguous=True`，严禁自动选取第一个 ID。
4. **技能覆盖证据（9 条）**：
   - 记录 3205 表写入覆盖，包含 4573 由「天魔返生術」覆盖为「地魔返生術」的完整旧值/新值。
5. **地图与 NPC 来源独立性**：
   - 2601 复合主键为 `(scene_id, record_index)`，保留 632 条零 ID 记录。
   - 2804 POS 复合主键为 `(scene_id, scene_display_name, record_index)`，保留 631 条零 ID 记录。
   - 保留两表记录顺序与重复项，不擅自按 NPC ID 合并去重。

---

## 4. 查询 API 实现 (`review_api`)

### 4.1 统一路由与严格参数校验
- 所有路由统一前缀为 `/api/v1/review`。
- **严格参数校验**：
  - 排序参数 `order` 必须为 `asc` 或 `desc`，传入非法值返回 400 `INVALID_PARAMETER`。
  - 单数据集查询支持的字段过滤仅限该数据集的实际列名或 `_pk`，若拼错或传入未知过滤列（例如 `invalid_col=123`），严格返回 400 `INVALID_PARAMETER`，绝不静默忽略。
  - 隔离记录接口 `/quarantine` 仅接受 `entry_index`、`record_key`、`offset`、`limit`；若传入 `record_kee` 等未知参数，严格返回 400 `INVALID_PARAMETER`。
  - 技能覆盖接口 `/overwrites` 仅接受 `key`、`offset`、`limit`，其它未知参数返回 400 `INVALID_PARAMETER`。
  - 无参数接口（`/health`、`/batch`、`/datasets`、`/missing-aptitudes`、`/ambiguous-skills` 等）若收到任何查询参数，返回 400 `INVALID_PARAMETER`。
- 统一错误格式：
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": {}
    }
  }
  ```
- 错误码包括：`INVALID_PARAMETER` (400), `NOT_FOUND` / `DATASET_NOT_FOUND` / `RECORD_NOT_FOUND` (404), `METHOD_NOT_ALLOWED` (405), `CATALOG_NOT_READY` (503), `INTERNAL_SERVER_ERROR` (500)。

### 4.2 接口矩阵
| 路径 | 方法 | 功能描述 |
|---|---|---|
| `/api/v1/review/health` | GET | 探针与就绪检查（返回总记录数 12,202，已加载文件数 22，数据集数 17） |
| `/api/v1/review/batch` | GET | 批次声明、校验结果与非原生确认标记 |
| `/api/v1/review/datasets` | GET | 17 个数据集的 Schema 与字段清单 |
| `/api/v1/review/datasets/{dataset_id}` | GET | 单数据集元数据及字段类型 |
| `/api/v1/review/datasets/{dataset_id}/records` | GET | 核心查询：支持 offset/limit 分页、q 模糊搜索、字段等值过滤、排序 |
| `/api/v1/review/datasets/{dataset_id}/records/{record_id}` | GET | 单记录精确查找（支持单主键与冒号拼接的复合主键） |
| `/api/v1/review/quarantine` | GET | 4 条隔离记录详情与原始字节证据 |
| `/api/v1/review/overwrites` | GET | 9 条技能写入覆盖证据 |
| `/api/v1/review/missing-aptitudes` | GET | 3 条缺失资质宠物看板接口 |
| `/api/v1/review/ambiguous-skills` | GET | 4 条同名技能候选看板接口 |

---

## 5. 服务启动与受控配置

### 5.1 依赖安装
```bash
pip install -r server/apps/review_api/requirements.txt
```

### 5.2 受控批次目录配置（供 Agent J 验收）
默认加载路径为 `server/docs/csv_checks/batch_001`。
为了便于测试夹具与异常批次注入，支持以下三种受控方式指定测试目录（严禁通过 HTTP 参数传入任意路径）：
1. 环境变量：`REVIEW_BATCH_DIR=/path/to/test_batch python3 server/apps/review_api/main.py`
2. 命令行参数：`python3 server/apps/review_api/main.py --batch-dir /path/to/test_batch`
3. 应用工厂：`create_app(batch_dir="/path/to/test_batch")`

### 5.3 启动开发服务
服务端默认绑定 `0.0.0.0:8000`，完全适配 Arena 容器预览网络环境：

```bash
# 启动命令
python3 server/apps/review_api/main.py --host 0.0.0.0 --port 8000
```
