# E（网络）小证据审阅报告 — 3176 / 2170 / 871 / 516 定点恢复摘要

> 性质：按 `script_manual/docs/CONTRACT.md` §3 的「小审阅报告」约定提交的可分发摘要，
> 不是完整源码、不是第二套底稿。正文 JSON（`net.json` 等）引用本报告的行号；
> 原始行号另以 `R<行>` 标注，H 可按 §1 配方在仓库外重恢复后逐行复核。
> 本报告只做静态阅读：未执行、未 import、未 eval 任何恢复模块，未连网，未改游戏包。
> 1288 严格排除：未读其 payload，未恢复，未引用。

## 1. 来源、方法与可复核性

- 冻结输入：`data/script.fls` SHA-256
  `8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72`（与
  `script_manual/coordination/baseline.json` 一致，已只读核对）；
  参数表 `tools/decompiler/script_fls_keys.json` SHA-256
  `43bb090d09b95e234292829e7d5ce1495d53c0ec2ee4e9727d09aac3d97daceb`（已只读核对）。
- 恢复命令（仓库外，只读输入）：
  `/home/user/dec-venv/bin/python tools/decompiler/recover_entries.py
  --out /home/user/mxsj-e-net/rec --entries 3176,2170,871,516,4293
  --report /home/user/mxsj-e-net/rec_report.json`
  解释器 Python 3.11.2 + uncompyle6 3.9.3；5 条均 `stage=baseline`、
  `密钥修复=False`、`decompile=decompile_ok`、`kind=source`。
  产物只留仓库外，不入库；本报告只记其摘要与行号。
- 行号约定：`R` = 仓库外恢复文件的行号（含文件头 6 行恢复注释）。
  仓库内既有候选（871/516）无此 6 行头，故仓库内行号 = `R - 6`（已用 diff 实证，见 §4/§5）。
- 交叉核对（本轮实际执行，均为只读）：
  1. 871/516 的仓库外新恢复稿与仓库内
     `tools/decompiler/output/script_fls/script/netquicklogin.py`、
     `tools/decompiler/output/script_fls/script/login/netserver.py`
     做 `diff`：除恢复头 6 行外逐行一致（见 §4/§5 的 SHA）。
  2. 函数名与 `server/docs/catalog/script_entries.jsonl`（SHA-256
     `d42694bf2621496a9107b22c1123a73a753a34fd6e907d74cd72707b127f62da`，
     与 baseline 的 inventory 种子来源摘要一致）逐条比对：2170/871/516 的
     历史函数名集合与新恢复稿的定义集合一致（顺序按代码对象序，略有差异）；
     3176 历史解码为 `fail`、函数名为空，新恢复稿是本轮首次可读文本（见 §2）。
  3. 协议号数值与 entry 3970 `script/protocol.py` 的号表产物
     `work/dream-world-connect-login-map/artifacts/protocol_table/protocol_opcodes.json`
     （SHA-256 `a464a9cf66d66de01b8ed6272ea7529217c5d1631f94509bd7ca773077a9c9d9`；
     其自述方法为 marshal 线性遍历、未执行游戏代码，412 条赋值/409 个整型）
     交叉比对。注意：该号表不在 E 的 4 个样板内，以下凡引数值均注明出处，
     不把号表当作 E 已独立验证的服务端行为。
- 置信分级口径（与 CONTRACT 一致）：`extracted`=自动/直接观察到的字面事实；
  `static_reviewed`=作者已读恢复文本并核对的解释；`inferred`=推测待核；
  本工作包无任何 `runtime_verified`（无实机记录）。

## 2. 3176 `script/net.py`（仓库外候选 c8221fc8…）

- 身份：entry 3176，entry_id `2691519347`（0xa06d5373），存储长 17485，
  解出 pyc 长 42742，`co_filename='script/net.py'`（path_class=ok，未改名）。
- 候选文件（仓库外）SHA-256
  `c8221fc806ed0af1cd4dcb4905cf29d4ba25e0cb7652be093405386d3a96c905`，
  1364 行（uncompyle6 3.9.3，Py2.5 字节码 62131）。
- 本节行号均为 R 行（恢复稿行号，下同）。

### 2.1 职责与结构（net）

- R13–R18 导入：`defines, permission`、`from C_net import *`（原生网络基类来源）、
  `innerversion, interface`、`from protocol import *`（协议号符号来源）、
  `time, huodongdefine, misc, performancecount, specialword, C_marshal`、`deque`。
  职责判断：游戏主通道的 Python 层总管——连接对象、收包分发、发包封装、
  HTTP 小通道、断线/错误提示与命令延迟队列都在本文件；线格式与套接字本体
  在原生 `C_net`（`CNetClient`/`CServerCommand`），不在本文件内。
- 主要定义（R 行）：`ResetUnpackParams` R34、`LowestUnpackParams` R55、
  `GetFNet` R73（恒返回 True）、`SetCheckPacket` R77、
  `InitNetServerCommandQueue` R83、`OnLoadingFinish` R94、
  类 `CNetServerCommand(CServerCommand)` R630、`CNet(CNetClient)` R661、
  `CFakeNet(int)` R996、`ShowError` R1013、`GetUrlInfo` R1048、
  `CHttpObject(CNetClient)` R1080、`DisconnectNet` R1148、
  `ClearCmdDelay` R1169、`CreateCmdDelay` R1192、`OpenUrl` R1201、
  `GetNet` R1217、模块级 `PacketPrepare` R1221、`WrapPacketSend` R1228、
  `CNetServerCommandQueue` R1290；模块末 R1364 为顶层 `return`
  （uncompyle6 对 Py2.5 模块码的已知伪影，不计为源码语义）。

### 2.2 协议号证据（net，分别取证）

- 符号分发：R111–R611 `NET_FUNCTION_NAME` 是以 `GS2C_*` 符号为键的
  「协议号 → (模块名 sModuleName, 处理函数 sProcessFuncName, 可选扩展标志
  iExtFlag/特殊函数 sSpecialFuncName)」大字典；数值本身不在本文件，
  由 `from protocol import *`（R15）注入。本文件只直接给出 3 个本地常数：
  `GS2C_PLAYER_IB = 24`（R24）、`GS2C_CLIENTUI = 174`（R26）、
  `GS2C_ZHIDAO = 181`（R27），与 3970 号表同名数值一致（号表 JSON 对应行）；
  `GS2C_ONLINEEDITSOURCE = 46`（R25）在 3970 号表中无同名项，
  且本文件内除定义外未见使用点（grep 仅命中定义行）——不得据此断言 46 号
  在服务端有处理，更不得断言其不存在（号表自述未用值为 17/28/46/197，
  口径来自号表产物，非本文件）。
- 字面协议号：`GetFunc` 对 `iCmd == 219` 特判返回
  `S2CBoutSpecialServerCMD`（R718–R720），后者转调
  `netnewplayerguide.S2CRefreshInfo`（R710–R716）；
  `SPECIAL_SERVER_CMD` 亦含字面键 `219: True`（R613–R621 段内）。
  3970 号表的 GS2C 命名空间无 219 同名符号（仅 C2GS 方向
  `C2GS_LOGIN_EXT_INFO=219`），故 219 的 GS2C 语义名在本工作包内缺失，
  只登记「字面 219 已被客户端 Python 路由到 netnewplayerguide」这一事实。
- 战斗字面号：`OnServerCmd` 内 `icmd == 167` 先 `UnpackInt(1)` 取子字节，
  子值在 `(7, 8, 13)` 时入延迟队列、否则立即调用处理函数（R751 起的
  OnServerCmd 体内，约 R780–R795）；`icmd == 112` 调
  `warrecord.StartRecord(self)`（同段）。3970 号表中 GS2C 方向
  167=`GS2C_PLAYER_CHAT`、112=`GS2C_WAR_START`，与此处「聊天/战斗」上下文
  吻合，但这是跨文件交叉推断，不是本文件内符号证据，置信级只能标 inferred。
- 方向性提醒：号表里 C2GS 与 GS2C 是两套独立命名空间且同号并存
  （如 1=C2GS_LOGIN_ACCOUNT_ENTER 与 GS2C_HELLO、24、63 等）；
  客户端「发送符号」（C2GS_*）只能证明客户端这样组包，
  不能证明服务端已确认、已处理或回包内容。

### 2.3 帧处理与收发（net）

- 帧/长度（Python 层唯一直接证据）：`CNet.__init__` 调
  `self.SetMaxLenBytes(3)` 与
  `self.SetProcessSvrCmdNumPerFrame(UNPACK_PACKET_NUM_PER_PROCESS)`（R663–R672）。
  但这只是 Python 对原生对象的设值调用，其线格式含义（是否等于
  「0xFF 转义后续读长度字节数」）在本文件内无定义；
  仓库内 `work/dream-world-connect-login-map/report/client-status-20261012.md`
  §2 以 mx.exe 反汇编主张该字段原生构造默认值为 2、续读为 2 字节小端，
  并称全二进制只有一处 imm32 写入。二者表面冲突（Python 运行时经包装层
  传 3 不会被「imm32 写入扫描」命中），本工作包未做原生复核、未抓包，
  故帧续读字节数在本包内记为「未结清冲突」，禁止把 3 或 2 任一写成已证实线格式。
- 发送：`CNet.PacketPrepare` 记录 `m_NetHead` 后转原生（R901–R904）；
  字段追加有 `PacketAddPS`（长度前缀字符串，R906–R911）、
  `PacketAddBinaryPS`（R921–R926）、`PacketMarshal/UnpackMarshal`
  （经 `C_marshal`，R936–R947）、`PackLstFreeColor`（R949–R961）；
  `SendLongText` 以 `C2GS_TEXT` 分片：先发子型 1，再按 240 字节切片发子型 2
  （R883–R894；3970 号表 `C2GS_TEXT=86`，数值来自号表）。
  `WrapPacketSend` 以 `C2GS_MIXPACKET`（号表 151，本文件 R1229 取符号）
  做「夹包」：marshal 扩展消息、md5 校验串、整包 <240 时单包（子型 3），
  否则按 200 字节分片（子型 0 首片/1 中片/2 尾片）（R1228–R1288）。
  以上均为客户端组包代码，不证明服务端拆包/校验行为。
- 发送侧自检（异常分支）：`CNet.PacketSend`（R963–R994）在原生发送后，
  若 `g_CheckPacketFlag` 开启，会随机抽一字节与发送后再次取到的包数据比对，
  不一致则调 `blacklist.SendIlleageCallInfo(119, ...)` 并打日志
  「包被修改，通知服务器」（R980–R990）。这是客户端自报线索：
  119 是该自报调用的字面参数，不是已确认的协议号语义；
  服务端是否据此处置，未知。
- 接收/解包：`CNetServerCommand` 与 `CNet` 各有一套
  `UnpackSigned`（R632–R638 / R875–R881）、`UnpackPS`（R647–R653 / R913–R919）、
  `UnpackString`（经 `pubtimeformat.ChangeTimeLink` 改写时间链接文本，
  R655–R659 / R896–R899）、`UnpackBinaryPS`（R928–R934）。
  原生收包状态机（`ProcessServerCmd` 本体）不在 Python 文本内。
- 每帧处理节流：R28–R32 常数 `0.016` 秒/`8` 次/每次半帧/`4` 包，
  `ResetUnpackParams`/`LowestUnpackParams` 按 `setfps.GetCurFrame()/30`
  缩放并回写原生 `SetProcessSvrCmdNumPerFrame`（R34–R70）。
  这与 4293 `main.py` 的 `NetMultiProcessServerCmd` 消费同一组常数
  （协审报告另述），但帧率缩放公式是否在原生层同样生效，未验证。

### 2.4 回调/分发与错误分支（net）

- 分发主链：`CNet.OnServerCmd(icmd)`（R751–R812）顺序为——
  计数 `g_UnpackNumThisFrame` → 若命令队列对象存在且
  `AddNetServerCommand` 命中高/低优先级集合则入队返回 →
  `GetFunc(icmd)` 查 `m_NetFunction` 缓存、未命中则按
  `NET_FUNCTION_NAME` 动态 `__import__` 目标模块并 `getattr` 处理函数
  （R718–R735）→ 函数为 None 时只打日志
  `!!!! func==None, OnServerCmd: 0x%x` 并返回 →
  记录 `crashrpt.RecordPacketData`、`AddS2CProtocol` →
  战斗中按 `m_WarCmd` 扩展标志 bit0 缓存命令/bit1 写战报 →
  `g_CmdDelay` 存在时按 bit4（16）入 `g_DelayQueue`（167 特判见 §2.2）→
  `netgm.IsClientLocked()` 且函数非 netgm 模块时拦截 →
  计时调用 `func(self)` 并做性能计数。
  动态导入意味着「字典里有符号」不等于「目标模块/函数在冻结包里存在且可导入」，
  本包未逐项核对全部目标模块。
- 特殊通道：`OnSpecialServerCmd`（R824–R848）对
  `SPECIAL_SERVER_CMD` 集合、`GS2C_HUODONG_OP`（先 `PreUnpackInt(1)`+
  `PreUnpackString` 预读子标识与 `SPECIAL_HUODONG` 比对）、
  `SPECIAL_SERVER_CMD_EXT`（本文件内为空字典 R628）分别处理；
  `GetSpecialFunc`（R737–R749）取 `sSpecialFuncName` 特殊处理函数。
  预读不消费的语义依赖原生 `PreUnpack*` 实现，Python 层未定义。
- 命令队列：`CNetServerCommandQueue`（R1290–R1362）双 deque 高/低优先，
  `Start` 用 0.016 秒定时器 `Loop`，每轮最多处理 2 条（R1293、
  R1317–R1343）。静态异常点（须 H/原生核对，不得当已证实 bug）：
  `Loop` 中低优先分支写作 `self.m_oLQueue = oQueue`（此时 oQueue 为 None，
  疑似应为 `oQueue = self.m_oLQueue` 的反编译/原文笔误，R1323–R1343）；
  且 `HIGH_PRIORITY_CMD`/`LOW_PRIORITY_CMD` 在本文件内均为空集（R109–R110），
  未见本文件内的填充点，故队列实际是否启用高/低优先，缺失待查。
- 连接与错误：`CNet.Connect` 先过 `whitewebsite.CheckUrlIsInWhite(ip)`，
  不在白名单直接返回不连接（R678–R687）——参数名虽为 ip，亦走 URL 白名单函数，
  语义以原生/whitewebsite 模块为准。
  `OnConnectFail`（R850–R854）把全局 `g_Net` 换成 `CFakeNet()`（空操作假对象，
  R996–R1010：把 CNet 全部公有方法替换为无返回值 FakeFunc）；
  `OnError`（R856–R873）：若可瞬连则先 `main.HideWindow`、
  未收到 Hello（`m_Hello` 假）转 `OnConnectFail`、已标记重登/退出则直接返回、
  否则能瞬连走 `netquicklogin.Connect(sReason='網絡中斷-2')`、
  不能则 `ShowError(msg)` 弹「退出/重新登录」框（R1013–R1046）。
  `DisconnectNet`（R1148–R1167）用 20 次计数定时器等
  `g_Net.IsSent()` 后 `Disconnect()` 再 `ShowError`。
  `ShowError`/重登链含 10 秒延迟回调（R1021–R1035），属 UI 行为，未实机验证。
- HTTP 通道：`CHttpObject`（R1080–R1146）自拼
  `GET ... HTTP/1.1\r\nHost:...\r\nConnection: Close` 后 `NakedSend` 裸发，
  用 `CreatePyCommand(0, NetProcess)` 轮询 `Process()` 累积数据；
  回调约定 `callback(data, succeed, *arg)`，`OnError` 里以响应行
  第二段前 3 字符 == '200' 判成功（R1115–R1146）。
  构造时亦先过白名单（R1090）；`method` 参数除存入外未见使用（只发 GET）。
  这是明文 HTTP 形态描述，不是已抓包的线上行为。

### 2.5 配置与修改风险（net）

- 直接相关配置面：协议号符号来自 entry 3970 `protocol.py`（改号须改彼处，
  不是改本字典的键名）；白名单判定在 `whitewebsite` 模块（不在 E 样板内）；
  本文件内可调面只有节流常数（R28–R32）、特殊命令集合与队列开关
  `g_bEnableServerCommandQueue`（R22）、包自检开关 `g_CheckPacketFlag`（R21）。
- 风险：改 `NET_FUNCTION_NAME` 的模块/函数名字符串会影响动态导入目标，
  写错只会在运行期 `getattr/import` 失败或落入 func==None 日志分支；
  改 `SetMaxLenBytes(3)` 的字面值在帧冲突未结清前属于高风险臆测修改；
  `PacketSend` 自检与 `WrapPacketSend` 的 md5/分片是反篡改/夹包逻辑，
  改动可能触发服务端侧未知处置（未证实），不得以客户端代码推断服务端容忍度。

## 3. 2170 `script/connect.py`（仓库外候选 002200b5…）

- 身份：entry 2170，entry_id `1832585054`（0x6d3b075e），存储长 4322，
  解出 pyc 长 8329，`co_filename='script/connect.py'`（path_class=ok）。
- 候选文件（仓库外）SHA-256
  `002200b5022b23b77bb0e0034cc5d4bb962d32dbb4879f817dffbf54c4ea8b55`，295 行。
- catalog 第 2171 行历史函数名与本稿定义集合一致（历史解码 ok）。

### 3.1 职责与结构（connect）

- 职责判断：选服/跨服场景的「多路尝试连接」层——同时向多个候选地址发起
  连接尝试，谁先回 Hello 谁胜出；并提供跨服（KuaFu）直连与代理候选列表生成。
  它不做账号登录本体（Hello 之后转 `netlogin.S2CHello`）。
- 主要定义（R 行）：`CMXNet(net.CNet)` R17（`__init__` R19、`OnConnectFail` R30、
  `OnError` R38、`ConnectServer` R46）、模块函数 `S2CHello` R61、
  `ProcessServerCmd` R72、`CAttemptNet(net.CNet)` R93（`Run` R128、`Release` R136 等）、
  `S2CAttemptHello` R144、`ConnectAttempt` R151、`ClearAttempt` R158、
  `DoConnect` R164（内嵌 `Success` R171、`Fail` R179）、`IsDianXin` R200、
  `KuaFuConnect` R221、`NewKuaFuConnect` R233、`GetKuaFuProxyLst` R247；
  全局 `g_NetobjList=[]`、`g_AttemptDict={}`、`g_DelaySecond=24`（R14–R16）。

### 3.2 连接、协议号与回调（connect）

- 协议号证据：两处把「命令 1」直接注册为 Hello 处理——
  `CMXNet.__init__` 的 `self.m_NetFunction[1] = S2CHello`（R27）、
  `CAttemptNet.__init__` 的 `self.m_NetFunction[1] = S2CAttemptHello`（R101）。
  字面 1 与 3970 号表 `GS2C_HELLO=1` 一致（数值来自号表交叉）；
  本文件证明的是「客户端把收到的 1 号命令交给这两个函数」，
  不证明服务端一定先发 1 号或其包体字段（字段在 `netlogin.S2CHello` 内解包，
  不在 E 样板内；work 区 hello-path 笔记有他人结论，本包未复核）。
- 连接发起：`ConnectServer`（CMXNet R46–R58 与 CAttemptNet R114–R126 同构）——
  有代理时先连接代理地址，再以 `NakedSend` 裸发目标 IPv4 的 4 字节
  （逐字节 `chr(int(octet))`）+ 目标端口 4 字节小端序拆分
  （`port%256, /256, /65536, /16777216`）；无代理直连 `Connect(m_IP, m_Port)`。
  这是代理握手字节的客户端写法；代理服务端是否按此解析，未证实。
- 成功回调：`S2CHello`（R61–R69）清空 `g_NetobjList`、把胜出对象写入
  `net.g_Net`、转 `netlogin.S2CHello(netobj)`，并把该对象的 1 号处理
  替换为 `netlogin.S2CHello`；`S2CAttemptHello`（R144–R149）按 IP 取出
  尝试记录、删除后调用成功回调 `callback(netobj)`。
- 尝试管理：`ConnectAttempt`（R151–R156）以 IP 为键存
  `(callback, error_callback, netobj)`；`CAttemptNet.Run` 每帧
  `ProcessServerCmd()` 并递减 `m_Frame`，归零打印「连接超时」并 `Release`（R128–R134）；
  `Release` 删除记录并调用 `error_callback(self)`（R136–R142）。
  `ProcessServerCmd`（R72–R90）遍历未失败的 `g_NetobjList` 与尝试字典驱动 `Run`。
  帧数预算来自调用方传入的 `frame`（`DoConnect` 传 `g_DelaySecond=24`，R16/R164 起），
  「24」的单位是帧而非秒，变量名 DelaySecond 与实际单位不一致，须防误读。
- `DoConnect`（R164–R198）：`g_DelaySecond<=0` 直接走
  `main.RestarConfirmEx`；有代理时对候选表前两条各发一次尝试，
  无代理时按 `IsDianXin(net.g_Net.m_IP)` 选电信/网通候选（R200–R219 按
  `selectserver.ServerInfo()` 文本行判定，找不到默认 True）。
  静态异常点（须核对，不得当已证实 bug）：内嵌 `Success`（R171–R177，
  内容为 `ClearAttempt` 后 `main.RestarConfirm(...)`，且有
  `selectserver.g_Proxy` 赋值）在本稿中未被任何调用点引用，
  三处 `ConnectAttempt` 均把成功与失败回调都传为 `Fail`（R183–R198）；
  这与函数名语义矛盾，可能是反编译丢线或原文即如此，须回原生码对象核对，
  本包不断言真实胜出路径。
- 跨服：`KuaFuConnect`（R221–R231）/`NewKuaFuConnect`（R233–R245，后者先
  `GetKuaFuProxyLst` 重排候选）对每个 `(proxy, port, ip)` 建 `CMXNet`，
  置 `m_Hello=False, m_ReConnect=True, m_Idx, m_Pwd` 后 `ConnectServer`；
  胜出后如何用 idx/pwd 登录，处理在别模块（Hello 链），本文件未给出。
  `GetKuaFuProxyLst`（R247–R294）按代理名/登录区判电信(1)/网通(2)/教育网(3)，
  组合直连与代理候选；静态注意点：判型循环
  `for (field, tp) in field2type.items(): if ... else: nettype = 1`（约 R260–R265）
  在未命中分支每轮把 nettype 重置为 1，字典迭代序下结果可能被覆盖，
  属疑似原文/反编译问题，只登记待核。

### 3.3 错误分支（connect）

- `CMXNet.OnConnectFail/OnError`（R30–R44）用 `m_IsFail` 做一次性守卫：
  首次只打印并置位，第二次才上抛 `net.CNet.OnConnectFail/OnError`
  （后者会把 `g_Net` 换成 FakeNet 或走 ShowError，见 §2.4）。
  `CAttemptNet` 的同名回调则直接打印 + `Release`（R104–R112），
  经 `Release` 触发尝试失败回调。两类对象的错误语义不同，改动时不可混同。

## 4. 871 `script/netquicklogin.py`（仓库内候选与新恢复稿一致）

- 身份：entry 871，entry_id `696666009`（0x29864799），存储长 4481，pyc 长 8966。
- 仓库内来源：`tools/decompiler/output/script_fls/script/netquicklogin.py`，
  SHA-256 `36def1780a9bb229e98b850339eee91827ed6f6f972f330f52fa3f23183597b9`，307 行；
  仓库外新恢复稿 SHA-256
  `bee5c1a93c2c90f86a8f021eae086d44fa34bbdeb24df171c87388ed811a90e3`，313 行；
  diff 仅多恢复头 6 行，其余逐行一致。下文 R 行为恢复稿行号，仓库内行号 = R-6。
- catalog 第 872 行历史函数名与本稿定义集合一致。

### 4.1 职责与结构（quicklogin）

- 职责判断：断线「瞬连」（快速重登）——保存一次性 LoginKey、断线后按计时器
  反复尝试重连、Hello 后交 `main.RestartQuickLogin` 恢复会话；
  以及会话内 LoginKey 的收发与失效处理。
- 主要定义（R 行）：`ModuleReset` R24、`S2CLoginKey` R64、`S2CForceLoginOut` R73、
  `S2CQuickLoginFail` R83、`S2CDelLoginKey` R92、`S2CQuickLogin` R105、
  `C2SSendLoginKey` R117、`C2SRequestQuickLogin` R126、`CQuickNet(net.CNet)` R139、
  `S2CHello` R180、`NormalLogout` R192、`Connect` R206、`ClearConnectTimer` R230、
  `IsQuickConnect` R238、`CanQuickConnect` R242、`StartConnectTimer` R247、
  `ProcessServerCmd` R266、`StartQuickTimer` R272、`DoQuickLoginConnect` R286、
  `ClearQuickTimer` R296、`SetCanQuickLogin` R307；
  常数 `QUICKLOGIN_SECOND = 10`（R14）。

### 4.2 协议号、发送、接收与回调（quicklogin，分开取证）

- 接收（GS2C 方向）：本模块由 `net.py` 的 `NET_FUNCTION_NAME` 以
  `GS2C_QUICKLOGIN → netquicklogin.S2CQuickLogin` 注册（net.py R111 起字典内，
  键为符号）；3970 号表 `GS2C_QUICKLOGIN=12`（数值来自号表）。
  `S2CQuickLogin`（R105–R115）先 `UnpackInt(1)` 取子类型，
  再按 `FUNC_DICT`（R101–R103）分发：1=`S2CLoginKey`（再 `UnpackInt(4)` 取 key、
  `UnpackInt(1)` 取 itype 并保存 `g_LoginKey`，R64–R70）、
  2=`S2CForceLoginOut`（清 key、剧本中则停剧本，R73–R81）、
  3=`S2CQuickLoginFail`（置失败标志、`main.Restart()`，R83–R89）、
  4=`S2CDelLoginKey`（清 key，R92–R99）；未知子类型只打印「找不到函数」。
  子类型数值是本文件字面证据；服务端何时发哪一子型，未证实。
- 发送（C2GS 方向）：`C2SSendLoginKey`（R117–R124）与
  `C2SRequestQuickLogin`（R126–R137）都以符号 `net.C2GS_QUICKLOGIN`
  （3970 号表数值 13，来自号表）起包：前者加子型 1（1 字节）+ key（4 字节）；
  后者加子型 2 + key（4 字节）+ pid（4 字节，缺省取 `netserver.GetPlayerID()`）。
  函数名里的 C2S 只证明客户端发送意图，不证明服务端受理。
- Hello 回调：`CQuickNet.__init__` 注册 `m_NetFunction[1] = S2CHello`（R147，
  字面 1，号表 GS2C_HELLO=1）；本模块 `S2CHello`（R180–R190）清连接对象与
  计时器后调 `main.RestartQuickLogin(g_LoginKey, hero.g_ID)`。
  注意它先 `traceback.print_stack()` 打印调用栈（R182–R183），属调试残留形态，
  是否原样如此须核对，但不得据此改判 Hello 字段（字段不在本模块解包）。

### 4.3 连接、计时器与错误分支（quicklogin）

- `Connect(showdlg, sReason)`（R206–R228）从 `selectserver.g_Proxy/g_LastVisit`
  取上次地址，可选弹「网络异常断开，尝试重新连接中」框（取消回调
  `cancel` 清计时器并 `net.ShowError`），随后 `StartConnectTimer`。
  `StartConnectTimer`（R247–R264）以 `CreatePyCommand(30, done, 0)` 周期回调：
  计数 i>60 放弃并 ShowError；偶数次且无连接对象时新建 `CQuickNet` 尝试连接。
  30 与 60 的时间单位依赖原生 CreatePyCommand 语义，本文件未定义，不得写成秒。
- `CQuickNet.ConnectServer`（R162–R178）与 connect.py 同构：有代理先连代理并
  `NakedSend` 目标 IP 4 字节 + 端口 4 字节；无代理直连。
  `OnConnectFail/OnError`（R150–R160）只打印、清 `g_ConnectObj`（下个偶数周期会重试），
  不直接弹框——最终放弃由计数上限分支负责。
- 可瞬连判定：`CanQuickConnect` 需 `g_LoginKey` 且 `hero.g_ID`（R242–R245）；
  `IsQuickConnect` 返回计时器对象本身（真值判定，R238–R240）。
  `NormalLogout`（R192–R198）在有 key 且有网络对象时先 `C2SSendLoginKey` 再清 key。
- 静态异常点（须核对）：`StartQuickTimer`（R272–R284）写作
  `if g_oStartQucikTimer:` 才新建 `timer.Timer(QUICKLOGIN_SECOND, DoQuickLoginConnect, 1)`，
  而该全局在模块初始化（R16）与 `ModuleReset`（R34）中均为 None，
  本文件内无先行置真点；按字面读，首次调用不会启动计时器。
  这与函数名/调用点（main.py 两处调用）语义矛盾，可能是原文条件写反或
  反编译丢线，必须回码对象/实机核对，本包不断言其实际是否生效。
  `DoQuickLoginConnect`（R286–R294）仅当 `g_bCanDoQuickLogin` 为真时
  `Connect(False)` 并显示 loading。

## 5. 516 `script/login/netserver.py`（仓库内候选与新恢复稿一致）

- 身份：entry 516，entry_id `406718548`（0x183e0854），存储长 7690，pyc 长 17242。
- 仓库内来源：`tools/decompiler/output/script_fls/script/login/netserver.py`，
  SHA-256 `1fccc33d2d20540680c6af62e2bfdcf850291a855ed4bf626374262b8702c94b`，578 行；
  仓库外新恢复稿 SHA-256
  `569ceb2c7a3317b48cf95815bf5d16a77059e6fa1da66637fea3c29e964c5025`，584 行；
  diff 仅多恢复头 6 行。下文 R 行为恢复稿行号，仓库内行号 = R-6。
- catalog 第 517 行历史函数名与本稿定义集合一致。

### 5.1 职责与结构（netserver）

- 职责判断：登录前选服阶段的连接管理——服务器/代理候选状态、随机测连
  （多台并发试连、超时换批）、转服重连（reselect）、选服协议收发，
  以及经 `net.CHttpObject` 拉取服务器错误提示文案。
  它与 2170 connect.py 分工不同：本文件管「选哪台、测哪台」，
  connect.py 管「跨服/重登时多路尝试」；两者都有名为 `CMXNet`、
  `ProcessServerCmd` 的不同定义，不得混同（本文件 `CMXNet` 在 R280，
  connect.py 的在 R17）。
- 主要定义（R 行）：`ModuleReset` R14 及一组全局状态存取（玩家 ID R58、
  代理 R133–R187、登录服地址 R207–R222）、`RefreshServerInfo` R68、
  `SetServerRoleInfo` R189、`TransferServer` R224、`ShowConnectingDlg` R240、
  `S2CServerRoleInfo` R260、`C2STransferServer` R272、
  `CMXNet(net.CNet)` R280、`CConnectMgr` R314、`CRandomConnectMgr` R362
  （`GetTestProxyList` R380、`GetTestServerList` R398、`Connect` R426、
  `SetTimeOutCmd` R468、`ConnectTestFail` R479）、
  `CReselectConnectMgr` R489（`Connect` R498）、
  模块函数 `RandomConnect` R543、`ReselectServerConnect` R550、
  `DgwReselectServerConnect` R559、`NormalReselectServerConnect` R566、
  `ProcessServerCmd` R573。

### 5.2 协议号、发送与接收（netserver，分开取证）

- 接收：`S2CServerRoleInfo`（R260–R270）解包格式为
  计数 `UnpackInt(1)`，循环每项 `serverid=UnpackInt(4)` + `rolenum=UnpackInt(1)`，
  结果交 `SetServerRoleInfo`（R189–R201：若当前连接带 `m_ServerInfo` 且
  目标服可进或已有角色信息则直接 `TransferServer`，否则回登录界面流程）。
  该处理在 net.py 分发表中以符号 `GS2C_SELSERVER → netserver.S2CServerRoleInfo`
  注册（net.py 字典内）；3970 号表 `GS2C_SELSERVER=47`（数值来自号表）。
- 发送：`C2STransferServer`（R272–R278）以符号 `net.C2GS_SELECT_SERVER`
  （号表数值 41）起包，加 `serverid`（2 字节）后发送；
  `TransferServer`（R224–R238）先存登录服状态、写 `restartsave`、
  置 `SetSelectServerOver(True)`，再调它并弹连接中对话框。
  同样：客户端发送符号不证明服务端已切换或回包。
- 本文件内的连接对象 `CMXNet`（R280–R312）覆写
  `OnServerCmd`：仅当对象已有 `m_Hello` 属性时才转 `net.CNet.OnServerCmd`
  （R292–R295），这是测连对象在 Hello 前后行为的门闸；
  `m_Hello` 由别处（loginhello 链，E 样板外）在收到 Hello 后置位，
  本文件只置 False（R443、R516 等）。不得把「有 m_Hello 属性」写成「已握手」。

### 5.3 测连、代理、错误分支与配置（netserver）

- 随机测连：`CRandomConnectMgr.Connect`（R426–R467）取测试服列表
  （优先服或电信随机 5 + 网通随机 2，R398–R424）与代理列表
  （R380–R396，用户指定代理优先、`auto` 时置 `g_AutoProxy`），
  对每台建 `CMXNet(iType=loginhello.TEST_HELLO)` 并发连接（有代理则
  先连代理再 `NakedSend` 目标 IP 4 字节 + 端口 4 字节小端，与 §3.2 同构），
  弹连接中框、`m_Time += 1`、设 15 秒级超时命令
  `PROXY_CONNECT_TIMEOUT = 15`（类常数 R363，`SetTimeOutCmd` R468–R477
  以 `CreatePyCommand(15, nexttest)` 再次 `Connect` 换批）；
  尾行 `if self.m_Time - 1 != 0 or g_AutoProxy: self.Connect()`（R465–R466）
  使首轮在自动代理时立即再扩一轮，属须留意的行为形态。
  15 的单位依赖 CreatePyCommand 原生语义（netserver 连接管理器基类
  为 `interface.CBaseObject`），本文件未定义，不得径称秒数已证实——
  类名常数虽写作 TIMEOUT，亦只作字面登记。
- 全失败路径：`CConnectMgr.ConnectTestFail`（R326–R344）在
  `IsConnectTestFail()`（全部对象 `m_IsFail`，R354–R360）为真时，
  优先用 HTTP 拉到的 `g_ErrorAnsMsg`（按所选服名或 `default` 键）弹框，
  刷新计数 <3 时「确定」回调 `selectserver.Refresh`，并
  `loginin.CheckShowRefreshServer()`；随机管理器版本
  （R479–R487）先在未全试过时重置 `m_Time` 全量重试一次，再落基类逻辑。
  `CMXNet.OnConnectFail/OnError`（R297–R312）置 `m_IsFail` 并优先交
  `g_ConnectMgr.OnSocketConnectFail/OnSocketError`，无管理器时落
  `net.CNet` 默认错误处理（换 FakeNet/弹框，见 §2.4）。
- 转服重连：`ReselectServerConnect`（R550–R557）按 `main.g_IsDgwConnect`
  分 DGW 路径（`dgwconnecttest.ConnectTest`，R559–R564，DGW 本体不在样板内）
  与普通路径 `CReselectConnectMgr`（按 serverID 在非推荐区找目标、
  带 `(idx, pwd)` 凭据 `m_PassPort`、有代理走代理裸发，R498–R541）。
  `ProcessServerCmd`（R573–R584）遍历管理器对象收包，任一 `m_Hello` 为真即 break。
- 配置面：代理设置经 `SetProxy` 写 `mx.ini [Game] proxy`（R149–R159，
  写失败吞异常）；测连刷新节流读 `mx.ini [Game] refreshserver` 时间戳，
  超 1200 秒才再刷（R68–R79）；错误文案 URL 读
  `update.ini [Setting] BulletinURL` 经 `net.CHttpObject(web, 'get', getMsg)`
  拉取并按 `serverid:文案` 行解析（R81–R101，解析失败吞 ValueError）。
  服务器/代理候选本体来自 `selectserver.GetServerInfo()`（区名、ip、port、
  serverid、代理 ipPort/type），该模块不在 E 样板内，其数据文件格式未在本包核对。

## 6. 跨模块关系与缺失总表（E 样板）

- 已静态确认的 Python 层链（只到符号调用，不含原生与服务端）：
  `main.MainLoop`（4293，协审另述）每帧依次驱动
  `net.g_Net.ProcessServerCmd`、`netserver.ProcessServerCmd`、
  `connect.ProcessServerCmd`、`netquicklogin.ProcessServerCmd`；
  `net.CNet.OnServerCmd` 按号动态导入目标模块处理函数；
  `connect.S2CHello`/`netquicklogin.S2CHello` 在 Hello 后分别转
  `netlogin.S2CHello`/`main.RestartQuickLogin`；
  `netserver.TransferServer → C2STransferServer` 为选服发送点。
- 明确缺失/未证实（不得补写）：原生 `C_net` 的套接字、帧状态机、加解密
  （SetSeed 等）实现；帧续读 2/3 字节冲突（§2.3）；全部 GS2C/C2GS 数值的
  服务端语义与回包；`protocol.py`（3970）号表与本 4 文件符号的一致性
  未做全量逐项核对（只抽查了正文引用符号）；`NET_FUNCTION_NAME` 字典
  指向的约二百个目标模块/函数是否都存在于冻结包，未逐项验证；
  219 号 GS2C 语义名缺失；`loginhello`、`selectserver`、`netlogin`、
  `whitewebsite`、`dgw*` 等上下游模块不在 E 样板内，仅按调用符号登记；
  所有计时常数（24 帧、30/60 计数、15、10、0.016 秒、CreatePyCommand 单位）
  的真实时间含义依赖原生调度，未实机测定；三处静态异常点
  （队列低优先赋值、DoConnect 的 Success 未引用、StartQuickTimer 条件）
  未回码对象复核，可能是反编译错误而非原文缺陷；
  无任何实机/抓包证据，本包全部结论最高为 static_reviewed。
