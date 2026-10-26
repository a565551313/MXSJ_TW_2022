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

實測輸出（`mxmain.dll` `637331b5…be424d`；這一輪 0.8 s 就撞到同一個 fault——把
`UC_HOOK_CODE` 限定在樁區之前，每條指令都回 Python，要 12.0 s，兩者的停因、寫入
次數、API 集合逐項相同）：

```
導入 859 槽 / 假匯出 691 名 / 0.8 s / 停因：fault: Invalid memory fetch（eip=0xb40a2330）
被調用的 API： {'GetModuleHandleA': 2, 'GetModuleFileNameW': 2, 'LocalAlloc': 1,
               'GetProcessWindowStation': 1, 'GetUserObjectInformationW': 1, 'LoadLibraryA': 1}
映像被改寫的區間： [{'va': '0xe1b000', 'size': 3580}]
IAT 重綁： {'iat_va': '0xe1b000', 'iat_size': 3584, ...}
```

### 想看得更細：`--trace-tail`

```bash
python tools/dyprot_unpack/dyprot_emulate.py --seconds 25 --trace-tail 12
```

它會留下最後 N 條被執行的指令（位址 + 當時的原始位元組）。注意這個鉤子**不限範圍**，
每條指令都回 Python，實測慢 15 倍左右；只在追停因時開。

實測尾巴（`637331b5…`）是：`0xd9f590: 8b 44 25 00`（`mov eax,[ebp]`，`ebp=0x203fef80`）
→ `0xd9f594: ff d0`（`call eax`）→ `eax=0xb40a2330`，於是 fetch 失敗。那個 dword
不是映射內的位址，是從 VM 棧上取出來的。

## 已經確認的兩件事

1. **殼走的是「解析 PE 匯出表」拿 API**，不是直接讀 IAT。所以要讓它往下走，
   必須給它結構合法的假 kernel32 / ntdll / user32 / advapi32 映像
   （`fake_modules.py`：DOS+PE 頭、`.edata`、匯出目錄，RVA == 偏移）。
   給對了以後，它會把 **859/896 個 IAT 槽**重寫成這些假匯出表的位址——
   IAT 有 3,430 位元組被改寫，映像其他部分零改動。
2. **它沒有解密任何載荷**：`.data` 運行期尾部（`0x93C180`，27 個 `interface`
   型別的 `tp_name` 就是從那裡被 `strcpy` 出去的）在整段執行裡始終是 0，
   `_dyprot0/1` 一個位元組都沒被改寫。

## 參數個數：不知道就停下來，不猜

`stdcall` 的返回地址在 `[esp]`、參數從 `esp+4` 起，返回時 `esp += 4 + 4*argc`——
所以「這個名字有幾個參數」是必須知道的，猜 0 會讓返回值寫錯位置、`esp` 一路歪掉。
樁自己用 `@stdcall(n)` 宣告，其餘靠 `win32_env.ARG_COUNTS`。兩邊都沒有時直接拋
`UnknownArity` 並在停因裡寫出名字（把它加進 `ARG_COUNTS` 再跑），**不會**默默當 0 清棧。

目前 613 個非修飾導入名裡，66 個有語義實作、其餘大多不在殼的呼叫面上；殼實測只碰到
6 個，所以「缺哪個補哪個」是安全的迭代方式。順帶一提，`?…@…@@…` 那些是 C++ 修飾名
（Wwise / 自繪引擎匯出），不屬於 Win32 stdcall，殼不會透過它們拿 API。

## 為什麼還沒成功（兩個已排除的方向）

- **不是缺 API 數量**：導入名單 691 個名字全部進了假匯出表；有語意實作的樁正常
  執行，沒實作、但參數個數在 `ARG_COUNTS` 裡的按表清棧回 0，兩張表都沒有的名字
  會直接停下來報錯（不會清錯棧）。殼照樣在某個計算跳轉後失控。
- **不是異常沒派發**：`fs:[0]` 確實指向棧上的 `EXCEPTION_REGISTRATION_RECORD`
  （殼裝了 SEH），手動造 `EXCEPTION_RECORD` + `CONTEXT` 跳進 handler 之後
  行為沒有改變。

還有一條路徑統計支持「它是 VM 型混淆，不是在等解密」：跑的那 12 秒裡，`_dyprot1`
裡有 **1,450 個不同的 EIP** 往同一段 256 位元組的棧窗口（`0x203fef00`–`0x203ff000`）
寫了 **22,987 次**——這是解釋器/虛擬機的分發器特徵，而不是「解密迴圈」。加上
「沒有任何節區被改寫」，比較合理的解釋是：這兩節本來就是可直接執行的混淆代碼，
殼最後用從位元組流裡取出的指標 `call [ebp]`（`[ebp]=0xb40a2330`）去呼叫一個
只有真實宿主才有的東西。

剩下兩種可能：殼在檢查「這是不是它自己的宿主環境」（模組位址/節佈局/父進程/CPUID），
或者那個被呼叫的位址依賴我們沒提供的輸入。

## 環境限制（照抄，別踩第二次）

- **unicorn 2.1.4 的 32 位模式不實作 `UC_X86_REG_FS_BASE` 寫入**（no-op 並告警）：
  本探針不設 FS 段，`fs:[0x30]` 讀到的就是 `[0x30]`，TEB/PEB 因此擺在位址 0。
  這是**這個探針配置**的性質，不是「Unicorn 裡 FS 永遠失效」的斷言；真要換配置，
  得先把段基址寫得進去。附帶效果是「空指針」和「fs:0」在模擬器裡變成同一件事。
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

13 項。缺 `pefile` / `unicorn` 時整檔跳過。釘住的是：假 DLL 映像的結構（`pefile`
真的能解析出匯出名與位址——這一條壞了會表現成「殼突然停在入口」而不是明顯錯誤）、
映像按匯出量放大、輸出不覆蓋輸入的兩條護欄、參數個數未知時必須報錯、每個樁的
`@stdcall(n)` 要和 Python 簽名一致、`UC_HOOK_CODE` 只掛在樁區。

## 下一步（按性價比）

1. 在 Windows 上跑 [`work/dream-world-connect-login-map/tools/dump_dyprot.py`](../../work/dream-world-connect-login-map/tools/dump_dyprot.py)
   （只讀 `ReadProcessMemory`，30 秒拿到解密後的兩節）——不需要模擬器。
2. 繼續模擬：讓假模組的基址/節佈局更像真的系統模組，補完整 SEH（含 `CONTEXT` 還原），
   並處理 `CPUID` / `RDTSC` 這類反虛擬機檢查。
