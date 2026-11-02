# tools 依赖清单与迁移闸门

核对：2026-10-18，代码／旧证据基线 `886915c2611e661d7c51b057a7a5a8b6cc4038c0`。
这是**已确认的代表性静态依赖清单，不是穷尽调用图**。没有执行被检查工具或恢复模块。
状态分类与推荐入口见 [README](README.md)。

## 三类引用

- **运行依赖 R**：import、动态加载、读取文件、子进程调用或打包所需输入。包含开发／测试／构建时依赖，不表示生产运行。
- **证据依赖 E**：固定 SHA、预期产物、来源对照；即使代码不 import 也不能无审查移除。
- **说明引用 D**：注释、设计和历史来源记录。不能只凭字符串出现就称为运行依赖。

## 已核实的依赖边

| 类型 | 消费者 → 依赖 | 代码／材料依据及影响 |
|---|---|---|
| R | [build_material_inventory.py](../server/tools/build_material_inventory.py)、[verify_source_map.py](../server/tools/verify_source_map.py) → `decompiler/batch_decompile.py` | 直接导入 `Py25MarshalTranspiler, XTABS`；移除会破坏来源／材料检查 |
| R | [map_npc_reproduction.py](../server/tools/map_npc_reproduction.py) → `decompiler/batch_decompile.py` | 导入 `PY25_MAP, XTABS`，另读取源码计算摘要 |
| R | [review_client_data_boundaries.py](../server/tools/review_client_data_boundaries.py)、[verify_client_data_boundaries.py](../server/tools/verify_client_data_boundaries.py) → `batch_decompile`、`fls_batch_decoder.MarshalReader` | 直接导入；CSV 探针目录也有同类引用，未逐个执行 |
| R | [build_native_registration.py](registration/build_native_registration.py) → batch、pack、decoder | `load_module` 动态加载三个旧文件；日常脚本编辑器接替用途不消除注册构建依赖 |
| R | [batch_decompile.py](decompiler/batch_decompile.py) → [universal_fls_tool.py](data-parser/universal_fls_tool.py) | `process_data_fls()` 在输入为包时启动 `unpack` 子进程；输入目录分支不同 |
| R | [pack_and_encrypt.py](decompiler/pack_and_encrypt.py) → batch | 导入转译器／映射；不是独立于旧研究管线的实现 |
| R | [recover_entries.py](decompiler/recover_entries.py) → batch、[build_script_index.py](script_link/build_script_index.py) | 前者转译，后者用于受限 marshal 摘要；[crosscheck_pycdc.py](decompiler/crosscheck_pycdc.py) 再复用 recover_entries |
| R | [build_script_index.py](script_link/build_script_index.py) → batch＋key DB | 默认 `--out` 为 `ui_editor/src/ui_editor/data/script_index.json`，直接 write_text；不能无审批覆盖索引 |
| R | [UI ScriptIndex](../ui_editor/src/ui_editor/core/script_index.py) → 随包 `script_index.json` | `load_builtin()` 读取生成产物；GUI 日常运行不是调用生成器，也不因编辑器升级自动刷新产物 |
| R | [agent_b_item_probe.py](../server/tools/agent_b_item_probe.py) → `decompiler/output/data_fls/lib/opcode.py` | `read_text` 后按文本解析标准 opcode 名，不是执行恢复模块；output 不能整体当缓存删掉 |
| R | [build_material_inventory.py](../server/tools/build_material_inventory.py) → output 的 manifest／源码路径集合 | 读取 data_fls/manifest.json、扫描恢复文本；删除会改变材料统计 |
| R | [make_source_package.py](../script_manual/make_source_package.py) → batch、recover、recover 测试＋devkit | EXTRAS／PREFIXES 纳入源码交付材料；是打包依赖，不是手册查看器运行时导入 |
| R | [check_manual.py](../script_manual/check_manual.py) → `test_recover_entries.py` | 统一闸门以子进程执行专项测试；移动会破坏开发检查 |
| R | [data_browser/app.py](data_browser/app.py)、[desktop_app.py](data_browser/desktop_app.py) → `data-export/game_data.sqlite` | 两者 DB_PATH 指向旧数据库；新复核系统不自动替代旧表 |
| R | [extract_dlg.py](data-parser/extract_dlg.py) → [mx_path_hash.py](data-parser/mx_path_hash.py) | 直接 import；共享核心真源不是自动替换这个 import |
| R | [pe_resource_patch.py](data-parser/pe_resource_patch.py) → [pe_resource_dump.py](data-parser/pe_resource_dump.py) | SourceFileLoader 动态加载；删除 dump 会影响 patch |
| R | [dis_v43.py](dis_v43/dis_v43.py) → [parse_marshal.py](dis_v43/parse_marshal.py) | 本目录导入 load/walk/codename |
| R | [pymarshal_dis.py](pymarshal_dis.py)、[extract_co_signatures.py](extract_co_signatures.py) → fls_batch_decoder | 导入 MarshalReader／解码模块，历史 CLI 也并非完全独立 |
| R | [ui_pack_write_probe.py](ui_pack_write_probe.py) → [build_registration_preview.py](client_patches/build_registration_preview.py)、UI 核心 | 旧补丁辅助函数仍被探针复用，存在临时包写入；停用 UI 方案不代表辅助代码无消费者 |
| E | [agent_e_reproduction.json](../server/docs/csv_checks/agent_e_reproduction.json) → batch SHA | `inputs.shared_decoder` 记录路径／摘要；改注释也改变输入身份 |
| E | [batch_001/manifest.json](../server/docs/csv_checks/batch_001/manifest.json) → batch、fls decoder SHA | `tool_and_evidence_sha256` 固定来源；迁移需重新生成并审查差异，不是随手改哈希 |
| D | [脚本 VM tables.py](../script_editor/src/script_editor/core/vm/tables.py) → batch 历史版本 | 来源注释及 SHA 不等于当前运行 import 该文件 |
| D | [地图 scriptfls.py](../map_editor/src/map_editor/client/scriptfls.py)、[mx_common](../mx_common/README.md) → 旧 decoder／格式参考 | 同源／参考说明，不应误记为直接 import |

## 核查方法与未覆盖范围

从仓库根进行只读检索，再打开命中处区分实际调用与注释。例如：

```bash
git grep -n -E 'batch_decompile|fls_batch_decoder|pack_and_encrypt|universal_fls_tool' -- '*.py' ':!tools/decompiler/output/**' ':!work/**'
git grep -n -E 'shared_decoder|tool_and_evidence_sha256' -- server/docs/csv_checks
```

第二轮按实际目标检索 `build_script_index`、`game_data.sqlite`、`mx_path_hash`、`pe_resource_dump` 等名称，并查看文件路径读取、动态加载与调用分支。
排除恢复文本和庞大历史 work 区是为了不把材料内容当作当前工具 import；**不代表这些区没有依赖**。
动态拼路径、外部批处理／用户工作流、未纳入 Git 的材料、完整历史证据引用仍未穷尽。
没有发现引用只能标“尚未确认消费者”，不能写“无依赖，可删除”。

## 第二阶段迁移的批准条件（尚未实施）

1. 选定一个消费者及固定输入，保存原输出、失败项、依赖版本与摘要。
2. 新旧实现隔离运行，核对条目身份、字段／常量、失败分布与未改负载，不只比较成功数量。
3. 明确接受或拒绝每类差异；有游戏语义影响时增加独立原生验证。
4. 再改调用、测试和必要证据；旧证据保留历史，不用改期望值掩盖行为变化。
5. 完成消费者迁移及外部工作流核查后才决定归档。停用候选也先检查辅助函数依赖。

## 保护壳模拟（2026-10-26）

- R：`dyprot_unpack/dyprot_emulate.py` 需要 pefile 2024.8.26 + Unicorn 2.1.4 与仓库根
  `mxmain.dll`（摘要锁定；缺任一依赖时工具给提示并退出 2）。
- R：`fake_modules.py` 只依赖标准库；`test_dyprot_emulate.py` 在缺依赖时整档跳过。
- E：假 DLL 映像只用于让壳能解析导出表，**不是** Windows 系统 DLL 的真实行为；
  模拟结果不能替代 Windows 实机或 `ReadProcessMemory` 转储。

## 客户端原生 MCP 接入骨架（2026-11-02）

- D：`client_mcp/` 当前只有 README、文档和占位目录；没有可运行 Python 包、探针或构建器，因此暂无已核实运行依赖。
- D：文档草案引用原始 `data/script.fls` 与 `tools/decompiler/script_fls_keys.json` 的锁定 SHA-256，仅作为输入边界说明；当前没有代码读取或修改它们。
- 未来 M1 需要用户提供的修改版 `script.fls`；在输入登记和只读差异核对前，不得假设探针挂点、条目编号或 key DB 适用性。
- 未来如复用 decompiler / script_editor / registration 管线，必须重新核实运行依赖与证据依赖，不能因文档提到就视为已接入。

## 原生 TCP 候选模块（2026-10-20）

- R：`native_channel/src` 与普通单元测试只依赖 Python ≥3.10 标准库。
- R/E：可选 `tests/native_oracle.py` 依赖 pefile 2024.8.26、Unicorn 2.1.4 和摘要锁定的 `mxmain.dll`、`exe/render.dll`；不调用 Windows DLL 入口。
- R/E：`tests/script_evidence.py` 只读复用 `script_link/build_script_index.py` / decompiler 管线，校验 script.fls 与 key DB 摘要；不执行游戏模块。
- E：`native_channel/evidence/vectors.json` 是原生指令模拟的假数据预期值，不能随兼容实现任意更新；变更需重新运行独立 oracle。
