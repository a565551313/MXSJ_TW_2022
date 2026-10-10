# 商城协议专题分析（mall-protocol-analysis）

**范围**：`dlgitembill*`/`dlgitemshop`/`netitemshop`/`netshop`/`dlggoodsshop`/`netopenui` 中的商城相关 C2S 发送函数，以及 `dlgbuildequip`/`dgtbuildequip` 对应的装备打造 C2S。
**方法**：离线解码 `data/script.fls`（`tools/fls_batch_decoder.py` 的 `decode_entry_auto`，v4-ok 条目），用 `tools/extract_co_signatures.py` 导出每个 code object 的 varnames / names / consts，再按下列规则整理：
- 基础命令（base opcode 名）= 函数内 `PacketPrepare`/`GetOpenUINetObj` 相关的 `C2GS_*` 全局名；
- 子命令 sub = 函数 consts 中第一个非负整数（字节码里 PacketAddI 的第一个常量），仅对“单层子命令”结构成立；
- 参数名 = varnames 去掉 netobj 等通道参数；
- **数字 opcode（基础命令的 0x 值）大多未能恢复**，见第 5 节。

**与任务书的差异（已核对）**：`dlgitembill1.py` / `dlgitemshop.py` 在 catalog 中**不存在**；实际模块为 `dialog\dlgitembill_new.py`、`dialog\dlgitembill1_item.py`、`dialog\dlgitembillminibuy2.py`、`netitemshop.py`、`netshop.py`。装备打造实际模块为 `mxgame\makeequip\view\viewbuild\dlgbuildequip.py` 与 `mxgame\makeequip\delegate\delegatebuild\dgtbuildequip.py`（均存在）。

**不含“调试串签名”**：这些模块内没有 `Name(p=%s,...)` 形式的调试串，签名只能从字节码的 varnames 推出，因此下表的“函数签名”是**参数名列表**，不是类型签名。

## 1. C2S 商城命令（C2GS_ITEMSHOP 族 — 物品店/摆摊）

| 命令名 | 模块 | 函数签名 | 基础命令 | 子命令 sub | 说明 | 置信度 |
|---|---|---|---|---|---|---|
| C2SPutItem | netitemshop.py | `C2SPutItem(ID=%s, iPrice=%s, iNum=%s)` | C2GS_ITEMSHOP | 1 | 上架物品 | 高（sub 与 consts 序列一致） |
| C2SGetItem | netitemshop.py | `C2SGetItem(pos=%s, destPos=%s)` | C2GS_ITEMSHOP | 2 | 取回物品 | 高（sub 与 consts 序列一致） |
| C2SModifyPrice | netitemshop.py | `C2SModifyPrice(pos=%s, price=%s)` | C2GS_ITEMSHOP | 3 | 修改单价 | 高（sub 与 consts 序列一致） |
| C2SGetShopList | netitemshop.py | `C2SGetShopList()` | C2GS_ITEMSHOP | 4 | 获取店铺列表 | 高（sub 与 consts 序列一致） |
| C2SGetShopIntro | netitemshop.py | `C2SGetShopIntro(pid=%s, idx=%s)` | C2GS_ITEMSHOP | 5 | 获取店铺介绍 | 高（sub 与 consts 序列一致） |
| C2SLookShop | netitemshop.py | `C2SLookShop(pid=%s, idx=%s)` | C2GS_ITEMSHOP | 6 | 浏览店铺 | 高（sub 与 consts 序列一致） |
| C2SGetItemInfo | netitemshop.py | `C2SGetItemInfo(pos=%s)` | C2GS_ITEMSHOP | 7 | 查询物品信息 | 高（sub 与 consts 序列一致） |
| C2SBuyItem | netitemshop.py | `C2SBuyItem(pos=%s, amount=%s, shape=%s, price=%s)` | C2GS_ITEMSHOP | 8 | 购买物品（pos/数量/形状/单价） | 高（sub 与 consts 序列一致） |
| C2SSaving | netitemshop.py | `C2SSaving(cash=%s)` | C2GS_ITEMSHOP | 9 | 存入金钱 | 高（sub 与 consts 序列一致） |
| C2SDraw | netitemshop.py | `C2SDraw(cash=%s)` | C2GS_ITEMSHOP | 10 | 取出金钱 | 高（sub 与 consts 序列一致） |
| C2SSetIntro | netitemshop.py | `C2SSetIntro(intro=%s)` | C2GS_ITEMSHOP | 11 | 设置店铺介绍 | 高（sub 与 consts 序列一致） |
| C2SSetAdFee | netitemshop.py | `C2SSetAdFee(fee=%s)` | C2GS_ITEMSHOP | 12 | 设置广告费 | 高（sub 与 consts 序列一致） |
| C2SChangeType | netitemshop.py | `C2SChangeType(itype=%s, name=%s)` | C2GS_ITEMSHOP | 13 | 修改店铺类型/名称 | 高（sub 与 consts 序列一致） |
| C2SSwithItem | netitemshop.py | `C2SSwithItem(pos=%s, pos1=%s)` | C2GS_ITEMSHOP | 15 | 交换货位 | 高（sub 与 consts 序列一致） |
| C2SLock | netitemshop.py | `C2SLock()` | C2GS_ITEMSHOP | 16 | 锁定店铺 | 高（sub 与 consts 序列一致） |
| C2SUnLock | netitemshop.py | `C2SUnLock()` | C2GS_ITEMSHOP | 17 | 解锁店铺 | 高（sub 与 consts 序列一致） |
| C2SSaveSign | netitemshop.py | `C2SSaveSign(sign=%s, focus=%s)` | C2GS_ITEMSHOP | 18 | 保存店铺标识 | 高（sub 与 consts 序列一致） |
| C2SSendShopIdx | netitemshop.py | `C2SSendShopIdx(idx=%s)` | C2GS_ITEMSHOP | 19 | 发送店铺索引 | 高（sub 与 consts 序列一致） |
| C2SChangeItemShopName | netitemshop.py | `C2SChangeItemShopName(name=%s)` | C2GS_ITEMSHOP | 20 | 改店名 | 高（sub 与 consts 序列一致） |
| C2SDelItemPrice | netitemshop.py | `C2SDelItemPrice(price=%s)` | C2GS_ITEMSHOP | 21 | 删除价格记录 | 高（sub 与 consts 序列一致） |
| C2SMultiBuy | netitemshop.py | `C2SMultiBuy(buyList=%s)` | C2GS_ITEMSHOP | 22 | 批量购买（buyList） | 高（sub 与 consts 序列一致） |

## 2. C2S 商城命令（C2GS_SHOP 族 — 店铺/摊位）

| 命令名 | 模块 | 函数签名 | 基础命令 | 子命令 sub | 说明 | 置信度 |
|---|---|---|---|---|---|---|
| C2SGetGoodsList | netshop.py | `C2SGetGoodsList(idx=%s)` | C2GS_SHOP | 1 | 获取商品列表 | 高 |
| C2SGetBuyList | netshop.py | `C2SGetBuyList(idx=%s)` | C2GS_SHOP | 2 | 获取求购列表 | 高 |
| C2SVendue | netshop.py | `C2SVendue(price=%s, name=%s)` | C2GS_SHOP | 3 | 摆摊/拍卖上架 | 高 |
| C2SChgGoodInfo | netshop.py | `C2SChgGoodInfo(shape=%s, need=%s, buy=%s, sell=%s)` | C2GS_SHOP | 4 | 修改商品信息（形状/需求/买入/卖出价） | 高 |
| C2SChgShopName | netshop.py | `C2SChgShopName()` | C2GS_SHOP | 11 | 修改店名 | 中（无参，sub 可能为 11 的特殊映射，需复核） |
| C2SDelGood | netshop.py | `C2SDelGood(shape=%s)` | C2GS_SHOP | 5 | 下架商品 | 高 |
| C2SBuyPet | netshop.py | `C2SBuyPet(shape=%s)` | C2GS_SHOP | 6 | 购买宠物 | 高 |
| C2SSellPet | netshop.py | `C2SSellPet(petid=%s)` | C2GS_SHOP | 7 | 出售宠物 | 高 |
| C2SPushMoney | netshop.py | `C2SPushMoney(cash=%s)` | C2GS_SHOP | 8 | 存钱（店铺） | 高 |
| C2SPopMoney | netshop.py | `C2SPopMoney(cash=%s)` | C2GS_SHOP | 9 | 取钱（店铺） | 高 |
| C2SChgDesc | netshop.py | `C2SChgDesc(desc=%s)` | C2GS_SHOP | 10 | 修改店铺描述 | 高 |
| C2SChgCountryShop | netshop.py | `C2SChgCountryShop(country=%s)` | C2GS_SHOP | 12 | 修改国家店铺 | 高 |

## 3. C2S 商城命令（C2GS_OPEN_UI 族 — 快捷购买 / 物品获取弹窗）

| 命令名 | 模块 | 函数签名 | 基础命令 | 子命令 sub | 说明 | 置信度 |
|---|---|---|---|---|---|---|
| C2SQuickBuyHTDan | netopenui.py | `C2SQuickBuyHTDan(iMode=%s, iItemId=%s, iAmount=%s)` | C2GS_OPEN_UI(=0x58) | 165 | 快捷购买花图单/道具（dlgitembillminibuy2 调用） | 高 |
| C2SOpenPublicMiniBuyDialog | netopenui.py | `C2SOpenPublicMiniBuyDialog(iShape=%s)` | C2GS_OPEN_UI(=0x58) | 166 | 打开公共迷你购买框 | 高 |
| C2SItemOpenQuickBuyDlgByUseType | netopenui.py | `C2SItemOpenQuickBuyDlgByUseType(iShape=%s, iUseType=%s, iReason=%s, iTarget=%s)` | C2GS_OPEN_UI(=0x58) | 168 | 按用途打开快捷购买；源码注释给出 `4b iShape / 1b iUseType / 1b iSub / 4b iTarget` | 高（注释佐证） |
| C2SItemAccessDlgBuy | netopenui.py | `C2SItemAccessDlgBuy(iShape=%s, iLv=%s, iType=%s, iPrice=%s, iAmount=%s, iAmountType=%s, iSumAmount=%s, iPriceType=%s)` | C2GS_OPEN_UI(=0x58) | 160 | 物品获取弹窗-购买；注释 `0x58 sub 160`，iPriceType 有 0/1/2 三种取值（注释为乱码，具体支付方式未确认） | 高（注释佐证） |
| C2SOpenItemAccessDlg | netopenui.py | `C2SOpenItemAccessDlg(iShape=%s, iLv=%s, iType=%s, sName=%s, iAmount=%s, iAmountType=%s)` | C2GS_OPEN_UI(=0x58) | 159 | 物品获取弹窗-打开；注释 `0x58 sub 159` | 高（注释佐证） |
| C2SUseQuickBuy | netopenui.py | `C2SUseQuickBuy(iItemID=%s, iNeedNum=%s, iSumID=%s, iMode=%s)` | C2GS_OPEN_UI(=0x58) | 150 | 使用道具时的快捷购买 | 高 |

## 4. C2S 商城命令（C2GS_PLAYER_IB 族 — 限量道具/元宝商城）

| 命令名 | 模块 | 函数签名 | 基础命令 | 子命令 sub | 说明 | 置信度 |
|---|---|---|---|---|---|---|
| C2SXianLiuPage | dlggoodsshop.py | `C2SXianLiuPage(ipage=%s)` | C2GS_PLAYER_IB | 25 | 限量道具翻页 | 中 |
| C2SXianLiuBuy | dlggoodsshop.py | `C2SXianLiuBuy(ipage=%s, ipos=%s, amount=%s)` | C2GS_PLAYER_IB | 25 | 限量道具购买（被 dlgitembill_new 调用） | 中 |

> ⚠ **待复核**：两个函数的 sub 同为 25，区分依据未知（可能是同一子命令的两种参数形态，或解码偏差）。在未验证前不要据此实现协议。

## 5. 基础命令（主 opcode）状态

| 基础命令 | 数字值 | 状态 |
|---|---|---|
| C2GS_OPEN_UI | 0x58 | ✅ 已确认：`protocol-commands-catalog.md` + 源码注释 `0x58 sub 159/160` |
| C2GS_ITEMSHOP | 未恢复 | 在 `netprotocol.py` 的常量表中未出现；`script\protocol\` 下 64 个 ok 条目（共 67 个）已扫描模块级常量，无定义 |
| C2GS_SHOP | 未恢复 | 同上 |
| C2GS_PLAYER_IB | 未恢复 | 同上 |
| C2GS_BUILD / C2GS_CREATE（装备打造） | 未恢复 | 见第 6 节 |

在仓库内的 `*.dll` / `*.exe` 与文本文件中 `grep` 不到 `C2GS_ITEMSHOP` / `C2GS_PLAYER_IB`（注意：脚本本体在加密的 `data/script.fls` 中，grep 无法覆盖脚本内容，这一步只排除了原生二进制与明文文件）。推测其数字定义位于解码后的某个未扫描模块（如 `*define*.py` 类，约 70 个 ok 条目），或由 C++ 侧注册。**下一步**：解码并扫描这些 `*define*` 条目，查 `C2GS_ITEMSHOP` 等名字的赋值常量。

## 6. S2C 商城命令（服务端→客户端）

`netitemshop.py` 模块级代码将 9 个处理函数登记为子命令 1–9（`LOAD_NAME → <5A> → LOAD_CONST n → <05>` 形态；`5A`/`05` 在映射表中仍为未知，子命令号来自 consts 1..9，置信度中）：

| 子命令 | 处理函数 | 解包字段（UnpackInt/UnpackString 次序） | 说明 |
|---|---|---|---|
| 1 | S2CMyShop | UnpackInt(idx,iLocked,freeze,itype,money,fee,ad,ad2,followerNum), UnpackString(name,intro) | 我的店铺信息 → `dlgitemshop.ShowMyShop` |
| 2 | S2CItemList | UnpackInt(pos,shape,amount,price,level,bModel) | 物品列表 → `OnItemList` |
| 3 | S2CRefreshItem | UnpackInt(pos,shape,amount,price,level,bModel) | 单格刷新 → `RefreshItem` |
| 4 | S2CShopList | UnpackInt(pid,idx,itype,…), UnpackString(name,oweer,sign) | 店铺列表 → `OnShopList` |
| 5 | S2CShopIntro | UnpackInt(pid,idx), UnpackString(intro) | 店铺介绍 → `OnShopIntro`（经 banword 过滤） |
| 6 | S2CShopGoods | UnpackInt(pid,idx,…), UnpackString(name,oweer) | 店铺商品 → `OnShopGoods` |
| 7 | S2CShopHistory | UnpackInt, UnpackString(`||`/`,` 分隔) | 交易历史 → `ShowHistory` |
| 8 | S2CShopName | UnpackInt(size), UnpackString(name) | 店铺名列表 → `ShowShopName` |
| 9 | S2CShopPrice | UnpackInt(size,price) | 价格 → `SetLastPrice` |
| — | S2CItemShop | UnpackInt(isub) | 分发包装（`ItemShopFunc`，日志 `>>S2CItemShop isub>>`） |

`netshop.py` 的 `GS2C_SHOP` 为分派函数（`ShowShopList`/`ShowVendue`/`ShowManage`/`ShowBuy`/`ChgSellAmount`/`ShowSell`），子命令到分支的映射未完全恢复（置信度低）。

## 7. 装备打造相关 C2S（dgtbuildequip / dlgbuildequip 调用的发送函数）

此处为**两级结构**（族 ID + 子命令），首个 int 不是子命令，故不套用第 1 节规则：

| 命令名 | 模块 | 函数签名 | 族/sub（consts 原序） | 说明 | 置信度 |
|---|---|---|---|---|---|
| C2SQuicklyIdentify1 | nethdcreate.py | `C2SQuicklyIdentify1(iEquipID=%s)` | 12 | 快速鉴定（一） | 中 |
| C2SQuicklyIdentify2 | nethdcreate.py | `C2SQuicklyIdentify2(iEquipID=%s)` | 13 | 快速鉴定（二） | 中 |
| C2SUseEquip | nethdcreate.py | `C2SUseEquip(iBindState=%s, iItemID=%s)` | 14 | 使用装备 | 中 |
| C2SDoubleElevenMakingTips | nethdcreate.py | `C2SDoubleElevenMakingTips()` | 15 | 双十一打造提示 | 中 |
| C2SAskMakeTuiJianState | netbuild.py | `C2SAskMakeTuiJianState()` | 13（第一常量为 None） | 查询推荐打造状态 | 低 |
| C2SRequestEquipInfo | netbuild.py | `C2SRequestEquipInfo(iType=%s, iLevel=%s)` | 50 | 请求装备信息（S2C `S2CEquipInfo` 对应） | 中 |
| C2SQuickBuyItem | netbuild.py | `C2SQuickBuyItem(iShape=%s, args=%s)` | 2 | 快速购买（超级符） | 低 |
| C2SAskMakeSymbolMoney | netbuild.py | `C2SAskMakeSymbolMoney(iSkill=%s, iGrade=%s, iSuper=%s)` | 1 | 符文打造费用查询 | 低 |

> 装备打造族 `netbuild.py` 中宝石子族（族 21/23/24/25/26）的 sub 为第二个常量，例如 `C2SRequestGemInfo` = 21/1，`C2SNewRemoveGemInfo` = 21/11，`C2SNewCancelTransformGem` = 21/22；未逐条验证，列入后续。

## 8. 未解决与风险

1. 基础命令数字值（ITEMSHOP/SHOP/PLAYER_IB/BUILD）未恢复，因此本文件**无法给出完整的 opcode 列表**。
2. 子命令 sub 来自“首个整数常量”启发式；对单层子命令族（ITEMSHOP、SHOP、OPEN_UI 的商城部分）与源码注释吻合度高，对两级结构族（BUILD 族）不适用。
3. `C2GS_PLAYER_IB` 的两条命令 sub 相同（25），待复核。
4. 部分 consts 为 Big5 编码中文注释，已按 UTF-8 解码失败/乱码处理，仅用其中的数字信息。
5. 数字常量 1/2/4 出现在多数打包调用中，推测为字段字节宽度（1/2/4B）；**未证实**，不写入签名。

## 附：复现

```bash
python3 tools/extract_co_signatures.py --indices 1498,1848,1425,3291,1203,194 --out /tmp/mall
```
