# 交接文档：给后续 agent（2026-10-10 晚）

> 本文件是接手说明，覆盖 `HANDOVER-20261010.md` 之后的进展。旧交接文档中的部分表述已被 `report/verification-20261010.md` 修正，以那份为准。

## 1. 一句话状态

客户端连接链路仍未打通。已证实：TCP 能连上 `127.0.0.1:3134`，但连接后没有应用层字节发出。密钥计算链的结构已弄清，但种子来源未知。静态分析的四个子任务（P1–P4）已合并。Windows 观察器跑过一次，**没有命中任何 IMP 函数，且客户端在点击“刷新列表”后连接了外部 HTTP 地址**（E-OBS-001，范围偏离）。下一步需要用户决定防火墙策略，并提供原始日志。

## 2. 仓库与分支（先看这里）

- 工作分支：`arena/febc1561-mxsj-tw-2022`。**只在这个分支上工作，只推送到它。**
- 当前 HEAD：`f248c96`，与 `origin/arena/febc1561-mxsj-tw-2022` 一致。
- 没有打开的 PR。已合并：#6（P1）、#7（P2）、#8（P4）、#9（P3，含 `tools/dis_v43/`，用户明确保留）。
- **没有暂存记录**。之前的 `stash@{0}` 和 `/tmp/local-backup-20261010/` 在一次环境重建后都不存在了。我们核对过，那些内容已全部在远端分支里，没有丢失。
- **推送前必须先检查分叉**：`git fetch origin`，然后比较 `git log origin/…..HEAD` 与 `HEAD..origin/…`。2026-10-10 曾因本地分支基于旧的 `ffec3d9` 而几乎推送了一个会删除 `tools/dis_v43/` 的提交，最后用 `git reset --mixed origin/…` 修正。**禁止 force push。**
- 不要创建或切换到其他分支。

## 3. 用户确认过的约束（不得违反）

1. 不删除任何文件（包括 `git rm`、移动或 `git rm --cached`）。唯一例外：用户已批准删除的 `tools/mock-server-logs/mock-server-20261010-094859.log` 及其空目录，已完成。
2. 变更范围限于文档。不修改游戏文件（`mx.exe`、`mxmain.dll`、`IMProtocol.dll`、`gameplayer.exe`、`DuoyiProtect.dll`、`server.ini`、`mx.ini` 等）。不修改已有的工具代码。`tools/dis_v43/` 是用户明确要求保留的新增工具，不是修改。
3. 游戏二进制和资源保留在 Git 中（WI-014 记录的决定），不移出、不 `--cached`。
4. `server.ini` 保留 `127.0.0.1 3134` 回环条目，**不恢复** `caa7996` 的 `.205` 版本。文件中还保留着 `203.70.8.207/.206/.204/.198` 外部条目。
5. 范围（`scope.md`）：自有副本、离线、只读分析、只绑定 127.0.0.1。**不得让原版客户端连接外部服务器。** 2026-10-10 的 E-OBS-001 违反了这一点（见第 6 节）。
6. 地图 GUI 的 png 提示问题：用户说先放一边。

## 4. 已证实的事实（可直接引用）

| 项 | 内容 | 依据 |
|---|---|---|
| 文件哈希 | `mx.exe` 与 `mxmain.dll` 字节相同，SHA-256 `637331b54f7fa9fa6c236fa7f9ac8a8b27f228bd46d05046fdccddf52fbe424d`；`IMProtocol.dll` SHA-256 `bc356c88a6470d761b8976f8c027056b8c0e0f483ca2f59cf5c42542e112c82c` | P1 §2，E-OBS-001 |
| 导出地址 | `IMP_RefreshCryptKey` `0x10003110`；`IMP_SendBuffer2NS` `0x10003240`；`IMP_EncryptBuffer` `0x100031f0`；`IMP_UnConnectNsServer` `0x100030d0` | PE 导出表核对 |
| 密钥链（P1） | `IMP_RefreshCryptKey` 把输入 C 字符串（长度 ≥ 8）交给 `0x10001770`，按 `%02X` 八次解析成 8 字节种子；再由 `0x10005b80` 对两个 12 字节上下文做 S 盒链式变换（8 张表与 `key_sbox_0..7.bin` 逐字节相同）。 | P1 |
| 密钥未知项 | 调用者、种子来源（本地常量／配置／服务器）、是否依赖服务器首包：**均未证实**。未推算任何密钥值。 | P1 §6 |
| 发包路径（P2） | `IMP_SendBuffer2NS`（`0x10003240`）→ `0x10001AA0` → `0x10005F80` → socket vtable → `ws2_32!send`（IAT `0x1001F1A8`）。DLL 内部没有等待服务器首包的判断。 | P2 |
| 主客户端调用者 | `mx.exe` 导入了 `IMP_SendBuffer2NS` 和 `IMP_RefreshCryptKey`，但**调用点未找到**，不能证明会／不会调用。 | P1 §6，P2 §1 |
| 连接流程（P3） | 直连分支**没有**连接前的 NakedSend。代理分支在 `Connect(代理)` 之后发 8 字节（4 个 IP 八位组 + 4 字节小端端口；3134 为 `3E 0C 00 00`）。`'127.0.0.1'.split('.')` 正确，结果只用于代理分支。 | P3 §3.2–3.3 |
| 超时（P3） | `PROXY_CONNECT_TIMEOUT = 15`（数值已证实，单位未证实）。超时后 nexttest 前移代理候选、重洗服务器列表。 | P3 §3.4 |
| 原 H3/H4 | H3（单字节被丢弃）前提不成立；H4（IP 拆分错误）不成立。建议作废。 | P3 §4 |
| 外部 HTTP | 点击“刷新列表”后，客户端连接 `150.230.97.144:80`、`158.101.159.192:80`。 | E-OBS-001（agent 报告，原始文件未入库） |
| 10-09 回环 | 22 个 stream 文件全为 0 字节；服务端日志 4 次 accept，均由客户端关闭。 | E-LOOPBACK-001/002 |
| 10-10 回环 | 用户口头报告仍为 0 字节，未附文件。 | E-LOOPBACK-003 |

## 5. 假设状态（`notes/loopback-test-plan-20261010.md`）

| 编号 | 状态 |
|---|---|
| H1 服务端先发才发 loginhello | **未证实**（P4 判为无法判断；P2 反对 DLL 内部等待，但调用者未闭合） |
| H2 超时后切换候选 | 静态部分证实（参数与重连路径）；运行时未验证 |
| H3 单字节被丢弃 | **前提不成立**，建议作废或改写 |
| H4 IP 拆分错误 | **不成立**，建议作废 |
| H5 登录走其他通道 | 未检验（需要记录全部 TCP 连接） |

**关键推断（未证实）**：如果测试走直连，连接后不发字节是正常的，问题变成“什么事件触发第一包”。如果走代理，理论上会先发 8 字节，但 P3 指出 `Connect` 可能是异步的，因此不能据此否定代理分支。下一次测试必须确认走的是哪条分支。

## 6. 观察器与 E-OBS-001

- 草稿位置：`notes/observer-20261010/`（`observe.js`、`observe.py`、`AGENT-brief-windows.md`、`步骤.md`）。
- `observe.js` 已修复 Frida 17 兼容问题（`Process.findModuleByName('ws2_32.dll')`），语法检查通过。Windows 上 agent 的版本是这一修复的先行版，已同步。
- 2026-10-10 20:28–20:43 的首次运行（agent 报告）：
  - 挂载成功，8 个 hook 安装，无 missing；
  - IMP 函数 0 次调用，`ws2_32.send` 0 次；
  - `ws2_32.connect` 2 次，均为外部 HTTP 80 端口，发生在点击“刷新列表”之后；
  - 界面停在“伺服器選擇”，弹窗“獲取服務器列表中...”，未选中任何条目。
- **范围偏离**：agent 点击了刷新列表。任务书已加入“禁止点击刷新/远程请求按钮”的规则。
- 未知：HTTP 请求的内容（hook 只覆盖了 `send`，未覆盖 `WSASend` 等）；服务器列表的来源；为什么 10-09 的测试能直接连到 3134，而这次要先刷新列表。
- agent 报告的原始文件（`observe-log.jsonl` 1171 字节、`gamelog_2026-10-10 20-28-35.txt` 730 字节、`tasklist.txt`、截图）**尚未进入工作区**，需要用户提供。

## 7. 等待用户的事项（不要替用户决定）

1. **防火墙**：是否阻止 `150.230.97.144`、`158.101.159.192` 和 `203.70.8.0/24` 的出站连接。这是系统设置改动，由用户决定。
2. **原始日志**：请用户提供 `observe-log.jsonl` 全文、游戏日志和 `tasklist.txt`，然后核对 E-OBS-001 的 agent 摘要。
3. **是否再跑一次观察器**：如果要跑，先要搞清楚服务器列表如何出现、回环条目如何被选中；运行前要求 agent 不点刷新，只记录列表出现的过程。
4. 之前提议但**尚未派发**的任务：P5（C→S 命令字来源，WI-013）、P6（未知 opcode 口径，WI-016）、P7（修悬空引用与过度“完成”表述，WI-015/017，应在 P5/P6 之后做）、P8（找出 `IMP_RefreshCryptKey` 与 `IMP_SendBuffer2NS` 在 `mx.exe` 里的真实调用者，**最关键**）。是否派发由用户决定。
5. 地图 GUI 的 png 提示问题：用户说先放一边，不作为当前任务。

## 8. 建议的下一步（按优先级）

1. 等用户回复第 7 节的事项，不要自行运行任何会连接网络的操作。
2. 收到原始日志后，核对 E-OBS-001：确认 connect 目标、有没有 send、IMP 是否命中，把 agent 摘要替换为已核对的事实。
3. 若用户同意派发：优先 P8（调用者），然后 P5、P6；P7 最后做。
4. 静态工作可以在不连网的情况下继续：例如 P3 中“55 唯一解 / 3 无解 / 1 双解”的统计尚未核对，可以在 `/tmp` 下重跑 `tools/dis_v43/dis_v43.py`（只读，不要写入仓库）。
5. 修正 `notes/protocol-artifacts/im_crypto.py` 中第 188 行的地址（应为 `0x10003110`），但**要先取得用户同意**，因为它是代码文件。目前只在 `notes/protocol-artifacts/README.md` 中记录了问题。

## 9. 已知陷阱（不要重复）

- 中文文件名在 `tar`、`git status` 中会被转义；用 `git ls-files -z`、`tar --null -T -` 处理。
- `git commit` 的路径要用仓库相对路径，并在 `work/dream-world-connect-login-map` 内或完整路径下执行。
- 推送前先检查本地与远端是否分叉（见第 2 节）。
- Frida 17 不支持 `Module.findExportByName` 静态调用，要用 `Process.findModuleByName(...).findExportByName(...)`。
- 游戏是 32 位，观察器必须用 32 位 Python。
- 不要把密钥相关字节写进聊天或文档；回报只写“是否调用”和长度。MAC 地址等本机标识也不写入回报。
- `tools/test-data/`、`docs/`、`tools/mock_server_v2.py`、`task-briefs/TASK-X-xxx.md` 不存在，不要再引用。
- `all_scripts_catalog.json` 只有 11 条记录，不是 5002 条。全量目录用 `notes/task-b-脚本分析/artifacts/script-catalog.csv`。
- `mock_server.py` 运行时会在 `tools/mock-server-logs/` 生成日志。
- E-TOOLS-001 的结论是错误的，不是有效证据。
- P3 的“55 唯一解 / 3 无解 / 1 双解”统计尚未核对。

## 10. 未证实清单（汇总）

- 密钥种子来源与调用者（WI-010）
- `IMP_SendBuffer2NS`、`IMP_RefreshCryptKey` 在主客户端中的调用点（P1、P2）
- H1（服务端先发）
- 直连还是代理分支（测试时实际走的哪条）
- `PROXY_CONNECT_TIMEOUT` 的单位
- `NakedSend` 原生实现的位置、`CNet.Connect` 是否异步（P3 §7 #4、#8）
- 服务器列表的来源（外部 HTTP 或本地配置）
- C→S 命令字数值（WI-013，`protocol-commands-values.md` 中的数值未证实）
- loginhello 样本的出处（`tools/test-data/` 不存在）

## 11. 相关文件索引

- 结果：`notes/parallel-20261010/P1-result.md` 至 `P4-result.md`；任务书与协调表在同目录。
- 观察器：`notes/observer-20261010/`；证据 `evidence/E-OBS-001.md`。
- 回环：`evidence/E-LOOPBACK-001.md`、`E-LOOPBACK-002.md`、`E-LOOPBACK-003.md`；计划 `notes/loopback-test-plan-20261010.md`。
- 工具：`tools/dis_v43/`（P3 工具，用户保留）；`tools/loopback_capture_server.ps1`、`enhanced_capture_server.py`、`mock_server.py`（用途见 `tools/README.md`）。
- 核对报告：`report/verification-20261010.md`；时间线 `timeline.md`；工作项 `workitems.md`。
