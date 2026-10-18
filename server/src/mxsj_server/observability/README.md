# 共享结构化诊断日志

已实现标准库 JSONL sink 与 ContextVar 追踪；不是指标平台、网络日志收集器或可靠资产审计。
由 bootstrap 注入 `EventLogger`，账号、会话、角色与 SQLite 共用；程序化调用未传入时默认仅 stderr，
本地 CLI 则在访问数据库之前打开文件 sink。配置见 [本地入口](../../../../local_server/README.md)。

## 格式与事件

每行独立 JSON，UTC `time`、`level`、固定 `event/component/outcome`。
按适用范围记录 `realm_id/account_id/character_id/session_epoch/duration_ms`、32 位 hex `trace_id`、
`operation_id_sha256`；操作 ID 不记录原文，SHA-256 仅用于关联，不是匿名化保证，请使用随机操作 ID。
无 trace 的入口生成新 trace；可信 RequestContext 复用该 trace，`asyncio.to_thread` 继承上下文。

- `process.start/stop/failed`、`config.validated`、`console.rejected`：启动、退出、输入失败。
- `database.initialize/check/transaction/busy`：schema、事务结果和锁忙。
- `account.provision/authenticate/revoke`：建号、认证、会话撤销。
- `session.context/takeover/stale/expired`：可信上下文、活动会话接管、旧代数、过期。
- `character.list/create/enter_world`：查询、创建、未实现的进图拒绝。

默认 INFO；正常事务成功为 DEBUG，业务拒绝 WARNING、内部／存储错误 ERROR。
业务成功在等待事务提交完成后记录，幂等命中为 `replayed`，失败为 `failed`。
取消线程等待记录 `unknown/CANCELLED_UNKNOWN`：线程仍可能提交，可用相同 trace 查数据库事件，
必须用同一 operation_id 重试，不得把取消理解为回滚。

## 安全与可靠性边界

- 字段与错误码白名单；不序列化请求、响应、用户名、角色名、密码／密码哈希、票据、SQL、reason 或任意异常文本。
  异常只保留允许的类型名与最多 8 个共享服务端／启动器代码位置，不含源码行、locals、cause、args。
- 文件按大小轮替，默认 5 MiB，保留 5 份备份；`server.jsonl.1` 最新，`.5` 最旧。
  支持大小 4096–104857600 字节、备份 1–20 份；没有按天压缩或远端归档。
- `.writer.lock` 使用 OS 排他锁；同一目录只允许一个进程，崩溃后锁自动释放，不需删除锁文件。
  多进程部署必须各用独立目录，不能共享轮替文件。
- 新目录请求 0700、新文件请求 0600；已有路径权限不自动修正，Windows ACL 由操作员配置。
  拒绝明显 symlink/hardlink/非普通文件；目录必须由可信操作员管理，不承诺抵御敌对并发替换路径。
- 初始化无法打开／锁定日志目录则启动失败，不创建业务数据库。
  运行中写入失败不替换业务结果，不回滚已提交业务；`health()` 给出累计 failures 和当前 degraded。
  stderr 固定 `MXSJ_LOGGING_DEGRADED` 告警：连续故障首条及 CLI 退出时提醒，不递归记录内部异常。
  如果文件与 stderr 均不可用，则无法保证告警可见；恢复后允许继续记录，失败计数不清零。
- 同步输出和锁会增加延迟；没有异步队列、集中检索、指标导出或采样。日志 flush 不等于 fsync。
  进程可在数据库提交与成功日志之间崩溃；轮替会淘汰旧记录，日志可被操作员修改。
  **不可把它当余额、物品、奖励的可靠审计账本**。后续资产审计须与业务同事务持久化／outbox 并另做验收。

## 验证

仓库根目录执行 `python -m unittest discover -s server/tests/observability`。
专项覆盖真实文件轮替、进程锁／崩溃释放、敏感字段过滤、输出失败、提交失败、幂等、trace 并发隔离、取消及 CLI 兼容。
Windows 锁／ACL／BAT／EXE 尚未实机验证。
