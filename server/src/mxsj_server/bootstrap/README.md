# 启动组装与生命周期

当前存在 `game_server.py` 的 loopback JSON-lines 开发入口，可运行注册、选区、登录、建角、选角和进入起始地图的最小闭环。启动命令、请求字段和测试见 [`server/README.md`](../../../README.md)。该入口不是原版客户端协议，不应暴露公网。

其余生产生命周期仍待实现：优雅停机与有界排空、持久化会话恢复、正式 PostgreSQL Unit of Work、完整 runtime 路由/拥有者代数、独立 GM/内部监听及生产观测。只读复核 API/网页仍独立装配。
