# 管理与运营（`administration`）

状态：**v0.1 接口草案 / 无业务实现**。负责人：待分配，不代表需要独立一个人。

## 独占负责范围

管理命令授权、审计、封禁/补偿用例、操作追踪；只调用业务公开接口。

## 不负责 / 禁止越界

复用客户端GM脚本执行任意代码、直接改在线角色数据。

## 本组可修改的路径

- `server/src/mxsj_server/modules/administration/`
- `server/tests/modules/administration/`
- 后续本模块 SQLAlchemy 模型放在自己的 `adapters/`，不是公共大 models.py。
- 对外接口是本目录 `contracts.py`；接口变更须与调用方确认。

## 客户端材料

均来自 `data/script.fls`。下表中的历史 `ok` **不是源码语义正确或服务端规则完整的证明**。
当前检查只验证 marshal 转译及根文件名；函数行为抽查见 `docs/SOURCE_EVIDENCE.md`。

| 条目 | 文件名 | 历史解码状态 | 当前检查 |
|---|---|---|---|
| 3257 | `script/netchat.py` | ok | marshal_transpiled_filename_checked |

前缀检索命中 0 条，仅用于定位研究范围，不是玩法完成度；主参考可能与其他模块重叠。

## 实现入口与验收

- `contracts.py`：类型化公开接口；**新设计的内部 API，不是原版网络协议**。
- `application/`：命令处理、认证授权、幂等、事务与跨模块协调。
- `domain/`：业务规则和状态，不依赖 TCP、FastAPI、SQLAlchemy。
- `adapters/`：数据库和其他外部系统适配。
- 不导入别的模块的 `domain/`、`application/` 或 `adapters/`；跨模块只使用公开契约。
- 实现前：补齐操作前置条件、失败码、字段约束、数据模型和材料缺口。
- 提交时：成功、越权、重复操作、失败恢复测试；需要协议的模块补报文样本测试。
- 当前接口仅覆盖起步用例，不代表本模块全部功能。

## 更细的分工

见本目录 [FEATURES.md](FEATURES.md)。一级契约不是完整功能清单；人工设计请放本目录 design/，不要改生成的材料卡。

## 多功能网关与 GM 控制面设计

人工设计见 [GATEWAY_SECURITY_GM.md](../../../../docs/GATEWAY_SECURITY_GM.md)。
公网游戏入口不暴露本模块；私有 GM 入口只做认证/适配/权限初检，本模块负责再次授权、
审批计划、可靠任务和审计，并调用业务端口，不直接修改别的模块的私有表/在线对象。

当前 compensate / ban_account 只是类型草案；source=admin 不是授权。
实施前须联合冻结独立员工身份、管理上下文、审批摘要、范围/额度、目标级结果与持久化审计。
高风险操作不得自批；同操作幂等，未知结果不自动重试发奖；业务与审计/outbox 在正确事务边界提交。
查询、踢线/撤销、限时处罚先行；公告/维护、补偿、策略、救援和配置按业务成熟度分期开放。
禁止 SQL/shell/eval/任意 Python 或“万能 GM 命令”入口。
