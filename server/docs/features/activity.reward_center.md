# 礼包、奖励中心与赠礼

工作包：`activity.reward_center`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`list_reward_entitlements / claim_reward_entitlement / give_present`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 48 | `script/dialog/presentcenter/model/mdsummervacation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 56 | `script/dialog/presentcenter/presentcenterdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 104 | `script/mxgame/activityreward/delegate/dgtbuyactivityqua.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 155 | `script/mxgame/newgive/view/dlgnewgivefurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 205 | `script/dialog/presentcenter/model/mdchargepresentadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 227 | `script/dialog/presentcenter/view/dlgvip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SAutoVIPBuy |
| 242 | `script/mxgame/newgive/delegate/dgtnewgivemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 267 | `script/mxgame/newgive/view/dlggetpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 276 | `script/dialog/presentcenter/view/dlgdailylottery.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 315 | `script/mxgame/activityreward/view/dlgbuyactivityqua.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 374 | `script/mxgame/activityreward/delegate/dgtbppreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 401 | `script/dialog/presentcenter/view/dlgsummonpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 419 | `script/mxgame/newgive/givedefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 457 | `script/mxgame/newgive/model/newgivemgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 535 | `script/dialog/presentcenter/delegate/dgtpresentcenter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 536 | `script/mxgame/newgive/model/mdnewbuyflower.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 541 | `script/mxgame/activityreward/view/dlgtreasurecollection.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 552 | `script/dialog/presentcenter/netsummervacation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGetSummerVacationInfo, C2GSSignSummerVHcation |
| 772 | `script/dialog/presentcenter/delegate/dgtsummervacation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 811 | `script/dialog/presentcenter/view/dlglevelgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 855 | `script/mxgame/activityreward/view/dlgbftreasurechest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 878 | `script/mxgame/newgive/delegate/dgtnewgiveflower.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 932 | `script/mxgame/activityreward/delegate/dgtseasonchallenge.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1213 | `script/mxgame/newgive/delegate/dgtnewgivehuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1372 | `script/mxgame/newgive/delegate/dgtnewgivepet.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1380 | `script/dialog/presentcenter/delegate/dgtwinterpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1590 | `script/mxgame/newgive/delegate/dgtnewgiveappearance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1663 | `script/mxgame/newgive/view/dlgnewgivepet.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1671 | `script/mxgame/activityreward/delegate/dgtreasurecollection.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1703 | `script/mxgame/newgive/delegate/dgtnewbuyflower.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1810 | `script/dialog/presentcenter/netprerole.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSOpenPrePay, C2GSBindPayMember, C2GSQuestAllCharge |
| 1814 | `script/mxgame/newgive/view/dlgnewgivemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1829 | `script/dialog/presentcenter/view/dlgh5present.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1835 | `script/dialog/presentcenter/view/dlgwinterpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1840 | `script/dialog/presentcenter/model/mdfestivalgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1853 | `script/mxgame/activityreward/view/preview/dlgbppreview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1893 | `script/dialog/presentcenter/delegate/dgtaccumulatechargeadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1924 | `script/mxgame/newgive/delegate/dgtnewgiveitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1934 | `script/dialog/presentcenter/model/mdwinterpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2111 | `script/mxgame/activityreward/activityrewardutils.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2173 | `script/mxgame/newgive/view/dlgnewgivehuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2175 | `script/dialog/presentcenter/view/dlgpresentcenter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2378 | `script/mxgame/activityreward/delegate/dgtactivityrewardmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2413 | `script/dialog/presentcenter/view/presentcenterwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2414 | `script/mxgame/givepresent/dgtgivepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2450 | `script/mxgame/activityreward/delegate/dgtbfweekreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2502 | `script/dialog/presentcenter/delegate/dgtchargepresentadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2518 | `script/dialog/presentcenter/view/dlglevelpresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2586 | `script/mxgame/activityreward/view/dlgbfweekreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2702 | `script/mxgame/newgive/view/dlgnewgiveitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2706 | `script/mxgame/newgive/testnewgive.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2743 | `script/dialog/presentcenter/view/dlgaccumulatechargeadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2761 | `script/mxgame/newgive/view/dlgnewbuyflower.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2791 | `script/mxgame/newgive/view/dlgnewgiveflower.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2801 | `script/mxgame/activityreward/delegate/dgtzhanmenggift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2837 | `script/mxgame/activityreward/netactivityreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SAskGetReward, C2SAskGetAllReward, C2SOpenTreasureChest, C2SSnyTreasureChest, C2SCompositeTreasureChest, C2SGetActivityKey |
| 2899 | `script/mxgame/givepresent/mdgivepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3032 | `script/mxgame/activityreward/view/preview/dlgbppreviewpart.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3116 | `script/mxgame/activityreward/model/mdzhanmenggift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3175 | `script/dialog/presentcenter/delegate/dgtpresentcenterlevelgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3182 | `script/dialog/presentcenter/view/dlgsevendaypresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3346 | `script/mxgame/activityreward/view/dlgzhanmenggift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3472 | `script/dialog/presentcenter/delegate/dgtfirstchargeadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3473 | `script/mxgame/newgive/newgiveinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2COpenNewGiveDlg |
| 3548 | `script/mxgame/activityreward/view/dlgbprewardshow.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3554 | `script/dialog/presentcenter/delegate/dgtlimitedtimeoffer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3563 | `script/dialog/presentcenter/model/mdserverstartgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3576 | `script/mxgame/activityreward/view/dlgseasonchallenge.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3606 | `script/mxgame/givepresent/givepresentdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3615 | `script/dialog/presentcenter/view/dlgfirstchargepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3625 | `script/mxgame/newgive/delegate/dgtnewgivefurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3709 | `script/mxgame/activityreward/model/mdseasonchallenge.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3717 | `script/mxgame/newgive/view/dlgnewgiveappearance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3758 | `script/dialog/presentcenter/view/dlgreturnofoldplayerfornewserver.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3777 | `script/mxgame/givepresent/dlggivepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3779 | `script/dialog/presentcenter/delegate/dgtserverstartgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3997 | `script/mxgame/activityreward/delegate/dgtbftreasurechest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4011 | `script/dialog/presentcenter/model/mddailylottery.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4032 | `script/dialog/presentcenter/festivalgiftdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4039 | `script/dialog/presentcenter/delegate/dgtfestivalgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4124 | `script/dialog/presentcenter/view/dlgfirstchargeadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4129 | `script/dialog/presentcenter/view/dlglimitedtimeoffer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4359 | `script/dialog/presentcenter/view/dlgserverstartgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4363 | `script/dialog/presentcenter/delegate/dgtnewplayeradvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4410 | `script/dialog/presentcenter/view/dlgchargepresentadvance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4450 | `script/mxgame/activityreward/activityrewarddefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4457 | `script/mxgame/activityreward/view/dlgactivityrewardmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4482 | `script/dialog/presentcenter/delegate/dgtdailylottery.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4540 | `script/dialog/presentcenter/model/mdlimitedtimeoffer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4692 | `script/dialog/presentcenter/view/dlgsummervacation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4710 | `script/dialog/presentcenter/view/dlgfestivalgift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4735 | `script/dialog/presentcenter/model/mdpresentcenter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4910 | `script/dialog/presentcenter/view/dlgchargepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4925 | `script/dialog/presentcenter/view/dlgaccumulatechargepresent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4929 | `script/dialog/presentcenter/view/dlgreturnofoldplayerforweb.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4954 | `script/mxgame/activityreward/model/mdactivityreward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
