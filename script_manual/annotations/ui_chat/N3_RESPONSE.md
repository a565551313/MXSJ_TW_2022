# N3_RESPONSE · 主菜单（entry 219）D1 返修与三篇已通过 UI 说明保护

> 交付者：**N3**（全新 Arena 会话；逻辑任务包 D / ui_chat）。不是旧 D 会话，未复用任何旧 B–H 分支。
> 任务卡：`script_manual/coordination/new_agents_20261016/N3.md`（版本标识 `20261016-new-cohort-v1`）
> 范围：只改 `script_manual/annotations/ui_chat/mainmenu.json` 与新增 `script_manual/annotations/ui_chat/evidence/mainmenu_d1_deferred.txt`，外加本文件。

## 1. 实际基线与作者会话

| 项 | 实际值 |
|---|---|
| Arena 固定分支 | `arena/10debde2-mxsj-tw-2022`（未切换、未新建其他工作分支） |
| 交接基线 | `9b0dea799768aaacbb967ffc59f45753970752be` |
| 集成分支 | `arena/61deb9e5-mxsj-tw-2022`；`git ls-remote` 显示其 head 同为 `9b0dea7` |
| `git merge --no-edit FETCH_HEAD` | 输出 `Already up to date.`（本地已在该提交上） |
| **实际开工 SHA** | `9b0dea799768aaacbb967ffc59f45753970752be` |
| 合并内容检查点 | `7d32e5340b0ab4168f725d238d767ad6232f715d` **已验证在祖先中** |
| 会话起始工作树 | 干净（`nothing to commit, working tree clean`），无既有未保存工作需先提交 |
| `author` 字段 | 由 `D` 改为 `N3（全新会话；逻辑任务包 D / ui_chat，非旧 D 会话）`；`owner` 仍为 `D`（schema enum 限定，逻辑归属不变） |

本地克隆是 **shallow**，检查点一开始取不到对象；用 `git fetch --deepen 50 origin` 取回后
`git merge-base --is-ancestor 7d32e534… HEAD` 返回 0。未追浮动分支、未改用 master。

### 锁定输入本机核对（全部相符）

```text
8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72  data/script.fls      ✓
5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c  data/data.fls        ✓
43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb  tools/decompiler/script_fls_keys.json ✓
```

## 2. 候选复现：与 D 原报告**逐字节相同**

分析环境建在**仓库外**（`/home/user/mxsj-recover-venv`），按已核版本装：
Python **3.11.2** / uncompyle6 **3.9.3** / xdis **6.1.8** / spark-parser **1.9.0**（与 D 原报告同版；未混入编辑器 dev6 的 3.9.4.dev0 / xdis 6.3）。

```bash
<仓库外venv>/bin/python tools/decompiler/recover_entries.py \
  --out /home/user/n3_ext/recover219 --entries 219 \
  --decompile-timeout 30 --report /home/user/n3_ext/recover219_report.json
# → 处理 1 条，用时 0.9s → {'recovered': 1}；entry 219 recovered / source / script/mainmenu.py
```

`status=recovered`、`stage=baseline`、`repaired=False`、`decompile=decompile_ok`、`path_class=ok`；
`entry_id=177381689(0x0a92a139)`、`keys_used=[82,66,131,42,233]`、`bounds_used=[8389,16778,25091,33374]`、
`stored payload SHA256` 前 16 位 `c9835c4b13272697`（与 D 原报告一致）。

| 产物 | SHA256 | 字节 | 行 |
|---|---|---|---|
| 本次原始落盘（含 `recover_entries.py` 自加的 6 行 `# MXSJ 恢复产物` 头） | `65bf5f83cd27c3e483ca074d1e462eabe007a42e2cbc8baf35dcd9fe0c761e4f` | 43119 | 1294 |
| 去掉开头 **恰好 6 行**恢复头之后 | `e03d31ac8deaab37766addcab9e2a1a63dd1b3c223e977cfe3f427b80df05bfd` | 42790 | 1288 |
| D 原报告钉的候选 | `e03d31ac8deaab37766addcab9e2a1a63dd1b3c223e977cfe3f427b80df05bfd` | 42790 | 1288 |

**结论：MATCH（SHA / 字节数 / 行数三项同时吻合）。**

诚实声明（按任务卡「若实际候选头不同，钉新输入/SHA 并解释，不能扩大去头/忽略范围凑旧摘要」）：
去头范围**恰好**是工具自加的 6 行恢复头，D 原报告编号也从 `# -*- coding: utf-8 -*-` 起算，
所以两套行号可直接对齐；**没有**为了凑旧摘要而扩大去头/忽略范围或改动比对方式，
**两个 SHA 都登记**在此，未只报对得上的那一个。下文一切候选行号均为去头候选（= D 原编号）。

## 3. D1 逐项修复（函数 / 调用 / 问答三层同步）

### 3.1 机器核对结果（由候选自动计算，非人工目测）

| 核对项 | 结果 |
|---|---|
| `PushCall` L377–L385 内非空非注释行 | 9 行；其中 docstring 占 L378–L383（6 行）→ **可执行语句只剩 2 行**：L384 `_g_Callback.append((func, args))`、L385 `return` |
| L377–L385 内出现 `g_MainMenu` 的行 | **0** |
| L377–L385 内出现 `func(` 直接调用的行 | **0** |
| L377–L385 内出现控制流关键字（if/elif/else/try/except/finally/while/for/with）的行 | **0** → 本函数没有任何分支 |
| 裸名 `_` 在整份 1288 行候选中的出现 | 命中 `[1279]`，计数 **1**（只被读取，就在争议行本身） |
| `_` 的绑定形态（`_ = …` / `for _ in …` / `import … as _`） | 命中 **0** |
| `_g_Callback` 全部出现 | `[8, 11, 14, 384, 1278, 1279, 1284]`，计数 7 |
| `PushCall` 全部出现 | `[377, 465, 1223]` → 排除定义行后**调用点 2 处**：L465、L1223 |
| `Recall` 全部出现 | `[159, 1277]` → **唯一调用点 L159**（在 `Show(s)` 的 `elif g_MainMenu is None` 分支内） |

### 3.2 必做清单第 1 项 —— PushCall

- **旧**（`functions/PushCall/summary`，失真）：「主界面存在立即调用外部传入 func；不存在则把 (func,args) 存入 _g_Callback，Recall 逐个调用后清队列。」`calls: ["func"]`
- **新**：按候选字面改为**无条件入队**——本体只有 L384 append + L385 return，函数内无 `g_MainMenu` 判断、无 `func` 直接调用、无任何控制流关键字（三项计数 0）；并写明「存在就立即做、不存在才排队」的分支其实属于**调用者**：`ShowGmBtn` 在 `if g_MainMenu` 走 `dlggm.ShowGMButtonDlg`、**else** 才 `PushCall(ShowGmBtn, bShow)`（L461–L465），`OnPlayerMailNotify` 先 `commoncb.TriggerCB`、再 `if not g_MainMenu` 才 `PushCall(OnPlayerMailNotify, bNotify)`（L1221–L1223），两处都把**自身**作为 func 入队。
- `calls`：`["func"]` → `["_g_Callback.append"]`（不存在的直接调用已移除；空/短 calls 不表示无调用）
- **没有**补想象中的立即执行分支；`branches` 仍为 `[]`。

### 3.3 必做清单第 2 项 —— Recall（新增函数记录）

原稿**没有** `Recall` 独立条目，只在 `Show` 里被顺口说成「Recall 待处理回调」。本轮新增
`functions/Recall`（`signature: "()"`, `kind: "function"`），插在 `PushCall` 之后使延迟回调成对相邻：

- 只登记候选声明的字面流程：`global _g_Callback`(L1278) → `cl = [_[1] for x in _g_Callback]`(L1279) → `for (cb, args) in cl: print cb, args; cb(*args)`(L1280–L1282) → **无条件** `_g_Callback = []`(L1284) → `return`(L1285)。
- 登记推导式异常：循环变量是 `x` 而表达式取 `_[1]`，两者不对应；裸名 `_` 在候选内无绑定，故 `cl` 不保证取得队列里的 `(func,args)` 对，紧随的解包也就不保证逐个回调正常完成。
- 执行成败一律标 **待核**：NameError / ValueError / 能正常回放 / 该行本属转译器伪影，四种可能都未排除（`decompile_ok` 不证明语义正确）。
- `calls: []` —— 唯一调用 `cb(*args)` 的目标来自队列、属动态调用，按契约不写死；已在正文明说「空 calls 不表示无调用」。
- `branches: []` —— **没有**给候选补分支，也没把候选修好当原文。
- 连带限定 `Show`：summary 与 `branches[1]` 由「Recall 待处理回调」改为「调用 Recall()（L159）回放排队回调；此处只确认调用发生，逐个回调是否被执行待核」。

### 3.4 必做清单第 3 项 —— 必须保留的内容（已逐条复验，全部保留）

| 项 | 复验结果 |
|---|---|
| `source_status = recovered_partial` | 保留，与旧值一致 |
| 219 候选 L305 损坏 import 标识符的 limitation | 保留，与旧值**逐字一致** |
| 菜单 4 号 `SS_ClickSkill` 实际委托锻造（`makeequipctrl.GetMakeEquipDlgCtrl`）、「不能仅凭 Skill 写成技能面板」 | 保留；`CMainMenu.OnHotKeyMsg` 整个函数记录与旧值**完全相同** |
| 多订阅关系（「候选多处 ssConnect 订阅同一信号」「不能假定只有一个处理者」） | 保留，`relationships[3]` 与旧值相同 |
| 问答「4→SS_ClickSkill 实际走锻造，技能页另有 skillmagicsignal 入口」 | 保留，`modification_guides[0]` 与旧值相同 |
| 动态回调未知 | 保留并**收窄**（见 3.5），未退回按名字猜 |
| `runtime_verified` 计数 | **0**（与旧稿一致；本轮无任何实机记录） |

### 3.5 其余同步纠正

- `relationships[6]`（`module=null, symbol=null`）：旧文「PushCall/Recall 中的 func 来自调用者，运行期具体对象未知」把**可静态确认的部分**也说成未知。改为：entry 219 候选内可静态确认的调用点只有 L465 `ShowGmBtn` 与 L1223 `OnPlayerMailNotify`（都把自身入队），Recall 回放时才执行 `cb(*args)`；**跨条目调用者本工作包未检索，属未知**，不把「未检索」写成「不存在」。confidence 由 `inferred` → `static_reviewed`（依据是已读并核对的候选文本，非自动升级）。
- `limitations[2]`：删掉已不准确的「PushCall 传入目标…未确认」，改为「PushCall 在 entry 219 候选内只有 ShowGmBtn(L465)/OnPlayerMailNotify(L1223) 两个调用点，跨条目调用者未检索，Recall 回放的运行期成败未验」。
- 新增 `limitations[9]`：Recall 推导式异常只登记字面、未修候选、未判定实机、未排除转译器伪影。
- 新增 `limitations[10]`：新证据只放 N3 专用文件；三篇已通过 JSON 共用的 7 份证据字节一律未改；mainmenu 旧审核转 stale 是预期，交 N7 对新 SHA 复核。
- 新增 `modification_guides[3]`「PushCall/Recall 这套延迟回调要改，应该动哪里？」：分层指出开关在**调用者**不在 PushCall 本体、回放侧在 Recall(L1277–L1285)、队列另在 ModuleReset(L11/L14) 清空、模块级初值在 L8，并警示改 Recall 前必须注意 L1279 变量不对应、不要把修好的版本当原文语义。

### 3.6 mainmenu.json 差异面（结构性 diff 实测）

| 位置 | 变化 |
|---|---|
| `author` | `D` → N3 会话标识 |
| `functions` | 17 → **18**（新增 `Recall`）；documented branches 仍 17（未造分支） |
| `functions[0] Show` | summary 文本 + evidence（2→4）；`branches[1]` effect 文本 + evidence（1→2） |
| `functions[13] PushCall` | summary 文本 + evidence（1→5）；calls `["func"]`→`["_g_Callback.append"]` |
| `functions[14]` | **新增 Recall**；其后 `CMainMenu.ShowTarget` / `CTargetFrame.OnMessage` / `CTargetPngFrame.OnMessage` 仅索引 +1，三条与旧 `[14][15][16]` **深度相等** |
| `relationships` | 数量不变（7）；仅 `[6]` 变化，`[0]–[5]` 全部未变 |
| `modification_guides` | 3 → **4**；前 3 条与旧值**完全相同** |
| `limitations` | 9 → **11**；仅 `[2]` 变化，其余 8 条未变 |
| `sources` | 3 → **4**；**原 3 条逐字节保留且顺序不变** |
| `evidence` | 17 → **24**；**原 17 条逐字节保留且顺序不变**，新增 7 条追加在尾部 |
| 其余顶层字段 | `schema_version / archive_sha256 / entry_index / path / owner / domain / source_status / purpose / keywords / resources / related_modules` **全部未变** |

> 过程记录：第一次落盘时我顺手对 `evidence` 数组做了排序，导致原 17 条位置全变。已回滚到
> pristine 快照重做，改为**只按现有约定追加**（分组按 `sources` 声明顺序、组内按 id 字母序），
> 现在原 17 条与旧稿逐字节相同、顺序相同，不给 N7 添无谓 diff。

**Claim confidence 分布**：旧 `{static_reviewed:47, extracted:2, inferred:1}` → 新 `{static_reviewed:50, extracted:2}`（`inferred` 归零来自 `relationships[6]` 的有据升级）。`runtime_verified` 两版均为 **0**。

## 4. 必做清单第 4 项 —— 新增证据，未动任何共享字节

新增 `script_manual/annotations/ui_chat/evidence/mainmenu_d1_deferred.txt`
（**只供 mainmenu.json 引用**）：

| 项 | 值 |
|---|---|
| SHA256 | `dc43e5560cb5aee6d06987b1d505f564e2b1ba81e2056f4826dda1ffd7cfe504` |
| 字节 / 行 | 11209 / 171（LF、无 CR、有效 UTF-8；`script_manual/.gitattributes` 为 `* text=auto eol=lf`，已 `git check-attr` 确认） |
| `sources.id` | `report_mainmenu_d1`（`kind=metadata`） |

新增 7 条 evidence（source_id 均为 `report_mainmenu_d1`，行号指**本报告**实际行，与候选行号严格分开）：

| id | start–end | 内容 |
|---|---|---|
| `d1_reproduce` | 19–37 | 复现命令、恢复记录、两个 SHA、MATCH 结论与去头诚实声明 |
| `d1_pushcall_body` | 39–64 | PushCall 完整函数体原样摘录 + 四项机器计数 |
| `d1_recall_body` | 66–84 | Recall 完整函数体原样摘录 + 字面形态说明 |
| `d1_underscore_scan` | 86–94 | 裸名 `_` 全量扫描与边界（运行期结果待核） |
| `d1_callback_refs` | 96–106 | `_g_Callback` 全部 7 处出现及读法 |
| `d1_deferred_callers` | 108–163 | 两个 PushCall 调用点所在函数全文 + Recall 唯一调用点 + 未覆盖范围 |
| `d1_scope` | 165–171 | 本报告边界与红线声明 |

摘录全部由脚本从**字节相同的复现候选**机械生成（`L%05d: ` + `json.dumps(line, ensure_ascii=False)`，
与 D 原 `mainmenu.txt` 同一格式），未手工转录、未更名、未补分支、未修乱码；乱码 docstring 按原文保留且未猜其中文含义。

**改证据前先查共用者**：实测 `provenance.txt` / `support.txt` / `mainmenu.txt` / `chatoutput.txt` /
`interface.txt` / `key.txt` 被已在 A 有限通过的 interface(3854)、key(3232)、chatoutput(4832) 以 SHA 共同引用
（`mainmenu.txt` 四篇共用）。因此本轮**一份共享证据都没改**，D1 新证据一律走新文件，
无需向 A 申请共用来源修订。

## 5. 必做清单第 5 项 —— 三篇已通过内容逐条复验（**未动**）

改动前后各做一次 `sha256sum`，并对三篇逐条比对「JSON 原字节 ↔ review 绑定 SHA ↔ 全部来源 SHA ↔ 证据行号范围」：

| 文件 | 原字节 SHA256（改前 = 改后） | review 绑定相符 | 全部来源摘要相符 | 证据行号在范围内 | reviewer / delegation / decision |
|---|---|---|---|---|---|
| `interface.json` (3854) | `a8c3ddf43ef74a6a0fe4319dc6922233ae9e44583523fe26d72830a3d9258318` | ✓ | ✓（6 个来源全 OK） | ✓ | `A_delegate` / 非空 / `accepted` |
| `key.json` (3232) | `745bd2579c85ab7e1faf9deb78fd37cedb23bb0a5e322b398064a2c8ed4f4b0f` | ✓ | ✓（6 个来源全 OK） | ✓ | `A_delegate` / 非空 / `accepted` |
| `chatoutput.json` (4832) | `bb4b492a400adfcb7812b255e76c51a0c655e24e34c0f49121448959068bf799` | ✓ | ✓（4 个来源全 OK） | ✓ | `A_delegate` / 非空 / `accepted` |

共享证据文件（改前 = 改后，全部 `sha256sum -c` OK）：

```text
d3af89258166a961d4774e64500048a610ea01d904431802f1e53684d49bd4b4  evidence/chatoutput.txt
f77a860eb09e3cd633987da3d179b4639b4d1194522e927cdfd6841f366c7f87  evidence/interface.txt
fba55fa88c872e1d1b1a499d63373369e475e87cc4f9907a3344385780c00860  evidence/key.txt
9eaed517871aac63f1523dc3b29c4cc0adf628e31b385395723882dc0a0068d7  evidence/mainmenu.txt
41b341949b2c7c9c086a7d46b2083137f3a5f1a5c006563dcc55d972fdea7998  evidence/provenance.txt
f7896042c8b14af9303ff523e61b468f6fe0daadee124f9ea13bdbfce21ba1d9  evidence/support.txt
fbc8baeea9ba588de2b2deae7b8d699a55704669949850b7c9832f6b687b6272  evidence/validation.txt
```

`script_manual/reviews/` 下 **8 份记录全部未动**（含 `8b6e9266_219.json`，其自身 SHA
`a0fec43a09d71c1f1d1f04dfaf3354b0a5358df45b958d9ca6fd7244c6ba5376` 与 A 机器收据里的
`staged_review_sha256` 一致）。`reviews/` 不在本卡允许路径内，本轮未自行改旧 review 去「恢复通过」。

**本轮改动面实测只有 2 个文件**（对 19 个受保护路径做改前/改后 `sha256sum` 比对）：
`mainmenu.json`（预期修订）与新增 `evidence/mainmenu_d1_deferred.txt`。其余 17 个路径全部 OK。

三篇仍只是**有限通过**：不据此宣称全模块已解释、候选可回编、原生或实机通过。

## 6. 实际命令与结果（本机实跑，非引用历史）

```bash
# 1
PYTHONPATH=script_manual/src python -m mxsj_manual validate \
  --verify-evidence --require-full-inventory --repository .
# → {"expected_entries": 5135, "indexed": 5135, "annotated": 20, "accepted": 3, "excluded": 1}
# → WARNING: 说明已变化，审核过期：8b6e9266…c0d72:219      RC=0
#   accepted 仍为 3（219 原 decision 本就是 changes_requested，不计入 accepted）
#   该 WARNING 是任务卡预期的 stale，交 N7 对新 SHA 复核

# 2
PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest \
  discover -s script_manual/tests
# → Ran 82 tests … OK (skipped=11)      即 71 通过 / 11 跳过 / 0 失败

# 3
ruff check script_manual script_manual/script_manual.spec
# → All checks passed!      RC=0

# 4
python tools/devkit/check_windows_compat.py script_manual --strict
# → 文件名检查 122 项，源码/脚本扫描 27 个；ERROR 0，WARNING 0，INFO 0      RC=0
```

改前基线同样实跑过一遍，结果一致（validate RC=0 / accepted 3；82 项 71 过 11 跳；ruff 通过；
wincompat 文件名 121 项、ERROR 0 WARNING 0 INFO 0）。改后文件名检查 121→122，正是新增的那份证据文件。

## 7. 未跑 / 保留风险

1. **11 项 Qt 跳过不是通过**：沙箱缺 `libGL.so.1`，`test_gui*` 等 ImportError 跳过。按 AGENTS §3 记为**未执行**。
2. **无真实浏览器 / 真实 Qt**：本轮未跑离线 HTML 构建与 jsdom 页面脚本验证（那属 A 的集成验证链，且不在本卡允许路径内）。
3. **无 Windows / EXE / 游戏 / 原生 / 实服验证**；`runtime_verified` 计数 0。Linux 侧结论不得当作 Windows 或实机可用。
4. **Recall 运行期结果仍待核**：NameError / ValueError / 正常回放 / 转译器伪影四种可能都未排除。本轮只登记候选字面，未修候选、未判定实机行为。
5. **跨条目 PushCall 调用者未枚举**：本卡白名单只有 entry 219，未做多条目恢复或全量语料检索（也未下载 79 MB 语料）。已在 `relationships[6]`、`limitations[2]` 与证据 `d1_deferred_callers` 明确标为未知，未写成「不存在」。
6. **`mainmenu.json` 旧审核已 stale**：原绑定 `a88bd387…48d`（decision `changes_requested`），新原字节 SHA256 =
   **`87525f6936f2818def3e30fbc729f29e1a428d863e929ec4f74c55cbd892a4e8`**。请 N7 按新 SHA 独立复核；
   本轮**未**改 `reviews/8b6e9266_219.json`，也未自行恢复通过。
7. 完整候选、pyc、恢复产物、两个 venv 全部留在仓库外 `/home/user/n3_ext/`、`/home/user/mxsj-*-venv/`，未搬入 Git；未生成站点、未装 npm 依赖。
8. 未改原包 / 密钥库 / 参数 / 编辑器 / 启动器；未 import、eval、exec 任何恢复稿；未定点恢复敏感条目 1288（仅目录元数据用于排除范围断言）；未请求业务 URL、未上传网盘、未改权限。
9. 结论仅适用 `archive_sha256=8b6e9266…c0d72` 的 entry 219，不外推注册派生包、PR34 清单或其他引擎候选。
10. 身份仍以 `(archive_sha256, entry_index)` 为准；`path` 只作展示，未用 entry ID 伪装路径。

## 8. 完成标准对照

| 任务卡完成标准 | 状态 |
|---|---|
| D1 在函数 / 调用 / 问答层同步纠正 | ✅ `PushCall` summary+calls、新增 `Recall`、`Show` summary+branch、`relationships[6]`、`limitations[2]`+2 条新增、新增 1 条问答 |
| 改后主菜单旧审核变 stale 是预期，交 N7 对新 SHA 复核 | ✅ validate 明确 WARNING；新 SHA 已报（`87525f69…a4e8`） |
| 其余三个已通过 JSON 和关联来源原字节保持不变 | ✅ 3 篇 JSON + 7 份共享证据 + 8 份 review 全部 `sha256sum -c` OK |
| accepted 仍至少 3 | ✅ validate 实测 `"accepted": 3` |
| 不擅自把候选修好当原文 | ✅ 未修候选；异常只登记字面并标待核 |
| 不改共享证据字节使三份审核失效 | ✅ 新证据走 mainmenu 专用新文件 |
