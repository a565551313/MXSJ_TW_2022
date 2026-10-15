# Agent任务卡（协议v1）

所有Agent先读 `CONTRACT.md`、根 `AGENTS.md` 和根 `docs/STATUS.md`。输入/归属只认 `coordination/baseline.json` 与 `tasks.json`，不追浮动master。先提交推送自己现有工作再开工；不切换各自Arena固定分支，不擅自合master或上传游戏包/改权限。

这是任务分配，不表示这些Agent已经开工或完成；A不能从本会话启动/验证其他独立会话。

> **2026-10-16 授权变更**：用户“H宕机了你审吧”，A以 `A_delegate` 代审已交D/E，不再等20篇齐备。实际身份/授权/字节绑定、有限范围和激活规则见CONTRACT§4.1及根STATUS§3.46；不是启动独立H会话或领域合并授权。旧H后置安排只作历史。

## A — 总控与工具

独占schema、coordination、src、生成器、工具文档、集成和根STATUS。维护版本/唯一归属，给其他Agent先提供固定提交的 `script_manual/` 底座；不让所有人共改总索引和导航。不包办B全量重建或C–G领域分析。先接20个样板并逐批审核已提交部分（H或用户授权A代审），再扩域、串链、集中验收；不以20篇未齐阻挡已有提交的审核。

## B — 全量目录提取

只改 `inventory/`。目标是两固定包全部登记条目的inventory，不是全量函数解释。只读已有语料或安全结构化解析，不执行游戏脚本、不恢复1288。登记co_filename路径、类/函数签名及提取失败；区分“原生结构读取/历史线索/不可读/目录/政策排除”。对接PR34时提交实际语料manifest与所有工具SHA/版本，不拿旧catalog函数名充新提取结果。

交付 `inventory/modules.jsonl`（替换20条样板，仍保留同身份）、`inventory/B_extraction_receipt.json`、必要抽样报告。保持全条目且每身份一行，无法提取的明确标缺失；不要让“缺函数”和“无函数”混为一谈。先做20条回归给A确认，再扩到全部。用 `validate --require-full-inventory` 检查登记覆盖；不要宣称函数讲解已全量。

## C–G — 领域说明

每人先完成下表4个样板，放自己领域目录；每模块解释职责、重点类函数、消息分支、上下游线索、资源/配置/布局、修改入口和风险。依据不够就保留推测/缺失，不凑已核对。完整源码过大时先提供带SHA的小审阅报告作为证据，不搬大语料进Git。task状态变化报A，别直接改总任务表。

### C — 启动与登录

只改 `annotations/login/`。

| entry | 路径 |
|---|---|
| 337 | `script/login/mainpage.py` |
| 4293 | `script/main.py` |
| 4007 | `script/login/register.py` |
| 4806 | `script/login/loginin.py` |

先复核并接管 `login/mainpage.json` 的A格式样板，不再新增同337的第二份文件；本版所有说明仍是推测/待H审。main.py归C主责，E/F协审网络和战斗切换；C负责最终统一文字。

### D — 界面、输入与聊天

只改 `annotations/ui_chat/`。

| entry | 路径 |
|---|---|
| 219 | `script/mainmenu.py` |
| 3854 | `script/interface.py` |
| 3232 | `script/key.py` |
| 4832 | `script/chatoutput.py` |

### E — 网络、连接和协议

只改 `annotations/network/`。

| entry | 路径 |
|---|---|
| 3176 | `script/net.py` |
| 2170 | `script/connect.py` |
| 871 | `script/netquicklogin.py` |
| 516 | `script/login/netserver.py` |

协议号、帧处理、错误路径要分别找真实证据；不要把发送符号等同服务端行为。与C协审main.py但不重复建档。

### F — 战斗调度与表现

只改 `annotations/battle/`。

| entry | 路径 |
|---|---|
| 697 | `script/core/war.py` |
| 1406 | `script/netwar.py` |
| 1612 | `script/core/magicperform/warcmd.py` |
| 8 | `script/pubscript/pubskill/e_warctrl.py` |

区分core战斗流程与表现命令；与C协审main.py，不能仅凭函数名推定真实战斗计算。

### G — 角色、物品、任务与NPC

> 2026-10-16 用户报告G停工，A承接下列四篇的有限说明。owner=G仅保留任务包归属，author必须明确A代写；这不是G独立提交。A不对自己代写稿创建A_delegate accepted，须另一个实际审核者复核。其他C–F返修仍由原owner承担。

只改 `annotations/gameplay/`。

| entry | 路径 |
|---|---|
| 3038 | `script/hero.py` |
| 717 | `script/mxgame/item/view/dlgitem.py` |
| 1129 | `script/mxgame/task/model/task.py` |
| 949 | `script/char/npc.py` |

## H — 独立审核

只改 `reviews/`。先按契约校验每份JSON，再核对来源版本、摘要、行范围、关键解释、缺失/推测/实机状态；重点反证“完整恢复=正确”“函数缺失=无函数”。对模块原字节SHA提交独立accepted/changes_requested，不改owner正文自批。整合前必须让A实际核对审核提交者和范围，格式字段reviewer=H不等于认证。

验收至少覆盖：公告刷新失败出处；正文/地址/布局分别改哪；登录点击链；注册逻辑与布局；main主循环；快捷键入口。记录哪些有证据、哪些仅候选解释、哪些必须实机补证。B的全量登记统计与C–G的函数解释覆盖分开验收。不要用A的1份历史稿样板充20份已审核。

## 每人提交前

```bash
PYTHONPATH=script_manual/src python -m mxsj_manual validate --verify-evidence --repository .
```

在各自固定分支提交并推送，只交自己目录和一段范围明确的说明：模块数、函数/分支数、来源SHA、推测/缺失、未实机项、冲突。A按主键去重集成后统一生成站点；禁止自行改总导航、schema、归属、根STATUS或覆盖别人的目录。
