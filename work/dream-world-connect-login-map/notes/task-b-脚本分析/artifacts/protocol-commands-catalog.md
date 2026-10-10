# Protocol Commands Catalog — script\protocol + net modules

来源: v4-ok 解码中的 P0-net 条目 (369 个模块)。命名规则: `C2GS*` = client→server, `GS2C*` = server→client;
主 opcode + `iSub` 子命令；函数签名来自模块内调试字符串（`Name(p=%s,...)`）。CJK 字符串为 Big5 编码。

## 主 opcode 家族

| 主 opcode | 模块数 | 模块 |
|---|---|---|
| `C2GS=0xcd` | 1 | `csdailyscore.py` |
| `C2GS_BAND=0xe8` | 1 | `csdailyteam.py` |
| `C2GS_BIGDATA=0xea` | 1 | `csbigdata.py` |
| `C2GS_CONSIGNMENT_SALE=0xe1` | 1 | `csconsignmall.py` |
| `C2GS_ENTRUST=0xec` | 1 | `c2sweituonew.py` |
| `C2GS_FRDZONE=0xe9` | 1 | `csnewmyq.py` |
| `C2GS_HUODONG=0xcd` | 30 | `cs2021newyeargift.py`, `cs2021springactivity.py`, `cs2021summerlottery.py`, `csNZZJ2019.py`, `cscatchfish.py`, `csconfession.py` 等 |
| `C2GS_MARRY=0x88` | 1 | `netmarriageseeking.py` |
| `C2GS_OPEN_UI=0x58` | 1 | `csyanzhiguan.py` |
| `C2GS_OPEN_UI_NEW=0xe6` | 1 | `csopenui.py` |
| `C2GS_PERFORM=0x42` | 1 | `cshuajing.py` |
| `C2GS_PRE_ROLE=0xeb` | 1 | `csprerole.py` |
| `C2GS_UNIQUE_DEVICE=0xe3` | 1 | `csuniquedevice.py` |
| `DEVICE=0xe3` | 1 | `csuniquedevice.py` |
| `DONG=0xcd` | 1 | `cs2021newyeargift.py` |
| `GS2C=0xce` | 1 | `csdailyscore.py` |
| `GS2C_BAND=0xec` | 1 | `csdailyteam.py` |
| `GS2C_BLOCK=0x4d` | 1 | `cshuajing.py` |
| `GS2C_CONSIGNMENT_SALE=0xe5` | 1 | `csconsignmall.py` |
| `GS2C_ENTRUST=0xed` | 1 | `c2sweituonew.py` |
| `GS2C_FRDZONE=0xef` | 1 | `csnewmyq.py` |
| `GS2C_HUODONG_OP=0xce` | 33 | `cs2021newyeargift.py`, `cs2021springactivity.py`, `cs2021summerlottery.py`, `csNZZJ2019.py`, `csbestlover.py`, `cscatchfish.py` 等 |
| `GS2C_MARRY=0x38` | 1 | `netmarriageseeking.py` |
| `GS2C_OPEN_UI=0x59` | 1 | `csyanzhiguan.py` |
| `GS2C_OPEN_UI_NEW=0xe6` | 1 | `csopenui.py` |
| `GS2C_OPEN_UI_NEW=0xea` | 1 | `csopenui.py` |
| `GS2C_PRE_ROLE=0xf0` | 1 | `csprerole.py` |
| `GS2C_UNIQUE_DEVICE=0xe7` | 1 | `csuniquedevice.py` |

## 各模块命令

### `script\dialog\newyearwish\netnewyearwish.py` (entry1400)
- C2GS (10):
  - `C2GSChangePriv(?)`
  - `C2GSGetGoodAmount(?)`
  - `C2GSGetShareInfo(?)`
  - `C2GSGiveGood(?)`
  - `C2GSMakeWish(?)`
  - `C2GSOpenWishCard(?)`
  - `C2GSOpenWishUI(?)`
  - `C2GSRefreshShowUI(?)`
  - `C2GSSetShareInfo(?)`
  - `C2GSShareWish(?)`

### `script\dialog\presentcenter\netprerole.py` (entry1810)
- C2GS (3):
  - `C2GSBindPayMember(?)`
  - `C2GSOpenPrePay(?)`
  - `C2GSQuestAllCharge(?)`

### `script\dialog\presentcenter\netsummervacation.py` (entry552)
- C2GS (2):
  - `C2GSGetSummerVacationInfo(?)`
  - `C2GSSignSummerVHcation(?)`

### `script\dialog\qixi\netqixi\netqixi.py` (entry2265)
- C2GS (14):
  - `C2GSCancelBindFriend(?)`
  - `C2GSChangeFriend(?)`
  - `C2GSChangeLabel(?)`
  - `C2GSChooseLabel(?)`
  - `C2GSOpenFate(?)`
  - `C2GSRequestBindFriend(?)`
  - `C2GSRequestFriendList(?)`
  - `C2GSRequestQixiTask(?)`
  - `C2GSRequestTestResult(?)`
  - `C2GSRollLottery(?)`
  - `C2GSSendRestTime(?)`
  - `C2GSSendTaskComplete(?)`
  - `C2GSStartChat(?)`
  - `C2GSWorldFindFriend(?)`

### `script\login\netlogin.py` (entry4082)
- C2GS (1):
  - `C2GSRoleInfoLog(?)`

### `script\mxgame\activity\2019double12shop\net2019double12shop.py` (entry1882)
- C2GS (5):
  - `C2GSChangeShoujue(?)`
  - `C2GSGetName(?)`
  - `C2GSOpenCelebration(?)`
  - `C2GSSelectLastBuy(?)`
  - `C2GSShowShoujue(?)`

### `script\mxgame\activity\2021duangwu\netduanwu2021.py` (entry952)
- C2GS (10):
  - `C2GSClickZongziActBtn(?)`
  - `C2GSHelpSpeedUp(?)`
  - `C2GSIllustratedbooksDlg(?)`
  - `C2GSInitiateHelp(?)`
  - `C2GSOpenPersonalHelpDlg(?)`
  - `C2GSOpenSeekHelpList(?)`
  - `C2GSReceiveAward(?)`
  - `C2GSRequestMainDlgData(?)`
  - `C2GSSeekHelp(?)`
  - `C2GSSpeedUp(?)`

### `script\mxgame\activity\2021newyeargift\net2021newyeargift.py` (entry1136)
- C2GS (2):
  - `C2GSClickBtn(?)`
  - `C2GSOpenSubPage(?)`

### `script\mxgame\activity\2021summerlottery\net2021summerlottery.py` (entry7)
- C2GS (5):
  - `C2GSBuySummPoint(?)`
  - `C2GSGetAward(?)`
  - `C2GSLevelUpSummerAwards(?)`
  - `C2GSOpenSummerLotteryView(?)`
  - `C2GSOpenSummerMainView(?)`

### `script\mxgame\activity\bestlover\netbestlover.py` (entry120)
- C2GS (17):
  - `C2GSBestLoverAddFriendLog(?)`
  - `C2GSChangeDeclaration(?)`
  - `C2GSConfirmSign(?)`
  - `C2GSConfirmSignUp(?)`
  - `C2GSGetLoversInfo(?)`
  - `C2GSGetMoreList(?)`
  - `C2GSGetReward(?)`
  - `C2GSGetSearchList(?)`
  - `C2GSOpenBestLoverDlg(?)`
  - `C2GSOpenFollwerDlg(?)`
  - `C2GSOpenMyTeamDlg(?)`
  - `C2GSOpenSignUpDlg(?)`
  - `C2GSPublicity(?)`
  - `C2GSRefuseJoin(?)`
  - `C2GSRequestFix(?)`
  - `C2GSSendFlower(?)`
  - `C2GSVote(?)`

### `script\mxgame\activity\dailykeju\netdailykeju.py` (entry1777)
- C2GS (5):
  - `C2GSEnterAnswer(?)`
  - `C2GSOpenDlg(?)`
  - `C2GSOpenLinker(?)`
  - `C2GSPictureUrl(?)`
  - `C2GSPictureUrlEx(?)`

### `script\mxgame\activity\gopenguin\netgopenguin.py` (entry1624)
- C2GS (1):
  - `C2GSRequestMinMapNpcPos(?)`

### `script\mxgame\activity\ladderrankallstar\netladderrankallstar.py` (entry2682)
- C2GS (16):
  - `C2GSAllRankInfo(?)`
  - `C2GSCloseZhuwei(?)`
  - `C2GSCreateTeam(?)`
  - `C2GSGuessBuyItem(?)`
  - `C2GSGuessChampion(?)`
  - `C2GSGuessGame(?)`
  - `C2GSGuessTips(?)`
  - `C2GSMatchTip(?)`
  - `C2GSOpenChampionGuessUI(?)`
  - `C2GSOpenFirstGuess(?)`
  - `C2GSOpenGuessShop(?)`
  - `C2GSOpenGuessUI(?)`
  - `C2GSTeamInfo(?)`
  - `C2GSTeamTip(?)`
  - `C2GSWatchViedo(?)`
  - `C2GSZhuwei(?)`

### `script\mxgame\activity\mengxiang3activity\netactivity\netsameheartplant.py` (entry3772)
- C2GS (5):
  - `C2GSClickReward(?)`
  - `C2GSOpenPage(?)`
  - `C2GSPlantFriend(?)`
  - `C2GSSayHello(?)`
  - `C2GSUseWater(?)`

### `script\mxgame\activity\mxkitchen\netmxkitchen.py` (entry4480)
- C2GS (2):
  - `C2GSClickNpc(?)`
  - `C2GSLeaveScene(?)`

### `script\mxgame\activity\newcatchfish\netnewcatchfish.py` (entry4963)
- C2GS (2):
  - `C2GSCatchFish(?)`
  - `C2GSLeaveScene(?)`

### `script\mxgame\activity\newracingspeed\netnewracingspeed.py` (entry3298)
- C2GS (14):
  - `C2GSBarrierCatchHero(?)`
  - `C2GSBoxGameClick(?)`
  - `C2GSClickDance(?)`
  - `C2GSClickQuestion(?)`
  - `C2GSClientNpcMove(?)`
  - `C2GSClosePhraseDialog(?)`
  - `C2GSPhraseAnswer(?)`
  - `C2GSPlayerEnterCircle(?)`
  - `C2GSPushStone(?)`
  - `C2GSRewarBoxClick(?)`
  - `C2GSTuLangChoose(?)`
  - `C2GSUseProps(?)`
  - `C2GSUsePropsOnRole(?)`
  - `C2GSUseStrongCard(?)`

### `script\mxgame\activity\piaoliuping\netseamail.py` (entry4545)
- C2GS (16):
  - `C2GSAddSuperReward(?)`
  - `C2GSBindHelpPlayer(?)`
  - `C2GSBuyHight(?)`
  - `C2GSChickHuoyueReward(?)`
  - `C2GSClickLuckDraw(?)`
  - `C2GSGetHelpGift(?)`
  - `C2GSGetReturnGift(?)`
  - `C2GSJKDrawReward(?)`
  - `C2GSJKGetDailogData(?)`
  - `C2GSJKGetReward(?)`
  - `C2GSOpenBottle(?)`
  - `C2GSOpenDlgAsk(?)`
  - `C2GSOpenQiRiDlg(?)`
  - `C2GSOpenWishDlg(?)`
  - `C2GSShareAndRecruit(?)`
  - `C2GSSign(?)`

### `script\mxgame\activity\school\netschooladmission.py` (entry2955)
- C2GS (1):
  - `C2GSCustomOP(?)`
- GS2C (1):
  - `GS2COpenDlg(?)`

### `script\mxgame\activity\summertrainpet\netsummertrainpet.py` (entry527)
- C2GS (5):
  - `C2GSAddZiZhi(?)`
  - `C2GSOpenTrainDlg(?)`
  - `C2GSRequestFumoRange(?)`
  - `C2GSSelectSummon(?)`
  - `C2GSShengLing(?)`

### `script\mxgame\activity\timewheel\net\nettimewheeldelegate.py` (entry3886)
- C2GS (11):
  - `C2GSAskEntrustSelect(?)`
  - `C2GSChangeEntrust(?)`
  - `C2GSChangeNewTaskInformState(?)`
  - `C2GSChangeQuickAcceptState(?)`
  - `C2GSChangeZhiyeRewardType(?)`
  - `C2GSConfirmClause(?)`
  - `C2GSQuickGetReward(?)`
  - `C2GSRequestLinkWeituoState(?)`
  - `C2GSRequestNewTaskInformState(?)`
  - `C2GSSetEntrustSelect(?)`
  - `C2GSShowEntrustConsume(?)`

### `script\mxgame\activity\yardmatch\netyardmatch.py` (entry4926)
- C2GS (12):
  - `C2GSApply(?)`
  - `C2GSCloseApplyDlg(?)`
  - `C2GSFollow(?)`
  - `C2GSGetEntriesList(?)`
  - `C2GSGetMyEntriesData(?)`
  - `C2GSGetPlayerCardData(?)`
  - `C2GSGetYardSnapShot(?)`
  - `C2GSOpenYardMatchMainDLg(?)`
  - `C2GSPublicize(?)`
  - `C2GSSaveAndUpload(?)`
  - `C2GSSearchEntries(?)`
  - `C2GSVote(?)`

### `script\mxgame\activity\yearsummary\netyearsum.py` (entry4270)
- C2GS (3):
  - `C2GSAskInfo(?)`
  - `C2GSDelComment(?)`
  - `C2GSSendComment(?)`

### `script\mxgame\appearance\net\netappearance.py` (entry1242)
- C2GS (18):
  - `C2GSAppearanceChgShape(?)`
  - `C2GSAppearanceChgShapeConfirm(?)`
  - `C2GSAppearanceConfirmPTDye(?)`
  - `C2GSAppearanceDelFreeDye(?)`
  - `C2GSAppearanceDelTmpDye(?)`
  - `C2GSAppearanceFreeDye(?)`
  - `C2GSAppearancePTDye(?)`
  - `C2GSAppearanceSaveFreeDye(?)`
  - `C2GSAppearanceTGF(?)`
  - `C2GSAskGiveItemPrice(?)`
  - `C2GSAskTeamMarkInfo(?)`
  - `C2GSBuyBack(?)`
  - `C2GSConfirmDye(?)`
  - `C2GSDyeBack(?)`
  - `C2GSGetOwnBack(?)`
  - `C2GSOpenGiftDlgForHsvColor(?)`
  - `C2GSQuickBuyFlower(?)`
  - `C2GSWearBack(?)`
- GS2C (1):
  - `GS2CReplyGiveItemPrice(?)`

### `script\mxgame\auction\nethdidauction.py` (entry4385)
- C2GS (7):
  - `C2GSAskForNextAuction(?)`
  - `C2GSBid(?)`
  - `C2GSCloseDlg(?)`
  - `C2GSModifyAutoBid(?)`
  - `C2GSOpenAucDlg(?)`
  - `C2GSSetAutoBid(?)`
  - `C2GSSetRemind(?)`

### `script\mxgame\autoupgrade\netautoupgrade.py` (entry4439)
- C2GS (2):
  - `C2GSGetAutoUpgradeData(?)`
  - `C2GSNeverShowUpgradePage(?)`

### `script\mxgame\bigdata\netbigdata.py` (entry2131)
- C2GS (4):
  - `C2GSOpenFrdList(?)`
  - `C2GSOpenFrdZoneTL(?)`
  - `C2GSOpenFriendFrdZone(?)`
  - `C2GSOpenMainFrdZone(?)`

### `script\mxgame\consignmentsalecenter\model\netconsignmall.py` (entry2777)
- C2GS (21):
  - `C2GSAddMyGoods(?)`
  - `C2GSAddMySummon(?)`
  - `C2GSBuyGoods(?)`
  - `C2GSBuyVictualGoods(?)`
  - `C2GSEnterOneShelf(?)`
  - `C2GSGetGoodsDetail(?)`
  - `C2GSGetReferencePrice(?)`
  - `C2GSGetShelfItemRefPrice(?)`
  - `C2GSGetSkillInfo(?)`
  - `C2GSGetSummonRealID(?)`
  - `C2GSOpenRecord(?)`
  - `C2GSOpenSalePage(?)`
  - `C2GSReAddMyGoods(?)`
  - `C2GSReAddMyPet(?)`
  - `C2GSRefreshGoods(?)`
  - `C2GSRefreshTime(?)`
  - `C2GSRemoveMyGoods(?)`
  - `C2GSRemoveMySummon(?)`
  - `C2GSSaveDiscount(?)`
  - `C2GSSummonTakeCash(?)`
  - `C2GSTakeCash(?)`

### `script\mxgame\dailyteam\netdailyteam.py` (entry1790)
- C2GS (21):
  - `C2GSApplyBand(?)`
  - `C2GSAttention(?)`
  - `C2GSBandPublishRecomend(?)`
  - `C2GSBandPublishRecruit(?)`
  - `C2GSBandTaskData(?)`
  - `C2GSChangeLeader(?)`
  - `C2GSConfimApply(?)`
  - `C2GSDelApplyInfo(?)`
  - `C2GSGetApplyInfo(?)`
  - `C2GSGetDailyTeamInfo(?)`
  - `C2GSGetHideBandState(?)`
  - `C2GSHideBand(?)`
  - `C2GSInviteFriend(?)`
  - `C2GSKickMember(?)`
  - `C2GSLeaveDailyTeam(?)`
  - `C2GSOneKeyJoinTeam(?)`
  - `C2GSOpenChangeLeader(?)`
  - `C2GSOpenInviteFriendDlg(?)`
  - `C2GSSetBandTitle(?)`
  - `C2GSSimpleInfo(?)`
  - `C2GSTouchLeader(?)`

### `script\mxgame\gongji\netdailyscore.py` (entry507)
- C2GS (2):
  - `C2GSGiveItem(?)`
  - `C2GSOpenGZUI(?)`

### `script\mxgame\goodvoice\netgoodvoice.py` (entry54)
- C2GS (12):
  - `C2GSBroadCastGoodVoice(?)`
  - `C2GSDeletePIC(?)`
  - `C2GSDeleteVoice(?)`
  - `C2GSGetPageInfo(?)`
  - `C2GSGetSingerInfo(?)`
  - `C2GSJubao(?)`
  - `C2GSOpenFlowerRecord(?)`
  - `C2GSOpenSendFlowerDlg(?)`
  - `C2GSSendFlower(?)`
  - `C2GSSetShowPIC(?)`
  - `C2GSUploadVoice(?)`
  - `C2GSVote(?)`

### `script\mxgame\lottery\net2020springlottery.py` (entry32)
- C2GS (2):
  - `C2GSOpenLotteryDlg(?)`
  - `C2GSStartLottery(?)`
- GS2C (2):
  - `GS2CLotteryResult(?)`
  - `GS2COpenLotteryDlg(?)`

### `script\mxgame\marriage\netmarriageseeking.py` (entry2642)
- opcode `C2GS_MARRY=0x88` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- opcode `GS2C_MARRY=0x38` iSub=[1, 2, 3]

### `script\mxgame\mxride\net\netride.py` (entry1272)
- C2GS (6):
  - `C2GSActiveMode(?)`
  - `C2GSDelActive(?)`
  - `C2GSResetRideEquipment(?)`
  - `C2GSResetRideSkill(?)`
  - `C2GSRideSkillUp(?)`
  - `C2GSRideUp(?)`

### `script\mxgame\myqnew\netnewmyq.py` (entry4262)
- C2GS (9):
  - `C2GSAddShow(?)`
  - `C2GSCheckRelation(?)`
  - `C2GSComment(?)`
  - `C2GSDelComment(?)`
  - `C2GSDelShow(?)`
  - `C2GSGetOneShow(?)`
  - `C2GSMessagePage(?)`
  - `C2GSPro(?)`
  - `C2GSRequestFrdZonePage(?)`

### `script\mxgame\nethuodong\activity\nethdpresentcenter.py` (entry2716)
- C2GS (7):
  - `C2GSBackManGiftBuyItem(?)`
  - `C2GSBackManGiftClickIcon(?)`
  - `C2GSBackManGiftGetInfo(?)`
  - `C2GSCloseReturnOldPlayerRedPoint(?)`
  - `C2GSGetDailyLottery(?)`
  - `C2GSGetFirstChargeInfo(?)`
  - `C2GSOpenDailyLottery(?)`

### `script\mxgame\nethuodong\activity\nethdquestinfo.py` (entry1567)
- C2GS (2):
  - `C2GSKejuFlySwordScore(?)`
  - `C2GSKejuPoetry(?)`
- GS2C (1):
  - `GS2CRefreshHuishiJNNum(?)`

### `script\mxgame\pet\lianyao\talent\netsummontalent.py` (entry4345)
- C2GS (10):
  - `C2GSClearTalent(?)`
  - `C2GSCloseTalentResultDlg(?)`
  - `C2GSGetTalentCase(?)`
  - `C2GSLearnTalent(?)`
  - `C2GSOpenTalentTarget(?)`
  - `C2GSReplaceTempTalent(?)`
  - `C2GSResetTalent(?)`
  - `C2GSSaveResetTalent(?)`
  - `C2GSSaveTalent(?)`
  - `C2GSSetTalentTarget(?)`
- GS2C (7):
  - `GS2CCloseResultDlg(?)`
  - `GS2CRefreshLeftLing(?)`
  - `GS2CShowEffect(?)`
  - `GS2CTalentInfo(?)`
  - `GS2CTalentResult(?)`
  - `GS2CTalentTargetInfo(?)`
  - `GS2CUpdateSaveResult(?)`

### `script\mxgame\recordiconfunc\audiocard\netvoicecard.py` (entry2817)
- C2GS (5):
  - `C2GSDeleteAudio(?)`
  - `C2GSJuBao(?)`
  - `C2GSOpenUI(?)`
  - `C2GSRequestAudioExist(?)`
  - `C2GSUploadAudioSuccess(?)`

### `script\mxgame\redpoint\netreddot.py` (entry4244)
- GS2C (2):
  - `GS2CAddRedDot(?)`
  - `GS2CDelRedDot(?)`

### `script\mxgame\rookieback\netrookieback.py` (entry2095)
- C2GS (9):
  - `C2GSAddSuperReward(?)`
  - `C2GSBuyPayLB(?)`
  - `C2GSChickHuoyueReward(?)`
  - `C2GSClickLuckDraw(?)`
  - `C2GSClickXinxiuChuanGon(?)`
  - `C2GSGetShouChongReward(?)`
  - `C2GSOpenMainDlg(?)`
  - `C2GSOpenWishDlg(?)`
  - `C2GSRewardTask(?)`

### `script\mxgame\sevendaytarget\netsevendaytarget.py` (entry3236)
- C2GS (3):
  - `C2GSOpenDialog(?)`
  - `C2GSRewarTask(?)`
  - `C2GSRewardDayTask(?)`

### `script\mxgame\yearvoice\netannualdreamvoice.py` (entry2107)
- C2GS (16):
  - `C2GSAdvertise(?)`
  - `C2GSAttention(?)`
  - `C2GSDeleteVoice(?)`
  - `C2GSGetPageInfo(?)`
  - `C2GSGetRecordRank(?)`
  - `C2GSGetSingerInfo(?)`
  - `C2GSJubao(?)`
  - `C2GSOpenAllPro(?)`
  - `C2GSOpenPersonalInfo(?)`
  - `C2GSOpenRegisterUI(?)`
  - `C2GSOpenSendFlowerDlg(?)`
  - `C2GSSendFlower(?)`
  - `C2GSSetShowPIC(?)`
  - `C2GSSetTop(?)`
  - `C2GSUploadVoice(?)`
  - `C2GSVote(?)`

### `script\netgm.py` (entry4531)
- GS2C (1):
  - `GS2CGMLookGroupInfo(?)`

### `script\netgoodsserver.py` (entry3556)
- GS2C (3):
  - `GS2CCloseQuickBuy(?)`
  - `GS2CGetServerGoodsData(?)`
  - `GS2CQuickBuyInfo(?)`

### `script\nethero.py` (entry826)
- C2GS (2):
  - `C2GSGetSendUpCode(?)`
  - `C2GSSelectTitle(?)`

### `script\netnpc.py` (entry731)
- C2GS (1):
  - `C2GSQuestItemString(?)`

### `script\netopenui.py` (entry1425)
- C2GS (2):
  - `C2GSClickJinXiu(?)`
  - `C2GSSendLogDataEx(?)`
- GS2C (1):
  - `GS2CActivityOpenDlg(?)`

### `script\netpet.py` (entry1599)
- C2GS (4):
  - `C2GSAddPointAttr(?)`
  - `C2GSOpenQuickHuanTongBuy(?)`
  - `C2GSSendPetSort(?)`
  - `C2GSSummonSoulBind(?)`

### `script\netrichman.py` (entry2982)
- C2GS (2):
  - `C2GSCheckMatch(?)`
  - `C2GSLeaveGame(?)`

### `script\netshop.py` (entry1848)
- GS2C (1):
  - `GS2C_SHOP(?)`

### `script\protocol\c2sweituonew.py` (entry2785)
- opcode `C2GS_ENTRUST=0xec` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
- opcode `GS2C_ENTRUST=0xed` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
- C2GS (20):
  - `C2GSAskEntrustSelect()`
  - `C2GSCancelWeituo(iType=%s)`
  - `C2GSChangeEntrust(iType=%s,iModel=%s)`
  - `C2GSChangeNewTaskInformState(iState=%s)`
  - `C2GSChangeQuickAcceptState(iType=%s,iState=%s)`
  - `C2GSChangeZhiyeRewardType(iGrade=%s)`
  - `C2GSConfirmClause(iType=%s)`
  - `C2GSDrawReward(iType=%s)`
  - `C2GSGoToWeituo()`
  - `C2GSOpenPick()`
  - `C2GSOpenPublish(iType=%s,iModel=%s)`
  - `C2GSOpenWeituo()`
  - `C2GSPick(iTargetID=%s,iType=%s)`
  - `C2GSPublish(lstWeituo=%s,lstTarget=%s)`
  - `C2GSQuickGetReward()`
  - `C2GSRequestEntrustData(iType=%s)`
  - `C2GSRequestLinkWeituoState(iPubID=%s,iTypeLst=%s)`
  - `C2GSRequestNewTaskInformState()`
  - `C2GSSetEntrustSelect(iType=%s)`
  - `C2GSShowEntrustConsume(iTaskTag=%s)`
- GS2C (17):
  - `GS2CCloseWeituoUI()`
  - `GS2CEntrustChange(iModel=%s,iTask=%s,lstOrderPid=%s)`
  - `GS2CEntrustData(iType=%s,lstEntrustData=%s)`
  - `GS2CGetRewardSucceed()`
  - `GS2COneWeituoInfo(lstWeituo=%s,iAllDur=%s,iOrderGroup=%s,iOrderHYX=%s,lstQuick=%s)`
  - `GS2COpenClauseDlg()`
  - `GS2COpenQuickGetReward()`
  - `GS2COpenWeituo(iType=%s,iPageParam=%s)`
  - `GS2CPickInfo(lstType=%s)`
  - `GS2CPickWeituoInfo(iType=%s,iProcess=%s,iMaxProcess=%s,iEndTime=%s)`
  - `GS2CPublishInfo(iMode=%s,lstFrd=%s,lstBatchWeituoInfo=%s)`
  - `GS2CPublishRes(iType=%s,iRes=%s)`
  - `GS2CRefreshLinkWeituoState(iPubID=%s,lTypeInfo=%s)`
  - `GS2CSetNewTaskInformState(iState=%s)`
  - `GS2CSetOrgEntrustLinkState(iState=%s)`
  - `GS2CUpdateEntrustType(iType=%s)`
  - `GS2CWeituoInfo(lstWeituo=%s,iAllDur=%s,iOrderGroup=%s,iOrderHYX=%s,lstQuick=%s)`

### `script\protocol\cs2019double12shop.py` (entry2948)
- C2GS (16):
  - `C2GSAddShoppingCart(iType=%s,iPos=%s,iItemNum=%s)`
  - `C2GSBuy()`
  - `C2GSBuyPecial(iPos=%s,iItemSID=%s)`
  - `C2GSChangeShop()`
  - `C2GSChangeShoujue(lstShoujue=%s)`
  - `C2GSGetEndTime()`
  - `C2GSGetName()`
  - `C2GSInsertShoppingCart(iPos=%s,iItemSID=%s,iItemNum=%s)`
  - `C2GSIsOpen()`
  - `C2GSOpenCelebration()`
  - `C2GSRefreshShopBuy()`
  - `C2GSSelectLastBuy()`
  - `C2GSShop1212ItemList()`
  - `C2GSShoppingCart()`
  - `C2GSShoppingCartSelect(iItemSID=%s,iType=%s)`
  - `C2GSShowShoujue()`
- GS2C (13):
  - `GS2CAllCelebrationInfo(iLeftTimes=%s,iGetName=%s,iSg=%s,bChangShoujue=%s)`
  - `GS2CAllShoppingCart(lstGoods=%s,iDiscount=%s)`
  - `GS2CCelebrationBuyTimes(iLeftTimes=%s)`
  - `GS2CCelebrationGetName(iGetName=%s)`
  - `GS2CCloseCartDialog()`
  - `GS2CCloseShoujue()`
  - `GS2CEndTime(iType=%s,iEndTime=%s)`
  - `GS2CIsOpen(iType=%s,iEndTime=%s)`
  - `GS2CRefreshBuyTimes(iShopTimes=%s,iBookTimes=%s)`
  - `GS2CRefreshRedPoint(iGiftPoint=%s,iNamePoint=%s)`
  - `GS2CRefreshShopBuyTimes(iShopBuyTimes=%s,iShopMaxTimes=%s)`
  - `GS2CShop1212ItemList(lstGoods=%s,iUsePrice=%s)`
  - `GS2CShowShoujue(lstShoujue=%s)`

### `script\protocol\cs2021newyeargift.py` (entry1588)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `DONG=0xcd` iSub=[4]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6]
- C2GS (4):
  - `C2GSClickBtn(iBtnType=%s)`
  - `C2GSGetLuckyKing()`
  - `C2GSOpenMyGongXian()`
  - `C2GSOpenPage(iOpenNum=%s)`
- GS2C (6):
  - `GS2CGetGift(dGetGiftList=%s)`
  - `GS2CLuckyKing(sName=%s)`
  - `GS2CMyGongXian(bBefore=%s,iReady=%s,iRecieve=%s,lGiftInfoList=%s)`
  - `GS2COpenGetGift(dGetGiftList=%s,iBestItemID=%s,iReadyNum=%s,lAvatarInfoList=%s,iBuLingType=%s)`
  - `GS2COpenGiftInfo(dGiftInfoList=%s,iReadyNum=%s,iGiftItemNum=%s)`
  - `GS2CReadyGift(iShape=%s,iNum=%s,iMaxNum=%s,iReadyNum=%s,iGiftItemNum=%s)`

### `script\protocol\cs2021springactivity.py` (entry3692)
- opcode `C2GS_HUODONG=0xcd` iSub=[1]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (2):
  - `C2GSSendLogData(dAllData=%s)`
  - `C2GSSendLogDataEx(?)`
- GS2C (1):
  - `GS2COpenDlg(iActivityID=%s)`

### `script\protocol\cs2021summerlottery.py` (entry4552)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (5):
  - `C2GSBuySummPoint()`
  - `C2GSGetReward(iLevel=%s,iAwardId=%s)`
  - `C2GSOpenSummerMain()`
  - `C2GSOpenSummerReward()`
  - `C2GSSummerRewardUp()`
- GS2C (2):
  - `GS2COpenSummerMain(iLotteryNum=%s)`
  - `GS2COpenSummerReward(iLotteryNum=%s,iLevelAward=%s,dRewardInfo=%s)`

### `script\protocol\csNZZJ2019.py` (entry1488)
- opcode `C2GS_HUODONG=0xcd` iSub=[1]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (1):
  - `C2GSAskInfo(?)`
- GS2C (1):
  - `GS2CRefreshInfo(?)`

### `script\protocol\csbestlover.py` (entry4608)
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
- C2GS (17):
  - `C2GSChangeDeclaration(sDeclaration=%s)`
  - `C2GSConfirmSign(iLeaderID=%s)`
  - `C2GSConfirmSignUp(iLeaderID=%s,iMemberID=%s,sTeamName=%s,sDeclaration=%s)`
  - `C2GSGetLoversInfo(iLeaderID=%s)`
  - `C2GSGetMoreList(iCurListSum=%s)`
  - `C2GSGetReward()`
  - `C2GSGetSearchList(sSearchText=%s)`
  - `C2GSGiveRecordAddFriendLog(iAddPlayerID=%s)`
  - `C2GSOpenBestLoverDlg(iLeaderID=%s)`
  - `C2GSOpenFollwerDlg(iLeaderID=%s)`
  - `C2GSOpenMyTeamDlg()`
  - `C2GSOpenSignUpDlg()`
  - `C2GSPublicity(iLeaderID=%s)`
  - `C2GSRefuseSign(iLeaderID=%s)`
  - `C2GSRequestFix(iLeaderID=%s)`
  - `C2GSSendFlower(iLeaderID=%s,iFlowerNum=%s)`
  - `C2GSVote(iLeaderID=%s)`
- GS2C (10):
  - `GS2CCloseSignDlg()`
  - `GS2CGetLoversInfo(iLeaderID=%s,iLoverNumber=%s,sDeclaration=%s,sTeamName=%s,lstPlayer=%s)`
  - `GS2CGetMoreList(lstLover=%s)`
  - `GS2CGetSearchList(lstLover=%s)`
  - `GS2COpenBestLoverDlg(iLeaderID=%s)`
  - `GS2COpenMyTeamDlg(iTicketNum=%s,iLoverNumber=%s,sDeclaration=%s,sTeamName=%s,lstPlayer=%s)`
  - `GS2CRefreshMainDlg(iSignUpEndTime=%s,iMyLeaderID=%s,iHasRank=%s,lstLover=%s,iShowLeaderID=%s)`
  - `GS2CRefreshMemberSignDlg(sTeamName=%s,sDeclaration=%s)`
  - `GS2CSendFollwer(lstRecord=%s)`
  - `GS2CSignSuccess(iLeaderID=%s)`

### `script\protocol\csbigdata.py` (entry4981)
- opcode `C2GS_BIGDATA=0xea` iSub=[1, 2, 3, 4, 5]
- C2GS (4):
  - `C2GSHangUpTime(iEven=%s)`
  - `C2GSOpenFrdZoneTL()`
  - `C2GSOpenFriendFrdZone()`
  - `C2GSOpenMainFrdZone()`

### `script\protocol\cscatchfish.py` (entry2627)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- C2GS (2):
  - `C2GSCatchFish(iFishList=%s,iFishingNetX=%s,iFishingNetY=%s)`
  - `C2GSLeaveScene()`
- GS2C (9):
  - `GS2CCatchFish(iFishList=%s,iFishingNetX=%s,iFishingNexY=%s,iPlayerID=%s,iFishingNetType=%s)`
  - `GS2CChangeFishingNet(iType=%s)`
  - `GS2CCreateFish(iFishList=%s)`
  - `GS2CEndFishing()`
  - `GS2CEnterScene(iEndTimeStamp=%s,iPlayerScore=%s,iDurability=%s,TeamScoreInfoLst=%s,iEnterTimes=%s)`
  - `GS2CFishScare(iFishList=%s)`
  - `GS2CUpdateDurability(iDurability=%s)`
  - `GS2CUpdateScore(iPlayerScore=%s)`
  - `GS2CUpdateTeamScoreInfo(TeamScoreInfoLst=%s)`

### `script\protocol\csconfession.py` (entry179)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (2):
  - `C2GSPraise(sParma=%s)`
  - `C2GSShare(iItemID=%s,iPlayerID=%s,sPlayerName=%s,sContent=%s,iZaoyao=%s)`
- GS2C (1):
  - `GS2COpenDlg(iItemID=%s)`

### `script\protocol\csconsignmall.py` (entry2933)
- opcode `C2GS_CONSIGNMENT_SALE=0xe1` iSub=[1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22]
- opcode `GS2C_CONSIGNMENT_SALE=0xe5` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]
- C2GS (20):
  - `C2GSAddMyGoods(iID=%s,iPrice=%s,iAmount=%s)`
  - `C2GSAddMySummon(iID=%s,iPrice=%s)`
  - `C2GSBuyGoods(iOwner=%s,iIdx=%s,iPrice=%s,iAmount=%s,iType=%s,iID=%s,iMode=%s,iPage=%s)`
  - `C2GSBuyVictualGoods(iSkillType=%s,iOwner=%s)`
  - `C2GSEnterOneShelf(iShelfID=%s,iStartPage=%s,iEndPage=%s,lstNeedItem=%s)`
  - `C2GSGetGoodsDetail(iOwner=%s,iIdx=%s,iType=%s)`
  - `C2GSGetReferencePrice(iID=%s)`
  - `C2GSGetShelfItemRefPrice(iID=%s,iIdx=%s)`
  - `C2GSGetSkillInfo(iSkillType=%s,iShelfVersion=%s)`
  - `C2GSGetSummonRealID(iOwner=%s,iIdx=%s)`
  - `C2GSOpenSalePage(iType=%s)`
  - `C2GSReAddMyGoods(lstGoods=%s,iIsOneKey=%s)`
  - `C2GSReAddMyPet(iID=%s,iIdx=%s,iPrice=%s,iAmount=%s)`
  - `C2GSRefreshGoods(iIsFree=%s)`
  - `C2GSRefreshTime()`
  - `C2GSRemoveMyGoods(iID=%s)`
  - `C2GSRemoveMySummon(iID=%s)`
  - `C2GSSaveDiscount(iDiscount=%s)`
  - `C2GSSummonTakeCash(iIdx=%s)`
  - `C2GSTakeCash(iIdx=%s)`
- GS2C (24):
  - `GS2CAllCookSkill(iShelfVersion=%s,lstPlayersSkill=%s)`
  - `GS2CAllGoodsOfShelf(iShelfID=%s,iAllGoodsAmount=%s,dGoods=%s)`
  - `GS2CAllNormalSkill(iShelfVersion=%s,iSkillType=%s,lstPlayer=%s)`
  - `GS2CAllRecord(iConsignReward=%s,iSaleReward=%s,lstRecord=%s)`
  - `GS2CBuyStoreSuccess(iOwner=%s,iStoreNpc=%s,iType=%s,iSkill=%s)`
  - `GS2CCanOpenDlg(iMode=%s)`
  - `GS2CDeleteGoodsOfShelf(iShelfID=%s,iOwner=%s,iIdx=%s)`
  - `GS2CIsGoodSale(iSale=%s,iTime=%s)`
  - `GS2CMyAllGoods(lstGoods=%s)`
  - `GS2CMyAllSummons(lstSummons=%s)`
  - `GS2COpenDlg()`
  - `GS2CReShelfDiscount(iDiscount=%s)`
  - `GS2CReferencePrice(iID=%s,iPrice=%s,iPriceUid=%s)`
  - `GS2CRefreshGoods()`
  - `GS2CRefreshSaleInfo(iOwnerID=%s,sOwnerName=%s,iOnlineState=%s,sSaleTitle=%s)`
  - `GS2CRefreshTime(iTime=%s)`
  - `GS2CRemoveOneNormalSkill(iShelfVersion=%s,iOwner=%s,iSkillType=%s)`
  - `GS2CRemoveOnePlayerCookSkill(iShelfVersion=%s,iOwner=%s)`
  - `GS2CShelfItemRefPrice(iPrice=%s,iIdx=%s,iID=%s,iPriceUid=%s)`
  - `GS2CShowSummonerRedDot()`
  - `GS2CSummonRealID(iOwner=%s,iIdx=%s,iSummonID=%s)`
  - `GS2CUpdateGoodsOfShelf(iShelfID=%s,iOwner=%s,iIdx=%s,iGoodsID=%s,iShape=%s,iAmount=%s,iPrice=%s,iTime=%s,sExt=%s)`
  - `GS2CUpdateOneNormalSkill(iShelfVersion=%s,iOwner=%s,lstNormalSkill=%s,iSkillType=%s)`
  - `GS2CUpdateOnePlayerCookSkill(iShelfVersion=%s,iOwner=%s,iPrice=%s,iSkillLevel=%s,iRefPrice=%s,lstCook=%s)`

### `script\protocol\csdailykeju.py` (entry2344)
- C2GS (5):
  - `C2GSEnterAnswer(iQuestion=%s,iAnswer=%s)`
  - `C2GSOpenDlg()`
  - `C2GSOpenLinker()`
  - `C2GSPictureUrl(iQuestion=%s,iAnswer=%s,sUrl=%s)`
  - `C2GSPictureUrlEx(iServer=%s,iPlayer=%s,sUrl=%s)`
- GS2C (7):
  - `GS2CCloseDlg()`
  - `GS2COpenDlg(iQuestion=%s,iExp=%s,iRplCash=%s,iTrueNum=%s,sQuestion=%s,lstAnswer=%s)`
  - `GS2COrgHelp(iQuestion=%s,sQuestion=%s,lstAnswer=%s)`
  - `GS2CRefrshRewarInfo(iExp=%s,iRplCash=%s)`
  - `GS2CRightAnswer(iQuestion=%s,iQuestAnswer=%s,iTrueNum=%s,iChooseNum=%s)`
  - `GS2CSendPicture(iQuestion=%s,iAnswer=%s,iShape=%s,dDesc=%s)`
  - `GS2CSendPictureEx(iServer=%s,iQuestion=%s,iShape=%s,dDesc=%s)`

### `script\protocol\csdailylottery.py` (entry115)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (3):
  - `C2GSBegin()`
  - `C2GSEnd(iTargetReward=%s)`
  - `C2GSOpenView()`
- GS2C (2):
  - `GS2CCanRun(iCanRun=%s)`
  - `GS2CSelec[}JXN]K(?)`

### `script\protocol\csdailyscore.py` (entry1248)
- opcode `C2GS=0xcd` iSub=[1, 2]
- opcode `GS2C=0xce` iSub=[1]
- C2GS (1):
  - `C2GSOpenGZUI()`
- GS2C (1):
  - `GS2COpenScoreUI(iTodayGot=%s,iTodayLimit=%s,iWeekGot=%s,iWeekLimit=%s,iWeekResume=%s,iAddRate=%s)`

### `script\protocol\csdailyteam.py` (entry4768)
- opcode `C2GS_BAND=0xe8` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
- opcode `GS2C_BAND=0xec` iSub=[1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
- C2GS (22):
  - `C2GSApplyBand(iBandID=%s)`
  - `C2GSAttention(iOp=%s,iBandID=%s)`
  - `C2GSBandPublishRecomend()`
  - `C2GSBandPublishRecruit()`
  - `C2GSBandTaskData()`
  - `C2GSChangeDailyTeamIntro(sIntro=%s)`
  - `C2GSChangeLeader(iPlayerID=%s)`
  - `C2GSConfimApply(iBandID=%s,iTaskTarget=%s,iOnlineTime=%s,sIntro=%s)`
  - `C2GSDelApplyInfo(iPlayerID=%s)`
  - `C2GSGetApplyInfo()`
  - `C2GSGetDailyTeamInfo(iOpenType=%s,iBandID=%s)`
  - `C2GSGetHideBandState()`
  - `C2GSHideBand(iOp=%s)`
  - `C2GSInviteFriend(iPlayerID=%s)`
  - `C2GSKickMember(iPlayerID=%s)`
  - `C2GSLeaveDailyTeam()`
  - `C2GSOneKeyJoinTeam()`
  - `C2GSOpenChangeLeader()`
  - `C2GSOpenInviteFriendDlg()`
  - `C2GSSetBandTitle(sBandName=%s)`
  - `C2GSSimpleInfo(iOpenType=%s)`
  - `C2GSTouchLeader(iPlayerID=%s)`
- GS2C (18):
  - `GS2CApplyInfo(dApply=%s)`
  - `GS2CAttentionRes(iOp=%s,iBandID=%s)`
  - `GS2CBandLeaderID(iCaptain=%s)`
  - `GS2CBandPublishRecommend()`
  - `GS2CBandPublishRecruit(iTeamType=%s,tPlayerDataLst=%s)`
  - `GS2CBandTask(tBandTaskList=%s,iTodayPoint=%s,iWeekPoint=%s,iMaxPoint=%s)`
  - `GS2CChangeIntro(sIntro=%s)`
  - `GS2CGetDailyTeamInfo(?)`
  - `GS2CGroupSimpleBandInfo(dBand=%s)`
  - `GS2CHaveBand(iHaveBand=%s)`
  - `GS2COpenApplyDlg()`
  - `GS2COpenChangeLeader()`
  - `GS2COpenInviteFriendDlg(tFriendList=%s)`
  - `GS2COpenPage(iPage=%s)`
  - `GS2CRefreshHideBandState(iState=%s)`
  - `GS2CRefreshTeamName(sTeamName=%s)`
  - `GS2CSimpleBandInfo(dBand=%s)`
  - `GS2CTeammatesOnlineInfo(lstTeanmateInfo=%s)`

### `script\protocol\csduanwu2021.py` (entry4407)
- C2GS (10):
  - `C2GSClickZongziActBtn(iID=%s,iBtn=%s)`
  - `C2GSHelpSpeedUp(iTargetID=%s,iZongZiNo=%s)`
  - `C2GSIllustratedbooksDlg()`
  - `C2GSInitiateHelp(iID=%s)`
  - `C2GSOpenPersonalHelpDlg(iID=%s)`
  - `C2GSOpenSeekHelpList()`
  - `C2GSReceiveAward(iIdx=%s)`
  - `C2GSRequestMainDlgData()`
  - `C2GSSeekHelp(iTargetID=%s,sMsg=%s,iZongziID=%s)`
  - `C2GSSpeedUp(iType=%s,iTargetID=%s,iZongziID=%s)`
- GS2C (12):
  - `GS2CIllustratedbooksDlg(lZongzi=%s)`
  - `GS2COpenCooking(?)`
  - `GS2COpenMaterialSource(iID=%s,iShow=%s,iZongyeNoumiAmount=%s,iZongyeNoumiSumAmount=%s,lClues=%s)`
  - `GS2COpenPersonalHelpDlg(iZongziID=%s,lFriend=%s,lGroup=%s)`
  - `GS2COpenSeekHelpList(iType=%s,lSeekHelp=%s,lHelpedMe=%s)`
  - `GS2CPlaySpeedUpAnimation(iCurrSpeedUpTime=%s,iSumSpeedUpTime=%s,iEndTime=%s,iSumTime=%s)`
  - `GS2CRefreshAwardRedDot(iShow=%s)`
  - `GS2CRefreshIllustratedbookRedDot()`
  - `GS2CRefreshMainDlgData(lZongziInfo=%s,iProgress=%s,iRewardList=%s)`
  - `GS2CRefreshPageRedDot()`
  - `GS2CRefreshSeekHelpListRedDot()`
  - `GS2CRefreshStartCookDot(iShow=%s,iZongziID=%s)`

### `script\protocol\csgoodvoice.py` (entry3706)
- C2GS (12):
  - `C2GSAdvertise(iTarget=%s)`
  - `C2GSDeletePIC(sUrl=%s)`
  - `C2GSDeleteVoice(sUrl=%s)`
  - `C2GSGetPageInfo(lPid=%s)`
  - `C2GSGetSingerInfo(iTarget=%s)`
  - `C2GSJubao(iPID=%s,iReason=%s,sContent=%s,sPicArgs=%s,sVoiceArgs=%s,sAudioUrl=%s)`
  - `C2GSOpenFlowerRecord(iPID=%s)`
  - `C2GSOpenSendFlower(iTarget=%s)`
  - `C2GSSendFlower(iPID=%s,iNum=%s)`
  - `C2GSSetShowPIC(sUrl=%s)`
  - `C2GSUploadVoice(sUrl=%s,iDur=%s,sName=%s)`
  - `C2GSVote(iPID=%s)`
- GS2C (7):
  - `GS2CAllSingerIDList(lPid=%s)`
  - `GS2CAllSingerInfo(lInfo=%s)`
  - `GS2COpenFlowerRecord(dRecord=%s)`
  - `GS2COpenRegisterUI()`
  - `GS2COpenSendFlower(iPID=%s,iNum=%s)`
  - `GS2COtherPersonInfo(?)`
  - `GS2CPersonalInfo(iNo=%s,iFame=%s,lInfo=%s)`

### `script\protocol\csgopenguin.py` (entry1169)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 7, 8]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
- C2GS (8):
  - `C2GSConfirmPetDye(iId=%s,lDye=%s)`
  - `C2GSConfirmVato(iIdx=%s,iId=%s,iVoteNum=%s,iAdd=%s)`
  - `C2GSOpenVatoDlg(iIdx=%s,iId=%s)`
  - `C2GSRequestMinMapNpcPos()`
  - `C2GSRequestPetDyeData()`
  - `C2GSRequestSituationData(iIdx=%s)`
  - `C2GSRequestTodayNewsData()`
  - `C2GSShoot(iAttackId=%s,iMode=%s,iItemID=%s)`
- GS2C (11):
  - `GS2CGoPengGuinState(iState=%s)`
  - `GS2CMiniMapNpcPos(iNpcId=%s,iScence=%s,iX=%s,iY=%s,iShape=%s,iName=%s)`
  - `GS2CNpcDoEvent(iNpcID=%s,iEvent=%s,iEndX=%s,iEndY=%s)`
  - `GS2CNpcMove(iNpcID=%s,iStartX=%s,iStartY=%s,iDistX=%s,iDistY=%s,iSpeed=%s)`
  - `GS2COpenSituation(iShow=%s,iType=%s)`
  - `GS2COpenVatoDlg(iCurIdx=%s,iId=%s,sName=%s,iVote=%s,iCurVote=%s,iUseVote=%s)`
  - `GS2CPlayerLoginSys(iState=%s)`
  - `GS2CRequestPetDyeData(lPetData=%s)`
  - `GS2CShoot(iOwnerId=%s,iTargetId=%s,iMode=%s,iShape=%s)`
  - `GS2CSituationData(iCurIdx=%s,iCurVote=%s,iUnFinalVote=%s,iCurScore=%s,lPetData=%s,iNowIdx=%s)`
  - `GS2CTodayNewsData(iCurIdx=%s,dTodayNewsData=%s)`

### `script\protocol\csheartychocolate.py` (entry3137)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (3):
  - `C2GSGiveRecordAddFriendLog(iAddPlayerID=%s)`
  - `C2GSOpenGiftRecord()`
  - `C2GSOpenMainUI()`
- GS2C (2):
  - `GS2COpenGiftRecord(lstRecord=%s)`
  - `GS2COpenMainUI(sTitle=%s,iTitleColor=%s,iExpire=%s,iPoint=%s,lstMaleGiveInfo=%s)`

### `script\protocol\cshelppresent.py` (entry4812)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (2):
  - `C2GSBegin()`
  - `C2GSOpenView()`
- GS2C (2):
  - `GS2CCJData(iTimes=%s,iRechargeTimes=%s)`
  - `GS2CRedDot(iRedDot=%s)`

### `script\protocol\cshuajing.py` (entry2796)
- opcode `C2GS_PERFORM=0x42` iSub=[1, 2, 3, 4]
- opcode `GS2C_BLOCK=0x4d` iSub=[1, 2, 3]
- C2GS (4):
  - `C2GSAskShowHuaJing()`
  - `C2GSGetAllSkill()`
  - `C2GSGetItfInfo()`
  - `C2GSLearnSkill(iSkill=%s)`
- GS2C (2):
  - `GS2CRefreshItfInfo(iServerJJ=%s,iJJGrade=%s,iPoint=%s,iOpenTime=%s)`
  - `GS2CShowHuaJing(iShow=%s)`

### `script\protocol\csidauction.py` (entry1727)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 7]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3]
- C2GS (7):
  - `C2GSAskForNextAuction()`
  - `C2GSBid(iItemID=%s,iPrice=%s)`
  - `C2GSCloseDlg()`
  - `C2GSModifyAutoBid(iItemID=%s,iMultiAdd=%s,iMaxPrice=%s)`
  - `C2GSOpenAucDlg()`
  - `C2GSSetAutoBid(iItemID=%s,iMultiAdd=%s,iMaxPrice=%s)`
  - `C2GSSetRemind(iItemID=%s,iIsRemind=%s)`
- GS2C (3):
  - `GS2COpenCurAuction(lstGoods=%s)`
  - `GS2CRefreshNextAuction(lstGoods=%s)`
  - `GS2CUpdateCurAuction(lstGoods=%s)`

### `script\protocol\csladderrankallstar.py` (entry2865)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 100, 101, 102, 103, 104, 105, 106, 107]
- C2GS (16):
  - `C2GSAllRankInfo(iTeamType=%s)`
  - `C2GSAllTeamType(iTeamType=%s)`
  - `C2GSCloseZhuwei()`
  - `C2GSCreateTeam(sTeamName=%s)`
  - `C2GSGuessBuyItem(iItem=%s,iAmount=%s)`
  - `C2GSGuessChampion(iGroup=%s,iTeamID=%s)`
  - `C2GSGuessGame(iGameID=%s,iTeamID=%s,iCoin=%s)`
  - `C2GSGuessTips(iTeamID=%s,iServerID=%s)`
  - `C2GSMyGuessUI()`
  - `C2GSOpenChampionGuessUI(iGroup=%s)`
  - `C2GSOpenFirstGuess()`
  - `C2GSOpenGuessUI(iGroup=%s)`
  - `C2GSOpenShop()`
  - `C2GSTeamInfo(iTeamState=%s,iTeamId=%s)`
  - `C2GSWatchViedo(iTeamType=%s,iMatchType=%s,iTeamId=%s)`
  - `C2GSZhuwei(iTeamID=%s,iGameID=%s)`
- GS2C (16):
  - `GS2CAllRankInfo(iTeamType=%s,dAllRankInfo=%s)`
  - `GS2CCloseMatchUI()`
  - `GS2CGuessShopItem(lstItem=%s,iScore=%s)`
  - `GS2CGuessTips(iTeamID=%s,iServerID=%s,sTeamName=%s,sLeaderName=%s,lstMemberInfo=%s)`
  - `GS2COpenAllTeam(iTeamType=%s,iMyTeamId=%s,sMyName=%s,iMyServerId=%s,iMyDanRank=%s,iMyWinPoint=%s,lstAllTeamInfo=%s)`
  - `GS2COpenCDPanel(iBattleOfIdx=%s,iTimer=%s)`
  - `GS2COpenChampionGuessUI(iGroup=%s,lstTeam=%s)`
  - `GS2COpenCreatTeamUI(iTeamType=%s,bShow=%s)`
  - `GS2COpenGuessUI(iGroup=%s,lstGuess=%s)`
  - `GS2COpenMatchScheduleUI()`
  - `GS2COpenTeamMemberUI(iTeamState=%s,iTeamId=%s,sTeamName=%s,lstMemberInfo=%s)`
  - `GS2COpenompetitionRewardUI()`
  - `GS2CRefreshCoin(iCoin=%s)`
  - `GS2CRefreshScore(iScore=%s)`
  - `GS2CSendMyGuessList(lstGuess=%s)`
  - `GS2CZhuWeiInfo(?)`

### `script\protocol\csmizong.py` (entry3493)
- opcode `C2GS_HUODONG=0xcd` iSub=[1]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (1):
  - `C2GSMizongFight(iCurStage=%s)`
- GS2C (1):
  - `GS2COpenTrack(iCurStage=%s)`

### `script\protocol\csmotherday.py` (entry4071)
- C2GS (2):
  - `C2GSGetReward()`
  - `C2GSOpenLetter()`
- GS2C (2):
  - `GS2COpenLetterCover()`
  - `GS2COpenLetterDlg(iRewardState=%s,sChildName=%s,iRewardLst=%s)`

### `script\protocol\csmxkitchen.py` (entry970)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- C2GS (3):
  - `C2GSChangeNoviceSign(iState=%s)`
  - `C2GSClickNpc(iMid=%s)`
  - `C2GSLeaveScene()`
- GS2C (10):
  - `GS2CAddNpc(lstFurniture=%s)`
  - `GS2CChangeNpcGoods(iMid=%s,iType=%s,iStatus=%s,lstGood=%s)`
  - `GS2CHuodongState(iState=%s)`
  - `GS2COpenCookInfoDlg(iOpen=%s)`
  - `GS2COpenCookShareDlg(iScoce=%s)`
  - `GS2COpenNoviceDlg(iState=%s)`
  - `GS2CRefreshOrderInfo(iCurrManege=%s,iIdx=%s,dCookItem=%s)`
  - `GS2CRefreshTeamInfo(iMaxManege=%s,iResidueTime=%s,iHighMaxManege=%s)`
  - `GS2CRemoveNpc(iMid=%s)`
  - `GS2CShowPorgress(iMid=%s,iType=%s,iStatus=%s,iRemainSec=%s,iSec=%s,iPlayerID=%s)`

### `script\protocol\csnewmyq.py` (entry111)
- opcode `C2GS_FRDZONE=0xe9` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- opcode `GS2C_FRDZONE=0xef` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
- C2GS (10):
  - `C2GSAddShow(sText=%s,sPics=%s,sVoice=%s,sLocation=%s,sAddress=%s,iVerify=%s,lstPid=%s)`
  - `C2GSCheckRelation(iTarget=%s)`
  - `C2GSClearRedPoint(sGuid=%s)`
  - `C2GSComment(iTarget=%s,iOwner=%s,sGuid=%s,sCommentGuid=%s,sText=%s,sVoice=%s,lstPid=%s)`
  - `C2GSDelComment(iOwner=%s,sGuid=%s,sComGuid=%s,sText=%s,lstPid=%s)`
  - `C2GSDelShow(sGuid=%s,lstPid=%s)`
  - `C2GSFrdZonePage(iPageIndex=%s,iPageSize=%s,iTarget=%s,sT1=%s,sT2=%s,iShowFriend=%s,iShowOrg=%s)`
  - `C2GSGetOneShow(sGuid=%s)`
  - `C2GSMessagePage(iPageSize=%s,sT1=%s,sT2=%s,iIsShowOrg=%s)`
  - `C2GSPro(iTarget=%s,iCancel=%s,sGuid=%s)`
- GS2C (16):
  - `GS2CAddOneShow(sIP=%s,dData=%s)`
  - `GS2CAddShow(dData=%s)`
  - `GS2CComment(iOwner=%s,iDel=%s,dData=%s)`
  - `GS2CCommentChange(iOwner=%s,sGuid=%s,iDel=%s,dData=%s)`
  - `GS2CDelShow(sGuid=%s)`
  - `GS2CFrdZonePage(sIP=%s,dData=%s)`
  - `GS2CInitFrdNew(dData=%s)`
  - `GS2CMessagePage(sIP=%s,dData=%s)`
  - `GS2CNoticeShare(iType=%s,iShape=%s,sName=%s,iNum=%s)`
  - `GS2CPro(iOwner=%s,iCancel=%s,sGuid=%s)`
  - `GS2CProChange(iOwner=%s,sGuid=%s,dData=%s)`
  - `GS2CRefreshFrdNew(dData=%s)`
  - `GS2CRelation(iTarget=%s,iRelation=%s)`
  - `GS2CScreenShot()`
  - `GS2CScreenShotEnd()`
  - `GS2CWeituoInfo(iPublishID=%s,sText=%s)`

### `script\protocol\csnewyearjifu.py` (entry2328)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (3):
  - `C2GSDrawReward()`
  - `C2GSGetDailogData()`
  - `C2GSGetReward(iRewardID=%s)`
- GS2C (2):
  - `GS2CDialogData(?)`
  - `GS2CRedDot(iRedDot=%s)`

### `script\protocol\csnewyearwish.py` (entry4637)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8]
- C2GS (10):
  - `C2GSChangePriv(iPriv=%s)`
  - `C2GSGetGoodAmount(iPlayerID=%s)`
  - `C2GSGetShareInfo()`
  - `C2GSGiveGood(iPlayerID=%s,iGiveFlag=%s)`
  - `C2GSMakeWish(iPriv=%s,sWish=%s)`
  - `C2GSOpenWishCard(iPlayerID=%s)`
  - `C2GSOpenWishUI()`
  - `C2GSRefreshShowUI()`
  - `C2GSSetShareInfo(lstInfo=%s)`
  - `C2GSShareWish(iPlayerID=%s)`
- GS2C (8):
  - `GS2CMakeWishUI()`
  - `GS2COpenAwardUI(lstHeroInfo=%s)`
  - `GS2COpenOtherWishUI(iPlayerID=%s,sName=%s,lstPhoto=%s,iGoodAmount=%s,bIsGood=%s,sWish=%s,iFrm=%s)`
  - `GS2COpenShowUI(PlayerInfoLst=%s)`
  - `GS2CRefreshAmount(iPlayerID=%s,iAmount=%s,iIsGood=%s)`
  - `GS2CShareInfo(lstFreindInfo=%s)`
  - `GS2CWishState(iWish=%s)`
  - `GS2CWishUI(iPriv=%s,sWish=%s,iGoodAmount=%s)`

### `script\protocol\csonlinelottery.py` (entry3993)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3]
- C2GS (3):
  - `C2GSGetDialogInfo()`
  - `C2GSGetPlayerListInfo(iDay=%s,iPrize=%s)`
  - `C2GSLeaveDialog()`
- GS2C (2):
  - `GS2CLotteryInfo(?)`
  - `GS2CPlayerListInfo(lAvatarInfoList=%s)`

### `script\protocol\cspintusecret.py` (entry2347)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (3):
  - `C2GSGetReward(iRewardPos=%s,iPage=%s)`
  - `C2GSOpenPage(iPage=%s)`
  - `C2GSUsePuzzle(iPos=%s,iPage=%s)`
- GS2C (2):
  - `GS2COpenPuzzle()`
  - `GS2CPageInfo(iPage=%s,iLeft=%s,lstPuzzle=%s,dRewardInfo=%s)`

### `script\protocol\csplayergrow.py` (entry101)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5]
- C2GS (3):
  - `C2GSAskChapterInfo(?)`
  - `C2GSGetChapterReward(?)`
  - `C2GSNewestChapter(?)`
- GS2C (5):
  - `GS2CCanRewardChapter(?)`
  - `GS2CChapterRewardState(?)`
  - `GS2CRefreshChapterInfo(?)`
  - `GS2CTaskDone(?)`
  - `GS2CUnreadChapter(?)`

### `script\protocol\csplayselection.py` (entry4317)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3]
- C2GS (2):
  - `C2GSGetResultByPage(iPage=%s)`
  - `C2GSSendAllSelection(dAllSelect=%s)`
- GS2C (3):
  - `GS2COpenUI(iUI=%s)`
  - `GS2CPageInfo(iPage=%s,dPageInfo=%s)`
  - `GS2CPlayerSelect(dPlayerSelect=%s)`

### `script\protocol\csprerole.py` (entry3805)
- opcode `C2GS_PRE_ROLE=0xeb` iSub=[1, 2]
- opcode `GS2C_PRE_ROLE=0xf0` iSub=[1, 2, 3, 4, 5]
- C2GS (2):
  - `C2GSBindPayMember(iSelectID=%s)`
  - `C2GSOpenPrePay()`
- GS2C (5):
  - `GS2CBindSuccess(iBindMember=%s)`
  - `GS2CClosePayUI()`
  - `GS2CPrePayInfo(iBindFlag=%s,iBindMember=%s,iPrePayFlag=%s)`
  - `GS2CPrePaySuccess(iPrePayFlag=%s)`
  - `GS2CSendAllCharge(iChargeGold=%s)`

### `script\protocol\csqingming.py` (entry4117)
- C2GS (2):
  - `C2GSQingmingAnswer(iQuestionIdx=%s,iSelectIdx=%s)`
  - `C2GSStopAnswer()`
- GS2C (3):
  - `GS2CRefreshAnswer(iTrueAnswer=%s)`
  - `GS2CRefreshTrueAmount(iTrueAmount=%s)`
  - `GS2CShowQuestionDlg(iIndex=%s,iQuestionID=%s,iTrueAmount=%s,sQuestion=%s,iEndTime=%s,lstAnswer=%s)`

### `script\protocol\csqixi.py` (entry3450)
- C2GS (14):
  - `C2GSCancelBindFriend()`
  - `C2GSChangeFriend(iCurFriend=%s)`
  - `C2GSChangeLabel(lstLabel=%s)`
  - `C2GSChooseLabel(lstLabel=%s)`
  - `C2GSRequestBindFriend(iFriendID=%s)`
  - `C2GSRequestFriendList()`
  - `C2GSRequestQixiTask()`
  - `C2GSRequestTest()`
  - `C2GSRequestTestResult()`
  - `C2GSRollLottery()`
  - `C2GSSendRestTime(iSeconds=%s)`
  - `C2GSSendTaskComplete()`
  - `C2GSStartChat(iTarget=%s,iFlag=%s)`
  - `C2GSWorldFindFriend()`
- GS2C (9):
  - `GS2COpenQiXiDlg(iPage=%s)`
  - `GS2CSendLabel(lstLabel=%s)`
  - `GS2CShowRestTime(iSeconds=%s)`
  - `GS2CUpdateFriendList(iFriendLst=%s)`
  - `GS2CUpdateMatchState(iMatchState=%s)`
  - `GS2CUpdateOneTask(sTaskName=%s,iCurProgress=%s,iMaxProgress=%s,sDifficulty=%s)`
  - `GS2CUpdateQixiTask(iFriendID=%s,sFriendName=%s,iSimScore=%s,iMidScore=%s,iDiffScore=%s,iTaskLst=%s)`
  - `GS2CUpdateRestTask(iHasRestTask=%s)`
  - `GS2CUpdateTestResult(iPlayerID=%s,iTestPoint=%s,sPlayerName=%s,iCurFriend=%s,lstLabel=%s)`

### `script\protocol\csracing.py` (entry3114)
- C2GS (14):
  - `C2GSBarrierCatchHero(iBarrierID=%s,iBarrierType=%s)`
  - `C2GSBoxGameClick(iBoxIndex=%s)`
  - `C2GSClickDance()`
  - `C2GSClickQuestion(iAnswerID=%s)`
  - `C2GSClosePhraseDialog()`
  - `C2GSCtrlNpcMove(lstPoint=%s)`
  - `C2GSPhraseAnswer(lstChar=%s)`
  - `C2GSPlayerEnterCircle(iBarrierID=%s,iBarrierType=%s,iMove=%s)`
  - `C2GSPushStone(iID=%s)`
  - `C2GSRewarBoxClick(iRewarBox=%s)`
  - `C2GSTuLangChoose(iChoose=%s)`
  - `C2GSUseItem(iItemID=%s)`
  - `C2GSUseProp(iItemID=%s)`
  - `C2GSUsePropOnRole(iItemID=%s,iID=%s)`
- GS2C (27):
  - `GS2CAddBarrierShip(iID=%s,iBarrierType=%s,iSceneID=%s,iGroupID=%s)`
  - `GS2CAddBuff(iBuff=%s,iTime=%s)`
  - `GS2CClearBarrier(iID=%s)`
  - `GS2CCreateRoleEffect(iID=%s,iAddonID=%s)`
  - `GS2CDelBarrierShip(iID=%s,iBarrierType=%s,iSceneID=%s,iGroupID=%s)`
  - `GS2CDelBuff(iBuff=%s)`
  - `GS2CHuodongState(iState=%s)`
  - `GS2CIsLevelRewardSucc(iLevel=%s,iSucc=%s)`
  - `GS2CNpcChangeState(iID=%s,iEmote=%s)`
  - `GS2COpenDanceDlg()`
  - `GS2COpenQuesDlg(sTitle=%s,lstAnswer=%s)`
  - `GS2COpenTuLangQA(sQuestion=%s,lstAnswer=%s)`
  - `GS2CPhraseGame(iPhraseID=%s)`
  - `GS2CPlayEffect(iID=%s,iEffectID=%s,iTimes=%s,iInterval=%s)`
  - `GS2CPlayEffectWithRole(iID=%s,iEffectID=%s)`
  - `GS2CRoseNum(iNum=%s)`
  - `GS2CSceneFixID(iSceneID=%s,iFixID=%s)`
  - `GS2CSetCtrlNpc(iNpcID=%s)`
  - `GS2CSetCtrlNpc2(iNpcID=%s)`
  - `GS2CStartBoxGame(lstItem=%s)`
  - `GS2CStoneProgress(?)`
  - `GS2CSyncSpeed(iID=%s,iSpeed=%s)`
  - `GS2CTuLangAnswer(iChoose=%s,iRight=%s)`
  - `GS2CUpdateAimTask(lstAimTask=%s)`
  - `GS2CUpdateBuff(lstBuff=%s)`
  - `GS2CUpdateItemInfo(lstItem=%s)`
  - `GS2CUpdateSelfBarriers(lstBarrier=%s)`

### `script\protocol\csrichman.py` (entry4822)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (2):
  - `C2GSCheckMatch(iMacth=%s)`
  - `C2GSLeaveGame()`
- GS2C (2):
  - `GS2CShowMatchMiniDlg(iState=%s)`
  - `GS2CShowOnlineNum(iNum=%s)`

### `script\protocol\csrookieback.py` (entry3173)
- C2GS (9):
  - `C2GSAddSuperReward(iType=%s,iSelect=%s)`
  - `C2GSBuyPayLB(iType=%s)`
  - `C2GSChickHuoyueReward(iLevel=%s)`
  - `C2GSClickLuckDraw(iType=%s)`
  - `C2GSClickXinxiuChuanGon()`
  - `C2GSGetShouChongReward()`
  - `C2GSOpenMainDlg()`
  - `C2GSOpenWishDlg()`
  - `C2GSRewardTask(iTask=%s)`
- GS2C (5):
  - `GS2CAddReddot(iWishNum=%s,iWishReward=%s,iTask=%s,iVipReward=%s)`
  - `GS2CAddSuperReward(iType=%s,iFlag=%s)`
  - `GS2CLuckDraw(iType=%s,idx=%s,iLevel=%s)`
  - `GS2COpenMainDlg(iTime=%s,iUsedCnt=%s,iAllCGCnt=%s,iShouChong=%s,iExpAddRatio=%s,iRewardProcessLB=%s,dTaskInfo=%s)`
  - `GS2COpenWishDlg(dReward=%s,iTotalChance=%s,iHuoyue=%s)`

### `script\protocol\cssameheartplant.py` (entry2049)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (5):
  - `C2GSClickReward(iPos=%s)`
  - `C2GSOpenPage()`
  - `C2GSPlantFriend()`
  - `C2GSSayHello(iType=%s,iTarget=%s)`
  - `C2GSUseWater()`
- GS2C (2):
  - `GS2CGameState(iGameState=%s)`
  - `GS2COpenPlantDlg(iWaterNum=%s,PlayerInfoLst=%s,TaskInfolst=%s,dReward=%s,iProcess=%s)`

### `script\protocol\csseamail.py` (entry1866)
- C2GS (26):
  - `C2GSAddSuperReward(iType=%s,iSelect=%s)`
  - `C2GSAllAgreed()`
  - `C2GSAllApply(iPage=%s)`
  - `C2GSAllJoin(iPage=%s)`
  - `C2GSApplyTeam(iTarget=%s)`
  - `C2GSBindHelpPlayer()`
  - `C2GSBuyHight()`
  - `C2GSChickHuoyueReward(iLevel=%s)`
  - `C2GSClickLuckDraw(iType=%s)`
  - `C2GSConsentTeam(iTarget=%s)`
  - `C2GSFriendApply(iTarget=%s)`
  - `C2GSGetHelpGift(iGiftIdx=%s)`
  - `C2GSGetReturnGift()`
  - `C2GSJKDrawReward()`
  - `C2GSJKGetDailogData()`
  - `C2GSJKGetReward(iRewardID=%s)`
  - `C2GSOpenBottle(iItem=%s,iTarget=%s,iNotify=%s)`
  - `C2GSOpenDlgAsk(iType=%s,iAnwser=%s)`
  - `C2GSOpenHelpDlg(iType=%s)`
  - `C2GSOpenQiRiDlg()`
  - `C2GSOpenWishDlg()`
  - `C2GSReturnMainDlg()`
  - `C2GSShareAndRecruit()`
  - `C2GSSign(iDay=%s)`
  - `C2GSTeamPage()`
  - `C2GSWorldRecruit()`
- GS2C (18):
  - `GS2CAddSuperReward(iType=%s,iFlag=%s)`
  - `GS2CCloseCombackDlg()`
  - `GS2CJKDialogData(?)`
  - `GS2CJKRedDot(iRedDot=%s)`
  - `GS2CLuckDraw(iType=%s,idx=%s,iLevel=%s)`
  - `GS2COpenAskDlg(iType=%s)`
  - `GS2COpenCombackDlg()`
  - `GS2COpenHelpDlg(iType=%s,iState=%s)`
  - `GS2COpenMailDlg(iItem=%s,dFrdState=%s)`
  - `GS2COpenReturnRecruit(bShow=%s)`
  - `GS2COpenShareDlg(lstPlayers=%s,lstTask=%s)`
  - `GS2COpenWishDlg(dReward=%s,iTotalChance=%s,iHuoyue=%s)`
  - `GS2CReturnMainDlg(bHasReturnHelp=%s)`
  - `GS2CSendAllJoin(dInfo=%s)`
  - `GS2CSendInfoHelpDlg(?)`
  - `GS2CSendSignInfo(iDay=%s,iBuyHight=%s,dSign=%s)`
  - `GS2CSendTeamPage(iPage=%s,iNext=%s,dInfo=%s)`
  - `GS2CSignFlash()`

### `script\protocol\csservercombine.py` (entry3749)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (4):
  - `C2GSGetShopDetail(?)`
  - `C2GSOperationBuyExp(?)`
  - `C2GSOperationShop(?)`
  - `C2GSOperationSpeedUp(?)`
- GS2C (1):
  - `GS2CGetShopDetail(?)`

### `script\protocol\cssevendaybonus.py` (entry3849)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- C2GS (3):
  - `C2GSCheckBonus(iTimes=%s)`
  - `C2GSCloseDlg()`
  - `C2GSOpenDlg()`
- GS2C (2):
  - `GS2CInfo(iCheckInDay=%s,iBonusDay=%s,iPoints=%s,iBonusStatus=%s)`
  - `GS2CPlayerInfo(lstPlayer=%s)`

### `script\protocol\cssevendaytarget.py` (entry1079)
- C2GS (3):
  - `C2GSOpenDialog()`
  - `C2GSRewarTask(iTask=%s)`
  - `C2GSRewardDayTask(iDay=%s)`
- GS2C (4):
  - `GS2CRefOneDayReward(iDay=%s,iReward=%s,iDayExtReward=%s)`
  - `GS2CRefOneObject(iTask=%s,iDoneNum=%s,iMaxNum=%s,iButtonStat=%s,iExtItemState=%s)`
  - `GS2CSendAllInfo(dAllDayInfo=%s,iToday=%s,iAllReward=%s,iExtAllReward=%s,iRechargeType=%s,iOverTime=%s)`
  - `GS2CUnlockSucceed()`

### `script\protocol\csspringfestivalblessing.py` (entry2612)
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3]
- C2GS (2):
  - `C2GSOpenBlessingDlg()`
  - `C2GSSendBlessing(sWish=%s)`
- GS2C (3):
  - `GS2CCloseBlessingDlg()`
  - `GS2COpenBlessingDlg()`
  - `GS2COpenBlessingMainDlg(PlayerInfoLst=%s)`

### `script\protocol\cssummersignin2021.py` (entry2433)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1]
- C2GS (3):
  - `C2GSClickSGSignIn(iType=%s)`
  - `C2GSClickSignIn(iType=%s,iDayPos=%s)`
  - `C2GSOpenDlg()`
- GS2C (1):
  - `GS2COpenDlgInfo(iType=%s,DictSignInReward=%s,DictSignNumReward=%s)`

### `script\protocol\cssummervacation.py` (entry4434)
- C2GS (2):
  - `C2GSGetSummerVacationInfo()`
  - `C2GSSignSummerVacation(iDay=%s)`
- GS2C (2):
  - `GS2CRefreshSummerVacationInfo(iCurDay=%s,dDayAwardt=%s,iSignNum=%s)`
  - `GS2CSignRefresh(iDay=%s,iState=%s,iSignNum=%s)`

### `script\protocol\cssumwashbaodi.py` (entry4221)
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2]
- GS2C (2):
  - `GS2CRefreshData(iColorWashCnt=%s,iTriggerTime=%s)`
  - `GS2CRefreshHDState(iOpen=%s)`

### `script\protocol\cstaofaboss.py` (entry4284)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7]
- C2GS (2):
  - `C2GSLottery(iType=%s)`
  - `C2GSOpenProcess()`
- GS2C (7):
  - `GS2CCloseHpDlg()`
  - `GS2CCloseLotteryDlg()`
  - `GS2CCloseProcessDlg()`
  - `GS2COpenProcessDlg(iBossHp=%s,iFirstLottery=%s,iSeceondLottery=%s,iCanGetFirstLottery=%s,iCanGetSecondLottery=%s)`
  - `GS2CRefreshHp(iBossHp=%s)`
  - `GS2CRefreshProcessDlg(iFirstLottery=%s,iSeceondLottery=%s,iCanGetFirstLottery=%s,iCanGetSecondLottery=%s)`
  - `GS2CShowRedPot(iShowRedPot=%s)`

### `script\protocol\cstimecapsule.py` (entry4682)
- C2GS (2):
  - `C2GSOpenReceiveCapsule(iPlayerID=%s,iItemID=%s)`
  - `C2GSSendTimeCapsule(iItemID=%s,iPlayerID=%s,sMsg=%s)`
- GS2C (2):
  - `GS2COpenReceiveTimeCapsuleDlg(iItemID=%s,iOwnerID=%s,sMsg=%s)`
  - `GS2COpenSendTimeCapsuleDlg(iItemID=%s,iItemShape=%s)`

### `script\protocol\cstrainpet.py` (entry4738)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 3, 4, 5, 6, 7]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 3, 4, 5, 6, 7]
- C2GS (6):
  - `C2GSAddGen(iSummon=%s,lstAttr=%s)`
  - `C2GSOpenTrainDlg(iOpenPage=%s,iSummon=%s)`
  - `C2GSRequestFumoRange(iSummon=%s)`
  - `C2GSSelectFumo(iSummon=%s,iFumoType=%s)`
  - `C2GSSelectSummon(iSummType=%s)`
  - `C2GSShengLing(iSummon=%s)`
- GS2C (6):
  - `GS2CAddGenSuccess(iAddZiZhiNum=%s,iResetPoint=%s)`
  - `GS2CCloseSelectUI()`
  - `GS2COpenTrainPetDlg(iShenglingNum=%s,iAddZiZhiNum=%s,iOpenPage=%s,iPresentYuLingNum=%s,iResetPoint=%s,lstAttr=%s)`
  - `GS2CPreviewSummon(dSummonInfo=%s)`
  - `GS2CShengLingSuccess(iShengLingNum=%s,iAddSkill=%s)`
  - `GS2CUpdateFumoRange(iSummonID=%s,iCommonMin=%s,iCommonMax=%s,iAttackMin=%s,iAttackMax=%s)`

### `script\protocol\csuniquedevice.py` (entry677)
- opcode `C2GS_UNIQUE_DEVICE=0xe3` iSub=[2]
- opcode `DEVICE=0xe3` iSub=[1]
- opcode `GS2C_UNIQUE_DEVICE=0xe7` iSub=[1]
- C2GS (2):
  - `C2GSUploadDevice(sToken=%s,sID=%s)`
  - `C2GSUploadDeviceDict(sDeviceCode=%s)`
- GS2C (1):
  - `GS2CSta][z_C@NKkJYFLJ(?)`

### `script\protocol\csvoicecard.py` (entry3280)
- C2GS (5):
  - `C2GSDeleteAudio(iPid=%s,sVoiceUrl=%s)`
  - `C2GSJuBao(iTarget=%s,iReason=%s,sContent=%s,sAudioUrl=%s,sArgs=%s)`
  - `C2GSOpenUI(iTarget=%s)`
  - `C2GSRequestAudioExist(iType=%s,iTarget=%s,sAudioUrl=%s)`
  - `C2GSUploadAudioSucc(iPid=%s,sVoiceUrl=%s)`
- GS2C (3):
  - `GS2COpenUI(iTarget=%s,sName=%s,iLeftChance=%s,iHaveVoice=%s,iVoiceState=%s,sVoiceUrl=%s)`
  - `GS2CRequestAudioResult(iType=%s,iResult=%s)`
  - `GS2CUploadCheckResult(iResult=%s)`

### `script\protocol\csyardmatch.py` (entry2760)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 4, 5, 6, 7, 8, 9, 10]
- C2GS (12):
  - `C2GSApply(sUrl=%s)`
  - `C2GSCloseApplyDlg(iType=%s)`
  - `C2GSFollow(iID=%s,iType=%s)`
  - `C2GSGetEntriesList(iType=%s)`
  - `C2GSGetMyEntriesData()`
  - `C2GSGetPlayerCardData(iID=%s)`
  - `C2GSGetYardSnapShot(iType=%s)`
  - `C2GSOpenYardMatchMainDLg()`
  - `C2GSPublicize(iID=%s)`
  - `C2GSSaveAndUpload(sUrl=%s)`
  - `C2GSSearchEntries(iID=%s)`
  - `C2GSVote(iID=%s)`
- GS2C (10):
  - `GS2COpenMyEntriesDlg(?)`
  - `GS2COpenPlayerCard(?)`
  - `GS2CRefreshApplyState(iApplyState=%s)`
  - `GS2CRefreshEntriesList(iFilterType=%s,lEntries=%s,iMyTicket=%s,iStep=%s,iEndTime=%s)`
  - `GS2CRefreshFollowState(iID=%s,iFollow=%s)`
  - `GS2CRefreshModifyTime(iNum=%s)`
  - `GS2CRefreshMyTicket(iNum=%s)`
  - `GS2CRefreshStepInfo(iStep=%s,iEndTime=%s)`
  - `GS2CRefreshTicketByID(iTicket=%s,iID=%s)`
  - `GS2CRefreshYardData(?)`

### `script\protocol\csyearback.py` (entry3251)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3, 4, 5, 6, 7, 8]
- C2GS (17):
  - `C2GSClickChangeShengXiao()`
  - `C2GSClickIButtonSay(iID=%s)`
  - `C2GSCombineID(iID=%s)`
  - `C2GSGetLastTime()`
  - `C2GSGetPlayItem(iItemIndex=%s)`
  - `C2GSGetReward(iReward=%s)`
  - `C2GSGetShengXiaoRewardItem(iId=%s)`
  - `C2GSGetShengxiao()`
  - `C2GSOpenCombineDlg()`
  - `C2GSOpenFriendDlg()`
  - `C2GSOpenPlayDlg()`
  - `C2GSOpenShengXiaoDlg()`
  - `C2GSRealItemInfo(iItemID=%s,sName=%s,sID=%s,sPhone=%s,sAddress=%s)`
  - `C2GSRemoveCombineID(iID=%s)`
  - `C2GSShowShengxiaoRule()`
  - `C2GSShowShengxiaoTitle()`
  - `C2GSShowTodayIMPoint(iID=%s)`
- GS2C (8):
  - `GS2CCombineList(lstGetReward=%s,iMaxPoint=%s,lstCombine=%s)`
  - `GS2CFriendCombineList(iBack=%s,lstInfo=%s)`
  - `GS2COpenCombineDlg()`
  - `GS2COpenRealItemDlg(iItemID=%s,sName=%s)`
  - `GS2COpenShengxiaoDlg(?)`
  - `GS2CRefreshLastTime(iLastTime=%s)`
  - `GS2CRefreshPlayData(iAllScore=%s,iSelfScore=%s,lstItem=%s)`
  - `GS2CShowShengXiaoRedDot()`

### `script\protocol\csyearsum.py` (entry3627)
- opcode `C2GS_HUODONG=0xcd` iSub=[1, 2, 3]
- opcode `GS2C_HUODONG_OP=0xce` iSub=[1, 2, 3]
- C2GS (3):
  - `C2GSAskInfo(iTarget=%s,iOpenType=%s)`
  - `C2GSDelComment(iKey=%s)`
  - `C2GSSendComment(iType=%s,iPlayerID=%s,sComment=%s)`
- GS2C (3):
  - `GS2CAddComment(iKey=%s,iPlayeriD=%s,sName=%s,sComment=%s,iTargetID=%s)`
  - `GS2CDelComment(iKey=%s)`
  - `GS2CRefreshInfo(?)`

### `script\protocol\csyearvoice.py` (entry2454)
- C2GS (16):
  - `C2GSAdvertise(iTarget=%s,iServer=%s,sUrl=%s)`
  - `C2GSAttention(iTarget=%s,iServer=%s,iAttention=%s)`
  - `C2GSDeleteVoice(sUrl=%s)`
  - `C2GSGetPageInfo(lPid=%s)`
  - `C2GSGetSingerInfo(iTarget=%s,iServer=%s)`
  - `C2GSJubao(iPID=%s,iServer=%s,iReason=%s,sContent=%s,sPicArgs=%s,sVoiceArgs=%s,sNameArgs=%s,sAudioUrl=%s)`
  - `C2GSOpenAllProInfo()`
  - `C2GSOpenFameRecord(iType=%s,iStart=%s,iCnt=%s,iNeedRank=%s)`
  - `C2GSOpenPersonalInfo()`
  - `C2GSOpenRegisterUI()`
  - `C2GSOpenSendFlower(iTarget=%s,iServer=%s,sUrl=%s)`
  - `C2GSSendFlower(iPID=%s,iServer=%s,iNum=%s,sUrl=%s)`
  - `C2GSSetShowPIC(sVoiceUrl=%s,sPicUrl=%s)`
  - `C2GSSetTop(sUrl=%s)`
  - `C2GSUploadVoice(sUrl=%s,iDur=%s,sName=%s,sPic=%s)`
  - `C2GSVote(iPID=%s,iServer=%s,sUrl=%s,iCnt=%s,iType=%s)`
- GS2C (14):
  - `GS2CAllSingerIDList(iStage=%s,iVote=%s,lPid=%s,lAttention=%s,iTarget=%s)`
  - `GS2CAllSingerInfo(iStage=%s,iIsApprove=%s,lInfo=%s)`
  - `GS2CFameRank(iStage=%s,lRank=%s)`
  - `GS2CFameRecord(lRecord=%s)`
  - `GS2COpenRegisterUI(iStage=%s,iIsApprove=%s)`
  - `GS2COpenSendFlower(iPID=%s,iNum=%s,sUrl=%s,iServer=%s)`
  - `GS2COpenSpecialVedio()`
  - `GS2COtherPersonInfo(?)`
  - `GS2CPersonalInfo(iStage=%s,iNo=%s,iFamer=%s,iVote=%s,lInfo=%s)`
  - `GS2CRefreshFame(iTotalFame=%s,sVoiceUrl=%s,iVoiceFame=%s)`
  - `GS2CRefreshSingerState(iSinger=%s)`
  - `GS2CRefreshTicket(iType=%s,iTicket=%s)`
  - `GS2CRefreshTopInfo(sUrl=%s,iTopTime=%s)`
  - `GS2CSetAttention(TnTSZXO %s,iAttention=%s,lstUrl=%s)`

### `script\protocol\openui\csopenui.py` (entry1596)
- opcode `C2GS_OPEN_UI_NEW=0xe6` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 29, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
- opcode `GS2C_OPEN_UI_NEW=0xe6` iSub=[7]
- opcode `GS2C_OPEN_UI_NEW=0xea` iSub=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
- C2GS (55):
  - `C2GSAppearanceAskFairyColor(iItemID=%s)`
  - `C2GSAppearanceAskWeaponColor(iItemID=%s)`
  - `C2GSAppearanceChgShape()`
  - `C2GSAppearanceChgShapeConfirm(iShape=%s,iPlayerMode=%s)`
  - `C2GSAppearanceCombineFairy(iItemID1=%s,iItemID2=%s)`
  - `C2GSAppearanceConfirmPTDye(iResult=%s,iType=%s,iFriendID=%s,sLog=%s)`
  - `C2GSAppearanceDelFreeDye(iType=%s,iPos=%s)`
  - `C2GSAppearanceDelTmpDye()`
  - `C2GSAppearanceFairyItemAct(iItemID=%s)`
  - `C2GSAppearanceFairyItemColor(iItemID=%s)`
  - `C2GSAppearanceFreeDye(lstHSV=%s,iType=%s,iID=%s,sLog=%s)`
  - `C2GSAppearanceGetOutFairy()`
  - `C2GSAppearanceHeroFairyAct()`
  - `C2GSAppearanceHeroFairyColor()`
  - `C2GSAppearanceHorseChangeCount()`
  - `C2GSAppearanceHorseColor(iType=%s,iHorseShape=%s)`
  - `C2GSAppearancePTDye()`
  - `C2GSAppearanceResetFairyColor(iFairyID=%s)`
  - `C2GSAppearanceResetHorseColor(iType=%s,iHorseShape=%s)`
  - `C2GSAppearanceResetWeaponColor(iItemID=%s)`
  - `C2GSAppearanceSaveFreeDye(iType=%s,iPos=%s,iShape=%s,lstHSV=%s)`
  - `C2GSAppearanceTGF()`
  - `C2GSAppearanceWeaponItemColor(iItemID=%s)`
  - `C2GSAskAllSpeEmoteInfo()`
  - `C2GSAskGiveItemPrice(iType=%s,iShape=%s)`
  - `C2GSAskTeamMarkInfo()`
  - `C2GSBuyBack(iType=%s,iShape=%s)`
  - `C2GSBuyFashion(iShape=%s,iType=%s)`
  - `C2GSBuyGift(iType=%s,iSubType=%s)`
  - `C2GSBuySpeEmote(iItemID=%s)`
  - `C2GSChangeFashionAttr(iAttrType=%s)`
  - `C2GSChangeShowPrettyID(iCanShowPrettyID=%s)`
  - `C2GSCommitMagicPal(iSkillID=%s,iCase=%s)`
  - `C2GSConfirmDye(iShape=%s,iSelect=%s)`
  - `C2GSConfirmExchangPay(iPlayerID=%s)`
  - `C2GSDyeBack(iShape=%s,iType=%s)`
  - `C2GSExChangeSuit(iItemID=%s,iType=%s)`
  - `C2GSGetOwnBack()`
  - `C2GSGetOwnFashion()`
  - `C2GSGiftFriend(iType=%s,iFriendID=%s,iShape=%s,iItemID=%s,iGiftNum=%s,iSendGroup=%s)`
  - `C2GSGiftState()`
  - `C2GSMagicPalPrice(iSkillID=%s,iCase=%s)`
  - `C2GSOpenAppearence()`
  - `C2GSOpenAttrView(iType=%s)`
  - `C2GSOpenFashionAttr()`
  - `C2GSOpenGiftDlgOther(iType=%s)`
  - `C2GSOpenGiftDlgWithDesc(iType=%s,iDesc=%s)`
  - `C2GSOpenGiftDlgWithHsv(iType=%s,lstHSV=%s)`
  - `C2GSOpenGiftDlgWithSpeEmote(iType=%s,iItemSID=%s)`
  - `C2GSQuickBuyFlower()`
  - `C2GSRideAllColor(iRideShape=%s,iRideType=%s,iRidePart=%s)`
  - `C2GSUnluckHorseFairy()`
  - `C2GSWeaponAllColor(iWeaponID=%s)`
  - `C2GSWearBack(iType=%s,iShape=%s)`
  - `C2GSWearFashion(iType=%s,iShape=%s)`
- GS2C (48):
  - `GS2CAddBack(iShape=%s,iColor=%s,iEndTime=%s)`
  - `GS2CAddFashion(iShape=%s,lstColor=%s,iEndTime=%s)`
  - `GS2CAllAttrShow(?)`
  - `GS2CAllHaveSpeEmote(dList=%s)`
  - `GS2CChangeAttr(iAttrType=%s)`
  - `GS2CChangeShapeUINew1(tShape=%s)`
  - `GS2CChangeShapeUINew2(lstbody=%s)`
  - `GS2CCloseColorUI()`
  - `GS2CColorUI(LstDesc=%s,dTime=%s,iColor1=%s,iColor2=%s,iColor3=%s)`
  - `GS2CColorUINew(lstDesc=%s,dColorTime=%s,iColor1=%s,iColor2=%s,iColor3=%s)`
  - `GS2CDelBack(iShape=%s)`
  - `GS2CDelFashion(iShape=%s)`
  - `GS2CDelTmpFreeColor(iTmpType=%s,iPos=%s)`
  - `GS2CDelTmpFreeColorNew(iTmpType=%s,iPos=%s)`
  - `GS2CDujieAttrShow(iUseNum=%s,iMaxNum=%s)`
  - `GS2CFashionNoticeShape(iType=%s,iShape=%s,sName=%s,iNum=%s)`
  - `GS2CFrdListMode(iType=%s,lstFrd=%s,iNeedSG=%s,iShape=%s,iItemID=%s)`
  - `GS2CFreeColorUI(iNeedHuancai=%s,iFirst=%s,iCostOff=%s,dTmpColor=%s)`
  - `GS2CFreeColorUINew(iNeedHuancai=%s,iFirst=%s,iCostOff=%s,dTmpColor=%s)`
  - `GS2CGiftState(lstState=%s)`
  - `GS2CImmortalAttrShow(iUseNum=%s,iMaxNum=%s)`
  - `GS2CItemAttrShow(iJiaozi=%s,iZongzi=%s,iYuebing=%s,iUseNum=%s,iMaxNum=%s)`
  - `GS2COpenChangeAttr(iAttrType=%s)`
  - `GS2COpenDyeDlg(iShape=%s,iColor1=%s,iColor2=%s)`
  - `GS2COpenExChangePayView(iPlayerID=%s,iShape=%s,iCost=%s,sName=%s,dDesc=%s)`
  - `GS2COpenFashionGift(iItemID=%s,iShape=%s,iFlag=%s,iType=%s)`
  - `GS2COpenPerformRanseUI(iPerform=%s)`
  - `GS2COpenSpeEmote(iType=%s)`
  - `GS2COpenYanZhiUI(iMainType=%s,iSubType=%s)`
  - `GS2COpenYanZhiUIAndSelect(iMainType=%s,dExtendData=%s)`
  - `GS2CPerfomColorCost(iSkillId=%s,iColorType=%s,iRyzyNum=%s,iChsNum=%s,iBanPal=%s)`
  - `GS2CRefreshOneBack(iShape=%s,iColor=%s,iEndTime=%s)`
  - `GS2CRefreshOneFashion(iShape=%s,lstColor=%s,iEndTime=%s)`
  - `GS2CRefreshOwnBack(lstOwnBack=%s,iAttrType=%s)`
  - `GS2CRefreshOwnFashion(iWearShape=%s,lstOwnFashion=%s,iAttrType=%s)`
  - `GS2CReplaceFreeColor(iTmpType=%s,lstInfo=%s,dTmpColor=%s)`
  - `GS2CReplyGiveItemPrice(iType=%s,iShape=%s,iPrice=%s)`
  - `GS2CRideColorList(iRideType=%s,iClass=%s,iPart=%s,lstOldColor=%s,lstNewColor=%s)`
  - `GS2CRideExchangeCnt(iCnt=%s)`
  - `GS2CShenwenAttrShow(dAttr=%s,iUseNum=%s,iMaxNum=%s)`
  - `GS2CSpriteItemColor(iItemObjId=%s,iColor=%s,iAddon=%s)`
  - `GS2CTitleAttrShow(dAttrTitle=%s,iUseNum=%s,iMaxNum=%s)`
  - `GS2CUpdateFreeColor(iTmpType=%s,dInfo=%s)`
  - `GS2CUpdateFreeColorNew(iTmpType=%s,dTmpColor=%s)`
  - `GS2CWeaponColorList(iItemObjId=%s,lstColor=%s)`
  - `GS2CWeaponItemColor(ItemID=%s,iColor=%s,iKaiQiao=%s,iKqTimeOut=%s,iNewColor=%s)`
  - `GS2CWearFashion(?)`
  - `GS2CYanzhiAttrShow(?)`

### `script\protocol\openui\csyanzhiguan.py` (entry2749)
- opcode `C2GS_OPEN_UI=0x58` iSub=[162]
- opcode `GS2C_OPEN_UI=0x59` iSub=[7]
- C2GS (32):
  - `C2GSAppearanceAskFairyColor(?)`
  - `C2GSAppearanceAskWeaponColor(?)`
  - `C2GSAppearanceChgShape(?)`
  - `C2GSAppearanceChgShapeConfirm(?)`
  - `C2GSAppearanceCombineFairy(?)`
  - `C2GSAppearanceConfirmPTDye(?)`
  - `C2GSAppearanceDelFreeDye(?)`
  - `C2GSAppearanceDelTmpDye(?)`
  - `C2GSAppearanceFairyItemAct(?)`
  - `C2GSAppearanceFairyItemColor(?)`
  - `C2GSAppearanceFreeDye(?)`
  - `C2GSAppearanceGetOutFairy(?)`
  - `C2GSAppearanceHeroFairyAct(?)`
  - `C2GSAppearanceHeroFairyColor(?)`
  - `C2GSAppearanceHeroWeaponColor(?)`
  - `C2GSAppearanceHorseChangeCount(?)`
  - `C2GSAppearanceHorseColor(?)`
  - `C2GSAppearancePTDye(?)`
  - `C2GSAppearanceResetFairyColor(?)`
  - `C2GSAppearanceResetHorseColor(?)`
  - `C2GSAppearanceResetWeaponColor(?)`
  - `C2GSAppearanceSaveFreeDye(?)`
  - `C2GSAppearanceTGF(?)`
  - `C2GSAppearanceWeaponItemColor(?)`
  - `C2GSCommitMagicPal(?)`
  - `C2GSGiftFriend(?)`
  - `C2GSMagicPalPrice(?)`
  - `C2GSOpenAppearence(?)`
  - `C2GSOpenGiftDlg(?)`
  - `C2GSRideAllColor(?)`
  - `C2GSUnluckHorseFairy(?)`
  - `C2GSWeaponAllColor(?)`
- GS2C (21):
  - `GS2CChangeShapeUINew1(?)`
  - `GS2CCloseColorUI(?)`
  - `GS2CColorUI(?)`
  - `GS2CColorUINew(?)`
  - `GS2CDelTmpFreeColor(?)`
  - `GS2CDelTmpFreeColorNew(?)`
  - `GS2CFrdList(?)`
  - `GS2CFreeColorUI(?)`
  - `GS2CFreeColorUINew(?)`
  - `GS2COpenPerformRanseUI(?)`
  - `GS2COpenYanZhiUI(?)`
  - `GS2COpenYanZhiUIAndSelect(?)`
  - `GS2CPerfomColorCost(?)`
  - `GS2CReplaceFreeColor(?)`
  - `GS2CRideColorList(?)`
  - `GS2CRideExchangeCnt(?)`
  - `GS2CSpriteItemColor(?)`
  - `GS2CUpdateFreeColor(?)`
  - `GS2CUpdateFreeColorNew(?)`
  - `GS2CWeaponColorList(?)`
  - `GS2CWeaponItemColor(?)`

### `script\pub2\pubchangephone\pubchangephonenet.py` (entry1390)
- C2GS (1):
  - `C2GSChangePhone(?)`
- GS2C (1):
  - `GS2CChangePhone(?)`

### `script\pub2\pubterms\pubtermsnet.py` (entry853)
- C2GS (1):
  - `C2GSClauseVersion(?)`
- GS2C (1):
  - `GS2CClauseVersion(?)`

### `script\yard\netyard.py` (entry3599)
- GS2C (2):
  - `GS2COpenBuyHouse(?)`
  - `GS2COpenUpHouse(?)`
