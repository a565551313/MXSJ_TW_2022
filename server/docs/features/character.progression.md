# 自动升级、属性与流派成长

工作包：`character.progression`；当前归口：`character`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`allocate_attributes / request_level_up / select_progression_plan`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 1608 | `script/data/liupaileveldata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1637 | `script/mxgame/attribute/testattributemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1881 | `script/mxgame/autoupgrade/dlgautoupgrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2055 | `script/mxgame/autoupgrade/delegate/dgtautoupgrade_log.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2179 | `script/mxgame/autoupgrade/dlgmagicviewforautograde.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2462 | `script/mxgame/attribute/dlgattributemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2579 | `script/mxgame/autoupgrade/model/mdautoupgrde.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2908 | `script/mxgame/autoupgrade/delegate/dgtmagicviewforautograde.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3092 | `script/data/newxinfa.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3323 | `script/mxgame/attribute/mdattribute.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3795 | `script/mxgame/attribute/dgtattributemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4172 | `script/mxgame/attribute/attributedefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4439 | `script/mxgame/autoupgrade/netautoupgrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSubmit, C2SGetSummonInfo, C2SGetEquipInfo, C2GSNeverShowUpgradePage, C2GSGetAutoUpgradeData, S2COpenAutoUpgradeDialog |
| 4557 | `script/mxgame/autoupgrade/delegate/dgtautoupgrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4956 | `script/mxgame/attribute/netattribute.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
