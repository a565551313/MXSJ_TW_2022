# N6 响应：gameplay 四篇接管核对与修订

> 作者会话：**N6 新会话**（Arena 新 agent）。逻辑任务包 G / gameplay，owner 仍为 G。
> 本报告只记录 N6 的独立核对与修订。**N6 不自批，未写入 `reviews/`，未做 accepted 判定**；四篇仍需 N7 按修订后的 JSON 字节独立复核。
> 所有 claim 的 confidence 仍为 `static_reviewed` 或 `inferred`（未运行），不是 runtime_verified。

## 1. 分支与基线

| 项 | 值 |
|---|---|
| 固定分支 | `arena/6f7784e1-mxsj-tw-2022`（未切换、未新建、未推送到其它分支） |
| 开工 HEAD | `9b0dea799768aaacbb967ffc59f45753970752be`，工作区干净 |
| 集成分支 | `origin/arena/61deb9e5-mxsj-tw-2022` = `9b0dea7`，`git merge` 为 Already up to date |
| 检查点 | `7d32e5340b0ab4168f725d238d767ad6232f715d` 为 HEAD 祖先 |
| 注意 | 本地为浅克隆，核对祖先关系时执行了 `git fetch --unshallow origin`，只补历史，未改工作树 |

## 2. 独立复现（四个固定条目）

环境（仓库外）：Python 3.11.2 venv，`uncompyle6==3.9.3`、`xdis==6.1.8`、`spark-parser==1.9.0`、`click==8.5.0`。

命令（仓库根，`--report`/`--out` 均在仓库外）：

```bash
/tmp/n6/venv/bin/python tools/decompiler/recover_entries.py --out /tmp/n6/out1 --entries 3038,717,1129,949 --decompile-timeout 30 --report /tmp/n6/rec1.json
```

结果：退出 0，用时 6.9 s，`counts = {"recovered": 4}`，四条均 `stage=baseline`、`repaired=false`、`decompile=decompile_ok`，未超时，未触碰 1288，未跑全量语料。

| 核对项 | 结果 |
|---|---|
| `data/script.fls` SHA256 | `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`（与任务卡固定值一致，且与 rec1 的 `script_fls_sha256` 一致） |
| `tools/decompiler/script_fls_keys.json` | `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`（一致） |
| `recover_entries.py` | `152dbc28864a10c8…`（与 A 收据一致） |
| `batch_decompile.py` | `a74742231e04c018…`（与 A 收据一致） |
| stored_sha256 前缀 | 3038 `930eb0dfac061776`，717 `55322bfd081248c9`，1129 `09505840b0cbd3f6`，949 `45deec3b0ae52005`（与 A 收据四条前缀一致） |
| 去六头正文 SHA256（稳定标识） | hero `e04fe622f96f7b8a…27dce7`，dlgitem `153bae3a3ec02b9d…bcbbb`，task `7169355746d61124…ec764f7`，npc `cf66726ed19a239a…140dfb`：**与 A 收据四条完全一致** |
| 候选行数 | 2927 / 3215 / 1107 / 1235（与 A 收据一致） |
| 整文件 SHA256（本次） | hero `1e69fabb…ea08dd`，dlgitem `3a901e1d…108a575`，task `6a0c1365…318684`，npc `e0b0487e…5972`。与 A 收据不同，因头部生成时间戳随每次重跑变化；**以正文 SHA 作为稳定标识** |

摘录逐行核对（`/tmp/n6/check_excerpt.py`，仓库外）：hero 205 行、dlgitem 225 行、task 224 行、npc 326 行，合计 **980 个 L 行，0 个不一致**。其中包含 A 原有 951 行与 N6 追加的 29 行（dlgitem +6：L2558–L2562、L2613；npc +23：L13–L18、L266–L277、L310–L314）。追加仅在文件末尾，原行号不变。

摘录文件修订后 SHA256：hero `58c5d634…feeb277`（未改），dlgitem `3d2d9796…7a1a`，npc `306145dd…91f5`，task `9b0b94d5…67ca`（未改）。

**复现范围**：只证明四份候选输出形状与正文字节稳定，不证明可回编、可运行或语义正确。

## 3. 逐篇核对与修订

修订原则：只改有原文证据或已发现错误的句子；没有问题的句子不改字节。

### 3.1 hero（3038，`script/hero.py`，候选 2927 行）

**核对保留**（与候选一致）：CreateProp 的 ITEM_SERVERINIT 解包与 ITEM_ALL Default 两段遍历、PROPNAMEWITHCALLBACK 登记与 CheckBanWord；UpdateSkill 的 `sktype -= 1`、删除条件 `(id not in g_FightSkillLst or limit <= 0)`、仅 ST_SKILL 刷新两学习页、回调与 warui/shortcut/dlgautofight 通知；GetRealID 的 `g_ID/10` 与类型未知；GetHeroShow 的 OR 与庭院秋千提前 True；GetClientPos 两种多人坐骑类的 (0,0) 回落；GetServerPos 仅有地图对象时转换；SavePrivateData/GetPrivateData 的 `if data:` 假值回落；SetPlayerExtAttr 仅在值不等时通知。

**修订**：
- GetHeroShow：`calls` 补充候选中实际出现的 `juben.IsForceEnd`、`hidecatcat.IsHeroInGamePlayer`、`racingspeedgame.CheckGameStart`、`GetHeroID`、`oCheckShow.IsHaveReason/IsOnlyReason`；`herochengshowmgr` 注明为名称推断，庭院秋千常量按名标注。
- SavePrivateData：原分支文本含“手册未调用此写盘函数”（否定表述，且未核所有调用方），已删去，改为“本稿未核所有调用方”。
- sources：`excerpt_hero` 类型 metadata → `recovered_source`（摘录为候选源码行）。

### 3.2 dlgitem（717，`script/mxgame/item/view/dlgitem.py`，候选 3215 行）

**修订**：
- ShowDlg 的 CloseOtherUI：原摘要写“关闭交易赠予窗口”，超出证据。候选 `CloseOtherUI()`（L2558–L2562）实际只调用 `dlgswap.CloseWindow()` 与 `dlggive.CloseWindow()`。摘要改为写原调用，两窗口功能未核；追加证据 `dlgitem_CloseOtherUI`。
- ShowDlg 的 `@syncoperate.Operate()` 装饰器：原仅在 limitation 提及，无行号。追加 L2613 为证据 `dlgitem_ShowDlg_decorator`；装饰器调度语义仍标未核。
- ShowDlg 的 `dlgshenmoisland.IsShenmoHuodong()`：原文未标注，现注明为函数名推断（未核）。
- PreShowDlgAfterLogin：原摘要“若测试禁用dlgitem或首次OpenSys运行则return”。现改为与候选一致的条件表述：`permission.IsTestBansys('dlgitem')` 或 `gamectrl.IsFristRunFromOpenSys()` 为真 → 直接 return；并写明 `ShowDlg(False)` 仍会构造对象。
- relationships：`hero.GetRealID` 原为 `upstream / imports`。候选 OnMessage 的 22 号动作是**本模块调用** hero.GetRealID（再交 netopenui.C2SOpenPlayerInfoDlg），按 §6 约定改为 `downstream / calls`，并把该调用补为 OnMessage 的 22 号分支（symbol 注明“OnMessage 22号”）。
- limitation 补充：OnMessage 的 9/10/21 号与 1000 以上宠物号分支本体未展开。

**核对保留**：`item_new.dlg`（构造器实参）与 `GetDlgPath` 返回的 `item1.dlg` 并存，JSON 明确写为“未复核 CCombDialog 何时读取 GetDlgPath，不能宣布只用其中一张”；Show 只作用于已有窗；ShowDlg 首次构造即使 flag=False 也会构造并登记回调；ShowSwitch 的 `not IsDialogShowing()`；4 号网络整理（C2SPackItem）与 15 号本地排序（ShowItemSortDlg）两条路径分开记录；5/7 号物品加解锁、1 号 C2SOpenLock；右键 UseItem 的手持门禁与 m_ShowSummon 二选一；Shift 复制（OnCopyItemInfo）与 Take 的分流。`CItemDialog` 继承 `combdialog.CCombDialog`（候选 L879）。

### 3.3 task（1129，`script/mxgame/task/model/task.py`，候选 1107 行）

**核对保留**：ModuleReset 不含 g_iTaskChain；AddNecessary 的 itype 1–5 映射、同 shape 覆盖而非累加、SPECIALTASK extend；IsSatisfyTask 为 OR；ClearTask 的 8 个字典与满足列表（不清 g_WithoutNoticeTask、g_Task2PetCheckInfo）；HasBanFindPathTask 只提示并返回 True；IsTaskItem 的空表 True 与 SPECIALSHAPE / 精确匹配；ServerTaskSatisfy 的 `if not in` 之后仍 TriggerCB。

**修订**：
- RefreshNecessary：`petOrItemTaskList` 分支把 `petTaskList` 解包赋给两个列表的操作，补充“petTaskList 为空或假值时该解包可能异常”，标 `inferred`（未运行）。
- TaskSatisfy / TaskUnSatisfy：推导式 `dict([_[1] for k in tasklist])` 中 `_` 在推导式内未绑定。补充“非空 tasklist 时可能异常（inferred）”。
- TaskUnSatisfy：原摘要写“读取未满足描述”；候选为 `desc = g_UnsatisfyTaskID2Desc.get(tid)` 后 desc 无后续引用，改为该表述。
- CheckNpcFlag：原分支文本含“国家/职业相关额外门禁”，拆为两条：`country==0 且 tasktype∈LIMITCOUNTRY_TASKTYPE`、`zy==0 且 tasktype==18`；`LIMITSTATUS_TASKTYPE` 写明集合名。`zy` 取自 `hero.g_Prop.m_Force`，“职业”语义仅凭变量名推断，标未核。

### 3.4 npc（949，`script/char/npc.py`，候选 1235 行）

**修订**：
- CNpc.LeftUp：原摘要“依剧本婚礼…分流”。候选 LeftUp 函数体本身不含剧本/婚礼判断；该判断在它调用的 `IsLimitClick()`（L310–L314，函数体 `juben.IsPlayJuben() or marriage.IsWedding()`）中。追加证据 `npc_CNpc_IsLimitClick`，LeftUp 与 RightUp 的门禁分别引用。
- 召唤兽/孩子：`IsHeroSummon`/`IsHeroChild`（L266–L277）原文追加为 `npc_CNpc_IsHeroSummon_IsHeroChild`；ClickHeroSummon/ClickHeroChild 本体未核，写入分支说明。
- 常量：追加 L13–L18 为 `npc_module_constants`：`NPCMOD = 50000`、`RANDOM_VALUE = {4456: 0, 7000: 30, 7001: 25}`、`TRANSMISSION_POINT_NPC_ID = 4999`、`DISTANCE_CLICK = 18`；运行期取值未验证。
- CNpc.LeftUp 新增分支（原稿未列）：竞速中 iDis 减半（`racingspeedgame.CheckGameStart()`）；RANDOM_VALUE 换调色板并 return 的完整条件（`m_CharIdx in RANDOM_VALUE`、随机数 > 阈值、`m_PopoTick < 2`，否则清零并继续）；`IsSale()` 直接 return（基类未展开）；近距离放行后调用 `mgrschedule/mdnewschedule.JoinActivityInNpcShape` 与 `dlgkeju.CheckHasKejuTask()`，功能仅凭模块名描述、未核。
- CClientNpc.LeftUp：原稿仅 4 个分支。补全为 6 个：忽略标志、自定义回调、地图/节流门禁（与 CNpc 同形但无 IsLimitClick/IsSale）、world 通用回调、近距离 m_TaskID==0 的 NpcLook、近距离 m_TaskID!=0 的 NpcTask(m_TaskID, m_Sequence)、**远处（≥10 格）且 map.AllowMove() 时只 WalkTo**。
- CNpc.RightUp：原文“摊位/限制点击时 return”改为 `IsSale()或IsLimitClick()`；“1 的时间比较”改为“1 秒”（候选确认）；常量注明 NPCMOD 为 50000。
- NpcNeed：原文“按候选key/出生标志过滤计数”改为候选原条件：type==1 用 `GetItemNumBySpecialShape`，type==2 对 `pet.g_Pets` 中 `m_Prop.m_Shape==shape` 且（`m_Key&64==0`，或 `m_Key&pet.MARK_SOUL_BINDED` 真且 `m_BirthKey==0`）计数，g_Pets 为 None 时 0；重复登记未去重。
- UpNpcNeedByNpcTask：补“`g_NpcNeedThing[npcId][taskId]` 不存在时候选直接索引、未见守卫（inferred，未运行）”。

**核对保留**：GetAroundNpc 返回首个命中（非最近）与非对称矩形；GetNpcSignFileName 的高 8 位/低 8 位映射与未知键无兜底；CNpc.ClickNpc 的 `m_bCheckOverlap` 设置无 try/finally；普通 LeftUp 的地图/节流/距离/重叠门禁与近距离 NpcLook、远处 WalkTo 两路；RightUp 的节流与 NPCMOD 随机颜色；CClientNpc.LeftUp 的 `m_bIgnoreClick`、自定义回调、`m_TaskID` 分流；CreateNpc 的三段连续 if（后者覆盖前者）；ManageNpcSign 与 NpcNeed 的表结构；UpNpcNeedByNpcTask 的 `max(have+增量,0)` 与首条命中。

## 4. 作者与 sources

- 四篇 `author` 统一为：`N6新会话（接管修订；原初稿为A代写，非G会话；本记录未经独立审核，N6不自批）`。`owner` 保持 G。
- `source_status` 保持 `recovered_complete_not_original`。
- 未写 `reviews/`，未改 A 的 `docs/evidence/` 报告与收据。

## 5. 方向约定（仅 gameplay 内，供 A/N7 复核）

`CONTRACT.md` 对 `direction` 只写 upstream/downstream，未定义 caller/callee。gameplay 内统一为：**本模块调用或导入 X，则 X 在 relationships 中记 `downstream`；调用或导入本模块的一方记 `upstream`。** 本轮只改动了一处按此约定修正的记录（dlgitem → hero.GetRealID，已改为 downstream/calls）。仓库内 login 等领域存在两种写法，是否推广到 CONTRACT 由 A 决定。

## 6. 函数与分支统计

| 文件 | 函数 原/现 | 分支 原/现 | 本轮新增 evidence id |
|---|---|---|---|
| hero.json | 13 / 13 | 12 / 12 | —（只修订摘要与 calls） |
| dlgitem.json | 13 / 13 | 19 / 21 | `dlgitem_CloseOtherUI`、`dlgitem_ShowDlg_decorator` |
| task.json | 13 / 13 | 14 / 16 | —（只修订摘要与分支） |
| npc.json | 12 / 12 | 17 / 24 | `npc_module_constants`、`npc_CNpc_IsHeroSummon_IsHeroChild`、`npc_CNpc_IsLimitClick` |
| **合计** | **51 / 51** | **62 / 73** | 5 |

- 函数数不变：51 个函数记录仍是 A 选定的范围，未新增函数，未声称穷尽整模块。
- 新增（原稿没有）：dlgitem 的 22 号分支、npc 的竞速减半 / RANDOM_VALUE / IsSale / 召唤兽孩子 / CClientNpc 远处 WalkTo 与门禁、task 的 CheckNpcFlag 门禁拆分、npc 的 UpNpcNeedByNpcTask 缺键说明。
- 修订（原稿有但错误或超出证据）：dlgitem 的 CloseOtherUI 描述、dlgitem 的神魔判断归因、dlgitem 的 GetRealID 方向、npc LeftUp 的剧本/婚礼归因、npc RightUp 的门禁描述、npc NpcNeed 的过滤描述、task TaskUnSatisfy 的 desc 描述、hero SavePrivateData 的否定表述。
- 只改了四份 JSON 与两份摘录（dlgitem、npc）；hero 与 task 的摘录未改。

## 7. 验证命令与实际结果（N6 本机）

| 命令（仓库根，`PYTHONPATH=script_manual/src`） | 结果 |
|---|---|
| `/tmp/n6/mvenv/bin/python -m mxsj_manual validate --verify-evidence --require-full-inventory --repository .`（修订后，含修正文本的最终版；不带 `--repository` 时 `--verify-evidence` 会报错退出 2） | 退出 0；expected 5135 / indexed 5135 / annotated 20 / accepted 3 / excluded 1 |
| `/tmp/n6/mvenv/bin/python -m mxsj_manual build --output /tmp/n6/site --repository .`（仓库外输出） | 退出 0；生成 `index.html`（约 26 MB）与 `BUILD.json`；页面含修订文本（`CloseOtherUI` 12 处、`N6新会话` 4 处） |
| `QT_QPA_PLATFORM=offscreen /tmp/n6/mvenv/bin/python -m unittest discover -s script_manual/tests -v` | **82 项 = 71 通过 + 11 跳过 + 0 失败**，退出 0。跳过的 11 项是 GUI 测试：PySide6 6.10.3 已安装，但沙箱缺 `libGL.so.1`，**未执行，不计为通过** |
| `ruff check script_manual script_manual/script_manual.spec` | 退出 0 |
| `python3 tools/devkit/check_windows_compat.py script_manual --strict` | 退出 0；ERROR 0 / WARNING 0 / INFO 0 |
| 摘录逐行核对（仓库外脚本） | 980 行，0 不一致 |

**未运行**：`validate` 的改前基线（不声称做过）；浏览器/jsdom 对新 HTML 的渲染检查；Windows、EXE、游戏运行、原生模块；任何业务 URL 或布局资源。

## 8. 残留风险与未核项

1. **非独立审核**：本报告是 N6 作者的修订自查；N7 须按修订后 JSON 的新字节 SHA 独立复核，旧 reviews 已随字节变化失效（由 A/N7 处理，N6 未写入）。
2. **候选为反编译输出**：`baseline` / `decompile_ok` 仅说明输出形状。`TaskSatisfy`/`TaskUnSatisfy` 推导式异常、`RefreshNecessary` 解包异常、`_` 绑定情况、`zy/m_Force` 语义，都需字节码或运行期核对，不能据此修补为“正常流程”。
3. **名称推断仍存**：dlgkeju、mgrschedule/mdnewschedule、dlgshenmoisland、herochengshowmgr、zy 的职业含义，均只凭名字标注，未核。
4. **未覆盖**：hero 完整属性表（只摘表头）；dlgitem 的装备/召唤兽/快捷栏/闪烁/奖励窗口、OnMessage 的 9/10/21 与 1000 以上宠物号；npc 的 ClickHeroSummon/ClickHeroChild、IsSale 基类、CreateNpc 动态类签名；task 的需求管理器与宠物/装备匹配细节。
5. **运行期取值**：RANDOM_VALUE、DISTANCE_CLICK、NPCMOD、map.CELLSIZE、misc.Time 的运行期值与 `Operate` 装饰器语义均未验证。
6. **服务端协议**：所有 C2S 调用的服务端语义未核。
7. **1288 未触碰**，本轮未定点恢复或读取。
8. **GUI 测试未执行**：11 项因 libGL 缺失跳过，不计通过；无 Windows 或游戏实机验证。
9. **仓库外产物**：候选、venv、日志、site 均在 `/tmp/n6`，未入库；如需重跑，按 §2 命令在仓库外目录执行。
