# 二级/三级子系统与接口缺口清单

**上一版21项是一级责任区，不是完整玩法清单。这里展开工作包，不把目录数当玩法数。**

- 全量索引覆盖 5002 个 script.fls 条目；见[原始索引与异常清单](catalog/DIRECTORIES.md)。
- 当前已细分 81 个跨目录工作包；包含客户端材料线索和服务端新增工程要求，并不代表81套原版逻辑已还原。
- `contracts.py` 仍只有上一版起步用例。本页新增接口为**文字级设计建议，未生成可执行方法、未冻结字段**。
- 后续代码目录/迁移/跨域事务需按这些工作包进一步细分；本次不盲目制造未核实的业务实现。

| 工作包 | 当前责任区 | 客户端材料命中 | 接口起点（新设计） |
|---|---|---:|---|
| [账号安全、二次密码和异常登录保护](features/account.security.md) | `account` | 1 | `request_protection_change / confirm_protection_change` |
| [登录排队](features/account.login_queue.md) | `account` | 2 | `join_queue / query_queue / cancel_queue` |
| [短信验证与未成年人保护](features/account.identity_protection.md) | `account` | 2 | `request_verification / verify_challenge / evaluate_login_policy` |
| [成就、徽章、推荐目标](features/character.achievement.md) | `character` | 2 | `list_achievements / claim_achievement_reward / equip_badge` |
| [称谓和称号表现](features/character.title.md) | `character` | 2 | `list_titles / equip_title` |
| [坐骑成长、技能、形态与多人座位](features/character.mount.md) | `character` | 16 | `list_mounts / train_mount / learn_mount_skill / set_riding_party` |
| [自动升级、属性与流派成长](features/character.progression.md) | `character` | 15 | `allocate_attributes / request_level_up / select_progression_plan` |
| [角色靓号与标识](features/character.pretty_number.md) | `character` | 7 | `query_identifier_offer / claim_identifier` |
| [仓库、保险仓、租赁和续租](features/inventory.warehouse.md) | `inventory` | 1 | `list_storage / transfer_storage_item / rent_storage / renew_storage` |
| [仓库密码、锁定、检索与整理](features/inventory.warehouse_security.md) | `inventory` | 1 | `unlock_storage / change_storage_protection / search_storage / arrange_storage` |
| [临时背包与特殊场景物品](features/inventory.virtual_bag.md) | `inventory` | 1 | `list_temporary_items / use_temporary_item / move_temporary_item` |
| [物品扩展属性与快捷栏](features/inventory.extension.md) | `inventory` | 2 | `query_item_details / set_item_shortcut` |
| [装备打造、打造符与鉴定](features/crafting.creation.md) | `crafting` | 1 | `preview_craft / craft_equipment / identify_equipment` |
| [装备熔炼与结果确认](features/crafting.smelting.md) | `crafting` | 2 | `preview_smelting / perform_smelting / confirm_smelting` |
| [宝石合成、镶嵌、拆卸与转换](features/crafting.gems.md) | `crafting` | 1 | `combine_gems / inlay_gem / remove_gem / transform_gem` |
| [生活生产、采集与作物](features/crafting.production.md) | `crafting` | 3 | `start_production / gather_resource / harvest_crop` |
| [工厂经营、雇工和产品订单](features/crafting.factory.md) | `crafting` | 2 | `create_factory / post_job / accept_job / place_product_order` |
| [飞行旗、传送、寻路与移动](features/world.travel.md) | `world` | 5 | `use_travel_point / validate_movement / enter_map` |
| [副本空间与进入离开](features/world.instance.md) | `world` | 1 | `create_instance / enter_instance / leave_instance` |
| [动态NPC、场景物品和副本对象](features/world.dynamic_entities.md) | `world` | 1 | `spawn_world_entity / remove_world_entity / interact_world_entity` |
| [对话、选项、输入与给予](features/npc.dialogue.md) | `npc` | 1 | `open_dialogue / answer_dialogue / submit_dialogue_input / give_items` |
| [人物与召唤兽战斗指令](features/battle.actions.md) | `battle` | 1 | `submit_action / replace_action_before_lock` |
| [回合推进、托管、掉线与时间窗](features/battle.turns.md) | `battle` | 2 | `advance_round / apply_timeout / set_auto_policy / resume_battle` |
| [战报编码、观战与录像](features/battle.reporting.md) | `battle` | 9 | `subscribe_spectator / query_public_battle_view / read_replay` |
| [战前准备、装备方案与附魔方案](features/battle.preparation.md) | `battle` | 25 | `save_preparation_plan / apply_preparation_plan / snapshot_combatants` |
| [门派/流派技能与学习](features/skill.school.md) | `skill` | 2 | `list_skill_tree / learn_skill / upgrade_skill` |
| [状态、技能效果与结算顺序](features/skill.effects.md) | `skill` | 2 | `resolve_effect / apply_status / expire_status` |
| [技能预览与推荐](features/skill.preview.md) | `skill` | 4 | `preview_skill / recommend_skill_plan` |
| [炼妖、合宠、还童与预览](features/pet.refinement.md) | `pet` | 29 | `preview_refinement / refine_pet / combine_pet / confirm_pet_result` |
| [召唤兽天赋及方案](features/pet.talent.md) | `pet` | 2 | `learn_talent / reset_talent / save_talent_plan / replace_talent_result` |
| [召唤兽技能学习与打书](features/pet.skills.md) | `pet` | 2 | `learn_pet_skill / use_pet_skill_book / unlock_pet_skill_slot` |
| [召唤兽图鉴与收藏奖励](features/pet.bestiary.md) | `pet` | 2 | `query_bestiary / claim_collection_reward` |
| [召唤兽装备、寄存与出战](features/pet.equipment_storage.md) | `pet` | 2 | `equip_pet_item / store_pet / withdraw_pet / set_active_pet` |
| [子女培养与成长](features/children.cultivation.md) | `children` | 26 | `query_child_growth / cultivate_child / select_child_training` |
| [子女技能与参战](features/children.combat.md) | `children` | 2 | `assign_child_skill / select_child_for_battle` |
| [剧情、任务条件与分支](features/quest.story.md) | `quest` | 328 | `accept_story_task / evaluate_objective / progress_story / claim_story_reward` |
| [任务追踪、导航与交付](features/quest.tracking.md) | `quest` | 15 | `set_tracking / query_task_targets / submit_task_items` |
| [新手引导、变强指引与章节奖励](features/quest.onboarding.md) | `quest` | 25 | `query_guide_chapters / advance_guide_objective / claim_chapter_reward` |
| [队伍招募、申请、邀请与跟随](features/party.recruitment.md) | `party` | 2 | `publish_recruitment / apply_to_party / approve_application / set_follow` |
| [日常固定队与队长激励](features/party.daily.md) | `party` | 22 | `query_daily_team / register_daily_team / claim_captain_reward` |
| [成员、职务、申请、公告与权限](features/guild.membership.md) | `guild` | 1 | `apply_membership / review_membership / assign_role / edit_announcement` |
| [帮派建设、资金与升级](features/guild.construction.md) | `guild` | 2 | `query_buildings / contribute_resources / upgrade_building` |
| [帮派合并](features/guild.merger.md) | `guild` | 1 | `request_guild_merge / approve_guild_merge / execute_guild_merge` |
| [帮派红包与领袖成长](features/guild.red_packets.md) | `guild` | 2 | `create_guild_red_packet / claim_guild_red_packet / claim_leader_title` |
| [好友、黑名单、关系与离线通知](features/social.friendship.md) | `social` | 1 | `request_friend / accept_friend / block_character / query_relationship` |
| [婚姻与配偶玩法](features/social.marriage.md) | `social` | 19 | `request_marriage / confirm_marriage / request_divorce` |
| [师徒关系与师徒任务](features/social.mentorship.md) | `social` | 19 | `request_mentorship / confirm_mentorship / graduate_apprentice` |
| [结拜及成员关系](features/social.sworn.md) | `social` | 32 | `create_sworn_group / invite_sworn_member / leave_sworn_group` |
| [频道、私聊、语音与传音](features/social.chat.md) | `social` | 5 | `send_channel_message / send_private_message / publish_voice_reference` |
| [空间、相册、动态与互动](features/social.community.md) | `social` | 74 | `publish_post / list_feed / react_to_post / report_content` |
| [报纸、文章、广告与审核](features/social.newspaper.md) | `social` | 1 | `submit_article / review_article / publish_newspaper / buy_ad_slot` |
| [系统邮件、通知与附件](features/mail.system.md) | `mail` | 1 | `send_system_mail / list_inbox / claim_attachments` |
| [玩家邮件与离线消息](features/mail.player.md) | `mail` | 5 | `send_player_mail / read_mail / delete_mail` |
| [NPC商店、玩家商店与物品定价](features/trade.shop.md) | `trade` | 3 | `list_shop_goods / purchase_goods / set_shop_price / deposit_shop_funds` |
| [寄售、交易中心与订单](features/trade.consignment.md) | `trade` | 61 | `create_listing / purchase_listing / cancel_listing / claim_sale_proceeds` |
| [竞拍、自动出价与结拍](features/trade.auction.md) | `trade` | 9 | `place_bid / set_auto_bid / cancel_auto_bid / settle_auction` |
| [角色交易与资产展示](features/trade.role_market.md) | `trade` | 6 | `query_sale_character / prepare_character_listing / confirm_ownership_transfer` |
| [家具摆放、地块和家园编辑](features/housing.editing.md) | `housing` | 121 | `place_furniture / move_furniture / expand_plot` |
| [家园访问、家具权限与使用](features/housing.visiting.md) | `housing` | 43 | `visit_house / set_house_permissions / use_furniture` |
| [庭院种植与收获](features/housing.plants.md) | `housing` | 8 | `plant_seed / tend_plant / harvest_plant` |
| [鱼塘、观赏鱼与幸运鱼](features/housing.fish.md) | `housing` | 40 | `stock_fish / feed_fish / harvest_fish / claim_fish_reward` |
| [家园收藏与展示](features/housing.exhibition.md) | `housing` | 3 | `set_exhibition / query_exhibition` |
| [活动日历、周历与开放时间](features/activity.calendar.md) | `activity` | 24 | `list_schedule / evaluate_entry_eligibility / query_instance_schedule` |
| [排行榜、历史榜与奖励榜](features/activity.ranking.md) | `activity` | 3 | `query_ranking / query_historical_ranking / finalize_ranking_rewards` |
| [天梯房间、匹配、段位与赛季](features/activity.ladder.md) | `activity` | 53 | `create_match_room / join_match_queue / accept_match / claim_season_reward` |
| [赛事战队、赛程、报名和观战](features/activity.tournaments.md) | `activity` | 65 | `register_tournament_team / query_bracket / schedule_match / subscribe_match` |
| [跨服物品/宠物链接和来源标识](features/activity.cross_realm_links.md) | `activity` | 2 | `resolve_cross_realm_reference / verify_reference_scope` |
| [帮派Boss、洞窟、烧烤和精英帮战](features/activity.guild_modes.md) | `activity` | 33 | `enter_guild_activity / update_activity_objective / settle_guild_activity` |
| [国家赛事与阵营活动](features/activity.country_contest.md) | `activity` | 105 | `enroll_faction_event / query_faction_progress / claim_faction_reward` |
| [小游戏公共框架与活动内小游戏](features/activity.minigames.md) | `activity` | 17 | `start_minigame / submit_minigame_action / finish_minigame` |
| [回归、召回、回归收集与补偿](features/activity.returning.md) | `activity` | 42 | `query_returning_status / claim_returning_reward / exchange_collection` |
| [新服、七日目标与签到](features/activity.new_server.md) | `activity` | 15 | `query_new_server_progress / claim_milestone / sign_in` |
| [礼包、奖励中心与赠礼](features/activity.reward_center.md) | `activity` | 96 | `list_reward_entitlements / claim_reward_entitlement / give_present` |
| [月卡权益、任务与升级](features/activity.month_card.md) | `activity` | 4 | `query_card_entitlement / claim_card_task / upgrade_card` |
| [节日、周年与限时活动](features/activity.festivals.md) | `activity` | 42 | `join_event_instance / progress_event_objective / claim_event_reward` |
| [外观解锁、穿戴、染色与装饰](features/appearance.cosmetics.md) | `appearance` | 88 | `unlock_appearance / equip_appearance / change_color` |
| [翅膀展示与相关养成材料](features/appearance.wings.md) | `appearance` | 9 | `query_wing_state / change_wing_appearance` |
| [世界红包、系统红包与领用](features/economy.red_packets.md) | `economy` | 11 | `create_red_packet / claim_red_packet / expire_red_packet` |
| [充值订单、支付验证、补单与对账](features/administration.payment.md) | `administration` | 19 | `create_payment_order / accept_verified_provider_event / reconcile_payment_order` |
| [申诉、举报与客服入口](features/administration.customer_support.md) | `administration` | 2 | `submit_report / review_case / apply_audited_resolution` |
| [开关、补偿、停服与运营审计](features/administration.operations.md) | `administration` | 12 | `set_feature_policy / issue_approved_compensation / schedule_maintenance` |

## 不要遗漏活动的独立分支

下面展开当前索引里全部活动分支，包括公共框架、测试和历史活动；不能把每个目录都算成一个独立线上玩法。

| 分支 | 材料条目数 | 代表条目 |
|---|---:|---|
| `2018worldcup` | 3 | 2557, 4349, 4451 |
| `2019double12shop` | 16 | 119, 439, 491, 1036, 1655, 1882 |
| `2019znq` | 13 | 47, 906, 1439, 1997, 2051, 2632 |
| `2021duangwu` | 19 | 83, 456, 542, 952, 1101, 1116 |
| `2021newyeargift` | 9 | 372, 510, 919, 1099, 1136, 1300 |
| `2021newyearrank` | 10 | 126, 268, 1111, 1940, 2575, 2653 |
| `2021springactivity` | 10 | 11, 750, 758, 1341, 1510, 1763 |
| `2021springjifu` | 5 | 53, 156, 3814, 3828, 4488 |
| `2021summer` | 10 | 180, 915, 1312, 1455, 1889, 1912 |
| `2021summerlottery` | 7 | 7, 2042, 2057, 2137, 2626, 3258 |
| `acteye` | 11 | 334, 521, 839, 1026, 1610, 1842 |
| `activitymainbase` | 8 | 88, 583, 619, 801, 1489, 1983 |
| `allserverboss` | 10 | 1369, 1403, 1702, 2388, 2567, 3165 |
| `annualbeauty` | 58 | 4, 14, 19, 297, 301, 341 |
| `bestlover` | 9 | 120, 1329, 1494, 1787, 2387, 2731 |
| `cardgame` | 13 | 133, 157, 487, 721, 835, 971 |
| `cookfight` | 3 | 696, 2436, 3039 |
| `countrycontest` | 75 | 199, 204, 206, 232, 281, 289 |
| `dailykeju` | 7 | 286, 511, 1777, 2185, 2891, 3833 |
| `dengmi` | 1 | 1449 |
| `eliteorgwar` | 10 | 191, 761, 1253, 1949, 1991, 2503 |
| `fashionactive` | 4 | 2073, 2831, 3584, 4561 |
| `fightpig` | 1 | 4967 |
| `firehouse` | 1 | 4521 |
| `formation` | 3 | 186, 2190, 2821 |
| `gameplaymethodselection` | 7 | 1282, 1844, 2164, 2529, 3976, 4295 |
| `gopenguin` | 16 | 462, 738, 810, 1259, 1290, 1309 |
| `groupbbq` | 11 | 108, 1860, 1981, 2603, 2819, 2881 |
| `groupboss` | 2 | 2667, 3276 |
| `guildcavern` | 10 | 1324, 1502, 1821, 2238, 3026, 3089 |
| `heartychocolate` | 7 | 1757, 1950, 2202, 2310, 3332, 3747 |
| `helppresent` | 4 | 2174, 2272, 2432, 4930 |
| `insidewar` | 30 | 80, 209, 534, 538, 693, 827 |
| `keju` | 6 | 1013, 1043, 1554, 2970, 4853, 4878 |
| `labyrinth_treasure` | 3 | 3953, 4465, 4567 |
| `ladderrank` | 15 | 96, 261, 501, 752, 1279, 1287 |
| `ladderrankallstar` | 38 | 183, 279, 433, 682, 687, 831 |
| `mengxiang3activity` | 29 | 200, 217, 223, 321, 350, 815 |
| `minitimewheel` | 3 | 2543, 4058, 4241 |
| `mizong` | 4 | 522, 1114, 3406, 3604 |
| `motherday` | 5 | 676, 936, 1106, 1926, 4208 |
| `mx2018cj` | 4 | 703, 745, 1418, 2362 |
| `mx2019cj` | 5 | 75, 2596, 2741, 3052, 4090 |
| `mx2019party` | 2 | 1073, 3212 |
| `mx2020cj` | 6 | 295, 1104, 2011, 2120, 3868, 3961 |
| `mxkitchen` | 13 | 243, 890, 1583, 1849, 1954, 2359 |
| `nauticaladventure` | 1 | 79 |
| `newcatchfish` | 10 | 36, 1417, 2306, 2418, 2559, 2812 |
| `newracingspeed` | 9 | 1707, 1935, 2036, 2577, 3298, 4024 |
| `newserveractivity` | 4 | 1293, 1765, 2183, 4182 |
| `onlinelottery` | 6 | 1839, 2366, 2526, 2726, 3680, 3784 |
| `piaoliuping` | 13 | 709, 939, 991, 1063, 1273, 2004 |
| `qixi` | 4 | 868, 2515, 3172, 4882 |
| `school` | 4 | 1710, 2322, 2955, 3390 |
| `sevendaybonus` | 5 | 1140, 1859, 2779, 4185, 4939 |
| `shenyuan` | 5 | 2733, 3193, 3512, 4078, 4686 |
| `singlematch` | 6 | 759, 3035, 3679, 3887, 4283, 4335 |
| `springlottry` | 2 | 568, 1517 |
| `summerdiscount` | 4 | 1025, 3783, 4282, 4797 |
| `summertrainpet` | 17 | 527, 1142, 1180, 1970, 2534, 2878 |
| `sumwashbaodi` | 1 | 2155 |
| `survive` | 4 | 909, 2350, 3465, 4755 |
| `testthd` | 2 | 2224, 2938 |
| `timecapsule` | 4 | 686, 699, 1731, 2619 |
| `timewheel` | 37 | 10, 387, 621, 644, 1033, 1150 |
| `timewheel7discount` | 2 | 3656, 4887 |
| `timewheelfuben` | 2 | 4060, 4087 |
| `writeinfo` | 2 | 1161, 4859 |
| `yardmatch` | 20 | 95, 147, 288, 570, 627, 684 |
| `yearsummary` | 7 | 396, 555, 2291, 2443, 2478, 4103 |

## 覆盖与剩余项

81个工作包引用了 1654 个不同条目；剩余 3348 个尚未映射到这些工作包。
未映射不等于缺失玩法：其中可能是界面、通用库、渲染、原生模块绑定、异常条目，也可能确实是尚漏的玩法。完整ID清单见 `catalog/entry_feature_map.jsonl`。
每个条目均有记录，未匹配项保留空工作包列表，不用“其他”掩盖未分析内容。
