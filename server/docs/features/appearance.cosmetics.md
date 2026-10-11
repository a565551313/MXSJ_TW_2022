# 外观解锁、穿戴、染色与装饰

工作包：`appearance.cosmetics`；当前归口：`appearance`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`unlock_appearance / equip_appearance / change_color`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 28 | `script/mxgame/appearance/view/pageoutward/appearanceauraview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 105 | `script/mxgame/appearance/delegate/delegatedecorate/delegateappearancemark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 152 | `script/mxgame/appearance/view/appearancebase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 178 | `script/mxgame/decorate/view/dlgdecoratemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 269 | `script/mxgame/appearance/appearancedefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 291 | `script/mxgame/appearance/model/mddecorate/mdappearancemark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 300 | `script/mxgame/appearance/model/mdappearancetittle.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 378 | `script/mxgame/appearance/view/dyeplanselectinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 390 | `script/mxgame/appearance/delegate/delegateoutward/delegateappearanceaura.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 426 | `script/mxgame/appearance/delegate/delegateoutward/dgtfashiondressttribute.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 459 | `script/mxgame/appearance/model/mdoutward/mdappearancewing.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 513 | `script/mxgame/appearance/view/gift/appearancegiftview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 581 | `script/mxgame/appearance/model/mdappearancefairy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 599 | `script/mxgame/appearance/delegate/dgtexchangepay.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 609 | `script/mxgame/appearance/view/pageoutward/appearancewingview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 681 | `script/mxgame/appearance/view/dlgappearancemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 719 | `script/mxgame/appearance/view/pageoutward/dlgfashiondressttribute.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 863 | `script/mxgame/appearance/view/pagedecorate/appearancetittleview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 884 | `script/mxgame/appearance/view/pageoutward/dlgfashiondress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 911 | `script/mxgame/appearance/delegate/delegatehorse/delegateappearancehorse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1005 | `script/mxgame/appearance/view/dlgcanceldye.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1070 | `script/mxgame/appearance/delegate/appearancedelegatebase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1076 | `script/mxgame/appearance/view/pageoutward/dlgbackrefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SChooseColor |
| 1096 | `script/mxgame/decorate/delegate/dgtteammark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1192 | `script/mxgame/appearance/model/mdweaponcolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1219 | `script/mxgame/appearance/model/mdoutward/mdappearancechangeshape.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1242 | `script/mxgame/appearance/net/netappearance.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2GSAppearanceTGF, C2GSAppearancePTDye, C2GSAppearanceChgShape, C2GSAppearanceConfirmPTDye, C2GSAppearanceFreeDye, C2GSAppearanceSaveFreeDye |
| 1429 | `script/mxgame/appearance/model/mdoutward/mdbackdecoration.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1444 | `script/mxgame/appearance/view/appearanceviewsignal.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1481 | `script/mxgame/appearance/view/pagedecorate/pageappearancedecorate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1518 | `script/mxgame/decorate/delegate/dgtdecorate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1644 | `script/mxgame/decorate/view/dlgnewteammark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1662 | `script/mxgame/appearance/model/mdoutward/mdappearanceaura.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1719 | `script/mxgame/appearance/delegate/delegatedecorate/delegateappearancetittle.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1745 | `script/mxgame/appearance/view/pageoutward/dlgbackdecoration.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1813 | `script/mxgame/appearance/view/pagehorse/appearancehorseview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1930 | `script/mxgame/appearance/delegate/delegateoutward/dgtfashiondress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1964 | `script/mxgame/appearance/delegate/dgtdyeplanselect.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1988 | `script/mxgame/appearance/model/mdexchangepay.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2006 | `script/data/horseskindata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2041 | `script/mxgame/appearance/delegate/delegatedecorate/delegateapperancemagic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2260 | `script/mxgame/appearance/delegate/delegateoutward/dgtappearancechangeshape.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2287 | `script/mxgame/appearance/model/mdoutward/mdappearancechangecolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2399 | `script/mxgame/appearance/model/mdappearancegift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2402 | `script/mxgame/appearance/model/mdappearancehorse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2405 | `script/mxgame/appearance/view/pageoutward/newappearancefreecolorview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2483 | `script/mxgame/appearance/net/netyanzhiguan.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2523 | `script/mxgame/appearance/view/appearancepagebase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2564 | `script/mxgame/appearance/delegate/delegateoutward/dgtappearancehsv.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2629 | `script/mxgame/appearance/delegate/delegateoutward/delegatebackdecoration.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2635 | `script/mxgame/appearance/delegate/delegategift/delegateappearancegift.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2650 | `script/mxgame/appearance/delegate/delegateoutward/delegateappearancewing.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2739 | `script/mxgame/appearance/view/pagedecorate/appearancemarkview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2823 | `script/mxgame/decorate/view/dlgredpacketdecorade.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2861 | `script/mxgame/appearance/delegate/delegateappearancemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2879 | `script/mxgame/decorate/model/mddecorate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2894 | `script/mxgame/appearance/view/pageoutward/appearanceweaponview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3113 | `script/mxgame/appearance/delegate/delegateoutward/delegateappearanceoutward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3131 | `script/mxgame/appearance/net/netfashiondress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetOwnFashionDress, C2SBuyFashionDress, C2SWearOrDownFashion, C2SOpenFashionAttrView, C2SChangeFashionAttr, C2SGetCanBuyState |
| 3164 | `script/mxgame/decorate/model/mdteammark.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3171 | `script/mxgame/appearance/model/mddecorate/mdappearanceavatarfrm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3312 | `script/mxgame/appearance/view/pageoutward/appearancechangeshapeview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3403 | `script/mxgame/appearance/model/mdappearancemagic.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3424 | `script/mxgame/appearance/appearanceinterface.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3547 | `script/mxgame/appearance/view/pagehorse/appearancefairyview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3578 | `script/mxgame/appearance/view/pageoutward/appearancechangecolorview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSaveColor |
| 3587 | `script/mxgame/appearance/delegate/delegatehorse/delegateappearancefairy.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3712 | `script/mxgame/appearance/view/pagehorse/pageappearancehorse.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3714 | `script/mxgame/appearance/view/pagedecorate/appearanceavatarfrmview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3715 | `script/mxgame/appearance/view/dlgexchangepay.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3766 | `script/mxgame/appearance/view/pageoutward/pageappearanceoutward.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3959 | `script/mxgame/appearance/view/dlgappearanceavatar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4035 | `script/mxgame/appearance/view/pageoutward/appearanceshapemainview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4065 | `script/mxgame/appearance/view/pagedecorate/appearancemagicview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4251 | `script/mxgame/appearance/view/appearanceridepv.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4265 | `script/mxgame/appearance/model/mdoutward/newmdappearancefreecolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4453 | `script/mxgame/appearance/view/appearancepagefactory.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4459 | `script/mxgame/appearance/model/mdappearanceweapon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4501 | `script/mxgame/appearance/appearancecontext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4503 | `script/mxgame/appearance/model/mdoutward/mdfashiondress.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4588 | `script/mxgame/appearance/delegate/delegateoutward/dgtappearancechangecolor.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4706 | `script/mxgame/appearance/delegate/delegatedecorate/delegateappearancedecorate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4724 | `script/mxgame/appearance/delegate/delegateoutward/delegateappearanceweapon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4753 | `script/mxgame/appearance/delegate/delegatedecorate/delegateappearanceavatarfrm.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4833 | `script/mxgame/appearance/view/dlgdyeplanselect.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4895 | `script/mxgame/decorate/view/dlgdecorate.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4915 | `script/mxgame/appearance/delegate/delegateoutward/delegateroleview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4997 | `script/mxgame/appearance/delegate/delegateoutward/dgtappearanceshapemain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
