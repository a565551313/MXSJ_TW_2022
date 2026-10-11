# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [NPC商店、玩家商店与物品定价](../../../../docs/features/trade.shop.md) | `list_shop_goods / purchase_goods / set_shop_price / deposit_shop_funds` |
| [寄售、交易中心与订单](../../../../docs/features/trade.consignment.md) | `create_listing / purchase_listing / cancel_listing / claim_sale_proceeds` |
| [竞拍、自动出价与结拍](../../../../docs/features/trade.auction.md) | `place_bid / set_auto_bid / cancel_auto_bid / settle_auction` |
| [角色交易与资产展示](../../../../docs/features/trade.role_market.md) | `query_sale_character / prepare_character_listing / confirm_ownership_transfer` |
