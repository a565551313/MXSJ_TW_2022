# 一级模块清单 v0.1

> **这是一级责任区，不是完整玩法列表。** 补充的81个二级/三级工作包见 [SUBSYSTEMS.md](SUBSYSTEMS.md)，全量材料见 [目录索引](catalog/DIRECTORIES.md)。新增子系统接口尚未全部落实到Python契约。

该清单是**材料驱动的开发责任边界**，不是原版服务端目录的还原，也不是全部玩法枚举。模块可由同一人兼任；角色名不是已分配到具体人。

| 模块 | 建议协作组 | 独占负责范围 | 起步材料（script.fls 条目） |
|---|---|---|---|
| [account](../src/mxsj_server/modules/account/README.md) · 账号与认证 | A 基础设施/认证 | 账号认证、封禁、登录票据；不长期持有数据库事务 | 4082, 516, 1607, 4289, 164, 337 |
| [character](../src/mxsj_server/modules/character/README.md) · 角色与成长 | B 角色成长 | 建角、选角、等级经验、基础属性、修炼、称谓与成就；协调角色生命周期 | 3038, 826 |
| [economy](../src/mxsj_server/modules/economy/README.md) · 经济与奖励 | C 资产与制造 | 货币、资产流水、奖励计划执行与幂等；与 inventory 在同一工作单元完成资产事务 | 826, 1498, 2020 |
| [inventory](../src/mxsj_server/modules/inventory/README.md) · 背包与装备实例 | C 资产与制造 | 物品归属、数量、位置、装备槽、绑定、消耗及持久化；装备实例由本模块写入 | 3745, 1766, 1108, 17, 135, 519 |
| [crafting](../src/mxsj_server/modules/crafting/README.md) · 打造与装备加工 | C 资产与制造 | 配方、鉴定、强化、熔炼等操作规则；组织材料消耗与产物发放的事务 | 1, 1203, 31, 52, 69, 258 |
| [world](../src/mxsj_server/modules/world/README.md) · 地图与世界实例 | D 世界与交互 | 地图实例、位置、移动校验、可见范围、传送、进入离开和世界对象 | 3110, 826, 1301, 159, 189, 1430 |
| [npc](../src/mxsj_server/modules/npc/README.md) · NPC与交互 | D 世界与交互 | NPC交互距离、对话会话、选项、服务入口；将交易和任务交给对应模块 | 731 |
| [battle](../src/mxsj_server/modules/battle/README.md) · 战斗运行时与结算协调 | E 战斗 | 战斗生命周期、行动收集、超时、回合推进、状态拥有权、战报、重连视图与结算协调 | 1406, 697, 1721, 660, 44, 58 |
| [skill](../src/mxsj_server/modules/skill/README.md) · 技能与状态效果 | B 角色成长 | 角色技能学习、技能规则目录、伤害与治疗等效果、Buff、公式及规则版本；纯计算接口另行细化 | 454, 3255, 2242 |
| [pet](../src/mxsj_server/modules/pet/README.md) · 宠物与召唤兽 | F 宠物与子女 | 宠物实例、归属、培养、成长、技能、出战配置；提供参战快照 | 1599, 1355, 4345, 142, 584, 765 |
| [children](../src/mxsj_server/modules/children/README.md) · 子女系统 | F 宠物与子女 | 子女实例、培养、技能和出战配置；与宠物分开所有权 | 1059, 91, 237, 263, 316, 363 |
| [quest](../src/mxsj_server/modules/quest/README.md) · 任务与剧情 | G 任务与活动 | 任务状态、条件检查、推进、放弃、完成和奖励领取；管理剧情进度 | 4913, 3221, 1501, 1308, 23, 166 |
| [party](../src/mxsj_server/modules/party/README.md) · 队伍 | H 社交组织 | 组队邀请、申请、队长、成员、跟随和队伍准备快照 | 3636, 2889, 1790, 296, 307, 503 |
| [guild](../src/mxsj_server/modules/guild/README.md) · 帮派 | H 社交组织 | 帮派创建、成员、职务、权限、建设、帮贡规则与帮派玩法入口 | 1028, 20, 62, 89, 97, 112 |
| [social](../src/mxsj_server/modules/social/README.md) · 聊天与关系 | H 社交组织 | 好友、黑名单、频道、私聊、婚姻、师徒和结拜子域；分别保留内部子目录扩展位 | 4238, 3257, 319, 2642, 4397, 106 |
| [mail](../src/mxsj_server/modules/mail/README.md) · 邮件 | I 邮件与交易 | 系统邮件、玩家邮件、过期、附件领取状态；附件托管与领取原子性 | 2725 |
| [trade](../src/mxsj_server/modules/trade/README.md) · 商店交易与寄售 | I 邮件与交易 | NPC商店、玩家交易、摊位/商店、寄售订单、库存、价格、手续费和托管 | 122, 1498, 1848, 2020, 2777, 12 |
| [housing](../src/mxsj_server/modules/housing/README.md) · 家园与庭院 | D 世界与交互 | 家园实例、家具实例归属与摆放、访问权限、种植养殖子域 | 1387, 3179, 3057, 649, 3599, 4461 |
| [activity](../src/mxsj_server/modules/activity/README.md) · 活动与副本编排 | G 任务与活动 | 活动目录、开放时间、参与资格、进度、奖励资格、副本和小游戏编排；大型活动可在内部拆负责人 | 7, 47, 75, 96, 120, 185 |
| [appearance](../src/mxsj_server/modules/appearance/README.md) · 外观与收藏 | B 角色成长 | 外观解锁、穿戴、染色、坐骑外观及收藏进度；消耗走资产事务 | 269, 1242, 2483, 3131, 28, 105 |
| [administration](../src/mxsj_server/modules/administration/README.md) · 管理与运营 | A 基础设施/认证 | 管理命令授权、审计、封禁/补偿用例、操作追踪；只调用业务公开接口 | 3257 |

## 分类原则

- 客户端目录往往按界面/MVC分层，服务端按权威数据所有权分组，不机械照搬。
- 一个客户端脚本可为多个服务端模块提供线索，例如 nethero 涉及角色属性和地图移动；这不代表允许多个模块直接写同一份状态。
- `skill` 管规则定义与技能学习，`battle` 管实例和执行顺序；两组共同确认效果接口。
- `inventory` 管物品实例；`crafting` 只组织加工用例；`economy` 协调奖励/资产事务。
- `activity` 负责玩法编排，不重复实现战斗、任务和资产系统。活动内部再按具体活动分负责人。
- 婚姻、师徒、结拜暂属 `social` 的独立子域；子女独立为 `children`。
- 成就、称谓与非战斗修炼先归 `character`；具体来源和内部子域清单仍需角色组核对。
- 商城/支付渠道回调、跨服、反作弊、全服排行榜等尚未制定专门契约，**不能认为已完整覆盖**。涉及真实支付时应单独评审订单、支付验证和对账模块。

## 第一版接口边界

每个模块 `contracts.py` 已定义至少一个 Python Protocol 和类型化方法。
这是可导入的类型声明，业务方法没有实现；字段是新设计，不能按其顺序直接拼客户端报文。
本清单的接口只覆盖起步用例，完整接口需按各模块材料进一步补充。

## 数据所有权建议（尚未生成表）

| 数据 | 唯一业务写入方 |
|---|---|
| 账号/认证凭据 | account |
| 角色基础与成长 | character |
| 钱包与资产流水 | economy |
| 物品、装备、背包槽位与托管归属 | inventory |
| 加工操作记录 | crafting |
| 地图在线位置与可见集合 | world |
| 战斗快照、输入、结果与结算状态 | battle |
| 宠物 / 子女 | pet / children |
| 任务进度与领取状态 | quest |
| 队伍 / 帮派 / 社交关系 | party / guild / social |
| 邮件与领取标记 / 交易订单 | mail / trade |
| 家具实例、摆放与访问权限 | housing |
| 活动进度 / 外观解锁 | activity / appearance |
| 管理授权与操作审计 | administration |

物品从背包变成家园家具等跨域转换，必须在明确事务中转移所有权，禁止复制为两份可消费资产。
数据库由各模块模型协作组成，不要求每模块独立数据库；区服/账号范围约束由迁移设计统一落实。
