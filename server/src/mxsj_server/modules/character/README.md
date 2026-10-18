# 角色与成长（`character`）

状态：**共享服务第一阶段**：基于显式策略的角色元数据创建／查询、归属校验及幂等；完整角色初始化、进图／成长仍待实现。本地运行和验收边界见 [local_server](../../../../../local_server/README.md)。

本轮由当前集成会话实现，不代表后续所有玩法已分配。

## 独占负责范围

建角、选角、等级经验、基础属性、修炼、称谓与成就；协调角色生命周期。

## 不负责 / 禁止越界

背包、货币直接写入、战斗临时血量。

## 本组可修改的路径

- `server/src/mxsj_server/modules/character/`
- `server/tests/modules/character/`
- 后续本模块 SQLAlchemy 模型放在自己的 `adapters/`，不是公共大 models.py。
- 对外接口是本目录 `contracts.py`；接口变更须与调用方确认。

## 客户端材料

均来自 `data/script.fls`。下表中的历史 `ok` **不是源码语义正确或服务端规则完整的证明**。
当前检查只验证 marshal 转译及根文件名；函数行为抽查见 `docs/SOURCE_EVIDENCE.md`。

| 条目 | 文件名 | 历史解码状态 | 当前检查 |
|---|---|---|---|
| 3038 | `script/hero.py` | ok | marshal_transpiled_filename_checked |
| 826 | `script/nethero.py` | ok | marshal_transpiled_filename_checked |

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
