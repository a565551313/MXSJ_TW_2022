# G停工后A代写首批四篇（2026-10-16）

用户报告“G也罢工了”，A承接G固定四篇，实际作者明确为A。不是G独立提交，也不是A代审通过；**本轮不为自己的四篇创建accepted记录**。只补角色/物品/任务/NPC领域，不接管C–F的返修，不合并其他PR。

## 本轮落地

| entry | 路径 | 已列函数 / 分支 | 状态 |
|---:|---|---:|---|
| 3038 | `script/hero.py` | 13 / 12 | A代写，待其他实际审核者复核 |
| 717 | `script/mxgame/item/view/dlgitem.py` | 13 / 19 | 同上 |
| 1129 | `script/mxgame/task/model/task.py` | 13 / 14 | 同上 |
| 949 | `script/char/npc.py` | 12 / 17 | 同上 |

合计4篇、**51个重点函数、62个关键分支**，每篇含职责、资源/上下游、3个修改问答、来源和未覆盖风险。不是全模块函数穷尽；列表以外不补假解释。正式加载由20种子/1说明变为 **20种子/5说明/0审核通过**；其他D/E三份有限通过仍是未合正文的外置待激活记录，本轮未偷偷激活。

JSON：`script_manual/annotations/gameplay/{hero,dlgitem,task,npc}.json`。owner=G保留任务包身份，author填真实A代写，不修改为G会话作者。schema版本与工具版本不变（dev3），没有为接管而放宽证据、来源或审核闸门。

## 来源与可复现范围

- 开工前同一固定A分支已推送且干净，起点`69ca61f3830f23e8710427c4113adc5e01e77c11`。
- 固定script.fls SHA `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`；参数表 SHA `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`，均未修改。
- Python3.11.2 / uncompyle6 3.9.3 / xdis6.1.8 / spark-parser1.9.0 / click8.5.0。恢复器和batch工具摘要、各stored/pyc/完整候选及去头正文SHA详机器收据。
- 仓库外两次运行：`tools/decompiler/recover_entries.py --out <新的仓库外目录> --entries 3038,717,1129,949 --decompile-timeout 30 --report <仓库外JSON>`。两轮均4/4 baseline、decompile_ok/source；**精确去六行恢复头的正文4/4逐字节一致**。生成时间头可变，不能拿整文件SHA作跨次稳定摘要。
- 四份候选分别2927/3215/1107/1235行，只表示有完整输出外形。非原始源码，不证明语法、可回编、语义、原生或运行期正确。
- Git只收四份小摘录与JSON，**951行摘录逐行JSON解码后与固定候选原行精确相等**；每段保留原候选行号及来源全文/正文SHA。摘录不是完整候选源码；原候选、pyc、重跑目录、生成站点和npm依赖不入Git。

## 已明确保留的关键疑点与开发入口

- **hero**：属性应用只解释CreateProp遍历Unpack/Default与回调，属性表只摘表头，未核完整字段顺序。PropInitFinish仅检查属性存在；GetHeroShow是多状态OR加庭院秋千例外，不能简化成角色可见。跨服GetRealID保留`g_ID/10`字面及实际类型未知；角色配置假值也会回落mx.ini。坐标转换不是服务器坐标回包证明。
- **dlgitem**：构造器传`item_new.dlg`，GetDlgPath返回`item1.dlg`，未核基类何时读取后者，不能盲改一张。Show只作用已有窗；ShowDlg(False)也可能先构造/登记回调；装饰器调度未核。4号网络整理与15号本地排序窗不同，Shift复制、右键使用、手持对象/召唤兽分流分别解释，不把UI号当协议号。
- **task**：RefreshNecessary的二选一结果分支却从petTaskList拆值；TaskSatisfy/TaskUnSatisfy出现`dict([_[1] for k in tasklist])`不对应变量形态。只登记声明代码和待核异常，不擅自修成正常任务满足流程。IsSatisfyTask在缺少未满足描述时也可True；ClearTask不是清理所有全局表；禁止寻路函数只提示/返回，不直接停止寻路。
- **npc**：普通NPC与客户端任务NPC的LeftUp不同；先后门禁、自定义回调消费、重叠选择、远处只WalkTo、任务ID分NpcLook/NpcTask分别说明。发送调用不等于服务端对话成功。CreateNpc的连续if可能覆盖此前类选择，动态构造签名未统一核对；任务标记编码与对话正文/布局/URL严格分开。
- 完整角色生命周期、装备/物品各种使用、宠物/装备任务匹配管理器、NPC特例/资源实际存在、原生调度/编码/焦点、服务端和真实运行均未验。所有runtime_verified与本轮审核通过数为0。

## 实际验证

- 正式5说明：schema、任务归属、路径、来源摘要和行号验证通过。**仍只有20种子，不运行或冒称full inventory闸门通过**。
- unittest共82项：71通过、11 Qt因缺libGL.so.1跳过、0失败；固定夹具不随生产说明数量改变。
- ruff含spec通过；Windows静态检查全0，精确计数见收据。
- 仓库外单HTML构建通过；jsdom26.1.0执行页面脚本，四个中文关键词各命中对应G模块，作者为A且无审核记录、界面显示待审核；总说明5/通过0。jsdom不是实际浏览器或Qt。
- 未执行/导入恢复的游戏模块，未改原包/参数/编辑器/启动器，未读取布局/图片payload、未请求业务URL、未实机/Windows/EXE/原生/服务端测试。恢复器整包读取用于既有输入和指纹，但只定点处理四个白名单条目；1288未定点恢复。
- 机器收据：`docs/evidence/script_manual_G_A_draft_validation_20261016.json`。下一步由非作者复核这四篇有限稿；不借H宕机把A作者静态核对升级成独立审核。
