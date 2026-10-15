# E提交ec97941的A集成预审（不是H独立审核）

- 被审分支：`arena/14596f40-mxsj-tw-2022`。
- 被审SHA：`ec97941f386c7e199e2f7fb39f49f0cf71b2959a`，基于协议底座cc5c1ba。
- 日期：2026-10-15。结论：**范围/结构预审通过，内容需小修后再交H；尚未合入。**
- 本次只fetch和建立仓库外副本，没有切分支、cherry-pick、merge或修改E正文；未见该head打开的PR。A不写H accepted。

## 1. 已独立复核的范围

1. 差异仅network域6文件：4份JSON、证据报告、给C的main网络协审。计157条类/函数记录、42分支；数量不代表逐项语义已审核。
2. 隔离证据镜像中严格validate（包含SHA/行范围）退出0：20目录/5说明/0 H通过；唯一关联警告为3970尚未编入目录。ruff通过；隔离目录walk模式wincompat 0/0/0。
3. 用独立venv（Python3.11.2、uncompyle6 3.9.3、xdis6.1.8）只读定点恢复3176/2170/871/516/4293，5条均source、baseline、未修keys。只导入分析工具，不导入/执行恢复的游戏模块，没有对1288取条目载荷、解密或恢复。
4. 工具摘要：recover_entries.py=`152dbc28864a10c8b7188df7ae91c8039b0b8c0b056d98591e407b897e39c458`；batch_decompile.py=`a74742231e04c018c3f63452cfc859c20c6404fd73891eae9076bfcf8185b4e8`。原包/参数SHA复核不变。
5. 871/516新恢复稿去掉前6行恢复头后，**原字节分别与仓库既有候选完全相同**，复现了E的关键来源交叉。其余三份恢复后的行数与E报告一致，并逐段抽查主要网络/错误/回调链；未声称全文逐行语义复核。
6. Protocol号表抽查：GS2C_HELLO=1、GS2C_QUICKLOGIN=12、C2GS_QUICKLOGIN=13、GS2C_SELSERVER=47、C2GS_SELECT_SERVER=41、C2GS_TEXT=86、C2GS_MIXPACKET=151、GS2C_HEART_BEAT=63，引用行对应。C2GS/GS2C独立命名空间、缺失号名与服务端未证实边界处理谨慎，保留。
7. 重恢复的net.py:670可见SetMaxLenBytes(3)，main.py:454–474可见四条收包/连接驱动的顺序；低优先队列赋值、DoConnect回调、StartQuickTimer疑点均按静态候选登记，不裁决原文/反编译谁错，也不裁决原生续读2/3字节。
8. E导出HTML在真实Chromium153断网file://冒烟中显示5说明、帧冲突、函数内容与证据状态；真实Qt额外完成E内容载入/渲染冒烟。两者不是完整GUI回归或语义/游戏验收。

## 2. 请E修改的内容

### P1：OnError的隐藏窗口条件写反，瞬连分支缺守卫

证据报告约176行写“若可瞬连则先main.HideWindow”，实际本次恢复的net.py:856–873为：

- 仅当`not IsQuickConnect() and not CanQuickConnect()`时调用HideWindow；不是“可瞬连时”。
- 未收到Hello则OnConnectFail返回；重登/退出标志随后分别提前返回。
- 只有`not IsQuickConnect()`时才进入CanQuickConnect判定：可瞬连则Connect，不可则ShowError；已经在瞬连时不再重复发起。

请同时修正报告与net.json约519行分支的完整前提，不要让简写条件变成“只要CanQuickConnect就一定重连”。

### P1：选服后“回登录界面”与候选实际Show(False)相反

netserver.json约282行SetServerRoleInfo及1071行关系写“否则回登录界面/选服完成后回登录界面”，报告约384行亦如此。

仓库候选netserver.py:183–194（恢复稿R189–200）非TransferServer分支实际是`loginin.OnLogin()`再`loginin.Show(False)`。C候选loginin.py:642–654也显示Show(False)将LoginIn置None；657–661的OnLogin才是SaveAccount。

请明确写“调用OnLogin后隐藏登录面板”，后续进入何界面需要独立证据，不能从函数名推成显示登录界面。这条协审也应反馈C，以统一登录提交/账号保存/面板隐藏链。

### P2：DoConnect成功链的确认程度要前后一致

connect.json约294行summary说“成功/失败最终落到RestarConfirm/RestarConfirmEx”，但同条branches和limitations已承认Success未引用、三处ConnectAttempt都把成功/失败回调传为Fail。main协审§1第5条仍将两者表述为实际成功/失败回调落点。

恢复稿connect.py:164–197支持的是：Success函数体声明了RestarConfirm，但三个注册点均传Fail→RestarConfirmEx。请修改摘要、关系和给C的协审，统一为“候选声明/待核成功链”，不得一处保留缺失、一处又写成已确认实际路径。

### P2：候选SHA重现方法需处理时间头，并补工具/依赖锁

恢复工具每次把生成时间写入第5行。直接照命令重跑，不可能得到同一个整文件SHA，不能要求H重跑后无条件比对E整文件SHA。

请保留E当时整文件摘要作为历史产物标识，同时补充：工具文件SHA、xdis及依赖/完整解释器版本、Big5/后处理选项、可复核的pyc或正文摘要，以及明确的归一化规则。报告可保留H重恢复配方，但注明怎样排除变化的恢复头；不要通过忽略任意差异来“匹配”。

A此次仅去除前6行恢复头后的原字节SHA（用于交叉核对，不是替E证明当时产物相同）：

| entry | SHA256 |
|---|---|
| 3176 | `4cad123e0121c3c18cf24a6af59d1827da28517478b5c92e90f98bf664092c50` |
| 2170 | `0a46ea6fb77879332c53531a1a746556782b9fc48a1fb01f6330e97c8c775e24` |
| 871 | `36def1780a9bb229e98b850339eee91827ed6f6f972f330f52fa3f23183597b9` |
| 516 | `1fccc33d2d20540680c6af62e2bfdcf850291a855ed4bf626374262b8702c94b` |
| 4293 | `bf5051dc501a38128b4cf33dcdd17d5e2e99f2f274838af6e672e14d9edb05dc` |

另外，报告仍有“0.016秒”“15秒级”等文字，又在其他位置说单位未证实。请明确这些数值的单位依据，未经核对不要让限定在段落间丢失；2/3字节冲突及服务端行为的现有限制继续保留。

**报告一改，4份JSON引用的sources.sha256也必须重算；行号移动后逐项更新，再跑verify。**

## 3. 测试夹具：A已经修，不要求E改公共目录

- A在未改夹具的E覆盖副本中，复现75项：3失败、3错误、11 GUI跳过，即58通过；不把跳过算通过。这些失败/错误来自测试期望和证据夹具耦合生产内容，不据此认定E产品代码有6个缺陷。
- A的0.1.0.dev2把schema v1固定样本放tests/fixtures，单元测试不再复制生产annotations/inventory/reviews；实际生产数据另保留不假定说明数量的结构冒烟，验证失败不会被隔离机制吞掉。
- 新增3项回归；A正式内容、E覆盖副本、C+E同时覆盖副本均**78/78、零跳过、11真实Qt GUI**。只在仓库外组合C/E内容，**没有集成**。C的Python2证据.py仍有独立ruff问题，C/E内容问题仍须修；单元绿灯不代替上述内容审查。
- 未改schema、ownership、任务表或C/E正文，其他Agent无需为了测试改自己的交付范围。Windows/EXE/游戏仍未验。

## 4. 下一步

E在自己的固定分支，仅修改network域并逐项回应；修订后可开PR到A固定分支，不开到master、不自行合并。A再检查后交H；main协审交C取舍，F继续核战斗链。A不要求E凭现有Python字面值解决原生帧冲突。
