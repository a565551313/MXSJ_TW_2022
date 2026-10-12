# MXSJ Python 服务端工程骨架

**状态：模块边界与内部接口 v0.1 草案。游戏运行时尚无网络服务、数据库实现或可游玩业务；独立只读复核 API/网页已交付。**

本地与公区共用业务代码与数据一致性要求；本次只建立多人开发基线。
没有修改客户端、FLS、原有 Mock 或旧逆向工具；没有将客户端脚本当作可信服务端运行。
Pygame 不属于本项目服务端依赖。技术方向为 asyncio + PostgreSQL；具体依赖锁定由基础设施组统一完成。

## 完整度说明（补充盘点）

**21个目录是一级责任区，不是全部玩法。** 当前进一步建立81个细分工作包及5002条完整材料索引。
先读[细分子系统与接口缺口](docs/SUBSYSTEMS.md)，再读一级模块。新增接口仅为设计卡，不能误认为已有代码实现。
完整条目覆盖不等于完整玩法覆盖：3348个条目尚未映射到这81个工作包。

## 阅读顺序

1. [模块清单](docs/MODULES.md)：21 个模块、负责范围与材料入口。
2. [协作与所有权](docs/OWNERSHIP.md)：谁可以改哪些目录，公共变更怎么协调。
3. [接口与一致性约定](docs/INTERFACES.md)：认证、命令、查询、幂等与事务。
4. [战斗交接契约](docs/BATTLE.md)：角色/宠物/世界/技能/资产的边界。
5. [材料证据与局限](docs/SOURCE_EVIDENCE.md)：已核对事实与新设计的区别。
6. [分工启动任务](docs/WORK_PACKAGES.md)：各组可以先做什么。
7. [非玩法基础能力缺口](docs/FOUNDATION_BACKLOG.md)：接入、可靠性、运维与支付等工程要求。
8. [客户端配置异常复核](docs/CLIENT_DATA_REVIEW.md)：道具/宠物表的边界修复候选、未解决记录和正式CSV的准入条件（非生产配置）。
9. [CSV可提取性清单](docs/CSV_READINESS.md)：33个脚本、48个表目标的结构/文字/部分关联检查，区分待审候选、异常隔离和未恢复目标。
10. [可拆分网关设计](docs/GATEWAY.md)：第一版同进程接入，预留独立网关；会话、路由、回送、幂等与故障边界。设计已纳入基线，运行实现尚未交付。

## 目录

```text
src/mxsj_server/
  bootstrap/       启动组装（基础设施组）
  runtime/         会话、状态拥有者、队列和调度（基础设施组）
  transport/       TCP与流控（接入负责人）
  protocol/        legacy/modern 协议适配（接入负责人）
  contracts/       共享DTO与错误模型（集成负责人）
  persistence/     连接池和事务基础设施（基础设施组）
  observability/   日志、指标、追踪（基础设施组）
  modules/<name>/  每个玩法的独立责任区
    contracts.py   公开类型化接口
    domain/        业务规则
    application/   用例与事务协调
    adapters/      数据库/外部适配
    README.md      独占职责、材料和验收
migrations/        迁移链，指定负责人集成
game_data/        静态配置（当前为空）
tests/modules/    每模块自有测试目录
tests/integration/  跨模块事务、恢复测试
tests/protocol/     报文测试
tests/simulation/   战斗模拟与机器人测试
tools/ deploy/    配置导出、运维和部署预留
```

## 检查骨架

仅需要 Python 3.11+ 标准库；生产 Python 版本和依赖尚未锁定。
从仓库根目录运行：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s server/tests/architecture -v
PYTHONDONTWRITEBYTECODE=1 python3 server/tools/verify_source_map.py
```

这些测试只证明目录、契约和静态依赖边界，不证明玩法、协议兼容性或持久化正确。
目前没有可游玩服务端的启动命令，不能将契约文件直接部署为游戏服务器。
只读数据复核工具另见 [验收与运行说明](docs/review_browser/ACCEPTANCE.md)，不属于游戏网关。
