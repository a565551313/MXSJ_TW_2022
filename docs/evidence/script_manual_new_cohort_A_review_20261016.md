# 全新N1–N7交付：A固定PR复核（2026-10-16）

## 结论先行

七个**新会话**均已提交新PR39–45，不是旧B–H续工。**提交齐了不等于全部验收完成。**

- N1、N3、N4、N6：可作为本轮**有限集成候选**。N3/N4/N6九份新JSON都有新N7独立accepted模板且原字节SHA完全相符；A不自批自己原先代写的G。
- N2：原五组返修经A重点复核有实质进展；新N7尚未审完此head的新Claim/关系/保真链，不把基线退修当新稿审核。
- N5：三篇名称底稿确已补写、原五组主要返修方向成立，但新增**3项P2待修**。不是全盘否定其补写，也不能直接接纳。
- N7：有效的**部分审核交付**，需补N2新稿及N5修后head的尾审，更新旧“battle无PR”行动状态。

本轮仅审查/评论/维护A协调文档。**未merge任何新PR、未正式激活新review、未合master、未上传、未改游戏/编辑器/启动器/原包。** 正式内容仍是`9b0dea7`的5135/20/3/1，5退修review、12pending；不能把外置模拟的12通过写成A已12通过。

## 1. 环境重建与基线保护

用户指出分派前已提交推送，远端实查确为`9b0dea799768aaacbb967ffc59f45753970752be`，不是漏交。新沙箱本地HEAD却回到`8212b26`，同时保留最新工作文件；旧venv/日志/jsdom消失。

逐路径比较215个相关路径：212个Git blob原字节相同，3个bat仅CRLF/LF差异、Git过滤后hash也相等，无缺失或本地独有文件。只对齐当前固定分支指针/索引，保留工作文件字节，工作区恢复干净；未hard reset/clean/stash/覆盖或重复提交。开工前push A返回up-to-date。此次新建环境和日志，不冒充旧沙箱仍在或旧测试已重跑。

固定分析包和参数指纹未变；运行恢复工具SHA仍`152dbc28…`，batch仍`a7474223…`。Python3.11.2 / uncompyle6 3.9.3 / xdis6.1.8 / spark-parser1.9.0 / click8.5.0，手册jsonschema4.25.1 / ruff0.17.1；依赖和完整候选均留仓库外。

## 2. 七PR固定输入与实际判断

所有PR inspection时均OPEN、base为A、文件范围符合各卡，未切换任何领域分支。正式底座`9b0dea7`；各自快照与按PR文件叠加的组合层均在仓库外。

| 新会话 | PR及固定head | A本轮判断 | 后续 |
|---|---|---|---|
| N1 | [43](https://github.com/a565551313/MXSJ_TW_2022/pull/43) `f953eb992bf3c5d072ae478a0ac67e4d651e5064` | 目录修复独立复现；认可额外186条保守null策略 | 有限集成候选，非全目录语义通过 |
| N2 | [39](https://github.com/a565551313/MXSJ_TW_2022/pull/39) `c7142366fabafea0b35d943d8746a1de9d899b49` | 五组修复重点核对成立，来源保真链已重建 | N7补新字节逐Claim/关系/来源尾审 |
| N3 | [41](https://github.com/a565551313/MXSJ_TW_2022/pull/41) `77b64beda4b3b31455445ae48dfc124d614ce931` | D1已修、三已过JSON与共用来源未动；N7模板SHA匹配 | 有限集成候选 |
| N4 | [40](https://github.com/a565551313/MXSJ_TW_2022/pull/40) `44230b98527f72948acf16295e83f0151a26eb27` | 十项问题按候选复核，四模板SHA匹配 | 有限集成候选，时间/网络运行未知保留 |
| N5 | [44](https://github.com/a565551313/MXSJ_TW_2022/pull/44) `e2fb1aa1fd9019a84df391c13d68e3ec3d9179b6` | 有实质补写，3项P2仍需修 | 同一新N5 PR返修，再交N7 |
| N6 | [42](https://github.com/a565551313/MXSJ_TW_2022/pull/42) `23b60f96c602fe605912c3d323af743a4d54c22a` | 980行复现、四模板SHA匹配；接纳依据为新N7，不是A自批 | 有限集成候选 |
| N7 | [45](https://github.com/a565551313/MXSJ_TW_2022/pull/45) `db872c5cd6aad0349e62d17af2959576aa3fec12` | 九份模板与新正文匹配，三UI有限维持，login基线退修有效 | 部分交付，补N2/N5尾审/当前报告 |

七PR已分别发布A评论，精确URL见同名JSON。作者/审核实际身份保留，A只是本轮协调复核，不伪称H或改写N7的审核结论。

## 3. N5三项P2（已评论，不代写正文）

### B-N5-01 两条来源头entry_id写错

`war_697_excerpt.txt:7`及`n5_provenance_20261016.txt:21`写`0x2069990b`，原包目录/独立恢复实际是**0x206d634b**。`e_warctrl_8_excerpt.txt:7`及provenance第36行写`0x5d2ab3`，实际是**0x005d26b3**。

包SHA、entry_index、stored/pyc/正文摘要都匹配正确条目，未发现错解了别的条目；错误在来源回执的ID。应从原包目录机械取值，改四处并核全部四条ID，更新所有引用变化摘录的sources SHA，再跑来源闸门，不能只改正文数字不更新摘要。

### B-N5-02 Release的“可重入安全”无证据

`e_warctrl.json:975`，`CPlayCtrl.Release`：独立候选去头L159–163先调`self.m_WarCmdMgr.Release(self)`，正常返回后才把引用置None。同步重入仍能看到非空引用，调用抛异常也到不了清空语句。因此不能由这段证明“可重入安全”；最多说正常返回后再次顺序调用会跳过。收缩断言，不把候选修好后当原文。

### B-N5-03 Timer参数不能直接保证30fps和无限重复

`e_warctrl.json:495`只引调用者`timer.Timer(0.033,self.OnUpdate,-1,self)`，未提供Timer实现/计时单位/重复参数语义，却写“约30fps、-1无限循环”。应补有效被调来源，或只保留参数字面值并把周期/重复语义标未知/推测；不等于实测帧率。

完整退修评论：[PR44](https://github.com/a565551313/MXSJ_TW_2022/pull/44#issuecomment-6206333803)。N5剩42条名称底稿诚实列出，按本卡重点入口有限说明不要求扩写全部；1406仍u6失败，pycdc动画真实守卫仍未知。

## 4. 独立复现与逐行来源核对

A新环境17条白名单：337/4293/4007/4806、219、3176/2170/871/516、3038/717/1129/949、697/1406/1612/8。16条source形状候选，1406仍decompile_fail/source_partial+digest。`recovered`计数17不等于17完整源码。不执行/导入恢复稿，无1288定点读取/恢复。

| 核对 | A本轮结果 |
|---|---|
| N2四条来源链 | 原包stored→pyc→raw u6(False)→严格cp950→候选去六头正文，stored/pyc/raw/body SHA和目录ID/offset/长度4/4一致 |
| N2 main摘录 | 17段/975行与本轮候选逐字相同，无损main替代旧稿的来源链成立 |
| N3专用摘录 | 59条L行逐行相同 |
| N4新网络摘录 | 302条R行逐行相同 |
| N6四摘录 | 205+225+224+326=980条L行逐行相同 |
| N5三候选摘录 | 2000+38+170=2208条L行逐行相同；四条stored/pyc/body SHA匹配，但两条header ID有误 |
| N1真20种子→5135 | A本轮一棵新的隔离树sample/full均过，三产物逐字节等于PR43；不是把N1/N7的“两棵树”说成A已跑两棵 |
| N1独立元数据测试 | 32项全过、0跳过；首次仅快照运行因缺BDF收据跳1，补同版收据后实际重跑32全过 |

A明确认可186条非标识符形参保守置null：保留全部函数/限定名/kind及原渲染、原字节审计，不猜形参，不静默丢128382记录。48内部槽+186不可靠参数及70kwargs修复不表示所有签名/函数语义已验证。N1/N7反证树构成不同，不是相互矛盾。

## 5. N7原字节绑定与模拟集成结果

PR45 `.json`有效记录针对**旧基线**；九份`.json.template`针对新N3/N4/N6。A逐个核模板SHA与对应新PR JSON一致，才在**仓库外**覆盖canonical记录。只选择九个具名`8b6e9266_<entry>.json.template`，不激活`example.json.template`。初次宽glob误遇example被断言拦下，修为具名白名单；未触碰正式review目录。

- 仅七PR内容叠加、尚未激活模板：3accepted/13stale/4pending。
- 外置精确激活九模板后：**12accepted/4login stale/4battle pending**；来源/full无硬错误，四login stale是缺新审核，不是结构工具失效。
- 正式A仍：**3accepted/5changes_requested/12pending**。不在未授权合入正文前激活模板，不复制N7基线退修作为新稿通过。
- A原G作者身份不变；N6是接管作者，新N7是非作者审核人。A只复现/核SHA，不自批G。

N7旧报告“battle无PR/N5未交”保留为当时快照，当前PR44已在且有三项返修，行动状态须补到最新。N2不能用基线L01–L13退修替代新head审核。补审要求：[PR45评论](https://github.com/a565551313/MXSJ_TW_2022/pull/45#issuecomment-6206334018)。

## 6. 本轮实际闸门与未做范围

- 七份固定快照和组合层schema/来源原字节/行号/full均过；stale按上表如实显示，未关闭警告迎合计数。
- 模拟组合标准unittest **82=71通过+11因本次新环境未装PySide6跳过/0失败**。不是引用旧libGL环境原因，更不是82全通过。
- N1另跑32全过，**不在标准82 discovery范围内**。待PR43实际集成后，A须把该入口加入标准验证说明/自动化；本轮不引入会引用未合代码的A测试。
- ruff0.17.1含spec通过；Windows静态walk166路径/29源码、ERROR/WARNING/INFO全0，非Windows运行。
- 模拟组合单HTML构建通过，jsdom26.1.0实际执行脚本：4中文搜索、CreateCmdObject函数搜索、3审核筛选、3路径/identity hash导航、20篇×4页=80次tab呈现、hero→npc按钮跳转、N6作者/H审核展示；0 jsdom错误。
- jsdom只是DOM脚本执行，未做真实浏览器/CSP实测、Qt、Windows/EXE、游戏/原生/实服。HTML/依赖/完整候选/大日志留仓库外，不上传。

## 7. A工具跟进与下一步

1. CONTRACT补明行号指`sources.path`文件自身物理行，L/R标签另指候选原行，避免改已审摘录/JSON让九模板stale。
2. `recover_entries.py` False先repr再`!r`导致子进程收到真值字符串，已由代码核实。N2用直接工具API真实bool False绕过，raw链4/4成立，默认True恢复不受此项影响。另排A工具修复及纯参数传递回归，本轮不静默改冻结工具指纹。
3. N5在同一**新N5 PR44**修三P2发新head；新N7继续同一PR45补N2新字节和N5修后独立审核，不再重启旧H。
4. 获授权且满足对应门槛后，A再merge到固定集成分支、精确核SHA激活审核并重跑集成闸门；这份复核本身不是merge授权。

同名JSON含七固定head、逐PR变更路径/评论URL、原字节绑定、复现/测试/DOM指纹、215路径Git恢复比较、三P2及工具跟进。历史报告不重写为当前结果。
