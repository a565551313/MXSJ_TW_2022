# 鱼塘、观赏鱼与幸运鱼

工作包：`housing.fish`；当前归口：`housing`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`stock_fish / feed_fish / harvest_fish / claim_fish_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 136 | `script/yard/yardplayfish/yardplayfishdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 329 | `script/yard/yardplayfish/view/dlgyardplayfishobtainfishfry.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 649 | `script/yard/yardplayfish/net/netyardplayfish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SUseFishFry, C2SPutInFishFry, C2SPutInFishFry_Quick, C2SRequesToFeedFish, C2SRequestForMarkingFish, C2SRequestFeedFishInfo |
| 730 | `script/yard/yardplayfish/view/yardfishcultureinfo/dlgyardplayfishmyfishpond.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 760 | `script/yard/yardplayfish/view/yardfishgetreword/dlgyardplayfishgetrewordmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 860 | `script/yard/yardplayfish/model/mdyardplayfishmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 977 | `script/yard/yardplayfish/view/dlgyardplayfishmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1303 | `script/yard/yardplayfish/view/yardfishfeed/dlgyardplayfishfeed.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1386 | `script/yard/yardplayfish/view/dlgyardplayfishculturechart.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1435 | `script/yard/luckyfish/view/dlgfudaishare.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1589 | `script/yard/yardplayfish/delegate/yardfishcultureinfo/dgtardplayfishcultureinfomain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1800 | `script/yard/yardplayfish/view/yardfishgetreword/dlgyardplayfishunlockevaluation.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1951 | `script/yard/yardplayfish/delegate/yardfishcultureinfo/dgtyardplayfishobtainfishfry.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2022 | `script/yard/yardplayfish/model/mdyardplayallfish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2268 | `script/yard/yardplayfish/delegate/yardfishcultureinfo/dgtyardplayfishmyfishpond.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2383 | `script/yard/luckyfish/delegate/delegatefudaishare.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2474 | `script/yard/yardplayfish/view/yardplayfishpagefactory.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2556 | `script/yard/luckyfish/yardmapsub_luckyfishcontext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2599 | `script/yard/yardplayfish/model/mdyardplayfishobtainfishfry.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2604 | `script/yard/yardplayfish/view/yardfishfeed/dlgyardplayfishfeedtips.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2709 | `script/yard/yardplayfish/view/yardfishcultureinfo/dlgyardplayfishcultureinfomain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2713 | `script/yard/yardplayfish/view/yardfishfeed/dlgyardplayfishfeedup.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2862 | `script/yard/yardplayfish/yardplayfishcontext.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3041 | `script/yard/luckyfish/model/luckyfishdatamgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3057 | `script/yard/luckyfish/netyardluckyfish.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SYardLuckyFish_Info, C2SYardLuckyFish_Feed, C2SYardLuckyFish_GetReward, C2SYardLuckyFish_OpenShareDlg, C2SYardLuckyFish_OpenFeedHisDlg, C2SYardLuckyFish_ShareBag2Player |
| 3083 | `script/yard/yardplayfish/delegate/delegateyardplayfishmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3340 | `script/yard/luckyfish/view/dlgluckyfishrecorditem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3430 | `script/yard/yardplayfish/view/yardfishgetreword/dlgyardplayfishexchangepoints.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3439 | `script/yard/luckyfish/view/dlgluckyfishrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3698 | `script/yard/luckyfish/view/dlgluckyfishmainview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3744 | `script/yard/yardplayfish/delegate/dgtyardplayfishculturechart.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3846 | `script/yard/yardplayfish/view/dlgyardplayfishrecommend.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3852 | `script/yard/yardplayfish/delegate/yardfishfeed/dgtyardplayfishfeed.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4169 | `script/yard/yardplayfish/view/yardplayfishpagebase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4481 | `script/yard/luckyfish/delegate/delegateluckyfishrecord.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4564 | `script/yard/yardplayfish/delegate/yardfishgetreword/dgtyardplayfishgetrewordmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4611 | `script/yard/luckyfish/view/dlgfudaishareitem.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4639 | `script/yard/yardplayfish/yardplayfishmgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4717 | `script/yard/yardplayfish/delegate/yardplayfishdelegatebase.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4911 | `script/yard/luckyfish/delegate/delegateluckyfishmainview.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
