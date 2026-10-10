# Evidence E-DATA-001: 《夢想世界》遊戲核心數據表解析與逆向工程證據

- **ID**: E-DATA-001
- **任務**: Task D - 技能/裝備/道具/怪物遊戲數據分析與瀏覽器構建
- **日期**: 2026-10-09
- **狀態**: 驗證完成 (Verified)

---

## 1. 核心檔案與架構定位

通過對客戶端 `data/` 目錄中各類歸檔檔案的深入逆向與動態分析，確定了遊戲資源與數據結構的劃分體系：

| 封包路徑 | 封包格式 | 條目總數 | 關鍵用途與數據內容 |
| :--- | :--- | :--- | :--- |
| `data/data.fls` | FLS ZIP-Variant | 133 | 客戶端核心 Python 執行庫、字元集編碼 (`core/gamecode.pyo`)、網路通訊與日誌模組 |
| `data/script.fls` | 0SLF Header, 4-dword Index | 5,002 | 核心業務數據邏輯庫：裝備屬性、場景清單、NPC隨機互動、活動獎勵、招式配置等 |
| `data/skill.fls` | 0SLF Header | 342 | 戰鬥技能招式底層動畫與施法邏輯定義 |
| `data/skill2.fls` | 0SLF Header | 454 | 高級法術、寵物技能與被動觸發元數據 |
| `data/passive.fls` | 0SLF Header | 41 | 被動戰鬥天賦與心法觸發數據庫 |

---

## 2. 多重混淆加密破解機制

### 2.1 索引表動態混淆算法
每個歸檔檔案尾部存儲目錄索引表，每個條目由 4 個 32 位整數組成 `(entry_id, r1, r2, r3)`，透過多項式線性變換還原條目資訊：
```python
MASK32 = 0xFFFFFFFF
f1 = (((index * 0x0E7C83D2 + entry_id) & MASK32) ^ r1) & MASK32
f2 = (((r1 * entry_id + 0x0DF25E) & MASK32) ^ r2) & MASK32
f3 = (((r2 * index * 0x00F718FE + 0x0D59D16C) & MASK32) ^ r3) & MASK32
# f2 = 壓縮後長度 (compressed_length)
# f3 = 數據區段偏移量 (data_offset)
```

### 2.2 5段動態 XOR 密鑰切分機制
在 `data/script.fls` 條目中，解壓後的 Python Marshal  bytecode 被劃分為 5 個近似等長的數據段，各段使用獨立的 XOR 密鑰：
- 段 0 密鑰由位元組碼起始特徵標記 `'c'` (0x63) 決定：`k0 = raw[0] ^ 0x63`。
- 後續段 1~4 的密鑰與邊界偏移量依據頻率統計與相鄰邊界平滑算法自動計算提取。

以 Entry 17 (`script\data\equipitemdata.py`) 為例：
- 解壓大小：9,732 位元組
- 5 段 XOR 密鑰：`[0x63, 0x1d, 0xab, 0x4c, 0x94]`
- 區段邊界切分點：`[0, 1964, 3807, 5798, 7700, 9732]`

---

## 3. 多益定製 Python Marshal 結構解析

解密後的 Bytecode 符合 Python 2.5 系列標準，但具有多益特製擴展：
- 程式碼對象 (`type 'c'`) 在標準屬性 `(argcount, nlocals, stacksize, flags)` 之後，額外插入了 **4 位元組定製頭部 (`extra`)**。
- 字串編碼體系採用 **Big5 (繁體中文)** 與 **GBK (簡體中文)** 混合相容，支援遊戲全量裝備、地圖、招式描述與 NPC 劇本。

---

## 4. 驗證產出物

1. **解析引擎腳本**: `tools/data-parser/extract_game_data.py`
2. **多格式導出數據庫**:
   - `tools/data-export/equipment.json` / `equipment.csv` (裝備體系)
   - `tools/data-export/scenes.json` / `scenes.csv` (全圖場景)
   - `tools/data-export/npc_dialogs.json` / `npc_dialogs.csv` (NPC互動對白)
   - `tools/data-export/reward_gifts.json` / `reward_gifts.csv` (獎勵清單)
   - `tools/data-export/skills.json` / `skills.csv` (流派招式)
   - `tools/data-export/game_data.sqlite` (關聯型數據庫)
3. **可視化數據瀏覽器**: `tools/data_browser/app.py`（支援 Web 儀表板與 CLI 查詢）
