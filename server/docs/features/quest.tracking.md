# 任务追踪、导航与交付

工作包：`quest.tracking`；当前归口：`quest`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`set_tracking / query_task_targets / submit_task_items`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 166 | `script/mxgame/tasktrace/view/dlgtasktracetaskframe.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 817 | `script/mxgame/tasktrace/model/mdhuodongtrace.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 821 | `script/mxgame/tasktrace/model/mdtasktrace.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1569 | `script/mxgame/tasktrace/view/tasktraceitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1996 | `script/mxgame/tasktrace/view/dlgtasktracehuodongframe.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2024 | `script/mxgame/tasktrace/tasktraceutil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2134 | `script/mxgame/tasktrace/model/mdtasktraceprase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2393 | `script/mxgame/tasktrace/delegate/dgttasktracemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2512 | `script/mxgame/tasktrace/delegate/dgttasktracetaskframe.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3214 | `script/mxgame/tasktrace/tasktracedefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3735 | `script/mxgame/tasktrace/model/mdhuodongtraceprase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3960 | `script/mxgame/tasktrace/delegate/dgttasktracehuodongframe.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4045 | `script/mxgame/tasktrace/view/dlgtasktrace.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4414 | `script/mxgame/tasktrace/model/mdtasktracesort.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4913 | `script/mxgame/task/nettask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetTask, S2CJuqingStatus, S2CUnpackClientNpc, S2CTaskAdd, S2CTaskRemove, C2SGiveUpTask |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
