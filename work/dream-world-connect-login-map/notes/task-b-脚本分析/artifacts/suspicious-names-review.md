# 可疑名二轮重试与抽检结论（suspicious-names-review）

## 0. 定义与数据说明（与任务书的差异）

- 任务书称“177 个 ok-but-suspicious-name 条目，`decode-results.jsonl` 中有 `suspicious_name` 字段”。**实际数据中不存在该字段**（`fullrun/decode-results.jsonl` 字段为 `index,id,f1,clen,explen,status,method,keys,bounds,bconf,filename,modname,code_count,garbage,strbytes,func_names`，`status=ok` 共 4132 条）。
- 因此本次按下列规则**自行定义**可疑名，得到 **179 条**（非 177）：
  - 文件路径不匹配 `script\\...\\*.py`（3 条），或
  - `func_names` 中存在非标识符字符串（排除 `<module>`/`<lambda>` 等合法特殊名）（176 条相关）。
- 完整列表：`suspicious-names.json`（179 条，含 v4 坏名、v7 结果、分类、候选修复）。

## 1. v7 二轮重试结果

用当前 `tools/fls_batch_decoder.py`（`greedy-v7` 路径，即 v7 解码器）对 179 条重新解码，输出 `fullrun/suspicious-v7/`。

| 分类 | 条数 | 含义 |
|---|---|---|
| A. 全部函数名在“干净词表”内 | 55 | 通过验证（名字都出现在 v4-ok 条目的名字集合里） |
| B. 解码 ok，但仍含词表外名字 | 113 | 通过了 sanity 过滤，但名字可能仍有乱码 |
| C. v7 解码 fail / suspect | 11 | 6 fail（其中 2 条为 timeout-s0），5 suspect |

> **重要更正**：早先用 sanity 过滤（无非标识符字符）统计的“v7 修复 155/179”**高估**了效果。sanity 过滤无法识别“合法标识符字符但错误”的名字（如 `GS2CSJCJLtReward`、`__inifMM`、`GetWeekPbint`）。以“是否落在干净词表”为准，能确认的只有 55 条。

## 2. 抽检（24 条，人工对照 v4 坏名与 v7 结果）

| index | 分类 | v4 坏名 | v7 名字（抽样） | 判断 |
|---|---|---|---|---|
| 3083 | A | `I ':` | GetView, Init | ✅ 正确 |
| 3561 | A | `__ini\n!_` | UpdateRecordRankData, GetState | ✅ 正确 |
| 4482 | A | `\x8dª\xadt` | Init, EditInit | ✅ 正确 |
| 3140 | A | `__:=:t__` | ShowGroupTaskDlg, ModuleReset | ✅ 正确 |
| 4901 | A | `C2SOpe\r!ox` | C2SStartLottery | ✅ 正确 |
| 3260 | A | `GetMy#ata` | GetModel | ✅ 正确 |
| 3651 | A | `´«\x8c\x8b\x96` | VInit, InitSignal | ✅ 正确 |
| 1312 | A | `\x9b\x84£¤¹` | VInit, VSetFutureSubPage | ✅ 正确 |
| 1006 | B | `C2IMCanrt}\d}tiDownload` | C2IMCancelMultiDownload | ✅ 很可能正确（待对照） |
| 3645 | B | `6W&RefershBadgeLockData` | S2CRefershBadgeLockData | ❔ 拼写可能是原文 `Refersh`，无法判定 |
| 2796 | B | `DP1@QfereshSkillInfo` | GS2CQfereshSkillInfo | ❌ 应为 `Refresh`（Q/R 错一位） |
| 830 | B | `JhyZhhf]bint` | GetWeekPbint | ❌ 应为 `GetWeekPoint`（b/o 错一位） |
| 4510 | B | `^ebwTips` | SebwTips | ❌ 仍乱码 |
| 1895 | B | `bUVBUCX`QgeBtn` | RefreshPQgeBtn | ❌ 仍乱码 |
| 3000 | B | `uuCDC^u_` | __initu_ | ❌ 仍乱码 |
| 2881 | B | `C2S\r'*=or` | C2SFlavor | ❌ 疑似乱码 |
| 3654 | B | `Z{VlearSearch_Signal` | OnVlearSearch_Signal | ❌ 应为 `OnClearSearch_Signal`（疑） |
| 4566 | B | `CServerBPEE]TcankModel` | CServerBattlTcankModel | ❌ 仍乱码 |
| 660 | B | `Q UAAe{fqzWcg{bQsaw` | C2GSSwitchEquibQsaw | ❌ 仍乱码 |
| 677 | B | `GS2CSta][z_C@NKkJYFLJ` | GS2CStNrtUploadDevice | ❌ 疑似仍乱码（`StNrt` 可疑） |
| 3462 | C | `~UangeMultiItemPos` | — (timeout) | 未恢复 |
| 242 | C | `OnSelectO^line` | — (fail) | 未恢复（v4 中为 `OnSelectOnline`/`Outline` 之一，单字节错） |
| 4299 | C | 无坏名 | OnStarted, OnUpdated | ❌ 文件名前缀 `QAPipt\\` 已损坏，suspect |
| 4154 | C | `Zxi^rsiext` | GetCrsiext | ❌ 仍乱码 |

**抽检结论**：
- 分类 A 的 8 条抽样全部正确 → 词表校验可信。
- 分类 B 的 19 条抽样中仅约 2 条可判为正确 → **B 类多数仍是错误名字**，不能按“已修复”计入。
- C 类 fail/suspect 基本未恢复。

## 3. 错误形态（用于定位根因）

对 v4 坏名与其最近干净词做逐字节比较（`/tmp` 脚本，可复现），发现：
- 相当多条目与干净名只差 **1–2 个字节**（如 `OnHotBoxL=ave` ↔ `OnHotBoxLeave`，`OnSelectO^line` ↔ `OnSelectOnline`，`GetJubenDat:` ↔ `GetJubenData`），
  差异字节的 XOR 值呈单点分布，符合“段边界偏移一个字节、该字节用了相邻段的密钥”的假设。
- 另有大量条目差 10 个字节以上，说明整段密钥/边界错误，单字节修正无效。
- 这与任务书提到的“S 盒多变体/偏移”一致，但**尚未证实**，需要对单个条目做逐段密钥核对。

## 4. 候选修复（未应用，需人工确认）

`suspicious-names-repair-candidates.json`：对 118 个词表外名字，寻找长度相同、差 1–2 字节的干净词，共 33 条有候选（18 条差 1 字节，15 条差 2 字节）。例：`GetJubenDat:→GetJubenData`、`55init__→__init__`、`OnSetW43Times→OnSetWinTimes`、`GetWeekPbint→SetWeekPoint`（候选中错误，应人工确认）。**候选不是事实**，未写回任何解码结果。

## 5. 后续建议

1. 对 B 类 113 条按“单字节错误”路径做段边界再搜索（固定其余边界，只扫描名字所在段）。
2. C 类 11 条中 2 条 timeout：提高单条时限或拆分扫描。
3. 把 `suspicious` 判定改为“词表校验”而非 sanity 过滤，并在终版统计中区分 A/B/C。
