# 寄售、交易中心与订单

工作包：`trade.consignment`；当前归口：`trade`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`create_listing / purchase_listing / cancel_listing / claim_sale_proceeds`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 12 | `script/mxgame/consignmentsalecenter/view/dlgconsignmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 37 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallguildsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 175 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallsellmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 260 | `script/mxgame/consignmentsalecenter/model/mdconsignmallsetitemprice.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 290 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallhuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 432 | `script/mxgame/tradecenter/market/dlgtradecenter_marketitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 497 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 515 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 545 | `script/mxgame/consignmentsalecenter/consignmalldefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 547 | `script/mxgame/tradecenter/market/dlgtradecenter_marketgoods.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 630 | `script/mxgame/tradecenter/market/dlgtradecenter_market.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 646 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallguildequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 784 | `script/mxgame/tradecenter/tradeguild/dlgtradecenter_guild.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 875 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallhuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1154 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallguildequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1247 | `script/mxgame/consignmentsalecenter/consignmallhuolidefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1250 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1277 | `script/mxgame/consignmentsalecenter/view/dlghuolisalesetprice.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1289 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallbuyfilt.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1553 | `script/mxgame/consignmentsalecenter/model/mdconsignmallrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1579 | `script/mxgame/consignmentsalecenter/view/showlogic_consignbuy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1606 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallguildsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1843 | `script/mxgame/tradecenter/market/showlogic_markettrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2020 | `script/mxgame/tradeguild/nettradeguild.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SRequestItemList, C2SBuyItem, C2SRequestItemInfo, C2SRequestSaleList, C2SRequestSaleRecord, C2SPullItem |
| 2061 | `script/mxgame/tradecenter/tradeguild/showlogic_guildtrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2110 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2380 | `script/mxgame/tradecenter/mainframe/showlogic_tradecentermain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2554 | `script/mxgame/consignmentsalecenter/model/mdconsignmallbuy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2669 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallredpoint.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2777 | `script/mxgame/consignmentsalecenter/model/netconsignmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSEnterOneShelf, C2GSBuyGoods, C2GSAddMyGoods, C2GSRemoveMyGoods, C2GSOpenSalePage, C2GSAddMySummon |
| 2849 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallsellsetitemprice.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3073 | `script/mxgame/consignmentsalecenter/model/mdconsignmallredpoint.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3094 | `script/mxgame/consignmentsalecenter/model/mdconsignmallhuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3169 | `script/mxgame/consignmentsalecenter/view/consignmallwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3199 | `script/mxgame/consignmentsalecenter/view/showlogic_consignmall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3238 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallsellgoods.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3264 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellgoods.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3343 | `script/mxgame/tradecenter/tradecenterdefines.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3422 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellsetitemprice.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3433 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3460 | `script/mxgame/consignmentsalecenter/consignmalltest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3647 | `script/mxgame/consignmentsalecenter/model/mdconsignmallselllist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3651 | `script/mxgame/consignmentsalecenter/view/showlogic_consignhuoli.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3670 | `script/mxgame/tradecenter/market/mdtradecenter_market.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3754 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallsellsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3776 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellgoodsbag.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3910 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallsellitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4033 | `script/mxgame/tradecenter/mainframe/dgttradecentermain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4204 | `script/mxgame/consignmentsalecenter/view/dlgconsignmallbuy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4278 | `script/mxgame/tradecenter/market/dlgtradecenter_marketbag.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4323 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4348 | `script/mxgame/tradecenter/showlogic_jingpingtrade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4419 | `script/mxgame/consignmentsalecenter/view/showlogic_consignsell.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4520 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallbuy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4524 | `script/mxgame/consignmentsalecenter/consignmallutil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4539 | `script/mxgame/tradecenter/tradecenterwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4568 | `script/mxgame/tradecenter/market/dlgtradecenter_marketpet.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4679 | `script/mxgame/tradecenter/mainframe/dlgtradecentermainframe.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4707 | `script/mxgame/consignmentsalecenter/model/mdconsignmallsell.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4801 | `script/mxgame/consignmentsalecenter/delegate/dgtconsinmallsellitemlist.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4809 | `script/mxgame/consignmentsalecenter/delegate/dgtconsignmallsellitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
