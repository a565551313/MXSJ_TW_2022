# 探针钩子与常驻定时器：做了什么、为什么安全

> 日期：2026-11-03。工具：`client_probe/patch_package.py`（钩子）、`client_probe/build_resident.py`（常驻定时器）。

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

## 4.5 常驻定时器（第二步）

只改一个条目：`mxsj_probe`（entry id `2537560296`，第 2996 条）。追加约 60 字节模块代码和一个函数：

```python
def _tick():
    try:
        write_report()
    except:
        pass

try:
    import timer
    _TIMER = timer.Timer(1, _tick, -1)   # 1 秒一次，-1 = 一直重复
except:
    pass
```

`timer` 是客户端自带的脚本级定时器模块，游戏自己也在用（`twautologin` 里
`timer.Timer(0.1, self.CheckStep, iRepeat=-1)`、`dlgloginqueue` 里 `timer.Timer(0.6, ...)`）。
`_TIMER` 存成模块全局，是为了不让定时器对象被回收导致定时器停掉。

效果：只要客户端在跑，`mxsj_probe_report.txt` 每秒被重写一次。因此**报告文件的修改时间
就是存活信号** —— 宿主侧 `client_ping` 现在按“报告是否在 5 秒内更新”判定 `alive`，
客户端关掉几秒后就会变成 `alive=false`。

字节码（`_tick`，21 字节）：

```text
0   SETUP_EXCEPT -> 13
3   LOAD_GLOBAL  write_report
6   CALL_FUNCTION 0
9   POP_TOP
10  JUMP_FORWARD -> 17
13  POP_TOP; POP_TOP; POP_TOP; END_FINALLY
17  LOAD_CONST   None
20  RETURN_VALUE
```

模块尾部追加（节选）：

```text
LOAD_CONST <code _tick>; MAKE_FUNCTION 0; STORE_NAME '_tick'
SETUP_EXCEPT -> handler
  LOAD_CONST -1; LOAD_CONST None; IMPORT_NAME 'timer'; STORE_NAME 'timer'
  LOAD_NAME 'timer'; LOAD_ATTR 'Timer'
  LOAD_CONST 1; LOAD_NAME '_tick'; LOAD_CONST -1; CALL_FUNCTION 3
  STORE_NAME '_TIMER'
  POP_BLOCK; JUMP_FORWARD -> end
handler: POP_TOP ×3; END_FINALLY
end: LOAD_CONST None; RETURN_VALUE
```

模块 stacksize 由 4 提到 6（这段最多用 4 层栈）。

## 5. 复核与重做

```text
双击 tools/client_mcp/检查当前客户端包.bat
```

会打印当前包的 SHA-256、中文结论、以及 0SLF 结构是否正常。要重做钩子（例如回退了包版本）：

```text
python3 tools/client_mcp/client_probe/patch_package.py            # 加钩子
python3 tools/client_mcp/client_probe/build_resident.py           # 加常驻定时器
```

两个工具都支持 `--check`（只检查不写回），重复运行会直接提示“已经加过了”，不会叠加。
顺序不能反：先加钩子，再加定时器（定时器依赖 `mxsj_probe` 已被导入时执行）。

## 6. 记录

本次修改的前后 SHA 与条目信息存在 [`evidence/probe_hook_20261103.json`](evidence/probe_hook_20261103.json)；
工具每次运行会把新的记录写到 `tools/client_mcp/runtime/probe_hook_report.json`（不入库）。

## 7. 还没证明的事

- 只在 Linux 上做了静态校验（结构、字节码布局、跳转、栈收支），**没有在 Windows 客户端里实跑过**；
- `timer.Timer` 的第三个参数按 `iRepeat=-1` 传；如果客户端对它的解释不同，退化为只触发一次；
- 报告写在游戏进程的当前目录；如果启动方式改了工作目录，`mxsj_probe_report.txt` 可能落在别处；
- 这是**启动时快照**，不是实时 IPC。
