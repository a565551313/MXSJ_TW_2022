# 探针钩子：做了什么、为什么安全

> 日期：2026-11-03。工具：`tools/client_mcp/client_probe/patch_package.py`。

## 1. 目标

让**客户端自己在启动时**写一份只读探针报告，供 MCP Server 读取；同时保证**探针出任何问题都不影响游戏启动**。

## 2. 实际改动

只改一个条目：`mainpage`（entry id `276057508`，第 337 条）。其余 5002 条载荷逐字节不动。

改动等价于在模块末尾追加：

```python
try:
    import mxsj_probe
    mxsj_probe.write_report()
except:
    pass
```

`mxsj_probe` 模块早就在包里（entry id `2537560296` = `mx_hash("mxsj_probe.s")`），这次只是让它被导入一次。它只 `import sys` 并定义函数，`write_report()` 把 `repr(dict)` 写到**游戏进程的当前目录**下的 `mxsj_probe_report.txt`。

## 3. 字节码（CPython 2.5，标准编号）

原模块末尾的 `LOAD_CONST None; RETURN_VALUE`（4 字节）被替换为 37 字节：

```text
206  SETUP_EXCEPT  -> 235        ; 异常兜底
209  LOAD_CONST    -1            ; 与编译器一致：import 的 level
212  LOAD_CONST    None          ; fromlist
215  IMPORT_NAME   'mxsj_probe'
218  STORE_NAME    'mxsj_probe'
221  LOAD_NAME     'mxsj_probe'
224  LOAD_ATTR     'write_report'
227  CALL_FUNCTION 0
230  POP_TOP
231  POP_BLOCK
232  JUMP_FORWARD  -> 239        ; 跳过异常处理段
235  POP_TOP                      ; 异常处理：丢弃 traceback/value/type
236  POP_TOP
237  POP_TOP
238  END_FINALLY
239  LOAD_CONST    None          ; 模块正常返回 None
242  RETURN_VALUE
```

栈收支：成功路径 0 → 1 → 2 → 1 → 0 → 1 → 1 → 1 → 0 → 0；异常路径进入处理段时栈高 3，三次 `POP_TOP` 后归零，`END_FINALLY` 后落到 239。两条路径都不残留栈元素。

## 4. 为什么安全

- 整段包在 `SETUP_EXCEPT … END_FINALLY` 内，导入失败、`write_report` 抛异常（目录只读、磁盘满）都会被吞掉；
- 不新增全局名字以外的副作用：只多一个 `mxsj_probe` 名字；
- 不改原模块的任何一条既有指令，只在末尾追加；
- 只改这一个条目，其余载荷逐字节保留，目录按原生公式重算；
- 写回前先做全量校验（条目数、顺序、未改动条目逐字节比对、全部 zlib 可解、钩子布局与跳转目标）；
- 上一次的包（`1d6b2152…3074a`，无钩子）保留在 git 历史里，随时可回退。

## 5. 复核与重做

```text
双击 tools/client_mcp/检查当前客户端包.bat
```

会打印当前包的 SHA-256、中文结论、以及 0SLF 结构是否正常。要重做钩子（例如回退了包版本）：

```text
python3 tools/client_mcp/client_probe/patch_package.py            # 就地写入
python3 tools/client_mcp/client_probe/patch_package.py --check    # 只检查
```

重复运行会直接提示“已经有探针钩子了”，不会叠加。

## 6. 记录

本次修改的前后 SHA 与条目信息存在 [`evidence/probe_hook_20261103.json`](evidence/probe_hook_20261103.json)；
工具每次运行会把新的记录写到 `tools/client_mcp/runtime/probe_hook_report.json`（不入库）。

## 7. 还没证明的事

- 只在 Linux 上做了静态校验（结构、字节码布局、跳转、栈收支），**没有在 Windows 客户端里实跑过**；
- 报告写在游戏进程的当前目录；如果启动方式改了工作目录，`mxsj_probe_report.txt` 可能落在别处；
- 这是**启动时快照**，不是实时 IPC。
