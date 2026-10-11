# 家园访问、家具权限与使用

工作包：`housing.visiting`；当前归口：`housing`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`visit_house / set_house_permissions / use_furniture`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 215 | `script/yard/yardplayerhome/yardhome_oneplayer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 743 | `script/yard/yardplayerhome/delegate/delegateyardhomeshareroom.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 751 | `script/yard/yardplayerhome/view/dlgyardhome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 770 | `script/yard/yardplayerhome/delegate/delegatecmpyardhome_map.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 916 | `script/yard/yardplayerhome/delegate/logicshow_dgtyardhomevisit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1098 | `script/yard/yardplayerhome/delegate/delegateyardminimapanimal.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1222 | `script/yard/yardplayerhome/delegate/delegatecmpyardhome_visit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1387 | `script/yard/yardplayerhome/netyardvisit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SEnterYard, C2SYardRequestYardInfoList, S2CRefreshFriendLst, S2CYardVisit_FindResult, S2CShowYardVisit |
| 1503 | `script/yard/yardplayerhome/view/dlgresetyardfengshui.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1522 | `script/yard/yardplayerhome/delegate/delegateyardhome_info.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1688 | `script/yard/yardplayerhome/view/cmpyardhome_map_subyard.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1712 | `script/yard/yardplayerhome/delegate/delegateyardhome_pageself.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1921 | `script/yard/yardplayerhome/view/dlghomerecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2262 | `script/yard/yardplayerhome/view/cmpyardhome_map_subroom2.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2412 | `script/yard/yardplayerhome/yardhomefactory.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2416 | `script/yard/yardplayerhome/delegate/delegateyardshare.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2425 | `script/yard/yardplayerhome/model/yardhomevisitdatamgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2732 | `script/yard/yardplayerhome/view/dlgyardstatenormalview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2904 | `script/yard/yardplayerhome/view/cmpyardhome_map_subroom.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3022 | `script/yard/yardplayerhome/view/dlgyardhomeshareroombase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3179 | `script/yard/netyardfurauth.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CYardFurAuth, S2CYarFurAuth_AllFur, S2CYarFurAuth_OneFurAuth, S2CYarFurAuth_Change, S2CYarFurAuth_GetSelfAuth, S2CYardFur_HotSpringLog |
| 3216 | `script/yard/yardplayerhome/delegate/delegateyardhome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3275 | `script/yard/yardplayerhome/view/cmpyardhome_visit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3299 | `script/yard/yardplayerhome/view/dlgrecordjiayuan.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3348 | `script/yard/yardplayerhome/view/dlgvisititemview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3381 | `script/yard/yardplayerhome/model/yardmapdata_oldyard.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3426 | `script/yard/yardplayerhome/view/dlgyardhome_pageself.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3560 | `script/yard/yardplayerhome/yardhomedefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3687 | `script/yard/yardplayerhome/view/dlgyardplayerhome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3720 | `script/yard/yardplayerhome/view/cmpyardhome_map.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3938 | `script/yard/yardplayerhome/model/yardmapdatamgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3940 | `script/yard/yardplayerhome/delegate/logicshow_dgtyardhomeself.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4052 | `script/yard/yardplayerhome/view/dlgyardhome_pagevisit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4143 | `script/yard/yardplayerhome/view/dlgyardstateroomcreateview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4202 | `script/yard/yardplayerhome/view/cmpyardhome_yardold.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4461 | `script/yard/yardplayerhome/netyardhome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CYardHomeProcess, S2CYardHome_BaseInfo, S2CYardHome_StateInfo, S2CYardHome_OpenDlg, S2CYardHome_GetFurnitrueLst, S2CYardHome_OldYardGarthPlant |
| 4490 | `script/yard/yardplayerhome/delegate/logicshow_dgtyardhome.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4673 | `script/yard/yardplayerhome/model/yardmapdata_room.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4705 | `script/yard/yardplayerhome/view/cmpyardhome_yardnew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4852 | `script/yard/yardplayerhome/yardhomecontext_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4880 | `script/yard/yardplayerhome/view/dlgyardstatechildview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4938 | `script/yard/yardplayerhome/model/yardhomeinfodatamgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4987 | `script/yard/yardplayerhome/view/dlguphousenew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
