# 帮派Boss、洞窟、烧烤和精英帮战

工作包：`activity.guild_modes`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`enter_guild_activity / update_activity_objective / settle_guild_activity`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 108 | `script/mxgame/activity/groupbbq/delegate/dgtgroupbbqrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 191 | `script/mxgame/activity/eliteorgwar/view/dlgeliteorgwarprogress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 761 | `script/mxgame/activity/eliteorgwar/eliteorgwardefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1253 | `script/mxgame/activity/eliteorgwar/neteliteorgwar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenTeamMainDlg, C2SOpenTeamSetDlg, C2SAddMember, C2SDelMember, C2SCloseTeamDlg, C2SAddEliteTeam |
| 1324 | `script/mxgame/activity/guildcavern/view/dlgguildcavernroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1502 | `script/mxgame/activity/guildcavern/guildcaverndefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1821 | `script/mxgame/activity/guildcavern/model/mdguildcavernroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1860 | `script/mxgame/activity/groupbbq/view/dlggroupbbqtime.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1949 | `script/mxgame/activity/eliteorgwar/delegate/dgteliteorgwar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1981 | `script/mxgame/activity/groupbbq/view/dlggroupbbqrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1991 | `script/mxgame/activity/eliteorgwar/model/mdeliteorgwar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2238 | `script/mxgame/activity/guildcavern/model/mdguildcavern.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2503 | `script/mxgame/activity/eliteorgwar/view/dlgeliteorgwartime.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2603 | `script/mxgame/activity/groupbbq/groupbbqmap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2667 | `script/mxgame/activity/groupboss/netgroupboss.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CGameBossHP, S2CCloseBossHP, S2CUpdatePanel, S2CClosePanel, S2CGroupBoss |
| 2819 | `script/mxgame/activity/groupbbq/view/dlggroupbbq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2881 | `script/mxgame/activity/groupbbq/netgroupbbq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2COpenBBQDlg, S2CCloseDlg, S2CAddItem, S2CRefreshItemState, S2CStartProgress, S2COpenRecordDlg |
| 3025 | `script/mxgame/activity/groupbbq/groupbbqdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3026 | `script/mxgame/activity/guildcavern/view/dlgguildcavernprogress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3089 | `script/mxgame/activity/guildcavern/netguildcavern.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenRewardDlg, C2SLotteryReward, C2SStartRoll, C2SRollEnd, S2CShowProgress, S2CCloseProgress |
| 3276 | `script/mxgame/activity/groupboss/dlggroupboss.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3316 | `script/mxgame/activity/groupbbq/netnewgroupbbq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CQuestionGameState, S2CBBQStep, S2CChefCountDown, S2CNewBBQProcess, C2SQuestionStateChange |
| 3418 | `script/mxgame/activity/groupbbq/model/mdgroupbbq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3579 | `script/mxgame/activity/eliteorgwar/elitewarmap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3922 | `script/mxgame/activity/eliteorgwar/eliteorgwartest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3943 | `script/mxgame/activity/guildcavern/delegate/dgtguildcavern.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4121 | `script/mxgame/activity/guildcavern/guildcaverntest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4467 | `script/mxgame/activity/groupbbq/delegate/dgtgroupbbq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4476 | `script/mxgame/activity/groupbbq/model/mdgroupbbqrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4556 | `script/mxgame/activity/guildcavern/view/dlggldcapreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4714 | `script/mxgame/activity/guildcavern/delegate/dgtguildcavernroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4824 | `script/mxgame/activity/eliteorgwar/view/dlgeliteorgwarteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4839 | `script/mxgame/activity/eliteorgwar/view/dlgeliteorgwarteamset.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
