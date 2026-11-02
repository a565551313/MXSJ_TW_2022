# client_probe — 客户端内探针占位

> 状态：占位，未实现。  
> 本目录未来存放运行在客户端老 Python VM 内的自写探针，以及生成测试包的构建入口。

## 未来文件候选

```text
mxsj_probe.py              # 客户端内 Python 2.5 探针
harness.py2                # 离线桩测试，不执行原游戏模块
build_probe_package.py     # 基于用户修改版 script.fls 生成测试包
probe_report.schema.json   # 探针报告 schema
```

## 关键约束

1. 探针必须适配客户端实际 VM；当前主游戏脚本 VM 是定制 Python 2.5，不能使用 Python 3 语法。
2. 不执行反编译 / 恢复出来的游戏模块。
3. 不覆盖用户输入包或仓库原始包。
4. 探针挂点必须等用户修改版 `script.fls` 到位后只读核对再定。
5. 第一阶段只读，不提供任意命令执行。
6. 所有客户端内部调用必须考虑主循环 / 线程安全。
7. 报告必须脱敏，不记录账号密码。

## 当前阻塞

等待用户提供修改版 `script.fls`。见 [SCRIPT_FLS_HANDOFF.md](../docs/SCRIPT_FLS_HANDOFF.md)。
