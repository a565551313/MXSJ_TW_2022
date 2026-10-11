# 子系统工作包

起步 contracts.py 不覆盖本表的全部接口。新增接口先在工作包设计卡中冻结。

| 工作包 | 接口草案 |
|---|---|
| [飞行旗、传送、寻路与移动](../../../../docs/features/world.travel.md) | `use_travel_point / validate_movement / enter_map` |
| [副本空间与进入离开](../../../../docs/features/world.instance.md) | `create_instance / enter_instance / leave_instance` |
| [动态NPC、场景物品和副本对象](../../../../docs/features/world.dynamic_entities.md) | `spawn_world_entity / remove_world_entity / interact_world_entity` |
