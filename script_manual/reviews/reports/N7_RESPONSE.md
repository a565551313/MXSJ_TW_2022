# N7_RESPONSE · 全新独立审核与集成验收

> **会话身份**：N7 —— Arena 2026-10-16 分配的**全新第 7 个新 agent**。
> 逻辑任务包：H / review。允许路径：`script_manual/reviews/`。
> **不是**之前宕机的旧 H，**不是** A，**不是**任何领域作者；**未代写任何作者正文**，只写审核记录。
> 所有审核记录 `reviewer` 一律写真实的 `"H"`，并在 `note` 中写明本 N7 会话身份、输入提交、核对范围与未知；
> 未新增 `H_x.json` 造成重复，对已存在的 `reviews/8b6e9266_<entry>.json` **原位更新**。

---

## 1. 实际基线与分支

| 项 | 值 |
|---|---|
| 本会话固定分支 | `arena/474295bc-mxsj-tw-2022`（全程未切换、未新建、未复用旧 B–H 分支） |
| 交接基线 | `9b0dea799768aaacbb967ffc59f45753970752be` |
| 集成分支 | `arena/61deb9e5-mxsj-tw-2022`（`git fetch` 得到同一 SHA；`git merge --no-edit FETCH_HEAD` → `Already up to date`） |
| **开工 HEAD** | `9b0dea799768aaacbb967ffc59f45753970752be` |
| 开工前工作树 | 干净（`nothing to commit, working tree clean`），无既有未保存工作需先抢救 |
| 合并内容检查点 | `7d32e5340b0ab4168f725d238d767ad6232f715d` —— 本地为 **shallow** 克隆（`.git/shallow` 存在），先 `git fetch --unshallow origin` 取回历史（289 个提交）后，`git merge-base --is-ancestor` 返回 0，**已确认在祖先中** |
| 任务卡版本 | `20261016-new-cohort-v1` |

**锁定输入本机核对（全部相符，未改动）**

```text
8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72  data/script.fls
5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c  data/data.fls
43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb  tools/decompiler/script_fls_keys.json
```

分析环境一律建在**仓库外**：Python **3.11.2** + `uncompyle6==3.9.3` / `xdis==6.1.8` / `spark-parser==1.9.0` / `click==8.5.0`（与任务卡参考环境一致）；手册依赖另装 `jsonschema==4.25.1`、`ruff==0.17.1`。

---

## 2. 独立复现（全部本会话自己跑，不是引用历史）

```bash
<仓库外venv>/bin/python tools/decompiler/recover_entries.py --out <仓库外目录> \
  --entries <白名单> --decompile-timeout 30 --report <仓库外JSON>
```

| 批次 | 白名单 | 结果 |
|---|---|---|
| gameplay | 3038, 717, 1129, 949 | 4/4 `recovered` / `source` / `baseline` / `decompile_ok`；候选 2927 / 3215 / 1107 / 1235 行 |
| mainmenu | 219 | 1/1；去六头正文 SHA `e03d31ac8deaab37766addcab9e2a1a63dd1b3c223e977cfe3f427b80df05bfd`、42790 字节 |
| network | 3176, 2170, 871, 516 | 4/4；net.py 1364 / connect.py 295 / netquicklogin.py 313 / netserver.py 584 行 |
| ui_chat | 3854, 3232, 4832 | 3/3；interface.py 5681 / key.py 276 / chatoutput.py 2478 行 |
| login | 337, 4293, 4007, 4806 | 4/4；mainpage.py 338 / main.py 1579 / register.py 1311 / loginin.py 1442 行 |

工具指纹：`recover_entries.py` `152dbc28864a10c8…`、`batch_decompile.py` `a74742231e04c018…`（与作者收据一致，未改动）。

**gameplay 复现逐条吻合**：四条 `stored_sha256` 前缀 `930eb0dfac061776` / `55322bfd081248c9` / `09505840b0cbd3f6` / `45deec3b0ae52005`，
去六头正文 SHA `e04fe622…27dce7` / `153bae3a…bcbbb` / `71693557…ec764f7` / `cf66726e…140dfb`，**与 A / N6 自报逐字一致**。
**摘录逐行核对**：基线 205+219+224+303 = **951** 行、PR#42 为 **980** 行，与本次重跑候选**字节完全相同、0 处不一致**。

---

## 3. 一次差点误判的复核（如实记录）

审查 gameplay 证据绑定时，本会话先按「`evidence.start_line/end_line` 指**候选原行**」假设核对，发现四份文件的全部证据范围都
**从 L9 起连续平铺**在候选首段（hero L9-213 / dlgitem L9-240 / task L9-246 / npc L9-323），
而 `GetHeroObject` 实际在候选 L164、`ShowDlg` 在 L2614——一度判定为**系统性错绑**，并已按该结论写好退修。

随后核对 `ui_chat/evidence/*.txt`，其头部**明示约定**：

> 「摘录规则：L 后数字是外置候选原始 1-based 闭区间行号；冒号后是原行的 JSON 字符串……
> **手册 evidence.start_line/end_line 则指本报告实际行号；两套行号不可混用。**」

按该约定重审：每条 evidence 的首行都是 `[symbol] candidate Lx–Ly` 块头，块内 L 行恰为声明的闭区间——
**基线 56/56、PR#42 61/61 全部正确绑定**。因此**撤回错绑判定**，未写入任何基于该误判的退修。

**遗留的文档缺口（报 A，不作退修项）**：gameplay 四份摘录**没有**写明这套“行号指摘录文件自身行”的约定，
而 ui_chat 写了。同一仓库两套证据文件约定不同且一处未声明，复核者极易误判（本会话即为一例）。
建议 A 在 `CONTRACT.md` §3 或 gameplay 摘录头补一句统一约定。

---

## 4. 逐模块审核判断（按实际 JSON 原字节 SHA）

### 4.1 gameplay 四篇（A 代写；此前无独立审核，属 12 份 pending）

| entry | 文件 | 基线原字节 SHA | 基线决定 | PR#42 原字节 SHA | PR#42 决定 |
|---:|---|---|---|---|---|
| 3038 | hero | `f4b276b70609ce668d08bce184de930698cb733ee2795a1fda962c395d5112c3` | changes_requested | `75a8fe1074967a6125de05a569ac2b669632a1e7e6dee387c6a0d8a4fd3a916a` | accepted（模板） |
| 717 | dlgitem | `f2877ccf38925edcd1547a6d3d248ea8bdca4ca40fa690c4ac3cd148813e2382` | changes_requested | `59f17f879663241bc013d946f0ac2b5cdc9e0596d703efed612604db3f8f2f4d` | accepted（模板） |
| 1129 | task | `5a3d4b9f24a5c75884e7608cdd0e16749b328a1f73edfd5dcf34aa37c3fa84d9` | changes_requested | `35861348caf819b147087a5b6676a95a1d4aa1355e1dee91467e4aa0cd608f1c` | accepted（模板） |
| 949 | npc | `738877ff88e071f7fdf66549301dfb795987352c63e6cdb6d31ed7c7496dd23e` | changes_requested | `965e88b5e5c2b4f6494bc74af01ef58ed617e37da7016121a7209b5c2ed3c459` | accepted（模板） |

基线退修（均为本会话按候选原文独立核出）：

- **H01** `hero` `SavePrivateData/summary` 末句「手册未调用此写盘函数」——无证据的全称否定，违反 CONTRACT§3「不能把未发现写成不存在」。
- **H02** `hero` `GetHeroShow/calls` 未列候选实际出现的 `juben.IsForceEnd`、`hidecatcat.IsHeroInGamePlayer`、`racingspeedgame.CheckGameStart`、`GetHeroID`、`oCheckShow.IsHaveReason/IsOnlyReason`。
- **H03** `hero` `sources` 的 `kind` 为 `metadata`，实为候选源行摘录，应为 `recovered_source`。
- **D01** `dlgitem` `ShowDlg/summary`「关闭交易赠予窗口」越出证据——`CloseOtherUI`（L2558-2562）只调 `dlgswap.CloseWindow()` 与 `dlggive.CloseWindow()`。
- **D02** `dlgitem` `relationships[0] hero.GetRealID` 标 `upstream/imports`，实为 L2452 `netopenui.C2SOpenPlayerInfoDlg(hero.GetRealID(), 0)` 的主动调用，应 `downstream/calls`。
- **D03** `dlgitem` `@syncoperate.Operate()`（L2613）只在 limitations 提及、无行号证据。
- **D04** `dlgitem` `PreShowDlgAfterLogin` 条件为意译，应落到 `permission.IsTestBansys('dlgitem')` / `gamectrl.IsFristRunFromOpenSys()`。
- **T01** `task` `TaskUnSatisfy/summary`「读取未满足描述」——候选 L768 `desc = g_UnsatisfyTaskID2Desc.get(tid)` 后 `desc` 无任何引用。
- **T02** `task` `RefreshNecessary` 未写明 `petTaskList` 为空/假值时解包可能异常。
- **T03** `task` `CheckNpcFlag`「国家/职业相关额外门禁」笼统，实为 `country==0 且 tasktype∈LIMITCOUNTRY_TASKTYPE` 与 `zy==0 且 tasktype==18`。
- **N01** `npc` `CNpc.LeftUp/summary`「依剧本婚礼…分流」——该判断在 `IsLimitClick()`（L310-314），LeftUp 仅 L336 调用它。
- **N02** `npc` `NpcNeed/summary`「按候选key/出生标志过滤计数」含糊，实为 `m_Key&64==0` 或（`m_Key&pet.MARK_SOUL_BINDED` 真且 `m_BirthKey==0`）。
- **N03** `npc` 模块常量（L13-18）未登记为证据；`RightUp`「1 的时间比较」应写明 1 秒。

PR#42（N6）复核：上述 13 项**逐条已消除**，且 N6 新增的 5 条证据
（`npc_module_constants`→L13-18、`npc_CNpc_IsHeroSummon_IsHeroChild`→L266-277、`npc_CNpc_IsLimitClick`→L310-314、
`dlgitem_CloseOtherUI`→L2558-2562、`dlgitem_ShowDlg_decorator`→L2613）**绑定正确**，与本会话重跑候选逐字一致。
语义抽查：hero 13 个函数**全部**逐行核对与 Claims 一致；dlgitem/npc/task 关键入口与全部修订项逐一核对一致。

> 提示（不阻塞）：PR#42 `hero.json` 的 `limitations` 仍写「作者是A代写，不是G会话提交或独立审核」，
> 与已改为 `N6新会话（接管修订…）` 的 `author` 字段不一致，建议同步措辞。

### 4.2 mainmenu 219（PR#41 / N3）

- 基线 `a88bd387abcc8e0edcb3f6a1dd0258a922ef149332c3f16f66e63238f8cee48d` → **changes_requested**（原位更新 A_delegate → H）
- PR#41 `87525f6936f2818def3e30fbc729f29e1a428d863e929ec4f74c55cbd892a4e8` → **accepted（模板）**

机器计数**8 项全部独立复算吻合**（详见 §5）。D1 成立：`PushCall` 去头 L377-385 内 `g_MainMenu` / `func(` / 控制流关键字命中**均为 0**，本体只有 `_g_Callback.append((func,args))` + `return`。
保护项实测：interface/key/chatoutput 三份 JSON + evidence 下 7 份共享证据 + `reviews/` 8 份记录**全部 UNCHANGED**。

### 4.3 网络四篇（PR#40 / N4）

| entry | 基线 SHA | 基线决定 | PR#40 SHA | PR#40 决定 |
|---:|---|---|---|---|
| 3176 net | `e00bd3e82ff47faf1d93b4f29a4916a54c484ce252c84a023850619ba9039a1d` | changes_requested | `17c3a9956859c5c22ac61e362d1f5458d9cc5168b042522aa16b5a27eebeab90` | accepted（模板） |
| 2170 connect | `3c32bc2397114566c1fe35dcb32036ff695f33e9da4b0f734f0145f198e323e9` | changes_requested | `505977078ec047c3584311ed3f25e8a2547e70a13ecf874b41e532c84fe21ba3` | accepted（模板） |
| 871 netquicklogin | `9c2a8cd021148264f1069469fdb366e1857d4ebc3c80004f3cbb2c3ea52ce678` | changes_requested | `55b81261b69494667555e03f64c9cabf69c36a8f0d6383eaa6e0edb961062850` | accepted（模板） |
| 516 netserver | `0eca5474ea815ad5269c4659db590344ec504399aa2778ef3db2eca41d961621` | changes_requested | `1ec1bc8f6bc812f24d27520c22036461cd4301c307e7e56ec0d0e6df2ec59fef` | accepted（模板） |

A 的十条发现（N1/N2/N3、Q1/Q2、S1–S4、C1）本会话**逐条按候选原文独立复算，全部成立**（行号见各 review note）：
net.py L902-903、L62/L67/L69、L702；netquicklogin L24-39、L242-244；
netserver L293 + L441-442、L287-289、L70-99（含 L77 完整 OR 谓词与 L98-99 外层 HTTP）、L462-465；
connect L190-196。PR#40 十条**全部已消除**，新证据 R 行号与本会话重跑候选逐字一致，前轮已改正项未见回退。

### 4.4 ui_chat 三篇（维持 accepted，原位更新为 H）

| entry | SHA | 决定 |
|---:|---|---|
| 3854 interface | `a8c3ddf43ef74a6a0fe4319dc6922233ae9e44583523fe26d72830a3d9258318` | accepted（有限范围） |
| 3232 key | `745bd2579c85ab7e1faf9deb78fd37cedb23bb0a5e322b398064a2c8ed4f4b0f` | accepted（有限范围） |
| 4832 chatoutput | `bb4b492a400adfcb7812b255e76c51a0c655e24e34c0f49121448959068bf799` | accepted（有限范围） |

抽样核对（**非全函数穷尽**，已在 note 中写明）：
`CClickBox.__init__` 候选 L1087 `(self, parent, w, h, color=0, alpha=256, msgid=0)` 与 JSON 逐字一致（本项目 CClickBox 签名事故的教训未回退）；
`RegisterHotKey` L142 / `RegisterHotKeyEx` L161 / `IsHotKey` L188 / `GetCallFunc` L204 与 JSON 一致；
`AddChat` L1778-1784 证实**先 `g_Chats.append` 再 `if not g_CurChatOutput: return`**，JSON 的“缓存先于无窗口返回”顺序正确。

> A_delegate 的 accepted **不是独立审核**。本会话按实际字节重新核对后维持结论，但这是**有限范围**的维持，
> 不代表全模块已解释、候选可回编或游戏行为正确。

### 4.5 login 四篇（PR#39 / N2）—— 基线退修，PR#39 **本轮不验收**

| entry | 基线 SHA | 决定 |
|---:|---|---|
| 4806 loginin | `76b2fea23dbcaf49b4c146e9cfe1a3de21512beba393672e9d3c3f1963f47b5f` | changes_requested（L01–L03） |
| 337 mainpage | `bcb980a3271c5cb90f643dd04563e0e7fdd36b93da748c942ad14a14c75ad511` | changes_requested（L04–L06） |
| 4293 main | `361b5a067f40ffe3f9f3f7b75689f748c45b60ff4bb407f31b745f8eadc7a5bd` | changes_requested（L07–L10） |
| 4007 register | `8dcdf564b029821d4ae8a54bfd7adbeb47a44ddca0a2a839a3abe8eaa9373f4a` | changes_requested（L11–L13） |

已核实的矛盾：候选 `LoginOk`（L252-269）**不保存账号**，`OnLogin`（L663）才走 `SaveAccount`——
基线 `loginin.json` 那条「LoginOk保存账号；网络连接由 netserver.RandomConnect 与 netlogin 处理」与同文件 summary、
`main.json` 三方互相矛盾。协议勾选检查**只在 `not misc.IsTWServer()` 内**（L583）。
公告地址选择实际在 `mainpage.OnMessage(30)` **L232-L249**（含 180 秒节流 L234-239），基线证据未覆盖。

**PR#39 本轮不给结论**：已核对 N2 对 C 预审第 1、2 项的修正（文本已与候选 L252-269、L583-589 一致），
但第 3 项（逐 Claim 证据覆盖）、第 4 项（方向/kind）、第 5 项（main 来源保真链）**尚未逐条复核**。
与其发一个未经核实范围的 accepted，**留到下一批**；详见 §7。

### 4.6 battle 四篇（无新 PR）

`war / netwar / warcmd / e_warctrl` 当前**无对应新 PR**（N5 未交付）。基线四篇仍属 pending，
本轮**未审核、未给结论**，不因已合并而放行。F 的 173 条多为名称底稿，仍不等于已解释。

---

## 5. 独立复算的机器计数（N3 / mainmenu 219）

| 核对项 | N3 自报 | 本会话实测 | 一致 |
|---|---|---|---|
| `PushCall` L377-385 非空非注释行 | 9 | 9 | ✓ |
| 其中 docstring 占位 | L378-383（6 行） | 同 | ✓ |
| 可执行语句 | L384 append + L385 return | 同 | ✓ |
| L377-385 内 `g_MainMenu` 命中 | 0 | 0 | ✓ |
| L377-385 内 `func(` 命中 | 0 | 0 | ✓ |
| L377-385 内控制流关键字命中 | 0 | 0 | ✓ |
| 裸名 `_` 全量出现 | `[1279]`，计数 1 | 同 | ✓ |
| `_` 绑定形态（`_ =`/`for _ in`/`import … as _`） | 0 | 0 | ✓ |
| `_g_Callback` 出现 | `[8,11,14,384,1278,1279,1284]`，7 处 | 同 | ✓ |
| `PushCall` 出现 | `[377,465,1223]` | 同 | ✓ |
| `Recall` 出现 | `[159,1277]` | 同 | ✓ |

调用者侧：L461-465 `if g_MainMenu → dlggm.ShowGMButtonDlg / else → PushCall(ShowGmBtn, bShow)`；
L1221-1223 先 `commoncb.TriggerCB` 再 `if not g_MainMenu → PushCall(OnPlayerMailNotify, bNotify)`；
L157-159 `elif g_MainMenu is None → CMainMenu(...) → Recall()`；`ModuleReset` L11/L14 清队列、L8 为初值。**全部逐行一致。**

---

## 6. 实际执行的命令与结果

| 命令 | 结果 |
|---|---|
| `PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .` | 退出 0；`{"expected_entries":5135,"indexed":5135,"annotated":20,"accepted":3,"excluded":1}` |
| `PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests` | **82 项 = 71 通过 + 11 跳过 + 0 失败**（跳过原因：`PySide6/系统Qt库缺失；GUI未执行，不计通过`） |
| `ruff check script_manual script_manual/script_manual.spec` | All checks passed（ruff 0.17.1） |
| `python tools/devkit/check_windows_compat.py script_manual --strict` | 140 文件名 / 27 脚本；ERROR 0 WARNING 0 INFO 0 |
| PR 覆盖层 validate（PR#39/40/41/42/43） | 全部退出 0；PR#40/PR#41 按预期输出“审核过期”stale 警告 |
| `unittest discover -s script_manual/inventory -p test_signature_metadata.py`（PR#43） | 32 项全通过；反向对照旧代码 13 失败 + 16 错误 |
| 冻结 20 种子 → `--sample` → `--full`（隔离树） | 三份产物与 PR#43 交付**逐字节一致** |
| 各 PR 保护路径 `sha256sum` 比对 | PR#41 的 3 份 JSON + 7 份共享证据 + `reviews/` 8 份全部 UNCHANGED |

### 未执行 / 明确跳过（**一律不计为通过**）

- **11 项 Qt GUI 测试**：`test_gui*`，含中文与函数名搜索、按路径列目录与覆盖率、模块跳转、审核身份与绑定 SHA 展示、tab 展示。
  这些正是“路径/中文/函数搜索、模块跳转”验收点的主要承载用例，本轮**未执行**。
- **真实浏览器 / jsdom**：本会话未运行（历史 jsdom 结果属 A，不属本会话）。
- **Windows / EXE / 游戏实机 / 原生引擎 / 服务端**：全部未执行。
- **离线 HTML 构建**：未生成站点（仓库外产物不入 Git）。

---

## 7. 仍未通过的验收项 / 交 A 处理

1. **login 四篇（PR#39）未验收** —— C 预审第 3/4/5 项未复核完；下一批优先。
2. **battle 四篇（N5）无 PR** —— 完全未审；请 A 催 N5 交付或明确延期。
3. **证据行号约定未统一** —— gameplay 摘录未写明“行号指摘录文件自身行”，ui_chat 写了。建议 A 在 CONTRACT §3 统一（本会话差点据此误判，见 §3）。
4. **目录回归测试未接入标准套件** —— `script_manual/inventory/test_signature_metadata.py` 不在 `script_manual/tests` 发现范围内，且需 `PYTHONPATH=.`（仓库根）才能 import `script_editor.core.archives.flsdata`，否则直接 `ModuleNotFoundError`。这 32 项在常规验证里不会被执行。
5. **N1 的 186 条“非标识符形参置 null”是超出 A 所列 48 条的范围判断** —— 已在 N1 响应 §2b 声明并给出可逆方式，但**应由 A 显式确认**，审核不代批。
6. **N1 反证树构成请在响应中写明** —— 本会话用“旧代码+旧数据”得 13 失败 + 16 错误；N1 自报“6 项交付数据失败 + 25 合成通过”（应为“新代码+旧数据”）。结论一致，口径需对齐。
7. **PR#42 hero.json limitations 与 author 不一致** —— 建议 N6 同步措辞（不阻塞）。
8. **11 项 Qt GUI 测试长期跳过** —— 建议 A 在具备 Qt 的环境补跑，否则“路径/中文/函数搜索、模块跳转”的验收点始终无实据。

---

## 8. 交付物清单（全部在 `script_manual/reviews/` 内）

- `8b6e9266_{3038,717,1129,949}.json` —— gameplay 基线退修（H）
- `8b6e9266_{3038,717,1129,949}.json.template` —— PR#42 暂存 accepted，**A 合并后按绑定 SHA 核对再改名为 `.json` 激活**
- `8b6e9266_219.json` / `.json.template` —— mainmenu 基线退修 / PR#41 暂存 accepted
- `8b6e9266_{3176,2170,871,516}.json` / `.json.template` —— 网络基线退修 / PR#40 暂存 accepted
- `8b6e9266_{3854,3232,4832}.json` —— ui_chat 原位更新为 H，accepted（有限范围）
- `8b6e9266_{337,4293,4007,4806}.json` —— login 基线退修
- `reports/N7_inventory_review.md` —— 目录语义验收（20 种子复现、签名修复、1288 边界）
- `reports/N7_acceptance.md` —— 合并态验收六题 + 集成闸门实测
- 本文件 `reports/N7_RESPONSE.md`

未改动任何作者正文、未改 `src/` / `schema/` / `tests/`、未改原包/参数/编辑器/启动器、
未 import/eval/exec 任何恢复稿、未定点恢复 1288、未请求业务 URL、未上传网盘或改权限。
