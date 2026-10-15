# pycdc 交叉复核产物 · script.fls entry 3316
# co_filename(原始)='script/mxgame/activity/groupbbq/netnewgroupbbq.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:59Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_3316.pyc (Python 2.5)


def S2CQuestionGameState(netobj):
    iState = netobj.UnpackInt(1)
    iGX = netobj.UnpackInt(2)
    iGY = netobj.UnpackInt(2)
    iRX = netobj.UnpackInt(2)
    iRY = netobj.UnpackInt(2)
    import groupbbqmap
    groupbbqmap.GetQuestionGame().SetGameState(iState, tGreenCP = (iGX, iGY), tRedCP = (iRX, iRY))


def S2CBBQStep(netobj):
    iNpcID = netobj.UnpackInt(4)
    iState = netobj.UnpackInt(1)
    for iStartTime in netobj:
        iEndTime = netobj.UnpackInt(4)
        import groupbbqmap
        groupbbqmap.SetBBQDestopInfo(iNpcID, iState, iStartTime, iEndTime)
        return None


def S2CChefCountDown(netobj):
    iNpcID = netobj.UnpackInt(4)
    import groupbbqmap
    groupbbqmap.GetQuestionGame().ChefCountDown(iNpcID)

S2CFunc = {
    1: S2CQuestionGameState,
    2: S2CBBQStep,
    3: S2CChefCountDown }

def S2CNewBBQProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CNewBBQProcess-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' % iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('netnewgroupbbq', oFunc.__name__)
    LOG_DEBUG('S2CNewBBQProcess-%d' % iSub)
    oFunc(netobj)


def GetNewBBQNetObj(iSub):
    import net
    import nethuodong
    netobj = net.g_Net
    sTreaty = nethuodong.NEWGROUPBBQ
    if netobj:
        netobj.PacketPrepare(net.C2GS_HUODONG)
        netobj.PacketAddI(len(sTreaty), 1)
        netobj.PacketAddS(sTreaty, len(sTreaty))
        netobj.PacketAddI(iSub, 1)
        LOG_DEBUG('C2SNewGroupBBQ-%d' % iSub)
    
    return netobj


def U$SQuestionStateChange(iInCircle):
    oNetobj = GetNewBBQNetObj(1)
    if oNetobj:
        oNetobj.PacketAddI(iInCircle, 1)
        oNetobj.PacketSend()
