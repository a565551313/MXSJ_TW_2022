# 日常固定队与队长激励

工作包：`party.daily`；当前归口：`party`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`query_daily_team / register_daily_team / claim_captain_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 307 | `script/mxgame/dailyteam/logicshowdailyteam/showlogic_dgtdailyteamtask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 650 | `script/mxgame/dailyteam/testdailyteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CUpdateTeamInfo |
| 830 | `script/mxgame/dailyteam/mddailyteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1396 | `script/mxgame/captainbonus/netcaptainbonus.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SAppreciate, C2SAppreciateFriend, S2COpenDialog, S2CCloseDialog, S2CCaptainBonus |
| 1445 | `script/mxgame/dailyteam/logicshowdailyteam/showlogic_dgtdailyteammain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1790 | `script/mxgame/dailyteam/netdailyteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGetDailyTeamInfo, C2GSOpenInviteFriendDlg, C2GSLeaveDailyTeam, C2SChangeDailyTeamIntro, C2GSKickMember, C2GSChangeLeader |
| 2498 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteamintro.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2615 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteamoperate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2641 | `script/mxgame/dailyteam/logicshowdailyteam/showlogic_dailyteamrecruit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2880 | `script/mxgame/dailyteam/dailyteamdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2969 | `script/mxgame/dailyteam/logicshowdailyteam/showlogic_dgtdailyteaminfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2993 | `script/mxgame/dailyteam/dgtdailyteam/dgtdailyteamtask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3024 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteamziku.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3188 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteammain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3677 | `script/mxgame/dailyteam/dailyteampopmenu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3707 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteamtask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3906 | `script/mxgame/captainbonus/dlgcaptainbonus.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3964 | `script/mxgame/dailyteam/logicshowdailyteam/showlogic_dgtrecuitmember.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4389 | `script/mxgame/dailyteam/dgtdailyteam/dgtdailyteammain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4871 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteamname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4905 | `script/mxgame/dailyteam/dlgdailyteam/dlgdailyteaminfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4952 | `script/mxgame/dailyteam/dgtdailyteam/dgtdailyteaminfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
