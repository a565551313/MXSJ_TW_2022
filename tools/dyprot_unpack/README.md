# dyprot_unpack —— 在 Unicorn 裡跑保護殼入口（實驗性，尚未脫殼）

`mxmain.dll` 有 54% 的鏡像在 `_dyprot0` / `_dyprot1` 兩節裡（熵 7.85 / 7.72），
靜態讀不進去。這個工具把整個 PE 映射進 [Unicorn](https://www.unicorn-engine.org/)，
從 PE 入口開始執行保護殼，觀察它到底需要什麼、卡在哪一步。

**它現在能做的**：把殼跑到「自己崩掉」為止，並如實報告呼叫了哪些 API、有沒有
回頭改寫映像、IAT 有沒有被重綁。
**它現在做不到**：解出被保護的載荷。別把它當脫殼器用。

## 跑起來

```bash
python -m pip install pefile==2024.8.26 unicorn==2.1.4
python tools/dyprot_unpack/dyprot_emulate.py            # 預設 30 秒
python tools/dyprot_unpack/dyprot_emulate.py --seconds 60 --json /tmp/dyprot.json
```

實測輸出（`mxmain.dll` `637331b5…be424d`，30 秒預算）：

```
導入 859 槽 / 假匯出 691 名 / 12.0 s / 停因：fault: Invalid memory fetch（eip=0xb40a2330）
被調用的 API： {'GetModuleHandleA': 2, 'GetModuleFileNameW': 2, 'LocalAlloc': 1,
               'GetProcessWindowStation': 1, 'GetUserObjectInformationW': 1, 'LoadLibraryA': 1}
映像被改寫的區間： [{'va': '0xe1b000', 'size': 3580}]
IAT 重綁： {'iat_va': '0xe1b000', 'iat_size': 3584, ...}
```

## 已經確認的兩件事

1. **殼走的是「解析 PE 匯出表」拿 API**，不是直接讀 IAT。所以要讓它往下走，
   必須給它結構合法的假 kernel32 / ntdll / user32 / advapi32 映像
   （`fake_modules.py`：DOS+PE 頭、`.edata`、匯出目錄，RVA == 偏移）。
   給對了以後，它會把 **859/896 個 IAT 槽**重寫成這些假匯出表的位址——
   IAT 有 3,430 位元組被改寫，映像其他部分零改動。
2. **它沒有解密任何載荷**：`.data` 運行期尾部（`0x93C180`，27 個 `interface`
   型別的 `tp_name` 就是從那裡被 `strcpy` 出去的）在整段執行裡始終是 0，
   `_dyprot0/1` 一個位元組都沒被改寫。

## 為什麼還沒成功（兩個已排除的方向）

- **不是缺 API 數量**：導入名單 691 個名字全部進了假匯出表，未實作的樁按
  `ARG_COUNTS` 正確清棧並回 0；殼照樣在某個計算跳轉後失控。
- **不是異常沒派發**：`fs:[0]` 確實指向棧上的 `EXCEPTION_REGISTRATION_RECORD`
  （殼裝了 SEH），手動造 `EXCEPTION_RECORD` + `CONTEXT` 跳進 handler 之後
  行為沒有改變。

剩下兩種可能：殼在檢查「這是不是它自己的宿主環境」（模組位址/節佈局/父進程），
或者它執行的本來就是它以為已解密的位元組（解密依賴我們沒提供的輸入）。

## 環境限制（照抄，別踩第二次）

- **unicorn 的 32 位模式忽略 `FS` 段基址**（寫 `UC_X86_REG_FS_BASE` 是 no-op 並告警），
  所以 `fs:[0x30]` 讀的其實是 `[0x30]`：TEB/PEB 只能擺在位址 0，這也讓「空指針」
  和「fs:0」在模擬器裡變成同一件事。
- `pefile.get_memory_mapped_image()` 不會幫你套用重定位，也不含 `.data` 的
  未初始化尾部——殼在那塊跑起來看到的是全 0。
- 殼的入口跳板鏈很短（`0xcba0ae → 0xcba0b8 → 0xe0aa77`），真正的邏輯在
  `_dyprot1` 裡；用 `objdump` 直接反組譯那兩節只會得到看起來像指令的亂碼。

## 邊界

只讀 `mxmain.dll`；不載入任何 Windows DLL、不調用系統、不連網、不改原檔；
`--json` / `--snapshot` 的目標路徑不許指向輸入映像（同路徑 / symlink / 硬連結都拒）。
模擬器裡的「執行」只發生在 Unicorn 的記憶體裡，不是啟動客戶端。

## 測試

```bash
python -m unittest tools.dyprot_unpack.test_dyprot_emulate -v
```

缺 `pefile` / `unicorn` 時整檔跳過。測試釘住的是假 DLL 映像的結構（`pefile`
真的能解析出匯出名與位址——這一條壞了會表現成「殼突然停在入口」而不是明顯錯誤）
和輸出不覆蓋輸入的護欄。

## 下一步（按性價比）

1. 在 Windows 上跑 [`work/dream-world-connect-login-map/tools/dump_dyprot.py`](../../work/dream-world-connect-login-map/tools/dump_dyprot.py)
   （只讀 `ReadProcessMemory`，30 秒拿到解密後的兩節）——不需要模擬器。
2. 繼續模擬：讓假模組的基址/節佈局更像真的系統模組，補完整 SEH（含 `CONTEXT` 還原），
   並處理 `CPUID` / `RDTSC` 這類反虛擬機檢查。
