# 内部接口契约 v0.1

## 0. 状态与适用范围

当前是可分工的起步接口草案，不是完整玩法 API，也不是原版线协议。
`contracts.py` 是类型约束而非运行时验证器；实现方仍必须检查范围、权限、状态和大小限制。
所有接口字段的新设计必须经负责组审阅后冻结；端口名与客户端函数并非一一对应。

## 1. 请求链路

```text
TCP字节流 → transport帧处理 → legacy/modern协议白名单适配
                                      ↓
                 会话权威校验 → 实体归属路由 → 有界命令投递
                                      ↓
                  应用服务 → 状态拥有者/纯规则 → 仓储/事务
                                      ↓
                  查询视图或回执 → 定向回送 → 编码 → 客户端
```

采用**可拆分接入层**：第一版同进程装配，后续以远程适配器替换投递/回送，
不把 socket、connection_id 或网关节点放入玩法接口。
详细约束见 [GATEWAY.md](GATEWAY.md)，包括会话接管、归属代数、幂等、超时、背压与实施门槛。
这是设计基线，尚未实现独立网关、路由目录或内部通信。

接入层校验帧长度、格式、握手阶段和请求频率；业务层再次校验角色归属、权限、版本和资源。
认证时不能让客户端输入任意 account_id；account.authenticate 例外地接收尚未认证的 LoginRequest，须由接入层限流并保护凭据。

## 2. 公共字段

`RequestContext` 由受信任的接入/调度/管理层生成，不直接解码自客户端：

| 字段 | 语义 |
|---|---|
| operation_id | 稳定的业务幂等键；重复提交同一操作应复用，同键不同参数应拒绝 |
| trace_id | 链路追踪，不承担幂等职责 |
| realm_id | 区服范围；即使ID全局唯一仍校验范围 |
| account_id / character_id | 已认证主体与角色；角色命令要求角色非空并核对归属 |
| session_epoch | 登录接管代数；业务接受边界验证，不能只在网关检查；内部任务可为空 |
| source | client/internal/admin；只是来源，**不替代授权** |

内部实体ID暂以正整数表示；旧协议里一字节战斗单位ID、4字节角色ID等由适配器检查范围并映射，不能无校验截断。
所有金额使用最小单位的整数；时间字段 `*_at_ms` 使用 UTC Unix 毫秒。在线超时用单调时钟，恢复时重新计算剩余时间。
中文内部用 Unicode，Big5 只留在 legacy 编码边界。凭据、票据禁止记录到日志。

## 3. 命令与查询

- 查询返回请求者有权看到的不可变 DTO，不返回数据库对象或内部恢复快照。
- 金币、物品、任务奖励、邮件附件、交易、培养等持久化命令：**提交后才返回成功**。
- 移动、聊天、对话、在线队伍等瞬态命令：回执只表示对应状态拥有者已接受，不自动承诺崩溃恢复。
- 战斗指令若向用户确认“可恢复”，必须先持久化接受记录；第一版实现前需在 BATTLE.md 明确采用哪种恢复保证。
- CommandReceipt.revision 是主实体版本；不等于多个资产对象共享同一版本。
- CreateCharacter、LoginResult 等有独立返回值的命令，也要分别满足创建幂等/会话安全策略。
- `expected_revision` 不匹配时返回冲突；重复操作必须先查幂等结果，不能被重试时的版本变化误判。

基础失败码：`UNAUTHENTICATED`、`FORBIDDEN`、`NOT_FOUND`、`INVALID_ARGUMENT`、`INVALID_STATE`、`VERSION_CONFLICT`、`INSUFFICIENT_RESOURCE`、`RATE_LIMITED`、`TEMPORARILY_UNAVAILABLE`。
使用 DomainError(code) 表示预期业务失败；未处理异常进入统一错误边界，不能原样发送堆栈。
未知提交结果（如数据库提交时断连）不能直接重新执行扣款，必须通过 operation_id 查询已持久化结果。

## 4. 模块间公开端口（已在代码声明）

| 模块 | 起步接口 |
|---|---|
| account | authenticate / revoke_sessions |
| character | list_characters / create / enter_world |
| inventory | list_items / move / use |
| economy | balances / apply_reward（只限内部授权） |
| crafting | craft |
| world | position / move / use_portal |
| npc | interact / select_option |
| battle | submit_action / view / acknowledge_presentation |
| skill | list_learned / learn |
| pet | list_owned / set_active / train |
| children | list_owned / cultivate |
| quest | list_active / accept / claim_reward |
| party | current / invite / respond_invitation |
| guild | current / apply_to_join / review_application |
| social | send_chat / request_friend |
| mail | list_inbox / claim_attachments |
| trade | purchase / cancel_listing |
| housing | place_furniture / visit |
| activity | available / join / claim_reward |
| appearance | owned / equip |
| administration | compensate / ban_account |

命令不能只根据签名机械实现：NPC选项token必须绑定角色/NPC/过期时间；交易以服务器价格为准，maximum_total_price只是买家保护上限；战斗目标与行动参数按种类校验；管理补偿计划必须已审批。

## 5. 跨模块事务：不能串联几个各自提交的公开接口

例如邮件领取：邮件标记、物品发放、货币流水必须在同一事务中。
由 mail 应用服务牵头，复用 persistence 提供的 Unit of Work，调用资产模块的**事务内端口**，一次提交。
这些事务内端口与上表“独立用例接口”分开，当前尚未在 Python 中冻结签名，必须由 C/I/基础设施组先共同完成。
建议签名边界：

```text
InventoryTxn.stage_changes(uow, validated_item_plan) -> provisional_item_result
EconomyTxn.stage_changes(uow, validated_currency_plan) -> provisional_ledger_result
RewardTxn.stage_grant(uow, server_reward_plan, claim_key) -> provisional_reward_result
```

规则：
- plan 只能来自服务端规则与配置，不直接接受客户端指定金额/奖励。
- stage 方法不提交事务、不发网络消息、不提前修改在线已提交视图。
- 外层用例负责提交；提交后更新/失效在线缓存并发出通知。
- 同一用例的幂等记录、领取标记、账本、物品和 outbox 一并提交。
- 客户端价格/数量/ID不可作为已校验结果信任；行锁或条件更新保障数据库并发约束。
- 锁多个实体时按稳定顺序取得；死锁重试须保留幂等键。
- outbox 消费者去重并处理重试/死信，内存事件总线不提供持久化保证。
- ORM会话只属于一个短事务，不与整个玩家连接绑定，也不在并发任务之间共享。

邮件、交易、打造组可并行实现规则和 fake；在事务内端口冻结前，不能声称完成真实资产集成。

## 6. 状态所有权与事件

角色、地图、战斗分别串行处理各自可变状态。数据库约束兜底，单线程 asyncio 本身不是事务隔离。
对外调用不传可变的角色/宠物对象；使用 ID、只读快照与版本。

建议事件信封（尚未定义所有事件载荷）：
`event_id, event_type, schema_version, realm_id, aggregate_id, aggregate_revision, operation_id, occurred_at_ms, payload`。

起步事件：`CharacterCreated`、`InventoryChanged`、`AssetTransactionCommitted`、`MapEntered`、`BattleStarted`、`RoundResolved`、`BattleFinished`、`BattleSettled`、`QuestProgressed`、`MailAttachmentsClaimed`。
事件表示已发生事实，不作为跳过授权的通用远程命令。不承诺全局事件顺序，只声明实体内顺序。

## 7. 协议注册和玩法扩展

接入负责人维护明确白名单 `(protocol_version, opcode, subcode) -> adapter`，适配器构造业务命令。
不能使用客户端传来的模块名动态 import 或 eval。原协议尚未核实的字段标为待验证，不根据DTO生成假定报文。
配置必须有来源、schema、配置版本、校验器；运行中战斗固定规则版本，禁止热加载污染正在执行的回合。


## 8. 补充盘点后的接口缺口

21个模块的起步 Protocol 不能代表完整API。详细缺口见 `SUBSYSTEMS.md` 和 `features/` 下81个工作包设计卡。
仓库、坐骑、成就、生产/工厂、拍卖、角色交易、排名/赛事、新手、月卡、支付和安全等均需补充操作与字段。
这些卡片目前只有接口名字与职责，**不是类型化接口，也不保证接口已冻结**。
新增独立模块（如 mount、achievement、profession、ranking、competition、billing 等）是待确认的拆分建议，未擅自移动现有所有权。
各组先在自己模块的 `design/<feature_id>.md` 细化；集成负责人确认后再写入 contracts.py 或新增公开契约文件。

## 9. 接入可拆分约束

- RequestContext 保持业务上下文；session_id、连接回送句柄和路由元数据放在外层可信信封，不进入玩法参数。
- request_id 关联单次请求；operation_id 去重同一业务操作；session_epoch 隔离旧会话；owner_epoch 隔离旧归属。
  这四者不能相互替代。跨进程消息按白名单和版本校验，不直接反序列化 Python 对象。
- 同一区服同账号第一版只允许一个活动会话/一个已选角色；接管与命令接受按拥有者顺序处理。
  接管前已合法接受的命令不保证撤销；需要提交 fencing 的业务必须与持久化层联合实现。
- 路由失败只有在明确未接受执行时才允许重新投递；超时/断链导致未知结果时按原 operation_id 恢复。
  网关默认不自动重试有副作用请求，客户端缺少稳定幂等键时必须先解决协议适配。
- 业务回执不等于 TCP ACK，推送失败不回滚已提交结果；断线重连通过授权快照/版本恢复。
- GATEWAY.md 中的 SessionAuthority、OwnerDirectory、CommandDispatcher、ClientDelivery 是待实现端口，
  尚未加入本文件 §4 的已声明 Python Protocol 清单，不得误认为已经能部署。
