# 回归、召回、回归收集与补偿

工作包：`activity.returning`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`query_returning_status / claim_returning_reward / exchange_collection`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 359 | `script/mxgame/return2020/dgt2020returnrecruit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 421 | `script/mxgame/return2020/dlg2020returnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 485 | `script/mxgame/return2020/dlg2020returnrecruit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 606 | `script/mxgame/returnwish/dgtreturnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 642 | `script/mxgame/return2020/dgt2020returnreturn.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 670 | `script/mxgame/returncollectcards/dgtreturncollectcards.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 679 | `script/mxgame/return/showlogic_return/showlogic_dlgreturnmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 807 | `script/mxgame/return/returnrewardmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SFirstReward, C2SBuyPayPresent, C2SRequestTips |
| 995 | `script/mxgame/return2020/dgt2020returnapplyjoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1217 | `script/mxgame/return2020/dgt2020returnfriend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1357 | `script/mxgame/return/showlogic_return/showlogic_dlgreturnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1401 | `script/mxgame/returnwish/mdreturnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1437 | `script/mxgame/returnwish/dlgreturnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1744 | `script/mxgame/return2020/dgt2020returnreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1750 | `script/mxgame/return/dlgreturnreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1805 | `script/mxgame/return/dgtreturnreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1969 | `script/mxgame/return2020/dgt2020returnmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2038 | `script/mxgame/return2020/md2020returnrecuit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2077 | `script/mxgame/return/netreturnreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSelectEquip, C2SBuyPayPresent, C2SOpenProccessPresent, C2SSwitchTmpWing, C2SSwitchTmpHorse, C2SSelectPlayer |
| 2081 | `script/mxgame/return2020/dlg2020returnmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2095 | `script/mxgame/rookieback/netrookieback.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSOpenMainDlg, C2GSOpenWishDlg, C2GSAddSuperReward, C2GSClickLuckDraw, C2GSChickHuoyueReward, C2GSRewardTask |
| 2257 | `script/mxgame/returncollectcards/dlgreturncard.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2429 | `script/mxgame/returnwish/mdreturnwish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2487 | `script/mxgame/rookieback/dlgrookiebackreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2664 | `script/mxgame/return/showlogic_return/showlogic_dlgreturncollectcards.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2712 | `script/mxgame/return2020/dlg2020returnselect.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2718 | `script/mxgame/return/dlgreturnrewardfindfriend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3086 | `script/mxgame/returnwish/dgtreturnwish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3128 | `script/mxgame/returncollectcards/mdreturncollectcards.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3129 | `script/mxgame/returnwish/dlgreturnwish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3146 | `script/mxgame/return2020/dgt2020returnhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3719 | `script/mxgame/return2020/dlg2020returnfriend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3726 | `script/mxgame/return2020/net2020return.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenRewardDialog, C2SChgBindPlayer, C2SReleaseBindPlayer, C2SRecruitPlayer, C2SGetReward, C2SOpenFriendDialog |
| 3808 | `script/mxgame/returncollectcards/dlgreturncollectcards.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3883 | `script/mxgame/return2020/md2020return.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3894 | `script/mxgame/return/returnrewarddefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4047 | `script/mxgame/return2020/md2020returnapplyjoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4332 | `script/mxgame/return2020/dlg2020returnreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4430 | `script/mxgame/return2020/dlg2020returnapplyjoin.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4840 | `script/mxgame/rookieback/mdrookiebackreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGetShouChongReward, C2SBuyPayPresent |
| 4902 | `script/mxgame/returncollectcards/returncollectcardsdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4965 | `script/mxgame/return/showlogic_return/showlogic_dlgreturntask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
