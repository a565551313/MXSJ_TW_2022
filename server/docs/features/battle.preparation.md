# 战前准备、装备方案与附魔方案

工作包：`battle.preparation`；当前归口：`battle`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

装备与消耗由inventory/crafting负责，不由战斗直接改表。

## 接口设计起点

`save_preparation_plan / apply_preparation_plan / snapshot_combatants`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 44 | `script/mxgame/warprepare/delegate/dgtonekeyfumosummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 58 | `script/mxgame/warprepare/model/mdonekeyhuanhua.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 364 | `script/mxgame/warprepare/delegate/dgtonekeyfumo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 660 | `script/mxgame/warprepare/netwarprepare.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSOpenWarReadyDlg, C2GSSwitchEquibQsaw, C2GSOpenEquipSwitchDlg, C2GSRenameCase, C2GSChangeCaseItem, C2GSGetItemInfo |
| 736 | `script/mxgame/warprepare/delegate/dgtwarpreparemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 813 | `script/mxgame/warprepare/delegate/dgtonekeyfumohero.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 828 | `script/mxgame/warprepare/view/dlgwarprepareswitchequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 994 | `script/mxgame/warprepare/model/mdwarprepareswitchequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1229 | `script/mxgame/warprepare/view/dlgwarpreparemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1241 | `script/mxgame/warprepare/delegate/dgtwarprepareswitchequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1360 | `script/mxgame/warprepare/view/dlgchoosesameposequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1389 | `script/mxgame/warprepare/delegate/dgtnewwarprepareswitchequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1534 | `script/mxgame/warprepare/delegate/dgtonekeyhuanhua.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1618 | `script/mxgame/warprepare/view/dlgonekeyfumo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1974 | `script/mxgame/warprepare/view/dlgwarprepareshare.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2600 | `script/mxgame/warprepare/delegate/dgtchoosesameposequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3010 | `script/mxgame/warprepare/model/fumodatamgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3361 | `script/mxgame/warprepare/view/dlgonekeyfumosummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3557 | `script/mxgame/warprepare/view/dlgonekeyfumohero.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3635 | `script/mxgame/warprepare/warpreparedefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4100 | `script/mxgame/warprepare/view/dlgonekeyhuanhua.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4260 | `script/mxgame/warprepare/delegate/dgtfumootherbagequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4614 | `script/mxgame/warprepare/view/dlgfumootherbagequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4630 | `script/mxgame/warprepare/view/dlgnewwarprepareswitchequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4720 | `script/mxgame/warprepare/model/mdwarpreparemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
