# 实施计划草案

> 状态：M0 文档骨架。日期：2026-11-02。

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

## 当前阻塞

```text
等待用户提供修改版 script.fls。
```

在收到修改版前，不应假设探针挂点、条目编号或用户已有修改内容。
