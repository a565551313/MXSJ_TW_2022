# 数据库迁移与恢复

## 当前实现：SQLite 本地基础 v1

SQL 真源是 [`persistence/sqlite/schema.py`](../src/mxsj_server/persistence/sqlite/schema.py)，
包含 accounts、sessions、characters、operations 和 schema_migrations，及角色归属索引。
这只是账号／会话／角色元数据，不是完整角色、资产或地图 schema。

仅显式 `local_server/run.py --config ... init-db` 初始化：
- 独立 application_id、user_version 与迁移 checksum；同版本重复运行幂等。
- DDL、迁移记录和版本标记在同一事务；不用隐式提交的 executescript。
- 未初始化的启动、未知新版本、迁移摘要不匹配、外部／损坏库均拒绝；没有自动删除重建或降级。
- 角色创建／幂等回执、撤销／幂等回执各自同事务提交；sessions.epoch 持久化，不因重启归零。
- 外键、唯一约束和 SQLite writer 锁共同约束并发，不能只依赖 Python 内存锁。

**恢复要求**：先停止所有访问该数据库的进程，保留原文件及现存 journal/WAL 辅助文件，使用 SQLite 支持的备份／恢复方式。
不得在活跃数据库上简单复制主文件就宣称备份一致；不要删除 journal 或手动改 version 来绕过错误。
当前仅 v1，尚无 v1→v2 升级或 downgrade 工具；将来新增迁移须备份、事务执行并做故障恢复测试。

## PostgreSQL 尚未实现

正式数据库不是把 SQLite 文件改名／换 URI。未来适配须提供等效约束、行锁、事务、会话代数与幂等，并运行共享与专属并发验收。
具体表／迁移由集成负责人统一；领域业务不持有连接、不写 SQLite 专有 SQL。
入口与阶段边界见 [local_server](../../local_server/README.md)。
