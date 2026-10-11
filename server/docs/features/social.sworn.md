# 结拜及成员关系

工作包：`social.sworn`；当前归口：`social`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`create_sworn_group / invite_sworn_member / leave_sworn_group`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 113 | `script/mxgame/sibling/delegate/dgtsiblinginvite.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 253 | `script/mxgame/sibling/view/dlgsiblinginvite.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 442 | `script/mxgame/sibling/view/dlgsiblinghome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 626 | `script/mxgame/sibling/view/dlgsiblingbadge.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1086 | `script/mxgame/sibling/delegate/dgtsiblingchat.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1221 | `script/mxgame/sibling/view/dlgmakeavow.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1407 | `script/data/sibilingdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1556 | `script/mxgame/sibling/model/mdsiblingsort.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1582 | `script/mxgame/sibling/view/dlgsiblingsort.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1626 | `script/mxgame/sibling/delegate/dgtsiblingvote.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1645 | `script/mxgame/sibling/view/dlgsiblingfriendenterbtn.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1734 | `script/mxgame/sibling/model/mdsiblinglasttime.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2138 | `script/mxgame/sibling/siblingdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2407 | `script/mxgame/sibling/model/mdsiblingchat.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2522 | `script/mxgame/sibling/delegate/dgtsiblinghome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2562 | `script/mxgame/sibling/delegate/dgtsiblingbtn.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2685 | `script/mxgame/sibling/model/mdsiblinghome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2780 | `script/mxgame/sibling/view/dlgsiblingname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3006 | `script/mxgame/sibling/model/mdsiblingallplayer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3133 | `script/mxgame/sibling/model/mdsiblinginvite.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3170 | `script/mxgame/sibling/delegate/dgtsiblingtime.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3309 | `script/mxgame/sibling/view/dlgsiblingvote.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3318 | `script/mxgame/sibling/delegate/dgtsiblingsort.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3645 | `script/mxgame/sibling/siblingctrl.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CShowSiblingHomeDlg, S2CShowHistoryDlg, S2CRefreshAllVoteInfo, S2CRefreshVoteDetial, S2CSiblingAlbumID, S2CSiblingAlbumData |
| 3655 | `script/mxgame/sibling/model/mdsiblingchangefirstname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3666 | `script/mxgame/sibling/delegate/dgtsiblingname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3902 | `script/data/siblingdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3965 | `script/mxgame/sibling/view/dlgsiblingchatcomponent.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3968 | `script/mxgame/sibling/view/dlgsiblingsored.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4132 | `script/mxgame/sibling/model/mdsiblingvote.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4190 | `script/mxgame/sibling/siblingtest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4397 | `script/mxgame/sibling/netsibling.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SOpenSiblingHomeDlg, C2SLookHistoryDlg, C2SLookVote, C2SVote, C2SAcceptNewVote, C2SKickOldVote |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
