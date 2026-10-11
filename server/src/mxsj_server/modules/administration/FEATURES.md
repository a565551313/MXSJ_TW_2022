# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [充值订单、支付验证、补单与对账](../../../../docs/features/administration.payment.md) | `create_payment_order / accept_verified_provider_event / reconcile_payment_order` |
| [申诉、举报与客服入口](../../../../docs/features/administration.customer_support.md) | `submit_report / review_case / apply_audited_resolution` |
| [开关、补偿、停服与运营审计](../../../../docs/features/administration.operations.md) | `set_feature_policy / issue_approved_compensation / schedule_maintenance` |
