# A接手收尾：七PR合入、16份有限通过、4份A修订待独审

日期：2026-10-16。用户“你帮他们收尾吧”授权A接手；既有“H宕机了你审吧”授权有限代审。**不是独立H，不自批A所写正文，不合master、不上传。**

## 1. 实际集成与当前状态

本轮开工前A的8638aad已推且工作区干净。逐条执行`gh pr merge <明确PR号> --merge`成功并读回MERGED，base均为固定A分支；随后本地fast-forward到集成检查点`e60fcb588ff7a50249504ff603f1a64af50f5c8b`。

|PR|固定head|实际merge|
|---|---|---|
|#43|`f953eb992bf3`|`474bd3abe514`|
|#39|`c7142366faba`|`3f0db0306c49`|
|#41|`77b64beda4b3`|`eb3b7b776eea`|
|#40|`44230b98527f`|`bbfb2748aca7`|
|#44|`6fd5061dded8`|`c2c1f6e1803f`|
|#42|`23b60f96c602`|`e06e6f4c4bac`|
|#45|`db872c5cd6aa`|`e60fcb588ff7`|

正式状态：**5135登记 / 20说明 / 16有限accepted（12 H + 4 A_delegate）/ 4pending / 0stale / 0changes_requested / 1排除**。此前§3.49/3.50及原分派卡是历史，不把“未合/3通过”继续当现状。目录128382个函数结构记录不是128382条讲解；battle仍42条名称底稿，全部语义/实机没有验收。

- 九份N7模板逐个核对JSON原字节SHA一致后激活；原已过UI三篇保护，gameplay采用N6稿与N7独审，不恢复A自批。
- 登录四篇原字节不改，A_delegate新作有限代审，不挪N7基线退修的SHA冒充N7已审。
- 四篇battle有A改写，均明示共同作者并保持pending；不能用本次结构通过或用户授权代替独立审核。

## 2. N2四篇有限代审的事实范围

四条原包目录ID/offset/length、stored、pyc、raw u6与正文SHA重新计算匹配。修正工具后通过真实隔离子进程分别传布尔False/True，四对raw/正文输出与N2钉值匹配，严格cp950后处理4/4一致。无恢复游戏模块的import/执行，无业务URL请求。原N7基线问题清单仅用作复核索引，新review均记A_delegate及授权。

实际阅读并核对六题涉及的路径、Claim和关系：

|入口|本轮核对|
|---|---|
|mainpage 337|refreshbulletin的succeed假和缺头分隔符两失败点；写news.txt异常才缓存g_News；OnMessage(30)按g_LangVersion取News/Service；首页选服/TW外链/非TW注册；Show异常else保留未知|
|loginin 4806|普通按钮仅非TW协议框门禁；LoginOk校验→C2SLoginIn→错误回调；OnLogin独立SaveAccount；OneoffLogin不串入普通链；ShowLogin不猜地区|
|register 4007|reg1–5/confirm布局定位；Step三类映射；普通OnRegisterGame成功Step(2)/120验证码与2980的Code250→Register2980(1)分开；OnRegCode错误处理；ResultEmail提供数据方向|
|main 4293|新候选1573行去六头正文、17段975行摘录保真；MainLoop/WarLoop/Loop setters、Restart→AfterRestart；ExitGame守卫与延迟Quit；退出/重登；ClearHotKey、默认键与SwitchHotKey守卫，不据赋值猜message或直接显示关系|

四篇新review各自钉原字节SHA和具体范围。接受只限原五组阻塞与六题相关的新/改结论、来源链和定位，不是穷尽每个函数/分支。反编译异常、原生焦点/事件、布局内容、完整选服/登录成功链、真实服务端均未升级为已验。

## 3. A实际补写的battle范围（必须非A末审）

接手中不止修改war一句：

1. **war**：B-N5-04限定“仍需消费队列的非终止回调”；End录像CloseGame返回、普通SetMainLoop收尾是不继续推进的终止反例。补w_process/w_wait/w_end，修改建议标inferred。
2. **netwar**：同一全称NextCmd/Wait要求也出现在其新增指令指南，已同步收窄；撤回“C2S与S2C必须字段严格对称”的误导，每个方向应各自匹配服务端协议，服务端未核。
3. **e_warctrl**：主动RemoveSkill先Release再_removeSkill；自动_OnUpdate直接_removeSkill，不伪称自动路径也Release。TriggerSignal调用ssEmit是发出而非订阅。ModuleReset仅置None，不证明timer/资源释放，撤回“跨战斗必须reset/登记即可完成技能”的建议。
4. **warcmd**：损坏键实际是候选正文L12、映射字面顺序**第6项**，不是第12项；同步摘录/provenance的元描述及四篇引用SHA。原L前缀候选原文一字未改；没有猜补损坏键。新增命令指南只是从本地三实参调用推测，不代表21个子模块接口都核过。

原B-N5-01/02/03仍closed；此次不复活原三项，也不替反编译候选修程序。作者N5原回执保留历史SHA，追加明确A补记与新SHA，而不是假称N5独自交完。**A对四篇均不出accepted**。

|待非A审核文件|最终JSON原字节SHA256|
|---|---|
|e_warctrl.json|`8dfca6e5ca37b5787c11ce6f0d1d4c688fb8d9eae4fd94f938e512d69e2deb31`|
|war.json|`3e2a00ab67215267c471a9d60b90a09b743d765da46ae94571eabd6de20400d7`|
|netwar.json|`614bef9d870b118b1e58bf9593e5297de08a3da4cf7b819adfc5f15d27bd766a`|
|warcmd.json|`65e19f3c4a93e2dbb8add8ecea523f6d64bddf6f55dd031cd864986c8e2d15da`|

## 4. 工具修复与统一闸门

`recover_entries.py`从`decode_big5=repr(decode_big5)`改为传入原布尔值，避免模板`!r`二次表示使False成为真值字符串。先加两项AST/假子进程回归并在原代码复现2失败，再修一行；修后27项合成工具测试全过。测试只检查生成子进程代码AST、合成输出，不导入游戏。另把既有测试的硬编码/tmp换成自动清理的TemporaryDirectory，绝对路径安全夹具用合成路径，避免Windows测试依赖真实POSIX位置。

工具新SHA：`cd0e95fef232e9b34769bdb1e98e70dd46b6e023d17fca6ac32670d854196a35`。历史N2/N5/基线报告的旧工具SHA保持历史，不改写成新工具；本次四条真实False/True的验证证明其输出链仍与原钉值吻合。N1提取器及产物指纹未变。

新统一入口（依赖requirements-dev.txt）：

```sh
python script_manual/check_manual.py
# 需要Qt真跑时，缺Qt不得跳过：
python script_manual/check_manual.py --require-gui
```

六闸门：严格来源/full、标准手册测试、N1独立测试、恢复工具合成测试、ruff含spec、Windows静态。新增4项纯合成runner回归，检查命令覆盖、非零失败传播、启动失败和强制GUI环境；任一步失败整体非零，不短路掩盖后续结果。Windows扫描用--no-git直接walk包含新文件。命令不做恢复、执行游戏或生成站点。

## 5. 最终合并态实际验证

|检查|结果|
|---|---|
|严格来源 + full inventory|通过；5135/20/16/1，无过期警告|
|标准手册测试|86发现：75通过、11因缺PySide6跳过、0失败；原82另加runner4|
|N1独立元数据|32/32通过，无跳过；不是标准86的子集|
|恢复工具合成回归|27/27通过，无跳过；原25另加布尔2|
|ruff含spec|通过|
|Windows静态walk|manual 168路径/31源：ERROR/WARNING/INFO均0；改动工具2路径/2源亦全0|
|N1真种子重放|**两棵真实隔离树**，各20冻结种子→sample/full，四次成功；三份产物跨树一致且与交付字节一致；1288定点读取4次均0|
|严格离线HTML|构建通过；HTML SHA `7d5266729228c475591591647ee317f262fc76a284f9f7ffd183372c5767439c`|
|jsdom26.1.0实际脚本|4中文搜索、2审核过滤、3路径/身份导航、CreateCmdObject函数搜索、20篇×4页80tab、hero→npc跳转均过；N2四篇显示A_delegate授权，A共同作者battle四篇保持pending，无脚本错误|

N1整包SHA读取会覆盖1288字节范围，不谎称从未读过其字节；审计证明没有定点payload读/解密/恢复。此次两树重放是新执行，不借上轮单树的退化“跨树一致”冒充。

所有大语料、pyc、raw、虚拟环境、站点和原始日志留仓库外`/home/user/manual-finalize-20261016/`，小JSON报告钉摘要；没有把它们打入Git/网盘。HTML/DOM测试不是真实浏览器/CSP/Qt/Windows/EXE/游戏验收。

## 6. 仍未通过与下一步

- **四篇battle的新字节尚无非A独立审核**；A已经完成修正，不把自己reviewer改成H或A_delegate凑20。只需独立按上表SHA复核，不能复用6fd5061的旧结论。后续实际请求链接追加在本报告；目前没有新的N7审核结果。
- Qt缺依赖导致11跳过；Windows/EXE、真实浏览器/原生、服务端/实机未跑。42名称底稿与未扩5000语义明确保留。
- 不改master/游戏/编辑器/启动器/原包/参数，不上传，不重做79MB语料，也不要求用户再启动七个agent。


### 实际交接留言（A补记）

- 修订内容固定提交：`0b04cc17ae3e4c10c7dc3d60ba48fc1d43d193bd`（已推A，四篇待审SHA仍为本报告表）。
- N7独立末审请求已实际发布：https://github.com/a565551313/MXSJ_TW_2022/pull/45#issuecomment-6206831156 。PR45已合；若N7继续，须自己的固定分支合此head并新PR到A，只改reviews，不改四篇字节。
- N5收尾通知：https://github.com/a565551313/MXSJ_TW_2022/pull/44#issuecomment-6206831398 。
- 这只是已发布请求，不等于N7已收到/开工/给了新结果；截至本次交接仍16有限通过、四battle pending。
