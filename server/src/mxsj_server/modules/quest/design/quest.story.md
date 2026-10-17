# 剧情 / 任务条件与分支（`quest.story`）— 客户端线索交接文档

> 本文件是人工设计记录，不会被材料生成工具覆盖。
> 对应 feature_id：`quest.story`；owner_module：`quest`。
> 状态：**客户端材料入口与接口设计卡；未实现，未逐函数语义核实。**
> 生成依据：`server/docs/features/quest.story.md`、`server/docs/feature_specs.json`、
> `work/.../v4ok-classified.json`、`tools/decompiler/output/script_fls_pycdc/script/data/juben/*`、
> `work/.../quest-item-analysis.md`。

---

## 1. 范围与边界

- 本卡只整理**客户端可观察的剧情/任务线索**，用于服务端开发对接。
- 三层必须分开：
  1. **可确认的客户端行为**（封包名、UI、演出命令、数据文件）。
  2. **可提取数据**（JUBENDATA、任务 ID、剧情任务判定、NPC/场景数据）。
  3. **缺失的服务端规则**（条件、分支、奖励、幂等、事务）——这些**尚未实现**，不能把客户端脚本当权威规则。
- 不得只凭客户端完成通知发奖；金币/物品/资格变化必须走同一工作单元，不能直接写其他模块私有表。
- 本模块不负责：账号、背包/经济的底层写入、战斗结算、地图权威移动（仅消费其公开契约）。

---

## 2. 客户端材料索引（剧情相关）

### 2.1 主入口条目（feature_specs `primary_entries`）

| entry | 文件 | 关键函数（线索） |
|---:|---|---|
| 4913 | `script/mxgame/task/nettask.py` | `C2SGetTask, S2CJuqingStatus, S2CUnpackClientNpc, S2CTaskAdd, S2CTaskRemove, C2SGiveUpTask, S2COpenGiveTask, S2CNotifyTaskDone, S2CTaskProcess, ...` |
| 1501 | `script/data/storytaskdata.py` | `IsStoryTask, IsStoryTaskWithName` |
| 3159 | `script/data/juqingdata.py` | `GetData` |

### 2.2 剧情演出 / 新剧情链路

| entry | 文件 | 关键函数（线索） |
|---:|---|---|
| 767 | `script/mxgame/newstory/netnewstory.py` | `C2SRequestNpcData, C2SReceiveNpcTask, C2SRequestSceneMapSchedule, C2SSendLetter, C2SGetGift, C2SGetLetterHistory, S2CRefreshNpcData, S2CRefreshNpcTaskStatus, S2CRefreshSceneMapSchedule, S2COpenLetter, S2CSetLetterHistory, S2CNewStoryProcess` |
| 1363 | `script/mxgame/newstory/rookieguide.py` | `ShowCalendarGuideTips, ShowCMItemGuide, ShowXiuLianGuide, S2CGetStrong, S2CWarFailTips` |
| 2176 | `script/mxgame/newstory/newstorymgr.py` | `InitNpcData, GetNpcDataById, GetNpcTaskData, GetNpcStoryData, GetTaskIndexById, GetNpcMaxPageByType, GetIntimateLevel, RefreshNpcTaskStatus, ReceiveNpcTask, RefreshPageSceneData, SetSceneSchedule, GetSceneMaxPage, RefreshPageLetterHistory, SetLetterHistory, GetLetterHistoryData, GetLetterHistoryLength, RequestLetterHistory` |
| 2640 | `script/mxgame/newstory/dlgdreamnote.py` | `CNPCIntimateDegree, CSceneMapDescDlg, CLetterHistoryDialog, CDreamNoteDialog` |
| 4023 | `script/mxgame/newstory/dlgdreamletter.py` | `CLetter`（标题/描述/礼物/选项） |

### 2.3 任务 UI

| entry | 文件 | 关键函数（线索） |
|---:|---|---|
| 23 | `script/mxgame/task/view/dlgtasknew.py` | `CTaskDialog, CTaskItem, CTaskItemButton, DoAcceptLinkEvent, DoRecieveLinkEvent, CreateTaskIcon, TraceAll, GiveUp, OnGiveUpTask, SetTask, GetClientShowList, ShowTaskPropProgress` |
| 166 | `script/mxgame/tasktrace/view/dlgtasktracetaskframe.py` | `CTaskFollowFrame, SetAllTaskInfo, SetOneTaskText, SetOneTaskPreviewReward, SetOneTaskGuideTips, SetOneTaskAutoFindEff, OnTaskSwitch, OnTaskDelete` |

### 2.4 剧情演出数据（`script/data/juben/`）

- feature card 列出 **320 条** `script/data/juben/task*.py`（entry 51, 66, 67, …, 5000），统一导出 `GetJubenData(jubenID)`。
- 每个文件是一个演出脚本（cutscene），结构为 `JUBENDATA: { jubenID: [ command, command, ... ] }`。
- 仓库内反编译输出仅落盘 29 个文件；其余 291 条在 source map 中有索引但未反编译到输出目录。
- 文本编码：BIG5（cp950 兼容）；反编译文本中的 `\x..` 转义需按 latin-1 → BIG5 还原。

### 2.5 任务追踪 / 导航（`quest.tracking`，同模块）

来源前缀：`script/mxgame/tasktrace/`（15 条）。关键文件：

| entry | 文件 |
|---:|---|
| 166 | `script/mxgame/tasktrace/view/dlgtasktracetaskframe.py` |
| 817 | `script/mxgame/tasktrace/model/mdhuodongtrace.py` |
| 821 | `script/mxgame/tasktrace/model/mdtasktrace.py` |
| 1569 | `script/mxgame/tasktrace/view/tasktraceitem.py` |
| 1996 | `script/mxgame/tasktrace/view/dlgtasktracehuodongframe.py` |
| 2024 | `script/mxgame/tasktrace/tasktraceutil.py` |
| 2134 | `script/mxgame/tasktrace/model/mdtasktraceprase.py` |
| 2393 | `script/mxgame/tasktrace/delegate/dgttasktracemain.py` |
| 2512 | `script/mxgame/tasktrace/delegate/dgttasktracetaskframe.py` |
| 3214 | `script/mxgame/tasktrace/tasktracedefines.py` |
| 3735 | `script/mxgame/tasktrace/model/mdhuodongtraceprase.py` |
| 3960 | `script/mxgame/tasktrace/delegate/dgttasktracehuodongframe.py` |
| 4045 | `script/mxgame/tasktrace/view/dlgtasktrace.py` |
| 4414 | `script/mxgame/tasktrace/model/mdtasktracesort.py` |
| 4913 | `script/mxgame/task/nettask.py` |

### 2.6 新手引导 / 章节奖励（`quest.onboarding`，拟独立模块）

来源前缀：`script/mxgame/newguide/`、`script/mxgame/guide/`、`script/mxgame/jobguide/`（feature card 列 25 条）。
主入口：entry 1838 `script/mxgame/newguide/netnewplayerguide.py`，函数：
`C2SGetTaskInfo, C2SGetReward, C2SGetTask, C2SCheckItem, C2SCloseTask, C2SRequestStrongInfo, C2SCloseGetStrong, S2CRefreshInfo, S2CGetStrong, S2CWarFailTips, S2CUpdateStrong, S2CUpdateAllTaskSchedule, S2CUpdateOneTaskSchedule, S2CNewplayerGuide, OnRefreshChapterInfo, OnTaskDone, OnChapterRewardState, OnCanRewardChapter, OnUnreadChapter`。

---

## 3. 协议命令线索

> 以下命令名来自客户端反编译/字符串提取，**不是已冻结的服务端协议**。字段语义需二轮核实。

### 3.1 任务主链路（`nettask.py`）

客户端 → 服务端（C2S）：
- `C2SGetTask`：拉取任务列表
- `C2SGiveUpTask`：放弃任务
- `C2STaskTraceAll / C2STaskTrace / C2SCancelTrace`：任务追踪开关
- `C2STaskGiveOpen`：打开交付/给予界面
- `C2SFinishClientTask`：客户端完成任务通知
- `C2SGetTask`（重复出现，可能重载）

服务端 → 客户端（S2C）：
- `S2CJuqingStatus`：**剧情状态**（剧情进度同步）
- `S2CUnpackClientNpc`：客户端 NPC 解包/生成
- `S2CTaskAdd / S2CTaskRemove`：任务增删
- `S2COpenGiveTask`：打开交付界面
- `S2CNotifyTaskDone`：任务完成通知
- `S2CTaskProcess`：任务进度更新

客户端内部（非网络，但影响服务端判定）：
- `IsTaskTracing, HasTask, GetTask, GetTaskInfo, GetAllTaskInfo, GetTaskNameInNpcDlg, UpdateTask, IsHide, UpdateNpcState, AddTaskNpcID/DelTaskNpcID/IsTaskNpcID, AddClientNpc/UpdateClientNpc/RemoveClientNpc, TaskSpecialEff, RefreshMinimapTaskNpc, ...`

### 3.2 新剧情 / NPC / 场景 / 信件 / 礼物（`netnewstory.py`）

客户端 → 服务端：
- `C2SRequestNpcData`：请求 NPC 数据
- `C2SReceiveNpcTask`：领取 NPC 任务
- `C2SRequestSceneMapSchedule`：请求场景地图进度
- `C2SSendLetter`：发送信件
- `C2SGetGift`：领取礼物
- `C2SGetLetterHistory`：拉取信件历史

服务端 → 客户端：
- `S2CRefreshNpcData`：刷新 NPC 数据
- `S2CRefreshNpcTaskStatus`：刷新 NPC 任务状态
- `S2CRefreshSceneMapSchedule`：刷新场景地图进度
- `S2COpenLetter`：打开信件
- `S2CSetLetterHistory`：设置信件历史
- `S2CNewStoryProcess`：新剧情进度

管理器（`newstorymgr.py`）：
- `InitNpcData, GetNpcDataById, GetNpcTaskData, GetNpcStoryData, GetTaskIndexById, GetNpcMaxPageByType, GetIntimateLevel`
- `RefreshNpcTaskStatus, ReceiveNpcTask`
- `RefreshPageSceneData, SetSceneSchedule, GetSceneMaxPage`
- `RefreshPageLetterHistory, SetLetterHistory, GetLetterHistoryData, GetLetterHistoryLength, RequestLetterHistory`

### 3.3 新手引导（`netnewplayerguide.py`）

见 §2.6。核心是 `S2CNewplayerGuide, S2CUpdateAllTaskSchedule, S2CUpdateOneTaskSchedule, S2CGetStrong, S2CWarFailTips`。

---

## 3.4 函数签名（来自 `script_manual/inventory/modules.jsonl`）

### 3.4.1 `nettask.py`（entry 4913）

| 函数 | 签名 |
|---|---|
| `C2SGetTask` | `()` |
| `S2CJuqingStatus` | `(netobj)` |
| `S2CUnpackClientNpc` | `(netobj)` |
| `S2CTaskAdd` | `(netobj)` |
| `S2CTaskRemove` | `(netobj)` |
| `C2SGiveUpTask` | `(taskid)` |
| `C2STaskTraceAll` | `(trace_flag)` |
| `C2STaskTrace` | `(iTaskID)` |
| `C2SCancelTrace` | `(iTaskID)` |
| `C2STaskGiveOpen` | `(bOpen)` |
| `C2SFinishClientTask` | `(iTaskID)` |
| `S2COpenGiveTask` | `(netobj)` |
| `S2CNotifyTaskDone` | `(netobj)` |
| `S2CTaskProcess` | `(netobj)` |

### 3.4.2 `netnewstory.py`（entry 767）

| 函数 | 签名 |
|---|---|
| `GetNewStoryNetObj` | `(iSub)` |
| `C2SRequestNpcData` | `(iNpcId)` |
| `C2SReceiveNpcTask` | `(iNpcId, iTaskId)` |
| `C2SRequestSceneMapSchedule` | `()` |
| `C2SSendLetter` | `(iLetterID, lChoices)` |
| `C2SGetGift` | `(iLetterID)` |
| `C2SGetLetterHistory` | `(iLen)` |
| `S2CRefreshNpcData` | `(netobj)` |
| `S2CRefreshNpcTaskStatus` | `(netobj)` |
| `S2CRefreshSceneMapSchedule` | `(netobj)` |
| `S2COpenLetter` | `(netobj)` |
| `S2CSetLetterHistory` | `(netobj)` |
| `S2CNewStoryProcess` | `(netobj)` |

### 3.4.3 `newstorymgr.py`（entry 2176）

| 函数 | 签名 |
|---|---|
| `GetNpcDataById` | `(self, iNpcId)` |
| `GetNpcTaskData` | `(self, iNpcId)` |
| `GetNpcStoryData` | `(self, iNpcId)` |
| `GetTaskIndexById` | `(self, iNpcId, iTaskId)` |
| `GetNpcMaxPageByType` | `(self, iType)` |
| `GetIntimateLevel` | `(self, iIntegral)` |
| `RefreshNpcTaskStatus` | `(self, iNpcId, iTaskId, iTaskStatus)` |
| `ReceiveNpcTask` | `(self, iType, iPage, iTaskIndex)` |
| `SetSceneSchedule` | `(self, iUnLockIndexList)` |
| `GetSceneMaxPage` | `(self)` |
| `SetLetterHistory` | `(self, dData)` |
| `GetLetterHistoryData` | `(self)` |
| `GetLetterHistoryLength` | `(self)` |
| `RequestLetterHistory` | `(self)` |

### 3.4.4 `netnewplayerguide.py`（entry 1838）

| 函数 | 签名 |
|---|---|
| `C2SGetTaskInfo` | `(iPage)` |
| `C2SGetReward` | `(iTaskID)` |
| `C2SGetTask` | `(iTaskID)` |
| `C2SCheckItem` | `(idx)` |
| `C2SCloseTask` | `(iTaskID)` |
| `C2SRequestStrongInfo` | `(iSub)` |
| `C2SCloseGetStrong` | `()` |
| `S2CRefreshInfo` | `(netobj)` |
| `S2CGetStrong` | `(netobj)` |
| `S2CWarFailTips` | `(netobj)` |
| `S2CUpdateStrong` | `(netobj)` |
| `S2CUpdateAllTaskSchedule` | `(oNetObj)` |
| `S2CUpdateOneTaskSchedule` | `(oNetObj)` |
| `S2CNewplayerGuide` | `(netobj)` |
| `OnRefreshChapterInfo` | `(iChapterID, iIsDone, iRewardState, dTask)` |
| `OnTaskDone` | `(iTaskID, iIsDone)` |
| `OnChapterRewardState` | `(iPageIndex, iRewardState)` |
| `OnCanRewardChapter` | `(lstChapter)` |
| `OnUnreadChapter` | `(lstChapter)` |

### 3.4.5 数据查询

| 文件 | entry | 函数 | 签名 |
|---|---:|---|---|
| `juqingdata.py` | 3159 | `GetData` | `(sid)` |
| `storytaskdata.py` | 1501 | `IsStoryTask` | `(taskID)` |
| `storytaskdata.py` | 1501 | `IsStoryTaskWithName` | `(taskName)` |

## 4. 剧情演出数据（JUBENDATA）结构与命令词汇

### 4.1 结构

```python
# script/data/juben/taskNNNNN.py
def GetJubenData(jubenID):
    return JUBENDATA.get(jubenID)

JUBENDATA = {
    jubenID: [
        None,                 # [0] 常见占位/场景头
        [cmd, arg, ...],      # 演出指令序列
        ...
    ]
}
```

- `jubenID` 为剧情/任务实例的演出编号（与任务 ID 不一定相同）。
- 序列中的每条指令是一个列表，首元素为命令名（BIG5），后续为参数（NPC ID、坐标、资源路径、文本、时长等）。
- 部分文件的反编译输出被 pycdc 拆成 `None[1] = [ ... ]` 形式，需人工还原；文本中出现的 JSON 片段（如 `{"color": [0,2,1], "weapon": [0,0,0]}`）表示 NPC 外观/装备参数。

### 4.2 已观测的命令词汇（29 个样本文件统计）

| 命令（BIG5） | 含义（推断） | 出现次数 |
|---|---|---:|
| 創建NPC | 创建 NPC | 212 |
| NPC說話 | NPC 对白 | 120 |
| 刪除NPC | 删除 NPC | 96 |
| NPC轉向 | NPC 转向 | 90 |
| NPC移動 | NPC 移动 | 74 |
| NPC動作 | NPC 动作 | 29 |
| 壓屏對白 | 压屏对白（全屏对话） | 27 |
| 地圖特效 | 地图特效 | 27 |
| 載入地圖 | 加载地图 | 19 |
| 跳躍 | 跳跃 | 12 |
| NPC特效 | NPC 特效 | 10 |
| 移動鏡頭 | 镜头移动 | 9 |
| 特殊移動 | 特殊移动 | 9 |
| TJC說話 | TJC 对白（特殊角色） | 8 |
| 震屏 | 震屏 | 7 |
| 濾鏡 | 滤镜 | 6 |
| 播放音效 | 播放音效 | 5 |
| 資源播放 | 资源播放 | 5 |
| 刪除資源 | 删除资源 | 5 |
| 播放音樂 | 播放音乐 | 3 |
| 壓屏 | 压屏 | 3 |
| 尋路下一任務 | 寻路到下一任务 | 2 |
| NPC淡出 | NPC 淡出 | 2 |
| 刪除NPC特效 | 删除 NPC 特效 | 2 |
| （损坏）`\x95wdNPC` | 未识别（反编译损坏，参数结构与「創建NPC」相同） | 6 |
| 綁定NPC鏡頭 | 绑定 NPC 镜头 | 1 |

> 注：命令参数的精确语义（坐标系、NPC ID 分配、资源路径约定）尚未逐条核实；服务端若要驱动演出，应以客户端解析为准，或先只下发剧情 ID/阶段，由客户端本地播放。

### 4.2.1 命令参数结构（25 个可解析样本文件统计）

| 命令 | 参数个数（不含命令名） | 参数含义（推断） |
|---|---:|---|
| 載入地圖 | 4 | `[delay, mapID, x, y]` |
| 播放音樂 | 5 | `[delay, filename, None, None, None]` |
| 創建NPC | 17/18 | `[delay, npcID, name?, title?, ?, ?, json外观, x, y, ?, None×4, action, None, flag, -1, None]`（17/18 差异为可选字段） |
| NPC特效 | 7 | `[delay, npcID, effectIndex, spritePath, layer?, x?, y?]` |
| 壓屏對白 | 2 | `[delay, text]`（富文本） |
| 刪除NPC特效 | 3 | `[delay, npcID, effectIndex]` |
| NPC動作 | 4/5 | `[delay, npcID, actionName, None(, None)]` |
| NPC說話 | 3 | `[delay, npcID, text]` |
| 震屏 | 3 | `[delay, amplitude, duration]` |
| 播放音效 | 4 | `[delay, filename, loop?, volume?]` |
| NPC轉向 | 3 | `[delay, npcID, direction]` |
| 刪除NPC | 2 | `[delay, npcID]` |
| NPC移動 | 6 | `[delay, npcID, x, y, speed, flag]` |
| 跳躍 | 10 | `[delay, npcID, "x,y,dir,speed,action", ...]` |
| 移動鏡頭 | 7 | `[delay, None, x1, y1, x2, y2, duration]` |
| 特殊移動 | 13 | `[delay, npcID, action, None, ?, x, y, ?, count, None×5]` |
| TJC說話 | 3 | `[delay, npcID, text]`（特殊角色） |
| 濾鏡 | 4 | `[delay, "r|g|b", duration, flag]` |
| 資源播放 | 6 | `[delay, layer, x, y, ?, spritePath, tag]` |
| 刪除資源 | 2 | `[delay, layer]` |
| 壓屏 | 3 | `[delay, None/flag, duration]` |
| 尋路下一任務 | 5 | `[delay, mapName, x, y, npcName]` |
| NPC淡出 | 3 | `[delay, npcID, duration]` |
| 地圖特效 | 4 | `[delay, flag, x, y, value]` |
| 綁定NPC鏡頭 | 3 | `[delay, npcID, ?]`（样本 1） |

> 说明：以上参数名均为推断；服务端若需驱动演出，建议仅下发剧情 ID/阶段，由客户端本地播放 JUBENDATA，避免服务端硬编码演出细节。

### 4.3 文本与资源引用

- 对白文本支持富文本标记：`P H\n...#32……`、`P N(2440,魔將)\n...`、`#r` 换行、`#Y/#n` 颜色等。
- 资源引用：`m001.ogg`、`thunder/05.wav`、`waddon/229_0.spr`、地图 ID（1025 等）。
- NPC 参数 JSON：`{"color": [0,2,1], "weapon": [0,0,0]}`。

---

## 5. 任务 / 剧情数据文件

| 文件 | entry | 函数 | 作用（推断） |
|---|---:|---|---|
| `script/data/juqingdata.py` | 3159 | `GetData` | 剧情数据表（ID → `{"max": int, "dist": int}`） |

### 5.1 `juqingdata.py` 解析结果（entry 3159）

`GetData(sid)`：若 `sid` 在 `DATA` 中则返回 `{"max": <int>, "dist": <int>}`，否则 `None`。

`DATA` 共 25 条，键为剧情/场景编号（2001–2028，缺 2002/2003/2006）：

| sid | max | dist |
|---:|---:|---:|
| 2001 | 5 | 3 |
| 2004 | 5 | 2 |
| 2005 | 5 | 3 |
| 2007 | 5 | 3 |
| 2008 | 5 | 2 |
| 2009 | 5 | 2 |
| 2010 | 5 | 2 |
| 2011 | 5 | 2 |
| 2012 | 5 | 2 |
| 2013 | 5 | 2 |
| 2014 | 6 | 2 |
| 2015 | 5 | 2 |
| 2016 | 5 | 2 |
| 2017 | 8 | 2 |
| 2018 | 3 | 4 |
| 2019 | 3 | 4 |
| 2020 | 3 | 3 |
| 2021 | 5 | 3 |
| 2022 | 5 | 3 |
| 2023 | 5 | 3 |
| 2024 | 5 | 3 |
| 2025 | 5 | 3 |
| 2026 | 5 | 2 |
| 2027 | 5 | 2 |
| 2028 | 5 | 2 |

> `max`/`dist` 的业务语义（如最大进度/距离阈值）尚未核实；字段名直接取自客户端常量。
| `script/data/storytaskdata.py` | 1501 | `IsStoryTask, IsStoryTaskWithName` | 判断某任务是否为剧情任务 |
| `script/data/taskdata.py` | 3221 | `GetData, GetNianShouTaskID` | 任务数据表 |
| `script/data/shitutaskdata.py` | 1308 | `GetTaskInfo` | 师徒任务数据 |
| `script/data/juben/task*.py` | 320 条 | `GetJubenData` | 剧情演出脚本 |

---

## 6. UI 表面（服务端不直接渲染，但决定交互）

- 任务对话框：`dlgtasknew.py`（`CTaskDialog/CTaskItem`，接受/追踪/放弃/交付链接）。
- 任务追踪：`dlgtasktracetaskframe.py`（`CTaskFollowFrame`，追踪/预览奖励/引导提示/自动寻路）。
- 新剧情面板：`dlgdreamnote.py`（NPC 亲密度、场景地图描述、信件历史）、`dlgdreamletter.py`（信件标题/描述/礼物/选项）。
- 新手引导：`rookieguide.py`（日历/修练/变强指引）。

服务端应保证这些 UI 所需的数据字段（任务名、描述、进度、奖励预览、NPC 状态、场景进度、信件列表）可查询。

---

## 7. 依赖与边界

| 依赖模块 | 交互点 | 说明 |
|---|---|---|
| `world` / 地图 | `載入地圖`, `C2SRequestSceneMapSchedule`, `S2CRefreshSceneMapSchedule` | 剧情演出与场景进度强相关；地图权威状态在 world 模块 |
| `npc` | `C2SRequestNpcData`, `C2SReceiveNpcTask`, `S2CRefreshNpcData`, `S2CUnpackClientNpc`, `AddClientNpc/UpdateClientNpc` | NPC 生成/移动/对话由剧情驱动，但 NPC 权威状态在 npc 模块 |
| `inventory` / `economy` | 任务奖励、交付物品、礼物 | 奖励发放必须走 economy/inventory 公开契约，不能直接写表 |
| `pet` / `children` / `social` | 部分任务条件（宠物/子女/师徒/婚姻） | 通过各自模块契约查询，不越界 |
| `activity` | 活动任务、日历指引 | 与 quest.onboarding 重叠，注意去重 |
| `mail` | 信件历史（`C2SSendLetter/C2SGetLetterHistory`） | 可能归属 mail 模块，需确认所有权 |
| `battle` | `S2CWarFailTips`（引导） | 仅提示，不改战斗结算 |

---

## 8. 服务端设计建议（对应 `QuestAPI`）

当前 `contracts.py` 仅有 `list_active / accept / claim_reward`。建议按 feature 拆分：

### 8.1 `quest.story`
- `accept_story_task(ctx, quest_template_id) -> CommandReceipt`
- `evaluate_objective(ctx, quest_instance_id, objective_key, value) -> ...`
- `progress_story(ctx, quest_instance_id, stage) -> ...`
- `claim_story_reward(ctx, quest_instance_id) -> CommandReceipt`
- 查询：`get_story_progress(ctx, quest_instance_id) -> QuestProgressView`
- NPC/场景：`request_npc_data`, `receive_npc_task`, `request_scene_schedule`（或委托给 npc/world 模块）

### 8.2 `quest.tracking`
- `set_tracking(ctx, quest_instance_id, enabled)`
- `query_task_targets(ctx, quest_instance_id)`
- `submit_task_items(ctx, quest_instance_id, items)`

### 8.3 `quest.onboarding`
- `query_guide_chapters(ctx)`
- `advance_guide_objective(ctx, chapter_id, objective_key)`
- `claim_chapter_reward(ctx, chapter_id)`

### 8.4 状态与并发
- 剧情进度需 `revision`（乐观并发）；重复请求幂等。
- 任务增删（`S2CTaskAdd/Remove`）必须与进度事务同提交。
- 客户端完成通知（`C2SFinishClientTask`）**不能直接发奖**，需服务端重新校验条件。
- 奖励发放与资产变更在同一工作单元；失败需可恢复（重试/补偿）。

### 8.5 事件
- `StoryTaskAccepted`, `StoryObjectiveProgressed`, `StoryTaskCompleted`, `StoryRewardClaimed`
- `NpcTaskReceived`, `SceneScheduleUpdated`, `LetterSent`, `GiftClaimed`

---

## 9. 未知与待核实（不要假设）

1. 320 条 `juben` 文件的 jubenID 与任务 ID 的映射关系未核实；部分文件反编译损坏（如 `\x95wdNPC`）。
2. `JUBENDATA` 的第 0 个元素（常为 `None`）与场景头的精确语义未核实。
3. `juqingdata.py` 的 `GetData` 返回结构未反编译到输出目录，需从 `data/script.fls` 重新提取。
4. 协议字段（坐标、NPC ID、进度值）未从封包样本中确认；当前只有函数名。
5. `C2SFinishClientTask` 是否为权威完成信号，还是仅客户端动画结束通知，需抓包确认。
6. 信件/礼物（`C2SSendLetter/C2SGetGift`）是否归属 `quest` 还是 `mail`，需与模块负责人确认。
7. 新手引导（onboarding）是否拆为独立模块，feature_specs 建议 `proposed_independent_module: onboarding`，但当前归口 quest。
8. `S2CJuqingStatus` 的字段与触发时机未核实。

---

## 10. 参考路径

- `server/docs/features/quest.story.md`（生成的材料卡，328 条目）
- `server/docs/features/quest.tracking.md`
- `server/docs/features/quest.onboarding.md`
- `server/docs/feature_specs.json`（feature 35/36/37）
- `server/src/mxsj_server/modules/quest/README.md`, `FEATURES.md`, `contracts.py`
- `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/quest-item-analysis.md`
- `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/protocol-commands-catalog.md`
- `work/dream-world-connect-login-map/notes/task-b-脚本分析/artifacts/fullrun/v4ok-classified.json`
- `tools/decompiler/output/script_fls_pycdc/script/data/juben/*.py`
- 锁定输入：`data/script.fls` SHA256 `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`

> 原则：以上均为客户端材料线索，不能直接作为服务端规则。实现前需补齐操作前置条件、失败码、字段约束、数据模型和材料缺口，并提供成功/越权/重复/失败恢复测试。
