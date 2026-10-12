# MXSJ 客户端数据复核查询 API 接口契约 (v1)

- **版本：** 1.0.0
- **基准批次：** `batch_001` (2026-10-12)
- **统一路由前缀：** `/api/v1/review`
- **定位：** 本接口为只读数据复核与目录浏览专用 API，供前端网页（Agent I 开发）展示与验收（Agent J）使用。**不是正式游戏服务器管理后台，不实现玩法逻辑，不支持任何写入操作。**

---

## 1. 核心设计原则与数据语义

1. **复核候选性质**：所有数据均为静态提取的复核候选数据，不代表原生加载器确认的服务端规则。
2. **禁止静默修改与推断**：
   - 严格类型转换：布尔值仅接受 `"true"` 为 True，`"false"` 为 False，不得把 `"false"` 转为真值；整数转换失败直接报错拒绝。
   - 遵守地图/NPC 的旧空值约定（E 约定），不擅自给空文本赋予新含义。
   - 保留复合主键，不按 NPC ID 简单去重；保留 NPC ID 为 0 的记录（原顺序、原计数值）。
   - 技能名称歧义保留（`高級命中` 对应 229/255，`終級命中` 对应 329/355，`ambiguous=true`），绝不自动选取第一个 ID。
   - 缺失资质（3010, 4021, 4022）与隔离资质（2800）严格区分，绝不补零。
   - 原始描述、公式、控制符和客户端标记原样作为字符串返回，**严禁 eval 或执行**。
3. **只读安全性**：
   - 无任何 POST / PUT / PATCH / DELETE 变更接口。
   - 只开放 manifest 声明的 17 个固定数据集及配套元数据，禁止任意文件路径访问。
   - 错误响应不泄露服务器内部绝对路径或调试堆栈。

---

## 2. 统一错误响应规范

所有错误响应均遵循统一 JSON 结构，并返回相称的 HTTP 状态码：

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "Dataset 'unknown_table' does not exist.",
    "details": {}
  }
}
```

### 错误码字典

| HTTP 状态码 | 错误码 (`code`) | 说明 |
|---|---|---|
| 400 Bad Request | `INVALID_PARAMETER` | 分页参数越界（如 limit < 1 或 > 500）、排序字段不存在、过滤字段类型非法 |
| 404 Not Found | `DATASET_NOT_FOUND` | 请求的数据集不存在 |
| 404 Not Found | `RECORD_NOT_FOUND` | 指定主键的记录不存在 |
| 405 Method Not Allowed | `METHOD_NOT_ALLOWED` | 尝试调用非 GET 请求 |
| 503 Service Unavailable | `CATALOG_NOT_READY` | 目录尚未加载完成或底层校验失败 |

---

## 3. 数据集标识与复合身份规范

### 3.1 稳定数据集标识符 (`dataset_id`)

API 支持以下标准 Slug 访问 17 个 CSV 数据集：

| `dataset_id` | 源文件路径 | 主键字段 (`primary_key`) | 行数 |
|---|---|---|---:|
| `items` | `items.csv` | `["client_shape_id"]` | 6,851 |
| `pets` | `pets.csv` | `["client_shape_id"]` | 135 |
| `pet_skill_candidates` | `pet_skill_candidates.csv` | `["client_shape_id", "sequence"]` | 458 |
| `pet_required_skills` | `pet_required_skills.csv` | `["client_shape_id"]` | 26 |
| `pet_aptitudes` | `pet_aptitudes.csv` | `["client_shape_id"]` | 131 |
| `pet_aptitude_missing` | `pet_aptitude_missing.csv` | `["client_shape_id"]` | 3 |
| `pet_skills` | `pet_skills.csv` | `["skill_id"]` | 579 |
| `pet_skill_overwrites` | `pet_skill_overwrites.csv` | `["write_order"]` | 9 |
| `pet_skill_name_matches` | `pet_skill_name_matches.csv` | `["skill_name_raw", "skill_id"]` | 145 |
| `mapdata_parent_scene` | `maps_npcs/mapdata_parent_scene.csv` | `["scene_id"]` | 6 |
| `mapdata_scene_dictionary` | `maps_npcs/mapdata_scene_dictionary.csv` | `["scene_id"]` | 104 |
| `minimapnpcpos_pos_records` | `maps_npcs/minimapnpcpos_pos_records.csv` | `["scene_id", "scene_display_name", "record_index"]` | 1,344 |
| `minimapnpcpos_wenzi_entries` | `maps_npcs/minimapnpcpos_wenzi_entries.csv` | `["scene_id", "x", "y"]` | 287 |
| `npc_2601_vs_2804_agreement` | `maps_npcs/npc_2601_vs_2804_agreement.csv` | `["scene_id", "npcid"]` | 677 |
| `npcname2realnamedata_alias_to_realname` | `maps_npcs/npcname2realnamedata_alias_to_realname.csv` | `["alias"]` | 55 |
| `npcposdata_records` | `maps_npcs/npcposdata_records.csv` | `["scene_id", "record_index"]` | 1,335 |
| `sceneid2name_minimap_scenes` | `maps_npcs/sceneid2name_minimap_scenes.csv` | `["scene_id"]` | 57 |

注：API 亦兼容带目录前缀的标识（如 `maps_npcs/npcposdata_records`）或带扩展名的标识（如 `items.csv`）。

### 3.2 复合主键与记录唯一身份 (`_pk`)

为便于前端表格行渲染（React `key` 等）及详情检索：
- 每个返回的记录对象均包含一个由 API 统一生成的 `_pk` 字符串字段。
- 单一主键：直接为其字符串形式，例如 `"1010"`。
- 复合主键：按主键声明顺序以冒号 `:` 拼接，例如 `pet_skill_candidates` 中 `client_shape_id=1010, sequence=0` 的 `_pk` 为 `"1010:0"`；`npcposdata_records` 中 `scene_id=1301, record_index=5` 的 `_pk` 为 `"1301:5"`。
- 查询单条记录接口 `/datasets/{dataset_id}/records/{record_id}` 中，`{record_id}` 支持传入此 `_pk` 字符串。

---

## 4. 接口列表与规范

### 4.1 服务健康与就绪检查

- **路径：** `GET /api/v1/review/health`
- **功能：** 供前端轮询与平台可用性探针使用，确认数据加载状态。
- **响应：**
  ```json
  {
    "status": "ready",
    "batch": "batch_001",
    "loaded_files_count": 22,
    "datasets_count": 17,
    "total_records_count": 12202
  }
  ```
  若启动校验失败或尚未就绪，返回 HTTP 503 与错误详情。

---

### 4.2 批次信息与校验摘要

- **路径：** `GET /api/v1/review/batch`
- **功能：** 获取当前复核批次元数据、校验规则汇总、疑点摘要和原生未确认声明。
- **响应：**
  ```json
  {
    "batch": "batch_001",
    "native_loader_confirmed": false,
    "manifest_files_count": 21,
    "csv_format": {
      "delimiter": ",",
      "encoding": "UTF-8 without BOM",
      "newline": "LF",
      "formula_policy": "Opaque text. Spreadsheet users must import text; do not evaluate formulas."
    },
    "tables_summary": {
      "1945": { "source_records": 6852, "review_csv_records": 6851, "quarantined_records": 1 },
      "2027": { "source_records": 135, "review_csv_records": 135, "quarantined_records": 0 },
      "2954": { "source_records": 132, "review_csv_records": 131, "quarantined_records": 1 },
      "3205": { "source_records": 581, "review_csv_records": 579, "quarantined_records": 2 }
    },
    "validation_summary": {
      "checks": {
        "csv_round_trip": "pass",
        "item_category_key_set": "pass",
        "map_npc_evidence_and_staging_match": "pass",
        "pet_aptitude_foreign_keys": "pass",
        "pet_skill_names_have_candidates": "pass"
      },
      "missing_aptitude_count": 3,
      "pet_skill_names": 143,
      "quarantined_record_count": 4,
      "skill_write_count": 590,
      "skill_unique_count": 581,
      "skill_overwrite_count": 9,
      "ambiguous_pet_skill_names": {
        "終級命中": [329, 355],
        "高級命中": [229, 255]
      }
    }
  }
  ```

---

### 4.3 数据集清单与 Schema 描述

- **路径：** `GET /api/v1/review/datasets`
- **功能：** 返回全部 17 个数据集的清单、显示名称、行数、主键定义及字段类型定义。
- **响应：**
  ```json
  {
    "total": 17,
    "datasets": [
      {
        "id": "items",
        "filename": "items.csv",
        "rows": 6851,
        "primary_key": ["client_shape_id"],
        "notes": "Display catalog, includes test/history entries. Category meanings not normalized...",
        "source_entry": 1945,
        "source_table": "DATA+ITEMDATABYTYPE+SHAPETABLE",
        "columns": [
          { "name": "client_shape_id", "type": "int" },
          { "name": "name", "type": "str" },
          { "name": "description_raw", "type": "str" },
          { "name": "category_code_raw", "type": "int" },
          { "name": "image_id", "type": "int" },
          { "name": "image_mapping_explicit", "type": "bool" },
          { "name": "source_entry", "type": "int" },
          { "name": "source_table", "type": "str" },
          { "name": "review_status", "type": "str" }
        ]
      }
    ]
  }
  ```

---

### 4.4 单数据集元数据查询

- **路径：** `GET /api/v1/review/datasets/{dataset_id}`
- **功能：** 查询单个数据集的详细 schema 与统计信息。
- **响应：**
  ```json
  {
    "id": "pets",
    "filename": "pets.csv",
    "rows": 135,
    "primary_key": ["client_shape_id"],
    "notes": "...",
    "source_entry": 2027,
    "source_table": "DATA",
    "columns": [
      { "name": "client_shape_id", "type": "int" },
      { "name": "name", "type": "str" },
      { "name": "liupai_raw", "type": "str" },
      { "name": "attack_type_raw", "type": "str" },
      { "name": "carry_grade", "type": "int" },
      { "name": "maxskillnum_raw", "type": "int" },
      { "name": "address_raw", "type": "str" },
      { "name": "source_entry", "type": "int" },
      { "name": "source_table", "type": "str" },
      { "name": "review_status", "type": "str" }
    ]
  }
  ```

---

### 4.5 单数据集记录查询（搜索、分页、精确字段过滤、排序）

- **路径：** `GET /api/v1/review/datasets/{dataset_id}/records`
- **功能：** 核心数据浏览接口，支持分页、模糊搜索、字段等值精确过滤、指定列排序。
- **查询参数：**
  | 参数名 | 类型 | 默认值 | 说明 |
  |---|---|---|---|
  | `offset` | int | `0` | 分页偏移量，>= 0 |
  | `limit` | int | `50` | 单页大小，1 <= limit <= 500 |
  | `q` | str | 无 | 文本搜索关键字，对表中字符串列进行大小写不敏感子串匹配，或对数值主键/代码列进行精确字符串匹配 |
  | `sort_by` | str | 无 | 排序字段名（必须为该表的合法列名或 `_pk`，否则返回 400 `INVALID_PARAMETER`） |
  | `order` | str | `asc` | 排序方向：仅接受 `asc`（升序）或 `desc`（降序）；传入其它值返回 400 `INVALID_PARAMETER` |
  | `*` (列名) | any | 无 | **精确字段过滤**：任何属于当前表列名或 `_pk` 的查询参数均作为精确相等过滤。如 `client_shape_id=1010`、`category_code_raw=3`、`scene_id=1301`、`review_status=candidate`。**若传入任何未知或拼错的参数名，严格返回 400 `INVALID_PARAMETER`，绝不静默忽略。** |
- **响应结构：**
  ```json
  {
    "dataset": "items",
    "total": 6851,
    "offset": 0,
    "limit": 50,
    "count": 50,
    "records": [
      {
        "_pk": "1001",
        "client_shape_id": 1001,
        "name": "跌打草",
        "description_raw": "#c00ff00回復氣血#r戰鬥外使用，每秒回復氣血10點，持續10秒",
        "category_code_raw": 1,
        "image_id": 1001,
        "image_mapping_explicit": false,
        "source_entry": 1945,
        "source_table": "DATA+ITEMDATABYTYPE+SHAPETABLE",
        "review_status": "candidate"
      }
    ]
  }
  ```
- **分页总数含义**：
  - `total`：满足当前过滤条件（`q` 和精确字段过滤）的记录总条数。前端据此计算总页数 `ceil(total / limit)`。
  - `count`：当前返回列表 `records` 的实际条数。
  - `offset`：当前返回第一条记录在过滤后结果集中的起始索引。

---

### 4.6 单条记录精确查询

- **路径：** `GET /api/v1/review/datasets/{dataset_id}/records/{record_id}`
- **功能：** 按记录主键获取单条记录。
- **参数说明：**
  - `{record_id}`：单一主键直接传主键值（如 `/items/records/1001`）；复合主键传入冒号拼接的 `_pk`（如 `/pet_skill_candidates/records/1010:0`）。
- **响应：** 存在则返回包含 `_pk` 的记录 JSON 对象；不存在返回 404 `RECORD_NOT_FOUND`。

---

### 4.7 隔离记录查询 (`quarantine`)

- **路径：** `GET /api/v1/review/quarantine`
- **功能：** 查询第一批复核中被隔离的 4 条问题记录（道具 72548、资质 2800、技能 719、技能 4406）及其原始字节证据与隔离原因。
- **查询参数：**
  - `entry_index` (int, 可选): 按源条目过滤，如 `1945`、`2954`、`3205`。
  - `record_key` (str/int, 可选): 按记录键过滤，如 `72548`、`2800`。
  - `offset` (int, 默认 0), `limit` (int, 默认 50, 1 <= limit <= 500)。
  - **严格参数校验**：仅允许上述 4 个参数；若传入未知或拼错参数（如 `record_kee`），严格返回 400 `INVALID_PARAMETER`，绝不静默忽略。
- **响应：**
  ```json
  {
    "total": 4,
    "records": [
      {
        "entry_index": 1945,
        "table": "DATA",
        "record_key": 72548,
        "native_verified": false,
        "reasons": [
          "invalid_cp950_source_name_bytes_preserved",
          "encoding_or_control_character"
        ],
        "value_under_applied_profile": {
          "tuple": [
            { "bytes_hex": "c2f9a448a7a4c34dc5e9c5e784" },
            { "bytes_hex": "a8cfa5ceabe1a569..." }
          ]
        }
      }
    ]
  }
  ```

---

### 4.8 技能覆盖证据查询 (`overwrites`)

- **路径：** `GET /api/v1/review/overwrites`
- **功能：** 查询 3205 技能表在编译时发生的 9 次覆盖摘要与字节码偏移证据（尤其包含 4573 从「天魔返生術」覆盖为「地魔返生術」证据）。
- **查询参数：**
  - `key` (int, 可选): 按技能 ID 过滤，如 `4573`。
  - `offset` (int, 默认 0), `limit` (int, 默认 50, 1 <= limit <= 500)。
  - **严格参数校验**：仅允许上述 3 个参数；若传入未知参数，严格返回 400 `INVALID_PARAMETER`。
- **响应：**
  ```json
  {
    "total": 9,
    "records": [
      {
        "order": 352,
        "code_offset": 22409,
        "entry_index": 3205,
        "table": "DATA",
        "key": 4573,
        "old_value": { "dict": [...] },
        "new_value": { "dict": [...] }
      }
    ]
  }
  ```

---

### 4.9 缺失资质与同名技能歧义辅助接口

为方便前端快速构建“异常/关注看板”，提供以下聚合快捷接口：

1. **缺失资质宠物列表**：`GET /api/v1/review/missing-aptitudes`
   - 返回 3 条在 2954 中无资质记录的宠物（3010 未定、4021 年獸、4022 爆竹），直接对应 `pet_aptitude_missing.csv`。
2. **同名技能歧义匹配列表**：`GET /api/v1/review/ambiguous-skills`
   - 返回 `終級命中` (329, 355) 与 `高級命中` (229, 255) 的详细关联信息，明确标注 `ambiguous: true`。

---

## 5. 安全与服务运行约束

1. **运行绑定**：开发服务器必须监听 `0.0.0.0`，适配 Arena Web 预览代理环境。
2. **依赖隔离**：查询 API 依赖维护在 `server/apps/review_api/requirements.txt` 中，不污染全仓统一构建规则。
3. **数据不可变性**：只读加载层在内存中必须封装为不可修改的数据结构（如只读副本、元组或深拷贝传递），防止调用方运行时篡改已校验的目录数据。
4. **启动时加载**：所有 21 个声明文件及 manifest 本身在服务启动时完成全量哈希校验与类型解析载入，HTTP 请求期间绝不重新读取或重解密 FLS 归档。若任何文件缺失或损坏，拒绝进入就绪状态。
5. **受控批次目录配置（供 Agent J 验收及本地测试）**：
   - 默认批次目录为仓库固定路径 `server/docs/csv_checks/batch_001`。
   - 支持通过本地启动命令行参数 `--batch-dir`、环境变量 `REVIEW_BATCH_DIR` 或 Python 应用工厂 `create_app(batch_dir=...)` 指定测试副本目录。
   - **严格禁止**在 HTTP 请求中接收任意文件系统路径参数，杜绝路径穿越与任意文件读取风险。
