# N5 回应（battle 域 / 逻辑任务包 F，2026-10-16）

> 本文件是 N5 自己的交付说明，**不是**手册正文、不是审核记录、不是运行报告。
> 正文只有本目录下的 4 份 annotation JSON；`evidence/` 下 5 份是给它们提供行级证据的小摘录。

## 1. 会话身份与基线（实际值，不是旧 F）

| 项 | 值 |
|---|---|
| 会话标识 | **N5**（全新会话；逻辑任务包 F / battle） |
| 固定分支 | `arena/ae1bd730-mxsj-tw-2022`（系统分配，全程未切换） |
| 开工基线 | `9b0dea799768aaacbb967ffc59f45753970752be` = A 交接提交，也是 `arena/61deb9e5-mxsj-tw-2022` 当时顶端 |
| 合并内容检查点 | `7d32e5340b0ab4168f725d238d767ad6232f715d` —— **是 `9b0dea7` 的父提交**（`git cat-file -p HEAD` 的 parent 字段） |
| 关于 merge-base | 本地是 depth=2 的 shallow 克隆（`.git/shallow` 含 `9b0dea7` 与 `8afb53a`），`git merge-base --is-ancestor` **无法越过 shallow 边界**，会误报 false。本轮已单独 `git fetch origin 7d32e534…` 拉到对象并以 HEAD 的 parent 判定；不是用它给“未合并”开脱。 |
| `git merge FETCH_HEAD` 结果 | `Already up to date.`（集成分支当时就等于该基线，无新提交可合） |
| 任务卡版本 | `20261016-new-cohort-v1`；分派见 `script_manual/coordination/reassignment_20261016.json` 的 N5 条目 |
| 未做 | 未推 A/master、未自行 merge、未开新分支、未切旧 B–H 分支 |

`author` 字段已写成 `N5（2026-10-16 全新会话，承接逻辑任务包 F/battle；不冒称旧 F 会话）`；
`owner` 仍按契约保持 `F`，`domain=battle`。

## 2. 文件边界

只改/新增 `script_manual/annotations/battle/` 下：

- 修订：`war.json`（697）、`netwar.json`（1406）、`warcmd.json`（1612）、`e_warctrl.json`（8）——**原位修订，没有另建同身份第二份**。
- 新增：`evidence/n5_provenance_20261016.txt`、`evidence/n5_codecensus_20261016.txt`、
  `evidence/war_697_excerpt.txt`、`evidence/warcmd_1612_excerpt.txt`、`evidence/e_warctrl_8_excerpt.txt`。
- 未触碰：`docs/STATUS.md`、根导航、`src/`、`schema/`、`coordination/`、任务总表、其他领域（login/ui_chat/network/gameplay）、
  `reviews/`、原包与参数文件。N2 的 `main` 正文没有越域写；本域只在 `war.json`/`netwar.json` 里记录对 `main` 的**调用点与行号**，并在 limitations 中写明归属。

## 3. 定点恢复（自己跑的，不是沿用旧结论）

```bash
# 仓库外 venv：Python 3.11.2 / uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser 1.9.0 / click 8.5.0
python tools/decompiler/recover_entries.py --out /tmp/n5-recover/entries \
    --entries 697,1406,1612,8 --decompile-timeout 30 --report /tmp/n5-recover/f-probe.json
# 实际输出：处理 4 条，用时 2.8s → {'recovered': 4}
```

| entry | co_filename | stage | 反编译 | 产物类型 | 总行数 | 去头正文行数 | 去头正文 SHA256 | 与 A 的 BDF 收据一致 |
|---|---|---|---|---|---|---|---|---|
| 697 | script/core/war.py | baseline | decompile_ok | source | 2640 | 2634 | `a6a81ad68ea82e0fbe028627b7d88c734ab56b889c79e1aa50da421b4a02f7b7` | ✅ |
| 1406 | script/netwar.py | baseline | **decompile_fail** | source_partial+digest | 13 | 7 | `242c5e7ab2d4f6c0f2f25105654586a6f7b80a66c682a8927f99ad5773f884da` | ✅ |
| 1612 | script/core/magicperform/warcmd.py | baseline | decompile_ok | source | 45 | 39 | `60f0e56950f96c9951029f6de2665bf16d0cb3fb7bc4cbb6d1adf312e16541fa` | ✅ |
| 8 | script/pubscript/pubskill/e_warctrl.py | baseline | decompile_ok | source | 176 | 170 | `bd97d6af2a54a26eacf1bb6c6cf14edc0843800dd8fa7f7234a88ec6034022ad` | ✅ |

（“去头正文”= 去掉 `recover_entries` 写入的 6 行产物头；A 的收据用的同一口径，四条逐字节对上。）

对应 pyc（本轮独立转译，额外钉住以便复核）：

| entry | stored payload SHA256 | exp_len | pyc_len | pyc SHA256 |
|---|---|---|---|---|
| 697 | `a1d49aa67473ac6b1def790d074830aa5833f23763ad4c04e08dca258d01b008` | 73197 | 73205 | `96cb750ee47247233359d6541d1a58c3d3ab879a03efb5113e1fa64a85a7b305` |
| 1406 | `bdc4e87128b2031bc5eaf6fd688e94325f8653d4fae0a2f5d62ae83b2f71536e` | 35240 | 35248 | `bda0b10a6333db59d813c7a21174e55f057a3fe71e3a335e265cbfe32f3d6b5e` |
| 1612 | `bf9104f82df4c4f27be91d882fd6a1e922f275f5fb48c68c918c365df20729c8` | 2621 | 2629 | `297eb007b449cd92f0062ed1e3d55c6a7d64d8edb0d32cd3f6c3882a7871cf16` |
| 8 | `a40d7aae07ddfda668fdfca77cdf4aea38b614e85c8bf07996cd077aef66cdc1` | 6330 | 6338 | `0853d1f0ba6e3957cad65d624e0f1d0f8f8e70f33cc77ea48f6de3df33bea182` |

**1406 本轮 uncompyle6 再次失败，没有“完整源码”**。因此：

1. 正文证据锚在仓库内既有的 pycdc 候选 `tools/decompiler/output/script_fls_pycdc/script/netwar.py`
   （SHA `2a050ae3a139b4e19029166377a6a60c5cd72d092f4c044427a07a56445028e0`，1086 行，git 跟踪）；
2. 用 xdis 6.1.8 **直接读本轮独立转译出的 pyc**做交叉印证：顶层码对象 **86 个**，与 pycdc 候选的顶层 `def`
   **86 个**名称一一对应，且 86 个名字全部落在模块 `co_names`（102 项）内
   （其余 16 项 = 12 个 import 模块名 + `g_WarTimes`/`g_WarVersion`/`g_WarLocation` + `g_WarRecordInfoFunc`）。
   这能证明“pycdc 候选来自同一份 entry 1406 字节码”，**不能**证明它的控制流与源码一致；
3. `source_status` 由旧稿的 `recovered_complete_not_original` **下调**为 `recovered_partial`。

**签名来源**：netwar 86 个函数的形参来自码对象 `co_varnames[:co_argcount]`（xdis 直读，不含默认值）；
war / warcmd / e_warctrl 的形参来自候选 `def` 行，并与码对象普查逐条对上。

## 4. 原报告 5 项逐条回应

### (1) 三份仅名称底稿现在有可读候选 —— 已补，并明确“decompile_ok ≠ 语义正确”

- `war.json` / `warcmd.json` / `e_warctrl.json` 的 `source_status` 从 `historical_unverified_origin`
  改为 **`recovered_partial`**（依据：三者候选里都有损坏标识符，见下），**没有**因为 decompile_ok 就升成
  `recovered_complete_not_original`。
- 三份的函数记录从“名字 + inferred + catalog”改成：逐条读过并解释的函数标 `static_reviewed` + 行级证据；
  没读的一律保留 `inferred` 且**只引码对象普查**，不做任何行为断言。
- 1406 用“钉摘要的历史 pycdc 候选”，局限在 3 处写明（第 3 节的失败事实、`evidence` 里的 note、limitations 第 1–3 条）。

### (2) netwar 三处非推测函数引用缺少函数体 —— 已补，并全文复查同类假引用

旧稿里 `ModuleReset` / `ReduceWarTime` / `IsWarEnd` 的 `confidence=extracted` 但只引 `globals`（22–26 行，
其实只是三个全局的**初值声明行**，不能证明重置/递减/判断）。现在改为引用各自函数体：

| 函数 | 新证据（pycdc 候选行） | 新摘要要点 |
|---|---|---|
| `ModuleReset` | 28–34 | `g_WarTimes=0`、`g_WarVersion=0`、`g_WarLocation=[0, 0]` |
| `ReduceWarTime` | 158–160 | `g_WarTimes -= 1`；候选里**没有**边界保护（负数不夹回 0），如实记录，不推断游戏行为 |
| `IsWarEnd` | 303–304 | `return g_WarTimes == 0` |

全文复查结果（旧稿共 10 条 `confidence=extracted`）：其余 7 条
（`S2CWarStart`/`WarStartCloseDlg`/`S2CWarEnd`/`S2CWarTurn`/`S2CWarAdd`/`S2CWarCalledPet`/`S2CWarRecordInfo`）
旧的“构造 war.CCmd 并入战斗指令队列”是**模板句、不区分函数**，本轮全部重写为按该函数体的实际描述；
`S2CWarAdd`/`S2CWarCalledPet`/`S2CWarRecordInfo` 三处旧证据范围（‘add’/‘calledpet’/‘recordinfo’）虽指向正确区间，
但旧摘要与区间内容不符，已一并改写。
另外旧稿 76 条 `inferred` + 空 evidence 的 S2C/C2S 记录，本轮全部按各自函数体生成了摘要并给了独立证据（86/86 全部有正文行证据）。

复查中额外发现并**原样记录**（不替候选“修好”、不据此认定游戏行为）：

- `S2CWarMPFP`：`func = None if iType == 1 else war.FpChange` → iType==1 时回调为 `None`（`war.CCmd(None)`），
  与“1=MP”的直觉相反，疑为 pycdc 对条件表达式的误拼。
- `S2CWarNotifyExt`：`if itype == 0 and itype == 4:` 恒为假。
- `S2CWarCalledPet`：`canAgainCall.g_CanCallAgain = None` 把整数当对象赋值，且 `return None` 落在 `try` 内。
- pycdc 候选 import 段 `permission` 出现两次。

### (3) 入场动画分支的候选形态 —— 已按字面写清，条件体归属标 inferred

`netwar.py` 候选 228–233 行（`S2CWarStart`）：

```text
228    bIsServerRecord = dlgwarrecord.IsWarRec()
229    bIsClientRecord = war.GetReplayWar()
230    bIsSureWarType = cmd.type in warenteranimation.SHOW_ANI_WAR_TYPE
231    if bIsSureWarType and not bIsServerRecord and not bIsClientRecord:
232        pass
233    warenteranimation.GetWarEnterAniMgr().SetEnterAniShow(not (cmd.startTurn))
```

- **事实（static_reviewed）**：第 232 行 `pass` 是候选里该 `if` 的全部条件体；
  第 233 行的 `SetEnterAniShow(...)` 与 `if` **同缩进、位于 if 之后**，在本候选中是无条件执行。
- **待核（inferred）**：真实字节码里该 `if` 的条件体内容无法从本候选判定，
  因此“特定战斗类型且非录像时才设置入场动画”这一说法**降级为 inferred**，并在 branch 的 `effect` 里明文写“真实守卫待核”。
- 同类形态还有 `S2CWarRecordInfo`（1084–1086 行：`if oFunc:` 体是 `pass`，`oFunc(netobj)` 在 if 之外），同样处理。
- 另外补了一条此前未记的守卫：`S2CWarStart` 225–226 行 `if ...GetIsShowingAni(): return None`，
  入场动画正在播时整段后续（含 `main.SetWarLoop()`）都不执行。

### (4) 跨模块事实与推测分开 —— CCmd 入队守卫、录像过滤、End 分支已各自钉证据

- **CCmd 入队 + 录像过滤守卫**：`war.py` 去头正文 205–216 行
  （`evidence/war_697_excerpt.txt` 的 `w_ccmd` 段，摘录第 233–246 行）：
  `CCmd.__init__` 里 `if not recordvideo.GetVideoMgr().IsFilter():` 才写 `m_Used/m_Callback`、
  `g_Cmds.append(self)`、`preload_interface.Record2PreloadQueue(self)`、`warturn.RecordCmd(self)`。
  过滤打开时对象被构造但**不入队也不带这两个属性**。这是 A 指出的“211–222 有录像过滤条件”的确认版本。
- **结束切循环**：`netwar.S2CWarEnd`（pycdc 307–335）**只**构造 `war.CCmd(war.End)`、`net.g_Net.Pause(1)`、
  释放战斗护盾、恢复游戏视图、关指令缓存，**没有任何主循环切换**。
  切换在 `war.End` 内部：
  - 录像分支（`GetReplayWar()` 为真）→ `main.CloseGame()` 后 `return`；
  - 普通分支 → `main.SetMainLoop()`（`war` 去头正文 **1927** 行，摘录文件第 1514 行）。
  `netwar.json` 的 `relationships` 与 `modification_guides` 里已显式写明“S2CWarEnd 不切主循环”，
  不再写成 `S2CWarEnd → SetMainLoop`。
- **main 仍归 N2**：`main.SetMainLoop` / `main.CloseGame` / `main.SetWarLoop` 只作为调用点与行号记录，
  两份 JSON 的 limitations 都写明 main.py 正文由 N2 负责。未越域写 `main` 的说明。
- 队列推进链（`NextCmd`/`Process`/`Wait`/`SetProcess`）与“回调必须最终 `NextCmd()` 或 `SetProcess(Wait, ...)`，
  否则队列卡死”写进了 `war.json` 的修改指南，依据 `w_nextcmd`/`w_process`/`w_wait` 三段。
- 未能确定的关系（`S2C*` 的原生分发方、`CreateCmdObject`/`GetWarCtrl` 的调用方）一律 `module: null` + `inferred`，
  不写成确定调用。

### (5) 证据与置信/来源 —— warcmd 资源清单改为双重证明，pycdc 候选来源补全

- **warcmd 资源清单**：旧稿 1 条 `extracted` 资源只引 entry 1612 的 catalog，不能证明所列子模块存在。
  现改为 **21 条独立资源**，每条同时给出两重证据：
  ① `warcmd.py` 去头正文第 6 行的 `import` 行（`wc_import` 段，摘录第 17–22 行）；
  ② 该子模块在 catalog 的独立 entry（行号 = entry_index+1）。
  清单（`script/core/magicperform/warcmd/*.py`）：
  addbuff 3722、attackend 4494、attackpre 803、bgcolor 3595、bgrolecolor 1847、delay 499、
  enermyhit 4126、enermyhurt 2691、ghost 4959、goback 2842、move 1834、playani 2784、
  playghostani 3991、playghostmoveani 1905、playmoveani 1621、playsound 231、remant 3367、
  rolepalette 1480、setaction 3972、setmulaction 3644、spare 2397。
  另外把 `e_comskilldefine`(203)、`e_debugctrl`(2013，包内自报路径已损坏)、`warcmdbase`(4694，未读其正文) 也单独列成资源。
- **pycdc_netwar 的 note 已补全**：实际输入 pyc（长度与 SHA，见表）、工具（Decompyle++ / pycdc，
  候选头自述生成时间 2026-10-14T23:55:56Z、输入包 SHA、File: entry_1406.pyc (Python 2.5)、uncompyle6 状态=stub）、
  处理方法（recover_entries 只读转译 → 本轮反编译失败仅留 marshal 摘要，正文沿用历史候选）、
  以及不可靠范围（重复 import、两处“空条件体 + 后续调用”形态、`S2CWarCalledPet` 的整数当对象赋值）。
- **置信度分布**：全部 4 份中 `extracted` 0 条、`runtime_verified` **0** 条；
  解释过的函数全部 `static_reviewed`（作者已读证据并核对），未解释的保留 `inferred`。
  旧稿 netwar 的 10 条 `extracted` 是“只引全局变量初值行”的假引用，本轮已全部取消。

## 5. 模块 / 函数 / 分支变化

| 文件 | functions | branches | static_reviewed | inferred | 非空 signature | source_status |
|---|---|---|---|---|---|---|
| `war.json` | 150 → **153** | 0 → **43** | 0 → **111** | 150 → 42 | 0 → 151 | `historical_unverified_origin` → `recovered_partial` |
| `netwar.json` | 86 → 86 | 10 → **12** | 0 → **86** | 76 → 0（另 10 条 extracted 取消） | 1 → 86 | `recovered_complete_not_original` → **`recovered_partial`（下调）** |
| `warcmd.json` | 1 → 1 | 0 → **2** | 0 → **1** | 1 → 0 | 0 → 1 | `historical_unverified_origin` → `recovered_partial` |
| `e_warctrl.json` | 22 → **27** | 0 → **6** | 0 → **27** | 22 → 0 | 0 → 25 | `historical_unverified_origin` → `recovered_partial` |
| **合计** | **259 → 267** | **10 → 63** | 0 → **225** | 259 → 42 | 1 → 263 | |

函数条数变化**逐条可解释**（不是凑数）：按任务卡“用限定名区分类与方法”的要求，把旧稿平铺/合并的同名记录拆成限定名。

- `war.json` +3：新增 `CCmd.__init__`、`CWarMgr.__init__`、`CWarMgr.OnPetDel/OnPetDead/OnPetRestore/OnPerform/OnWarriorAdd`、
  `PlayAni.Play`、`PlayTraceAni.PlayTraceAni`、`FrameTimer.FrameTimer`、`SetReplayVer.Timer`、`BossDelAddon.Fadeout`（+12），
  删除旧稿的 9 条平铺名（`__init__`、`Play`、`Timer`、`Fadeout`、`OnPetDel`、`OnPetDead`、`OnPetRestore`、`OnPerform`、`OnWarriorAdd`）。
- `e_warctrl.json` +5：20 条 `CWarCtrl.*` / `CPlayCtrl.*` 限定名替换 15 条平铺名（`__init__`、`OnUpdate`、`SetPause`、
  `RemoveSkill`、`GetPlayCtrl` 等原本在两类里各出现一次却被合并成一条）。
- `netwar.json` 条数不变（模块内全是顶层函数，无同名冲突）。

其它结构变化：`resources` 8→46（四份合计）、`relationships` 7→24、`modification_guides` 9→18、`sources` 每份 2→4/5、
`evidence` 每份 2/11→12–104（逐区间/逐函数绑定）。

**仍未解释的函数（诚实清单）**：`war.json` 保留 42 条 `inferred` 名称底稿，主要是
Boss 武器与命中结算系列（`AddBossWeapon`/`DelBossWeapon`/`CreateBossIcon`/`GetVictimPos`/`BeHurt`/`BossBeginHit`/
`BeginHitByArg`/`RefreshAddonPos`/`BossSetAddon`/`BossWarriorTurn`/`BossGetMagicInfo`/`BossHitOver`）、
`SetWarriorName`/`SetBossWarriorSelect`/`IsAllide`/`GetWarriorClass`/`GetWarriorGrade`/`GetWarriorPlace`、
`ChgAction`、`PerformName`/`MpChange`/`FpChange`/`ShowGraspTips`、血条显示系列、
`CmdFindAttackEndByID`/`CmdFindAttackNormalByID`/`GetNewMagicInfo`/`TransformShape` 等。
这些的 `summary` 一律写“本轮未逐行读取该函数正文；形参来自码对象普查，行为未解释，未做任何语义断言”，
并已在 `war.json` 的 limitations 里点名列出。

## 6. 损坏标识符（原样保留，未猜补、未用 catalog 历史名覆盖）

| 条目 | 位置（去头正文行） | 候选里的样子 |
|---|---|---|
| 697 war.py | 580 / 759 / 773 | `except SystemE??or:`（3 处） |
| 697 war.py | 172 | `EID2PATH` 的中文串带解码噪声 |
| 1612 warcmd.py | 22（映射表第 12 条键） | `e_comskilldefine.TLNKKXS^WBX@OHTSJHVEANI` |
| 8 e_warctrl.py | 79 | `e_warinterface.}EillFinished` |

## 7. 来源与工具 SHA256

输入 / 工具（与 A 的 BDF 收据一致）：

```text
data/script.fls                              8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
data/data.fls（仅指纹，未读条目正文）        5f96bdb23d4555c8014ac4a4a65819f48a3251b95a8cc94dff09ee7e2cc0a12c
tools/decompiler/script_fls_keys.json        43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb
tools/decompiler/recover_entries.py          152dbc28864a10c8b7188df7ae91c8039b0b8c0b056d98591e407b897e39c458
tools/decompiler/batch_decompile.py          a74742231e04c018c3f63452cfc859c20c6404fd73891eae9076bfcf8185b4e8
server/docs/catalog/script_entries.jsonl     d42694bf2621496a9107b22c1123a73a753a34fd6e907d74cd72707b127f62da
tools/decompiler/output/script_fls_pycdc/script/netwar.py
                                             2a050ae3a139b4e19029166377a6a60c5cd72d092f4c044427a07a56445028e0
```

入库的小证据摘录（`script_manual/annotations/battle/evidence/`）：

```text
n5_provenance_20261016.txt     88da51a167cb8e174266af6f04892f570fd66fa558d3834d85f02f819702e486
n5_codecensus_20261016.txt     32bf184461de4713d94d8bcde0dadb11fadbed06827235d73628a3a0d2973ad1
war_697_excerpt.txt            8399fc051da77ebc671c2e73f225bd08a20908aae8d37c5100309f809158cbbc
warcmd_1612_excerpt.txt        19380ecf7d56a3e82de937a07d4b6fc555145b958be2c397e00caa6b1826a30b
e_warctrl_8_excerpt.txt        2207f84774a15ae905aea2c917a9406d7563b879204499f833f2053e308549d1
```

修订后的正文原字节 SHA（供 N7/A 绑定审核用；改动任何一字节即失效）：

```text
war.json        99355dff36b7c77c0aac3de945e0c0372728148e1ab9053a169783cbcdf15c4f
netwar.json     d45fb764616f069a6fd2f012c2f8ae16ade3d55f7062349421eb7911c7b3d393
warcmd.json     5b518318eaefa874818b42eb9fac11c6f6bbaf3f43e94f580b119c9aacf92c73
e_warctrl.json  8c364cb547d35ac8ffbd712dc6963671231195e68c834e9e77912b8b6c0beede
```

## 8. 实际跑过的命令与结果

```bash
PYTHONPATH=script_manual/src python -m mxsj_manual validate \
    --verify-evidence --require-full-inventory --repository .
# {"expected_entries": 5135, "indexed": 5135, "annotated": 20, "accepted": 3, "excluded": 1}

PYTHONPATH=script_manual/src QT_QPA_PLATFORM=offscreen python -m unittest discover -s script_manual/tests
# Ran 82 tests — OK (skipped=11)   # 11 项 Qt GUI 因沙箱缺 libGL.so.1 跳过，未算通过

ruff check script_manual script_manual/script_manual.spec
# All checks passed!

python tools/devkit/check_windows_compat.py script_manual --strict
# 文件名检查 126 项，源码/脚本扫描 27 个；ERROR 0，WARNING 0，INFO 0
```

额外做的**负向验证**（证明 `--verify-evidence` 真的在校验，而不是空转）：

- 把 `warcmd.json` 里 `wc_create` 的 `end_line` 改成 99999 → `手册校验/失败：证据行范围超过来源文件`（已还原）。
- 把 `warcmd.json` 里 `warcmd_src` 的 `sha256` 改成全 0 → `手册校验/失败：证据来源摘要变化：…/warcmd_1612_excerpt.txt`（已还原）。

还原后 `validate` 重新通过；两条负向验证只改临时副本，未留下改动。

## 9. 未跑 / 保留风险

**未跑（不算通过）**

- Qt GUI 实跑：沙箱缺 `libGL.so.1`，11 项测试 skip。
- Windows / EXE / PyInstaller 实机构建。
- 真实浏览器、原生引擎、游戏实机、真实服务端。**没有任何 `runtime_verified` 结论。**
- 未执行、未 `import` 任何恢复出来的游戏模块（红线）。

**保留风险 / 仍未闭环**

1. **1406 没有可用的 uncompyle6 产物**，正文证据全靠 pycdc 候选；两处“if 体为 pass、调用在 if 之后”的控制流歧义
   （`S2CWarStart` 231–233、`S2CWarRecordInfo` 1084–1086）只能标 `inferred`，真实守卫待核。
2. **`war.py` 仍有 42 条名称底稿**（第 5 节点名清单），本轮没有把它们说成已解释。
3. **21 个 warcmd 子模块的正文本轮一条都没读**；它们是否共享 `warcmdbase`(4694) 基类、接口是否一致，无证据。
4. **`e_warcmdmgr`(631) 未读**，`CPlayCtrl.IsEnd`/`OnUpdate` 的真实语义（帧号→命令映射）没有证据。
5. **`CreateCmdObject` / `GetWarCtrl` 的调用方未解**，相关关系为 `module: null` + `inferred`。
6. **协议层**：C2S 的 `net.C2GS_WAR_*` 常量与 `PacketAddI/PacketAddS` 的长度参数仅按候选字面记录；
   仓库内没有任何真实抓包字节，未与真机/服务端核对，**不表示发送成功或服务端接受**。
7. **战斗计算（伤害、命中、AI、服务端裁决）不在本卡范围**，本轮零断言。
8. `DoAddonAction` 的 boss 分支在候选里不可达、`S2CWarMPFP` 的 `None` 回调、`S2CWarNotifyExt` 的恒假条件，
   都只是候选形态的如实描述，**没有**据此推断游戏必然如此。
9. 本轮没有改动 `docs/STATUS.md`、根导航、`coordination/`、`schema/`（A 独占）；若需同步 §3.48 的 F 计数，请 A 按新 SHA 更新。
10. 完整候选、pyc、venv、恢复报告 JSON 全部留在仓库外 `/tmp/n5-recover`（沙箱外置研究材料，不入 Git）；
    入库的只有 5 份小证据摘录 + 4 份正文 + 本文件。
