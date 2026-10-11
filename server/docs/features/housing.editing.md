# 家具摆放、地块和家园编辑

工作包：`housing.editing`；当前归口：`housing`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`place_furniture / move_furniture / expand_plot`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 39 | `script/yard/yardedit/yardeditmap/yarditemgrid.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 41 | `script/yard/yardedit/yardeditdelegate/delegateyardstaticticmapfurdlg.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 73 | `script/yard/yardedit/yardeditui/yardeditviewbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 114 | `script/yard/yardedit/yardeditzoom/yardeditzoommgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 130 | `script/yard/yardedit/yardeditui/yardeditminimapview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 144 | `script/yard/yardmap/mainui/yardmap2editview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 168 | `script/yard/yardedit/yardeditui/yardbrushshape.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 184 | `script/yard/yardedit/yardeditmap/yarditemfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 192 | `script/yard/yardmap/delegate/delegateyardminimapenv.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 221 | `script/yard/yardedit/yardeditmap/yardmaproot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 328 | `script/yard/yardmap/delegate/delegateyardfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 360 | `script/yard/yardmap/view/yardroom.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 549 | `script/yard/yardedit/yardeditui/yardeditviewitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 594 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushnpc.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 668 | `script/yard/yardmap/delegate/delegateyardactivehotspring.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 691 | `script/yard/yardedit/yardeditui/yardeditpushfur2bagview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 708 | `script/yard/yardedit/yardeditmap/yardbgview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 754 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 771 | `script/yard/yardmap/view/yardmapfurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 833 | `script/yard/yardedit/yardeditui/yardeditchoosebjview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 838 | `script/yard/yardedit/yardeditui/yardeditviewbrush_del.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 872 | `script/yard/yardedit/yardeditmap/cmp_renderhouse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 899 | `script/yard/yardmap/delegate/delegateyardminimapfurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 969 | `script/yard/yardmap/view/yardfieldhotspring.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1009 | `script/yard/yardedit/yardeditmap/cmp_rendernide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1047 | `script/yard/yardmap/delegate/delegateyardminimapplayer.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1072 | `script/yard/yardmap/delegate/delegateyardmap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1112 | `script/yard/yardmap/view/farmtouchlogic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1165 | `script/yard/yardmap/mainui/yardothersmapinfoview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1271 | `script/yard/yardedit/yardeditdelegate/delegateyardeditminimapnide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1281 | `script/yard/yardmap/view/yardfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1338 | `script/yard/yardedit/yardeditzoom/zoomedit/yardzoomeditbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1351 | `script/yard/yardedit/yardeditdelegate/delegateyardeditbar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1405 | `script/yard/yardmap/delegate/delegateyardstoragedlg.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1413 | `script/yard/yardedit/yardeditmap/yardeditmapitembase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1426 | `script/yard/yardmap/delegate/delegateyardguidemapobj.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1448 | `script/yard/yardedit/yardeditui/yardeditoperateview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1458 | `script/yard/yardedit/yardeditui/!9*<=<1,.1=/:*ush_farm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1536 | `script/yard/yardmap/view/yardextraeff.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1564 | `script/yard/yardedit/yardeditmap/yarditembase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1598 | `script/yard/yardmap/view/yardmap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1856 | `script/yard/yardmap/delegate/delegateyardinvitehotspring.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1880 | `script/yard/yardedit/yardeditmap/cmp_renderfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1901 | `script/yard/yardmap/delegate/delegateyardminimapfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1907 | `script/yard/yardmap/delegate/delegateyardborder.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1927 | `script/yard/yardedit/yardeditui/yardeditbarview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2005 | `script/yard/yardedit/yardeditmap/yardviewbaseKpy` | marshal_transpiled_no_filename / historical_fallback / needs_review |  |
| 2090 | `script/yard/yardedit/yardeditm/p/yarditemland.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2118 | `script/yard/yardmap/mainui/dlgyardfurauth.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2125 | `script/yard/yardedit/yardeditui/yardeditoperatedirview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2148 | `script/yard/yardedit/yardeditui/yardbrushlogic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2222 | `script/yard/yardedit/yardeditmap/cmp_rendergridsnew.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2285 | `script/yard/yardmap/delegate/delegateyardfurlistdlg.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2381 | `script/yard/yardedit/yardeditzoom/zoomedit/cmp_zoombase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2408 | `script/yard/yardedit/yardeditui/dlgyardblockeditor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2468 | `script/yard/yardmap/view/yardnpcmark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2470 | `script/yard/yardmap/delegate/delegatesitefurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2496 | `script/yard/yardmap/mainui/yardstoragedlg.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2592 | `script/yard/yardedit/yardeditzoom/yardeditzoomdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2637 | `script/yard/yardedit/yardeditdelegate/delegateyardtouchmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2639 | `script/yard/yardedit/yardeditui/dlgyardanchoreditor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2680 | `script/yard/yardmap/delegate/delegateyardanimal.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2687 | `script/yard/yardmap/mainui/yardfurlistdlg.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2704 | `script/yard/yardmap/view/yardmapanimal.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2845 | `script/yard/yardedit/yardeditmap/yardeditminimaproot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2850 | `script/yard/yardedit/yardeditui/yardeditviewbrush_nide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2857 | `script/yard/yardedit/yardeditmap/yarditemminimapfarm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2884 | `script/yard/yardedit/*ardeditzoom/yardeditzoomgridmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2978 | `script/yard/yardmap/yardmapdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3037 | `script/yard/yardedit/yardeditmap/yarditemnide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3048 | `script/yard/yardedit/yardeditmap/cmp_yardshape.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3155 | `script/yard/yardedit/yardeditminimapmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3230 | `script/yard/yardmap/delegate/delegateyardhouse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3239 | `script/yard/yardedit/yardeditui/yardeditouchmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3287 | `script/yard/yardedit/yardeditui/yardeditviewbrush_npc.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3335 | `script/yard/yardmap/mainui/dlgyardvisit.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SEnterYard, C2SYardRequestYardInfoList |
| 3351 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushfurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3360 | `script/yard/yardmap/view/yardminimap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3522 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3531 | `script/yard/yardedit/yardeditmap/yarditemdeco.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3567 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushnide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3663 | `script/yard/yardedit/yardeditzoom/yardeditzoomcontext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3681 | `script/yard/yardedit/yardeditzoom/zoomedit/yardbrushgridflag.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3686 | `script/yard/yardmap/delegate/delegateyardminimaphouse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3697 | `script/yard/yardedit/yardeditdelegate/delegateyardeditminimaproot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3702 | `script/yard/yardedit/yardeditui/yardeditstatisticmapfurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3732 | `script/yard/yardedit/yardeditui/yardeditmainview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3739 | `script/yard/yardmap/view/yardhotspringinviteicon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3743 | `script/yard/yardmap/view/yardfarmplant.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3841 | `script/yard/yardmap/view/yardmapbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4028 | `script/yard/yardedit/yardeditmap/cmp_rendernpc.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4088 | `script/yard/yardedit/yardeditzoom/zoomedit/yardeditzoommainview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4110 | `script/yard/yardmap/delegate/delegateyardcursorpos.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4130 | `script/yard/yardedit/yardeditdelegate/delegateyardtouch2delfurniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4137 | `script/yard/yardedit/yardviewmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4154 | `script/yard/yardmap/mainui/yardmainviewbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4159 | `script/yard/yardmap/delegate/delegateyardmapbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4167 | `script/yard/yardmap/delegate/delegateyardminimapbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4171 | `script/yard/yardedit/yardeditui/yardeditviewbrush_furniture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4196 | `script/yard/yardedit/yardeditui/yardeditviewbrush_land.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4247 | `script/yard/yardedit/yardeditmap/cmp_yardviewbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4267 | `script/yard/yardmap/delegate/delegateyardmapquickfish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4377 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushhouse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4394 | `script/yard/yardedit/yardeditmap/cmp_rendergrids.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4440 | `script/yard/yardedit/yardeditui/yardbrushshape_funiture.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4509 | `script/yard/yardedit/yardeditui/&>-;:;6+*ploadview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4523 | `script/yard/yardedit/yardeditui/yardeditviewroot.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4573 | `script/yard/yardedit/yardeditui/yardeditviewbrush.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4627 | `script/yard/yardedit/yardeditui/yardbackpreoplogic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4670 | `script/yard/yardedit/yardeditui/yardhidemainmenu.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4745 | `script/yard/yardedit/yardeditmap/cmp_renderunits.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4751 | `script/yard/yardedit/yardeditmap/cmp_renderevn.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4757 | `script/yard/yardmap/delegate/delegateyardminimapnpc.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4758 | `script/yard/yardedit/yardeditzoom/yardzoomdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4778 | `script/yard/yardmap/delegate/delegateyardbase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4827 | `script/yard/yardedit/yardeditzoom/zoomedit/cmp_zoomgridrender.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4834 | `script/yard/yardedit/yardeditviewmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4884 | `script/yard/yardedit/yardeditdelegate/delegateyardbrushland.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4922 | `script/yard/yardmap/mainui/yardmapmainuimgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4936 | `script/yard/yardedit/yardeditmap/yardeditblockview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4950 | `script/yard/yardmap/delegate/delegateyardminimap.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
