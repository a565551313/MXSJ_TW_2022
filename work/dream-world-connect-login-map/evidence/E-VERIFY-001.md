### E-VERIFY-001
- title: 2026-10-10 项目真实性核对：仓库历史、文件、工具、解码与配置的复现结果
- severity: info
- status: validated
- observed_at: 2026-10-10T09:50:00+08:00
- source_type: local_read_only_verification
- content_hash: n/a
- repro_command: |
    git rev-parse HEAD master origin/master          # ffec3d9 ×3
    git fetch --unshallow origin                      # 补全历史（无文件改动）
    git merge-base --is-ancestor 711e6a7 HEAD         # 成立
    sha256sum data/script.fls                         # 8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
    md5sum mx.exe mxmain.dll                          # 两者均为 2609423fe7fadd5446eb2425ab894ac8
    python3 tools/fls_batch_decoder.py --archive data/script.fls --index 516 --output /tmp/verify516
    python3 work/dream-world-connect-login-map/notes/task-c-地图分析/artifacts/test_maps.py   # Ran 11 tests OK
    python3 work/dream-world-connect-login-map/tools/mock_server.py --host 127.0.0.1 --port 3999 --response-type auto   # 6s 后超时终止
    git show caa7996:server.ini | iconv ... ; git show 1106434:server.ini | iconv ...        # 对比 server.ini
- raw_excerpt: |
    HEAD=master=origin/master=ffec3d9
    711e6a7 is ancestor of HEAD
    IMProtocol.dll: 187216 B, exports=29, imports=WS2_32.dll,KERNEL32.dll,USER32.dll,SHLWAPI.dll
    mx.exe: 9698712 B, sections=.text,.rdata,.data,_dyprot0,_dyprot1,.rsrc; mxmain.dll identical (md5)
    render.dll: root=MISSING; exe/render.dll=24543576 B
    script.fls: 24454082 B; sha256 matches; entry_count=5002
    entry 516: decode time 5.61s; code objects: 59; names incl. loginhello/TEST_HELLO/RESELECT_HELLO/CMXNet/OnServerCmd/m_Pwd/m_PassPort present in marshal
    all_scripts_catalog.json: 11 records
    script-catalog.csv: 5003 lines incl. header
    mapping_table_v4.json: version=4.3-taskB, table_a=43, table_b=5, unknown_hot=16 groups
    IMProtocolCrypto: encrypt/decrypt round-trip OK; no CryptContext/encrypt/decrypt/derive_key module-level API
    stream-0001..0022.bin: all 0 bytes
    tools/test-data/: absent; test_loginhello_plain.bin: absent (anywhere in repo)
    test_maps.py: Ran 11 tests … OK
    server.ini @caa7996: 203.70.8.205 x2 (recommended/free zone), 207, 206, 204, 198; [Login] lastserver= empty
    server.ini @1106434 (HEAD): 127.0.0.1 x2, 207, 206, 204, 198; [Login] lastserver= empty
    fls_batch_decoder.py --entry: unrecognized argument (doc usage invalid)
    pymarshal_dis.py --help: treated as filename -> FileNotFoundError
    data_browser/app.py --help: launches web server (timeout)
- notes: |
    本次核对只读；仅在仓库外生成解码输出（/tmp/verify516）与虚拟环境（/tmp/pevenv，安装 pefile 用于 PE 解析）。
    在 work/.../tools/mock-server-logs/ 下新增了 mock_server 试运行日志；经用户确认后已删除（仅删除该日志与其空目录）。
    server.ini 未被修改。
- effects: 无外部网络连接（仅 git fetch 到 github.com 与 pip 安装 pefile）；无客户端运行；无文件删除/移动。
- limitations: |
    未能核实：客户端完整安装大小 703 MB；Themida 相关结论（仅检查了节名与特征串）；命令字数值的来源；
    test_map_gui.py；packet_analyzer 对样例的处理（样例缺失）。
- linked_workitems: WI-002, WI-003, WI-006, WI-008, WI-009, WI-010, WI-011, WI-012
