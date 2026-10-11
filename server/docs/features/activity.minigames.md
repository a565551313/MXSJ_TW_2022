# 小游戏公共框架与活动内小游戏

工作包：`activity.minigames`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

只能上报操作，不接受任意客户端分数作权威结果。

## 接口设计起点

`start_minigame / submit_minigame_action / finish_minigame`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 27 | `script/mxgame/minigame/shootgame/shootgamemgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 68 | `script/mxgame/minigame/paintandguess/model/paintandguessutil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 210 | `script/mxgame/minigame/fixpig/dlgfixpig.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 710 | `script/mxgame/minigame/paintandguess/netpaintandguess.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SApplyJoin, C2SChooseTheme, C2SSyncDrawboard, C2SQuitGame, C2SStartPaint, S2COpenChooseDlg |
| 1283 | `script/mxgame/minigame/shootgame/dgtshootgame.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1557 | `script/mxgame/minigame/paintandguess/paintandguessdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2191 | `script/mxgame/minigame/trackgame/trackgame.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2971 | `script/netliving.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CProduce, S2CCropGrow, S2CCropReap, S2CMinerals, S2CTrees, S2CPlantTree |
| 3004 | `script/mxgame/minigametwo/netminigametwo.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGameCmd |
| 3096 | `script/mxgame/minigame/shootgame/dlgshootgame.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3144 | `script/mxgame/minigametwo/minigame101.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSGameCmd |
| 3518 | `script/mxgame/minigame/paintandguess/dlgpaintandguess_choosetheme.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3631 | `script/mxgame/minigame/paintandguess/model/paintandguessmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3793 | `script/mxgame/minigame/paintandguess/dlgpaintandguessnew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4478 | `script/mxgame/minigame/sneakgame/sneakgame.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4601 | `script/data/minigamesdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4719 | `script/mxgame/minigame/fixpig/dgtfixpig.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
