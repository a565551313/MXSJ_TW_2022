# 按改动选择材料与检查

所有代码路径相对实际仓库根。命令从该目录执行；本文件是定位入口，执行前
核对当前文件、依赖与 README，避免把历史命令当成无需检查的启动指令。

## 原生游戏 TCP 与 Mock

- 研究：`notes/native_tcp_channel.md`。
- 算法/API：`tools/native_channel/README.md`、`tools/native_channel/src/mxsj_native_channel/core/`。
- 独立预期：`tools/native_channel/evidence/vectors.json`、`tests/native_oracle.py`。
- 字节码依据：`tools/native_channel/tests/script_evidence.py`。
- 集成：`mock_server_v2.py`、`MOCK_SERVER_V2_README.md`、`test_v2_channel.py`。
  启动/副作用边界仍以 `docs/MOCK_SERVER.md` 和当前实现为准。

基础 codec 检查（无游戏监听）：

```bash
python3 -m unittest discover -s tools/native_channel/tests -v
python3 tools/native_channel/bootstrap.py --check-only
python3 tools/native_channel/run.py
```

只有修改算法、证据或需要重新确认原生结果时运行独立 oracle；依赖和锁定
输入见模块 README。它需要原 DLL、pefile、Unicorn；普通 codec 测试不需要。
改 Mock 集成时检查 `test_v2_channel.py` / `--self-test` 的当前临时文件与回环
副作用，先确定适合本次环境，再选择执行。

容易错的边界（改动前重新对照地址证据）：

- `UnpackInt(4)` 的有符号返回影响高位 seed 的 25 字节裸应答。
- NakedSend 不推进密码流；加密后的下行长度前缀也被加密。
- 上下行帧不对称；下行扩展长度宽度以当前脚本设置为准。
- RX/TX 独立，换包不重置密码流；LZW 字典跨下行帧保留。
- 主程序明文函数对照与 render 同族包装器对照有不同证据范围；
  真实连接反馈应结合最新 STATUS，不能只复述最早报告的待验状态。

## 编辑器、FLS、共享核心

- 子项目：`ui_editor/README.md`、`resource_editor/README.md`、
  `map_editor/README.md`、`script_editor/README.md`。
- FLS 路径/目录：`notes/native_dlg_path_cipher.md`、
  `notes/fls_path_hash_and_dlg.md`；新增 entry 涉及排序和偏移重建。
- 开发/Windows：`docs/PYTHON_TOOL_CONVENTIONS.md`、`tools/devkit/README.md`。
- 生命周期/依赖：`tools/README.md`、`tools/DEPENDENCIES.md`。

```bash
python3 tools/devkit/vendor_core.py --check
```

共享核心有变更时先核对该工具参数，再生成副本并检查。
对改动的工具目录跑其 README 指定单元测试、Ruff、bootstrap --check-only 和
Windows 检查；GUI 测试按约定使用 offscreen，并记录失败/跳过原因。
不把 STATUS 的历史 Qt 错误或计数自动作为当前运行结果。

## 服务端、SQLite 与只读数据复核

- 本地独立工程：`local_server/README.md`（其测试在本目录 `tests/`）。
- 正式服设计/责任区：`server/README.md`、`server/docs/OWNERSHIP.md`、
  `server/docs/INTERFACES.md`、`server/docs/SOURCE_EVIDENCE.md`。
- 待审数据：`server/docs/csv_checks/BATCH_001.md`；不能直接进入正式配置。

常用窄检查（按实际改动选择）：

```bash
python3 local_server/bootstrap.py --check-only
python3 -m unittest discover -s server/tests/architecture
python3 -m unittest discover -s server/tests/catalog
python3 server/tools/verify_source_map.py
python3 server/tools/export_review_csv.py --check
```

本地工程测试：工作目录切到 `local_server/`，执行
`python3 -m unittest discover -s tests -t .`，以其当前 README 为准。
API/网页依赖、构建、验收命令从 `server/apps/review_api/`、
`server/apps/review_web/` 与对应文档读取；不要为了修改说明安装整个前端/Qt 环境。

## 汇报兼容性结果

写明“哪个版本、哪些输入、执行了哪个检查、实际结果、可支持什么结论”。
例如用户口述 Windows Mock v2 连接至 NPC 传送成功，可作为该场景的用户实机
反馈；没有独立日志/抓包时，不得补写不存在的证据，也不能据此抹去用户反馈。
避免全项目完成率或“所有原生协议完全兼容”等超出检查范围的结论。
