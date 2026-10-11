# 开关、补偿、停服与运营审计

工作包：`administration.operations`；当前归口：`administration`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

运维权限和审计是服务器要求，不从客户端GM实现照搬。

## 接口设计起点

`set_feature_policy / issue_approved_compensation / schedule_maintenance`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 475 | `script/mxgame/stopgamemodule/mdstopgamemodule.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 748 | `script/mxgame/combinecompensation/delegate/dgtcombinecompensationitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1130 | `script/mxgame/combinecompensation/delegate/dgtcombinecompensationmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1639 | `script/mxgame/combinecompensation/view/dlgcombinecompensationitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1892 | `script/mxgame/stopgamemodule/stopgamemoduleinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1959 | `script/mxgame/combinecompensation/netservercombine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2618 | `script/mxgame/combinecompensation/model/mdcombinecompensation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2699 | `script/mxgame/combinecompensation/view/dlgcombinecompensationmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3082 | `script/data/switchdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3514 | `script/mxgame/stopgamemodule/netstopgamemodule.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CStopGameModule |
| 3842 | `script/mxgame/combinecompensation/combinecompensationdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4046 | `script/mxgame/stopgamemodule/gamemoduledefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
