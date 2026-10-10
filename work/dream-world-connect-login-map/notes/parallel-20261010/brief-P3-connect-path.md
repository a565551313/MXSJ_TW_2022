# 任务书 P3：连接流程与 Connect() 复核（v4.3）

## 目标
复核 `任务A深入-Connect函数破解报告.md` 中的 `Connect()` 重建。该报告基于 v4 映射，交接文档要求必须用 v4.3 重审。重点检查：`NakedSend(chr(port & 0xFF))` 是否真实存在、`ip.split(...)` 的分隔符是什么、连接失败后是否切换候选。

## 输入（只读）
- `notes/co_code_analysis/任务A深入-Connect函数破解报告.md`（待复核的旧结论）。
- `notes/co_code_analysis/mapping_table_v4.json`（版本 `4.3-taskB`，表 A 43 条，表 B 5 条，unknown_hot 16 组）。
- 脚本层：`netserver.py`（反编译结果见 `notes/co_code_analysis/netserver_py_decompiled.md`，登录流程为第 3.2 节）。
- `IMProtocol.dll` 的 `IMP_ConnectNsServer`（只读反汇编）。

## 需要回答的问题
1. 按 v4.3 映射，`Connect()` 中的每一步是否仍然成立？列出与 v4 不一致的步骤（v4.3 修正的 4 条是：0x98 STORE_NAME、0xE0 IMPORT_NAME、0xFB MAKE_FUNCTION、0x42 BUILD_CLASS，请核对是否影响 `Connect()` 的指令）。
2. `NakedSend(chr(port & 0xFF))` 是否在 `Connect` 之前执行？它发送的是否真的是一个字节（0x3E 对应端口 3134）？如果是，它在 TCP 连接建立之前还是之后发出？
3. `ip.split(...)` 的分隔符是什么？对 `127.0.0.1` 切分后得到的结果是否正确？
4. 连接失败或超时后，是否会切换到下一个候选？超时参数（`PROXY_CONNECT_TIMEOUT`）的值是多少？

## 产出
`notes/parallel-20261010/P3-result.md`：
- 复核表：每一步标注“v4.3 已证实 / 与 v4 不同 / 未证实”；
- 对 H3（NakedSend 被丢弃）与 H4（IP 拆分错误）的结论；
- 明确列出需要更新的旧报告段落。

## 禁止
- 不修改旧报告（只在结果文件中指出需要修改的位置，由协调者统一修改）；
- 不运行任何代码连接网络。
