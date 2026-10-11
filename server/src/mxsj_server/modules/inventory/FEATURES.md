# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [仓库、保险仓、租赁和续租](../../../../docs/features/inventory.warehouse.md) | `list_storage / transfer_storage_item / rent_storage / renew_storage` |
| [仓库密码、锁定、检索与整理](../../../../docs/features/inventory.warehouse_security.md) | `unlock_storage / change_storage_protection / search_storage / arrange_storage` |
| [临时背包与特殊场景物品](../../../../docs/features/inventory.virtual_bag.md) | `list_temporary_items / use_temporary_item / move_temporary_item` |
| [物品扩展属性与快捷栏](../../../../docs/features/inventory.extension.md) | `query_item_details / set_item_shortcut` |
