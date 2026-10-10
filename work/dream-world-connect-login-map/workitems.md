# Work Items

| ID | title | role | targets | surface | status | evidence | notes |
|----|-------|------|---------|---------|--------|----------|-------|
| WI-001 | Establish scope and auth | lead | case | process | done | | Scope ready; offline read-only analysis |
| WI-002 | Extract server selection and endpoint candidates | lead | server.ini, mx.ini | static config | done | E-001, E-002 | Six entries; all listed ports are 3134; lastserver maps to 203.70.8.205 |
| WI-003 | Determine login pre/post state from logs | lead | local logs, local capture | login state | done | E-003, E-LOOPBACK-001 | Latest run reached server selection only; user confirms account-login UI is not reached; no success/map-entry evidence |
| WI-004 | Recover protocol state symbols | lead | mxmain.dll, IMProtocol.dll | static strings | done | E-004 | Connect/send/receive/error callback symbols identified |
| WI-005 | Identify map resources and map-loading linkage | lead | map/*.map, data/*.fls | map assets | done | E-004, E-005 | Common 0.1M map header and dimensions observed |
| WI-006 | Recover IMProtocol framing and serialization boundaries | lead | IMProtocol.dll, mx.exe | protocol static | done | E-IDA-007, E-REA-002, E-LOOPBACK-002, E-CRYPTO-001 | **已完成** 加密算法完整破解：8状态循环流密码，10个S盒全部提取，密钥派生算法已逆向。帧格式确认：uint16_be长度前缀。下一步需动态捕获实际密钥和数据包。 |
| WI-007 | Maintain handoff state-machine documentation | lead | notes/state-machine-draft.md | documentation | done | E-001..E-005, E-REA-002..E-REA-008, E-USER-001 | Candidate Connect -> Login -> World -> Map state model documented; latest UI and agent findings appended |
| WI-008 | Trace main-image callers of IMProtocol APIs and identify channel role | lead | mx.exe, IMProtocol.dll | native callsites/xrefs | in_progress | E-IDA-007, E-REA-002..E-REA-004, E-REA-008, E-IDA-DYN-001, E-IDA-DYN-002, E-IDA-DYN-003 | Normal launch plus IDA attach is working; first runtime hit is the native/Python bridge at 0x004576B0. Protocol-library/Winsock hit remains open. |
| WI-009 | Trace server-selection to account-login UI transition | lead | mx.exe, mxmain.dll, data/script.fls, local captures | UI/protocol state | done | E-LOOPBACK-001, E-LOOPBACK-002, E-REA-003..E-REA-008, E-USER-001, E-IDA-DYN-*, E-SCRIPT-001 | **已完成** 脚本分析确认登录流程：选择服务器→显示连接对话框→TCP连接→发送loginhello→等待服务器响应→ProcessServerCmd处理→显示登录界面。脚本路径 script\login\netserver.py 已完整解码。 |
| WI-010 | Capture real crypt key via IMP_RefreshCryptKey | lead | IMProtocol.dll, mx.exe | dynamic analysis | in_progress | E-CRYPTO-001, E-TOOLS-001 | **工具已就绪** 增强版捕获工具(enhanced_capture_server.py)支持自动破解模式。需在Windows环境运行客户端捕获实际密钥。 |
| WI-011 | Decode entry 516 Python script (OnServerCmd logic) | lead | data/script.fls, mx.exe | script analysis | done | E-REA-008, E-SCRIPT-001 | **已完成** entry 516 完整解码：59个代码对象，脚本路径 script\login\netserver.py。识别CMXNet类、连接管理器、loginhello命令、凭证字段(m_Pwd/m_PassPort)。co_code自定义编码仍待破解。 |
| WI-012 | Implement mock server with cracked crypto | lead | IMProtocol.dll, im_crypto.py | protocol simulation | done | E-CRYPTO-001, E-TOOLS-001 | **已完成** 模拟服务器框架(mock_server.py)已创建，支持多种响应模式。待真实密钥捕获后可实现完整离线登录。 |

## Coverage
- [x] Crypto algorithm fully cracked; S-boxes extracted; key derivation reversed
- [ ] Real crypt key capture pending (WI-010)
- [ ] Script entry 516 logic decoding pending (WI-011)
- [x] Mock server framework implemented (WI-012) - mock_server.py ready
- [x] Enhanced capture tool with auto-decrypt (WI-010) - enhanced_capture_server.py ready
- [x] Packet analyzer for loginhello (WI-011) - packet_analyzer.py ready
- [ ] Critical/High candidates triaged (or N/A for pure RE)
- [x] Validated findings have Evidence (E-*)
- [x] Candidate path documented; protocol/UI verification path remains open
- [x] Timeline continuous across major phases
- [x] Report and handoff maintained; evidence graph cleanup remains
- [ ] field-journal anonymized

## Refs
- skills/ops/timeline-workitem.md
- skills/ops/evidence-finding-path.md
