# MCP 客户端配置示例

[generic_stdio.example.json](generic_stdio.example.json) 展示常见 `mcpServers` 格式。
将 Python 和仓库路径换成本机绝对路径，Python 环境需安装本项目依赖。各客户端的配置入口与字段以各自文档为准。

当前 Server 默认连接进程内 fake probe；也可通过 `--report-file` 读取客户端探针写出的报告文件（支持 JSON 或 CPython 2.5 `repr(dict)`），或通过 `--probe ipc` 连接本机探针 IPC。传输支持 stdio 与本机 Streamable HTTP。
stdio 的标准输出由 MCP 协议使用，不应插入普通日志。

报告文件示例：[generic_stdio_report_file.example.json](generic_stdio_report_file.example.json)。把 `--report-file` 指向 Windows 测试客户端目录下的 `mxsj_probe_report.txt`。该模式是文件快照桥，不是实时进程会话；`client_ping` 只表示报告文件当前可读。

HTTP 示例：[generic_http.example.json](generic_http.example.json)。先启动 `python run.py --transport http --host 127.0.0.1 --port 8765 --http-token <token> --report-file <报告路径>`，再把 URL 与 Bearer token 配到 MCP 客户端。token 不得提交 Git。
