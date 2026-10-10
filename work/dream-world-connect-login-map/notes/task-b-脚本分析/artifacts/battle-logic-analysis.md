# 战斗逻辑分析（Task-B 目标 6a）

反汇编器: `tools/pymarshal_dis.py` + `mapping_table_v4.json` (v4.1)。
状态: `script\core\warturn.py` (entry305, ok/0-garbage) 与 `script\core\magic.py`
(entry214, ok/0-garbage) 主干可读；算术 1B-op (3F/09/23/05/…) 具体归属见 v4.1 `unknown_hot`。

## 1. 回合状态机 — script\core\warturn.py

| 函数 | 行 | 行为（反汇编重构） |
|---|---|---|
| `MkStartCmd(cmd)` | 27 | `g_StartCmd = cmd; g_StartTurn = 0`（STORE_NAME 写模块全局） |
| `RecordCmd(cmd)` | 33 | `g_Quene.append(cmd)`（注意开发者笔误 `Quene`，原文如此） |
| `GetDictData(srcdata, keys=None)` | 38 | 嵌套 dict 取值：`keys is None → []`；`state=srcdata`；`for _key in keys: if state.has_key(_key): state=state[_key]`；末尾 `return state`（另有 8B 不可达死代码，编译器残留） |
| `SetDictData(srcdata, value, keys=None)` | 50 | 嵌套 dict 赋值：`for idx,_key in enumerate(keys): if idx != len(keys)-1: …drill…`（UNPACK-3B 变体 `6C 02`） |
| `StoreTurnState()` | 64 | 回合快照：`import copy`；`if war.GetReplayWar(): return`；`curturn=…`；`deepcopy` 进 `g_TurnDict`；处理 `g_AddCmds`、`HPPercent`、`buff` 移除列表 |
| `Delay(cmd)` | 130 | `cmd.delaytime` 倒数 → `war.NextCmd()`（比较链含 `00/01/02/0E` 未知 1B-op，见 v4.1） |
| `CalHP(cmd)` | 136 | `obj=world.g_Objects.get(cmd.id)`；`if obj: if cmd.per<=0: obj.m_Life=war.WARRIOR_LIFE_DEAD; obj.Die() else: war.HPPercent(cmd)` |
| `Jump(turn)` | 146 | 回合跳放：`if not g_TurnDict.has_key(turn): return`；`ClearWar()`；`statelist=g_TurnDict[turn]['state']`；`idLst=statelist.keys(); idLst.sort()`；逐 id 重放（`CalHP(id/per)`、`ChgShape(shape)`、`magicId/series`） |
| `ClearWar()` | 202 | 全局重置：`g_WarSaid=[]`、`g_SkillUseNum=None`、`g_JQEnough=None`、`g_SummonCalled=None`、`magicmgr.g_MagicObjects=[]`、`g_Attacker/g_Victim/g_VictimID/g_Protector=None`、`g_ProtectSucceed=True`、`g_Victims=[]`、… |

要点:
- 回合制：指令队列 `g_Quene` + 回合字典 `g_TurnDict[turn]['state']` 快照（deepcopy）+ `Jump()` 按 id 排序重放 = 录像/观战/断线重连基础。
- 伤害结算 `CalHP` 以 `per<=0` 判定死亡（写 `m_Life` + `Die()`），否则调 `HPPercent`。
- `B7` 条件跳转基址为 `pos+arg`（非标准 `pos+3+arg`），`A2` 为绝对跳转——见 v4.1。

## 2. 技能弹道/特效 — script\core\magic.py

| 函数 | 行 | 行为 |
|---|---|---|
| `GetLine(x1,y1,x2,y2,n,en)` | 18 | 直线插值：`points=[]`；`n<1 → return`；同点则 `append((x1,y1))`；`nx=x2-x1, ny=y2-y1`（`23`=SUB 实锤）；定点数 `*10000`（`09`=MUL 候选） |
| `GetHermiteCurve/GetBezierCurve` | 43/104 | Hermite/Bezier 曲线插值（9 参：控制点+分段） |
| `CNode.__init__(data)` | 117 | `import ratio`；`self.m_X/m_Y/m_Frame/m_StayFrame/m_Connected/m_IsLeftCurved/m_LeftX/…=int(data.pop())`（pop 驱动的二进制反序列化；`EA`=LOAD 变体） |
| `CMagic` | 141 | 特效场景节点：`LoadImages`、`SetFrame`（序列帧动画） |

## 3. 相关 P0-battle 模块（488 个中的核心）

- `script\core\magicperform\warcmd\warcmdplaysound.py`（出招音效指令）
- `script\warnotify.py`、`script\debug\warinfo.py`（战斗通知/调试）
- `script\mxgame\serverbattle\view\dlgteamreport.py`（跨服战报）
- `script\mxgame\activity\countrycontest\arena\…`（1v1/3v3 竞技场）、`…\insidewar\…`（帮战）、`…\eliteorgwar\…`（精英帮战）
- `script\mxgame\skill\mdskillutilizationrate.py`（技能使用率统计）
- `script\mxgame\warprepare\delegate\dgtonekeyfumo*.py`（一键附魔/召唤，战前准备）
- 完整 488 列表见 `artifacts/fullrun/v4ok-classified.json`（`prio=P0-battle`）。

## 4. 战斗协议钩子

- `S2CWarCalledPet`（entry1406，召唤兽出战）等 `S2CWar*`/`C2GSWar*` 见 `protocol-commands-catalog.md`。
- 回合指令经 `RecordCmd → g_Quene`，由 `war.NextCmd()` 驱动消费。
