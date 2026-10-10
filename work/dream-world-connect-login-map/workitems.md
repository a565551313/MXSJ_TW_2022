# Work Items

> **2026-10-10 核对更新**：以下状态已按 `report/verification-20261010.md` 修正。WI-009 由 done 改回 in_progress；WI-002 与 WI-006 的表述已修正；WI-012 由 done 改为 partial；新增 WI-013 至 WI-017。

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Establish scope and auth | lead | case | process | done | | Scope ready; offline read-only analysis |
| WI-002 | Extract server selection and endpoint candidates | lead | server.ini, mx.ini | static config | in_progress | E-001, E-002, E-VERIFY-001 | 原始 `server.ini`（`caa7996`）有 6 条：推荐区/免费区各一条指向 `203.70.8.205`，另有 `207/206/204/198`；`lastserver=` 为空。**2026-10-10 复核**：当前 HEAD 版（`1106434`）已把推荐区/免费区两条改为 `127.0.0.1`，`203.70.8.205` 不再出现在当前文件中。文件未恢复，等待决定。 |
| WI-003 | Determine login pre/post state from logs | lead | local logs, local capture | login state | done | E-003, E-LOOPBACK-001 | Latest run reached server selection only; user confirms account-login UI is not reached; no success/map-entry evidence |
| WI-004 | Recover protocol state symbols | lead | mxmain.dll, IMProtocol.dll | static strings | done | E-004 | Connect/send/receive/error callback symbols identified |
| WI-005 | Identify map resources and map-loading linkage | lead | map/*.map, data/*.fls | map assets | done | E-004, E-005 | Common 0.1M map header and dimensions observed |
| WI-006 | Recover IMProtocol framing and serialization boundaries | lead | IMProtocol.dll, mx.exe | protocol static | in_progress | E-IDA-007, E-REA-002, E-LOOPBACK-002, E-CRYPTO-001, E-VERIFY-001 | **2026-10-10 修正**：加密算法与 10 个 S 盒已还原，`IMProtocolCrypto` 往返自检通过（`notes/protocol-artifacts/im_crypto.py`）。**但通信密钥未获得**（见 WI-010），真实报文无法解密；帧格式 `uint16_be 总长度 + uint16_be 命令字 + payload` 仍为推断。原“完整破解”措辞不成立。 |
| WI-007 | Maintain handoff state-machine documentation | lead | notes/state-machine-draft.md | documentation | done | E-001..E-005, E-REA-002..E-REA-008, E-USER-001 | Candidate Connect -> Login -> World -> Map state model documented; latest UI and agent findings appended |
| WI-008 | Trace main-image callers of IMProtocol APIs and identify channel role | lead | mx.exe, IMProtocol.dll | native callsites/xrefs | in_progress | E-IDA-007, E-REA-002..E-REA-004, E-REA-008, E-IDA-DYN-001, E-IDA-DYN-003, E-IDA-DYN-004 | Normal launch plus IDA attach is working; first runtime hit is the native/Python bridge at 0x004576B0. Protocol-library/Winsock hit remains open. **2026-10-10**：`E-IDA-001` 与 `E-IDA-DYN-002` 在 timeline/workitems 中被引用但文件不存在（见 WI-015）。 |
| WI-009 | Trace server-selection to account-login UI transition | lead | mx.exe, mxmain.dll, data/script.fls, local captures | UI/protocol state | in_progress | E-LOOPBACK-001, E-LOOPBACK-002, E-REA-003..E-REA-008, E-USER-001, E-IDA-DYN-*, E-SCRIPT-001, E-VERIFY-001 | **2026-10-10 由 done 改回**：原记录“已完成登录流程确认”与运行证据矛盾。已确认的只有：脚本中的登录相关符号（`loginhello`、`TEST_HELLO`、`RESELECT_HELLO`、`CMXNet`、`OnServerCmd`）存在；客户端能连接 `127.0.0.1:3134`（E-LOOPBACK-002）；但**账号页未到达，无任何应用层数据与服务端响应**。 |
| WI-010 | Capture real crypt key via IMP_RefreshCryptKey | lead | IMProtocol.dll, mx.exe | dynamic analysis | in_progress | E-CRYPTO-001, E-TOOLS-001, E-VERIFY-001 | **阻塞项**。`enhanced_capture_server.py` 工具可用（`--help` 正常），但至今**没有捕获到任何应用层字节**：`notes/protocol-artifacts/stream-0001..0022.bin` 全部 0 字节。需要在 Windows 测试副本、仅回环环境下获取真实握手数据。 |
| WI-011 | Decode entry 516 Python script (OnServerCmd logic) | lead | data/script.fls, mx.exe | script analysis | done | E-REA-008, E-SCRIPT-001, E-VERIFY-001 | entry 516 完整解码：59 个代码对象，脚本路径 `script\login\netserver.py`。**2026-10-10 已在仓库外重跑核实**（`fls_batch_decoder.py --archive data/script.fls --index 516`）。co_code 自定义映射（v4.3）仍为部分完成。 |
| WI-012 | Implement mock server with cracked crypto | lead | IMProtocol.dll, im_crypto.py | protocol simulation | partial | E-CRYPTO-001, E-TOOLS-001, E-VERIFY-001 | **2026-10-10 由 done 改为 partial**：`mock_server.py` 可启动并绑定 127.0.0.1（`--response-type` 6 种）；**未与真实客户端联调**；依赖的密钥未获得；loginhello 样本缺失。 |
| WI-013 | Verify C→S numeric command IDs and loginhello sample provenance | lead | notes/protocol-commands-values.md, script netserver.py | protocol static | open | E-VERIFY-001 | 0x0001/0x0002/0x0003/0x0010/0x00FF 的数值没有证据来源：脚本中只有符号名（`LOAD_ATTR 'C2GS_SELECT_SERVER'`）。`tools/test-data/test_loginhello_plain.bin` 不存在。需要找到数值来源（原生 `net` 模块常量表、`mxmain.dll` 静态分析），或降级为未证实。 |
| WI-014 | Repository hygiene: tracked binaries and modified server.ini | lead | git tree, server.ini | repo | partial | E-VERIFY-001 | (a) 当前 HEAD 跟踪约 478 MB 文件，包括游戏二进制与音乐资源；(b) `server.ini` 已改为回环地址，**用户确认为有意保留的本地回环配置**，不恢复原始版本；(c) `mx.exe` 与 `mxmain.dll` 字节相同。**2026-10-10 用户决定：游戏二进制与资源保留在 Git 中，不移出。** 本次按要求未删除、未移动任何文件。 |
| WI-015 | Fix dangling evidence references | lead | workitems, timeline, notes | documentation | open | E-VERIFY-001 | `E-IDA-001`、`E-IDA-DYN-002` 被引用但不存在；多个报告引用的 `tools/test-data/`、`docs/`、`tools/mock_server_v2.py`、`notes/login-flow-complete.md` 等不存在。核对报告 §8 列出清单。 |
| WI-016 | Reconcile unknown-opcode counts | lead | notes/co_code_analysis/mapping_table_v4.json, task-b artifacts | script analysis | open | E-VERIFY-001 | 映射表 `unknown_hot` 记录 16 **组**；交接文档 §4.6 列出 24 个字节值。口径不一致，需统一。 |
| WI-017 | Correct overstated completion tables | lead | report/final-summary-20261010.md, TASK_DISPATCH.md, notes/protocol-commands-values.md | documentation | open | E-VERIFY-001 | 这些文件仍保留“完成”“已确认”的旧表述（如“实际密钥捕获 0%”与“登录流程梳理 90%”并存）。已在文件顶部加修正提示，正文未逐条重写。 |

## Coverage
- [x] 加密算法实现已还原并自检（`im_crypto.py`）；**通信密钥未获得**（WI-010）
- [x] S 盒全部提取（2 × 2048 B + 8 × 256 B）
- [ ] Real crypt key capture pending (WI-010)
- [x] Script entry 516 decoded and re-verified (WI-011)
- [ ] Real login flow / account-login UI reached (WI-009)
- [ ] Mock server validated against real client (WI-012)
- [ ] C→S command numeric IDs verified (WI-013)
- [x] Mock server framework runs on 127.0.0.1 (WI-012, partial)
- [x] Enhanced capture tool `--help` 可用 (WI-010)
- [x] Packet analyzer `--help` 可用 (WI-011)
- [ ] Critical/High candidates triaged (or N/A for pure RE)
- [x] Validated findings have Evidence (E-*)（本轮新增 E-VERIFY-001）
- [x] Candidate path documented; protocol/UI verification path remains open
- [x] Timeline continuous across major phases
- [x] Report and handoff maintained; 2026-10-10 核对报告已生成
- [ ] Dangling evidence references cleaned (WI-015)
- [ ] field-journal anonymized

## Refs
- skills/ops/timeline-workitem.md
- skills/ops/evidence-finding-path.md
- report/verification-20261010.md
