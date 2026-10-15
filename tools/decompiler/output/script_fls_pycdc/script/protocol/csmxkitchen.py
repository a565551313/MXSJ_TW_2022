# pycdc 交叉复核产物 · script.fls entry 970
# co_filename(原始)='script/protocol/csmxkitchen.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:55Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_970.pyc (Python 2.5)

import huodongdefine
import net
import protocolcount
import netmxkitchen

def GS2CAddNpc(oNetObj):
    lstFurniture = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iMid = oNetObj.UnpackInt(4)
        iSid = oNetObj.UnpackInt(2)
        lstFurniture.append([
            iMid,
            iSid])
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=1', 'GS2CAddNpc(lstFurniture=%s)' % lstFurniture)
    netmxkitchen.OnAddNpc(lstFurniture)


def GS2CRemoveNpc(oNetObj):
    iMid = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=2', 'GS2CRemoveNpc(iMid=%s)' % iMid)
    netmxkitchen.OnRemoveNpc(iMid)


def GS2CChangeNpcGoods(oNetObj):
    iMid = oNetObj.UnpackInt(4)
    iType = oNetObj.UnpackInt(1)
    iStatus = oNetObj.UnpackInt(1)
    lstGood = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iGoodsID = oNetObj.UnpackInt(4)
        lstGood.append(iGoodsID)
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=3', 'GS2CChangeNpcGoods(iMid=%s,iType=%s,iStatus=%s,lstGood=%s)' % (iMid, iType, iStatus, lstGood))
    netmxkitchen.OnChangeNpcGoods(iMid, iType, iStatus, lstGood)


def GS2CShowPorgress(oNetObj):
    iMid = oNetObj.UnpackInt(4)
    iType = oNetObj.UnpackInt(1)
    iStatus = oNetObj.UnpackInt(1)
    iRemainSec = oNetObj.UnpackInt(4)
    iSec = oNetObj.UnpackInt(4)
    iPlayerID = oNetObj.UnpackInt(4)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=4', 'GS2CShowPorgress(iMid=%s,iType=%s,iStatus=%s,iRemainSec=%s,iSec=%s,iPlayerID=%s)' % (iMid, iType, iStatus, iRemainSec, iSec, iPlayerID))
    netmxkitchen.OnShowPorgress(iMid, iType, iStatus, iRemainSec, iSec, iPlayerID)


def GS2COpenCookInfoDlg(oNetObj):
    iOpen = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=5', 'GS2COpenCookInfoDlg(iOpen=%s)' % iOpen)
    netmxkitchen.OnOpenCookInfoDlg(iOpen)


def GS2CRefreshTeamInfo(oNetObj):
    iMaxManege = oNetObj.UnpackInt(2)
    iResidueTime = oNetObj.UnpackInt(2)
    iHighMaxManege = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=6', 'GS2CRefreshTeamInfo(iMaxManege=%s,iResidueTime=%s,iHighMaxManege=%s)' % (iMaxManege, iResidueTime, iHighMaxManege))
    netmxkitchen.OnRefreshTeamInfo(iMaxManege, iResidueTime, iHighMaxManege)


def GS2CRefreshOrderInfo(oNetObj):
    iCurrManege = oNetObj.UnpackInt(2)
    iIdx = oNetObj.UnpackInt(1)
    dCookItem = { }
    dCookItem['item'] = oNetObj.UnpackInt(4)
    dCookItem['materials'] = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iMaterialsID = oNetObj.UnpackInt(4)
        dCookItem['materials'].append(iMaterialsID)
    
    dCookItem['currprogress'] = oNetObj.UnpackInt(1)
    dCookItem['maxprogress'] = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=7', 'GS2CRefreshOrderInfo(iCurrManege=%s,iIdx=%s,dCookItem=%s)' % (iCurrManege, iIdx, dCookItem))
    netmxkitchen.OnRefreshOrderInfo(iCurrManege, iIdx, dCookItem)


def GS2COpenCookShareDlg(oNetObj):
    iScoce = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=8', 'GS2COpenCookShareDlg(iScoce=%s)' % iScoce)
    netmxkitchen.OnOpenCookShareDlg(iScoce)


def GS2CHuodongState(oNetObj):
    iState = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=9', 'GS2CHuodongState(iState=%s)' % iState)
    netmxkitchen.OnHuodongState(iState)


def GS2COpenNoviceDlg(oNetObj):
    iState = oNetObj.UnpackInt(1)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=10', 'GS2COpenNoviceDlg(iState=%s)' % iState)
    netmxkitchen.OnOpenNoviceDlg(iState)

g_NetFunction = {
    1: GS2CAddNpc,
    2: GS2CRemoveNpc,
    3: GS2CChangeNpcGoods,
    4: GS2CShowPorgress,
    5: GS2COpenCookInfoDlg,
    6: GS2CRefreshTeamInfo,
    7: GS2CRefreshOrderInfo,
    8: GS2COpenCookShareDlg,
    9: GS2CHuodongState,
    10: GS2COpenNoviceDlg }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_HUODONG_OP', '\xb5L\xaak\xb8\xd1\xaaR GS2C_HUODONG_OP=0xce \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSClickNpc(iMid):
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketAddI(iMid, 4)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=1', 'C2GSClickNpc(iMid=%s)' % iMid)


def C2GSLeaveScene():
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=2', 'C2GSLeaveScene()')


def C2GSChangeNoviceSign(iState):
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketAddI(iState, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=3', 'C2GSChangeNoviceSign(iState=%s)' % iState)


def GetHuoDongNetObj(iSub):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    oNetObj.PacketAddI(len(huodongdefine.KITCHEN), 1)
    oNetObj.PacketAddS(huodongdefine.KITCHEN, len(huodongdefine.KITCHEN))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
