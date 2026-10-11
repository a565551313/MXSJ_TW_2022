# Agent D 客戶端技能、寵物技能、技能書、寵物主動技能列表與 Buff 異常核查報告

## 1. 執行摘要與核查範圍

本報告由 **Agent D** 依據 `server/docs/CSV_ANOMALY_ASSIGNMENTS.md` 與 `server/docs/CSV_READINESS.md` 規範完成，針對 `data/script.fls` 中與技能、寵物技能、技能書、寵物主動技能及 Buff 描述相關之 5 個目標條目進行唯讀靜態核查與跨表交叉驗證：

| `script.fls` 索引 | 模組路徑 | 目標表 | 原始狀態 (`CSV_READINESS.md`) | 核查結論分類 | 修復後狀態 |
|---:|---|---|---|---|---|
| `3205` | `script/data/petskill.py` | `DATA` (`AUTOFIGHTLIST`, `ShieldShortCutSkills`, `ICON_MAPPING`) | `blocked`：`DATA` 無法穩定恢復（`EXTENDED_ARG` 對齊錯誤 / 常數索引越界） | `confirmed_extraction_bug` + `confirmed_source_value` + `reader_limitation` | `DATA` 完整恢復 **581** 筆唯一技能 ID（字節碼含 **590** 次寫入、**9** 個重複鍵）；全表 **0** 處 CP950 錯誤 |
| `454` | `script/data/skilldata.py` | `DATA` | `blocked`：受限讀取器拒絕 `opcode 83 @3086` | `confirmed_extraction_bug` | `DATA` 完整恢復 **105** 筆門派/生活/指揮技能；同時揪出 1 處「可解碼但字元錯誤」之隱藏邊界偏移（`DATA[1006]['desc']` `'疳以'` $\to$ `'可以'`）；全表 **0** 處 CP950 錯誤 |
| `3075` | `script/data/skillbookdata.py` | `DATA` | `blocked`：受限讀取器拒絕 `opcode 70 @5626` | `confirmed_extraction_bug` | `DATA` 完整恢復 **4** 個分頁（`0: 36, 1: 36, 2: 36, 3: 68`，共 **176** 筆技能書）並修正 `DATA[3][38]['name']` (`skillid=507`, `'靈巧抵抗'`)；全表 **0** 處 CP950 錯誤 |
| `2242` | `script/data/petactiveskilldata.py` | `SKILLIDLST` | `review_needed`：`SKILLIDLST[16]` 為 `64605`（位於 `415` 與 `417` 之間） | `confirmed_extraction_bug` | 經字節層證明與 6 組獨立跨表證據交叉確認，`bounds[1]: 262 -> 264` 唯一還原 `SKILLIDLST[16] = 416`（`'水擊'`），全 **48** 個主動技能 ID 100% 映射至 `petskill.DATA` |
| `333` | `script/data/buffdata.py` | `DATA` | `review_needed`：`DATA[277]` 與 `DATA[702]` 之 `desc`/`effect` CP950 解碼失敗 | `confirmed_extraction_bug` | 修正全部 4 個分段邊界後，`DATA` 完整恢復 **432** 筆 Buff（`1..816`），除修復 `DATA[277]`（`'五感剝奪·舌...'`）與 `DATA[702]`（`'戰鬥風向；上'`）外，額外揪出 `bounds[1]=17877` 導致 Buff ID `110`（`'防護'`）靜默損毀為 `-1263225746` 之隱藏整數邊界錯誤 |

### 基線雜湊與偏移量約定

- `data/script.fls` SHA-256：`8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`
- `tools/decompiler/script_fls_keys.json` SHA-256：`43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`
- **偏移量單位約定**：
  - `payload_offset`（即 `bounds[0..3]`）：對應每個 `script.fls` 條目經 `expand_fls_Payload()` 解壓後之 5 段式 XOR 密文緩衝區 `exp` 的 0-based 字節偏移。
  - `code_offset`（即 `@at`）：對應頂層 `co_code` 字節串內的 0-based 指令字節偏移；所有頂層模組之 `co_code` 均始於 `payload_offset = 22`（17 字節 code header + `'s'` + 4 字節長度），因此頂層字節碼滿足 `payload_offset = code_offset + 22`。
- **紅線遵循聲明**：本核查全程未修改 `tools/decompiler/batch_decompile.py`、`tools/decompiler/script_fls_keys.json`、`tools/fls_batch_decoder.py` 或任何原始客戶端檔案；未執行任何解包後之遊戲腳本（無 `exec`/`eval`）；亦未將候選值寫入 `server/game_data/`。

---

## 2. 共同機制根因：為何 `script_fls_keys.json` 系統性停在 `'s'` / `'i'` 標記之後

在深入各條目之前，先說明 `tools/fls_batch_decoder.py` 產生 `co_consts` 內邊界偏移的系統性機制：

1. **字串與整數常數內部的 `marshal_progress` 平坦區**：
   `fls_batch_decoder.py` 在搜尋分段邊界 `bounds[k]` 時，以 `MarshalReader` 可成功解析的最遠位址 `marshal_progress` 作為評分函數，並由左向右（或局部半徑內）取第一個達到最高推進位址的偏移量 `b`。
   - 當真實的 XOR 分段邊界落在某個字串常數 `consts[m]`（marshal 格式為 1 字節 `'s'` `0x73` + 4 字節小端序長度 `L` + `L` 字節內容）內部時：只要候選邊界 `b` 跨過 5 字節標頭（即 `b >= header_start + 5`），無論 `b` 落在字串本體 `[header_start + 5 .. header_start + 5 + L]` 的哪個位置，前 5 字節標頭都能被前一段金鑰 `keys[k]` 正確解出長度 `L`，而字串結束後的下一個 marshal tag 已經位於下一段金鑰 `keys[k+1]` 範圍內。因此整個區間 `[header_start + 5 .. header_start + 5 + L]` 的 `marshal_progress` **完全相同**。
   - 同理，當真實邊界落在 32-bit 整數常數 `consts[m]`（1 字節 `'i'` `0x69` + 4 字節小端序整數）內部時，區間 `[tag_offset + 1 .. tag_offset + 5]` 內所有候選邊界 `b` 的 `marshal_progress` 亦完全相同。
2. **貪婪選取導致的前綴/後綴異或錯位**：
   - 若搜尋方向由小到大且以嚴格大於（`>`）更新最佳解，求解器必定停在標頭後的第一個字節 `header_start + 5`（或 `tag_offset + 1`），導致本屬於 `keys[k]` 的字串前綴或整數低位字節被誤用 `keys[k+1]` 解密（如 Entry `3205` 之 `bounds[2..3]`、Entry `454` 之 `bounds[1]`、Entry `2242` 之 `bounds[1]` 與 `bounds[3]`）。
   - 若採反向掃描（`method = 'ltr'` 中部分階段由右向左收斂），求解器則會停在下一個物件的 marshal tag 處（即 `header_start + 5 + L` 或 `tag_offset + 5`），導致本屬於 `keys[k+1]` 的字串後綴或整數高位字節被誤用 `keys[k]` 解密（如 Entry `454` 之 `bounds[2..3]`、Entry `3075` 之 `bounds[3]`、Entry `333` 之 `bounds[1..3]`）。

---

## 3. 逐項異常根因、原始字節與重現分析

### 3.1 Entry 3205：`script/data/petskill.py`（`DATA` 無法穩定恢復）

#### (1) 結論分類
- **`confirmed_extraction_bug`**：
  1. **第 2 段 XOR 金鑰錯誤（`keys[1]: 23 -> 152`）**：`script_fls_keys.json` 將 `keys[1]` 誤判為 `23` (`0x17`)，真實金鑰為 `152` (`0x98`)。
  2. **`co_code` 分段邊界微偏（`bounds[1]: 36122 -> 36123`）**：位於頂層 `co_code` 的 `at = 36100..36103`（`LOAD_CONST 33`）。
  3. **`co_consts` 字串常數邊界偏移（`bounds[2]: 54130 -> 54155`、`bounds[3]: 72108 -> 72143`）**：分別落在 `DATA[719]['desc']`（`consts[591]`）與 `DATA[4406]['desc']`（`consts[1275]`）內部。
- **`confirmed_source_value` + `reader_limitation`**：
  - 原始字節碼在構建 `DATA` 字面量時包含 **590** 次 `STORE_SUBSCR`，對應 **581** 個唯一技能 ID，其中 **9** 個技能 ID（`4573, 4574, 4575, 4576, 4577, 4578, 4579, 4581, 4236`）在源碼中重複定義了兩次；而 `server/tools/review_client_data_boundaries.py` 的 `evaluate_literals()` 規定遇到重複字典鍵時拋出 `ValueError('duplicate key ...')`，屬於受限讀取器為防範無聲覆寫而設的保護限制。

#### (2) 根因詳解與原始字節證據

1. **為何 `keys[1]` 被誤判為 `23` (`0x17`) 而非 `152` (`0x98`)**：
   - Entry 3205 解壓後長度為 `89,920` 字節，頂層 `co_code` 跨度為 `payload_offset 22..37496`（長達 `37,474` 字節）。
   - 因此整個第 2 段（`Segment 1: payload_offset 18043..36123`）**100% 位於頂層 `co_code` 字節碼內部**，完全不包含任何 `co_consts` 整數或字串標頭（在常數區內，`0x00` 因 32-bit 小端序高位補零而自然成為眾數）。
   - 在巨型字典字面量的 Python 2.5 `co_code` 中，每個技能欄位都由 `LOAD_CONST`（Duoyi Python 2.5 opcode `0x8F`）載入，出現頻率甚至略高於 `0x00` 高位字節。統計 `exp[18043:36123]` 的原始字節頻率：
     - 第 1 高頻字節：`0x17`（出現 **4,552** 次）$\to$ 真實明文為 `0x8F`（`LOAD_CONST`），滿足 `0x17 ^ 0x8F = 0x98 (152)`。
     - 第 2 高頻字節：`0x98`（出現 **4,347** 次）$\to$ 真實明文為 `0x00`（小端序參數高位字節），滿足 `0x98 ^ 0x00 = 0x98 (152)`。
   - `fls_batch_decoder.py` 的 `mode_byte()` 無條件假設各段最高頻字節對應明文 `0x00`，遂將 `0x17 ^ 0x00 = 23` 誤當作 `keys[1]`，使得整個 `Segment 1`（`18,080` 字節的 `co_code`）全部被多異或了 `0x8F`（`23 ^ 152 = 0x8F`）！

2. **為何不同解析路徑分別報「`EXTENDED_ARG` 位於無參數指令前」或「常數索引越界」**：
   - 在錯誤金鑰 `keys[1] = 23` 下，`Segment 1` 內所有明文 `0x00` 被解為 `0x8F`（Duoyi Py2.5 `LOAD_CONST`，轉譯後為標準 Py2.5 `100`），而所有明文 `0x8F`（`LOAD_CONST`）被解為 `0x00`（`STOP_CODE`）。
   - 在 `payload_offset = 18043`（`code_offset = 18021`）處：
     ```text
     payload 18043..18054 原始密文: 05 17 03 9b 98 a8 96 17 85 98 c6 17
     以錯誤 keys[1]=23  解密明文: 12 00 14 8c 8f bf 81 00 92 8f d1 00
     以正確 keys[1]=152 解密明文: 9d 8f 9b 03 00 30 0e 8f 1d 00 5e 8f
     ```
   - 在錯誤明文下，`code_offset = 18021` 的首字節為 `0x12 < 0x5F`（1 字節無參數指令），接著 `18022` 為 `0x00`（1 字節），`18023` 為 `0x14`（1 字節），到了 `18024` 遇到 `0x8C >= 0x5F`——在 `PY25_MAP` 中 `0x8C` 是未映射 opcode！
   - `batch_decompile.py` 的 `transpile_py25_code()` 遇到未知帶參數 opcode (`>= 0x5F`) 時，**只向輸出緩衝區寫入 1 個字節的 `NOP (9)`，卻將輸入指標 `i` 前進了 3 個字節（`i += 3`）**，導致輸出 `co_code` 長度縮水並破壞後續所有指令的 3-byte 對齊！到了原始 `18031`（縮水後 `@18025`），字節 `0xD1` 被 `PY25_MAP[0xD1] = 143` 轉譯為 `EXTENDED_ARG (143)`，其後緊跟由 `0x8F` 變成的 `0x00`（無參數指令），因此 `review_client_data_boundaries.py` 的 `instructions()` 立即拋出：
     `ValueError: EXTENDED_ARG before opcode without argument at 18025`。
   - 若不經由 `NOP` 縮水而直接按 3-byte 步進掃描 `LOAD_CONST`，則原本的小端序高位 `0x00` 已被翻轉為 `0x8F`，組合出如 `49034 >= len(consts) (1639)` 的 16-bit 常數索引，觸發常數索引越界。

3. **4 個分段邊界的精確定位**：
   - **`bounds[0] = 18043`（已精確，無需調整）**：
     位於頂層 `co_code` `at = 18021`（`STORE_SUBSCR` `0x9D` 首字節）：
     - `18040..18042` (`at = 18018..18020`)：密文 `43 cd cc` $\oplus$ `k0(204)` = `8f 01 00` $\to$ `LOAD_CONST 1` (`'type'`)。
     - `18043..18046` (`at = 18021..18024`)：密文 `05 17 9b 98` $\oplus$ `k1(152)` = `9d 8f 03 00` $\to$ `STORE_SUBSCR (60)`、`LOAD_CONST 3` (`'desc'`)。
   - **`bounds[1]: 36122 -> 36123`（`co_code` `at = 36100..36101`）**：
     - `36121` (`at = 36099`)：密文 `0x17` $\oplus$ `k1(152)` = `0x8F`（`LOAD_CONST`）。
     - `36122` (`at = 36100`)：密文 `0xB9` $\oplus$ `k1(152)` = `0x21 (33)`（若誤用 `k2(122)` 則為 `0xC3 (195)`）。
     - `36123` (`at = 36101`)：密文 `0x7A` $\oplus$ `k2(122)` = `0x00`（`LOAD_CONST 33` 之高字節，`consts[33] = 0`）。
     - 在此位置（構建 `DATA[4571]` `'極度狂暴'` 的 `'fpneed'` 欄位），所有標準技能模板均以 `consts[33]` (`'0'`) 賦值予 `'fpneed'`（當 `b1=36122` 時會誤載入 `consts[195] = 152` 作為 `'fpneed'`）。因此 `bounds[1] = 36123` 唯一正確。
   - **`bounds[2]: 54130 -> 54155`（`consts[591]`，`DATA[719]['desc']`，技能 `'念動力'`）**：
     - `consts[591]` 跨度為 `payload_offset [54125..54220)`（5 字節標頭 `54125..54129` + 90 字節 CP950 字串 `54130..54219`）。
     - 已保存之 `bounds[2] = 54130` 停在標頭後第 1 字節，導致前 25 字節 (`54130..54154`) 被誤用 `k3(74)` 解密而產生亂碼。
     - 掃描 `[54130..54220]` 發現僅 `54155` 與 `54156` 可使 90 字節完整通過 CP950 解碼：
       - `54155`（位於雙字節字元 `'禁'` `0xB8 0x54` 的兩個字節之間：`exp[54154]=0xC2 ^ 122 = 0xB8`、`exp[54155]=0x1E ^ 74 = 0x54`）：解出 `'星界十二宮星帝才配使用的禁技，白羊星的絕招；目標會受強大的念力影響，處於癲狂狀態，敵我不分'`。
       - `54156`：將 `exp[54155]=0x1E` 以 `122` 解密為 `0x64`（`0xB8 0x64` = `'粱'`），解出 `'...使用的粱技...'`。
       - 對照同系列 `DATA[720]` (`consts[594]`)、<i>`DATA[721]`</i> (`consts[597]`)、<i>`DATA[723]`</i> (`consts[603]`) 均以固定前綴 `'星界十二宮星帝才配使用的禁技，'` 開頭，**100% 確認 `bounds[2] = 54155`**。
   - **`bounds[3]: 72108 -> 72143`（`consts[1275]`，`DATA[4406]['desc']`，技能 `'影魂吸收'`）**：
     - `consts[1275]` 跨度為 `payload_offset [72103..72170)`（5 字節標頭 `72103..72107` + 62 字節 CP950 字串 `72108..72169`）。
     - 已保存之 `bounds[3] = 72108` 停在標頭後第 1 字節。測試區間內僅 `72143` 產生語義完整之正體中文：`'每回合檢查場上是否有影魂存在，如果有影魂，則在下回合末吸收影魂'`（與相鄰技能 `DATA[4405]` `'影魂召喚'`、<i>`DATA[4407]`</i> `'影魂自爆'` 完全呼應）。

4. **源碼中 `DATA` 字面量的 9 個重複技能 ID（`confirmed_source_value`）**：
   在 `co_code` 偏移 `at = 21779..22283` 與 `at = 22409..22913`（兩段之間夾著 `4580` 與 `4582: '真龍之拳'`），源碼連續兩次寫入了以下 9 個技能 ID：

   | 技能 ID | 第一次寫入 (`at=21779..22283`) | 第二次寫入 (`at=22409..22913`，Python 字典最終生效值) | 差異說明 |
   |---:|---|---|---|
   | `4573` | `name='天魔返生術'`, `type=1`, `desc='復活倒地目標，且本回合目標處於絕對防禦狀態，不會受到任何傷害及正面、負面的狀態'` | `name='地魔返生術'`, `type=1`, `desc='復活倒地目標，且本回合目標處於絕對防禦狀態，不會受到任何傷害及正面、負面的狀態'` | **僅 `name` 由 `'天魔返生術'` 覆寫為 `'地魔返生術'`**（分別引用 `consts[1044]` 與 `consts[1074]`） |
   | `4574` | `name='修羅魔靈'`, `type=1` | `name='修羅魔靈'`, `type=1` | 完全相同 |
   | `4575` | `name='天魔解體'`, `type=1` | `name='天魔解體'`, `type=1` | 完全相同 |
   | `4576` | `name='如來神掌'`, `type=1` | `name='如來神掌'`, `type=1` | 完全相同 |
   | `4577` | `name='天佛降世'`, `type=0` | `name='天佛降世'`, `type=0` | 完全相同 |
   | `4578` | `name='狂魔戰氣'`, `type=0` | `name='狂魔戰氣'`, `type=0` | 完全相同 |
   | `4579` | `name='真龍之血'`, `type=0` | `name='真龍之血'`, `type=0` | 完全相同 |
   | `4581` | `name='滅世龍炎'`, `type=1` | `name='滅世龍炎'`, `type=1` | 完全相同 |
   | `4236` | `name='順風連斬'`, `type=1` | `name='順風連斬'`, `type=1` | 完全相同 |

---

### 3.2 Entry 454：`script/data/skilldata.py`（`opcode 83 @3086` 阻斷與隱藏錯字）

#### (1) 結論分類
- **`confirmed_extraction_bug`**：全部 4 個分段邊界 `bounds=[3106, 6232, 9375, 12446]` 均有偏移，修正為 `bounds=[3108, 6233, 9356, 12506]`（搭配 `use_solver=False`）後，**105** 筆門派/生活/指揮技能完整恢復，且揪出 1 處基線下不報錯但字元錯誤的隱藏邊界問題。

#### (2) 根因詳解與原始字節證據
1. **`bounds[0]: 3106 -> 3108`（修復 `opcode 83 @3086`）**：
   - `co_code` 跨度為 `payload_offset 22..3839`。在 `payload_offset 3105..3111` (`code_offset 3083..3089`) 處：
     ```text
     payload 3105..3111 原始密文: fc 51 fc 99 1c 17 26
     k0 = 204 (0xCC), k1 = 22 (0x16)
     3105 (at=3083): 0xFC ^ 0xCC = 0x30 -> DUP_TOP (4)
     3106 (at=3084): 0x51 ^ 0xCC = 0x9D -> STORE_SUBSCR (60)   [若誤用 k1=22 則為 0x47 -> 71]
     3107 (at=3085): 0xFC ^ 0xCC = 0x30 -> ROT_TWO (2)        [若誤用 k1=22 則為 0xEA -> 234]
     3108 (at=3086): 0x99 ^ 0x16 = 0x8F -> LOAD_CONST (100)   [若誤用 k0=204 則為 0x55 -> RETURN_VALUE (83)!]
     3109 (at=3087): 0x1C ^ 0x16 = 0x0A -> lo_arg = 10
     3110 (at=3088): 0x17 ^ 0x16 = 0x01 -> hi_arg = 1 (arg = 266, consts[266] = 2403 '武學')
     ```
   - `script_fls_keys.json` 保存為 `3106`；而 `solve_py25_co_span()` 自動求解器則將邊界過度右移至 `3109`，使 `3108` (`at=3086`) 被 `k0=204` 解為 `0x55` (`RETURN_VALUE = 83`)，導致受限讀取器在 `@3086` 因遇到 `opcode 83` 而中止。將 `bounds[0]` 設為 `3108` 即可精確還原 `STORE_SUBSCR; ROT_TWO; LOAD_CONST 266`。
2. **`bounds[1]: 6232 -> 6233`（揪出隱藏無報錯錯字：`DATA[1006]['desc']` `'儒學理論'`）**：
   - `consts[67]` 跨度為 `[6227..6296)`（5 字節標頭 `6227..6231` + 64 字節字串 `6232..6295`）。
   - `script_fls_keys.json` 停在標頭後第 1 字節 `6232`：
     - `exp[6232..6233] = 0xB3 0x75`。
     - 在已保存 `bounds[1] = 6232` 下，`exp[6232]` 被誤用 `k2 = 28 (0x1C)` 解密為 `0xB3 ^ 0x1C = 0xAF`，與下一字節 `0x75 ^ 0x1C = 0x69` 組成合法 CP950 雙字節字元 **`'疳'` (`0xAF69`)**，使整個字串解為：
       `'疳以提升儒系招式的威力及封印效果，同時也是學習高級儒系招式的基礎'`（**完全不觸發 CP950 解碼錯誤，但首字錯為「疳」**）！
     - 當修正為 `bounds[1] = 6233` 時，`exp[6232]` 由 `k1 = 22 (0x16)` 解密為 `0xB3 ^ 0x16 = 0xA5`，與 `0x69` 組成 **`'可'` (`0xA569`)**，還原為 `'可以提升儒系招式的威力及封印效果，同時也是學習高級儒系招式的基礎'`（與同表 `DATA[1001..1011]` 其他流派主技能描述 `'可以提升...系招式的威力...'` 完全一致）。
3. **`bounds[2]: 9375 -> 9356`（修復 `consts[148]`，`DATA[2254]['desc']` `'抗法修煉'`）**：
   - `consts[148]` 跨度為 `[9331..9402)`（標頭 `9331..9335` + 66 字節字串 `9336..9401`）。已保存之 `9375` 導致中段亂碼；修正為 `9356` 後唯一還原為 `'學習後，每級可以使受到的法術傷害結果降低2%+5並且被封印成功率降低2%'`。
4. **`bounds[3]: 12446 -> 12506`（修復 `consts[286]`，`DATA[2018]['desc']` `'追捕'`）**：
   - `consts[286]` 跨度為 `[12433..12543)`（標頭 `12433..12437` + 105 字節字串 `12438..12542`）。修正為 `12506` 後還原為 `'【效果】擔任隊長時，可以在戰鬥中降低對方逃跑的成功率；技能等級越高，降低得越多#r【消耗】每級消耗4個劇情點'`。

---

### 3.3 Entry 3075：`script/data/skillbookdata.py`（`opcode 70 @5626` 阻斷）

#### (1) 結論分類
- **`confirmed_extraction_bug`**：`bounds[1]` (`5648 -> 5650`) 落在 `co_code` 內造成指令損毀；`bounds[2]` (`8450 -> 8440`) 落在 `GetSkillByID.co_lnotab`；`bounds[3]` (`11279 -> 11276`) 落在 `consts[340]` (`DATA[3][38]['name']`) 造成 CP950 亂碼。修正為 `bounds=[2805, 5650, 8440, 11276]`（搭配 `use_solver=False`）後完整恢復 **176** 筆技能書。

#### (2) 根因詳解與原始字節證據
1. **`bounds[0] = 2805`（已精確；注意 `solve_py25_co_span` 會誤移至 `2804`）**：
   - `2802..2804` (`at=2780..2782`) 在 `k0=210` 下為 `0xBB 0x00 0x00`（`BUILD_MAP 0`），`2805` (`at=2783`) 在 `k1=214` 下為 `0x30`（`DUP_TOP`）。若開啟 `solve_py25_co_span`，求解器會誤將 `2804` 歸入 `k1=214` 而變成 `BUILD_MAP 1024`。因此 `bounds[0]` 必須保持 `2805`。
2. **`bounds[1]: 5648 -> 5650`（修復 `opcode 70 @5626`）**：
   - 在 `payload_offset 5648..5652` (`code_offset 5626..5630`) 處：
     ```text
     payload 5648..5652 原始密文: 4b e6 0f 5d 80
     k1 = 214 (0xD6), k2 = 128 (0x80)
     5648 (at=5626): 0x4B ^ 0xD6 = 0x9D -> STORE_SUBSCR (60)  [若誤用 k2=128 則為 0xCB -> PRINT_EXPR (70)!]
     5649 (at=5627): 0xE6 ^ 0xD6 = 0x30 -> ROT_TWO (2)        [若誤用 k2=128 則為 0x66 -> SLICE+0 (30)!]
     5650 (at=5628): 0x0F ^ 0x80 = 0x8F -> LOAD_CONST (100)
     5651 (at=5629): 0x5D ^ 0x80 = 0xDD -> lo_arg = 221
     5652 (at=5630): 0x80 ^ 0x80 = 0x00 -> hi_arg = 0 (consts[221] = 28 '高級破魔')
     ```
   - 已保存之 `5648` 提早 2 字節切換至 `k2=128`，將 `STORE_SUBSCR (60), ROT_TWO (2)` 損毀為 `PRINT_EXPR (70), SLICE+0 (30)`，觸發 `opcode 70 @5626`。修正為 `5650` 即完全恢復。
3. **`bounds[2]: 8450 -> 8440`（修復嵌套函數 `consts[1]` `GetSkillByID.co_lnotab`）**：
   - `8440..8449` 位於 `GetSkillByID` 的行號表 `co_lnotab` 尾部；`b2=8440` 將其還原為合法單調遞增對 `00010d000c010d000c0111011001`。
4. **`bounds[3]: 11279 -> 11276`（修復 `consts[340]`，`DATA[3][38]['name']`）**：
   - `consts[340]` 跨度為 `[11266..11279)`（標頭 `11266..11270` + 8 字節字串 `11271..11278`）。已保存之 `11279` 將末 3 字節 `11276..11278` (`0xFB 0xF1 0x33`) 誤用 `k3=27 (0x1B)` 解密為亂碼 `e0 ea 28`；改用 `b3=11276` 以 `k4=87 (0x57)` 解密即得 `a4 a6 64`，與前 5 字節合為 `'靈巧抵抗'` (`c6 46 a5巧 a6 f8 a6 64`)，且與同筆記錄之 `skillid = 507` 在 `petskill.DATA[507]['name'] == '靈巧抵抗'` **100% 吻合**。

---

### 3.4 Entry 2242：`script/data/petactiveskilldata.py`（`SKILLIDLST[16]` `64605` vs `416`）

#### (1) 結論分類
- **`confirmed_extraction_bug`**：`SKILLIDLST[16]` 在 `script_fls_keys.json` 基線下解出 `64605` 係因 `bounds[1] = 262` 停在 `consts[16]` 的 `'i'` 標記之後第 1 字節，使低位 2 字節 (`262..263`) 被誤用 `k2=14` 而非 `k1=243` 解密。將 `bounds[1]` 修正為 `264` 後，唯一解出 `416`（`'水擊'`），並由字節層結構與 6 項跨表證據共同確認。

#### (2) 原始字節證明：為何 `bounds[1] = 264` 是唯一合法整數邊界
Entry 2242 解壓後長 `611` 字節，`consts[16]` 位於 `payload_offset [261..266)`（1 字節 `'i'` + 4 字節小端序整數 `262..265`）：

```text
Offset  RawHex  ^k1(243=0xF3)  ^k2(14=0x0E)   說明
------  ------  -------------  ------------   ------------------------------------------------
256     0x9A    0x69 ('i')     0x94           consts[15] 標記 ('i')
257     0x6C    0x9F           0x62           consts[15] byte 0 \
258     0xF2    0x01           0xFC           consts[15] byte 1  |-> 0x0000019F = 415 ('亂舞衝擊')
259     0xF3    0x00           0xFD           consts[15] byte 2  |
260     0xF3    0x00           0xFD           consts[15] byte 3 /
261     0x9A    0x69 ('i')     0x94           consts[16] 標記 ('i') —— 必須屬於 Segment 1 (k1=243)
262     0x53    0xA0           0x5D           consts[16] byte 0 (LSB)
263     0xF2    0x01           0xFC           consts[16] byte 1
264     0x0E    0xFD           0x00           consts[16] byte 2 —— 原始密文為 0x0E = k2，明文必為 0x00！
265     0x0E    0xFD           0x00           consts[16] byte 3 —— 原始密文為 0x0E = k2，明文必為 0x00！
266     0x67    0x94           0x69 ('i')     consts[17] 標記 ('i') —— 必須屬於 Segment 2 (k2=14)
267     0xAF    0x5C           0xA1           consts[17] byte 0 \
268     0x0F    0xFC           0x01           consts[17] byte 1  |-> 0x000001A1 = 417 ('火攻')
269     0x0E    0xFD           0x00           consts[17] byte 2  |
270     0x0E    0xFD           0x00           consts[17] byte 3 /
```

請注意 `offset 264..265` 的原始密文字節為 `0x0E 0x0E`（恰好等於 `k2 = 14 = 0x0E`），證明 Duoyi 打包器加密時第 2 與第 3 段的真實切分點**正是 `offset = 264`**（使高位兩字節 `0x00 0x00` 經 `k2=0x0E` 加密為 `0x0E 0x0E`）。窮舉 `consts[16]` 內部所有可能邊界 `b1 in [261..266]`：

| 候選 `bounds[1]` | `consts[16]` 解密後 4 字節 (LE) | 對應 32-bit 有號整數 | 評估結果 |
|---:|---|---:|---|
| `261` | 標記 `0x9A ^ 0x0E = 0x94` | Marshal 失敗 | 非法 marshal tag |
| `262` (已保存值) | `5d fc 00 00` | `64605` (`0x0000FC5D`) | 低位 2 字節 (`262..263`) 被誤用 `k2=14` 解密（多異或了 `243 ^ 14 = 0xFD`） |
| `263` | `a0 fc 00 00` | `64672` (`0x0000FCA0`) | `offset 263` (`0xF2`) 被誤用 `k2=14` 解密為 `0xFC` |
| **`264` (真實邊界)** | **`a0 01 00 00`** | **`416` (`0x000001A0`)** | **低位 `262..263` 用 `k1=243` 解出 `0x01A0`，高位 `264..265` 用 `k2=14` 解出 `0x0000`** |
| `265` | `a0 01 fd 00` | `16581024` (`0x00FD01A0`) | 高位 `264` 被誤用 `k1=243` 解密為 `0xFD` |
| `266` | `a0 01 fd fd` | `-33750624` (`0xFDFD01A0`) | 高位 `264..265` 均被誤用 `k1=243` 解密為 `0xFD 0xFD` |

（此外，Entry 2242 末尾 `co_lnotab` `[512..611)` 亦有一處不影響資料的 `bounds[3]: 517 -> 529` 與 `keys[4]: 230 -> 229` 偏移：因 `co_lnotab` 內容為 47 組重複的 `03 01`，偶數位字節密文 `0x03 ^ 229 = 0xE6 (230)` 被 `mode_byte` 誤判為 `0x00 ^ 230`。）

#### (3) 六項獨立跨表證據確認 `SKILLIDLST[16] = 416`（`'水擊'`）
除鄰號外，以下 6 個獨立模組均在未受邊界干擾的常數區直接引用 `416`：
1. **`petskill.DATA`（Entry 3205）**：`64605` 在 `petskill.DATA` 中不存在；而 `416` 為 `'水擊'`（`type = 1` 主動技能，`'單體法術攻擊，對目標造成智系法術傷害（可綁定技能），消耗法力15+LV/3'`），與 `417` `'火攻'`、`418` `'神罰'`、`419` `'落雷'`、`420` `'念力飛彈'`、`421` `'精神打擊'`、`422` `'亡靈氣箭'`、`423` `'鬼爪飛擊'`、`424` `'妖氣纏繞'`、`425` `'魔刃投擲'` 共同組成 5 系 × 2 招共 10 招單體基礎寵物法術（`416..425`）。
2. **`petskill.AUTOFIGHTLIST`（Entry 3205）**：自動戰鬥可用主動寵物技能列表（共 37 項）明文包含 `416`：`[407, 408, 409, 410, 411, 413, 414, 415, 416, 417, 418, ..., 581]`。當 `SKILLIDLST[16] = 416` 時，`AUTOFIGHTLIST` 37 項為 `SKILLIDLST` 48 項之嚴格子集（`set(AUTOFIGHTLIST) <= set(SKILLIDLST)`）。
3. **`skillbookdata.DATA`（Entry 3075）**：`DATA[3][12]` 明文定義 `{'name': '水擊', 'skillid': 416, '結晶積分': 2, '勛章積分': 10}`，與 `DATA[3][13..21]` (`417..425`) 連續排列。
4. **`petclashskilldata.DATA_CLASH`（Entry 1762）**：寵物技能衝突表 `DATA_CLASH[416] = [109, 209, 309]`，且 `DATA_CLASH[109/209/309]` 的衝突列表均包含 `416`。
5. **`rideskillrecdata.DATA`（Entry 2400）**：坐騎技能推薦表在 `'法師'` 與 `'戰士'` 的 `'單人競技'`、`'組隊競技爆發'` 方案中均明文配置 `{'iMain': 305, 'iSub1': 416, 'iSub2': 417}`。
6. **`warui.GetUseActiveSkill`（Entry 1080）**：戰鬥 UI 以 `if skill in petactiveskilldata.SKILLIDLST:` 過濾召喚獸已學技能 `oPet.GetSkill()`（其元素即 `petskill.DATA` 之技能 ID），若 `416` 變成 `64605`，學習了 `'水擊'` (`416`) 的召喚獸在戰鬥中將無法將 `'水擊'` 識別為主動技能。

---

### 3.5 Entry 333：`script/data/buffdata.py`（`DATA[277]`、`DATA[702]` CP950 失敗與隱藏整數損毀）

#### (1) 結論分類
- **`confirmed_extraction_bug`**：`script_fls_keys.json` 保存之 4 個邊界 `bounds=[8960, 17877, 26838, 35718]` **全部存在偏移**！除修復任務指派的 `DATA[277]` (`bounds[2]: 26838 -> 26798`) 與 `DATA[702]` (`bounds[3]: 35718 -> 35714`) 外，還發現並修復了 `bounds[0]: 8960 -> 8961`（`co_code` 指令參數邊界）與 **`bounds[1]: 17877 -> 17874`（隱藏整數邊界錯誤，原本將 Buff ID `110` `'防護'` 靜默損毀為 `-1263225746`）**。

#### (2) 根因詳解與原始字節證據
1. **`bounds[0]: 8960 -> 8961`（`co_code` `at = 8938..8939`）**：
   - `8959..8961` (`at = 8937..8939`) 為指令 `LOAD_CONST 12` (`consts[12] = 'desc'`)：
     - `8959`: `0x9B ^ k0(20) = 0x8F` (`LOAD_CONST`)
     - `8960`: `0x18 ^ k0(20) = 0x0C (12)`（若誤用 `k1=214` 則變為 `0xCE = 206`，把欄位名 `'desc'` 錯變成整數 `198`！）
     - `8961`: `0xD6 ^ k1(214) = 0x00` (`hi_arg = 0`)
   - 故 `bounds[0]` 真實值為 `8961`（基線調查時因 `solve_py25_co_span` 自動修正了 `co_code` 邊界才未報錯）。
2. **`bounds[1]: 17877 -> 17874`（重大隱藏錯誤：Buff ID `110` 被靜默損毀為 `-1263225746`）**：
   - `consts[84]` 位於 `payload_offset [17872..17877)`（1 字節 `'i'` + 4 字節小端序整數 `17873..17876`），緊接著 `17877` 是 `consts[85]` 的 `'s'` 標記：
     ```text
     Offset  RawHex  ^k1(214=0xD6)  ^k2(98=0x62)   說明
     ------  ------  -------------  ------------   -----------------------------------------
     17872   0xBF    0x69 ('i')     0xDD           consts[84] 標記 ('i') —— 必屬 Segment 1 (k1=214)
     17873   0xB8    0x6E (110)     0xDA (218)     consts[84] byte 0 (LSB)
     17874   0x62    0xB4           0x00           consts[84] byte 1 —— 密文 0x62 = k2，明文必為 0x00！
     17875   0x62    0xB4           0x00           consts[84] byte 2 —— 密文 0x62 = k2，明文必為 0x00！
     17876   0x62    0xB4           0x00           consts[84] byte 3 —— 密文 0x62 = k2，明文必為 0x00！
     17877   0x11    0xC7           0x73 ('s')     consts[85] 標記 ('s') —— 必屬 Segment 2 (k2=98)
     ```
   - 已保存之 `bounds[1] = 17877` 將 `17873..17876` 全部歸入 `k1 = 214`，使高 3 字節 `0x62 0x62 0x62` 解為 `0xB4 0xB4 0xB4`，產生荒謬負數 `-1263225746` (`0xB4B4B46E`)，卻因整數不需通過 CP950 檢查而在基線調查中完全潛伏！
   - 對比 `b1 = 17873` (`218`，與 `consts[282] = 218` 衝突) 與 **`b1 = 17874` (`110`)**：前後常數依序為 `consts[78] = 108` (`堅固`)、`consts[81] = 109` (`防護`)、**`consts[84] = 110`**、<i>`consts[86] = 111`</i> (`抗魔`)、<i>`consts[89] = 112`</i> (`庇佑`)。因此 **`bounds[1] = 17874` 唯一精確到字節**，將 `DATA[-1263225746]` 恢復為 `DATA[110] = {'desc': '防護；受物理類傷害降低', 'effect': '防護；受物理類傷害降低，目標等級越高減傷效果越低。'}`。
3. **`bounds[2]: 26838 -> 26798`（修復 `consts[406]`，即 `DATA[277]['desc']` 與 `DATA[277]['effect']`）**：
   - Python 編譯器對 `DATA[277]` 的 `'desc'` 與 `'effect'` 複用了同一個字串常數槽 `consts[406]`（跨度 `[26771..26838)`，標頭 `26771..26775` + 62 字節字串 `26776..26837`）。
   - 已保存之 `bounds[2] = 26838` 停在下一個常數 `consts[407]` 的 `'i'` 標記處，導致 `consts[406]` 的後 40 字節 (`26798..26837`) 被誤用 `k2=98` 而非 `k3=197` 解密。
   - 修正為 `bounds[2] = 26798` 後，62 字節完整還原為：
     `'五感剝奪·舌；與五感剝奪·眼、耳、鼻、身同時存在時，將立即死亡'`（與相鄰 `DATA[274..278]` 之 `'五感剝奪·眼/耳/鼻/舌/身'` 系列格式 **100% 一致**）。
4. **`bounds[3]: 35718 -> 35714`（修復 `consts[721]`，即 `DATA[702]['desc']` 與 `DATA[702]['effect']`）**：
   - `DATA[702]` 的 `'desc'` 與 `'effect'` 複用同一個字串常數槽 `consts[721]`（跨度 `[35701..35718)`，標頭 `35701..35705` + 12 字節字串 `35706..35717`）。
   - 已保存之 `bounds[3] = 35718` 停在 `consts[722]` 的 `'i'` 標記處，導致末 4 字節 (`35714..35717`, 原始密文 `83 68 86 4D`) 被誤用 `k3=197 (0xC5)` 解密為 `46 ad 43 88`（亂碼）。
   - 修正為 `bounds[3] = 35714` 後，末 4 字節由 `k4=34 (0x22)` 解密為 `a1 4a a4 57`（`'；上'`），完整字串還原為：
     `'戰鬥風向；上'`（與緊鄰之 `DATA[703]` `'戰鬥風向；下'`、`DATA[704]` `'戰鬥風向；左'`、`DATA[705]` `'戰鬥風向；右'` 構成完整上下左右四向風向 Buff）。

---

## 4. 主表恢復後之跨表一致性與映射核查

在恢復上述 5 張表後，我們依據任務要求對技能 ID 唯一性、名稱與 ID 對應、同名技能/別名、主動技能列表引用，以及 Agent C 寵物/怪物/子女表之技能映射進行全面核查：

### 4.1 技能 ID 唯一性核查

| 條目與模組 | 表名 | 字節碼寫入次數 | 唯一鍵數量 | ID 範圍 | 唯一性結論 |
|---|---|---:|---:|---|---|
| `3205` `petskill.py` | `DATA` | 590 | **581** | `101 .. 45432` | 源碼字面量含 **9** 個重複鍵（`4573..4579, 4581, 4236`），其中 `4573` 之 `name` 由 `'天魔返生術'` 被覆寫為 `'地魔返生術'`，其餘 8 筆完全相同 |
| `454` `skilldata.py` | `DATA` | 105 | **105** | `1001 .. 9202` | **100% 唯一**（無重複鍵；與 `petskill.DATA` 之整數 ID 集合交集為空集 $\emptyset$） |
| `3075` `skillbookdata.py` | `DATA` | 176 (`0:36, 1:36, 2:36, 3:68`) | **176** | 分頁索引 `1..36` / `1..68`；`skillid` `101..584` | **100% 唯一**（跨 4 個分頁共 176 筆記錄之 `skillid` 無任何重複，且 176 個 `skillid` 100% 存在於 `petskill.DATA`） |
| `2242` `petactiveskilldata.py` | `SKILLIDLST` | 48 | **48** | `109 .. 581` | **100% 唯一**（修正 `SKILLIDLST[16]=416` 後，48 個 ID 無重複且 100% 存在於 `petskill.DATA`） |
| `333` `buffdata.py` | `DATA` | 432 | **432** | `1 .. 816` | **100% 唯一**（修正 `bounds[1]=17874` 還原鍵 `110` 後，432 個正整數 Buff ID 無重複） |

### 4.2 技能名稱與 ID 對應、同名技能與別名核查

#### (1) `petskill.DATA` 內部同名技能（581 個技能 ID 對應 **515** 個唯一名稱）
共有 **39** 組技能名稱在 `petskill.DATA` 中對應多個技能 ID，按成因可嚴格分為 3 類：

1. **普通寵物技能 vs 幻化技能（2 組，影響標準寵物技能名稱映射）**：
   - `'高級命中'`：對應 `[229, 255]`。其中 `229` 為標準高級獸訣技能（`skillbookdata.DATA[1][33]['skillid'] == 229`），而 `255` 為幻化技能（`petskill.ICON_MAPPING[255] == 229`；其他幻化技能如 `155` `'命中·幻化'`、`296` `'高級慧根·幻化'` 均帶 `'·幻化'` 後綴，唯獨 `255` 與 `355` 在 `petskill.DATA` 中漏寫 `'·幻化'` 後綴）。
   - `'終級命中'`：對應 `[329, 355]`。其中 `329` 為標準終級獸訣技能（`skillbookdata.DATA[2][33]['skillid'] == 329`），而 `355` 為幻化技能（`petskill.ICON_MAPPING[355] == 329`）。
2. **內丹/特殊寵物技能 (`437..571`) vs 坐騎/天賦技能 (`6111..6121`)（4 組）**：
   - `'迅敏'`：`437`（內丹：`'增加等級*0.6+20點速度'`）vs `6111`（天賦：`'增加LV*0.15+10速度'`）
   - `'氣勢'`：`440`（內丹：`'出戰前2回合，物理或法術傷害結果提高20%...'`）vs `6113`（天賦：`'前2次出手的傷害結果提高10%'`）
   - `'無畏'`：`567`（內丹：`'擁有此技能的召喚獸存活時，主人被恐怖的概率下降5%'`）vs `6116`（天賦：`'召喚獸擁有勇敢技能時，主人被恐怖的概率降低5%'`）
   - `'厄運'`：`571`（內丹：`'單體攻擊時，對擁有幸運、高級幸運和終級幸運的召喚獸...'`）vs `6121`（天賦：`'攻擊擁有幸運類技能的目標，傷害結果提高6%'`）
3. **Boss / 副本怪物專用多階段技能（33 組，ID $\ge 723$）**：
   - 雙 ID 重複（6 組）：`'五感剝奪'` (`[723, 724]`)、`'順風連斬'` (`[4236, 4583]`)、`'左·大殺四方 '` (`[4369, 4640]`，源碼含尾隨空白)、`'右·熾炎地獄'` (`[4370, 4641]`)、`'狂·十方俱滅'` (`[4371, 4643]`)、`'狂·天魔誅絕'` (`[4372, 4644]`)。
   - 三難度 `(X, X*10+1, X*10+2)` 副本 Boss 技能（27 組）：`4133..4146`（`'橫掃六合'`, `'焚書坑儒'`, `'亂舞春秋'`, `'仁義天下'`, `'坑殺八荒'`, `'指鹿為馬'`, `'挑拔離間'`, `'合縱天下'`, `'過關斬將'`）及 `4509..4543`（`'幽暗審判'`, `'冥府震怒'`, `'主宰的制裁'`, `'沙塵爆轟'`, `'怨念轟擊'`, `'天隕之罰'`, `'流沙風暴'`, `'沙之荊棘'`, `'地火之罰'`, `'聖甲蟲之觸'`, `'烈日的灼燒'`, `'耀光術'`, `'尼羅河腐水'`, `'法老的毒酒'`, `'公正的稱量'`, `'偏心的稱量'`, `'罪孽吞噬'`, `'黃龍之怒'`）。

#### (2) `skilldata.DATA` 與 `petskill.DATA` 之同名跨表技能
- `skilldata.DATA` 內部 105 筆技能之 `name` **100% 唯一**（無重複名稱）。
- `skilldata.DATA` 與 `petskill.DATA` 有 **5** 個同名但不同命名空間的技能（ID 完全不重疊）：
  - `'必殺'`（人物 `1115` vs 寵物 `104`）、`'連擊'`（人物 `1326` vs 寵物 `102`）、`'神祐'`（人物 `1417` vs 寵物 `103`）、`'精準'`（人物 `2206` vs 寵物 `439`）、`'奇門遁甲'`（人物劇情技能 `2012` vs Boss 技能 `4211`）。

#### (3) `skillbookdata.DATA` 與 `petskill.DATA` 間的 3 組同音異字別名（`confirmed_source_value`）
全 176 筆技能書透過 `skillid` 與 `petskill.DATA` 100% 精確對應，其中 173 筆之 `name` 字串完全一致，僅 **3** 筆存在源碼級同音異字（別名）：

| 分頁與序號 | `skillid` | `skillbookdata.DATA` 名稱 | `petskill.DATA` 名稱 | 差異字元 |
|---|---:|---|---|---|
| `DATA[2][35]` (終級獸決) | `358` | `'終極法術狂暴'` | `'終級法術狂暴'` | `'極'` vs `'級'` |
| `DATA[3][22]` (特殊獸決) | `426` | `'烈焰爆破'` | `'烈炎爆破'` | `'焰'` vs `'炎'` |
| `DATA[3][33]` (特殊獸決) | `402` | `'偵查'` | `'偵察'` | `'查'` vs `'察'` |

### 4.3 主動技能列表與相關技能表引用關係核查

1. **`petactiveskilldata.SKILLIDLST`（Entry 2242，48 項）與 `petskill.py`（Entry 3205）及 `pet.py`（Entry 4051）的結構關係**：
   - `SKILLIDLST` 的前 **7** 項 `[109, 110, 209, 210, 309, 310, 401]`（隱身術/感知/高級隱身術/高級感知/終級隱身術/終級感知/犧牲）恰好完全等於 `script/pet.py` 中定義的特殊主動技能常數 `SPECIAL_INITIATIVE_SKILL = [401, 309, 310, 209, 210, 109, 110]`。
   - `SKILLIDLST` 的後 **41** 項（`403..581`）全部為 `petskill.DATA` 中 `type == 1` 的寵物主動技能，其中 **37** 項構成 `petskill.AUTOFIGHTLIST`，另外 **4** 項為不可掛機自動施放的主動技能（`403` `'媚笑'`、`450` `'隔山打牛'`、`460` `'一箭鐘情'`、`562` `'英勇對決'`）。
2. **`petskill.ShieldShortCutSkills` 與 `petskill.ICON_MAPPING`**：
   - `ShieldShortCutSkills = [556]`（`556: '獸王令'`），存在於 `petskill.DATA`。
   - `ICON_MAPPING` 共 12 對幻化技能圖示映射（`{155: 129, 191: 111, 196: 116, 197: 117, 198: 118, 255: 229, 296: 230, 297: 222, 298: 219, 299: 220, 355: 329, 599: 515}`），所有 12 個鍵與 12 個目標值 **100% 存在於 `petskill.DATA`**。
3. **`summontalentdata.DATA`（Entry 960，76 筆）與 `childdata.LUIPAIDCT`（Entry 3515，12 筆）**：
   - `summontalentdata.DATA` 全部 76 個主鍵 (`6101..6240`) 及其 `iRelatedList` 引用的所有關聯技能 ID **100% 存在於 `petskill.DATA`**。
   - `childdata.LUIPAIDCT` 全部 12 個流派共 24 個子女技能 ID (`807..828, 843..844`) **100% 存在於 `petskill.DATA`**。
4. **附帶發現：Entry 2697 `script/data/pillskilldata.py` (`PILLSKILLIDLST`) 同型整數邊界損毀**：
   - 在跨表掃描引用 `PILLSKILLIDLST` 的寵物 UI 模組（Entries `1249, 2034, 4038, 4048, 4920`）時，我們發現 Entry `2697` (`pillskilldata.py`) 的 `PILLSKILLIDLST`（共 23 項內丹技能 ID）在基線下第 17 項（索引 16，位於 `567` 與 `569` 之間）被解為 `58`（不存在於 `petskill.DATA`）。
   - 檢查 `exp[180..205]` 原始字節證實：Entry `2697` 的 Segment 1 與 Segment 2 原本皆以同一金鑰 `91 (0x5B)` 加密，但 `fls_batch_decoder.py` 將 2 字節區間 `[187..189)` 誤賦予 `keys[2] = 89 (0x59 = 91 ^ 2)`，把 `consts[17]` 的 `568` (`0x0238`, `'飲血'`) 異或成了 `58` (`0x003A`)！當將 `keys[2]` 還原為 `91` 後，`PILLSKILLIDLST` 完整恢復為 `[431..445, 567, 568, 569..574]`，23 個內丹技能 ID **100% 連續存在於 `petskill.DATA`**。

### 4.4 Agent C 寵物技能名稱映射可靠性核查

我們針對 Agent C 負責的寵物表 `script/data/petdata.py`（Entry 2027，135 筆寵物）與怪物圖鑑表 `script/data/monsterdata.py`（Entry 3526，143 筆怪物）進行技能名稱到 `petskill.DATA` 的映射驗證：

1. **`petdata.py`（Entry 2027，`maySkillLst` 與 `mustSkillName`）—— 可靠度：100% 可確定性映射**：
   - 跨全部 135 筆寵物記錄，`maySkillLst` 與 `mustSkillName` 共引用 **144** 個不同的技能名稱。
   - 在基線下，僅 `DATA[4011]['maySkillLst'][3]`（`'仙獸吉祥虎'`）因 Entry 2027 的 `bounds[3] = 21755` 邊界偏移而出現 CP950 亂碼 (`b2d7afc5d902cc27`)；對照 `monsterdata.DATA[4011]['lock3']` 及修正 Entry 2027 `bounds[3] = 21751` 後，該名稱還原為 `'終級強力'`。
   - 還原後，**全部 144 個技能名稱 100% 精確命中 `petskill.DATA[sid]['name']`（無任何別名差異或缺漏）**：
     - 其中 **142** 個名稱在 `petskill.DATA` 中為 **1 對 1 唯一映射**（對應 ID 均位於標準寵物技能區間 `101..584`）。
     - 僅 **2** 個名稱（`'高級命中'`、`'終級命中'`）在 `petskill.DATA` 中命中 2 個 ID（`[229, 255]` 與 `[329, 355]`）。如 4.2 節所證，`255` 與 `355` 屬於 `petskill.ICON_MAPPING` 中的幻化技能，排除 `ICON_MAPPING` 鍵（或限定於 `skillbookdata` 標準獸訣技能 ID）後，**144 個寵物技能名稱可 100% 無歧義地唯一映射至標準寵物技能 ID（`'高級命中' -> 229`、`'終級命中' -> 329`）**。

2. **`monsterdata.py`（Entry 3526，`lock3` 圖鑑展示文本）—— 僅供 UI 展示，不可直接作為結構化技能源**：
   - `monsterdata.DATA[mid]['lock3']` 為富文本字串（如 `'#c3300CC必然攜帶技能：#n  無#r#c3300CC可能攜帶技能：#n  連擊、反擊、幸運、智慧'`）。
   - 除 `DATA[2740]['lock3']`（`'喜兔兔'`）受邊界偏移影響（可由 `petdata.DATA[2740]['maySkillLst'] = ['高級魔法天份', '高級法術連擊', '法術必殺', '魔法毒咒']` 交叉印證）外，解析全表 `lock3` 文本發現其包含：
     - **斜線與括號說明語法**：如 `'協同攻擊/強力'` (`2770`)、`'生命吸取/水擊'` (`2780`)、`'詛咒之刃/連擊'` (`2790`)、`'自由意志/高級強力'` (`2800`)、`'英勇對決/強壯'` (`2800`)、`'念力飛彈/必殺'` (`4013`)、`'魔法毒咒（或：終級命中、終級神跡、劍氣四射、強力）'` (`4110, 4113`)。
     - **4 處圖鑑文案錯別字**（對比同 ID 之 `petdata.DATA` 即可證明為 `monsterdata` 文案筆誤）：
       - `4012` (`仙獸如意貓`)：`monsterdata` 寫作 `'終極靈敏'`，而 `petdata.DATA[4012]` 與 `petskill.DATA[316]` 為 `'終級靈敏'`。
       - `4019` (`神獸樂羊羊`)：`monsterdata` 寫作 `'終極慧根'`，而 `petdata.DATA[4019]` 與 `petskill.DATA[330]` 為 `'終級慧根'`。
       - `4020` (`神獸小靈猴`)：`monsterdata` 寫作 `'高級神獸'`，而 `petdata.DATA[4020]` 與 `petskill.DATA[203]` 為 `'高級神祐'`。
       - `2880` (`金剛`)：`monsterdata` 寫作 `'趁勝追擊'`，而 `petdata.DATA[2880]` 與 `petskill.DATA[555]` 為 `'乘勝追擊'`。
   - 因此，伺服器或資料表轉換應以結構化的 `petdata.py` (`Entry 2027`) + `petskill.py` (`Entry 3205`) 為準，而不應從 `monsterdata.py` 的 `lock3` UI 文本反推技能配置。

---

## 5. 候選修復參數匯總表（供 Agent A 整合參考）

| `script.fls` 索引 | 模組路徑 | 欄位 | 已保存值 (`script_fls_keys.json`) | 驗證後候選值 | `solve_py25_co_span` 建議 |
|---:|---|---|---|---|---|
| `3205` | `script/data/petskill.py` | `keys` / `bounds` | `keys=[204, 23, 122, 74, 218]`<br>`bounds=[18043, 36122, 54130, 72108]` | `keys=[204, 152, 122, 74, 218]`<br>`bounds=[18043, 36123, 54155, 72143]` | 關閉或以 `bounds[1]=36123` 為準（且讀取器需容許 `DATA` 9 個源碼重複鍵覆寫） |
| `454` | `script/data/skilldata.py` | `bounds` | `[3106, 6232, 9375, 12446]` | `[3108, 6233, 9356, 12506]` | 必須關閉（`solve_py25_co_span` 會將 `3108` 誤調為 `3109` 觸發 `opcode 83 @3086`） |
| `3075` | `script/data/skillbookdata.py` | `bounds` | `[2805, 5648, 8450, 11279]` | `[2805, 5650, 8440, 11276]` | 必須關閉（`solve_py25_co_span` 會將 `2805` 誤調為 `2804` 並將 `5650` 誤調回 `5648` 觸發 `opcode 70 @5626`） |
| `2242` | `script/data/petactiveskilldata.py` | `keys` / `bounds` | `keys=[57, 243, 14, 98, 230]`<br>`bounds=[130, 262, 401, 517]` | `keys=[57, 243, 14, 98, 229]`<br>`bounds=[130, 264, 401, 529]` | `bounds[1]=264` 將 `SKILLIDLST[16]` 由 `64605` 還原為 `416` (`'水擊'`)；`bounds[3]=529, keys[4]=229` 還原 `co_lnotab` |
| `333` | `script/data/buffdata.py` | `bounds` | `[8960, 17877, 26838, 35718]` | `[8961, 17874, 26798, 35714]` | `bounds[0]=8961` 修復 `co_code`；`bounds[1]=17874` 將 `DATA[-1263225746]` 還原為 `DATA[110]`；`bounds[2]=26798` 修復 `DATA[277]`；`bounds[3]=35714` 修復 `DATA[702]` |
| `2697` *(附帶發現)* | `script/data/pillskilldata.py` | `keys` | `keys=[153, 91, 89, 91, 191]`<br>`bounds=[120, 187, 189, 250]` | `keys=[153, 91, 91, 91, 191]` | `keys[2]=91` 將 `PILLSKILLIDLST[16]` 由 `58` 還原為 `568` (`'飲血'`) |

---

## 6. 唯讀重現與自動化驗證方法

在倉庫根目錄執行以下唯讀單行命令，即可重現本報告全部 5 個條目的異常根因、修復後結果與跨表映射檢查（不修改任何檔案，亦不執行任何客戶端字節碼）：

```bash
python3 -c '
import sys
from unittest.mock import patch
sys.path.insert(0, "server/tools")
from review_client_data_boundaries import Review, instructions, readable
from survey_csv_readiness import extract
from tools.decompiler import batch_decompile as decoder
from tools.fls_batch_decoder import MarshalReader

r = Review()

def load_custom(idx, keys=None, bounds=None):
    exp = r.payload(idx)
    meta = r.keys[str(idx)]
    k = list(keys if keys is not None else meta["keys"])
    b = list(bounds if bounds is not None else meta["bounds"])
    edges = [0] + b + [len(exp)]
    dec = b"".join(exp[edges[i]:edges[i+1]].translate(decoder.XTABS[k[i]]) for i in range(5))
    tr = decoder.Py25MarshalTranspiler(dec, exp, k, b)
    with patch.object(decoder, "solve_py25_co_span", return_value=None):
        tr.transpile_object()
    return MarshalReader(bytes(tr.out)[8:]).read()

# 1. Entry 3205 petskill.py
co3205 = load_custom(3205, keys=[204, 152, 122, 74, 218], bounds=[18043, 36123, 54155, 72143])
assert all(not isinstance(readable(c), dict) for c in co3205["consts"] if isinstance(c, bytes))

# 2. Entry 454 skilldata.py
co454 = load_custom(454, bounds=[3108, 6233, 9356, 12506])
d454 = extract(co454, "DATA")
assert len(d454) == 105 and readable(d454[1006][b"desc"]).startswith("可以提升儒系")

# 3. Entry 3075 skillbookdata.py
co3075 = load_custom(3075, bounds=[2805, 5650, 8440, 11276])
d3075 = extract(co3075, "DATA")
assert sum(len(v) for v in d3075.values()) == 176 and readable(d3075[3][38][b"name"]) == "靈巧抵抗"

# 4. Entry 2242 petactiveskilldata.py
co2242 = load_custom(2242, keys=[57, 243, 14, 98, 229], bounds=[130, 264, 401, 529])
lst2242 = extract(co2242, "SKILLIDLST")
assert len(lst2242) == 48 and lst2242[16] == 416

# 5. Entry 333 buffdata.py
co333 = load_custom(333, bounds=[8961, 17874, 26798, 35714])
d333 = extract(co333, "DATA")
assert len(d333) == 432 and 110 in d333 and -1263225746 not in d333
assert readable(d333[277][b"desc"]) == "五感剝奪·舌；與五感剝奪·眼、耳、鼻、身同時存在時，將立即死亡"
assert readable(d333[702][b"desc"]) == "戰鬥風向；上"
print("ALL AGENT D VERIFICATIONS PASSED")
'
```

同時，現有架構測試套件執行結果保持全數通過：
- `python3 -m unittest discover -s server/tests/architecture -v`：**31 tests OK**。
