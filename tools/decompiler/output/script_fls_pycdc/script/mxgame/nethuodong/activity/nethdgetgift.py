# pycdc 交叉复核产物 · script.fls entry 1993
# co_filename(原始)='script/mxgame/nethuodong/activity/nethdgetgift.py'
# uncompyle6 状态=stub  转译阶段=baseline
# 生成时间=2026-10-14T23:55:56Z
# 输入 sha256=8b6e9266bbe91fa77763df7bb2890d55c968c558b8d4b5e415f27febaf6c0d72
# Source Generated with Decompyle++
# File: entry_1993.pyc (Python 2.5)

import huodongdefine
import net

def GetGetgiftNetObj():
    netobj = net.PacketPrepare(net.C2GS_HUODONG)
    netobj.PacketAddPS(huodongdefine.GETGIFT)
    return netobj


def SetAbleShow(netobj):
    flag = netobj.UnpackInt(1)
    import dlgsysmail
    dlgsysmail.RefreshRewardBtn(flag)


def C2SGetGift(itime):
    netobj = GetGetgiftNetObj()
    netobj.PacketAddI(1, 1)
    netobj.PacketAddI(itime, 4)
    netobj.PacketSend()


def C2SAbleGet():
    netobj = GetGetgiftNetObj()
    netobj.PacketAddI(2, 1)
    netobj.PacketSend()

S2CFunc = {
    1: SetAbleShow }

def S2CGetgiftProcess(netobj):
    iSub = netobj.UnpackInt(1)
    if iSub not in S2CFunc:
        LOG('S2CGetgift-%d \xaf\xca\xa4\xd6\xa9w\xb8q\xa1I' *= iSub)
        return None
    
    import protocolprint
    oFunc = S2CFunc[iSub]
    protocolprint.AppendS2CSubInfo('Getgift', oFunc.__name__)
    oFunc(netobj)
