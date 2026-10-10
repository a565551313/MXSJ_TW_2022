# 任务/物品逻辑分析（Task-B 目标 6b/6c）

## 1. 任务系统（305 个 quest-ish 模块，P1）

模型层 `script\mxgame\task\model\task.py` (entry1129):
- `CItemTask`、`COwnerEquipItemTask`、`CCheckExpItemTask`（物品/装备/经验类任务条件）
- `CFlyLeadMgr`（飞行引导/传送）、`CItemSatifysTaskMgr`/`CPetOrItemSatifysTaskMgr`（条件满足器）
- `CheckNpcFlag`、`CheckItemAmount`、`AddTaskDesc`、`AddNecessary`

视图层:
- `…\task\view\dlgtasknew.py` (entry23): `CTaskDialog/CTaskItem/CTaskItemButton`、`DoAcceptLinkEvent`、`DoRecieveLinkEvent`（笔误 `Recieve`，原文如此）、`CreateTaskIcon`
- `…\tasktrace\view\tasktraceitem.py` (entry1569): `CTaskFollowTaskItem`、`CTaskTraceAutoFindEff`（自动寻路特效）、`CTaskRewardItem`
- `…\task\view\dlgtaskshow.py` (entry4376): `CHangHaiListOutPut`（沧海列表输出？）、倒计时 `DealCountDownTime`

数据层:
- `script\data\juben\taskNNNNN.py`（每任务独立数据模块，统一导出 `GetJubenData`；juben=剧本/副本）
- `script\data\tasktypedata.py` (entry1162): `GetLevel`、`GetBase/GetBaseList`、`AutoWalkEnable`、`GetAutoWalkLimit`（自动寻路开关/限制）

埋点: `script\mxgame\statistic\maintaskstatistic.py` (entry3901): `CMainTaskStatisticMgr`、`CFirstWarPassStatistic`、`CDotaskStatistic`、`CNpcMovieStatistic`（主线/首战/过场 buried points）。

## 2. 物品系统（195 个 item-ish 模块，P1）

模型层 `script\mxgame\item\item.py` (entry3462):
- `AddBagItem/AddBagItemByItem`、`AddItem/AddItemInterface`、`AddGemInfo`（宝石）、`CInterfaceBagsItem` 背包接口、影子/更新回调（`AddShadowCallback/AddUpdateCallback`）

视图层 `script\mxgame\item\view\dlgitem.py` (entry717):
- `CBagInterfaceItem`、`CEquipInterface`（装备栏）、`CExtendBag`（扩展背包）、`CFlashBox`（闪光特效盒）

商城（注意协议前缀是 C2S/S2C，不是 C2GS/GS2C）:
- `script\dialog\dlgitembill1.py` (entry3279): `C2SAskOpenShopPage`、`C2SAskOpenConcessShop`（优惠店）、`C2SAskSpringShop`、`BuyVip`、`BuyTimeCard`
- `script\dialog\dlgitembill.py` (entry3339): `C2GSOpenMXShop`、`C2SAutoVIPBuy`、`C2SBuyDiscount`、`C2SClickBuy`、`AutoVIPBuy`
- `script\dialog\dlgitemshop.py` (entry3917): `CBuyDialog/CCashDialog/CIntroDialog/CHistoryDialog`、`AmountAdd/AmountMax/AmountMin/AmountReduce`（数量步进器）

打造 `script\mxgame\makeequip\…`:
- `delegatebuild\dgtbuildequip.py` (entry1362): `BagAutoSelectBluePrint/Crystal/OrgMaterial`（图纸/水晶/帮材自动选料）、`CheckIsCanAutoMake`
- `viewbuild\dlgbuildequip.py` (entry1933): `CEquipShowPanel`、`CMakeDlg`、`AddBaseInfo/AddSubInfo/AddSkillInfo`

杂项: `script\data\dataitempath.py` (entry1034): `IsExitItemPath`（笔误 `Exit` 应为 `Exist`？原文如此）；`script\data\item_res_list.py` (entry4294) 纯资源表。

## 3. 相关协议

- 任务/物品 C2GS/GS2C 见 `protocol-commands-catalog.md`（`C2GS_HUODONG=0xcd` 家族 30 模块多为活动任务类）。
- 商城 C2S/S2C 家族需二轮挖掘（`dlgitembill*` 的 `C2SAsk*/C2SBuy*` 签名在模块 consts 内，提取脚本同协议目录生成器）。

## 4. 数据质量告警（16 类扩大确认）

全量 ok 中 177 个模块含可疑函数名（co_names 损坏但整体 parse+sane+0-garbage，如 entry115 `GS2CSelec[}JXN]K`、entry63 名字内嵌长度字节）。
合并后需二轮：对 ok-but-suspicious-name 条目跑 v7 重试 + 人工抽检。详见 `E-SCRIPT-002.md`。
