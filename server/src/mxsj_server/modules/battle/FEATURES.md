# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [人物与召唤兽战斗指令](../../../../docs/features/battle.actions.md) | `submit_action / replace_action_before_lock` |
| [回合推进、托管、掉线与时间窗](../../../../docs/features/battle.turns.md) | `advance_round / apply_timeout / set_auto_policy / resume_battle` |
| [战报编码、观战与录像](../../../../docs/features/battle.reporting.md) | `subscribe_spectator / query_public_battle_view / read_replay` |
| [战前准备、装备方案与附魔方案](../../../../docs/features/battle.preparation.md) | `save_preparation_plan / apply_preparation_plan / snapshot_combatants` |
