# 任务书 P4：脚本层登录流程（连接后的发送顺序）

## 目标
从已解码的脚本层（`netserver.py` 及相关模块）中，找出“客户端建立连接后，按什么顺序发送哪些消息”。用于验证 H1：客户端是否需要先等服务器首包。

## 输入（只读）
- `notes/task-b-脚本分析/artifacts/fullrun/decode-results-final.jsonl`（5002 行，ok 4484，fail 272，suspect 246）。
- `notes/co_code_analysis/netserver_py_decompiled.md`（第 3.2 节为登录流程）。
- `notes/script-analysis-complete.md`、`notes/protocol-commands-values.md`（命令字数值未证实，只能引用符号名）。

## 需要回答的问题
1. 连接成功后，客户端第一条发送的消息是什么（符号名）？它在哪个函数中发出？
2. 在发送第一条消息之前，是否有“等待服务器数据”的判断？如果有，判断的内容是什么？
3. 按脚本层的流程，有几种可能的“卡住”点（如等待首包、等待服务器列表）？分别对应哪一条代码？
4. 对 H1 给出结论：支持 / 反对 / 无法判断，并写明依据（函数名与行号）。

## 产出
`notes/parallel-20261010/P4-result.md`：
- 登录流程的顺序图（文字列表即可）；
- 每一步的依据（脚本模块名、函数名、解码记录中的索引）；
- 对 H1 的结论，标注“未证实”时写明缺什么证据。

## 禁止
- 不得使用未证实的命令字数值，只能引用符号名（如 `C2GS_SELECT_SERVER`）；
- 不得修改 `decode-results-final.jsonl` 或其他 artifacts；
- 不运行游戏。
