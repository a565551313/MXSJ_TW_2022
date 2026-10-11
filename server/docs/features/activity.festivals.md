# 节日、周年与限时活动

工作包：`activity.festivals`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

完整活动目录另列，不把所有活动当成同一种万能脚本。

## 接口设计起点

`join_event_instance / progress_event_objective / claim_event_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 11 | `script/mxgame/activity/2021springactivity/model/md2021springactivity.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 47 | `script/mxgame/activity/2019znq/net2019znq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 83 | `script/mxgame/activity/2021duangwu/Illustratedbooks/dlg2021duangwuIllustratedbooks.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 456 | `script/mxgame/activity/2021duangwu/personalhelp/dgt2021duangwupersonalhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 542 | `script/mxgame/activity/2021duangwu/cooking/dgt2021duangwucooking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 750 | `script/mxgame/activity/2021springactivity/net2021springactivity.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSSendLogData |
| 758 | `script/mxgame/activity/2021springactivity/dgt/dgt2021springhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 906 | `script/mxgame/activity/2019znq/view/dlg2019znqhappy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 952 | `script/mxgame/activity/2021duangwu/netduanwu2021.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSRequestMainDlgData, C2GSClickZongziActBtn, C2GSReceiveAward, C2GSInitiateHelp, C2GSHelpSpeedUp, C2GSOpenPersonalHelpDlg |
| 1101 | `script/mxgame/activity/2021duangwu/personalhelp/dlg2021duangwupersonalhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1116 | `script/mxgame/activity/2021duangwu/cooking/md2021duangwucooking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1133 | `script/mxgame/activity/2021duangwu/speedup/dlg2021duangwuspeedup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1341 | `script/mxgame/activity/2021springactivity/view/dlg2021springfuniu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1345 | `script/mxgame/activity/2021duangwu/helplist/md2021duangwuhelplist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1439 | `script/mxgame/activity/2019znq/mx2019znqtest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1510 | `script/mxgame/activity/2021springactivity/dgt/dgt2021springactivity.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1631 | `script/mxgame/activity/2021duangwu/duangwu2021define.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1763 | `script/mxgame/activity/2021springactivity/view/dlg2021springdinner.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1914 | `script/mxgame/activity/2021springactivity/dgt/dgt2021springdinner.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1997 | `script/mxgame/activity/2019znq/model/md2019znqshengxiao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2051 | `script/mxgame/activity/2019znq/view/dlg2019znqjianghu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2324 | `script/mxgame/activity/2021duangwu/main/dlg2021duangwumain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2632 | `script/mxgame/activity/2019znq/delegate/dgt2019znqmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2698 | `script/mxgame/activity/2019znq/delegate/dgt2019znqhappy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2714 | `script/mxgame/activity/2019znq/view/dlg2019znqshengxiao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2888 | `script/mxgame/activity/2021duangwu/helplist/dlg2021duangwuhelplist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2902 | `script/mxgame/activity/2021springactivity/view/dlg2021springhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2924 | `script/mxgame/activity/2019znq/view/dlg2019znqmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2986 | `script/mxgame/activity/2021springactivity/view/dlg2021springactivitymain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3254 | `script/mxgame/activity/2021duangwu/cooking/dlg2021duangwucooking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3428 | `script/mxgame/activity/2021duangwu/duangwu2021interface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3562 | `script/mxgame/activity/2021duangwu/test2021duangwu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3577 | `script/mxgame/activity/2021duangwu/main/md2021duangwumain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3980 | `script/mxgame/activity/2019znq/mx2019znqdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4223 | `script/mxgame/activity/2019znq/delegate/dgt2019znqjianghu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4263 | `script/mxgame/activity/2021duangwu/personalhelp/md2021duangwupersonalhelp.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4268 | `script/mxgame/activity/2021duangwu/main/dgt2021duangwumain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4292 | `script/mxgame/activity/2021springactivity/view/dlg2021springtreasure.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4489 | `script/mxgame/activity/2019znq/model/md2019znq.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4604 | `script/mxgame/activity/2021duangwu/helplist/dgt2021duangwuhelplist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4781 | `script/mxgame/activity/2019znq/delegate/dgt2019znqshengxiao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4916 | `script/mxgame/activity/2021duangwu/materialsource/dlg2021duangwumaterialsource.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
