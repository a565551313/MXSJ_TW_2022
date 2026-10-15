# 窗口标题与聊天文字编码链路（2026-10-15 结案）

> 触发问题：用户在真机上看到「窗口标题」和「聊天」乱码，而游戏内其他文字正常。
> 本文结论来自本轮对 `data/script.fls` **全量反编译语料**（4,401 个模块）的检索，
> 加上对 `mx.exe` / `mxmain.dll` / `imwin7.dll` 的导入表核对。
> 标注约定：**[事实]** = 本轮直接读到的字节/反编译源码；**[推断]** = 由事实推出但未真机验证。

## 0. 一分钟结论

1. **分界线**：游戏内绝大多数文字由脚本层用自带 Big5 码表解码后**引擎自绘**；
   而**窗口标题**和**输入/剪贴板（IM）层**把字节直接交给 Windows 的 **ANSI API**，
   由**系统 ANSI 代码页（ACP）**解释。只有后者会随系统区域设置乱码——这不是巧合，
   是两条不同的渲染路径。
2. **[事实]** 客户端**只有 ANSI 版**窗口 API：`mx.exe` 与 `mxmain.dll` 的 USER32 导入里有
   `SetWindowTextA` / `GetWindowTextA` / `MessageBoxA`，`SetWindowTextW` 出现次数为 **0**。
3. **[事实]** 标题字符串在脚本侧**不经过任何编码转换**：
   `misc.SetSysCaption()` → `C_sys.SetCaption()` 原样传递（`script/misc.py:1428-1432`）。
4. **[事实]** `script/interface.py:22-24`：`GBK = 0`、`BIG5 = 1`、**`GCODE = BIG5`**
   ——本版本是繁体（Big5）客户端。
5. **[事实]** 标题字面量本身是 **Big5 字节**：`script/data/defines.py:10`
   `TITLE_NAME_MX = b'\xb7s \xb9\xda \xb7Q \xa5@ \xac\xc9'`，按 cp950 解为 `新 夢 想 世 界`。
6. **[事实]** 登录后标题被**重建为三段拼接**（`script/nethero.py:153`）：
   游戏名（Big5 字面量）+ 服务器名（来自 `server.ini`，Big5）+ 角色名（服务端下发）。
   三段来源编码未必一致，全部原样送进 `SetWindowTextA`。
7. **[推断]** 因此：系统 ACP = cp950（繁中）时标题正常；cp932（日文）显示为半角片假名
   类乱码；cp1252 显示为带重音拉丁字母；cp936（简中）会在 `0xa5 0x40` 处**直接解码失败**。
   这四种表现都已在离线复算中重现（见 §3）。

## 1. 标题路径（逐跳）

```
script/data/defines.py:10      TITLE_NAME_MX = <Big5 字节>
  └ script/login/selectserver.py:190   C_sys.SetCaption(defines.TITLE_NAME_MX)
  └ script/login/mainpage.py:316       misc.SetSysCaption(defines.TITLE_NAME_MX)
  └ script/gamectrl.py:124,129         misc.SetSysCaption(...) / '《夢想世界》錄像播放器'
  └ script/blacklist/blacklist.py:323  misc.SetSysCaption(defines.TITLE_NAME_MX)
  └ script/nethero.py:153              misc.SetSysCaption('%s - %s - %s' % (TITLE_NAME_MX, serverName, hero.GetProp('m_Name','')))
        ↓
script/misc.py:1428  def SetSysCaption(s):
    if innerversion.IsInnerVer(): s = '開發端！' + s   # ← 内测版再加一段 Big5 字面量
    C_sys.SetCaption(s)                                # ← 无 encode/decode
        ↓
原生 C_sys.SetCaption → user32!SetWindowTextA(字节)    # ← 按系统 ACP 解释
```

`'%s - %s - %s'` 是 **str 格式化**，说明整条链上文本始终是字节串，Python 层不参与编解码。

## 2. IM / 输入层（聊天输入、剪贴板、字符切分）

**[事实]** `imwin7.dll` 的导入表只关心码页：`GetACP`、`GetOEMCP`、`GetCPInfo`、
`IsValidCodePage`、`MultiByteToWideChar`、`WideCharToMultiByte`、`CharNextA`（USER32 侧仅
`CharNextA`）。

- 一切进出文本按 **ACP** 与 Unicode 互转；
- `CharNextA` 按 ACP 判断字符边界 → 用简中/日文码页切 Big5 字节流会**切在半个汉字上**，
  表现为丢字、多字、退格删半个字。

**[事实]** 聊天发送 `script/netchat.py:109-122 C2SPlayerChat`：
`netobj.PacketAddS(word, len(word))` —— **原样把 Big5 字节发给服务端，无任何转换**。
所以自建服务端必须按 Big5 收发并**原样回传**，否则回显必乱。

## 3. 离线复算（可复现）

```python
raw = b'\xb7s \xb9\xda \xb7Q \xa5@ \xac\xc9'      # TITLE_NAME_MX 的真实字节
raw.decode('big5')    # '新 夢 想 世 界'      ← 正确
raw.decode('cp932')   # 'ｷs ｹﾚ ｷQ ･@ ｬﾉ'      ← 日文系统的表现
raw.decode('cp1252')  # '·s ¹Ú ·Q ¥@ ¬É'      ← 西文系统的表现
raw.decode('gbk')     # UnicodeDecodeError @9 ← 简中系统：解不动，显示 / 或方块
```

**判别法**：看到的是**错字**（合法汉字但不是那个词）→ 码页问题；看到的是**方块/空白**→
字体缺字（客户端自带 `Fonts/` 全是大陆字体，`FZLanTingYuan-DB-GBK.ttf` 文件名即写明 GBK，
原生用 `CreateFontA` + `GetGlyphOutline` 取字形）。

**[事实]** 脚本层自带码表，所以自绘文字不依赖系统：`mxmain.dll` 内可检出
`big5`、`big5hkscs`、`big5hkscs_bmp`、`big5hkscs_nonbmp`、`__map_big5`；`script.fls` 内还带
`script/lib/encodings/*`（如 entry 2473 `script/lib/encodings/ascii.py`）。

## 4. 处置建议（按代价从低到高）

1. **单进程模拟码页**（推荐，不动系统）：用 Locale Emulator 以 `zh-TW / cp950` 启动 `mx.exe`。
2. 改系统「非 Unicode 程序的语言」为中文(繁体，台湾)，注销后重启。**不要**开「使用 Unicode
   UTF-8 提供全球语言支持」（ACP=65001 时这类老客户端必坏）。
3. 缺字/方块另查字体：装或启用繁中字族（PMingLiU / Microsoft JhengHei）。
4. **不建议**改 `data/data.fls` 里 `core/gamecode.pyo` 的 `SYSCODE`：它是编译期常量
   （**[事实]** 全 `data.fls` 中只有该模块引用 `SYSCODE`/`GAMECODE`，无运行时探测），
   且同时被 `core/C_log.pyo`、`debug/logsys.pyo` 的日志路径共用；改它要重打包 data.fls，
   违反「不覆盖原包」红线。
5. 自建服务端方向：聊天/名字文本按 **Big5** 处理并与客户端 `interface.GCODE` 一致；
   不要用简繁转换去"修"客户端显示（`裏`、`羣` 等在 cp950 不可编码，会静默丢字）。

## 5. 顺带发现：台服构建的地区开关是 `'cn'`

**[事实]** `GetGameRegion()` 有两处定义，**都返回 `'cn'`**：

- `script/pub2/pubdelegate_v2.py:216`（默认实现，docstring 注明 `cn:中國(陸服)/tw:台服/hk/mo`）
- `script/delegate.py:227`，且带 `@Override('pubdelegate_v2')` —— 即显式覆盖生效的就是 `'cn'`。

其结果：`script/pub2/pubbandata/pubbandata.py:24-40` 的 `GetNameData()` / `GetWordData()`
取的是 **`pub_pc_name_cn` / `pub_pc_chat_cn`**（而非 `_tw` 版本）。

**已排除的危险假设**：本以为这两张表是码位表（GBK 码位套在 Big5 文本上会大面积误屏蔽）。
实测 `DATA` 是 **0..3863 的连续序号列表**（cn 3865 项、tw 3972 项、name_cn 3773、name_tw 3915），
不含双字节码位，因此**不会造成乱码**。真实含义是：台服构建启用了**简中区的屏蔽词子集**。

受该子集影响的字段（**[事实]** 调用点）：宠物名、战队名/简介、公会相关名、称号、商店名、
仓库名、指令名、`flypostext` 等，走 `banword.AddCheckWordTask(...)`；
你画我猜频道的聊天走 `netchat.CheckPaintAndGuessBanWords`，命中即 `sWord.replace(sBan, '*')`。
即表现应为**变星号/被拦**，而非乱码。

## 6. 本轮语料与复现方式

`tools/decompiler/output/` 历史上只入库 **173** 个文件。本轮把 `data/script.fls` 全量补跑：

| 项 | 值 |
|---|---|
| 条目总数 | 5002 |
| 完整反编译 | **4401** |
| 含失败标记/部分产出 | 28 |
| 明确失败（写出 52 字节占位，主要是已知 546 stub 一类） | 547 |
| 无产物 | 26（其中 23 条历史标记即 `fail`/`suspect`） |
| 产出体积 / 文件数 | 62 MB / 4987 个 `.py` |

**[勘误 2026-10-15]** 上表「无产物 26」是按索引 `current_filename` 清点得到的，其中
13 条其实早有产物（9 条落 `script/unknown/`，4 条因文件名取自包内自报路径而落在真实模块
路径下），另有 9 条已由 `tools/decompiler/recover_entries.py` 救回，真正解不出的只剩 4 条
（`1954`、`3066`、`4166`、`4691`）。语料现为 **5000 个 `.py` + 1 个 `.pyc` / 66 MB**：
完整反编译 4444、52 字节占位 547、本轮恢复产物 9。逐条根因见
`notes/opcode_mapping_and_decompilation.md` §4.5。**教训：清点产物必须扫目录，不能按 catalog 名匹配。**

**[事实]** 两个条目对 uncompyle6 是病态的：`script/core/preload/preload_mov.py`（entry 2371，
>900 s 未收敛）、`script/data/wingtypeposdata.py`（entry 2679，894 s 后仍失败）。
整池并行会被这类条目堵死，故本轮改为「一条一子进程 + 超时」驱动。

生成物**不入库**（62 MB / 近 5000 文件，超出仓库提交约定），需要时重跑：

```bash
python3 tools/decompiler/batch_decompile.py data/script.fls <仓库外目录> --workers N
# 单条目：--entry 4007 ；子串：--entry login ；只要原始字节不要 Big5 美化：--no-big5
```
