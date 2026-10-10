# Task D 遊戲數據分析、瀏覽器與打包工具全量記錄清單

本文件記錄 Task D 的全部逆向成果、數據導出、工具程式與相應檔案路徑。

---

## 1. 核心文檔與分析報告

| 檔案路徑 | 類型 | 內容說明 |
| :--- | :--- | :--- |
| `notes/task-d-游戏数据/game-data-analysis.md` | 主分析報告 | 全面分析歸檔體系、加密模型、裝備/地圖/招式數據結構、重打包逆向代數公式 |
| `work/dream-world-connect-login-map/notes/task-d-游戏数据/game-data-analysis.md` | 工作區存檔 | 同步至個人工作區的完整分析報告備份 |
| `evidence/E-DATA-001.md` | 驗證證據 | 記載目錄混淆演算法、5段XOR密鑰與位元組碼特徵驗證記錄 |
| `work/dream-world-connect-login-map/notes/task-d-游戏数据/E-DATA-001.md` | 工作區存檔 | 同步至個人工作區的驗證證據備份 |

---

## 2. 導出的全量遊戲數據庫 (`tools/data-export/`)

所有數據均提供 **JSON**、**CSV** (帶 UTF-8 BOM 支援 Excel) 及 **SQLite** 關聯數據庫 3 種格式：

1. **裝備防具數據**：
   - `tools/data-export/equipment.json`
   - `tools/data-export/equipment.csv`
   - 包含劍、刀、槍、拳套、筆、暗器 6 大武器系別與男女頭盔、衣服、腰帶、鞋子、護腕、戒指、香囊等全套防具飾品數值與製造人。
2. **世界地圖與場景**：
   - `tools/data-export/scenes.json`
   - `tools/data-export/scenes.csv`
   - 包含永澤城、天蒼城、香葉城、各大平原、海底神殿、迷宮及各國師道殿等 57 個地圖。
3. **NPC 互動與世界觀**：
   - `tools/data-export/npc_dialogs.json`
   - `tools/data-export/npc_dialogs.csv`
   - 包含兔狼兩族恩怨、黎明鎮/夜幕鎮對立及魔族對抗等 40 條經典對白。
4. **坐騎珍品與獎勵**：
   - `tools/data-export/reward_gifts.json`
   - `tools/data-export/reward_gifts.csv`
   - 包含獸魂勛章、神獸/仙獸祝福石、高級魔獸要訣等 23 種獎勵條目。
5. **戰鬥招式與流派**：
   - `tools/data-export/skills.json`
   - `tools/data-export/skills.csv`
   - 包含 11 大流派招式元數據與法術消耗。
6. **綜合數據庫**：
   - `tools/data-export/game_data.sqlite`（集成上述五張主表，支援複合查詢）。

---

## 3. 開發的工具程式庫

### 3.1 數據瀏覽器 (`tools/data_browser/`)
- `tools/data_browser/app.py`：
  - **Web 即時儀表板**（監聽 `http://0.0.0.0:8080`），支援響應式深色介面、五大數據表即時切換與防抖即時搜索。
  - **CLI 命令行模式**（`python3 tools/data_browser/app.py cli <表名> [關鍵字]`）。
- `tools/data_browser/desktop_app.py`：
  - **桌面視窗版 (Tkinter Desktop GUI)**：原生桌面視窗，帶下拉列表、動態表格與過濾搜索。
  - **終端交互桌面版 (TUI)**：無圖形介面/SSH 下自動啟動的全螢幕終端交互介面。

### 3.2 解析與重打包引擎 (`tools/data-parser/`)
- `tools/data-parser/extract_game_data.py`：
  - 自動化逆向數據提取腳本，負責從原生封包解密並生成上述所有 JSON/CSV/SQLite 檔案。
- `tools/data-parser/repack_fls.py`：
  - 單條目熱補丁與逆向多項式編碼引擎，支援修改數據並無損寫回封包。
- `tools/data-parser/universal_fls_tool.py`：
  - **全格式通用打包/解包工具**，全面支援遊戲全部兩類歸檔體系：
    1. **`0SLF` 體系**：`script.fls`, `skill.fls`, `skill2.fls`, `passive.fls`, `effect.fls`（目錄多項式逆向與 Zlib 雙向還原）。
    2. **`FLS\x00` 體系**：`data.fls`（自研 ZIP 格式解構與模組重封裝）。

---

## 4. GitHub PR 追蹤

- **PR 連結**：https://github.com/a565551313/MXSJ_TW_2022/pull/1
- **分支**：`arena/8bafffe0-mxsj-tw-2022` $\to$ `arena/6fbb3403-mxsj-tw-2022`
