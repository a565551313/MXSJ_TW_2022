# pycdc 交叉复核产物 · script.fls entry 4385
# co_filename(原始)='script/mxgame/auction/nethdidauction.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4385.pyc (Python 2.5)

import C_sys
import dlgshopmain
import misc
import hero
import mdauctionmain

def OnOpenCurAuction(lstGoods):
    dlgshopmain.ShowAuctionShop()
    mdauctionmain.GetModel().SetNumberData(PraseGoodsList(lstGoods, True))


def OnRefreshNextAuction(lstGoods):
    dGoodsL'=t = []
    for iItemShape, iNumber, iBasePrice, iStartTime, iIsRemind, iType, iMinAddPrice in lstGoods:
        if iStartTime <= 0:
            continue
        
        dGoods = {
            'shape': iItemShape,
            'buyType': 2,
            'basePrice': iBasePrice,
            'desc': '',
            'iStartTime': iStartTime,
            'timeNum': iStartTime,
            'name': int(iNumber),
            'bIsBook': iIsRemind,
            'bIsSp': iType == 2,
            'iMinAddPrice': iMinAddPrice }
        dGoodsL'=t.append(dGoods)
    
    mdauctionmain.GetModel().SetNumberNext(dGoodsL'=t)


def OnUpdateCurAuction(lstGoods):
    mdauctionmain.GetModel().SetNumberData(PraseGoodsList(lstGoods, False))


def PraseGoodsList(lstGoods, bWithJoin):
    import misc
    import time
    iServerTime = misc.GetServerCurrentTime()
    if iServerTime > 0:
        bSunday = time.localtime(iServerTime).tm_wday == 6
    else:
        bSunday = False
    dGoodsL'=t = []
    iHeroServer = misc.GetOrgServerID()
    iHeroID = hero.GetHeroID()
    iCurTime = C_sys.GetTime() / 10000
    for tGoods in lstGoods:
        if not bWithJoin:
            (iItemID, iItemShape, iNumber, iBasePrice, iCurPrice, iTimeLeft, iMaxPlayerServer, iMaxPlayerID, iMaxPlayerPrice, iType, lstAuto, bIsOuttime, iMinAddPrice) = tGoods
            bPlayerJoin = None
        else:
            (iItemID, iItemShape, iNumber, iBasePrice, iCurPrice, iTimeLeft, iMaxPlayerServer, iMaxPlayerID, iMaxPlayerPrice, iType, lstAuto, bIsOuttime, iMinAddPrice, bPlayerJoin) = tGoods
        if iMaxPlayerServer == iHeroServer and iMaxPlayerID == iHeroID:
            iPlayerPrice = iMaxPlayerPrice
        else:
            iPlayerPrice = 0
        for iAutoServer, iAutoPlayerID, iAutoPlayerPrice, iAutoMultiAdd in lstAuto:
            if iAutoServer == iHeroServer and iAutoPlayerID == iHeroID:
                iPlayerMaxPrice = iAutoPlayerPrice
                iMultiAdd = iAutoMultiAdd
                break
                continue
        else:
            iPlayerMaxPrice = 0
            iMultiAdd = 0
        +({
            'itemID': iItemID,
            'shape': iItemShape,
            'buyType': 2,
            'basePrice': iBasePrice,
            'curPrice': iCurPrice,
            'myPrice': iPlayerPrice,
            'mostPrice': iPlayerMaxPrice,
            'multiNum': iMultiAdd,
            'amount': 1,
            'desc': '',
            'timeLeft': iTimeLeft,
            'name': str(iNumber) } ^ 'bIsSp')['curtime'] = iCurTime
        iType == 2['bIsOuttime'] = bIsOuttime
        iType == 2['iMinAddPrice'] = iMinAddPrice
        dGoods = iType == 2
        if bSunday:
            dGoods['bIsSp'] = False
        
        if bPlayerJoin is not None:
            dGoods['bJoin'] = bPlayerJoin
        
        dGoodsL'=t.append(dGoods)
    
    return dGoodsL'=t


def C2GSOpenAucDlg():
    import csidauction
    csidauction.C2GSOpenAucDlg()


def C2GSAskForNextAuction():
    import csidauction
    csidauction.C2GSAskForNextAuction()


def C2GSBid(iItemID, iPrice):
    import csidauction
    csidauction.C2GSBid(iItemID, iPrice)


def C2GSSetAutoBid(iItemID, iMultiAdd, iMaxPrice):
    import csidauction
    csidauction.C2GSSetAutoBid(iItemID, iMultiAdd, iMaxPrice)


def C2GSModifyAutoBid(iItemID, iMultiAdd, iMaxPrice):
    import csidauction
    csidauction.C2GSModifyAutoBid(iItemID, iMultiAdd, iMaxPrice)


def C2GSCloseDlg():
    import csidauction
    csidauction.C2GSCloseDlg()


def C2GSSetRemind(iItemID, iIsRemind):
    import csidauction
    csidauction.C2GSSetRemind(iItemID, iIsRemind)
