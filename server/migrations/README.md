# 数据库迁移

`0001_playable_loop.sql` 是**SQLite 开发原型**使用的首个 schema，用于验证注册、区服、认证会话、角色和地图位置的闭环；它不是生产 PostgreSQL 迁移。生产迁移链、PostgreSQL 适配、备份/恢复与并发 fencing 仍待实现和验收。

不要把原型 SQLite 数据库当成正式账号/角色数据；原型尚无线上部署保证。
