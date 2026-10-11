# 赛事战队、赛程、报名和观战

工作包：`activity.tournaments`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

不能把赛事编排和一场战斗的结算放在同一模块。

## 接口设计起点

`register_tournament_team / query_bracket / schedule_match / subscribe_match`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 一级目录拆分建议

建议评审独立模块 `competition`。当前仍在原责任区研究，尚未创建该独立实现，也没有默认批准跨域写入。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 185 | `script/mxgame/serverbattle/netserverbattleallstart.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetBattleTableTeamInfo, C2SGetBattleTableBattleInfo, C2SOpenFinalsBattleTable, C2SRequestFinalsMatchDetail, C2SOpsRollDlg, C2SShowDrawLotsDlg |
| 266 | `script/mxgame/serverbattle/view/dlgteamreport.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 324 | `script/mxgame/serverbattle/view/allstart/dlgallstartguessmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 366 | `script/mxgame/serverbattle/view/allstart/dlgsbasbattletable.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 382 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartgamegroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 395 | `script/mxgame/serverbattle/view/allstart/dlgallstartgameschedule.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 402 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartmatchtable.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 444 | `script/mxgame/serverbattle/view/allstart/dlgallstartgameguessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 490 | `script/mxgame/serverbattle/view/dlgtop8table.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 514 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartgameprocessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 768 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 783 | `script/mxgame/serverbattle/delegate/dgtserverbattleteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 790 | `script/mxgame/serverbattle/model/allstart/mdallstarguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 950 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartgameschedule.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1016 | `script/mxgame/serverbattle/delegate/allstart/dgtallstardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1230 | `script/mxgame/serverbattle/model/allstart/mdallstartguessmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1280 | `script/mxgame/serverbattle/view/allstart/dlgallstartgameguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1298 | `script/mxgame/serverbattle/view/allstart/dlgallstartgamegroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1325 | `script/mxgame/serverbattle/view/allstart/dlgallstartmatchtable.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1359 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartmatchtableend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1415 | `script/mxgame/serverbattle/delegate/dgttop8table.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1433 | `script/mxgame/serverbattle/delegate/allstart/dgtallstarmathtablemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1521 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartchampionguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1561 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartgameguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1605 | `script/mxgame/serverbattle/view/allstart/allstarinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1679 | `script/mxgame/serverbattle/netserverbattlerank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SServerBattlePlayerInfo, C2SServerBattleRankInfo |
| 1775 | `script/mxgame/serverbattle/serverbattleinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1861 | `script/mxgame/serverbattle/model/mdserverbattleteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1897 | `script/mxgame/serverbattle/model/allstart/mdallstardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2002 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartmatchtablemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2026 | `script/mxgame/serverbattle/netserverbattleteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenChangeName, S2CShowChangeName, C2SChangeName, S2COnChangeName, C2SOpenInviteFrd, S2CShowInviteFrd |
| 2122 | `script/mxgame/serverbattle/serverbattledefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2681 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartgameguessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2727 | `script/mxgame/serverbattle/testtianxuan.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CRefreshDragonInfo, S2CTeamInfo, S2CInsertBattle, S2CTeamRecord, S2CTeamRank, S2CTeamManagerInfo |
| 2789 | `script/mxgame/serverbattle/view/allstart/dlgsbteamlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2822 | `script/mxgame/serverbattle/view/dlgteamkick.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2901 | `script/mxgame/serverbattle/view/dlgteamhistory.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3147 | `script/mxgame/serverbattle/view/dlgteamwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3185 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartwogroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3233 | `script/mxgame/serverbattle/delegate/allstart/dgtsbasbattletable.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3241 | `script/mxgame/serverbattle/view/allstart/dlgallstartgamegroupmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3359 | `script/mxgame/serverbattle/model/allstart/mdsbasroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3364 | `script/mxgame/serverbattle/netallstarguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenMainDlg, S2COpenMainDlg, C2SRequestMatchGuess, C2SRequestChampoinGuess, C2SGuessChampion, C2SGuessMatch |
| 3398 | `script/mxgame/serverbattle/view/allstart/dlgallstartmatchtableend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3476 | `script/mxgame/serverbattle/view/allstart/dlgsbasroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3589 | `script/mxgame/serverbattle/view/dlgbattlerank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3597 | `script/mxgame/serverbattle/model/allstart/mdsbasbattletable.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3672 | `script/mxgame/serverbattle/view/allstart/dlgallstardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3763 | `script/mxgame/serverbattle/model/mdserverbattlerank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3809 | `script/mxgame/serverbattle/view/allstart/dlgallstartmatchtablemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3860 | `script/mxgame/serverbattle/view/allstart/dlgallstartgametwogroup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3995 | `script/mxgame/serverbattle/view/dlgteaminvitefrd.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4029 | `script/mxgame/serverbattle/view/dlgteamchangename.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4403 | `script/mxgame/serverbattle/serverbattlepopmenu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4484 | `script/mxgame/serverbattle/view/dlgserverbattleteam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4493 | `script/mxgame/serverbattle/delegate/allstart/dgtsbasroll.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4522 | `script/mxgame/serverbattle/view/dlgserverbattlerank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4584 | `script/mxgame/serverbattle/view/allstart/dlgallstarguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4620 | `script/mxgame/serverbattle/view/dlgteamrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4654 | `script/mxgame/serverbattle/view/allstart/allstartgameprocessmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4668 | `script/mxgame/serverbattle/view/allstart/dlgallstartmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4736 | `script/mxgame/serverbattle/delegate/allstart/dgtallstarguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4770 | `script/mxgame/serverbattle/delegate/allstart/dgtallstartguessmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4933 | `script/mxgame/serverbattle/model/mdtop8table.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4949 | `script/mxgame/serverbattle/view/allstart/dlgallstartchampionguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
