# E 协审意见：4293 `script/main.py` 的网络相关链路（交 C / A）

> 协审人：E（网络）。主责：C。本文件只是协审意见，不建立 4293 的正文 JSON，
> 不重复 C 的 main.py 说明；C 取舍后由 C 统一写入 `annotations/login/`。
> 方法同 E 网络包：仓库外定点恢复 entry 4293（见 evidence_review_e_network.md §1），
> 只静态阅读，未执行/未 import/未连网；无实机结论，最高 static_reviewed。
> 候选（仓库外）当时整文件 SHA-256 `fec23f35882aaac22a0929faf579213a07a3b95f1d950bcc86fa5321407f2504`
> （含生成时间行，重跑必变，只作历史标识）；按 evidence_review §1 规则去头正文
> SHA-256 `bf5051dc501a38128b4cf33dcdd17d5e2e99f2f274838af6e672e14d9edb05dc`（可复核）。
> 1579 行，stage=baseline、decompile_ok；catalog 第 4294 行历史函数名与本稿一致。
> 下文 `M<行>` 为恢复稿行号（含 6 行恢复头）。

## 1. 建议 C 在正文中保留的网络链（有静态证据）

1. **每帧收包驱动顺序（MainLoop）**：M425–M491。先 `net.g_Net.ProcessServerCmd()`
   （经 `IsTestMultiProcessServerCmd()` 恒真分支走多包节流，见第 2 条），
   再依次 `netserver.ProcessServerCmd()`（选服测连对象）、
   `connect.ProcessServerCmd()`（跨服尝试对象）、
   `netquicklogin.ProcessServerCmd()`（瞬连重连对象），随后才是
   `pubhttp/pubhttps.NetProcess`、`imnet.ProcessIMCmd`、`ping.Loop`、`dgw.Loop` 等。
   建议 C 正文按此顺序画主循环链，并注明这 4 个 `ProcessServerCmd` 是同名不同实现：
   netserver 的遍历连接管理器对象（516 R573）、connect 的遍历尝试列表（2170 R72）、
   netquicklogin 的只驱动单个 `g_ConnectObj`（871 R266），`net.g_Net` 的本体在原生 `C_net`。
2. **多包节流消费 net.py 常数**：M519–M544 `IsTestMultiProcessServerCmd` 恒返回 True；
   `NetMultiProcessServerCmd` 循环上限 `net.MAX_PROCESS_SERVER_CMD_TIMES`、
   每轮以 `net.g_UnpackNumThisFrame` 是否增长判停、累计
   `UNPACK_PACKET_NUM_PER_PROCESS` 并与时间预算（每帧/每次）比较。
   这组常数定义在 3176 net.py R28–R32（0.016/8/半帧/4），E 正文已登记；
   C 只需引用其被 main 消费，不要在 main 正文中重定义数值语义；
   「时间预算真实单位」依赖原生计时，未实测，C 请勿写成已验证的帧时行为。
3. **重启即断网再置假对象**：M150–M227 `Restart`——先 `SaveServerData`（M134–M148：
   一组 C2S 日志回调，任一返回真才补一次 `ProcessServerCmd`）、可选
   `netquicklogin.NormalLogout()`（发送 LoginKey，见 871），再对旧 `net.g_Net`
   先 `ProcessServerCmd()` 后 `Disconnect()`，随即 `net.g_Net = net.CFakeNet()`、
   `pubhttp/pubhttps.Clear()`、`netprotocol.ResetProtocol()`，最后 `StartStep1(flag)`。
   顺序对登录态很关键，建议 C 明示「Restart 后旧连接对象不可再用、g_Net 是空操作假对象」。
4. **瞬连恢复链**：M291–M341 `RestartQuickLogin(loginKey, heroID)`——
   保存/恢复跨重启状态（`RestartSave/RestartRestore`，M228–M289，其中 netserver
   只存 6 个位置参数 `[15..20]` 的不透明槽位、netquicklogin 存 `g_LoginKey`）、
   `Restart(2, False)` 后用 `selectserver.CMXNet` 重建连接（置 `m_QuickLogin/m_HeroID/m_LoginKey`，
   有代理先连代理并 NakedSend 目标 IP/端口，与 E 其它文件的代理裸发同构），
   或 DGW 分支；完成态由 871 的 Hello 回调触发（871 R180–R190）。
   C 应注明 `selectserver.CMXNet` 不是 516/2170 的同名类，E 未审 selectserver 本体。
5. **跨服重连链（成功链为候选，勿写成已确认落点）**：M344–M388 `RestarConfirm`
   （注意原文拼写少一个 t）与 M391–M417 `RestarConfirmEx`——前者重建单个
   `selectserver.CMXNet`（`m_ReConnect/m_Idx/m_Pwd`）后 `netquicklogin.StartQuickTimer()`；
   后者先置 FakeNet 再 `connect.KuaFuConnect(idx, pwd, proxy_port_ip_list)`
   （2170 R221）多路并发。就 2170 `DoConnect` 而言，按恢复稿字面只有
   「Fail→RestarConfirmEx」是注册的回调落点；`RestarConfirm` 只出现在未被引用的
   内嵌 `Success` 函数体里（2170 R171–R177），属候选声明、真实成功链待核。
   请 C 在 main 正文中统一按此口径写：可确认 main 侧两个函数的定义与
   被 `Success/Fail` 函数体引用的事实，不得把 RestarConfirm 写成 DoConnect
   已确认的成功落点（KuaFuConnect 经 CMXNet.S2CHello 的另一条链不受此限）。
   E 在 connect 正文已同步此口径；C 只需给入口与状态，不要重述 2170 的尝试细节。
6. **关机/退出链**：M73–M131 `CloseGame` 先 `netquicklogin.NormalLogout()`、
   给 `net.g_Net.m_IsExit = True`（net.py 的 OnError 据此抑制弹框，3176 R856 起），
   延迟 30 计数后才真正置 Quit；M746–M767 一带还有「发送未完成且 t<90」的等待/Restart
   与 `m_IsRelogin` 置位（供 net.OnError 抑制重复处理）。建议 C 与 net.py 的
   `m_IsExit/m_IsRelogin` 分支互相引用，不要单方面写死弹框行为。
7. **窗口/尺寸变化触发瞬连**：M1503–M1557（`SetTryTime/ChangeTime`）两处在特定条件下调
   `netquicklogin.Connect(False, '窗口大小改動' / '-2')`。这是「非断线也可能触发
   瞬连入口」的证据，C 若写快捷键/窗口链时请留意触发源不止网络错误；
   net.py OnError 里的 `'網絡中斷-2'`（3176 R856 起）是另一处同类原因字符串。

## 2. 请 C/A 注意的静态异常与缺失（E 不在 main 正文中下结论）

- **未定义名疑点**：M319–M320 DGW 分支调用
  `netquicklogin.DoDgwQuickLogin(loginKey, heroID, serverid)`，其中 `serverid`
  在 `RestartQuickLogin` 作用域内未见赋值（本稿 grep 仅此一处出现），
  且 871 netquicklogin.py 中不存在 `DoDgwQuickLogin` 定义（871 全文已读）。
  可能是反编译丢线、动态注入或原文缺陷；请 C 在正文中标「缺失待核」，
  不要补写 DGW 瞬连流程，F/其它协审如有 DGW 模块证据请回 A。
- **选服角色信息落点反馈（E 516，请 C 统一登录链口径）**：516 的
  `SetServerRoleInfo` 在非 TransferServer 分支实际依次调用
  `loginin.OnLogin()` 与 `loginin.Show(False)`，即调用 OnLogin 后**隐藏**登录面板，
  不是显示/回到登录界面（E 旧稿曾误写「回登录界面」，已更正）。请 C 在 loginin
  正文中据此统一「OnLogin 的账号/保存语义、Show(False) 隐藏面板、隐藏后进入何界面」
  三者的证据链；隐藏后的界面去向在 E 的 516 证据内缺失，不要从函数名推断。
- **`StartQuickTimer` 条件疑点与 main 强相关**：main 在 M387、M416 两处调用
  `netquicklogin.StartQuickTimer()`，但 871 恢复稿中该函数只在
  `g_oStartQucikTimer` 为真时才建字面 `QUICKLOGIN_SECOND=10` 的计时器
  （首参单位未证实，不得径称 10 秒）、而该全局初始/重置均为 None
  （871 R272–R284、R16、R34）。按字面读，跨服重连后的「StartQuickTimer 备瞬连」
  可能不生效。E 已在 871 正文中登记为待核异常；请 C 在 main 正文中同步标风险，
  勿把该链写成已确认可用的重连保障，最终须回码对象或实机判定。
- **同名混淆风险**：main 还直接用 `selectserver.CMXNet`（M323、M368），
  与 516 netserver.CMXNet、2170 connect.CMXNet 三者同名不同类、构造签名不同。
  C 正文若画类图必须分开标注所属模块，E 正文已按此处理。
- **netserver 状态槽位不透明**：M229–M231 `RestartSave` 对 netserver 只记
  `[15, 16, 17, 18, 19, 20]` 六个位置索引（配合 M263–M289 的顺序存取），
  其对应的全局变量名在本稿中不可见（应为被截断/混淆的元组形态），
  E 无法把它们映射回 516 的具名全局。请 C 标缺失，不要按 516 的全局列表猜配。
- **网络外延未审**：main 还驱动 `ping.Loop`、`dgw.Loop`、`imnet.ProcessIMCmd`、
  `pubhttp(s)`（M466–M474），均不在 E 的 4 个样板内；E 只确认 main 的调用顺序，
  不确认这些子系统行为。心跳本体（heartbeatcheck 等）亦然：
  net.py 分发表把 `GS2C_HEART_BEAT` 路由到 heartbeatcheck（符号证据在 3176），
  main 正文如需写心跳周期，证据不在本协审范围内，请另找来源或标缺失。

## 3. 给 A 的集成提示

- 4293 的网络部分与 E 的 3176/2170/871 三份正文存在互相引用：
  E 正文的 relationships 已以 4293 为上游（帧驱动/重连入口）登记，
  请 A 集成时检查 C 正文是否回指，避免单向链被误读为已双向确认。
- 三处待核异常（队列低优先赋值、DoConnect 的 Success 未引用、StartQuickTimer 条件）
  分别落在 3176/2170/871，另加本文件第 2 节的 main 侧两处（serverid、
  netserver 槽位）。建议 A 在总导航单列「静态异常待原生复核」清单，不要让任一
  Agent 在正文里先行改判为 bug 或正常。
- 本协审无实机、无抓包、无原生复核；帧续读 2/3 字节冲突（见 E 证据报告 §2.3）
  也请 A 不要依据 main/net 的 Python 字面值裁决。

## 4. 全新 N4 退修协审补充（交 N2 / A；不是 main 正文）

- 本节作者是全新 N4 网络会话，非旧 E。上文 M 行、候选 SHA 和 main 链是旧 E 历史协审；
  本 N4 只独立恢复 3176/2170/871/516，**没有重恢复或重验 main**，不能把上文算作 N4 的新实证。
- Q2 采取收缩回答：netquicklogin 的诊断问答现只保证 871 的 CanQuickConnect/清 Key/Connect showdlg
  与 3176 OnError 门禁有实际原行证据，不再用状态初值段证明 main 窗口触发。请 N2 如采用上文
  第 7 条，独立核 main 的实际 if 条件和调用行后在自己的 main JSON 取证；否则保留待核。
- 已核 3176 R856–R873：初次 HideWindow 仅在 not IsQuickConnect() and not CanQuickConnect()；
  之后未 Hello、m_IsRelogin 或 m_IsExit 可返回，最后只有不在瞬连中才 Connect/ShowError。
  因而“退出/重登抑制”不代表一定抑制了前面的 HideWindow，main 正文请区分调用先后。
- 3176 LowestUnpackParams R55–R70 先写原生 2，再按 iRate 回写 2/iRate；若 main 描述消费预算，
  不得写成最终固定每轮 2 包，也勿与命令队列 PROCESS_NUM_PER_TIME=2 混为一项。
- 2170 DoConnect R184–R196：有代理才前两条各一次，无代理 target_idx 二选一仅一次；
  三处 Fail 双回调/Success 未引用仍保留，不能把 main.RestarConfirm 补成已确认的成功链。
- 516 SetServerRoleInfo 的 OnLogin 后 Show(False) 隐藏口径保留；main/serverid、DGW 缺链、
  netserver 不透明槽位、StartQuickTimer 条件异常、帧长 2/3 冲突仍待核，不因文档退修改判。

新证据与逐项响应：`evidence_n4_network.md`、`N4_reproduction.json.template`、`N4_RESPONSE.md`。
本节仅交协审，未改 `annotations/login/`、reviews、A 总表或 STATUS。
