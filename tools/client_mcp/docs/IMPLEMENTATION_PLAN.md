# 实施计划草案

> 状态：M2 完成（探针在 Windows 客户端内执行并写报告）；M3 只读 MCP Server 已实现（stdio 实测通过、本机 HTTP 待实机）；**M4 与 M5 尚未开始**。日期：2026-11-03。

## M0：目录与文档

目标：先把架构、边界、协议草案、输入交付流程写清楚。

交付：

- `tools/client_mcp/README.md`
- `docs/ARCHITECTURE.md`
- `docs/PROTOCOL.md`
- `docs/MCP_CLIENTS.md`
- `docs/SECURITY.md`
- `docs/SCRIPT_FLS_HANDOFF.md`
- `docs/WINDOWS_ACCEPTANCE.md`
- 本计划
- 子目录占位 README

不做：

- 不写可运行 MCP Server；
- 不写客户端探针；
- 不改 `script.fls`；
- 不启动 Mock；
- 不宣称可连接。

## M1：用户修改版输入核对

前置：用户提供修改版 `script.fls`。

目标：

1. 输入登记；
2. SHA-256 / 大小 / 来源记录；
3. 只读条目清点；
4. 与原始基线差异报告；
5. 确认 key DB 是否适用；
6. 确认探针候选挂点。

交付：

```text
../mxsj-client-mcp-out/inputs/<timestamp>/input_manifest.json
../mxsj-client-mcp-out/reports/<timestamp>/inventory.json
../mxsj-client-mcp-out/reports/<timestamp>/diff_from_locked_baseline.json
```

门槛：

- 不覆盖原始包；
- 不执行恢复脚本；
- key DB 不匹配时停止并报告。

## M2：客户端只读探针

目标：在客户端测试副本内加载自写探针，产出内部报告。

交付：

- `client_probe/mxsj_probe.py`
- `client_probe/build_probe_package.py`
- 探针报告 schema；
- Windows 测试包；
- 构建报告。

门槛：

- Windows 客户端真实进程内可读报告；
- 报告绑定测试包 SHA-256；
- 无敏感信息；
- 原始包不变。

## M3：标准 MCP Server

目标：让各种 MCP 编程工具接入。

交付：

- `src/mxsj_client_mcp/core/`
- `src/mxsj_client_mcp/mcp/`
- `src/mxsj_client_mcp/transports/`
- `run.py`
- `bootstrap.py`
- `pyproject.toml`
- `configs/` 示例；
- fake probe 测试；
- stdio / HTTP 测试。

门槛：

- Linux fake probe 协议测试通过；
- Windows 真实探针报告可通过 MCP 读取；
- 至少两个 MCP 编程工具接入成功；
- 只读并发正常；
- 控制类工具默认关闭。

## M4：最小受控操作

目标：开放一个白名单原生操作。

交付：

- 操作白名单 schema；
- 主循环调度；
- 独占锁；
- 审计；
- Windows 验收报告。

门槛：

- 操作前后状态可读取；
- 未授权命令拒绝；
- 无任意代码执行；
- 无敏感信息泄露。

## M5：场景测试

目标：组合登录 / 选角 / 进图 / NPC / 传送等场景。

交付：

- 场景定义；
- 断言；
- 报告；
- 失败证据；
- 回归入口。

门槛：

- 每个场景有独立 Windows 验收；
- 不把 Mock 回环当原生客户端验收；
- 不把 fake probe 当真实客户端。

## 当前状态

本地 `data/script.fls` 已作为当前输入基准。只读目录/存储载荷报告确认：5002 条、无增删或索引变化、4 条载荷变化。当前 `337` 可严格解析并确认 `script\\login\\mainpage.py`；`1145` 可由历史自动解码器识别为 `script\\gamectrl.py`，但严格 VM25 原生身份校验未能独立绑定；`4007`、`4806` 的原生身份解析仍为 ambiguous/unknown。

独立探针核心、localhost IPC 和仓外包构建器已实现并验证。当前尚未将探针替换进任何游戏模块：没有一个安全、独立、可回滚的当前载荷挂点已满足身份和原生密钥校验，因此继续写入会破坏客户端或制造不可验收包。下一步是获得当前载荷的独立身份/seed 证据，再做仅仓外副本的代码对象级插入。

## 当前状态（2026-11-02 晚）

- Windows guarded-hook 包已生成 `mxsj_probe_report.txt`，用户回传报告内容。
- 用户 MCP 客户端 `mxsj-client-report` 通过 stdio `--report-file` 成功调用 `client_ping` 与 `client_get_probe_report`。
- 宿主新增本机 Streamable HTTP：`--transport http --host 127.0.0.1 --port 8765 --http-token <token>`，强制 Bearer token，拒绝非本机监听。
- Linux 回归：55 项测试通过，覆盖 stdio、HTTP 鉴权、HTTP 双客户端并发、报告文件解析。
- 仍未完成：HTTP 在 Windows 编程工具实机验收；实时探针 IPC；报告绑定 `script_fls_sha256`；控制类工具与独占锁。

## 当前状态（2026-11-03）

四项“还没做”的进度，逐条对照代码，不含推测：

| 项目 | 状态 | 代码里实际是什么 |
|---|---|---|
| 实时探针 IPC | **部分完成（2026-11-03）** | 已做：探针用原生 `timer.Timer(1, _tick, -1)` 每秒重写报告，报告 mtime 成为真实存活信号，`client_ping` 按 5 秒新鲜度返回 `alive`。未做：socket 双向通道、按请求读取任意状态的命令通道。 |
| 控制类工具 | **未完成** | `mcp/tools.py` 只注册 6 个只读工具（`client_ping` / `client_get_runtime_info` / `client_get_module_status` / `client_get_native_api_status` / `client_get_probe_report` / `client_read_probe_log`）。没有任何写入或操作类工具。 |
| 多客户端控制独占锁 | **只有骨架** | `core/session.py` 有 `ControlLock` 类（holder id + 超时），但 M3 阶段**从不获取**，也没有任何工具调用它；等于没打开。 |
| 登录 → 选角 → 进图 → NPC → 传送 场景 | **未开始** | 仓库里没有场景定义、断言或报告代码。M5 只在计划里。 |

当前真正可用的能力边界：

```text
客户端启动
  -> mainpage 的受保护钩子 import mxsj_probe
  -> 写一次报告
  -> 探针注册 timer.Timer(1, _tick, -1)，此后每秒重写报告
MCP Server（stdio 或本机 HTTP）
  -> client_ping        : 报告 5 秒内更新 = alive=true；关游戏后变 false
  -> client_get_*       : 读取最新一份快照
```

也就是说：**能判断客户端是否在跑、能读到每秒刷新的快照；还不能按需询问、不能操作、不能跑场景。**

### 四项各自的前置条件

1. **实时 IPC**：探针必须在客户端里常驻并持续响应。需要先确认客户端 VM 里能用 `socket` / 线程，且要有安全的排空点（主循环或定时回调），否则只能在钩子处跑一次。
2. **控制类工具**：必须解决“MCP 线程 ≠ 客户端主线程”。操作要排进客户端主循环，不能从 socket 线程直接碰游戏对象；还需白名单 schema 与审计。
3. **独占锁**：依赖 2，先有可执行操作，锁才有意义；同时要定“客户端异常退出时锁怎么释放”。
4. **场景测试**：依赖 1+2+3，加上登录 / 选角 / 进图的稳定锚点（界面对象、状态字段、可选用的测试账号）。

顺序不能颠倒：先 1，再 2，再 3，最后 4。
