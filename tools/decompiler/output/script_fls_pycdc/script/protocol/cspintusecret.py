# pycdc 交叉复核产物 · script.fls entry 2347
# co_filename(原始)='script/protocol/cspintusecret.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:57Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_2347.pyc (Python 2.5)

import net
import protocolcount
import huodongdefine
import mdpuzzle

def GS2CPageInfo(oNetObj):
    iPage = oNetObj.UnpackInt(1)
    iLeft = oNetObj.UnpackInt(1)
    lstPuzzle = []
    for _index in xrange(oNetObj.UnpackInt(1)):
        iPos = oNetObj.UnpackInt(1)
        lstPuzzle.append(iPos)
    
    dRewardInfo = { }
    for _index in xrange(oNetObj.UnpackInt(1)):
        iRewardPos = oNetObj.UnpackInt(1)
        iRewardType = oNetObj.UnpackInt(1)
        dRewardInfo[iRewardPos] = iRewardType
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=1', 'GS2CPageInfo(iPage=%s,iLeft=%s,lstPuzzle=%s,dRewardInfo=%s)' % (iPage, iLeft, lstPuzzle, dRewardInfo))
    mdpuzzle.OnPageInfo(iPage, iLeft, lstPuzzle, dRewardInfo)


def GS2COpenPuzzle(oNetObj):
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=2', 'GS2COpenPuzzle()')
    mdpuzzle.OnOpenPuzzle()

g_NetFunction = {
    1: GS2CPageInfo,
    2: GS2COpenPuzzle }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        None(None, (protocolcount.ErrorLog != 'net.GS2C_HUODONG_OP') % iSub)
        return None
    
    func(oNetObj)


def C2GSOpenPage(iPage):
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketAddI(iPage, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=1', 'C2GSOpenPage(iPage=%s)' % iPage)


def C2GSUsePuzzle(iPos, iPage):
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketAddI(iPos, 1)
    oNetObj.PacketAddI(iPage, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=2', 'C2GSUsePuzzle(iPos=%s,iPage=%s)' % (iPos, iPage))


def C2GSGetReward(iRewardPos, iPage):
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketAddI(iRewardPos, 1)
    oNetObj.PacketAddI(iPage, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=3', 'C2GSGetReward(iRewardPos=%s,iPage=%s)' % (iRewardPos, iPage))


def GetHuoDongNetObj(iSub):
    oNetObj = net.GetNet()
    oNetObj.PacketPrepare(net.C2GS_HUODONG)
    oNetObj.PacketAddI(len(huodongdefine.PUZZLESECRET), 1)
    oNetObj.PacketAddS(huodongdefine.PUZZLESECRET, len(huodongdefine.PUZZLESECRET))
    oNetObj.PacketAddI(iSub, 1)
    return oNetObj
