# Connect -> Empty Map 状态机草稿

## 文档定位

- case: `dream-world-connect-login-map`
- 工作目录: `D:\Lager\夢想世界\work\dream-world-connect-login-map`
- 样本根目录: `D:\Lager\夢想世界`
- 编写日期: `2026-10-09`
- 状态: 假设草稿，未完成协议确认
- 网络约束: 仅使用当前目录中的离线文件；本草稿不连接网络

本文把“客户端从启动到进入空地图”的路径拆成可验证状态。状态名称和顺序来自当前文件名、日志、配置字段及二进制字符串线索；它们不是已确认的协议消息名。

## 当前证据摘要

### 已观察到的本地线索

| 线索 | 当前观察 | 对状态机的意义 |
|---|---|---|
| `log/game/gamelog_2026-10-09 09-18-40.txt` | 记录 `login/mainpage.dlg`，随后记录 `login/multi_selserver5.dlg` | 支持登录主界面与服务器选择界面至少存在一次 UI 状态转移 |
| 同一游戏日志 | 启动后报告 OpenGL 初始化失败，随后在约 `09:33:14` 关闭游戏 | 当前运行记录不能证明已完成连接、登录、角色选择或进图 |
| `server.ini` | 含服务器名、多个地址、端口 `3134` 及附加字段；文件编码显示为非 UTF-8/本地编码 | 支持 Server Select 使用本地服务器列表，并可能把选中项映射为地址、端口和分区参数 |
| `mx.ini` / `mxbak.ini` | `[Login] lastserver=...`，以及 `refreshserver=...` | 支持“最近服务器”持久化和服务器列表刷新相关状态 |
| `IMProtocol.dll` | 可读字符串集中出现 `Connect`、`Server`、`Map` | 支持存在独立的连接/服务器/地图协议或处理层；字符串本身不等于调用顺序 |
| `mxmain.dll` | 可读字符串集中出现 `Login`、`Connect`、`Server`、`Ready`、`Character`、`role`、`scene`、`Map` | 支持把登录、角色/世界就绪、场景/地图加载作为候选状态边界 |
| `gameplayer.exe` | 可读字符串出现 `Character`、`Server`、`Map` | 支持游戏进程或游戏层参与角色/地图阶段 |
| `map\*.map` | 当前目录存在约 101 个 `.map` 文件 | 支持本地地图资源阶段；尚未证明某个编号就是进入空地图时的目标地图 |
| `data\*.fls` | 存在 `map.fls`、`mapobject.fls`、`minimap.fls` 及角色/资源包 | 支持地图和对象资源可能在进图前后分阶段加载 |

### 尚未具备的关键证据

- 没有离线抓包、协议帧、消息编号、长度字段或序列化结构。
- 没有成功登录的客户端日志，也没有可确认的角色列表/角色选择记录。
- 没有确认 `server.ini` 的附加字段 `3 &` 的语义。
- 没有确认 `Ready` 是网络握手完成、角色数据完成、场景加载完成，还是 UI/渲染层标志。
- 没有确认“Empty Map”是实际空场景、地图资源未加载、地图对象为空，还是进入世界后的可见结果。
- 当前启动日志包含 OpenGL 初始化失败，因此 UI 日志只可作为启动路径证据，不能直接当作成功状态证据。

## 假设状态机

```text
S0 Process Start
  -> S1 Connect
  -> S2 Server Select
  -> S3 Login
  -> S4 Character/World Ready
  -> S5 Empty Map

任一状态
  -> F0 Local Init / Render Failure
  -> F1 Disconnect / Timeout
  -> F2 Protocol Reject / Auth Failure
  -> F3 Resource or Scene Load Failure

S2 --server list unavailable--> S1 or F1
S3 --credential/session reject--> S2 or F2
S4 --character/world data incomplete--> S3 or F3
S5 --map/object load incomplete--> S4 or F3
```

### S0 - Process Start / Login Main Page

**假设含义**

- 客户端进程启动，读取本地配置，初始化窗口、声音、渲染和登录 UI。
- 进入 `login/mainpage.dlg`，等待服务器列表、账号输入或已有服务器选择。

**支持证据**

- `log/game/gamelog_2026-10-09 09-18-40.txt` 中出现 `login/mainpage.dlg`。
- 同一日志记录 `style=2`、OpenGL 检测和 `GameStart` 过程。
- `mx.ini` / `mxbak.ini` 含 `[Game]` 和 `[Login]` 区段。

**需要的确认**

- `mainpage.dlg` 的加载是否等价于网络连接尚未开始。
- `refreshserver` 的读取时机，以及是否在 UI 创建前触发服务器列表刷新。
- `lastserver` 是否只影响默认选择，还是会直接触发连接。

**后续检查**

- 在不改样本的前提下定位 `mainpage.dlg` 的资源来源和调用者。
- 对比冷启动、已有 `lastserver`、清空 `lastserver` 三种本地配置路径。
- 记录从进程启动到 `mainpage.dlg` 的调用时间线。

### S1 - Connect

**假设含义**

- 客户端根据本地服务器配置或刷新结果，建立到登录/服务器服务的连接。
- 连接可能先到列表服务，再转到选中的游戏服务器；当前材料无法区分这两种拓扑。

**支持证据**

- `server.ini` 含多个服务器项、地址和端口 `3134`。
- `IMProtocol.dll` 与 `mxmain.dll` 都有 `Connect` / `Server` 字符串。
- `mxmain.dll` 有大量 `connect` / `ready` 相关字符串，但尚未建立函数、交叉引用或调用顺序。

**需要的确认**

- `3134` 是列表服务、登录服务还是游戏服务端口。
- 是否存在第二个端口或服务端返回的重定向地址。
- 连接建立后第一个客户端发送/接收的数据是什么，是否有版本、时间戳、客户端标识或握手字段。
- 连接失败时 UI 是停留在主界面、切换服务器选择，还是直接退出。

**后续检查**

- 静态定位 `server.ini` 解析函数、地址/端口读取点和 socket 创建点。
- 以本地离线分析方式确认 `IMProtocol.dll` 的导出、导入、RTTI/日志字符串引用。
- 为每个候选连接函数记录模块、函数地址、调用者和输入参数形态。

### S2 - Server Select

**假设含义**

- 客户端显示服务器选择界面，加载本地或缓存的服务器列表。
- 用户选择一项；选中项至少包含名称、地址、端口和一个附加字段；结果写入或更新最近服务器状态。

**支持证据**

- 日志在 `09:18:55` 出现 `login/multi_selserver5.dlg`。
- `server.ini` 有多条服务器记录和 `3134` 端口。
- `mx.ini` / `mxbak.ini` 保存 `[Login] lastserver`。

**需要的确认**

- `multi_selserver5.dlg` 是列表展示、分区选择，还是连接中间页。
- `server.ini` 每行字段的精确编码与语义，尤其是末尾的 `3 &`。
- `lastserver` 保存的是显示名、索引、完整地址，还是编码后的复合值。
- 服务器选择后是否立即进入 Login，还是先进行一次列表/版本/公告请求。

**后续检查**

- 以只读方式提取 `server.ini` 原始字节，按候选本地编码重解码并保留原始字节校验值。
- 在 `mxmain.dll` 中追踪 `lastserver`、服务器列表 UI 和 `multi_selserver5.dlg` 的引用关系。
- 将每个服务器项整理为：显示名、地址、端口、附加字段、来源文件、置信度。

### S3 - Login

**假设含义**

- 客户端向选定服务器提交账号/会话凭据及客户端版本或校验信息。
- 服务端返回登录成功、失败、需要重试或角色/世界入口信息。

**支持证据**

- `login/mainpage.dlg` 和 `Login` 字符串共同支持登录层存在。
- `mxmain.dll` 中同时出现 `LogIn`、`Login`、`Server`、`Connect`。
- `server.ini` 的服务器列表与 `[Login]` 配置表明登录前存在服务器上下文。

**需要的确认**

- 登录凭据是明文字段、加密字段、摘要、令牌还是本地会话引用。
- 登录成功响应是否直接携带角色列表，或先返回世界/分线服务器。
- `LogIn` 与 `Login` 是否是不同命令、不同 UI 事件或仅为大小写变体。
- 失败码、重试次数、超时和返回路径如何映射到 UI。

**后续检查**

- 先从静态字符串引用和导出关系入手，定位登录请求构造、响应分派和错误码表。
- 记录候选数据结构的字段边界、长度来源、字节序和校验方式；未知字段统一标为 `UNKNOWN_n`。
- 不把字符串邻近关系当作协议顺序，必须由调用图、状态字段或日志顺序交叉确认。

### S4 - Character / World Ready

**假设含义**

- 登录成功后，客户端取得角色列表或角色选择结果，并收到进入世界所需的角色、场景、地图和会话状态。
- `Ready` 表示进入下一阶段的门槛；具体是“角色数据就绪”还是“世界连接就绪”待确认。

**支持证据**

- `mxmain.dll` 中集中出现 `Character`、`role`、`scene`、`Ready`、`Map`。
- `gameplayer.exe` 中出现 `Character`、`Server`、`Map`。
- 本地存在大体量角色资源及 `data\char.fls`、`hero*.fls`。

**需要的确认**

- 是否存在独立的角色选择状态，还是自动选择最近角色/首个角色。
- 角色列表和世界入口是否来自同一连接。
- `Ready` 的设置点、清除点和依赖条件是什么。
- 世界准备阶段是否会先下载/解包地图对象、角色外观和初始坐标。

**后续检查**

- 在 `mxmain.dll` 与 `gameplayer.exe` 中分别寻找 `Ready`、`Character`、`role`、`scene` 字符串引用。
- 识别角色 ID、地图 ID、实例/分线 ID、初始坐标等候选字段。
- 将“登录成功”“角色数据完整”“地图资源可用”“渲染就绪”拆成独立布尔条件，不合并为单一 Ready。

### S5 - Empty Map

**假设含义**

- 客户端已通过连接、服务器选择、登录和角色/世界准备，开始进入目标地图。
- 画面或内部状态呈现“地图容器已建立但地图对象/角色/场景内容为空或未完成”的结果。

**支持证据**

- `mxmain.dll` 中存在 `Map`、`scene`、`ready` 相关字符串。
- 本地存在 `map\*.map`、`data\map.fls`、`data\mapobject.fls`、`data\minimap.fls`。
- `d2drender.dll` 中出现 `Scene` / `map` 相关字符串。

**需要的确认**

- “Empty Map”是观察到的实际结果，还是任务目标中的待达成状态。
- 空地图对应哪个地图 ID、文件名、场景类型或默认坐标。
- 空地图是资源未加载、服务端未下发对象、角色不可见，还是渲染初始化失败的表象。
- 进入空地图后客户端是否仍保持 socket 活跃并发送心跳/ready/场景确认。

**后续检查**

- 建立地图编号、`.map` 文件、地图包资源和场景 ID 的映射表。
- 静态追踪地图加载入口、对象列表解析、角色生成和场景切换条件。
- 将“无对象但地图背景存在”“地图文件未打开”“渲染窗口空白”“连接已断开”分别定义为不同结果。

## 状态转移与证据门槛

| 转移 | 最低证据门槛 | 当前状态 |
|---|---|---|
| S0 -> S1 | 找到连接触发点，或有明确连接尝试日志 | 候选，未确认 |
| S1 -> S2 | 服务器列表请求/响应或服务器选择 UI 的触发关系 | UI 已见，协议未确认 |
| S2 -> S3 | 选中服务器后的登录请求或状态变量变化 | 候选，未确认 |
| S3 -> S4 | 登录成功响应、角色列表/角色 ID、世界入口字段 | 未确认 |
| S4 -> S5 | 地图/场景 ID、地图资源加载完成、空地图可重复观察 | 未确认 |
| 任意 -> F0 | 明确初始化错误与状态中断的时间关联 | 启动日志已有 OpenGL 错误 |
| 任意 -> F1/F2/F3 | 可重复的错误码、断开点或资源加载失败点 | 未确认 |

## 待验证问题总表

1. `server.ini` 的字段编码、字段语义和服务器列表刷新来源是什么？
2. 端口 `3134` 对应哪个服务阶段，是否存在服务端重定向？
3. `multi_selserver5.dlg` 出现前后是否有网络/协议状态变化？
4. `lastserver` 如何影响默认服务器选择和连接入口？
5. 登录请求和响应的消息边界、版本字段、校验字段、错误码是什么？
6. 角色列表、角色选择、世界入口是否由一个响应完成？
7. `Ready` 在哪个模块、哪个调用路径设置，依赖哪些条件？
8. 地图 ID 如何映射到 `map\*.map` 和 `data\*.fls` 中的资源？
9. 空地图现象是否可与 OpenGL 初始化失败、地图资源未加载和服务端空对象列表区分？
10. 当前唯一运行日志是否因渲染失败而在到达网络阶段前终止？

## 后续接手者检查清单

### 文件与证据登记

- [ ] 阅读并补充 `scope.md`、`timeline.md`、`workitems.md`，不要覆盖已有内容。
- [ ] 为本草稿引用的关键文件生成证据条目，使用 case 约定的 `E-*` 编号。
- [ ] 记录每个分析输入的路径、SHA-256、读取方式和本地时间。
- [ ] 保留原始样本与原始配置；分析输出放在 `evidence/` 或 `notes/`。

### 静态分析

- [ ] 从 `mxmain.dll`、`IMProtocol.dll`、`gameplayer.exe` 开始做导入/导出、字符串引用和调用关系整理。
- [ ] 定位 `Connect`、`Login`、`Ready`、`Character`、`scene`、`Map` 的函数级引用，而不是只记录字符串命中。
- [ ] 定位 `server.ini`、`mx.ini`、`mxbak.ini` 的读取和写回函数。
- [ ] 建立服务器项、角色/世界字段、地图字段的候选结构表，未知字段保留占位名。

### 离线动态或重放准备

- [ ] 先确认当前日志中的 OpenGL 错误是否阻断了网络和游戏层初始化。
- [ ] 设计不联网的本地观察方案：日志、文件访问、状态变量和资源加载调用的时间线。
- [ ] 如已有离线数据，按原始字节保存候选消息；不要把猜测字段写回样本或配置。
- [ ] 每个状态至少记录进入条件、离开条件、成功标志、失败标志和可观察副作用。

### 结果判定

- [ ] 将“进入登录 UI”“建立连接”“登录成功”“角色/世界就绪”“地图容器创建”“空地图可见”分别判定。
- [ ] 为每个判定附至少一个直接证据和一个独立交叉证据。
- [ ] 对未确认的协议顺序使用“假设”标签，不升级为 finding。
- [ ] 更新 `timeline.md` 与 `workitems.md`，并在报告中引用最终证据链。

## 结论（当前置信度）

当前最稳妥的工作模型是：

1. 客户端启动并进入 `login/mainpage.dlg`；
2. 通过本地服务器配置或刷新结果进入 `login/multi_selserver5.dlg`；
3. 选择服务器后进入登录处理；
4. 登录成功后加载角色/世界状态；
5. 依赖地图和对象资源进入目标场景，空地图是待确认的末端表现。

其中第 1、2 步有直接日志/配置支持；第 3 步有模块字符串和配置上下文支持；第 4、5 步目前主要由字符串和资源命名支持。现有启动日志中的 OpenGL 错误使“完整流程已经跑通”的结论不成立，后续接手者应优先解决状态可观测性和证据登记问题。


## Ghidra update: S1 connection implementation (2026-10-09)

REA-Ghidra/Ghidra 12.1.4 static analysis has now traced `IMProtocol.dll`'s `IMP_ConnectNsServer` export through `FUN_10001660` and `FUN_10005cb0` to a socket-object connection method. The direct numeric-address branch constructs an IPv4 socket address, applies `htons` to the port field, and calls the Winsock `connect` import. A hostname branch passes message `0x502` to a WS2_32 ordinal; a separate initializer registers socket notifications at message base `context+0x503` with mask `0x3f`. See [`E-REA-002`](../evidence/E-REA-002.md).

**State-machine impact:** this raises confidence that the DLL contains a TCP connection implementation, but it does not prove the main client calls it, that the selected `server.ini` endpoint is used by this path, or that this connection is the game-login channel rather than an auxiliary service. The main-image IAT xref queries returned no direct code references, and the async completion dispatcher is not yet located. Therefore S0 -> S1 remains a candidate, S2 -> S3 remains unconfirmed, and no login, character/world-ready, or empty-map state is promoted to observed.

**Historical next offline checks (superseded by the stop record below):** resolve the `0x502`/`0x503` message handler; inspect indirect or dynamically resolved main-image call paths into the imported API; then trace any message-writer/send callers and relate them to server selection. No client launch or external connection was performed in that analysis phase.

## Current handoff and stop state (2026-10-09; E-USER-001, E-REA-008)

**Observed UI boundary:** the user's earlier report says either selecting a server directly or clicking “Next” opens the “Connecting to server” dialog. This establishes `S2 Server Select -> S2C Connecting Dialog`; it does not establish that the client sent application data, received a server response, or reached the account-credential page (`S3`). The historical loopback capture is not proven to be the same interaction. See [`E-USER-001`](../evidence/E-USER-001.md) and [`E-LOOPBACK-001`](../evidence/E-LOOPBACK-001.md).

**Script-payload correction:** the latest user-provided analysis handoff reports that entry 516 of `data/script.fls` now parses, after five XOR layers, as a complete Python 2.7 marshal tree containing 59 code objects, including `CMXNet.OnServerCmd`, `ProcessServerCmd`, and `C2STransferServer`. The earlier failure came from incorrect decompiler argument order. The tree's `co_code` still uses a second, non-standard opcode encoding; the pre-execution conversion layer, command conditions, and S2 -> S3 transition remain unresolved. The candidate `render.dll` `Py_Uncompress` path through `ResLib.dll` ordinals 13/12 does not match entry 516's data header and is not confirmed as its loader. See [`E-REA-008`](../evidence/E-REA-008.md); this is recorded from the handoff and was not re-run during this documentation-only task.

| Transition | Current evidence status |
|---|---|
| S2 -> S2C Connecting Dialog | User-reported observation; recorded in E-USER-001 |
| S2C -> S3 Account/Credential Login | Unresolved; no exact command condition, required response, or confirmed code-object execution path |
| S3 -> S4 -> S5 | Unconfirmed, as in the earlier draft |

**Stop boundary:** per the user's explicit instruction, further binary/game analysis and any forced-entry patch or runtime test are paused. The original `mx.exe` was not modified, and no forced-entry copy was created. Resume only after a new explicit user request.
