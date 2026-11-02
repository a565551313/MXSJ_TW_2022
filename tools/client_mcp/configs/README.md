# MCP 客户端配置示例

[generic_stdio.example.json](generic_stdio.example.json) 展示常见 `mcpServers` 格式。
将 Python 和仓库路径换成本机绝对路径，Python 环境需安装本项目依赖。各客户端的配置入口与字段以各自文档为准。

当前 Server 连接的是进程内 fake probe，输出为合成数据，尚未读取游戏客户端。HTTP 和真实探针接入仍未实现。
stdio 的标准输出由 MCP 协议使用，不应插入普通日志。
