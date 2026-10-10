# E-SCRIPT-002: script.fls 全量脚本解码与分析（Task-B）

> 状态: 终版（v4 全量 + v7 二轮重试已合并，见 `终版统计.md`）。
> 只读约束: 未修改 `data/script.fls`；全部离线，见仓库根约束。

## 1. 范围与方法

- `data/script.fls`（24MB，5002 entries）→ zlib 解压 → 5 段 XOR 自动破解
  （`tools/fls_batch_decoder.py` v7：贪心边界扫描 + key 候选 + combo 联合修复 +
  struct 探针 + 边缘扩展 + 熔断/超时）。
- 反汇编：`tools/pymarshal_dis.py` + S 盒映射 `mapping_table_v4.json` (v4.2)。

## 2. 解码结果（v4 全量，5002/5002）

v4 全量：ok 4132（82.6%）/ fail 689 / suspect 181。

**终版（v7-retry 合并）**：ok **4484（89.6%）** / suspect 246 / fail 272。
- v7-retry 覆盖 870 条 fail+suspect：fail→ok 287（救回率 41.7%），suspect→ok 65，合计净增 352 ok。
- 注意：`ok` 仅表示解析完整且 sanity 通过；名字级正确性另见 `suspicious-names-review.md`（可疑名 179 条，抽检显示二轮修复不完全）。
- 明细见 `终版统计.md`。

## 3. 关键发现

1. **五段 XOR 确认**：`estimate_keys` + 边界扫描在 82.6% 条目一次成功。
2. **co_code S 盒多变体**：同字节在不同 code-object 可具不同尺寸/含义
   （`0x6C` = UNPACK-3B（逻辑）/ BINARY-1B（数据），ok/0-garbage 真值双端验证）。
3. **v3 表四处纠正**（各千~万例）：`98→STORE_NAME`、`E0→IMPORT_NAME`、`FB→MAKE_FUNCTION`、`42→BUILD_CLASS`；新增 `08/AD/A2/AF/D3/36/58/38/E3` + BINARY-1B 类 + `(05,30)/(43,5A)` 对。121080 函数，98311 端对齐全解析。
4. **跳转基址怪癖**：B7/E3 用 `pos+arg`，A2 绝对，E5/AF/D3 用 `pos+3+arg`。
5. **协议结构**：`C2GS*/GS2C*` + 主 opcode + `iSub`（`C2GS_HUODONG=0xcd` 30 模块、`GS2C_HUODONG_OP=0xce` 33 模块……共 28 家族）；商城用 `C2S/S2C` 前缀；CJK=Big5。
6. **战斗**：`warturn.py` 回合状态机（`g_Quene` 指令队列笔误原文、`g_TurnDict` 快照、`Jump` 重放、`CalHP` 结算）+ `magic.py` 弹道插值（直线/Hermite/Bezier）与 `CMagic` 特效节点。
7. **任务/物品**：305 quest-ish / 195 item-ish；`juben/task*.py` 逐任务数据（`GetJubenData`）；打造/商城 API 面完整。
8. **开发者笔误指纹**（原文照录）：`soznd`（magicid2soznddata）、`Describle`（All_Describle1）、`Quene`（g_Quene）、`Recieve`（DoRecieveLinkEvent）、`btimapdemo.py`、`whilelstdata`（while-list）、`scripeMdata`（entry293 坏解码）、`annulbeautycontest`（目录名）。

## 4. 残留问题

- **可疑名**：179 个 ok 条目含损坏函数名（sanity 过滤无法识别）。二轮 v7 重解码后，经词表校验仅 55 条确认正确，113 条仍有词表外名字，11 条重解码失败保留 v4。见 `suspicious-names-review.md`。（任务书中的 177 与 `suspicious_name` 字段在数据中不存在，已按规则重新定义。）
- **entry84**（newpresentdata.py）：五 key 已破 `[eb,db,85,64,f6]`，卡 `'l'`-n 损坏（4B 归档损坏或第 6 微段）；已封存（`artifacts/entry84-parked-notes.md`）。
- **entry251**（50KB）：病态嵌套曾挂 6 分钟；已加读预算（60K）+ 熔断（8 hits）+ 单条 150s 上限，现 fail-fast（`timeout-s0`）。
- **bare-expr 之谜**：`(05,30)` 丢弃 BINARY 结果 11K 次（同模块亦有 1.8K 正常使用）；需栈模拟/运行时确认。
- **未知 opcode**：`00/72/db/06/47/0b/90/f2/0e/57/cf` 等（700~4000x/函数级）待第四轮挖掘；`0x38` 在函数=LOAD_LOCALS（9224/9224 类尾），模块零出现。第四轮（unknown_hot 16 个）本轮**未破解**，见 `unknown-opcode-round4-status.md`。

## 5. 交付物

- `artifacts/script-catalog.csv`（5002 行，终版，已按 v7 合并结果重出，保留原 prio 列）
- `artifacts/终版统计.md`（终版数字与明细）
- `artifacts/suspicious-names.json` / `suspicious-names-review.md` / `suspicious-names-repair-candidates.json`（可疑名二轮）
- `artifacts/mall-protocol-analysis.md`（商城 C2S/S2C 协议专题）
- `artifacts/fullrun/decode-results-final.jsonl`（终版逐条结果，带 source 字段）
- `tools/extract_co_signatures.py`（导出 code object 的 varnames/names/consts）
- `artifacts/protocol-commands-catalog.md`（1783 行，28 opcode 家族）
- `artifacts/battle-logic-analysis.md`、`artifacts/quest-item-analysis.md`
- `tools/fls_batch_decoder.py` (v7)、`tools/pymarshal_dis.py`
- `notes/co_code_analysis/mapping_table_v4.json` (v4.2)
- `artifacts/fullrun/v4ok-classified.json`（P0-battle 488 / P0-net 369 / P1 1254 / P2-data 329 / P9 1692）
- `artifacts/entry84-parked-notes.md`

## 6. 复现

```bash
python3 tools/fls_batch_decoder.py --all --output <outdir> --jobs 2        # v4 全量
python3 tools/fls_batch_decoder.py --archive data/script.fls --all --output <outdir>/v7-retry --indices <870 个 fail+suspect 索引> --jobs 2 --resume  # v7 重试（任务书中 --v7-retry/--input 参数不存在）
python3 tools/pymarshal_dis.py <entryN.marshal.bin> [--code-only F] [--sizes ..]  # 反汇编
```
