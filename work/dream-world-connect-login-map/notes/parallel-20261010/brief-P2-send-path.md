# 任务书 P2：发包路径（静态）

## 目标
弄清 `IMP_SendBuffer2NS` 在什么条件下被调用、会不会被调用，以及它与 `ws2_32!send` 的关系。用于判断“客户端连上后为什么不发包”。

## 输入（只读）
- `IMProtocol.dll`：导出 `IMP_SendBuffer2NS`、`IMP_EncryptBuffer`、`IMP_ConnectNsServer`（RVA 请自行从导出表读取）。
- `mx.exe` 与 `mxmain.dll`（两者字节完全相同，md5 `2609423f…`，只需分析一份）。
- 对照 `notes/loopback-test-plan-20261010.md` 中的假设 H1–H3。

## 需要回答的问题
1. `IMP_SendBuffer2NS` 的调用点在哪里（`mx.exe` 或 `IMProtocol.dll` 内部的地址）？每个调用点之前需要满足什么条件（如：已连接标志、已收到某个数据、已完成某个状态）？
2. `IMP_EncryptBuffer` 是否在 `IMP_SendBuffer2NS` 之前被调用？如果没有密钥，它会直接返回还是失败？
3. 客户端是否存在“连接后先等待服务器数据”的分支？如果有，请写出判断的地址和条件。这对 H1 是直接证据。
4. 结论与 10-09 的 0 字节抓包结果相比，是否一致？请说明理由。

## 产出
`notes/parallel-20261010/P2-result.md`，格式同 P1，并单列“对 H1 / H2 / H3 的支持或反对”。

## 禁止
- 不运行游戏，不建立任何网络连接；
- 不修改任何文件。
