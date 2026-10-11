# 天梯房间、匹配、段位与赛季

工作包：`activity.ladder`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`create_match_room / join_match_queue / accept_match / claim_season_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 一级目录拆分建议

建议评审独立模块 `competition`。当前仍在原责任区研究，尚未创建该独立实现，也没有默认批准跨域写入。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 96 | `script/mxgame/activity/ladderrank/netladderrank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CLadderRank, S2COpenRoomListDlg, S2CRefreshRoomList, S2CRefreshTeamMember, S2CRefreshOneRoom, S2CMemberOut |
| 183 | `script/mxgame/activity/ladderrankallstar/delegate/dgtseparategroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 261 | `script/mxgame/activity/ladderrank/delegate/dgtrankbattleitemdialog.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 279 | `script/mxgame/activity/ladderrankallstar/delegate/dgtteammember.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 433 | `script/mxgame/activity/ladderrankallstar/delegate/dgtmatchlive.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 501 | `script/mxgame/activity/ladderrank/dlgladderrank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 682 | `script/mxgame/activity/ladderrankallstar/view/dlgguesscoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 687 | `script/mxgame/activity/ladderrankallstar/model/mdallgameguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 752 | `script/mxgame/activity/ladderrank/view/dlgladderinfo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 831 | `script/mxgame/activity/ladderrankallstar/delegate/dgtchampionguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 968 | `script/mxgame/activity/ladderrankallstar/view/dlgladderrankitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1279 | `script/mxgame/activity/ladderrank/model/mdrankbattleitemdialog.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1287 | `script/mxgame/activity/ladderrank/delegate/dgtrewardpreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1304 | `script/mxgame/activity/ladderrankallstar/view/dlgseparategroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1370 | `script/mxgame/activity/ladderrankallstar/view/dlgladderrankgroupmatch.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1408 | `script/mxgame/activity/ladderrankallstar/model/mdladderrankallstar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1411 | `script/mxgame/activity/ladderrankallstar/view/dlgguessshop.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1465 | `script/mxgame/activity/ladderrankallstar/delegate/dgtladderrankallstarmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1487 | `script/mxgame/activity/ladderrankallstar/view/dlgcreateteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1500 | `script/mxgame/activity/ladderrankallstar/ladderrankinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1616 | `script/mxgame/activity/ladderrank/view/dlgladderreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1635 | `script/mxgame/activity/ladderrankallstar/view/dlgchampionguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1643 | `script/mxgame/activity/ladderrankallstar/model/mdguesscoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1900 | `script/mxgame/activity/ladderrank/delegate/dgtladderreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1902 | `script/mxgame/activity/ladderrankallstar/view/dlgladdergameguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2078 | `script/mxgame/activity/ladderrankallstar/view/dlgteammember.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2084 | `script/mxgame/activity/ladderrankallstar/delegate/dgtladderrankkfinals.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2203 | `script/mxgame/activity/ladderrankallstar/view/dlgteamtips.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2403 | `script/mxgame/activity/ladderrank/interfaceladder.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2444 | `script/mxgame/activity/ladderrankallstar/delegate/dgtallstarschedulemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2651 | `script/mxgame/activity/ladderrankallstar/delegate/dgtguessshop.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2671 | `script/mxgame/activity/ladderrank/delegate/dgtlarderranknew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetRankData |
| 2682 | `script/mxgame/activity/ladderrankallstar/netladderrankallstar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSCreateTeam, C2SAllTeamType, C2GSTeamInfo, C2GSTeamTip, C2GSMatchTip, C2GSAllRankInfo |
| 2786 | `script/mxgame/activity/ladderrankallstar/delegate/dgtladderrankguessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2937 | `script/mxgame/activity/ladderrankallstar/delegate/dgtguesscoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3033 | `script/mxgame/activity/ladderrankallstar/view/dlgallstarschedulemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3349 | `script/mxgame/activity/ladderrankallstar/view/dlgmatchlive.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3502 | `script/mxgame/activity/ladderrankallstar/view/dlgallteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3602 | `script/mxgame/activity/ladderrankallstar/delegate/dgtladderrankgroupmatch.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3612 | `script/mxgame/activity/ladderrankallstar/view/dlgladderrankfinals.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3877 | `script/mxgame/activity/ladderrankallstar/view/dlgcompetitionreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3891 | `script/mxgame/activity/ladderrankallstar/view/dlgbattleasupport.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3895 | `script/mxgame/activity/ladderrankallstar/ladderrankallstardefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4075 | `script/mxgame/activity/ladderrankallstar/delegate/dgtallgameguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4258 | `script/mxgame/activity/ladderrankallstar/testladderrankallstar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2COpenCDPanel, GS2CZhuWeiInfo |
| 4273 | `script/mxgame/activity/ladderrankallstar/view/dlgladderrankguessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4275 | `script/mxgame/activity/ladderrankallstar/view/dlgladderrankallstarmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4341 | `script/mxgame/activity/ladderrank/rankbattleitemdialogdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4372 | `script/mxgame/activity/ladderrankallstar/delegate/dgtcompetitionreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4469 | `script/mxgame/activity/ladderrank/view/dlgrewardpreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4733 | `script/mxgame/activity/ladderrank/view/dlgladderranknew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4776 | `script/mxgame/activity/ladderrank/ladderrankmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4974 | `script/mxgame/activity/ladderrank/view/rankbattleitemdialog.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
