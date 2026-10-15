# pycdc 交叉复核产物 · script.fls entry 4552
# co_filename(原始)='script/protocol/cs2021summerlottery.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:56:01Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_4552.pyc (Python 2.5)

import net
import protocolcount
import net2021summerlottery

def GS2COpenSummerMain(oNetObj):
    iLotteryNum = oNetObj.UnpackInt(2)
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=1', 'GS2COpenSummerMain(iLotteryNum=%s)' % iLotteryNum)
    net2021summerlottery.OnOpenSummerMain(iLotteryNum)


def GS2COpenSummerReward(oNetObj):
    iLotteryNum = oNetObj.UnpackInt(2)
    iLevelAward = oNetObj.UnpackInt(1)
    dRewardInfo = { }
    for _index in xrange(oNetObj.UnpackInt(1)):
        iLevel = oNetObj.UnpackInt(1)
        dLevelInfo = { }
        dLevelInfo['base'] = oNetObj.UnpackInt(1)
        dLevelInfo['baseget'] = oNetObj.UnpackInt(1)
        dLevelInfo['upget'] = oNetObj.UnpackInt(1)
        dRewardInfo[iLevel] = dLevelInfo
    
    protocolcount.ProtocolLog('GS2C_HUODONG_OP=0xce,iSub=2', 'GS2COpenSummerReward(iLotteryNum=%s,iLevelAward=%s,dRewardInfo=%s)' % (iLotteryNum, iLevelAward, dRewardInfo))
    net2021summerlottery.OnOpenSummerReward(iLotteryNum, iLevelAward, dRewardInfo)

g_NetFunction = {
    1: GS2COpenSummerMain,
    2: GS2COpenSummerReward }

def OnCommand(oNetObj):
    iSub = oNetObj.UnpackInt(1)
    func = g_NetFunction.get(iSub)
    if not func:
        protocolcount.ErrorLog('net.GS2C_HUODONG_OP', '\xb5L\xaak\xb8\xd1\xaaR GS2C_HUODONG_OP=0xce \xaa\xba\xa4l\xa8\xf3\xc4\xb3\xa1G%s' % iSub)
        return None
    
    func(oNetObj)


def C2GSOpenSummerMain():
    oNetObj = GetHuoDongNetObj(1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=1', 'C2GSOpenSummerMain()')


def C2GSOpenSummerReward():
    oNetObj = GetHuoDongNetObj(2)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=2', 'C2GSOpenSummerReward()')


def C2GSSummerRewardUp():
    oNetObj = GetHuoDongNetObj(3)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=3', 'C2GSSummerRewardUp()')


def C2GSGetReward(iLevel, iAwardId):
    oNetObj = GetHuoDongNetObj(4)
    oNetObj.PacketAddI(iLevel, 1)
    oNetObj.PacketAddI(iAwardId, 1)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=4', 'C2GSGetReward(iLevel=%s,iAwardId=%s)' % (iLevel, iAwardId))


def C2GSBuySummPoint():
    oNetObj = GetHuoDongNetObj(5)
    oNetObj.PacketSend()
    protocolcount.ProtocolLog('C2GS_HUODONG=0xcd,iSub=5', 'C2GSBuySummPoint()')


def GetHuoDongNetObj(iSub):
    import nethuodong
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    if netobj:
        sStr = nethuodong.SUMMER_LOTTERY
        netobj.PacketAddI(len(sStr), 1)
        netobj.PacketAddS(sStr, len(sStr))
        netobj.PacketAddI(iSub, 1)
    
    return netobj
