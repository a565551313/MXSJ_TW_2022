# Windows 启动报错排查与修复（2026-11-02）

> 状态：已在 Linux 侧完成只读诊断与仓外修复包构建；**Windows 实机启动尚未验收**。
> 输入：用户替换到 `data/script.fls` 的 Windows 钩子版包。

## 1. 输入身份

```text
路径: data/script.fls
大小: 24,273,249 B
SHA-256: 2914a4edfb4adb33f0661bba1297a827ebdc055b788673a9e25717b563f61a3d
0SLF: count=5003, directory=24193201
```

本轮**未覆盖、未修改**该输入文件。所有修复产物写到仓库外：

```text
/home/user/mxsj-client-mcp-debug/builds/
```

## 2. 已确认的两个致命缺陷

### 缺陷 A：0SLF 目录 r2 长度字全部错误

按原生目录公式逐条解码：

```text
clen = ((r1 * entry_id + 0x000DF25E) & 0xFFFFFFFF) ^ r2
doff = ((r2 * index * 0x00F718FE + 0x0D59D16C) & 0xFFFFFFFF) ^ r3
```

结果：

- 5003 条中 **803 条 payload 越界**；
- 其余条目解出的 `clen` 也远大于真实 zlib 流长度；
- 但所有 `doff` 与真实流偏移一致，且全部 5003 个 zlib 流首尾相接、可完整解压。

结论：Windows 侧重打包时**只写坏了目录 r2/r3 中的长度编码**，脚本载荷本体基本完好。
游戏启动时按错误长度读取/解压脚本，必然失败。

### 缺陷 B：`mainpage.py` 探针钩子字节码 malformed

入口 `276057508`（`script\login\mainpage.py`）顶层尾部原为：

```text
LOAD_CONST None
LOAD_CONST None
LOAD_CONST 'mxsj_probe'
IMPORT_FROM mxsj_probe      ; 错：应为 IMPORT_NAME
STORE_NAME mxsj_probe
LOAD_NAME mxsj_probe
COMPARE_OP 22               ; 错：应为 LOAD_ATTR write_report
CALL_FUNCTION 0
POP_TOP
RETURN_VALUE                ; 栈空返回
```

该序列不是合法 CPython 2.5 `import mxsj_probe; mxsj_probe.write_report()` 编译结果，
会在登录主页面模块导入时抛异常或破坏解释器栈。

## 3. 修复产物（均在仓库外）

| 用途 | 路径 | SHA-256 | 说明 |
|---|---|---|---|
| **推荐测试包** | `guarded-hook-final-20261102T122300Z/script.fls` | `068b4972050af4ffa98bf74016c5b97c66ac939e748ac991c1eb0f196da24dcf` | 目录已修复；探针钩子改为正确字节码并包在 `try/except` 中，探针失败不会拖垮登录。 |
| 无钩子回退包 | `no-probe-hook-20261102T121654Z/script.fls` | `1d6b21529e8fc651f5a1af18788090f7e61955914f2a1d00cd8c655b3ea3074a` | 目录已修复；移除 mainpage 探针钩子。探针条目仍在包内但不会被导入。用于确认游戏本体可启动。 |
| 仅修复目录+钩子（无异常保护） | `repaired-20261102T121147Z/script.fls` | `585040f9417ad8199d925a1fe3979891cf9d24e4c341c2cab7ecbd04fc547048` | 中间产物；不建议优先实机测试。 |

### 已做校验

- 推荐包与回退包均通过 `script_fls_compare.inventory()`：5003 条目录边界全部正确；
- 全部 5003 个 zlib 流可解压；
- `mainpage` / `mxsj_probe` 两条严格 marshal 解析通过，原生模块名哈希与 entry_id 绑定一致；
- 推荐包相对 broken 输入：**仅 entry 276057508 载荷变化**，其余 5002 条载荷逐字节保留；
- 回退包相对 locked baseline：仅用户已改的 4 条载荷变化 + 新增探针条目，无删除。

### 未做 / 不能宣称

- **未在 Windows 真实客户端启动验收**；
- 未证明探针报告文件一定生成（取决于客户端 cwd 是否可写、导入时机是否到达 mainpage）；
- 未把修复包写回 `data/script.fls`，未提交任何生成 FLS 到 Git。

## 4. Windows 测试步骤

1. 备份当前客户端 `data/script.fls`（即 SHA `2914a4ed…` 的 broken 包）。
2. 先替换为**无钩子回退包** `1d6b2152…`，启动游戏确认能到登录界面。
   - 若仍报错：问题不在探针钩子，需回传客户端日志/截图，排查用户既有 4 条修改或其他资源。
3. 再替换为**推荐测试包** `068b4972…`，启动游戏。
   - 预期：即使探针导入/写报告失败，登录流程也不应被探针异常中断。
4. 启动后在客户端目录查找 `mxsj_probe_report.txt`。
   - 若存在：回传内容（已脱敏，仅版本/模块状态）。
   - 若不存在但游戏正常：说明钩子被异常保护吞掉或 mainpage 尚未执行到钩子；回传 `log/pylog_*.txt` 与游戏日志。

## 5. 后续工具链整改

Windows 侧 ad-hoc 重打包脚本未入库，是本次目录损坏来源。后续探针包构建必须：

1. 使用正确的 `encode_0slf_dir_entry()` 公式重建 r2/r3；
2. 构建后强制跑 `script_fls_compare.inventory()` 与全量 zlib 解压校验；
3. 钩子字节码必须由 CPython 2.5.6 编译或经严格反汇编复核，不得手写错误 opcode；
4. 任何校验失败即拒绝出货，不允许“先替换再试”。

## 6. 用户回传探针报告（2026-11-02）

用户在 Windows 测试后回传：

```python
{'runtime': {'thread_count': None, 'main_loop_ticks': None, 'pid': None, 'python_version': [2, 5, 0]}, 'modules': {'modules': [{'loaded': True, 'name': 'sys'}, {'loaded': True, 'name': 'time'}, {'loaded': True, 'name': 'os'}]}, 'native_api': {'status': 'unknown', 'apis': []}, 'probe_version': '0.1.0'}
```

结论：

- 探针已在客户端定制 Python 2.5 VM 内执行，并写出 `mxsj_probe_report.txt`；
- `sys/time/os` 模块状态可读；
- `native_api` 仍为 `unknown`，符合当前只读内核边界；
- `pid/thread_count/main_loop_ticks` 为 `None`，因为当前探针未采集这些值；
- 报告未包含 `script_fls_sha256`，因此还不能把该报告强绑定到某个测试包；
- 这证明启动钩子路径已跑通，但**不等于 MCP 编程工具接入验收完成**。

宿主侧已修复 `FileProbeBackend`：客户端 Python 2.5 报告是 `repr(dict)`（含 `None/True` 与单引号），不是 JSON。现在 `--report-file` 会先尝试 JSON，失败后仅用 `ast.literal_eval` 解析受限字面量，不执行代码，并限制 256 KiB。新增回归测试覆盖用户回传格式、恶意表达式拒绝、非对象拒绝、超限拒绝，以及真实 MCP stdio 会话读取该格式报告。
