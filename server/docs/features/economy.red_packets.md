# 世界红包、系统红包与领用

工作包：`economy.red_packets`；当前归口：`economy`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

余额托管、领取唯一键、剩余金额与过期返还。

## 接口设计起点

`create_red_packet / claim_red_packet / expire_red_packet`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 306 | `script/mxgame/worldhongbao/networldhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SShowWorldHongbaoDlg, C2SCheckWorldHongbao, C2SOpenWorldHongbao, C2SRefreshSendHongbaoCash, C2SSendWorldHongbao, C2SRequestFriendIdList |
| 582 | `script/mxgame/worldhongbao/hongbaospecialtips.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 862 | `script/mxgame/worldhongbao/dlgsearchplayer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1450 | `script/mxgame/systemhongbao/netsystemhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SLinkSystemHongbao, C2SOpenSystemHongbao, S2CRefreshSystemHongbaoStatus, S2COpenSystemHongbao, S2CSystemHongaoDetail, S2CSystemHongbaoProcess |
| 2676 | `script/mxgame/worldhongbao/dlgsendworldhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2959 | `script/mxgame/systemhongbao/dlgsystemhongbaodetail.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3861 | `script/mxgame/systemhongbao/dlgopensystemHongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4073 | `script/mxgame/worldhongbao/dlgrecordworldhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4102 | `script/mxgame/worldhongbao/hongbaochatoutput.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4123 | `script/mxgame/worldhongbao/dlgopenworldhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4198 | `script/mxgame/worldhongbao/dlgworldhongbao.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
