# 子女培养与成长

工作包：`children.cultivation`；当前归口：`children`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`query_child_growth / cultivate_child / select_child_training`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 91 | `script/mxgame/newchild/delegate/dgtnewchildraise.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 237 | `script/mxgame/newchild/view/dlgnewchildrename.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 263 | `script/mxgame/newchild/newchilddefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 316 | `script/mxgame/newchild/dlgnewchildgetitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 363 | `script/mxgame/newchild/model/mdnewchildchoose.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 662 | `script/mxgame/newchild/view/dlgnewchildtrain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 840 | `script/mxgame/newchild/dlgnewchildoldtrain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 869 | `script/mxgame/newchild/model/mdnewchildtrain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1059 | `script/mxgame/newchild/netnewchild.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetTask, C2SFinishTask, C2SManGameSuccess, C2SWomanGameSuccess, C2SRandomChangeShape, C2SSelectChangeShape |
| 1267 | `script/mxgame/newchild/delegate/dgtnewchildname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1515 | `script/mxgame/newchild/newchild.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1586 | `script/mxgame/newchild/model/mdnewchildname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1687 | `script/mxgame/newchild/dlgnewchildreset.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1890 | `script/mxgame/newchild/view/dlgnewchildchoose.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2384 | `script/mxgame/newchild/model/mdnewchildraise.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2613 | `script/mxgame/newchild/dlgnewchildborn.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2949 | `script/mxgame/newchild/dlgnewchildexam.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3087 | `script/mxgame/newchild/view/dlgnewchildraise.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3477 | `script/mxgame/newchild/view/dlgnewchildname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3485 | `script/mxgame/newchild/view/dlgnewchildlookafter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3515 | `script/data/childdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3517 | `script/mxgame/newchild/dlgnewchildboilwater.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4136 | `script/mxgame/newchild/delegate/dgtnewchildlookafter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4228 | `script/mxgame/newchild/delegate/dgtnewchildchoose.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4421 | `script/mxgame/newchild/delegate/dgtnewchildtrain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4442 | `script/mxgame/newchild/model/mdnewchildlookafter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
