# B / D / F 首轮 A 集成预审（2026-10-16）

## 结论

| 工作包 | 固定提交 | A预审结论 |
|---|---|---|
| B 全量目录 | e516b63499615af7892ece0a217bd36c35894032 | 全量结构可复现，但签名生成有实际错误，需修改后重交 |
| D UI/聊天 | 1f6fdd323475e3940ea95b19e62c452e58dbd259 | 有限样板可进入H待审队列，83函数/75分支；不是H accepted |
| F 战斗 | 12ce0c63ab50db00050365de5a6891fd4fa37ce6 | 关键解释/证据及三篇仅名称底稿需补，暂退修 |

A底座固定 `3fbbea1`（0.1.0.dev2）。三包分别只改 inventory/、annotations/ui_chat/、annotations/battle/，未发现越域改动。截至核查三包只有固定分支提交，尚无PR；owner须各自在自己的固定分支开PR，base为 `arena/61deb9e5-mxsj-tw-2022`。A不替owner切分支或从其他会话分支创建PR。

本次仅外部覆盖验证，没有把B/D/F或既有C/E正文合入A。H仍按20篇样板齐备后独审，不由A代写accepted。正式数据仍20历史种子/1样板/H0。

完整机器收据：`docs/evidence/script_manual_BDF_A_validation_20261016.json`，含所有提交文件SHA、原包/工具指纹、复现结果、签名受影响清单、D四份待审原字节SHA、F探针及集成回归收据。

## B：全量结构认可，但签名需修

### 独立复现结果

- 在仓库外复制匹配指纹的工具及输入；13个复用模块和提取器自身SHA与B回执逐项核对。
- 用A冻结的20条种子重新开始，删除B已有回归报告，独立跑 `--sample` 再 `--full`；不是拿B自己覆盖后的目录当种子。
- 5135行输出与提交**逐字节相同**：SHA256 `35203710d79acd08b080e9d08fa1357ea9f8c29464a64eeb1a34aa27e36a9efd`，11,995,883字节，128,382个结构函数记录。
- script：4950 structurally_read / 37 historical / 14 unreadable / 1 excluded；data：121 structurally_read / 12 directory。20种子路径全部一致。
- 对 `ArchiveDocument.read_stored` 安装只读检查，先记录请求再断言排除1288。两遍工具执行共20004次script读取请求，覆盖5001个允许条目，没有1288定点读取请求。整包SHA读取仅为指纹，不据此声称逐条语义核验。
- 51条严格解析失败、1668次kind回退、疑似损坏名称等风险仍保留；结构读取不证明业务行为，不把历史回退的空functions当无函数。

### 必修：可确认签名不是任意码对象名字串

1. **70个仅有 `**kwargs` 的签名被错误插入裸 `*`。** 提取器 `signature_of` 的180–181行 `elif flags & 0x08: params.append('*')` 导致 `(self, path, *, **dct)` 等输出。这不是原Python2签名；没有 `CO_VARARGS` 时应直接追加 `**name`，不能添加不存在的参数。例：entry30 `CAccountMgr.GetUrl` / `C2980Mgr.GetUrl`，entry70 simplejson 多个函数。A用人工构造的纯元数据做五种微测试：普通、仅*args、*args+**kwargs通过；仅**kwargs、有/无位置参数两例均复现错误，没有执行游戏函数。
2. **48个签名含 `.0/.1/.3` 等编译器内部参数名。** 例如 entry233 `getmoduleinfo.<lambda>` 为 `(.0)`、`BlockFinder.tokeneater` 为 `(self, type, token, .3, .4, line)`，以及genexpr隐式参数。不能将内部槽名当已确认源码调用签名。无法安全重建原tuple参数形状或公开签名时应设 `signature=null`，不猜补、不删除函数、不拿旧catalog覆盖；原名字可保留在回执供审阅。
3. 重新生成 modules、样板报告及回执，更新摘要和签名统计；在B目录补针对普通/*args/**kwargs/两者/不可靠内部形参的回归，不改A测试。目录数、身份、路径和函数记录不应因修签名被静默删减。

次要回执问题：880/2310/3078/3122四条旧路径含控制字符，降不可读正确；但工具清空fallback后未把原线索写入回执，与“原样保留”的代码注释/交付表述不符。可增加明确的rejected_fallback字段保存JSON转义原值，或说明只能按已钉旧catalog+entry回查，不要把空串说成已保存原线索。

### 旧测试结论纠正

B使用cc5c1ba时报告的9项种子耦合失败，是A dev1旧夹具问题。A已在e49cb00的dev2隔离夹具；本轮全目录覆盖下78项=67通过+11 GUI跳过，0失败。B无需修改A测试，更不能只改期望计数。B签名错误是另一项真实数据问题，不能被测试通过掩盖。

## D：有限样板可入H待审队列

### 来源和关键解释复核

- 严格按D的白名单和锁定Python3.11.2/u6 3.9.3/xdis6.1.8/spark-parser1.9.0恢复12条候选；逐条核对stored payload、pyc、候选全文SHA，全部相同。没有宽松去头、重排或字符替换。
- D五份摘录文件含3142条 `Lnnnnn: JSON字符串` 原行；全部解码后与复现候选对应行逐字相同。
- 抽查：菜单message4→SS_ClickSkill→delegate.OnSkill实际调用makeequipctrl；另一个订阅者处理锻造按钮动画，不把符号名误写成技能面板。
- 抽查：聊天左键base300走显示掩码/索引，右键大偏移走hero接收位与netchat请求；没有把隐藏历史等同服务端拒收。
- 抽查：CClickBox实际构造参数为parent,w,h,color,alpha,msgid；CFunctor的组合键/编辑模式守卫、原生登记边界与文稿一致。未据候选认定原生输入事件的先后顺序。
- 219/3232损坏标识符按recovered_partial保留，业务动态目标/资源/实机限制明确，没有擅自改历史名补洞。

四份原字节SHA与83函数/75分支计数见 `script_manual/coordination/H_QUEUE_D_1f6fdd3.json`。它是A准备的输入队列，不是H审核；完整83函数语义仍由H独审，来源复现/抽查不能替代它。D原来的5模块关联警告在B全目录隔离覆盖中均已解析，无需D越界补索引。

## F：暂退修

1. **三份仅历史名称的底稿现在有可读候选。** A用冻结工具独立探针：
   ```text
   python tools/decompiler/recover_entries.py --out <新外置目录> \
     --entries 697,1406,1612,8 --decompile-timeout 30 --report <外置报告.json>
   ```
   同样使用u6 3.9.3/xdis6.1.8/spark-parser1.9.0/click8.5.0和默认Big5。697、1612、8均stage=baseline、decompile_ok、kind=source，分别2640/45/176行（含六头）；原包/参数未变。1406仍decompile_fail、只有13行的source_partial+digest，不冒称完整源码。请F独立复核前三条，补有限函数/关键分支/资源/修改入口及来源报告；不能只因旧pycdc未落盘就把三份长期停在名称名单，也不能将新decompile_ok直接提升为语义正确。
2. **netwar三处非推测函数引用未覆盖函数体。** ModuleReset(28–36)、ReduceWarTime(158–162)、IsWarEnd(303–306)均只引globals22–26；初始值不能证明重置/递减/判断函数。请引用实际函数体并全文查同类问题。
3. **入场动画分支解读不符当前pycdc文本。** 231–232的条件体是pass，233的SetEnterAniShow在if外。现稿虽标inferred，却未说明该控制流歧义，仍说成“特定类型且非录像时设置”。应按候选写明条件体pass/后续调用位置、真实守卫待核，或用另一份带摘要候选/码对象证据澄清，不能凭意图补条件。
4. **跨模块事实与推测要分开。** “CCmd入队”需core/war构造器证据和过滤守卫；netwar的S2CWarEnd片段没有SetMainLoop，不能凭“结束应恢复”冒充切换落点。A新候选中core/war.CCmd在211–222有录像过滤条件，End在1906起，正常分支1933才SetMainLoop，录像分支可能CloseGame。供F/C独立追链，不直接照搬为已确认运行链。main.py仍由C唯一负责。
5. **证据与置信/来源需补齐。** warcmd资源清单标extracted却只引1612单条catalog，不能证明列出的其他模块；应补真实导入/映射证据或降为相关推测。pycdc_netwar note只有缩略包SHA和候选头，需说明对应的实际输入pyc/工具版本、处理方法及候选不可靠范围。三份仅按旧名称平铺的150/22/1项不算已经完成四篇可用开发手册；补读后用限定名区分类/方法，未知内容仍可留空并明确限制，不要求强行解释全模块。

## 集成兼容性实测

- A+B+D+E+F隔离覆盖：5135登记/13说明/1排除/H0；严格来源与full-inventory闸门通过，无关联警告。
- 再覆盖C242fd8c草稿：5135/16/1/H0同样通过；不撤销C/F内容退修，也不把16说明计成16已完成样板。
- 两组当前dev2各78项：67通过、11 GUI因系统libGL.so.1缺失跳过，0失败/错误。真实Qt本轮未执行。
- ruff含B提取脚本和spec通过；静态Windows检查89文件名/27脚本，ERROR/WARNING/INFO=0/0/0。
- 全目录13说明离线HTML构建成功，25,816,929字节，小于64MiB上限；本轮没有浏览器运行验收。
- 未执行游戏脚本；未做Windows/EXE、原生协议、实机或真实服务端验收；没有把大候选/目录覆盖产物加入Git。

## 下一卡口

- B修签名并重出回执；C按既有意见继续修；F补源码形状候选审阅与证据；B/D/F各自开PR到A。
- D/E各四篇可列H待审队列（8篇A有限预审），不等于8篇H通过或正式集成。
- G尚未交付；H仍按20样板齐备后独审。A只维护工具/协调/集成，不越权包办领域正文。
