# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [活动日历、周历与开放时间](../../../../docs/features/activity.calendar.md) | `list_schedule / evaluate_entry_eligibility / query_instance_schedule` |
| [排行榜、历史榜与奖励榜](../../../../docs/features/activity.ranking.md) | `query_ranking / query_historical_ranking / finalize_ranking_rewards` |
| [天梯房间、匹配、段位与赛季](../../../../docs/features/activity.ladder.md) | `create_match_room / join_match_queue / accept_match / claim_season_reward` |
| [赛事战队、赛程、报名和观战](../../../../docs/features/activity.tournaments.md) | `register_tournament_team / query_bracket / schedule_match / subscribe_match` |
| [跨服物品/宠物链接和来源标识](../../../../docs/features/activity.cross_realm_links.md) | `resolve_cross_realm_reference / verify_reference_scope` |
| [帮派Boss、洞窟、烧烤和精英帮战](../../../../docs/features/activity.guild_modes.md) | `enter_guild_activity / update_activity_objective / settle_guild_activity` |
| [国家赛事与阵营活动](../../../../docs/features/activity.country_contest.md) | `enroll_faction_event / query_faction_progress / claim_faction_reward` |
| [小游戏公共框架与活动内小游戏](../../../../docs/features/activity.minigames.md) | `start_minigame / submit_minigame_action / finish_minigame` |
| [回归、召回、回归收集与补偿](../../../../docs/features/activity.returning.md) | `query_returning_status / claim_returning_reward / exchange_collection` |
| [新服、七日目标与签到](../../../../docs/features/activity.new_server.md) | `query_new_server_progress / claim_milestone / sign_in` |
| [礼包、奖励中心与赠礼](../../../../docs/features/activity.reward_center.md) | `list_reward_entitlements / claim_reward_entitlement / give_present` |
| [月卡权益、任务与升级](../../../../docs/features/activity.month_card.md) | `query_card_entitlement / claim_card_task / upgrade_card` |
| [节日、周年与限时活动](../../../../docs/features/activity.festivals.md) | `join_event_instance / progress_event_objective / claim_event_reward` |
