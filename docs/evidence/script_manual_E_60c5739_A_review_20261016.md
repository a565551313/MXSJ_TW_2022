# E network 第二轮 A 预审（2026-10-16）

## 结论与边界

固定审查 [PR #36](https://github.com/a565551313/MXSJ_TW_2022/pull/36) 的 `60c573956f12a739712e4b24ddf1fb852f71bff0`，相对首轮 `ec97941` 仅修改 network 六文件。A 工具底座固定 `94e6d33c703dbf985de6b37468962f95fbae4818`（工具仍为 e49cb00 的 0.1.0.dev2，新增的只是前轮审查文档）。

**上一轮五项问题已闭环，可进入 H 待审队列。不是 H accepted，不是全体函数语义验收，未合入 A。** 按既定顺序，20 篇样板及 B 输入齐备后 H 独审；本轮只准备固定字节交接单，未启动/联系 H 独立会话。

## 五项修订闭环

| 问题 | A 本轮独立核对 | 结果 |
|---|---|---|
| OnError 隐藏条件及正在瞬连守卫 | 新恢复 net R856–873；对照 net.json 函数摘要/分支、报告 §2.4 | 仅 `not IsQuickConnect() and not CanQuickConnect()` 才先 HideWindow；正在瞬连不重复发起 Connect/ShowError，已同步 |
| 选服后面板行为 | 新恢复 netserver R189–201；对照函数、关系、报告及给 C 的协审意见 | 非转服分支为 OnLogin 后 Show(False)，明确隐藏；不推定隐藏后的界面去向 |
| DoConnect 成功链矛盾 | 新恢复 connect R144–198；对照 purpose、函数/分支、关系、报告和 main 协审 | 三处 ConnectAttempt 都传 Fail；Success 仍为未引用的候选声明，已不再把 RestarConfirm 宣称为确认成功链；与 KuaFuConnect 的另一条已注册链分开 |
| 动态恢复头导致整 SHA 不可复现 | 独立锁环境恢复 3176/2170/871/516/4293；核对固定头/keys/bounds 与输入，再精确去前六行 | 五条正文 SHA 5/5 与 E 修订表、上一轮 A 独立结果一致；871/516 正文与仓库既有候选原字节一致；整文件 SHA 仅为各次历史标识 |
| 计时单位口径 | 全文检索四 JSON、证据报告及 main 协审；对照原始调用参数 | 0.016/15/10 等不再冒称已确认秒数；24 仅登记调用帧预算；1200 区分为 misc.Time 时间戳差值，不与 CreatePyCommand 单位混同 |

恢复环境：Python 3.11.2 / uncompyle6 3.9.3 / xdis 6.1.8 / spark-parser 1.9.0 / click 8.5.0。原包、参数表、两个恢复工具 SHA 均与冻结输入一致。未执行恢复模块，未定点提取/解码/恢复 1288，未请求公告/服务端 URL。

## 验证与覆盖

- E 说明四份：157 函数、43 分支（52/24/29/52 函数，23/7/6/7 分支）。数量不等于讲解准确率或全域覆盖。
- A+E 隔离覆盖：严格 validate（结构、来源 SHA、行号）20 种子/5 说明/H0，通过；唯一警告是 3970 号表关联未编入历史种子，留给 B 完整目录。
- A+C242fd8c+E60c5739 草稿覆盖：严格 validate 20/8/H0，通过；**C 内容仍退修，结构通过不撤销其阻塞。**
- A、A+E、A+C+E 三组各 78 项：**67 通过、11 GUI 跳过、0 失败/错误**。本轮已安装 PySide6 6.10.3，但系统缺 libGL.so.1，真实 Qt 未执行；不沿用历史三组零跳过结论。
- E 隔离覆盖 ruff 含 spec 通过；Windows 静态 69 文件名/26 脚本，ERROR/WARNING/INFO=0/0/0。
- E 与 C+E 两组离线 HTML 构建成功；本轮未做浏览器运行验收，HTML 构建不等于浏览器或游戏运行通过。
- Windows/EXE、原生帧长、实机、真实服务端行为未验；H 尚未独审 157 个函数的全部解释。

完整机器收据：`docs/evidence/script_manual_E_60c5739_A_validation_20261016.json`，包含输入/工具/全部 A 底座文件 SHA、E 六文件 SHA、四份 JSON 原字节 SHA、五条稳定恢复头及正文摘要、测试日志摘要和离线 HTML 摘要。

## H 固定输入与操作边界

交接单：`script_manual/coordination/H_QUEUE_E_60c5739.json`。此文件由 A 准备，不是 review，不计 accepted。四份说明逐字节绑定；E 若再修改正文，须更新待审输入，不能沿用旧 SHA。

1. 保持 H 自己的固定分支，不 checkout/cherry-pick E 或 A 到另一分支。用 `git archive` 在仓库外提取上面的 A 底座 `script_manual/`，再覆盖 E 固定提交的 `script_manual/annotations/network/` 六文件。
2. 对覆盖目录中每个 annotation.sources，建立外部 `evidence_repository/<source.path>`：覆盖快照已有文件取其原字节，否则取原仓库同路径；不重排、转换编码或宽松换行归一化。
3. 在该覆盖目录运行 `PYTHONPATH=<外置目录>/script_manual/src python -m mxsj_manual --content <外置目录>/script_manual validate --verify-evidence --repository <外置目录>/evidence_repository`。不要在尚无 E 正文的正式 A 数据上用空引用绕过验证。
4. 按 E 报告锁定环境独立恢复，核对稳定头第 1–4、6 行（第 4 行 keys/bounds 实际对照固定参数表；E 报告没有逐条列这两数组，A 收据已补列供核对）。仅允许第 5 行生成时间不同；正文仅删除准确六行，不忽略其余字节。A 结果不能代替 H 独立复现。
5. H 仅向自己的 `reviews/` 提交四份审核 JSON，以本交接单列出的实际 annotation SHA 绑定，独立给 accepted/changes_requested；验证时将 H 的 reviews 叠入外部 E 快照。A 后续联审 E+H，未合 E 前单独对正式 A 校验 H 引用会缺正文，不能改 schema 绕过。

## 仍未裁决

- Python 候选的帧续读 2/3 字节冲突：不据此裁定原生状态机。
- 队列低优先赋值、DoConnect.Success 未引用、StartQuickTimer 条件异常：继续登记待原生/码对象/实机核对，不预判为 bug 或正常。
- main 协审中的 serverid、状态槽位及其他模块缺失：C 唯一负责 main 最终表述，E 不重复建档。
- B 完整目录、D/F/G 的十二篇样板及 C 返修尚未收到可接纳交付；截至本轮查询只见 C/E 两个开放手册 PR，不能断言其他会话尚未开工。

正式生产数据仍为 20 历史种子/1 样板/H0。协调表仅把 C 标 blocked、E 标 submitted，其余保持 assigned，不假造已开工状态。
