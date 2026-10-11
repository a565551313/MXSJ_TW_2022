# 剧情、任务条件与分支

工作包：`quest.story`；当前归口：`quest`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

具体状态机、资源消耗、权限和失败处理需要本工作包负责人核对材料后细化。

## 接口设计起点

`accept_story_task / evaluate_objective / progress_story / claim_story_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 51 | `script/data/juben/task13720.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 66 | `script/data/juben/task13116.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 67 | `script/data/juben/task13422.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 107 | `script/data/juben/task13909.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 121 | `script/data/juben/task13661.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 137 | `script/data/juben/task53218.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 190 | `script/data/juben/task13715.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 198 | `script/data/juben/task13745.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 208 | `script/data/juben/task1.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 256 | `script/data/juben/task13393.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 275 | `script/data/juben/task13730.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 322 | `script/data/juben/task53241.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 323 | `script/data/juben/task13395.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 345 | `script/data/juben/task13364.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 346 | `script/data/juben/task13350.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 352 | `script/data/juben/task13766.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 373 | `script/data/juben/task33762.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 386 | `script/data/juben/task13412.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 391 | `script/data/juben/task13408.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 408 | `script/data/juben/task13389.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 424 | `script/data/juben/task13410.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 430 | `script/data/juben/task53067.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 441 | `script/data/juben/task13246.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 484 | `script/data/juben/task13213.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 496 | `script/data/juben/task70001.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 502 | `script/data/juben/task13755.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 509 | `script/data/juben/task53137.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 546 | `script/data/juben/task13379.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 564 | `script/data/juben/task13396.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 578 | `script/data/juben/task13244.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 590 | `script/data/juben/task13383.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 600 | `script/data/juben/task53217.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 612 | `script/data/juben/task13355.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 618 | `script/data/juben/task13226.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 625 | `script/data/juben/task13251.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 628 | `script/data/juben/task13161.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 634 | `script/data/juben/task13684.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 648 | `script/data/juben/task13186.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 653 | `script/data/juben/task13345.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 678 | `script/data/juben/task13700.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 690 | `script/data/juben/task13429.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 753 | `script/data/juben/task53018.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 757 | `script/data/juben/task13713.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 767 | `script/mxgame/newstory/netnewstory.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SRequestNpcData, C2SReceiveNpcTask, C2SRequestSceneMapSchedule, C2SSendLetter, C2SGetGift, C2SGetLetterHistory |
| 773 | `script/data/juben/task13399.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 775 | `script/data/juben/task13741.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 778 | `script/data/juben/task13457.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 779 | `script/data/juben/task13152.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 800 | `script/data/juben/task53121.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 805 | `script/data/juben/task34004.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 820 | `script/data/juben/task13851.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 822 | `script/data/juben/task13111.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 832 | `script/data/juben/task13154.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 861 | `script/data/juben/task13217.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 865 | `script/data/juben/task13155.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 904 | `script/data/juben/task53198.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 905 | `script/data/juben/task13744.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 920 | `script/data/juben/task13821.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 933 | `script/data/juben/task13112.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 948 | `script/data/juben/task13174.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 974 | `script/data/juben/task13702.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 976 | `script/data/juben/task13656.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 980 | `script/data/juben/task53219.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 984 | `script/data/juben/task13427.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 990 | `script/data/juben/task13462.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1032 | `script/data/juben/task13252.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1044 | `script/data/juben/task13235.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1055 | `script/data/juben/task13735.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1071 | `script/data/juben/task13321.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1091 | `script/data/juben/task13655.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1100 | `script/data/juben/task13411.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1121 | `script/data/juben/task13435.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1123 | `script/data/juben/task33769.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1138 | `script/data/juben/task13454.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1141 | `script/data/juben/task13694.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1144 | `script/data/juben/task13171.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1158 | `script/data/juben/task13402.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1164 | `script/data/juben/task13325.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1173 | `script/data/juben/task13344.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1178 | `script/data/juben/task13245.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1183 | `script/data/juben/task13414.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1187 | `script/data/juben/task0.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1190 | `script/data/juben/task13465.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1205 | `script/data/juben/task13650.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1220 | `script/data/juben/task13236.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1274 | `script/data/juben/task13315.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1295 | `script/data/juben/task53189.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1313 | `script/data/juben/task13106.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1336 | `script/data/juben/task13211.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1340 | `script/data/juben/task13658.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1363 | `script/mxgame/newstory/rookieguide.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1393 | `script/data/juben/task13371.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1410 | `script/data/juben/task13215.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1431 | `script/data/juben/task34001.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1443 | `script/data/juben/task13835.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1457 | `script/data/juben/task13256.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1466 | `script/data/juben/task13376.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1486 | `script/data/juben/task13765.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1501 | `script/data/storytaskdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1509 | `script/data/juben/task53060.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1524 | `script/data/juben/task13447.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1531 | `script/data/juben/task13313.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1541 | `script/data/juben/task13769.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1559 | `script/data/juben/task13134.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1566 | `script/data/juben/task13378.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1570 | `script/data/juben/task13407.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1575 | `script/data/juben/task13162.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1580 | `script/data/juben/task13682.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1587 | `script/data/juben/task53244.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1594 | `script/data/juben/task13340.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1603 | `script/data/juben/task53032.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1611 | `script/data/juben/task13146.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1629 | `script/data/juben/task13358.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1630 | `script/data/juben/task53220.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1674 | `script/data/juben/task13354.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1675 | `script/data/juben/task53216.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1683 | `script/data/juben/task13388.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1695 | `script/data/juben/task13311.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1735 | `script/data/juben/task13732.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1736 | `script/data/juben/task13714.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1755 | `script/data/juben/task53166.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1784 | `script/data/juben/task13739.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1823 | `script/data/juben/task13157.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1867 | `script/data/juben/task13149.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1877 | `script/data/juben/task13384.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1879 | `script/data/juben/task13433.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1883 | `script/data/juben/task13665.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1885 | `script/data/juben/task13437.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1908 | `script/data/juben/task33748.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1913 | `script/data/juben/task13126.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1942 | `script/data/juben/task13647.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1948 | `script/data/juben/task13761.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1986 | `script/data/juben/task13705.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2008 | `script/data/juben/task53181.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2015 | `script/data/juben/task13115.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2031 | `script/data/juben/task13691.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2044 | `script/data/juben/task13163.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2050 | `script/data/juben/task13144.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2063 | `script/data/juben/task13416.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2067 | `script/data/juben/task70004.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2091 | `script/data/juben/task13357.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2092 | `script/data/juben/task13804.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2100 | `script/data/juben/task13405.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2102 | `script/data/juben/task13686.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2121 | `script/data/juben/task13401.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2135 | `script/data/juben/task13304.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2139 | `script/data/juben/task13459.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2140 | `script/data/juben/task13653.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2176 | `script/mxgame/newstory/newstorymgr.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2226 | `script/data/juben/task13200.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2252 | `script/data/juben/task13685.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2267 | `script/data/juben/task53135.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2283 | `script/data/juben/task13320.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2327 | `script/data/juben/task13406.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2348 | `script/data/juben/task13813.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2355 | `script/data/juben/task13104.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2369 | `script/data/juben/task13326.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2410 | `script/data/juben/task13255.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2434 | `script/data/juben/task13724.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2460 | `script/data/juben/task13145.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2466 | `script/data/juben/task13348.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2488 | `script/data/juben/task13128.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2535 | `script/data/juben/task13767.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2536 | `script/data/juben/task13129.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2538 | `script/data/juben/task13310.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2544 | `script/data/juben/task13119.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2548 | `script/data/juben/task13729.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2551 | `script/data/juben/task13456.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2576 | `script/data/juben/task13209.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2638 | `script/data/juben/task13308.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2640 | `script/mxgame/newstory/dlgdreamnote.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2660 | `script/data/juben/task13812.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2700 | `script/data/juben/task13331.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2723 | `script/data/juben/task13696.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2775 | `script/data/juben/task13657.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2792 | `script/data/juben/task13409.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2809 | `script/data/juben/task13857.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2851 | `script/data/juben/task34016.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2875 | `script/data/juben/task13468.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2900 | `script/data/juben/task13452.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2912 | `script/data/juben/task13214.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2936 | `script/data/juben/task53139.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2941 | `script/data/juben/task13430.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2942 | `script/data/juben/task13448.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2953 | `script/data/juben/task13228.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2960 | `script/data/juben/task53243.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2981 | `script/data/juben/task13153.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3040 | `script/data/juben/task13306.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3049 | `script/data/juben/task53196.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3095 | `script/data/juben/task53195.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3115 | `script/data/juben/task13736.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3125 | `script/data/juben/task13476.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3141 | `script/data/juben/task13738.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3149 | `script/data/juben/task13212.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3159 | `script/data/juqingdata.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3160 | `script/data/juben/task13177.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3186 | `script/data/juben/task13150.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3198 | `script/data/juben/task13318.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3202 | `script/data/juben/task13362.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3204 | `script/data/juben/task13922.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3208 | `script/data/juben/task13731.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3211 | `script/data/juben/task13368.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3220 | `script/data/juben/task13471.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3226 | `script/data/juben/task13343.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3227 | `script/data/juben/task13181.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3240 | `script/data/juben/task13704.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3306 | `script/data/juben/task13131.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3308 | `script/data/juben/task13225.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3311 | `script/data/juben/task13759.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3324 | `script/data/juben/task13335.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3333 | `script/data/juben/task13105.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3377 | `script/data/juben/task13648.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3382 | `script/data/juben/task53369.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3383 | `script/data/juben/task13324.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3405 | `script/data/juben/task13359.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3411 | `script/data/juben/task13413.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3419 | `script/data/juben/task13693.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3425 | `script/data/juben/task13141.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3427 | `script/data/juben/task13323.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3470 | `script/data/juben/task13314.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3482 | `script/data/juben/task13231.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3497 | `script/data/juben/task53228.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3503 | `script/data/juben/task13723.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3508 | `script/data/juben/task14106.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3530 | `script/data/juben/task13770.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3537 | `script/data/juben/task13811.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3538 | `script/data/juben/task13841.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3546 | `script/data/juben/task53065.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3550 | `script/data/juben/task13928.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3559 | `script/data/juben/task13179.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3588 | `script/data/juben/task13113.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3596 | `script/data/juben/task13227.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3601 | `script/data/juben/task13229.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3611 | `script/data/juben/task13356.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3630 | `script/data/juben/task13753.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3632 | `script/data/juben/task13329.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3642 | `script/data/juben/task13701.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3658 | `script/data/juben/task13203.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3659 | `script/data/juben/task53178.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3678 | `script/data/juben/task13810.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3684 | `script/data/juben/task53136.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3695 | `script/data/juben/task13173.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3750 | `script/data/juben/task13856.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3765 | `script/data/juben/task13382.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3800 | `script/data/juben/task13818.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3818 | `script/data/juben/task13431.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3825 | `script/data/juben/task13428.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3837 | `script/data/juben/task13165.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3856 | `script/data/juben/task13248.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3857 | `script/data/juben/task13784.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3862 | `script/data/juben/task13652.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3874 | `script/data/juben/task13138.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3918 | `script/data/juben/task13403.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3919 | `script/data/juben/task13347.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3928 | `script/data/juben/task13706.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3937 | `script/data/juben/task13195.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3941 | `script/data/juben/task53225.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3962 | `script/data/juben/task13372.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3982 | `script/data/juben/task13695.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4015 | `script/data/juben/task13683.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4022 | `script/data/juben/task13187.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4023 | `script/mxgame/newstory/dlgdreamletter.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4040 | `script/data/juben/task13307.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4096 | `script/data/juben/task13218.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4105 | `script/data/juben/task13353.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4119 | `script/data/juben/task13687.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4125 | `script/data/juben/task13132.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4128 | `script/data/juben/task53122.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4131 | `script/data/juben/task53015.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4151 | `script/data/juben/task13302.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4162 | `script/data/juben/task13352.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4194 | `script/data/juben/task13322.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4197 | `script/data/juben/task53066.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4230 | `script/data/juben/task13199.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4242 | `script/data/juben/task13242.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4298 | `script/data/juben/task13750.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4313 | `script/data/juben/task13816.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4315 | `script/data/juben/task13139.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4338 | `script/data/juben/task13230.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4357 | `script/data/juben/task13703.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4366 | `script/data/juben/task13351.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4398 | `script/data/juben/task13208.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4416 | `script/data/juben/task13367.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4417 | `script/data/juben/task13472.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4420 | `script/data/juben/task13316.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4431 | `script/data/juben/task53184.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4438 | `script/data/juben/task13432.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4458 | `script/data/juben/task13164.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4474 | `script/data/juben/task13346.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4496 | `script/data/juben/task13762.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4502 | `script/data/juben/task53192.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4536 | `script/data/juben/task13319.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4551 | `script/data/juben/task13135.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4554 | `script/data/juben/task13127.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4572 | `script/data/juben/task13386.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4579 | `script/data/juben/task13169.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4592 | `script/data/juben/task13194.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4595 | `script/data/juben/task53226.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4602 | `script/data/juben/task13140.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4619 | `script/data/juben/task13333.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4623 | `script/data/juben/task13349.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4628 | `script/data/juben/task13142.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4631 | `script/data/juben/task13680.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4640 | `script/data/juben/task13690.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4642 | `script/data/juben/task13398.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4644 | `script/data/juben/task13458.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4669 | `script/data/juben/task13363.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4687 | `script/data/juben/task13243.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4700 | `script/data/juben/task13117.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4718 | `script/data/juben/task13370.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4722 | `script/data/juben/task13651.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4749 | `script/data/juben/task53165.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4789 | `script/data/juben/task53200.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4791 | `script/data/juben/task13317.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4828 | `script/data/juben/task13469.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4864 | `script/data/juben/task13366.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4866 | `script/data/juben/task53016.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4886 | `script/data/juben/task13681.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4912 | `script/data/juben/task13911.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4913 | `script/mxgame/task/nettask.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetTask, S2CJuqingStatus, S2CUnpackClientNpc, S2CTaskAdd, S2CTaskRemove, C2SGiveUpTask |
| 4943 | `script/data/juben/task13475.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4946 | `script/data/juben/task33755.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4948 | `script/data/juben/task13425.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4969 | `script/data/juben/task13688.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4982 | `script/data/juben/task13930.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4985 | `script/data/juben/task13193.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4990 | `script/data/juben/task13791.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 5000 | `script/data/juben/task13809.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
