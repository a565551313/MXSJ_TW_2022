# 婚姻与配偶玩法

工作包：`social.marriage`；当前归口：`social`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`request_marriage / confirm_marriage / request_divorce`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 128 | `script/mxgame/marriage/delegate/dgtmarriageseeking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 797 | `script/mxgame/marriage/view/dlgmarriagemodify.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1392 | `script/mxgame/marriage/marriageseekingctrl.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1451 | `script/mxgame/marriage/delegate/dgtmarriageregister.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1658 | `script/mxgame/marriage/delegate/dgtmarriagerequestlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1725 | `script/marriage.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CSearhI, S2CISearh, S2CMlist, S2CShowEnlist, S2CShowMarryDlg, S2CCloseMarryDlg |
| 2196 | `script/mxgame/marriage/view/dlgmarriagerequestlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2249 | `script/mxgame/marriage/delegate/dgtmarriageresponselist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2334 | `script/mxgame/marriage/marriageseekingdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2614 | `script/mxgame/marriage/model/mdmarriageseeking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2642 | `script/mxgame/marriage/netmarriageseeking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SMarriageSeekingList, C2SRegister, C2SModify, C2SCancelRegister, C2SResonse, C2SRequestList |
| 3053 | `script/mxgame/marriage/view/dlgmarriageresponseconfirm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3442 | `script/mxgame/marriage/model/mdmarriageresponselist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3574 | `script/mxgame/marriage/delegate/dgtmarriagemodify.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3866 | `script/mxgame/marriage/view/dlgmarriageregister.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3900 | `script/mxgame/marriage/view/dlgmarriageseeking.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4012 | `script/mxgame/marriage/delegate/dgtmarriageresponseconfirm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4139 | `script/mxgame/marriage/view/dlgmarriageresponselist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4215 | `script/mxgame/marriage/model/mdmarriagerequestlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
