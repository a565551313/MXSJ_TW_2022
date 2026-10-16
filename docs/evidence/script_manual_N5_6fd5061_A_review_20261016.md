# N5二轮复核：原三项闭合，另有一处指南待收窄（2026-10-16）

- 固定输入：PR44 `6fd5061dded82bbbcfc96694a5c20ef1a7a3e41e`，父提交核实为上轮审查的`e2fb1aa1fd9019a84df391c13d68e3ec3d9179b6`。用户说“开了pr”，实际是**原PR44快进更新**，不是另一个PR。
- A开工前de60052已推送、工作区干净，先push确认up-to-date。只在仓库外取快照/核对，没有切换领域分支、合PR或改正文/原包/工具/正式review。

## 1. 原三项P2本轮全部闭合

| 发现 | 二轮实查结果 |
|---|---|
| B-N5-01 两条entry_id写错 | 直接读原包目录四条ID，与新回执/摘录和本轮重新恢复一致；697=`0x206d634b`、1406=`0x458cd0df`、1612=`0x50646bdf`、8=`0x005d26b3`。三份变化证据的sources SHA与四份provenance行号同步，四新JSON SHA与N5_RESPONSE所列相符 |
| B-N5-02 Release可重入安全保证 | 已撤；摘要/真与假两分支/局限明确先调用下游，正常返回后才清引用，不保证同步重入或异常安全 |
| B-N5-03 Timer单位/帧率/重复保证 | 摘要/资源/关系/指南/局限已同步标未知；不把0.033/-1直接当30fps/无限重复，未扩取timer正文或修改候选 |

这三项不再列为未修，不要求N5重做。新增四条分支有对应候选，当前battle合计**267函数记录/67分支**；war仍42条名称底稿，不计全体已解释。

## 2. B-N5-04 / P2：二轮修改的指南仍须限定非终止回调

位置：`script_manual/annotations/battle/war.json:3770`，`modification_guides[1].answer`。

指南先列`End`为分派入口，又要求回调最终回到`NextCmd`或`SetProcess(Wait,...)`，不回到则队列不再前进。这仍把“继续消费队列的回调”建议应用到所有回调。**同一候选中的war.End是具体反例**：

- 本轮重新恢复并精确去六行头后，`End`在L1900–1974；录像分支L1909调`main.CloseGame()`并return，普通分支L1927调`main.SetMainLoop()`后收尾。
- 整个函数没有`NextCmd()`或`SetProcess(Wait,...)`；结束/退出战斗或切主循环不是漏推进队列。
- 仅补一句“推断而非实测”不能排除静态反例，且该Claim字段仍为static_reviewed。
- 新增Process/Wait断言的问答证据目前只有表现入口与w_nextcmd，未挂已有w_process/w_wait。相应原候选Process L227–250、Wait L251–263；无需再恢复其他模块。

**最小修法**：建议只针对仍须继续消费队列的**非终止回调**，明确End/关闭/退出战斗/切主循环等终止路径例外；给新增事实挂w_process/w_wait，建议和未穷尽结论标清推测。只需修改该指南并同步响应和war新SHA，其他三JSON不必重排，也不要改候选实现来满足指南。

双句号、冗长提示或PR描述仍展示旧统计属于非阻塞整理事项，不为这些要求返工。此项收窄后再交N7独立末审，不因原三项闭合就宣称四篇全部通过。

## 3. A本轮实际执行

- 重新白名单恢复697/1406/1612/8：3份source形状候选，1406仍decompile_fail/source_partial+digest，不是四份完整源。四条去六头正文SHA与回执一致，无1288定点恢复，未运行/导入候选。
- 三份小摘录**2000+38+170=2208条L行逐行相同**；只改身份头和provenance说明，没有手修候选代码。
- PR44独立快照的schema/来源原字节SHA/行号/full通过，无警告；标准82项**71通过+11缺PySide6跳过/0失败**。ruff含spec通过；Windows静态walk133路径/27源，ERROR/WARNING/INFO全0。
- 叠加到上轮仓库外组合层，来源/full通过，仍为12accepted/4login stale/4battle pending；九份N3/N4/N6新N7模板不受影响。**这不是正式A状态**。
- 此轮未另做HTML/jsdom/真实浏览器/Qt/Windows/EXE/游戏/原生/实服验收，不借用上轮结果冒充新执行。

## 4. 后续与提交边界

已发布[PR44二轮评论](https://github.com/a565551313/MXSJ_TW_2022/pull/44#issuecomment-6206634114)，并[同步新N7](https://github.com/a565551313/MXSJ_TW_2022/pull/45#issuecomment-6206634333)：原三项闭合，新一处指南小修后按最新head/四JSON原字节审核；N2新稿尾审仍待完成。

本轮未merge、未激活正式review，正式仍5135登记/20说明/3有限通过/1排除、5退修review/12pending。旧首轮报告只作为历史，不回写其固定输入的判断。同名JSON保存四ID、候选反例行段、四新JSON摘要、摘录行数及本轮验证日志指纹。
