# MXSJ 客户端数据复核后端与查询 API 说明文档 (BACKEND.md)

- **作者：** Agent H
- **分支：** `arena/e5907ab5-mxsj-tw-2022`
- **目标 PR 基线：** `arena/b53b33e6-mxsj-tw-2022`
- **版本：** 1.0.0 (2026-10-12)

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
│       ├── loader.py               # manifest 校验、SHA-256/大小核验、严格类型转换器
│       └── catalog.py              # ReviewCatalog 管理器、内存索引、不可变查询/过滤/排序
├── apps/
│   └── review_api/                 # FastAPI + Uvicorn 查询 API
│       ├── __init__.py
│       ├── config.py               # 路径配置与服务绑定（0.0.0.0:8000）
│       ├── schemas.py              # Pydantic 响应结构模型
│       ├── routes.py               # /api/v1/review 路由实现
│       ├── app.py                  # FastAPI 应用工厂与统一异常处理
│       ├── main.py                 # CLI 启动入口
│       └── requirements.txt        # 独立依赖清单
├── tests/
│   ├── catalog/                    # 加载层单元测试（21 tests）
│   │   ├── test_loader_and_types.py
│   │   ├── test_catalog_immutability.py
│   │   ├── test_corruptions_and_errors.py
│   │   └── test_semantics.py
│   └── review_api/                 # API 集成测试（23 tests）
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
- 启动时读取 `server/docs/csv_checks/batch_001/manifest.json`。
- 逐个校验全部 21 个清单文件的存在性、字节长度以及 SHA-256 哈希值；若存在不一致，直接抛出 `CatalogIntegrityError` 终止启动，绝不静默丢弃损坏文件。
- CSV 表头列名与顺序必须与 manifest `columns` 声明完全一致，否则抛出 `CatalogSchemaError`。
- 实际记录行数必须与 manifest `rows` 完全一致，否则抛出 `CatalogIntegrityError`。
- 一次性加载入内存，避免运行期每个 HTTP 请求重复解码或解析。

### 3.2 严格类型转换
- `int`：严格整数转换 `int(val.strip())`，拒绝空串、浮点数或非数字字符。
- `int_or_empty`：遵循地图/NPC 旧有约定，空串映射为 Python `None`（JSON 中为 `null`），非空值严格转换为整数。
- `bool`：严格比对 `"true"` -> `True`、`"false"` -> `False`，绝不把字符串 `"false"` 误判为真值；其它输入抛出 `CatalogValueError`。
- `str`：保留原始文本，空字符串保持 `""`，公式和格式控制符保持原始字面量，严禁 `eval`。

### 3.3 数据不可变性保证
- 加载后所有行记录均封装在 `types.MappingProxyType` 中，直接对其赋值修改会引发 `TypeError`。
- 检索接口（`get_record`, `query_records`）返回数据副本，调用方对其进行的任何篡改均不会渗透回底层缓存。

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

### 4.1 统一路由与错误规范
- 所有路由统一前缀为 `/api/v1/review`。
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
- 任何未捕获异常均由全局异常处理器拦截，不泄露服务器内部绝对路径与调用堆栈。

### 4.2 接口矩阵
| 路径 | 方法 | 功能描述 |
|---|---|---|
| `/api/v1/review/health` | GET | 探针与就绪检查（返回总记录数 12,202，数据集数 17） |
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

## 5. 服务启动与运行指南

### 5.1 依赖安装
```bash
pip install -r server/apps/review_api/requirements.txt
```

### 5.2 启动开发服务
服务端默认绑定 `0.0.0.0:8000`，完全适配 Arena 容器预览网络环境：

```bash
# 方式一：直接运行入口模块
python3 server/apps/review_api/main.py

# 方式二：使用 uvicorn 命令
uvicorn server.apps.review_api.app:create_app --factory --host 0.0.0.0 --port 8000
```

服务启动后，Swagger 交互式文档可通过 `http://<host>:8000/docs` 访问。

---

## 6. 测试与验证执行

### 6.1 现有基线回归（必须保持全部通过）
```bash
# 架构测试（161 项通过）
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -q

# 第一批 CSV 导出校验（22 个文件一致通过）
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/export_review_csv.py --check
```

### 6.2 新增只读加载层测试（21 项通过）
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/catalog -v
```
覆盖项：
- 17 个数据集加载完整性与 Schema 字段类型。
- 严格布尔值（`"false"` 绝不变真）与整数/空值转换。
- 数据不可变性防护（直接修改被拦截，副本修改不影响底表）。
- 临时夹具异常测试（缺少文件、哈希不符、字节大小不符、行数不符、表头缺失/多余、类型错误、主键重复）。
- 隔离、缺失、技能歧义与 NPC 复合键语义验证。

### 6.3 新增 API 查询接口测试（23 项通过）
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_api -v
```
覆盖项：
- 全部 API 合约端点返回结构与状态码。
- 分页默认值、自定义 limit/offset 及上下限校验。
- 精确字段过滤（宠物技能子表、地图场景 NPC）。
- 关键字搜索（`q` 参数）。
- 复合主键与单一主键单记录获取。
- 异常请求错误码（400, 404, 405, 503）与统一错误 JSON 结构。

### 6.4 运行所有新增测试汇总（44 项通过）
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/catalog -v && \
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/review_api -v
```
