# 国家赛事与阵营活动

工作包：`activity.country_contest`；当前归口：`activity`。负责人待分配。

**状态：材料入口与接口设计卡；未实现，未逐函数语义核实。**

本卡由工具生成。人工设计与进度记录请放在所属模块的 `design/<工作包名>.md`，避免重新生成覆盖。

## 职责与边界

国家管理本身仍需另找资料，不能用报纸模块补齐。

## 接口设计起点

`enroll_faction_event / query_faction_progress / claim_faction_reward`

这些方法名是服务端设计建议，不是已经存在的Python接口，也不是客户端opcode。
业务负责人需补齐请求/响应DTO、授权主体、前置条件、失败码、幂等键、事务边界和事件，随后与调用方冻结契约。
不允许通过通用 method_name + dict 或任意字符串动态调用来绕过接口设计。

## 客户端材料清单

命中代表研究入口；同一脚本可属于多个工作包。历史函数名只是线索，当前转译只检查文件名，不等于源码正确。

| 条目 | 当前/回退文件名 | 检查状态 | 历史接口函数样例 |
|---:|---|---|---|
| 80 | `script/mxgame/activity/insidewar/insidewardefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 199 | `script/mxgame/activity/countrycontest/ctysetequip/dgtctysetequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 204 | `script/mxgame/activity/countrycontest/rank/view/dlgctrycontestrankthree.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 206 | `script/mxgame/activity/countrycontest/setting/delegate/dgtctrycontestsetmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 209 | `script/mxgame/activity/insidewar/insidewarequip/netinsidewarequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSaveEquipInfo, C2SGetBaseAttr, C2SRequestEquipInfoByPart, S2CGetBaseAttr, S2CRequestEquipInfo, C2SResetEquipSetting |
| 232 | `script/mxgame/activity/countrycontest/recruitment/delegate/dgtctrycontestrecruitdetail.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 281 | `script/mxgame/activity/countrycontest/arena/model/mdctrycontest1v1arena.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 289 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest3v3gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 309 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 362 | `script/mxgame/activity/countrycontest/arena/ctrycontestarenactrl.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 492 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestsummon_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 534 | `script/mxgame/activity/insidewar/insidewarmain/dgtinsidewarmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 538 | `script/mxgame/activity/insidewar/insidewarride/mdinsidewarride.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 693 | `script/mxgame/activity/insidewar/testinsidewar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CTeamRank |
| 827 | `script/mxgame/activity/insidewar/insidesummonskill/dgtinsidesummonskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 935 | `script/mxgame/activity/countrycontest/arena/view/ctrycontestwidget.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 946 | `script/mxgame/activity/insidewar/insidewardrug/dgtinsidewardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 957 | `script/mxgame/activity/countrycontest/arena/delegate/dgtctrycontest1v1gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 987 | `script/mxgame/activity/countrycontest/arena/delegate/dgtctrycontest3v3gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1232 | `script/mxgame/activity/countrycontest/recruitment/view/dlgctrycontestrecruitment.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1233 | `script/mxgame/activity/countrycontest/crtycontestdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1236 | `script/mxgame/activity/insidewar/insidewarrank/dgtinsidewarrank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1269 | `script/mxgame/activity/countrycontest/recruitment/model/mdctrycontestrecruitment.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1353 | `script/mxgame/activity/countrycontest/recruitment/delegate/dgtctrycontestmsgboard.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1356 | `script/mxgame/activity/countrycontest/rank/view/dlgctrycontestrankone.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1358 | `script/mxgame/activity/countrycontest/recruitment/model/mdctrycontestrecruitdetail.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1471 | `script/mxgame/activity/insidewar/insidewarjob/mdinsidejob.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1576 | `script/mxgame/activity/countrycontest/setting/model/mdctrycontestsummonskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1581 | `script/mxgame/activity/countrycontest/netctrycontest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SCtryContestHeader, C2SOpenRecruitUI, C2SSubmitRecruitmentApply, C2SSubmitMyRecruitment, C2SViewMyMsgBoard, C2SViewMsgBoardInfo |
| 1633 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestsummonskil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1651 | `script/mxgame/activity/countrycontest/arena/model/mdctrycontest3v3arena.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1672 | `script/mxgame/activity/countrycontest/setting/model/mdctrycontestsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1746 | `script/mxgame/activity/insidewar/insidewarequip/mdinsidewarequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1771 | `script/mxgame/activity/insidewar/insidesummonskill/mdinsidesummonskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1785 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest1v1matchhall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 1961 | `script/mxgame/activity/insidewar/netinsidewar.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SCtryContestHeader, C2SMountSkillData, C2SSummonDetail, C2SSaveMountSkill, C2SSaveSummon, C2SSaveSummonSkill |
| 1971 | `script/mxgame/activity/countrycontest/ctysetequip/dlgctysetequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2093 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest3v3match.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2112 | `script/mxgame/activity/countrycontest/playerbaseinfosetting/dlgplayerbaseinfosetting_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2200 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestmountskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2314 | `script/mxgame/activity/countrycontest/arena/model/netctrycontest3v3arena.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CChangeFindTeamState, S2COpen3v3ArenaTeamDlg, S2CInitTeamList, S2CAddOneTeam, S2CTeamDetail, S2CUpdateTeamNum |
| 2364 | `script/mxgame/activity/countrycontest/playerbaseinfosetting/dgtplayerbaseinfosetting.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2401 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestskillpv.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2417 | `script/mxgame/activity/countrycontest/arena/delegate/dgtctrycontest1v1matchhall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2430 | `script/mxgame/activity/insidewar/insidewarjob/netinsidejob.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSendRoleSettingInfo, C2SOpenDefineSkillDlg, C2SOpenPropSettingDlg, C2SOpenHeartMethodDlg, C2SSetDefineSkills, C2SSetHeartMethod |
| 2484 | `script/mxgame/activity/insidewar/insidewarride/dlginsidewarride.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2563 | `script/mxgame/activity/countrycontest/ctysetequip/dgtctysetequip_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2648 | `script/mxgame/activity/countrycontest/recruitment/view/dlgctrycontestrecruitdetail.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2666 | `script/mxgame/activity/countrycontest/arena/model/mdctrycontest3v3gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2672 | `script/mxgame/activity/countrycontest/recruitment/delegate/dgtctrycontestrecruitment.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2675 | `script/mxgame/activity/insidewar/insidewarsummon/dgtinsidewarummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2695 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestmountskill_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2721 | `script/mxgame/activity/countrycontest/ctysetequip/ctysetequipdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2737 | `script/mxgame/activity/insidewar/insidewarrank/dlginsidewarrank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2738 | `script/mxgame/activity/countrycontest/ctrycontesttest.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2762 | `script/mxgame/activity/countrycontest/shop/model/mdctrycontestshop.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2863 | `script/mxgame/activity/countrycontest/setting/model/mdctrycontestmountskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2892 | `script/mxgame/activity/countrycontest/arena/model/mdctrycontest1v1gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2919 | `script/mxgame/activity/insidewar/insidewarmain/dlginsidewarmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2920 | `script/mxgame/activity/countrycontest/rank/model/mdctrycontestrankone.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2922 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestsetmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 2943 | `script/mxgame/activity/countrycontest/drug/dgtctrydrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3099 | `script/mxgame/activity/countrycontest/ctysetequip/dlgctysetequip_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3101 | `script/mxgame/activity/countrycontest/arena/model/netctrycontest1v1arena.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | S2CInitArenaList, S2CUpdateOneArena, S2CAddOneArena, S2CDelOneArena, S2CMasterEnterArena, S2CChallengerEnterArena |
| 3109 | `script/mxgame/activity/countrycontest/recruitment/model/mdctrycontestmsgboard.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3224 | `script/mxgame/activity/countrycontest/setting/view/dlgctrycontestsummonskil_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3249 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest1v1gonglei.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3266 | `script/mxgame/activity/insidewar/insidewarequip/insidewarequipdefine.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3305 | `script/mxgame/activity/countrycontest/setting/model/mdctrycontestsetmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3389 | `script/mxgame/activity/countrycontest/playerbaseinfosetting/netplayerbaseinfosetting.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SSendRoleSettingInfo, C2SOpenDefineSkillDlg, C2SOpenPropSettingDlg, C2SOpenHeartMethodDlg, C2SSetDefineSkills, C2SSetHeartMethod |
| 3391 | `script/mxgame/activity/insidewar/insidesummonskill/dlginsidesummonskil.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3429 | `script/mxgame/activity/insidewar/insidewarsummon/dlginsidewarsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3456 | `script/mxgame/activity/countrycontest/setting/delegate/dgtctrycontestchangesummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3511 | `script/mxgame/activity/countrycontest/ctysetequip/netctysetequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid | C2SGetEquipTipsInfo, C2SSaveEquipInfo, C2SGetBaseAttr, S2CGetEquipTipsInfo, S2CGetBaseAttr, C2SRequestEquipInfoByPart |
| 3565 | `script/mxgame/activity/countrycontest/setting/view/dlgcharacterpreinstall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3623 | `script/mxgame/activity/countrycontest/shop/view/dlgctrycontestshop.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3819 | `script/mxgame/activity/insidewar/insidewarjob/dgtinsidewarjob.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3882 | `script/mxgame/activity/countrycontest/recruitment/view/dlgctrycontestteamname.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3884 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest1v1randommatch.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3984 | `script/mxgame/activity/insidewar/insidewarmain/mdinsidewarmain.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 3998 | `script/mxgame/activity/countrycontest/arena/view/dlgctrycontest3v3matchhall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4098 | `script/mxgame/activity/insidewar/insidewardrug/mdinsidewardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4236 | `script/mxgame/activity/countrycontest/drug/dlgctrydrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4253 | `script/mxgame/activity/countrycontest/setting/delegate/dgtctrycontestmountskill_new.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4378 | `script/mxgame/activity/insidewar/insidewarequip/dlginsidesetequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4384 | `script/mxgame/activity/countrycontest/setting/delegate/dgtctrycontestsummonskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4515 | `script/mxgame/activity/countrycontest/ctysetequip/mdctysetequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4518 | `script/mxgame/activity/countrycontest/arena/model/mdctrycontest3v3match.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4543 | `script/mxgame/activity/insidewar/insidewarride/dgtinsidewarride.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4560 | `script/mxgame/activity/countrycontest/shop/delegate/dgtctrycontestshop.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4566 | `script/mxgame/activity/insidewar/insidewarrank/mdinsidewarrank.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4576 | `script/mxgame/activity/countrycontest/rank/ctrycontestrankctrl.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4582 | `script/mxgame/activity/countrycontest/playerbaseinfosetting/dlgplayerbaseinfosetting.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4666 | `script/mxgame/activity/countrycontest/arena/delegate/dgtctrycontest3v3match.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4677 | `script/mxgame/activity/countrycontest/setting/delegate/dgtctrycontestmountskill.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4701 | `script/mxgame/activity/countrycontest/drug/mdctrydrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4708 | `script/mxgame/activity/countrycontest/rank/delegate/dgtctrycontestrankone.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4764 | `script/mxgame/activity/countrycontest/rank/delegate/dgtctrycontestrankthree.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4794 | `script/mxgame/activity/insidewar/insidewarequip/dgtinsidewarequip.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4835 | `script/mxgame/activity/countrycontest/rank/model/mdctrycontestrankthree.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4849 | `script/mxgame/activity/insidewar/insidewarsummon/mdinsidewarsummon.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4863 | `script/mxgame/activity/insidewar/insidewardrug/dlginsidewardrug.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4900 | `script/mxgame/activity/countrycontest/playerbaseinfosetting/mdplayerbaseinfosetting.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4904 | `script/mxgame/activity/insidewar/insidewarjob/dlginsidewarjob.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |
| 4971 | `script/mxgame/activity/countrycontest/setting/delegate/dgtcharacterpreinstall.py` | marshal_transpiled_filename_checked / current_archive / structurally_valid |  |

## 独立交付要求

- 列清可确认的客户端行为、可提取数据、缺失服务端规则；不混用三个层次。
- 为新增接口补充字段与错误表；复用已有公开接口或提出版本化扩展。
- 金币、物品、资格变化通过同一工作单元，不能直接改其他模块的私有表。
- 成功、越权、重复请求、版本冲突、超时/断线、失败恢复均有测试。
- 回填代码和测试路径、完成状态及原客户端验证样本。
