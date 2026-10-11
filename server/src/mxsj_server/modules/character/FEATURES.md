# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [成就、徽章、推荐目标](../../../../docs/features/character.achievement.md) | `list_achievements / claim_achievement_reward / equip_badge` |
| [称谓和称号表现](../../../../docs/features/character.title.md) | `list_titles / equip_title` |
| [坐骑成长、技能、形态与多人座位](../../../../docs/features/character.mount.md) | `list_mounts / train_mount / learn_mount_skill / set_riding_party` |
| [自动升级、属性与流派成长](../../../../docs/features/character.progression.md) | `allocate_attributes / request_level_up / select_progression_plan` |
| [角色靓号与标识](../../../../docs/features/character.pretty_number.md) | `query_identifier_offer / claim_identifier` |
