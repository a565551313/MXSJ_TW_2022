# Agent F — CSV 抽取核查探针（只读）

全部脚本只读：不修改 `data/script.fls`、`tools/decompiler/*`、`tools/fls_batch_decoder.py`、
`server/game_data/`；不执行任何恢复出来的客户端脚本；不写任何正式数据。

运行方式（仓库根目录）：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/csv_checks_agent_f/<probe>.py
```

`*.out` 是对应的实际输出。

## 2566 / titledata.py

| 脚本 | 作用 |
|---|---|
| `probe67_recap_2566_1919.py` | 重算 2566 / 1919 的载荷 SHA-256、已存 vs 候选 bounds 下全模块字符串 CP950 审计、目标记录的载荷偏移 |

## 1919 / ridedata.py

同上（`probe67_recap_2566_1919.py`）。

## 244 / newfurnituredata.py

| 脚本 | 作用 |
|---|---|
| `probe40.py` | 对 B1 / B2 / B3 做"未映射 Duoyi opcode 数"细化扫描 |
| `probe41.py` | 已存 keys 下 marshal 走查 + 字符串 CP950 评分（证明 keys[2..4] 与 bounds[1..3] 对结构是自洽的） |
| `probe42.py` | `PY25_MAP` 的 `0x42` 孪生键统计；key1 取值对 marshal 走查的影响 |
| `probe43.py` | 已存 / key1=11 / key1=73 三种配置下走查 `co_code` 并抽取各表 |
| `probe44.py` | B1 = 36000–37200 全扫描（key1 固定 11） |
| `probe45.py` | B1 候选 + marshal 走查 + 各表抽取对比 |
| `probe46.py` | B1 候选的指令对齐检查 |
| `probe47.py` | 全部 64 个模块级 `STORE_NAME` 及 `co_code` 偏移 |
| `probe48.py` | `ORDER` 存储区与 `DATA` 构建起始段指令转储 |
| `probe49.py` | 第一条内层 dict 的完整字段序列转储 |
| `probe50_data_eval.py` | 本地扩展版 `evaluate_literals`（仅额外允许 `LOAD_NAME 'None'`），重算 `DATA` |
| `probe51_data_verify.py` | B1 候选对比 + 233 条 `DATA` 全量转储 |
| `probe52_29760.py` / `probe53_29760_detail.py` | 定位并转储 `DATA[29760].desc` 异常串 |
| `probe54_all_strings.py` | 全模块 665 个字符串的严格 CP950 审计（含控制字节表甄别） |
| `probe55_tail.py` | `DATA[29760].desc` 尾部读法与相邻 marshal 串 |
| `probe56_encodings.py` | 45 个坏字节在 10 种编码下的解码尝试（全部失败） |
| `probe57_key_scan.py` | 45 个坏字节穷举 256 个单字节 key |
| `probe58_split.py` | 119 字节串穷举"段内 split × 双键" |
| `probe63_b3.py` / `probe64_b3_scan.py` | B3 = 73000–73300 全扫描，唯一语义完整解 73114 |
| `probe65_final.py` | 终版验证：`instructions()` 无错 + 七张表重建 + 397 串 0 失败 |
| `probe66_cocode_stats.py` | `co_code` 区间未映射 Duoyi opcode 统计（已存 vs 候选）+ 全量表转储 |

## 报告

结论见 `server/docs/csv_checks/AGENT_F.md`。
