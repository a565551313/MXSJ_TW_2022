# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [好友、黑名单、关系与离线通知](../../../../docs/features/social.friendship.md) | `request_friend / accept_friend / block_character / query_relationship` |
| [婚姻与配偶玩法](../../../../docs/features/social.marriage.md) | `request_marriage / confirm_marriage / request_divorce` |
| [师徒关系与师徒任务](../../../../docs/features/social.mentorship.md) | `request_mentorship / confirm_mentorship / graduate_apprentice` |
| [结拜及成员关系](../../../../docs/features/social.sworn.md) | `create_sworn_group / invite_sworn_member / leave_sworn_group` |
| [频道、私聊、语音与传音](../../../../docs/features/social.chat.md) | `send_channel_message / send_private_message / publish_voice_reference` |
| [空间、相册、动态与互动](../../../../docs/features/social.community.md) | `publish_post / list_feed / react_to_post / report_content` |
| [报纸、文章、广告与审核](../../../../docs/features/social.newspaper.md) | `submit_article / review_article / publish_newspaper / buy_ad_slot` |
